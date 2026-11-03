"""Tests for the project list in the not-found reply of get_project().

Run: .venv/bin/python test_project_list.py

Contract: docs/00-context/001-agent-gates/architecture.md, T-3.
- get_project() for an unknown ID returns known_projects with the IDs of the
  projects that are not embargoed.
- A project is embargoed when its record has status "embargoed" or the flag
  "confidential" (as in T-2). Its ID appears nowhere in the reply.
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

FIXTURES = Path(__file__).parent / "fixtures"
UNKNOWN = "P-DOES-NOT-EXIST"


def record(name: str, status: str = "on_track", flags=()) -> dict:
    return {"name": name, "status": status, "flags": list(flags)}


class _Result(unittest.TextTestResult):
    # pytest-style headers, so each failure prints as its own named block.
    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(f"_____ test_project_list.py::{test.id().split('.', 1)[1]} {flavour} _____")
            self.stream.writeln(err)


class ProjectListTest(unittest.TestCase):
    def use_projects(self, projects: dict) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="test-fixtures-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        shutil.copytree(FIXTURES, tmp, dirs_exist_ok=True)
        (tmp / "projects.json").write_text(json.dumps(projects))
        patcher = mock.patch.object(tools, "FIXTURES", tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def assert_absent(self, reply: dict, ids) -> None:
        text = json.dumps(reply)
        for pid in ids:
            self.assertNotIn(pid, text, f"embargoed ID {pid} appears in the reply")

    def test_shipped_fixtures_list_only_the_projects_that_are_not_embargoed(self):
        reply = tools.get_project(UNKNOWN)
        self.assertCountEqual(reply["known_projects"], ["P-NORTH", "P-VEGA"])
        self.assert_absent(reply, ["P-ORBIT", "P-PULSAR"])

    def test_either_embargo_rule_alone_hides_the_project(self):
        self.use_projects({
            "P-OPEN": record("Open project"),
            "P-HELD": record("Held project", "at_risk", ["launch_hold"]),
            "P-STATUSONLY": record("Statusonly project", "embargoed"),
            "P-FLAGONLY": record("Flagonly project", "on_track", ["confidential"]),
            "P-BOTH": record("Both project", "embargoed", ["confidential", "launch_hold"]),
        })
        reply = tools.get_project(UNKNOWN)
        self.assertCountEqual(reply["known_projects"], ["P-OPEN", "P-HELD"])
        self.assert_absent(reply, ["P-STATUSONLY", "P-FLAGONLY", "P-BOTH"])

    def test_list_is_empty_when_every_project_is_embargoed(self):
        self.use_projects({
            "P-SECRETA": record("Secreta project", "embargoed"),
            "P-SECRETB": record("Secretb project", "on_track", ["confidential"]),
        })
        reply = tools.get_project(UNKNOWN)
        self.assertEqual(reply["known_projects"], [])
        self.assert_absent(reply, ["P-SECRETA", "P-SECRETB"])


if __name__ == "__main__":
    # argv is dropped: the TDD gate appends the file path, which unittest would read as a test name.
    unittest.main(argv=sys.argv[:1], testRunner=unittest.TextTestRunner(resultclass=_Result, verbosity=2))
