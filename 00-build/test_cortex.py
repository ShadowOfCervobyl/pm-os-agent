"""Tests for what Cortex lets the model read and for the bounds that halt a run.

Run: .venv/bin/python test_cortex.py

The model is the only thing faked: a scripted client stands in for the OpenAI
client at its boundary. The tools, the fixtures and the loop are real.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import httpx2
import openai

sys.path.insert(0, str(Path(__file__).parent))
import agent  # noqa: E402
import tools  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
EMBARGOED_NAMES = ("Orbit", "Pulsar")
EMBARGOED_PRD_TEXT = (
    "Unreleased AI features. Not to be referenced outside the core team",
    "Early exploration of a next-gen search experience",
)


def _usage():
    return SimpleNamespace(prompt_tokens=10, completion_tokens=10)


def text_reply(text):
    msg = SimpleNamespace(content=text, tool_calls=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=_usage())


def tool_reply(*calls):
    tool_calls = [SimpleNamespace(id=f"call-{i}", type="function",
                                  function=SimpleNamespace(name=name, arguments=json.dumps(args)))
                  for i, (name, args) in enumerate(calls)]
    msg = SimpleNamespace(content=None, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)], usage=_usage())


def api_error():
    return openai.APIConnectionError(request=httpx2.Request("POST", "https://model.invalid/v1"))


class ScriptedModel:
    """Stands in for openai.OpenAI. Each drafting call takes the next step of the
    script; the last step repeats. A step is a reply, an exception to raise, or a
    (seconds, reply) pair that sleeps first. Critic calls get `critic`."""

    def __init__(self, script, critic="pass"):
        self.script = list(script)
        self.critic = critic
        self.calls = []
        self.critic_calls = []

    def __call__(self, **_):
        return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=self.create)))

    def create(self, **kw):
        kw = {**kw, "messages": copy.copy(kw["messages"])}
        if "response_format" in kw:
            self.critic_calls.append(kw)
            if isinstance(self.critic, BaseException):
                raise self.critic
            return text_reply(json.dumps({"verdict": self.critic, "reasons": []}))
        self.calls.append(kw)
        step = self.script[min(len(self.calls), len(self.script)) - 1]
        if isinstance(step, BaseException):
            raise step
        if isinstance(step, tuple):
            time.sleep(step[0])
            return step[1]
        return step

    def everything_sent(self) -> str:
        parts = []
        for kw in self.calls + self.critic_calls:
            for m in kw["messages"]:
                content = m.get("content") if isinstance(m, dict) else getattr(m, "content", None)
                parts.append(str(content or ""))
        return "\n".join(parts)


class _Result(unittest.TextTestResult):
    # pytest-style headers, so each failure prints as its own named block.
    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(f"_____ test_cortex.py::{test.id().split('.', 1)[1]} {flavour} _____")
            self.stream.writeln(err)


class RunCase(unittest.TestCase):
    def setUp(self):
        # agent.py prints the saved path relative to 00-build, so the temp dir sits
        # inside the gitignored run-output/.
        agent.OUTPUT_DIR.mkdir(exist_ok=True)
        tmp = Path(tempfile.mkdtemp(prefix="test-", dir=agent.OUTPUT_DIR))
        self.addCleanup(shutil.rmtree, tmp, True)
        self.kill_file = tmp / "KILL"
        self.output_dir = tmp / "run-output"
        patcher = mock.patch.multiple(
            agent, KILL_FILE=self.kill_file, OUTPUT_DIR=self.output_dir,
            MAX_ITERATIONS=8, MAX_REVISIONS=3, MAX_ATTEMPTS=3,
            COST_CAP_USD=100.0, RUN_TIMEOUT_S=120.0)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_agent(self, model, which="happy") -> str:
        out = io.StringIO()
        with mock.patch.object(agent, "OpenAI", model), contextlib.redirect_stdout(out):
            agent.run(which)
        return out.getvalue()


class EmbargoTest(RunCase):
    def test_roadmap_withholds_embargoed_entries(self):
        source = (FIXTURES / "roadmap.md").read_text()
        for name in EMBARGOED_NAMES:
            self.assertIn(name, source, "the fixture must still hold the embargoed entry")
        sent = json.dumps(tools.get_roadmap())
        for name in EMBARGOED_NAMES:
            self.assertNotIn(name, sent)
        self.assertIn("Northstar", sent)
        self.assertIn("Vega", sent)

    def test_embargoed_project_prd_summary_withheld(self):
        source = (FIXTURES / "projects.json").read_text()
        for pid, text in zip(("P-ORBIT", "P-PULSAR"), EMBARGOED_PRD_TEXT):
            self.assertIn(text, source, "the fixture must still hold the embargoed PRD summary")
            self.assertNotIn(text, json.dumps(tools.get_project(pid)))

    def test_no_embargoed_text_reaches_the_model(self):
        model = ScriptedModel([
            tool_reply(("get_roadmap", {}),
                       ("get_project", {"project_id": "P-NORTH"}),
                       ("get_project", {"project_id": "P-VEGA"}),
                       ("get_project", {"project_id": "P-ORBIT"}),
                       ("get_project", {"project_id": "P-PULSAR"})),
            text_reply("Weekly status update draft."),
        ])
        self.run_agent(model)
        sent = model.everything_sent()
        self.assertGreaterEqual(len(model.calls), 2)
        self.assertIn("Northstar", sent)
        for text in EMBARGOED_NAMES + EMBARGOED_PRD_TEXT:
            self.assertNotIn(text, sent)


class BoundsTest(RunCase):
    def assert_held(self, out, label):
        self.assertIn(label, out)
        self.assertIn("LAST DRAFT (held, NOT posted", out)
        self.assertNotIn("FINAL STATUS UPDATE", out)

    def test_kill_file_halts_before_any_model_call(self):
        self.kill_file.write_text("")
        model = ScriptedModel([text_reply("draft")])
        out = self.run_agent(model)
        self.assertEqual(len(model.calls), 0)
        self.assert_held(out, "KILL SWITCH")

    def test_run_timeout_halts_at_next_turn(self):
        agent.RUN_TIMEOUT_S = 0.05
        model = ScriptedModel([(0.2, tool_reply(("get_norms", {}))), text_reply("draft")])
        out = self.run_agent(model)
        self.assertEqual(len(model.calls), 1)
        self.assert_held(out, "TIMEOUT")

    def test_model_api_error_halts_without_retry_loop(self):
        model = ScriptedModel([api_error(), text_reply("draft")])
        out = self.run_agent(model)
        self.assertEqual(len(model.calls), 1)
        self.assert_held(out, "MODEL CALL FAILED")
        self.assertFalse(any(self.output_dir.glob("*")), "no draft exists, so nothing is saved")

    def test_critic_api_error_holds_the_draft(self):
        model = ScriptedModel([text_reply("Weekly status update draft.")], critic=api_error())
        out = self.run_agent(model)
        self.assertEqual(len(model.critic_calls), 1)
        self.assert_held(out, "MODEL CALL FAILED")
        saved = (self.output_dir / "status-update-happy.md").read_text()
        self.assertIn("HELD", saved)
        self.assertIn("Weekly status update draft.", saved)

    def test_same_tool_failing_three_times_halts(self):
        model = ScriptedModel([tool_reply(("get_project", {"bogus": "x"}))])
        out = self.run_agent(model)
        self.assertEqual(len(model.calls), 3)
        self.assertLess(len(model.calls), agent.MAX_ITERATIONS)
        self.assert_held(out, "STUCK")

    def test_same_tool_failing_twice_does_not_halt(self):
        bad = tool_reply(("get_project", {"bogus": "x"}))
        model = ScriptedModel([bad, bad, text_reply("Weekly status update draft.")])
        out = self.run_agent(model)
        self.assertEqual(len(model.calls), 3)
        self.assertNotIn("STUCK", out)
        self.assertIn("FINAL STATUS UPDATE", out)


if __name__ == "__main__":
    # argv is dropped: the TDD gate appends the file path, which unittest would read as a test name.
    unittest.main(argv=sys.argv[:1], testRunner=unittest.TextTestRunner(resultclass=_Result, verbosity=2))
