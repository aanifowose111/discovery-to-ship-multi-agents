#!/usr/bin/env python3
"""
report_summarizer.py — pretty-print summaries of validation, scoping, scan,
and trend reports in market-research/.

Useful for "where am I" overviews when you have many reports. Extracts key
fields from each report (verdict, decision, status, dates, headline counts)
and prints a tabular summary grouped by report type.

Run from the repo root:
  python scripts/report_summarizer.py
  python scripts/report_summarizer.py --type validation
  python scripts/report_summarizer.py --type scoping --slug findvil
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKET_DIR = REPO_ROOT / "market-research"


class C:
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colored(text: str, color: str, enabled: bool = True) -> str:
    return f"{color}{text}{C.RESET}" if enabled else text


@dataclass
class ReportSummary:
    path: Path
    kind: str  # "validation" | "scoping" | "scan" | "trend"
    slug: str
    date: str
    status: str
    headline: str


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    out: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def first_section_match(text: str, section: str, pattern: str) -> str:
    """Find a value in the first paragraph after a section heading."""
    block = re.search(
        rf"##\s+{re.escape(section)}\s*\n+(.*?)(?=\n##\s|\Z)",
        text, re.DOTALL,
    )
    if not block:
        return ""
    m = re.search(pattern, block.group(1))
    return m.group(1).strip() if m else ""


def summarize_validation(path: Path) -> ReportSummary | None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    # New convention: validation-<slug>.md inside market-research/<run-id>/
    slug = fm.get("slug", path.stem.replace("validation-", ""))
    date = fm.get("date-validation", "")
    status = fm.get("status", "draft")
    verdict = first_section_match(text, "Verdict", r"\*?\*?(APPROVE-WITH-NOTES|APPROVE|REJECT)\*?\*?") or "(none)"
    decision = first_section_match(text, "Decision", r"\*?\*?(KILLED|GREEN-LIT|REVISE|OVERRIDE|[A-Za-z][\w-]+)\*?\*?") or "(none)"
    headline = f"verdict: {verdict} | decision: {decision}"
    return ReportSummary(path, "validation", slug, date, status, headline)


def summarize_scoping(path: Path) -> ReportSummary | None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    slug = fm.get("slug", "")
    date = fm.get("date-scoping", "")
    status = fm.get("status", "")
    verdict = first_section_match(text, "Combined verdict", r"\*?\*?([A-Z][A-Z -]+)\*?\*?")
    if not verdict:
        verdict = first_section_match(text, "Verdict", r"\*?\*?([A-Z][A-Z -]+)\*?\*?") or "(none)"
    decision = first_section_match(text, "Decision", r"\*?\*?([A-Za-z][\w-]+)\*?\*?") or "(none)"
    headline = f"verdict: {verdict} | decision: {decision}"
    return ReportSummary(path, "scoping", slug, date, status, headline)


def summarize_scan(path: Path) -> ReportSummary | None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    date = fm.get("date-scanned", "")
    aperture = fm.get("aperture", "")
    status = fm.get("status", "")
    territory_section = re.search(
        r"##\s+Candidate territories(.*?)(?=\n##\s|\Z)", text, re.DOTALL,
    )
    territories_count = 0
    if territory_section:
        territories_count = len(re.findall(
            r"^###\s+Territory\s*\d*", territory_section.group(1), re.MULTILINE,
        ))
    headline = f"aperture: {aperture} | {territories_count} territories"
    return ReportSummary(path, "scan", "(workspace)", date, status, headline)


def summarize_trend(path: Path) -> ReportSummary | None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    date = fm.get("date-swept", "")
    sweep_type = fm.get("sweep-type", "scheduled")
    status = fm.get("status", "")
    material_section = re.search(
        r"##\s+Material findings(.*?)(?=\n##\s|\Z)", text, re.DOTALL,
    )
    material_count = 0
    if material_section:
        material_count = len(re.findall(
            r"^###\s+Finding\s*\d*", material_section.group(1), re.MULTILINE,
        ))
    headline = f"{sweep_type} | {material_count} material findings"
    return ReportSummary(path, "trend", "(workspace)", date, status, headline)


def collect_summaries(filter_type: str = "", filter_slug: str = "") -> list[ReportSummary]:
    """Walk nested run-folders: market-research/<run-id>/<artifact>.md."""
    out: list[ReportSummary] = []
    if not MARKET_DIR.exists():
        return out
    # Maps filename to (kind, summarizer). Filenames are now generic inside run folders:
    #   scan.md, trends.md, triage.md, validation-<slug>.md, scoping-<slug>.md
    def kind_of(filename: str) -> tuple[str, callable] | None:
        if filename == "scan.md":
            return ("scan", summarize_scan)
        if filename == "trends.md":
            return ("trend", summarize_trend)
        if filename.startswith("validation-") and filename.endswith(".md"):
            return ("validation", summarize_validation)
        if filename.startswith("scoping-") and filename.endswith(".md"):
            return ("scoping", summarize_scoping)
        return None  # triage.md and README.md are skipped here

    for path in sorted(MARKET_DIR.rglob("*.md")):
        if path.name == "README.md":
            continue
        match = kind_of(path.name)
        if not match:
            continue
        kind, fn = match
        if filter_type and filter_type != kind:
            continue
        try:
            summary = fn(path)
        except Exception as e:
            print(f"Failed to summarize {path}: {e}", file=sys.stderr)
            continue
        if summary and (not filter_slug or summary.slug == filter_slug):
            out.append(summary)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Pretty-print report summaries from market-research/.")
    parser.add_argument("--type", choices=["validation", "scoping", "scan", "trend"],
                        help="Filter by report type")
    parser.add_argument("--slug", help="Filter by product slug")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    use_color = not args.no_color and sys.stdout.isatty()
    summaries = collect_summaries(args.type or "", args.slug or "")

    if not summaries:
        print(colored("No reports match the filters.", C.DIM, use_color))
        return 0

    by_kind: dict[str, list[ReportSummary]] = {}
    for s in summaries:
        by_kind.setdefault(s.kind, []).append(s)

    for kind in ["scan", "validation", "scoping", "trend"]:
        if kind not in by_kind:
            continue
        print(colored(f"\n=== {kind.upper()} REPORTS ({len(by_kind[kind])}) ===", C.BOLD, use_color))
        for s in by_kind[kind]:
            slug_str = colored(f"{s.slug:<30}", C.CYAN, use_color)
            date_str = colored(s.date, C.DIM, use_color)
            if s.status in ("active", "acted-on", "green-lit"):
                status_color = C.GREEN
            elif s.status == "draft":
                status_color = C.YELLOW
            else:
                status_color = C.DIM
            status_str = colored(f"[{s.status}]", status_color, use_color)
            print(f"  {slug_str} {date_str}  {status_str}")
            print(f"    {s.headline}")
            print(f"    {colored(str(s.path.relative_to(REPO_ROOT)), C.DIM, use_color)}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
