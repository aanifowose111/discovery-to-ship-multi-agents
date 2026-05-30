#!/usr/bin/env python3
"""
new_idea_card.py — interactive helper to capture a new product idea card
outside the /discover flow.

Prompts for each section, validates the slug, checks for duplicates against
ideas/ and ideas/killed/, and writes the card to ideas/<slug>.md ready for
/validate-card.

For one-off idea capture when you have a specific product in mind and don't
want to run a full discovery cycle. The /discover slash command remains the
canonical path for brainstorming multiple cards from territories.

Run from the repo root: python scripts/new_idea_card.py
"""

import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IDEAS_DIR = REPO_ROOT / "ideas"
KILLED_DIR = IDEAS_DIR / "killed"

VALID_SOURCES = [
    "personal-pain", "adjacent", "competitor-weakness",
    "capability-shift", "underserved", "multi-step",
]


class C:
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def colored(text: str, color: str) -> str:
    return f"{color}{text}{C.RESET}" if sys.stdout.isatty() else text


def prompt(question: str, default: str = "", multiline: bool = False) -> str:
    if multiline:
        print(colored(f"\n{question}", C.BOLD))
        print(colored("  (Multi-line input. Type a single '.' on its own line to finish.)", C.DIM))
        lines: list[str] = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == ".":
                break
            lines.append(line)
        return "\n".join(lines).strip()
    prompt_text = f"\n{colored(question, C.BOLD)}"
    if default:
        prompt_text += colored(f" [{default}]", C.DIM)
    prompt_text += ": "
    return input(prompt_text).strip() or default


def validate_slug(slug: str) -> tuple[bool, str]:
    if not slug:
        return False, "Slug cannot be empty."
    if not re.match(r"^[a-z][a-z0-9-]*$", slug):
        return False, "Slug must be lowercase kebab-case (letters, digits, hyphens; start with a letter)."
    if (IDEAS_DIR / f"{slug}.md").exists():
        return False, f"ideas/{slug}.md already exists. Pick a different slug or delete the existing card."
    if (KILLED_DIR / f"{slug}.md").exists():
        return False, f"ideas/killed/{slug}.md already exists. The slug was previously killed; pick a different one."
    return True, ""


def main() -> int:
    print(colored("\n=== New idea card ===", C.CYAN))
    print(colored("Walks you through capturing a new product idea outside /discover.", C.DIM))
    print(colored("Press Ctrl-C at any point to abort.", C.DIM))

    IDEAS_DIR.mkdir(parents=True, exist_ok=True)

    # Slug
    while True:
        slug = prompt("Slug (lowercase kebab-case, e.g. 'dev-task-tracker')")
        ok, err = validate_slug(slug)
        if ok:
            break
        print(colored(f"  ✗ {err}", C.RED))

    # Source
    print(colored(f"\nSource category — pick one of: {', '.join(VALID_SOURCES)}", C.BOLD))
    while True:
        source = prompt("Source").strip()
        if source in VALID_SOURCES:
            break
        print(colored(f"  ✗ Must be one of: {', '.join(VALID_SOURCES)}", C.RED))

    # Body
    one_liner = prompt("One-line product description (becomes the H1)")
    problem = prompt("Problem (who has it, when, severity, evidence)", multiline=True)
    alternatives = prompt("Current alternatives (what people do today)", multiline=True)
    solution = prompt("Proposed solution (1-3 sentences)", multiline=True)
    why_now = prompt("Why now (what shifted recently)", multiline=True)
    distribution = prompt("Distribution hypothesis (how the first 100 users find it)", multiline=True)
    founder_fit = prompt("Founder fit (why you specifically can build this)", multiline=True)
    stack_fit = prompt("Tech-stack fit (workspace defaults: Flask + RN; stretches?)", multiline=True)
    risks = prompt("Top 2-3 risks / unknowns", multiline=True)
    effort = prompt("Rough effort estimate (weeks at ~12 hrs/week)")

    today = date.today().isoformat()
    card_text = f"""---
slug: {slug}
date-captured: {today}
source: {source}
status: draft
---

# {one_liner}

## Problem
{problem}

## Current alternatives
{alternatives}

## Proposed solution
{solution}

## Why now
{why_now}

## Distribution hypothesis
{distribution}

## Founder fit
{founder_fit}

## Tech-stack fit
{stack_fit}

## Top risks / unknowns
{risks}

## Rough effort estimate
{effort}
"""

    card_path = IDEAS_DIR / f"{slug}.md"
    card_path.write_text(card_text, encoding="utf-8")

    print(colored(f"\n✓ Idea card written to {card_path.relative_to(REPO_ROOT)}", C.GREEN))
    print(colored("\nNext steps:", C.BOLD))
    print(f"  - Review the card and tighten any sections.")
    print(f"  - Lint with: {colored('python scripts/lint_pipeline.py', C.CYAN)}")
    print(f"  - When ready, in Claude Code: {colored('/validate-card ' + slug, C.CYAN)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(colored("\n\nAborted.", C.YELLOW))
        sys.exit(130)
