#!/usr/bin/env python3
"""
lint_pipeline.py — validate the consistency of pipeline state across the
discovery-to-ship-multi-agents workspace.

Checks idea cards, market-research reports, MVP briefs, and design artifacts
for frontmatter validity, status alignment, required sections, and broken
cross-references. Exits 0 if clean, 1 if errors found (warnings do not fail).

Run from the repo root:
  python scripts/lint_pipeline.py
  python scripts/lint_pipeline.py --json            # machine-readable
  python scripts/lint_pipeline.py --quiet           # counts only
  python scripts/lint_pipeline.py --no-suggestions  # hide fix hints
  python scripts/lint_pipeline.py --no-color        # plain output

This script never modifies any file. It only reports.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


# ─── ANSI color codes ────────────────────────────────────────────────────
class Color:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colored(text: str, color: str, enabled: bool = True) -> str:
    return f"{color}{text}{Color.RESET}" if enabled else text


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    file: str
    line: int  # 0 if not applicable
    rule: str
    message: str
    suggestion: str = ""


# ─── Frontmatter parser (avoids PyYAML dep) ──────────────────────────────

def parse_frontmatter(path: Path) -> dict[str, str]:
    """Return frontmatter dict. Empty dict if no frontmatter."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return {}
    if not text.startswith("---\n"):
        return {}
    end_index = text.find("\n---\n", 4)
    if end_index == -1:
        return {}
    fm_text = text[4:end_index]
    result: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


# ─── Checks ──────────────────────────────────────────────────────────────

def check_idea_cards(issues: list[Issue]) -> None:
    """Each idea card needs frontmatter with slug, status, source, date-captured."""
    ideas_dir = REPO_ROOT / "ideas"
    if not ideas_dir.exists():
        return
    required_fields = {"slug", "status", "source", "date-captured"}
    valid_statuses = {"draft", "triaged", "in-validation", "green-lit", "killed"}

    for card_path in ideas_dir.glob("*.md"):
        if card_path.name == "README.md":
            continue
        fm = parse_frontmatter(card_path)
        rel = str(card_path.relative_to(REPO_ROOT))
        if not fm:
            issues.append(Issue(
                severity="error", file=rel, line=1,
                rule="card.missing-frontmatter",
                message="Idea card has no YAML frontmatter",
                suggestion="Add a frontmatter block with slug, status, source, date-captured per guides/product/idea-discovery-methodology.md §4.",
            ))
            continue
        missing = required_fields - set(fm.keys())
        for field in sorted(missing):
            issues.append(Issue(
                severity="error", file=rel, line=1,
                rule=f"card.missing-{field}",
                message=f"Frontmatter missing required field: {field}",
                suggestion=f"Add `{field}:` to the frontmatter block.",
            ))
        status = fm.get("status", "")
        if status and status not in valid_statuses:
            issues.append(Issue(
                severity="error", file=rel, line=1,
                rule="card.invalid-status",
                message=f"Status `{status}` is not one of {sorted(valid_statuses)}",
                suggestion=f"Set status to one of: {', '.join(sorted(valid_statuses))}",
            ))


def check_status_alignment(issues: list[Issue]) -> None:
    """Cards in `in-validation` / `green-lit` should have corresponding downstream artifacts."""
    ideas_dir = REPO_ROOT / "ideas"
    market_dir = REPO_ROOT / "market-research"
    if not ideas_dir.exists():
        return

    for card_path in ideas_dir.glob("*.md"):
        if card_path.name == "README.md":
            continue
        fm = parse_frontmatter(card_path)
        slug = fm.get("slug", card_path.stem)
        status = fm.get("status", "")
        rel = str(card_path.relative_to(REPO_ROOT))

        if status == "in-validation" and market_dir.exists():
            validation_files = list(market_dir.glob(f"validation-{slug}-*.md"))
            if not validation_files:
                issues.append(Issue(
                    severity="warning", file=rel, line=1,
                    rule="status.in-validation-no-report",
                    message=f"Card status is `in-validation` but no `market-research/validation-{slug}-*.md` exists",
                    suggestion=f"Run `/validate-card {slug}` to produce the validation report, or roll the card back to `triaged`.",
                ))

        if status == "green-lit":
            web_brief = REPO_ROOT / "web-apps" / slug / "MVP.md"
            mobile_brief = REPO_ROOT / "mobile-apps" / slug / "MVP.md"
            if not (web_brief.exists() or mobile_brief.exists()):
                issues.append(Issue(
                    severity="warning", file=rel, line=1,
                    rule="status.green-lit-no-brief",
                    message=f"Card status is `green-lit` but no MVP.md exists in web-apps/{slug}/ or mobile-apps/{slug}/",
                    suggestion=f"Run `/scope-mvp {slug}` to produce the MVP brief, or roll the card back to `in-validation`.",
                ))


