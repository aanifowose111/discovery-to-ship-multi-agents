#!/usr/bin/env python3
"""
check_links.py — scan tracked markdown files for relative links and @path
references, verify the target files exist. Optionally check external URLs.

Catches broken links when files are renamed, removed, or moved. Particularly
useful before opening a PR, after refactoring, or to audit cross-references
between methodology guides.

Run from the repo root:
  python scripts/check_links.py
  python scripts/check_links.py --check-urls   # also HEAD-request external URLs (slow)
  python scripts/check_links.py --json         # output JSON
  python scripts/check_links.py --quiet        # show only summary count
"""

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent

IGNORED_DIRS = {
    "ideas", "market-research", "web-apps", "mobile-apps", "generated",
    "external", ".git", "node_modules", "__pycache__", ".venv", "venv",
}

MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(([^)#\s]+)(#[^)]*)?\)")
AT_REFERENCE = re.compile(r"(?<!\S)@([a-zA-Z0-9_\-./]+\.(?:md|typ|py|sh|json|yaml|yml|toml))")


class C:
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colored(text: str, color: str, enabled: bool = True) -> str:
    return f"{color}{text}{C.RESET}" if enabled else text


@dataclass
class Issue:
    file: str
    line: int
    link_text: str
    target: str
    reason: str
    kind: str  # "relative" | "at-ref" | "external"


def is_external_url(url: str) -> bool:
    return url.startswith(("http://", "https://", "mailto:"))


def walk_markdown_files() -> list[Path]:
    found: list[Path] = []
    for md_path in REPO_ROOT.rglob("*.md"):
        if any(part in IGNORED_DIRS for part in md_path.relative_to(REPO_ROOT).parts):
            continue
        found.append(md_path)
    return found


def extract_relative_links(text: str) -> list[tuple[int, str, str]]:
    out: list[tuple[int, str, str]] = []
    in_code = False
    for line_num, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for match in MARKDOWN_LINK.finditer(line):
            link_text, target = match.group(1), match.group(2)
            if is_external_url(target):
                continue
            out.append((line_num, link_text, target))
    return out


def extract_at_references(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    in_code = False
    for line_num, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or "`" in line:
            continue
        for match in AT_REFERENCE.finditer(line):
            out.append((line_num, match.group(1)))
    return out


def extract_external_urls(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    in_code = False
    for line_num, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        for match in MARKDOWN_LINK.finditer(line):
            target = match.group(2)
            if is_external_url(target) and not target.startswith("mailto:"):
                out.append((line_num, target))
    return out


def check_relative_link(source_file: Path, target: str) -> Optional[str]:
    resolved = (source_file.parent / target).resolve()
    if not resolved.exists():
        return f"target does not exist: {target}"
    return None


def check_at_reference(target: str) -> Optional[str]:
    if not (REPO_ROOT / target).exists():
        return f"@{target} does not resolve"
    return None


def check_external_url(url: str, timeout: int = 5) -> Optional[str]:
    try:
        req = Request(
            url, method="HEAD",
            headers={"User-Agent": "discovery-to-ship-link-checker/1.0"},
        )
        with urlopen(req, timeout=timeout) as response:
            if response.status >= 400:
                return f"HTTP {response.status}"
    except HTTPError as e:
        return f"HTTP {e.code}"
    except URLError as e:
        return f"connection error: {e.reason}"
    except Exception as e:
        return f"check failed: {type(e).__name__}: {e}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check markdown links and @path references.")
    parser.add_argument("--check-urls", action="store_true",
                        help="Also HEAD-request external URLs (slow)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--quiet", action="store_true", help="Show only summary count")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    use_color = not args.no_color and sys.stdout.isatty()
    issues: list[Issue] = []
    files = walk_markdown_files()
    print(colored(f"Checking {len(files)} markdown files...", C.DIM, use_color), file=sys.stderr)

    for md_path in files:
        try:
            text = md_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(md_path.relative_to(REPO_ROOT))

        for line_num, link_text, target in extract_relative_links(text):
            err = check_relative_link(md_path, target)
            if err:
                issues.append(Issue(rel, line_num, link_text, target, err, "relative"))

        for line_num, target in extract_at_references(text):
            err = check_at_reference(target)
            if err:
                issues.append(Issue(rel, line_num, "", target, err, "at-ref"))

    if args.check_urls:
        url_jobs: list[tuple[str, int, str]] = []
        for md_path in files:
            try:
                text = md_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            rel = str(md_path.relative_to(REPO_ROOT))
            for line_num, url in extract_external_urls(text):
                url_jobs.append((rel, line_num, url))

        print(colored(f"Checking {len(url_jobs)} external URLs...", C.DIM, use_color), file=sys.stderr)
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_job = {
                executor.submit(check_external_url, url): (rel, line_num, url)
                for (rel, line_num, url) in url_jobs
            }
            for future in as_completed(future_to_job):
                rel, line_num, url = future_to_job[future]
                err = future.result()
                if err:
                    issues.append(Issue(rel, line_num, "", url, err, "external"))

    if args.json:
        by_kind: dict[str, int] = {}
        for issue in issues:
            by_kind[issue.kind] = by_kind.get(issue.kind, 0) + 1
        payload = {
            "summary": {"total": len(issues), "by_kind": by_kind},
            "issues": [asdict(i) for i in issues],
        }
        print(json.dumps(payload, indent=2))
    elif not args.quiet:
        for issue in issues:
            loc = f"{issue.file}:{issue.line}"
            print(f"  {colored(loc, C.CYAN, use_color)}  [{issue.kind}]")
            print(f"    {issue.target} → {colored(issue.reason, C.RED, use_color)}")

    color = C.YELLOW if issues else C.GREEN
    print(colored(f"\n{len(issues)} issue(s) found.", color, use_color))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
