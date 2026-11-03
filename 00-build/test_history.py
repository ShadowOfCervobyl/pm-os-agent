"""Tests for what past updates let the model read and for the sprint check.

Run: .venv/bin/python test_history.py

Contract: docs/00-context/001-agent-gates/architecture.md, T-2.
- search_past_updates() returns no entry from past-updates.json or decision-log.json
  that names an embargoed project, fallback entries included. An entry names a
  project when the project's short name (the first word of its name) appears in
  the entry's project, summary or theme, ignoring case. Every other entry is
  still returned.
- A draft is rejected when it holds `Sprint <number>`, ignoring case, and that
  text is absent from the source log. An escalation is never rejected for it.
  A rejection uses one of the MAX_REVISIONS rounds.
As in test_cortex.py, only the model is faked.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import tools  # noqa: E402
from test_cortex import ACTIVITY, RunCase, ScriptedModel, text_reply, tool_reply  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
EMBARGOED = ("orbit", "pulsar")
# Text that only the embargoed entries in the shipped fixtures hold.
EMBARGOED_ENTRY_TEXT = (
    "Orbit is embargoed; status is shared only in the core-team channel",
    "Pulsar joins the confidential/embargoed set with Orbit",
    "Orbit stays embargoed and is never referenced",
)
PROJECT = ("get_project", {"project_id": "P-NORTH"})  # its record holds "Sprint 25"
HELD = "LAST DRAFT (held, NOT posted"
ACCEPTED = "FINAL STATUS UPDATE"


def draft(sprint_text: str) -> str:
    return (f"DONE: Northstar weekly update, queued for your review. Merged #820 and #823. "
            f"Open: #825. {sprint_text}")


def entry_text(entry: dict) -> str:
    return f"{entry.get('project', '')} {entry.get('summary', '')} {entry.get('theme', '')}".lower()


def names_any(entry: dict, short_names) -> bool:
    return any(name in entry_text(entry) for name in short_names)


class _Result(unittest.TextTestResult):
    # pytest-style headers, so each failure prints as its own named block.
    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(f"_____ test_history.py::{test.id().split('.', 1)[1]} {flavour} _____")
            self.stream.writeln(err)


class FixtureCase(unittest.TestCase):
    """Points tools at a copy of the fixtures that a test may edit."""

    def use_fixtures(self, past=None, decisions=None, projects=None, tasks=None) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="test-fixtures-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        shutil.copytree(FIXTURES, tmp, dirs_exist_ok=True)
        for name, data in (("past-updates.json", past), ("decision-log.json", decisions),
                           ("projects.json", projects)):
            if data is not None:
                (tmp / name).write_text(json.dumps(data))
        for which, body in (tasks or {}).items():
            (tmp / f"task-{which}.md").write_text(body)
        patcher = mock.patch.object(tools, "FIXTURES", tmp)
        patcher.start()
        self.addCleanup(patcher.stop)


def load(name: str):
    return json.loads((FIXTURES / name).read_text())


class PastUpdatesTest(FixtureCase):
    QUERIES = ("orbit", "Pulsar", "ORBIT pulsar", "confidential embargo", "orbit launch status",
               "core-team channel", "", "zzzz qqqq")

    def test_fixtures_still_hold_embargoed_entries(self):
        corpus = load("past-updates.json") + load("decision-log.json")
        for name in EMBARGOED:
            self.assertTrue(any(names_any(e, [name]) for e in corpus), name)

    def test_no_query_returns_an_entry_that_names_an_embargoed_project(self):
        for query in self.QUERIES:
            with self.subTest(query=query):
                result = tools.search_past_updates(query)
                for entry in result["matches"]:
                    self.assertFalse(names_any(entry, EMBARGOED), entry)
                sent = json.dumps(result).lower()
                for text in EMBARGOED_ENTRY_TEXT:
                    self.assertNotIn(text.lower(), sent)

    def test_entries_about_other_projects_are_still_returned(self):
        corpus = load("past-updates.json") + load("decision-log.json")
        for query, project in (("vega", "Vega"), ("northstar", "Northstar")):
            with self.subTest(query=query):
                expected = [e for e in corpus if e["project"] == project]
                self.assertGreaterEqual(len(expected), 3)
                matches = tools.search_past_updates(query)["matches"]
                for entry in expected:
                    self.assertIn(entry, matches)

    def test_entries_on_a_shared_theme_are_still_returned(self):
        # "sprint planning" hits a Northstar update and a team decision, neither embargoed.
        matches = tools.search_past_updates("sprint planning")["matches"]
        summaries = [e["summary"] for e in matches]
        self.assertIn("Decision: backlog batches larger than 10 stories go to sprint planning "
                      "to be sized, not straight into the tracker.", summaries)
        self.assertTrue(any(e["project"] == "Northstar" and "sprint planning" in e["theme"]
                            for e in matches))

    def test_fallback_never_returns_an_embargoed_entry(self):
        # Embargoed entries first, so a fallback that takes the head of the corpus meets them.
        orbit = {"week": "2026-W01", "project": "Orbit", "summary": "Orbit beta cohort grew.",
                 "theme": "status update format"}
        pulsar = {"week": "2026-W01", "project": "Pulsar", "summary": "Pulsar index rebuilt.",
                  "theme": "status update format"}
        self.use_fixtures(past=[orbit, pulsar] + load("past-updates.json"))
        for query in ("", "   ", "zzzz qqqq", "#", "ab"):
            with self.subTest(query=query):
                result = tools.search_past_updates(query)
                for entry in result["matches"]:
                    self.assertFalse(names_any(entry, EMBARGOED), entry)
                self.assertNotIn("Orbit beta cohort", json.dumps(result))
                self.assertNotIn("Pulsar index", json.dumps(result))

    def test_a_short_name_in_summary_or_theme_hides_the_entry_whatever_the_case(self):
        named = [
            {"date": "2026-01-01", "project": "team", "summary": "Moved two engineers to ORBIT.",
             "theme": "staffing"},
            {"date": "2026-01-02", "project": "team", "summary": "Moved two engineers.",
             "theme": "staffing, pulsar"},
            {"date": "2026-01-03", "project": "PuLsAr", "summary": "Moved two engineers.",
             "theme": "staffing"},
        ]
        kept = {"date": "2026-01-04", "project": "team", "summary": "Moved two engineers to Vega.",
                "theme": "staffing"}
        self.use_fixtures(decisions=named + [kept])
        matches = tools.search_past_updates("staffing engineers")["matches"]
        for entry in named:
            self.assertNotIn(entry, matches)
        self.assertIn(kept, matches)

    def test_embargo_comes_from_projects_json_status_or_flag(self):
        projects = load("projects.json")
        projects["P-COMET"] = {"name": "Comet (partner pilot)", "status": "on_track",
                               "flags": ["confidential"], "activity": []}
        projects["P-NOVA"] = {"name": "Nova (pricing rework)", "status": "embargoed",
                              "flags": [], "activity": []}
        projects["P-ATLAS"] = {"name": "Atlas (data export)", "status": "on_track",
                               "flags": ["launch_hold"], "activity": []}
        entries = [{"week": "2026-W02", "project": p, "summary": f"{p} moved forward this week.",
                    "theme": "weekly progress"} for p in ("Comet", "Nova", "Atlas")]
        self.use_fixtures(past=load("past-updates.json") + entries, projects=projects)
        matches = tools.search_past_updates("weekly progress forward")["matches"]
        self.assertNotIn(entries[0], matches, "a confidential flag embargoes Comet")
        self.assertNotIn(entries[1], matches, "status embargoed embargoes Nova")
        self.assertIn(entries[2], matches, "Atlas is neither, so its entry stays")

    def test_only_the_first_word_of_the_name_is_the_short_name(self):
        # Orbit is "Orbit (unreleased AI features)", Pulsar is "Pulsar (next-gen search,
        # unreleased)". Words after the first do not name the project.
        kept = [{"date": "2026-01-05", "project": "team",
                 "summary": "Unreleased AI features need a review of next-gen search copy.",
                 "theme": "features, search, unreleased"}]
        self.use_fixtures(decisions=load("decision-log.json") + kept)
        matches = tools.search_past_updates("unreleased features search")["matches"]
        self.assertIn(kept[0], matches)
        for entry in matches:
            self.assertFalse(names_any(entry, EMBARGOED), entry)


class PastUpdatesReachModelTest(RunCase):
    def test_no_embargoed_past_update_reaches_the_model(self):
        model = ScriptedModel([
            tool_reply(ACTIVITY,
                       ("search_past_updates", {"query": "orbit pulsar"}),
                       ("search_past_updates", {"query": "confidential embargo"}),
                       ("search_past_updates", {"query": ""}),
                       ("search_past_updates", {})),
            text_reply(draft("Activation 41% to 43% week over week.")),
        ])
        self.run_agent(model)
        sent = model.everything_sent()
        self.assertGreaterEqual(len(model.calls), 2)
        self.assertIn("Northstar", sent)
        for text in ("Orbit", "Pulsar") + EMBARGOED_ENTRY_TEXT:
            self.assertFalse(text in sent, f"{text!r} reached the model")


class SprintGateTest(RunCase, FixtureCase):
    def assert_held(self, out):
        self.assertIn(HELD, out)
        self.assertNotIn(ACCEPTED, out)
        for saved in self.output_dir.glob("*"):
            self.assertNotIn("accepted by validator", saved.read_text())

    def assert_accepted(self, out):
        self.assertIn(ACCEPTED, out)
        self.assertNotIn(HELD, out)

    def test_source_log_holds_no_sprint_26(self):
        # The test drafts below rely on this: P-NORTH says Sprint 25 and nothing says 26.
        self.assertIn("Sprint 25", json.dumps(tools.get_project("P-NORTH")))
        for text in (json.dumps(tools.get_activity("P-NORTH")),
                     tools.get_task("happy")["body"], tools.get_task("jailbreak")["body"]):
            self.assertNotIn("sprint 26", text.lower())
            self.assertNotIn("sprint 25", text.lower())

    def test_draft_naming_a_sprint_absent_from_the_source_is_held(self):
        for text in ("Next up: Sprint 26 planning.", "Next up: sprint 26 planning.",
                     "Next up: SPRINT 26 planning.", "Sprint 26"):
            with self.subTest(text=text):
                model = ScriptedModel([tool_reply(ACTIVITY), text_reply(draft(text))])
                self.assert_held(self.run_agent(model))

    def test_sprint_from_get_project_is_not_in_the_source_unless_pulled(self):
        # Sprint 25 sits in P-NORTH's record, but only get_activity ran.
        model = ScriptedModel([tool_reply(ACTIVITY), text_reply(draft("Sprint 25 closes Friday."))])
        self.assert_held(self.run_agent(model))

    def test_draft_naming_a_sprint_the_source_holds_passes(self):
        model = ScriptedModel([tool_reply(ACTIVITY, PROJECT),
                               text_reply(draft("Sprint 25 closes Friday."))])
        self.assert_accepted(self.run_agent(model))

    def test_sprint_in_the_task_brief_counts_as_source(self):
        body = tools.get_task("happy")["body"] + "\nWe are mid-way through Sprint 31.\n"
        self.use_fixtures(tasks={"sprint": body})
        model = ScriptedModel([tool_reply(ACTIVITY), text_reply(draft("Sprint 31 is on track."))])
        self.assert_accepted(self.run_agent(model, "sprint"))

    def test_longer_sprint_number_than_the_source_is_held(self):
        model = ScriptedModel([tool_reply(ACTIVITY, PROJECT),
                               text_reply(draft("Sprint 250 closes Friday."))])
        self.assert_held(self.run_agent(model))

    def test_one_absent_sprint_among_present_ones_is_held(self):
        model = ScriptedModel([tool_reply(ACTIVITY, PROJECT),
                               text_reply(draft("Sprint 25 closes Friday; Sprint 26 starts Monday."))])
        self.assert_held(self.run_agent(model))

    def test_draft_without_a_sprint_number_is_not_held_for_it(self):
        model = ScriptedModel([tool_reply(ACTIVITY),
                               text_reply(draft("Stories proposed for next sprint planning."))])
        self.assert_accepted(self.run_agent(model))

    def test_escalation_naming_an_absent_sprint_is_not_held_for_it(self):
        for output in ("ESCALATE: the brief asks for Sprint 26 dates, which no source holds.",
                       "**ESCALATE** Sprint 26 is not in any source."):
            with self.subTest(output=output):
                model = ScriptedModel([tool_reply(ACTIVITY), text_reply(output)])
                out = self.run_agent(model)
                self.assert_accepted(out)
                self.assertEqual(len(model.critic_calls), 1, "the critic still runs on an escalation")

    def test_rejected_sprint_draft_goes_back_to_cortex_and_can_recover(self):
        good = draft("Activation 41% to 43% week over week.")
        model = ScriptedModel([tool_reply(ACTIVITY), text_reply(draft("Sprint 26 starts Monday.")),
                               text_reply(good)])
        out = self.run_agent(model)
        self.assertEqual(len(model.calls), 3)
        self.assertEqual(len(model.critic_calls), 2, "the critic runs on the rejected draft too")
        last = model.calls[2]["messages"][-1]
        self.assertIsInstance(last, dict)
        self.assertEqual(last.get("role"), "user")
        self.assertIn("sprint", str(last.get("content") or "").lower())
        self.assert_accepted(out)
        saved = (self.output_dir / "status-update-happy.md").read_text()
        self.assertIn(good, saved)

    def test_sprint_draft_rejected_every_round_is_held_at_the_revision_cap(self):
        # RunCase sets MAX_REVISIONS to 3: four drafts, four critic calls, then the hold.
        model = ScriptedModel([tool_reply(ACTIVITY), text_reply(draft("Sprint 26 starts Monday."))])
        out = self.run_agent(model)
        self.assertEqual(len(model.critic_calls), 4)
        self.assertIn("REVISION CAP", out)
        self.assert_held(out)


if __name__ == "__main__":
    # argv is dropped: the TDD gate appends the file path, which unittest would read as a test name.
    unittest.main(argv=sys.argv[:1], testRunner=unittest.TextTestRunner(resultclass=_Result, verbosity=2))
