#!/usr/bin/env python3
"""
test_validate_architecture.py - verification for iluvatar's output validator.

Standard library only:

    python test_validate_architecture.py

The rule these cases exist to hold: a HIGH-LEVEL-ARCHITECTURE.md missing a
frontmatter key, missing or reordering a required section, or leaving one
truly blank, is reported as a problem — never accepted because the file
happened to have nine `#` headings somewhere in it.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_architecture

GOOD_DOC = """\
---
archetypes: [crud-service, background-jobs]
primary_artifact: a saved article
budget_notes: "trivial scale; see Provenance"
---
# Classification
One sentence per archetype.

# Flow Spine
stage one — a → b

# Cross-cutting
Runtime concerns here.

**5C catch-all:** none beyond 5A/5B.

# Deferred
none

# Known Constraints
Self-hosted on one server.

# Out of Scope
Browser extension.

# Open Questions
Is 7/day representative?

# Provenance
budget_notes — assumption.

# How to Verify
Nothing to reproduce; no script was run.
"""


class ParseFrontmatterTests(unittest.TestCase):
    def test_reads_all_three_keys(self):
        fields = validate_architecture.parse_frontmatter(GOOD_DOC)
        self.assertEqual(fields["archetypes"], "[crud-service, background-jobs]")
        self.assertEqual(fields["primary_artifact"], "a saved article")

    def test_folds_a_wrapped_value_onto_one_line(self):
        text = (
            '---\narchetypes: [x]\nprimary_artifact: y\nbudget_notes: "line one\n  line two"\n---\n'
        )
        fields = validate_architecture.parse_frontmatter(text)
        self.assertIn("line one", fields["budget_notes"])
        self.assertIn("line two", fields["budget_notes"])


class CheckFrontmatterTests(unittest.TestCase):
    def test_complete_frontmatter_reports_nothing(self):
        fields = validate_architecture.parse_frontmatter(GOOD_DOC)
        self.assertEqual(validate_architecture.check_frontmatter(fields), [])

    def test_a_missing_key_is_reported(self):
        fields = {"archetypes": "[x]", "primary_artifact": "y"}
        problems = validate_architecture.check_frontmatter(fields)
        self.assertTrue(any("budget_notes" in problem for problem in problems))

    def test_an_empty_key_is_reported_like_a_missing_one(self):
        fields = {"archetypes": "[x]", "primary_artifact": "", "budget_notes": "z"}
        problems = validate_architecture.check_frontmatter(fields)
        self.assertTrue(any("primary_artifact" in problem for problem in problems))


class CheckSectionsTests(unittest.TestCase):
    def test_all_nine_present_and_ordered_reports_nothing(self):
        body = validate_architecture.body_after_frontmatter(GOOD_DOC)
        headings = [m.group(1).strip() for m in validate_architecture.HEADING_RE.finditer(body)]
        self.assertEqual(validate_architecture.check_sections(headings), [])

    def test_a_missing_section_is_reported(self):
        headings = [h for h in validate_architecture.REQUIRED_SECTIONS if h != "Provenance"]
        problems = validate_architecture.check_sections(headings)
        self.assertTrue(any("Provenance" in problem for problem in problems))

    def test_sections_out_of_order_are_reported(self):
        headings = list(validate_architecture.REQUIRED_SECTIONS)
        headings[0], headings[1] = headings[1], headings[0]
        problems = validate_architecture.check_sections(headings)
        self.assertTrue(any("out of order" in problem for problem in problems))


class CheckEmptySectionsTests(unittest.TestCase):
    def test_a_section_saying_none_is_not_empty(self):
        body = validate_architecture.body_after_frontmatter(GOOD_DOC)
        problems = validate_architecture.check_empty_sections(body)
        self.assertEqual(problems, [])

    def test_a_truly_blank_section_is_reported(self):
        body = "# Classification\n\n# Flow Spine\nsomething\n"
        problems = validate_architecture.check_empty_sections(body)
        self.assertTrue(any("Classification" in problem for problem in problems))


class CheckFiveCCatchallTests(unittest.TestCase):
    def test_a_stated_result_reports_nothing(self):
        body = validate_architecture.body_after_frontmatter(GOOD_DOC)
        self.assertEqual(validate_architecture.check_five_c_catchall(body), [])

    def test_a_missing_marker_is_reported(self):
        body = "# Cross-cutting\nRuntime concerns here.\n\n# Deferred\nnone\n"
        problems = validate_architecture.check_five_c_catchall(body)
        self.assertTrue(any("no '5C catch-all' line" in problem for problem in problems))

    def test_an_empty_marker_is_reported(self):
        body = "# Cross-cutting\nRuntime concerns here.\n\n**5C catch-all:**\n\n# Deferred\nnone\n"
        problems = validate_architecture.check_five_c_catchall(body)
        self.assertTrue(any("empty '5C catch-all' line" in problem for problem in problems))

    def test_a_surfaced_concern_satisfies_the_check(self):
        body = (
            "# Cross-cutting\nRuntime concerns here.\n\n"
            "**5C catch-all:** code/module organization is unaddressed by 5A — "
            "candidate addition to the invariant list.\n\n# Deferred\nnone\n"
        )
        self.assertEqual(validate_architecture.check_five_c_catchall(body), [])


class ValidateTargetTests(unittest.TestCase):
    def test_missing_file_is_exit_2(self):
        result = validate_architecture.validate_target(Path("does-not-exist.md"))
        self.assertEqual(result["exit_code"], validate_architecture.EXIT_NO_TARGET)

    def test_a_fully_valid_document_is_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "HIGH-LEVEL-ARCHITECTURE.md"
            path.write_text(GOOD_DOC, encoding="utf-8")
            result = validate_architecture.validate_target(path)
            self.assertEqual(result["exit_code"], validate_architecture.EXIT_CLEAN)
            self.assertEqual(result["problems"], [])

    def test_a_document_missing_a_section_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = GOOD_DOC.split("# Provenance", maxsplit=1)[0]
            path = Path(tmp) / "HIGH-LEVEL-ARCHITECTURE.md"
            path.write_text(broken, encoding="utf-8")
            result = validate_architecture.validate_target(path)
            self.assertEqual(result["exit_code"], validate_architecture.EXIT_PROBLEMS)

    def test_a_document_missing_the_5c_catchall_line_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = GOOD_DOC.replace("\n**5C catch-all:** none beyond 5A/5B.\n", "")
            path = Path(tmp) / "HIGH-LEVEL-ARCHITECTURE.md"
            path.write_text(broken, encoding="utf-8")
            result = validate_architecture.validate_target(path)
            self.assertEqual(result["exit_code"], validate_architecture.EXIT_PROBLEMS)
            self.assertTrue(any("5C catch-all" in p for p in result["problems"]))


if __name__ == "__main__":
    unittest.main()
