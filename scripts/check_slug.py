#!/usr/bin/env python3
"""
check_slug.py — verify that a product slug is available for a NEW artifact.

Walks ideas/, ideas/killed/, web-apps/, mobile-apps/, desktop-apps/ and
returns the locations where the slug is already used. ANY current use
blocks reuse — see CLAUDE.md § Slug uniqueness for the full category
model and the post-/scope-mvp coexistence exception.

Note: this script is the "can I claim this name?" check. The richer
"is the workspace state consistent?" check (e.g., active+killed conflict,
multi-stack app conflict) lives in lint_pipeline.py:check_slug_uniqueness.

Used by:
  - new_idea_card.py (interactive card creator)
  - lint_pipeline.py (detects collisions across already-created artifacts)
  - directly by the user / by Claude before creating a new slug-keyed artifact

Run from the repo root:
  python scripts/check_slug.py <slug>           # check a specific slug
  python scripts/check_slug.py --list-all       # list every existing slug
  python scripts/check_slug.py --json <slug>    # machine-readable output

Exit codes:
  0 = slug is available
  1 = slug is taken (or invalid format)
  2 = usage error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass
class SlugLocation:
    kind: str   # "idea" | "killed-idea" | "web-app" | "mobile-app" | "desktop-app"
    path: str
    detail: str


def existing_slugs() -> dict[str, list[SlugLocation]]:
    """Return a map of slug → [locations where it appears]."""
    found: dict[str, list[SlugLocation]] = {}

    def add(slug: str, loc: SlugLocation) -> None:
        found.setdefault(slug, []).append(loc)

    # ideas/<run-id>/<slug>.md (active) and ideas/killed/<run-id>/<slug>.md (killed).
    # Walk nested run-folders.
    ideas_dir = REPO_ROOT / "ideas"
    if ideas_dir.exists():
        for md in ideas_dir.rglob("*.md"):
            if md.name == "README.md":
                continue
            rel_parts = md.relative_to(ideas_dir).parts
            if "killed" in rel_parts:
                add(md.stem, SlugLocation(
                    kind="killed-idea",
                    path=str(md.relative_to(REPO_ROOT)),
                    detail="killed idea card",
                ))
            else:
                add(md.stem, SlugLocation(
                    kind="idea",
                    path=str(md.relative_to(REPO_ROOT)),
                    detail="active idea card",
                ))

    # web-apps/<slug>/
    web_dir = REPO_ROOT / "web-apps"
    if web_dir.exists():
        for sub in web_dir.iterdir():
            if sub.is_dir() and sub.name not in {".gitkeep"}:
                add(sub.name, SlugLocation(
                    kind="web-app",
                    path=str(sub.relative_to(REPO_ROOT)),
                    detail="web app project folder",
                ))

    # mobile-apps/<slug>/
    mobile_dir = REPO_ROOT / "mobile-apps"
    if mobile_dir.exists():
        for sub in mobile_dir.iterdir():
            if sub.is_dir() and sub.name not in {".gitkeep"}:
                add(sub.name, SlugLocation(
                    kind="mobile-app",
                    path=str(sub.relative_to(REPO_ROOT)),
                    detail="mobile app project folder",
                ))

    # desktop-apps/<slug>/
    desktop_dir = REPO_ROOT / "desktop-apps"
    if desktop_dir.exists():
        for sub in desktop_dir.iterdir():
            if sub.is_dir() and sub.name not in {".gitkeep"}:
                add(sub.name, SlugLocation(
                    kind="desktop-app",
                    path=str(sub.relative_to(REPO_ROOT)),
                    detail="desktop app project folder",
                ))

    return found


def is_available(slug: str) -> tuple[bool, str, list[SlugLocation]]:
    """
    Returns (available, reason_if_not, conflicting_locations).
    """
    if not slug:
        return False, "slug is empty", []
    if not SLUG_PATTERN.match(slug):
        return False, "slug must be lowercase kebab-case (letters, digits, hyphens; start with a letter)", []

    all_slugs = existing_slugs()
    if slug in all_slugs:
        locations = all_slugs[slug]
        reason = (
            f"slug `{slug}` is already used in {len(locations)} location(s) — "
            "any current use blocks reuse (active card, killed card, or app folder in web/mobile/desktop)"
        )
        return False, reason, locations

    return True, "", []


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether a product slug is available.")
    parser.add_argument("slug", nargs="?", help="The slug to check")
    parser.add_argument("--list-all", action="store_true", help="List every slug currently in use across the workspace")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args()

    use_color = not args.no_color and sys.stdout.isatty()

    if args.list_all:
        all_slugs = existing_slugs()
        if args.json:
            payload = {
                slug: [{"kind": loc.kind, "path": loc.path, "detail": loc.detail} for loc in locs]
                for slug, locs in sorted(all_slugs.items())
            }
            print(json.dumps(payload, indent=2))
            return 0
        if not all_slugs:
            print(colored("No slugs in use yet.", C.DIM, use_color))
            return 0
        print(colored(f"\n{len(all_slugs)} slug(s) in use across the workspace:", C.BOLD, use_color))
        for slug in sorted(all_slugs.keys()):
            locs = all_slugs[slug]
            print(f"  {colored(slug, C.CYAN, use_color)}")
            for loc in locs:
                marker = colored(f"[{loc.kind}]", C.DIM, use_color)
                print(f"    {marker} {loc.path}  ({loc.detail})")
        return 0

    if not args.slug:
        print("Usage: python scripts/check_slug.py <slug> | --list-all", file=sys.stderr)
        return 2

    ok, reason, locations = is_available(args.slug)
    if args.json:
        print(json.dumps({
            "slug": args.slug,
            "available": ok,
            "reason": reason,
            "conflicts": [
                {"kind": loc.kind, "path": loc.path, "detail": loc.detail}
                for loc in locations
            ],
        }, indent=2))
        return 0 if ok else 1

    if ok:
        print(colored(f"\n✓ `{args.slug}` is available.", C.GREEN, use_color))
        return 0
    print(colored(f"\n✗ `{args.slug}` is NOT available.", C.RED, use_color))
    print(f"  {reason}")
    if locations:
        print(colored("\n  Conflicts:", C.YELLOW, use_color))
        for loc in locations:
            print(f"    [{loc.kind}] {loc.path}  ({loc.detail})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
