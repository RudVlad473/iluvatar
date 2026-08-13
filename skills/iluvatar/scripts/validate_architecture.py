#!/usr/bin/env python3
"""
validate_architecture.py — structural checks on iluvatar's emitted
HIGH-LEVEL-ARCHITECTURE.md.

Phase 6a says the output schema is frozen and its section names are the
contract downstream consumers parse by. Nothing checked that before this
script existed — a renamed heading, a missing frontmatter key, or a
section left silently blank would only surface once some other tool
failed to find what it was looking for.

What it checks
───────────────
  frontmatter   `archetypes`, `primary_artifact`, and `budget_notes` are
                all present and non-empty.
  sections      All nine required `#` headings are present, in the
                schema's order, spelled exactly as SKILL.md's Phase 6a
                names them.
  emptiness     No required section is blank. A section may legitimately
                say "none" — that is not emptiness, it is a heading with
                content — but a heading followed by nothing at all is a
                downstream consumer finding a section and getting no
                signal from it either way.
  5c catch-all  The Cross-cutting section contains a non-empty `5C
                catch-all` line. Phase 5C's result is required content,
                not an internal step the reader has to trust happened —
                see SKILL.md's Phase 5C and 6a.

What it refuses to decide
──────────────────────────
  Whether a section's content is genuine — traced to Phase 1-5 work
  rather than invented, or whether a Provenance tag is accurate. That is
  a judgment call about substance, not structure, and this script reads
  structure only.

Usage
─────
  python validate_architecture.py path/to/HIGH-LEVEL-ARCHITECTURE.md
  python validate_architecture.py path/to/HIGH-LEVEL-ARCHITECTURE.md --json

Exit codes
──────────
  0  Every check found nothing wrong
  1  A problem was found
  2  The target file does not exist

Dependencies
────────────
None. The standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FRONTMATTER_KEYS = ("archetypes", "primary_artifact", "budget_notes")

# Order matters: this is Phase 6a's schema order, and check_sections treats it
# as the contract.
REQUIRED_SECTIONS = (
    "Classification",
    "Flow Spine",
    "Cross-cutting",
    "Deferred",
    "Known Constraints",
    "Out of Scope",
    "Open Questions",
    "Provenance",
    "How to Verify",
)

HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
CROSS_CUTTING_SECTION = "Cross-cutting"
FIVE_C_MARKER_RE = re.compile(r"\*\*5C catch-all:\*\*\s*(\S.*)?$", re.MULTILINE)

EXIT_CLEAN = 0
EXIT_PROBLEMS = 1
EXIT_NO_TARGET = 2


def parse_frontmatter(text: str) -> dict[str, str]:
    """Flat `key: value` frontmatter reader; indented lines fold into the key above.

    Deliberately not a YAML parser — same reasoning and same shape as curator's
    own `validate_skill_md.py:parse_frontmatter`: this file's frontmatter is
    always three flat keys, one of them (`budget_notes`) often line-wrapped.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}

    fields: dict[str, str] = {}
    last_key: str | None = None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        if line[:1].isspace():
            if last_key:
                fields[last_key] = f"{fields[last_key]} {line.strip()}".strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            last_key = key.strip()
            fields[last_key] = value.strip()
        else:
            last_key = None
    return fields


def body_after_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text if end == -1 else text[end + 4 :]


def check_frontmatter(fields: dict[str, str]) -> list[str]:
    return [
        f"frontmatter: missing or empty required key {key!r}"
        for key in REQUIRED_FRONTMATTER_KEYS
        if not fields.get(key)
    ]


def check_sections(headings: list[str]) -> list[str]:
    """Presence and ordering of the required sections among the headings found."""
    problems = [
        f"missing required section: {section!r}"
        for section in REQUIRED_SECTIONS
        if section not in headings
    ]
    found_required = [h for h in headings if h in REQUIRED_SECTIONS]
    expected_order = [s for s in REQUIRED_SECTIONS if s in headings]
    if found_required != expected_order:
        problems.append(
            f"required sections are out of order: found {found_required}, expected {expected_order}"
        )
    return problems


def check_empty_sections(body: str) -> list[str]:
    """A required section with no content at all — not even 'none'."""
    matches = list(HEADING_RE.finditer(body))
    problems = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        if heading not in REQUIRED_SECTIONS:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        if not body[start:end].strip():
            problems.append(f'section {heading!r} is empty — write the heading plus "none"')
    return problems


def check_five_c_catchall(body: str) -> list[str]:
    """The Cross-cutting section states Phase 5C's catch-all result explicitly.

    Presence-only, like every other check here: this cannot tell a genuinely-run
    catch-all pass from one that just wrote the marker — see the module
    docstring's "What it refuses to decide".
    """
    matches = list(HEADING_RE.finditer(body))
    problems = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        if heading != CROSS_CUTTING_SECTION:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        section_text = body[start:end]
        marker = FIVE_C_MARKER_RE.search(section_text)
        if marker is None:
            problems.append(
                "section 'Cross-cutting' has no '5C catch-all' line — state what "
                "Phase 5C surfaced, or 'none beyond 5A/5B'"
            )
        elif not (marker.group(1) or "").strip():
            problems.append("section 'Cross-cutting' has an empty '5C catch-all' line")
    return problems


def validate_target(path: Path) -> dict:
    """Run every check against one HIGH-LEVEL-ARCHITECTURE.md. Never raises."""
    result: dict = {"target": str(path), "problems": []}

    if not path.is_file():
        result["problems"].append(f"target file does not exist: {path}")
        result["exit_code"] = EXIT_NO_TARGET
        return result

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        result["problems"].append(f"target file could not be read: {exc}")
        result["exit_code"] = EXIT_NO_TARGET
        return result

    result["problems"] += check_frontmatter(parse_frontmatter(text))

    body = body_after_frontmatter(text)
    headings = [m.group(1).strip() for m in HEADING_RE.finditer(body)]
    result["problems"] += check_sections(headings)
    result["problems"] += check_empty_sections(body)
    result["problems"] += check_five_c_catchall(body)

    result["exit_code"] = EXIT_PROBLEMS if result["problems"] else EXIT_CLEAN
    return result


def _print_human_readable(result: dict) -> None:
    print(f"\niluvatar architecture validation: {result['target']}")
    if not result["problems"]:
        print("  clean")
        return
    for problem in result["problems"]:
        print(f"  {problem}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="Path to HIGH-LEVEL-ARCHITECTURE.md")
    parser.add_argument(
        "--json", dest="json_out", action="store_true", help="Emit machine-readable JSON"
    )
    args = parser.parse_args()

    result = validate_target(Path(args.target))

    if args.json_out:
        print(json.dumps(result, indent=2))
    else:
        _print_human_readable(result)

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
