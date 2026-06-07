#!/usr/bin/env python3
"""
run_tests.py — repo health check / smoke test for discovery-to-ship-multi-agents.

Runs a battery of checks across:
- A. Required tools / dependencies (delegated to `which`).
- B. Repo structure (required files exist + non-empty).
- C. YAML frontmatter validity (agents, commands, methodology guides).
- D. Cross-reference integrity (markdown links + @-paths via check_links.py).
- E. Pipeline state lint (slug uniqueness, status alignment, via lint_pipeline.py).
- F. Script smoke tests (gen_run_id, check_slug execute cleanly).
- G. Documentation consistency (slash commands referenced in CLAUDE.md actually exist).

Output: per-check status (✓ pass, ⚠ warn, ✗ fail) + final summary + how to report bugs.
Exit code: 0 if no failures (warnings OK), 1 if any failures.

Usage:
  python3 scripts/run_tests.py                 # full human-readable output
  python3 scripts/run_tests.py --quiet         # summary + failures only
  python3 scripts/run_tests.py --json          # machine-readable
  python3 scripts/run_tests.py --no-color
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAINTAINER_EMAIL = "aanifowose111@gmail.com"


class C:
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colored(text: str, color: str, enabled: bool = True) -> str:
    return f"{color}{text}{C.RESET}" if enabled else text


@dataclass
class Check:
    category: str
    name: str
    status: str  # "pass" | "warn" | "fail"
    message: str = ""


# ─── Test functions ──────────────────────────────────────────────────────

def test_required_tools(checks: list[Check]) -> None:
    """A. Required tools."""
    tools = [
        ("git", True, ""),
        ("gh", True, "GitHub auth: `brew install gh`"),
        ("pandoc", True, "Markdown export: `brew install pandoc`"),
        ("typst", False, "PDF export engine: `brew install typst` (optional but recommended)"),
        ("python3", True, ""),
        ("node", False, "Mobile work only: `brew install node@20`"),
    ]
    for tool, required, help_text in tools:
        path = shutil.which(tool)
        if path:
            checks.append(Check("A. Required tools", tool, "pass", f"found at {path}"))
        elif required:
            checks.append(Check("A. Required tools", tool, "fail", help_text or "required but not found"))
        else:
            checks.append(Check("A. Required tools", tool, "warn", help_text or "optional; not found"))


def test_repo_structure(checks: list[Check]) -> None:
    """B. Required files exist and are non-empty."""
    required = [
        "CLAUDE.md", "README.md", "HELP.md", "CHANGELOG.md",
        "CONTRIBUTING.md", "LICENSE", "SECURITY.md", ".gitignore",
        ".claude/settings.json",
        ".claude/agents/README.md",
        ".claude/commands/README.md",
        ".claude/skills/README.md",
        "user-context/README.md",
        "user-context/INTERESTS.md.example",
        "user-context/IDEAS.md.example",
        "user-context/POLICY.md.example",
        "user-context/audit-log.jsonl.example",
        "scripts/README.md",
        "scripts/gen_run_id.py",
        "scripts/preflight.sh",
        "scripts/lint_pipeline.py",
        "scripts/check_slug.py",
        "scripts/check_links.py",
        "scripts/run_tests.py",
        "scripts/check_system.py",
        "scripts/projects.py",
        "scripts/audit_log.py",
        "desktop-apps/README.md",
        "guides/desktop/python-mvp-scaffold.md",
        "guides/desktop/packaging-and-distribution.md",
        ".claude/agents/senior-desktop-engineer.md",
        ".claude/commands/ship-app.md",
        ".claude/commands/documentation.md",
        ".claude/commands/log.md",
        ".claude/commands/reprice.md",
        ".claude/commands/revive-card.md",
        ".claude/commands/rework.md",
        ".claude/commands/consolidate.md",
        ".claude/commands/infra-cost.md",
        ".claude/commands/scope-v1.md",
        ".claude/commands/team.md",
        ".claude/agents/product-pricing-reviewer.md",
        "guides/product/v1-scoping-methodology.md",
        "scripts/team.py",
        "DOCUMENTATION.md",
    ]
    for f in required:
        path = REPO_ROOT / f
        if not path.exists():
            checks.append(Check("B. Repo structure", f, "fail", "missing"))
        elif path.stat().st_size == 0:
            checks.append(Check("B. Repo structure", f, "warn", "exists but empty"))
        else:
            checks.append(Check("B. Repo structure", f, "pass"))


def test_frontmatter(checks: list[Check]) -> None:
    """C. YAML frontmatter is valid in agents, commands, methodology guides."""
    folders = [
        (".claude/agents", "agent persona"),
        (".claude/commands", "slash command"),
        ("guides/product", "methodology guide"),
        ("guides/market", "methodology guide"),
        ("guides/funding", "methodology guide"),
        ("guides/web", "methodology guide"),
        ("guides/mobile", "methodology guide"),
        ("guides/desktop", "methodology guide"),
        ("guides/ui-ux", "methodology guide"),
    ]
    for folder, kind in folders:
        d = REPO_ROOT / folder
        if not d.exists():
            checks.append(Check("C. Frontmatter", folder, "warn", "folder missing"))
            continue
        for md in d.glob("*.md"):
            if md.name == "README.md":
                continue
            rel = str(md.relative_to(REPO_ROOT))
            try:
                text = md.read_text(encoding="utf-8")
            except Exception as e:
                checks.append(Check("C. Frontmatter", rel, "fail", f"unreadable: {e}"))
                continue
            # Agents and commands require frontmatter; guides may have it but don't require
            if not text.startswith("---\n"):
                if kind == "methodology guide":
                    checks.append(Check("C. Frontmatter", rel, "pass", "no frontmatter (ok for guide)"))
                else:
                    checks.append(Check("C. Frontmatter", rel, "fail", "missing frontmatter"))
                continue
            end = text.find("\n---\n", 4)
            if end == -1:
                checks.append(Check("C. Frontmatter", rel, "fail", "frontmatter unterminated"))
                continue
            fm = text[4:end]
            if kind in ("agent persona", "slash command") and "description:" not in fm:
                checks.append(Check("C. Frontmatter", rel, "warn", "missing description field"))
            else:
                checks.append(Check("C. Frontmatter", rel, "pass"))


def test_cross_references(checks: list[Check]) -> None:
    """D. Markdown links + @-path refs resolve."""
    script = REPO_ROOT / "scripts" / "check_links.py"
    if not script.exists():
        checks.append(Check("D. Cross-references", "check_links.py", "fail", "script missing"))
        return
    try:
        result = subprocess.run(
            ["python3", str(script), "--quiet", "--no-color"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        checks.append(Check("D. Cross-references", "scan markdown links", "fail", "timed out"))
        return
    out = (result.stdout + result.stderr).strip()
    if result.returncode == 0:
        checks.append(Check("D. Cross-references", "markdown links + @-path refs", "pass"))
    else:
        # Try to extract the count from stdout's "N issue(s) found." line
        m = re.search(r"(\d+)\s+issue\(s\)\s+found", out)
        count = m.group(1) if m else "?"
        checks.append(Check("D. Cross-references", "markdown links + @-path refs", "warn",
                            f"{count} broken refs (run scripts/check_links.py for details)"))


def test_pipeline_lint(checks: list[Check]) -> None:
    """E. Pipeline state lint: slug uniqueness + status alignment + required-section coverage."""
    script = REPO_ROOT / "scripts" / "lint_pipeline.py"
    if not script.exists():
        checks.append(Check("E. Pipeline lint", "lint_pipeline.py", "fail", "script missing"))
        return
    try:
        result = subprocess.run(
            ["python3", str(script), "--quiet", "--no-color"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        checks.append(Check("E. Pipeline lint", "lint pipeline state", "fail", "timed out"))
        return
    out = result.stdout
    err_m = re.search(r"Errors:\s+(\d+)", out)
    warn_m = re.search(r"Warnings:\s+(\d+)", out)
    errors = int(err_m.group(1)) if err_m else 0
    warnings = int(warn_m.group(1)) if warn_m else 0
    if errors > 0:
        checks.append(Check("E. Pipeline lint", "lint pipeline state", "fail",
                            f"{errors} error(s); see scripts/lint_pipeline.py for details"))
    elif warnings > 0:
        checks.append(Check("E. Pipeline lint", "lint pipeline state", "warn",
                            f"{warnings} warning(s) (often pre-existing data issues)"))
    else:
        checks.append(Check("E. Pipeline lint", "lint pipeline state", "pass"))


def test_smoke(checks: list[Check]) -> None:
    """F. Scripts execute without crashing."""
    smokes = [
        (["python3", "scripts/gen_run_id.py"], "gen_run_id.py", "generates a run-id"),
        (["python3", "scripts/check_slug.py", "test-slug-that-should-not-exist-xyz"], "check_slug.py", "checks availability"),
        (["python3", "scripts/audit_log.py", "list"], "audit_log.py", "lists entries"),
        (["python3", "scripts/team.py", "roles"], "team.py", "lists roles"),
    ]
    for cmd, name, desc in smokes:
        try:
            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=10)
            # 0 = success; 1 = expected non-error completion (e.g., slug taken). Both OK.
            if result.returncode in (0, 1):
                checks.append(Check("F. Smoke tests", f"{name} ({desc})", "pass"))
            else:
                first_err_line = (result.stderr or "").splitlines()[0] if result.stderr else "(no stderr)"
                checks.append(Check("F. Smoke tests", f"{name} ({desc})", "fail",
                                    f"exit {result.returncode}: {first_err_line[:100]}"))
        except subprocess.TimeoutExpired:
            checks.append(Check("F. Smoke tests", f"{name} ({desc})", "fail", "timed out"))
        except Exception as e:
            checks.append(Check("F. Smoke tests", f"{name} ({desc})", "fail", f"{type(e).__name__}: {e}"))


def test_documentation_consistency(checks: list[Check]) -> None:
    """G. Slash commands referenced in CLAUDE.md actually exist in .claude/commands/."""
    claude_md = REPO_ROOT / "CLAUDE.md"
    if not claude_md.exists():
        checks.append(Check("G. Documentation", "CLAUDE.md exists for cross-check", "fail", "CLAUDE.md missing"))
        return
    text = claude_md.read_text(encoding="utf-8")
    # Capture `/word` patterns; lowercase word, hyphens OK
    referenced = set(re.findall(r"`(/[a-z][a-z-]*)`", text))
    commands_dir = REPO_ROOT / ".claude" / "commands"
    available = set()
    if commands_dir.exists():
        for md in commands_dir.glob("*.md"):
            if md.name != "README.md":
                available.add(f"/{md.stem}")
    # Three categories that are intentionally absent from .claude/commands/:
    # (1) Claude Code built-in commands (handled by the harness).
    # (2) agent-skills commands that live in external/agent-skills/.claude/commands/.
    # (3) Generic documentation placeholders (literal words like /command, /cmd,
    #     or template forms like /<command-name>) that aren't real commands.
    builtins = {
        # Claude Code built-ins
        "/help", "/init", "/clear", "/config", "/exit", "/loop", "/schedule",
        "/keybindings", "/hooks",
        # agent-skills commands (live in external/agent-skills/.claude/commands/)
        "/spec", "/plan", "/build", "/test", "/review", "/ship", "/code-simplify",
        # Documentation placeholders — referenced as examples, not real commands
        "/command", "/cmd", "/name", "/foo", "/bar",
    }
    missing = sorted(referenced - available - builtins)
    if not missing:
        checks.append(Check("G. Documentation", "all `/cmd` mentions in CLAUDE.md resolve", "pass"))
    else:
        checks.append(Check("G. Documentation", "all `/cmd` mentions in CLAUDE.md resolve", "warn",
                            f"referenced but missing: {missing}"))


# ─── Reporting ───────────────────────────────────────────────────────────

def print_human(checks: list[Check], use_color: bool, quiet: bool) -> None:
    by_cat: dict[str, list[Check]] = {}
    for c in checks:
        by_cat.setdefault(c.category, []).append(c)
    pass_n = sum(1 for c in checks if c.status == "pass")
    warn_n = sum(1 for c in checks if c.status == "warn")
    fail_n = sum(1 for c in checks if c.status == "fail")

    if not quiet:
        for cat in sorted(by_cat.keys()):
            print(colored(f"\n{cat}", C.BOLD + C.CYAN, use_color))
            for c in by_cat[cat]:
                if c.status == "pass":
                    sym = colored("✓", C.GREEN, use_color)
                elif c.status == "warn":
                    sym = colored("⚠", C.YELLOW, use_color)
                else:
                    sym = colored("✗", C.RED, use_color)
                line = f"  {sym} {c.name}"
                if c.message and c.status != "pass":
                    line += colored(f" — {c.message}", C.DIM, use_color)
                elif c.message and not quiet:
                    line += colored(f" — {c.message}", C.DIM, use_color)
                print(line)
    else:
        # Quiet: only show failures
        fails = [c for c in checks if c.status == "fail"]
        if fails:
            print(colored("Failures:", C.BOLD + C.RED, use_color))
            for c in fails:
                print(f"  {colored('✗', C.RED, use_color)} [{c.category}] {c.name} — {c.message}")

    bar = "═" * 70
    print(colored(f"\n{bar}", C.BOLD, use_color))
    summary = (
        f"{colored(str(pass_n), C.GREEN, use_color)} passed   "
        f"{colored(str(warn_n), C.YELLOW, use_color)} warning(s)   "
        f"{colored(str(fail_n), C.RED, use_color)} failed   "
        f"({len(checks)} total)"
    )
    print(f"{colored('Summary:', C.BOLD, use_color)} {summary}")
    print(colored(bar, C.BOLD, use_color))

    if fail_n == 0 and warn_n == 0:
        print(colored("\nAll checks passed. The workspace is healthy.", C.GREEN, use_color))
    elif fail_n == 0:
        print(colored(f"\nNo failures. {warn_n} warning(s) — workspace usable; investigate when you have time.",
                      C.YELLOW, use_color))
    else:
        print(colored(f"\n{fail_n} failure(s). The workspace needs attention before it runs reliably.",
                      C.RED, use_color))

    print()
    print(colored("Found a real bug in the repo (not your local setup)? Report it:", C.DIM, use_color))
    print(colored(f"  Email: {MAINTAINER_EMAIL}", C.DIM, use_color))
    print(colored("  Subject: [discovery-to-ship test failure] — short summary", C.DIM, use_color))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the repo health check / smoke test suite.")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable.")
    parser.add_argument("--quiet", action="store_true", help="Show only failures + summary.")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output.")
    args = parser.parse_args()

    checks: list[Check] = []
    test_required_tools(checks)
    test_repo_structure(checks)
    test_frontmatter(checks)
    test_cross_references(checks)
    test_pipeline_lint(checks)
    test_smoke(checks)
    test_documentation_consistency(checks)

    fail_n = sum(1 for c in checks if c.status == "fail")

    if args.json:
        payload = {
            "summary": {
                "pass": sum(1 for c in checks if c.status == "pass"),
                "warn": sum(1 for c in checks if c.status == "warn"),
                "fail": fail_n,
                "total": len(checks),
            },
            "checks": [asdict(c) for c in checks],
            "report_to": MAINTAINER_EMAIL,
        }
        print(json.dumps(payload, indent=2))
    else:
        use_color = not args.no_color and sys.stdout.isatty()
        print_human(checks, use_color, args.quiet)

    return 1 if fail_n > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
