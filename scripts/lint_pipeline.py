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
    """Each idea card needs frontmatter with slug, status, source, date-captured.

    Cards live at `ideas/<run-id>/<slug>.md` (active) and `ideas/killed/<run-id>/<slug>.md`
    (killed). README.md and .gitkeep are skipped.
    """
    ideas_dir = REPO_ROOT / "ideas"
    if not ideas_dir.exists():
        return
    required_fields = {"slug", "status", "source", "date-captured"}
    valid_statuses = {"draft", "triaged", "in-validation", "green-lit", "killed"}

    # Walk all nested .md files (run folders + killed/run folders). Skip README.md.
    for card_path in ideas_dir.rglob("*.md"):
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
    """Cards in `in-validation` / `green-lit` should have corresponding downstream artifacts.

    Validation reports live at `market-research/<run-id>/validation-<slug>.md`.
    """
    ideas_dir = REPO_ROOT / "ideas"
    market_dir = REPO_ROOT / "market-research"
    if not ideas_dir.exists():
        return

    for card_path in ideas_dir.rglob("*.md"):
        # Skip killed/ tree (we're checking active cards here) + READMEs
        if card_path.name == "README.md":
            continue
        if "killed" in card_path.relative_to(ideas_dir).parts:
            continue
        fm = parse_frontmatter(card_path)
        slug = fm.get("slug", card_path.stem)
        status = fm.get("status", "")
        rel = str(card_path.relative_to(REPO_ROOT))

        if status == "in-validation" and market_dir.exists():
            # Look in nested run folders: market-research/<run-id>/validation-<slug>.md
            validation_files = list(market_dir.rglob(f"validation-{slug}.md"))
            if not validation_files:
                issues.append(Issue(
                    severity="warning", file=rel, line=1,
                    rule="status.in-validation-no-report",
                    message=f"Card status is `in-validation` but no `market-research/*/validation-{slug}.md` exists",
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
                    suggestion="Record design-path: claude-led|hired per the /scope-mvp pre-build decisions checkpoint.",
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
    """Slugs are category-scoped, not globally unique.

    Categories per CLAUDE.md § Slug uniqueness — workspace rule:
      - active        ideas/<run-id>/<slug>.md   (not under killed/)
      - killed        ideas/killed/<run-id>/<slug>.md
      - app           web-apps/<slug>/ OR mobile-apps/<slug>/ OR desktop-apps/<slug>/

    Expected post-/scope-mvp state: one active card + one app folder coexist.
    That is NOT a collision — the card is the canonical idea record, the
    app folder is the build artifact.

    Errors (`slug.collision`):
      - 2+ active cards with same slug (across run folders)
      - 2+ killed cards with same slug
      - Active card AND killed card with the same slug at the same time
      - 2+ app folders with same slug across different stack categories

    Warnings:
      - `slug.orphaned-app-after-kill` — killed card + app folder, no active
      - `slug.app-without-card`        — app folder with no card at all
    """
    by_slug: dict[str, dict[str, list[str]]] = {}

    def record(slug: str, category: str, path: str) -> None:
        by_slug.setdefault(slug, {}).setdefault(category, []).append(path)

    ideas_dir = REPO_ROOT / "ideas"
    if ideas_dir.exists():
        for md in ideas_dir.rglob("*.md"):
            if md.name == "README.md":
                continue
            rel_parts = md.relative_to(ideas_dir).parts
            cat = "killed" if "killed" in rel_parts else "active"
            record(md.stem, cat, str(md.relative_to(REPO_ROOT)))

    for top in ("web-apps", "mobile-apps", "desktop-apps"):
        d = REPO_ROOT / top
        if not d.exists():
            continue
        for sub in d.iterdir():
            if sub.is_dir() and sub.name != ".gitkeep":
                record(sub.name, "app", str(sub.relative_to(REPO_ROOT)))

    for slug, cats in by_slug.items():
        active = cats.get("active", [])
        killed = cats.get("killed", [])
        apps = cats.get("app", [])

        if len(active) > 1:
            issues.append(Issue(
                severity="error", file=active[0], line=0, rule="slug.collision",
                message=f"Slug `{slug}` appears as an active card in {len(active)} run-folders: {', '.join(active)}",
                suggestion="A slug can only have ONE active card. Pick a different slug for the duplicate, or kill one.",
            ))
        if len(killed) > 1:
            issues.append(Issue(
                severity="error", file=killed[0], line=0, rule="slug.collision",
                message=f"Slug `{slug}` appears as a killed card in {len(killed)} run-folders: {', '.join(killed)}",
                suggestion="A slug can't be killed twice. Investigate the duplicate and remove the redundant entry.",
            ))
        if active and killed:
            issues.append(Issue(
                severity="error", file=active[0], line=0, rule="slug.collision",
                message=(
                    f"Slug `{slug}` is both active ({active[0]}) and killed ({killed[0]}) — "
                    "a card can't be both at the same time"
                ),
                suggestion="Either restore the killed card (delete the killed entry) or kill the active card (move it to killed).",
            ))
        if len(apps) > 1:
            issues.append(Issue(
                severity="error", file=apps[0], line=0, rule="slug.collision",
                message=(
                    f"Slug `{slug}` is used by multiple app folders across stack categories: "
                    f"{', '.join(apps)} — a product is ONE stack at MVP time"
                ),
                suggestion="Pick a single stack for this slug. Move or rename the duplicate(s).",
            ))

        if killed and apps and not active:
            issues.append(Issue(
                severity="warning", file=apps[0], line=0, rule="slug.orphaned-app-after-kill",
                message=(
                    f"Slug `{slug}` has an app folder ({apps[0]}) but the card is killed ({killed[0]}) "
                    "— orphaned MVP after kill"
                ),
                suggestion="If the kill is correct, delete the app folder. If the app folder is correct, restore the card.",
            ))
        if apps and not active and not killed:
            issues.append(Issue(
                severity="warning", file=apps[0], line=0, rule="slug.app-without-card",
                message=f"Slug `{slug}` has an app folder ({apps[0]}) but no parent idea card — orphaned",
                suggestion="An app folder normally comes from /scope-mvp on a green-lit card. Investigate the missing card.",
            ))


def check_required_sections_validation(issues: list[Issue]) -> None:
    """Validation reports must have the locked sections from the methodology guide.

    Two report shapes are valid (per `guides/product/idea-validation-methodology.md`):

    A. **Per-reviewer verdict report (§5)** — a single reviewer's verdict, used
       as the standalone output of an individual reviewer agent. Required:
       Verdict, Confidence, Findings, What I could not verify, Sources.
       Sections appear either as H2/H3/H4 headings (`## Verdict`) or as bold
       labels (`**Verdict:**`).

    B. **Integrated report (§7)** — produced by `/validate-card` when it
       combines multiple reviewer verdicts into one report. Required:
       Card snapshot, Reviewer verdicts, Integration summary, Decision,
       Open questions for MVP scoping. In this shape, the per-reviewer
       verdict info is embedded in per-reviewer subheadings inside the
       `## Reviewer verdicts` block (e.g., `### Viability — APPROVE (Confidence: HIGH)`),
       so we do NOT additionally require top-level Verdict / Confidence /
       Sources headings.

    Detection: a report is "integrated" if it has BOTH a `## Reviewer verdicts`
    AND a `## Integration summary` heading; otherwise it's per-reviewer.
    """
    market_dir = REPO_ROOT / "market-research"
    if not market_dir.exists():
        return

    per_reviewer_sections = [
        "Verdict", "Confidence", "Findings",
        "What I could not verify", "Sources",
    ]
    integrated_sections = [
        "Card snapshot", "Reviewer verdicts", "Integration summary",
        "Decision", "Open questions for MVP scoping",
    ]

    integrated_marker_a = re.compile(r"^#{2,4}\s+Reviewer verdicts\b", re.MULTILINE)
    integrated_marker_b = re.compile(r"^#{2,4}\s+Integration summary\b", re.MULTILINE)

    for report_path in market_dir.rglob("validation-*.md"):
        try:
            text = report_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        is_integrated = bool(integrated_marker_a.search(text)) and bool(integrated_marker_b.search(text))
        if is_integrated:
            required, shape = integrated_sections, "integrated (§7)"
        else:
            required, shape = per_reviewer_sections, "per-reviewer verdict (§5)"

        for section in required:
            heading_re = rf"^#{{2,4}}\s+{re.escape(section)}\b"
            bold_label_re = rf"\*\*{re.escape(section)}\*\*\s*:|\*\*{re.escape(section)}:\*\*"
            has_heading = re.search(heading_re, text, re.MULTILINE)
            has_bold = re.search(bold_label_re, text)
            if not (has_heading or has_bold):
                issues.append(Issue(
                    severity="warning",
                    file=str(report_path.relative_to(REPO_ROOT)),
                    line=0,
                    rule="report.missing-section",
                    message=f"Validation report missing required section: {section} (detected shape: {shape})",
                    suggestion=f"Add the section per guides/product/idea-validation-methodology.md (shape: {shape}).",
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
