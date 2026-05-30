#!/usr/bin/env python3
"""
changelog_helper.py — auto-extract commits since the last tag (or a given
range) and format them as a CHANGELOG entry stub for you to edit.

Groups commits by conventional-commit prefix (feat:, fix:, docs:, refactor:,
test:, chore:, ...) and outputs a Markdown stub matching the section
structure used by CHANGELOG.md.

Output goes to stdout — pipe or copy into CHANGELOG.md.

Run from the repo root:
  python scripts/changelog_helper.py                       # since latest tag
  python scripts/changelog_helper.py --since v0.3.0        # since a specific tag
  python scripts/changelog_helper.py --range main..feature # arbitrary range
  python scripts/changelog_helper.py --header "[0.4.0] — 2026-06-15"
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Conventional-commit prefix → CHANGELOG section heading
SECTION_MAP = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": "Documentation",
    "refactor": "Changed",
    "perf": "Changed",
    "style": "Changed",
    "test": "Tests",
    "build": "Tooling",
    "ci": "Tooling",
    "chore": "Tooling",
    "revert": "Reverted",
}

SECTION_ORDER = [
    "Added", "Changed", "Fixed", "Removed", "Deprecated", "Security",
    "Documentation", "Tests", "Tooling", "Reverted", "Other",
]

CONVENTIONAL = re.compile(
    r"^(?P<type>\w+)(?:\((?P<scope>[\w-]+)\))?(?P<breaking>!)?:\s*(?P<message>.+)$"
)


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git"] + args, cwd=REPO_ROOT, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"git {' '.join(args)} failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def latest_tag() -> str:
    try:
        return run_git(["describe", "--tags", "--abbrev=0"])
    except SystemExit:
        return ""


def commits_in_range(rev_range: str) -> list[str]:
    """Return list of commit subject lines in the range, oldest first."""
    output = run_git(["log", "--reverse", rev_range, "--pretty=format:%s"])
    if not output:
        return []
    return [line for line in output.splitlines() if line.strip()]


def categorize(subjects: list[str]) -> dict[str, list[str]]:
    by_section: dict[str, list[str]] = defaultdict(list)
    for subject in subjects:
        match = CONVENTIONAL.match(subject)
        if match:
            cc_type = match.group("type").lower()
            scope = match.group("scope")
            breaking = match.group("breaking") == "!"
            message = match.group("message")
            section = SECTION_MAP.get(cc_type, "Other")
            entry = f"- {message}"
            if scope:
                entry = f"- **{scope}**: {message}"
            if breaking:
                entry = f"- **BREAKING**: {message}"
            by_section[section].append(entry)
        else:
            by_section["Other"].append(f"- {subject}")
    return by_section


def format_stub(by_section: dict[str, list[str]], header: str) -> str:
    out = [f"## {header}", ""]
    for section in SECTION_ORDER:
        if section not in by_section:
            continue
        out.append(f"### {section}")
        for entry in by_section[section]:
            out.append(entry)
        out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a CHANGELOG entry stub from git history.")
    parser.add_argument("--since", help="Tag or ref as the lower bound (default: latest tag)")
    parser.add_argument("--range", dest="commit_range",
                        help="Explicit git revision range, e.g. 'main..feature'")
    parser.add_argument("--header", default="[Unreleased]",
                        help="Section header for the stub (default: [Unreleased])")
    args = parser.parse_args()

    if args.commit_range:
        rev_range = args.commit_range
    elif args.since:
        rev_range = f"{args.since}..HEAD"
    else:
        tag = latest_tag()
        if not tag:
            print("No tags found in this repo. Use --range or --since explicitly.", file=sys.stderr)
            return 1
        rev_range = f"{tag}..HEAD"
        print(f"# Using range: {rev_range} (latest tag: {tag})", file=sys.stderr)

    subjects = commits_in_range(rev_range)
    if not subjects:
        print(f"# No commits in range {rev_range}", file=sys.stderr)
        return 0

    by_section = categorize(subjects)
    print(format_stub(by_section, args.header))
    return 0


if __name__ == "__main__":
    sys.exit(main())