def check_brief_picks(issues: list[Issue]) -> None:
    """Briefs with status `green-lit-to-build` must record design-path and build-support."""
    for brief_path in (
        list((REPO_ROOT / "web-apps").glob("*/MVP.md"))
        + list((REPO_ROOT / "mobile-apps").glob("*/MVP.md"))
    ):
        fm = parse_frontmatter(brief_path)
        rel = str(brief_path.relative_to(REPO_ROOT))
        if fm.get("status") == "green-lit-to-build":
            if not fm.get("design-path"):
                issues.append(Issue(
                    severity="warning", file=rel, line=1,
                    rule="brief.missing-design-path",
                    message="Brief is green-lit-to-build but `design-path:` is not set",
                    suggestion="Record design-path: generic|hired per the /scope-mvp pre-build decisions checkpoint.",
                ))
            if not fm.get("build-support"):
                issues.append(Issue(
                    severity="warning", file=rel, line=1,
                    rule="brief.missing-build-support",
                    message="Brief is green-lit-to-build but `build-support:` is not set",
                    suggestion="Record build-support: self|fijara per the /scope-mvp pre-build decisions checkpoint.",
                ))


def check_at_references(issues: list[Issue]) -> None:
    """Verify @path references in tracked markdown files resolve to real files."""
    at_pattern = re.compile(r"(?<!\S)@([a-zA-Z0-9_\-./]+\.(?:md|typ|py|sh|json|yaml|yml|toml))")
    ignored_dirs = {
        "ideas", "market-research", "web-apps", "mobile-apps", "generated",
        "external", ".git", "node_modules", "__pycache__", ".venv", "venv",
    }
    for md_path in REPO_ROOT.rglob("*.md"):
        if any(part in ignored_dirs for part in md_path.relative_to(REPO_ROOT).parts):
            continue
        try:
            text = md_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        in_code = False
        for line_num, line in enumerate(text.splitlines(), start=1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code or "`" in line:
                continue
            for match in at_pattern.finditer(line):
                ref = match.group(1)
                target = REPO_ROOT / ref
                if not target.exists():
                    issues.append(Issue(
                        severity="warning",
                        file=str(md_path.relative_to(REPO_ROOT)),
                        line=line_num,
                        rule="link.broken-at-reference",
                        message=f"@{ref} does not resolve to an existing file",
                        suggestion="Fix the path or remove the reference if the target was renamed/removed.",
                    ))


def check_slug_uniqueness(issues: list[Issue]) -> None:
    """A slug must be unique across ideas/, ideas/killed/, web-apps/, mobile-apps/."""
    locations: dict[str, list[str]] = {}

    def record(slug: str, path: str) -> None:
        locations.setdefault(slug, []).append(path)

    ideas_dir = REPO_ROOT / "ideas"
    if ideas_dir.exists():
        for md in ideas_dir.glob("*.md"):
            if md.name == "README.md":
                continue
            record(md.stem, str(md.relative_to(REPO_ROOT)))

    killed_dir = REPO_ROOT / "ideas" / "killed"
    if killed_dir.exists():
        for md in killed_dir.glob("*.md"):
            record(md.stem, str(md.relative_to(REPO_ROOT)))

    for top in ("web-apps", "mobile-apps"):
        d = REPO_ROOT / top
        if not d.exists():
            continue
        for sub in d.iterdir():
            if sub.is_dir() and sub.name != ".gitkeep":
                record(sub.name, str(sub.relative_to(REPO_ROOT)))

    for slug, paths in locations.items():
        if len(paths) > 1:
            issues.append(Issue(
                severity="error",
                file=paths[0],
                line=0,
                rule="slug.collision",
                message=f"Slug `{slug}` is used in {len(paths)} places: {', '.join(paths)}",
                suggestion="Slugs must be unique across ideas/, ideas/killed/, web-apps/, mobile-apps/. Rename one of the conflicting artifacts.",
            ))


def check_required_sections_validation(issues: list[Issue]) -> None:
    """Validation reports must have the locked verdict-format sections."""
    market_dir = REPO_ROOT / "market-research"
    if not market_dir.exists():
        return
    required_sections = [
        "Verdict", "Confidence", "Findings",
        "What I could not verify", "Sources",
    ]
    for report_path in market_dir.glob("validation-*.md"):
        try:
            text = report_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for section in required_sections:
            # Accept H2 or H3 (sub-reviewer reports nest under H3 sometimes)
            if not re.search(rf"^#{{2,4}}\s+{re.escape(section)}\b", text, re.MULTILINE):
                issues.append(Issue(
                    severity="warning",
                    file=str(report_path.relative_to(REPO_ROOT)),
                    line=0,
                    rule="report.missing-section",
                    message=f"Validation report missing required section: {section}",
                    suggestion="Add the section per guides/product/idea-validation-methodology.md §5.",
                ))


# ─── Reporting ───────────────────────────────────────────────────────────

def report_human(issues: list[Issue], use_color: bool, quiet: bool, fix_suggestions: bool) -> int:
    by_severity: dict[str, list[Issue]] = defaultdict(list)
    for issue in issues:
        by_severity[issue.severity].append(issue)
    errors = by_severity["error"]
    warnings = by_severity["warning"]

    if not quiet:
        for sev, items in [("error", errors), ("warning", warnings)]:
            if not items:
                continue
            label_color = Color.RED if sev == "error" else Color.YELLOW
            print(colored(f"\n=== {sev.upper()}S ({len(items)}) ===", label_color, use_color))
            for issue in items:
                loc = f"{issue.file}:{issue.line}" if issue.line else issue.file
                print(f"  {colored(loc, Color.CYAN, use_color)}  [{issue.rule}]")
                print(f"    {issue.message}")
                if fix_suggestions and issue.suggestion:
                    print(f"    {colored('→ ' + issue.suggestion, Color.DIM, use_color)}")

    print(colored("\n=== Summary ===", Color.BOLD, use_color))
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if not errors and not warnings:
        print(colored("\n  Pipeline state is clean. ✓", Color.GREEN, use_color))
        return 0
    if not errors:
        print(colored("\n  Warnings only — workspace usable.", Color.YELLOW, use_color))
        return 0
    print(colored("\n  Errors present — fix and re-run.", Color.RED, use_color))
    return 1


def report_json(issues: list[Issue]) -> int:
    payload = {
        "summary": {
            "errors": sum(1 for i in issues if i.severity == "error"),
            "warnings": sum(1 for i in issues if i.severity == "warning"),
            "total": len(issues),
        },
        "issues": [asdict(i) for i in issues],
    }
    print(json.dumps(payload, indent=2))
    return 1 if payload["summary"]["errors"] else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate pipeline state consistency.")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-suggestions", action="store_true")
    args = parser.parse_args()

    issues: list[Issue] = []
    check_idea_cards(issues)
    check_status_alignment(issues)
    check_brief_picks(issues)
    check_at_references(issues)
    check_slug_uniqueness(issues)
    check_required_sections_validation(issues)

    if args.json:
        return report_json(issues)
    use_color = not args.no_color and sys.stdout.isatty()
    return report_human(issues, use_color, args.quiet, not args.no_suggestions)


if __name__ == "__main__":
    sys.exit(main())
