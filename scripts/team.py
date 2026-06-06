#!/usr/bin/env python3
"""
team.py — manage per-product senior-engineer team-member names.

Each product (web-apps/<slug>/, mobile-apps/<slug>/, desktop-apps/<slug>/)
can have an optional team.json that maps senior-persona role-keys to
human-chosen names. Names are used by the build orchestrator
(senior-software-engineer) in narration:

  Named:    "Paul (Senior Software Engineer) is invoking Maria (Senior
            Database Engineer) for the schema work."
  Unnamed:  "Senior Software Engineer is invoking Senior Database Engineer
            for the schema work."

The team is a fixed roster of 9 build-phase personas — these are the
long-running collaborators, not the one-shot reviewers. Members cannot
be deleted (they're critical to the workflow); they can only be named,
renamed, or reset to unnamed.

team.json shape:
  {
    "slug": "<slug>",
    "team": {
      "senior-software-engineer": "Paul",
      "senior-database-engineer": "Maria",
      "senior-frontend-engineer": "",
      ...
    },
    "last-updated": "2026-06-06"
  }

Empty-string name = unnamed; the default role label is used in narration.

Usage:
  team.py get <slug> <role>            print the name (exit 1 if unnamed)
  team.py set <slug> <role> <name>     set the name; validates format
  team.py list <slug>                  print a table of role | name
  team.py list <slug> --json           machine-readable
  team.py init <slug>                  create empty team.json if missing
  team.py reset <slug>                 clear all names (file stays)
  team.py roles                        print the fixed role list
  team.py path <slug>                  print the team.json path for this slug

Name validation rules:
  - 1 to 30 characters total
  - Must start with a letter or digit
  - Allowed characters: letters, digits, spaces, hyphens, apostrophes

Exit codes:
  0 = success
  1 = product folder not found, role not found, or unnamed (for `get`)
  2 = usage error / invalid name
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ROLES: list[tuple[str, str]] = [
    ("senior-software-engineer", "Senior Software Engineer"),
    ("senior-system-design-engineer", "Senior System Design Engineer"),
    ("senior-database-engineer", "Senior Database Engineer"),
    ("senior-backend-engineer", "Senior Backend Engineer"),
    ("senior-frontend-engineer", "Senior Frontend Engineer"),
    ("senior-desktop-engineer", "Senior Desktop Engineer"),
    ("senior-qa-engineer", "Senior QA Engineer"),
    ("senior-devops-engineer", "Senior DevOps Engineer"),
    ("senior-security-engineer", "Senior Security Engineer"),
]

ROLE_KEYS = {r for r, _ in ROLES}
ROLE_LABEL = dict(ROLES)

VALID_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 \-']{0,29}$")

PRODUCT_DIRS = ["web-apps", "mobile-apps", "desktop-apps"]


def find_product_folder(slug: str) -> Path | None:
    for d in PRODUCT_DIRS:
        folder = REPO_ROOT / d / slug
        if folder.is_dir():
            return folder
    return None


def team_path_for(slug: str) -> Path | None:
    folder = find_product_folder(slug)
    if folder is None:
        return None
    return folder / "team.json"


def empty_team_map() -> dict[str, str]:
    return {role: "" for role, _ in ROLES}


def load_team(slug: str) -> dict | None:
    """Return the parsed team.json, or None if the product folder doesn't exist."""
    p = team_path_for(slug)
    if p is None:
        return None
    if not p.exists():
        return {"slug": slug, "team": empty_team_map(), "last-updated": ""}
    data = json.loads(p.read_text())
    # Backfill any missing roles (e.g., file from before a new role was added).
    team = data.setdefault("team", {})
    for role, _ in ROLES:
        team.setdefault(role, "")
    return data


def save_team(slug: str, data: dict) -> None:
    p = team_path_for(slug)
    if p is None:
        raise RuntimeError(f"no product folder for slug '{slug}'")
    data["last-updated"] = date.today().isoformat()
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def cmd_get(args: argparse.Namespace) -> None:
    data = load_team(args.slug)
    if data is None:
        print(f"error: no product folder for slug '{args.slug}' under web-apps/ mobile-apps/ desktop-apps/", file=sys.stderr)
        sys.exit(1)
    if args.role not in ROLE_KEYS:
        print(f"error: unknown role '{args.role}'. Valid: {', '.join(r for r, _ in ROLES)}", file=sys.stderr)
        sys.exit(2)
    name = data["team"].get(args.role, "")
    if not name:
        sys.exit(1)
    print(name)


def cmd_set(args: argparse.Namespace) -> None:
    if args.role not in ROLE_KEYS:
        print(f"error: unknown role '{args.role}'. Valid: {', '.join(r for r, _ in ROLES)}", file=sys.stderr)
        sys.exit(2)
    if not VALID_NAME.match(args.name):
        print(
            "error: invalid name. Rules: 1-30 chars, must start with letter or digit, "
            "allow letters / digits / spaces / hyphens / apostrophes only.",
            file=sys.stderr,
        )
        sys.exit(2)
    data = load_team(args.slug)
    if data is None:
        print(f"error: no product folder for slug '{args.slug}'", file=sys.stderr)
        sys.exit(1)
    data["team"][args.role] = args.name
    save_team(args.slug, data)
    print(f"set {args.role} = {args.name}")


def cmd_list(args: argparse.Namespace) -> None:
    data = load_team(args.slug)
    if data is None:
        print(f"error: no product folder for slug '{args.slug}'", file=sys.stderr)
        sys.exit(1)
    team = data["team"]
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    p = team_path_for(args.slug)
    rel = p.relative_to(REPO_ROOT) if p else "(none)"
    print(f"Team for `{args.slug}` (path: {rel}):")
    print()
    print(f"  #  {'Role':<33} {'Name':<32}")
    print(f"  -  {'-' * 33} {'-' * 32}")
    for i, (role, label) in enumerate(ROLES, 1):
        name = team.get(role, "")
        display = name if name else "(unnamed — uses role label)"
        print(f"  {i}  {label:<33} {display:<32}")
    print()
    last = data.get("last-updated", "")
    print(f"  Last updated: {last or '(never set)'}")
    print()
    print("  Notes: names can be set or edited; members can NOT be deleted")
    print("  (the 9 roles are critical to the build workflow).")


def cmd_init(args: argparse.Namespace) -> None:
    p = team_path_for(args.slug)
    if p is None:
        print(f"error: no product folder for slug '{args.slug}'", file=sys.stderr)
        sys.exit(1)
    if p.exists():
        print(f"team.json already exists at {p.relative_to(REPO_ROOT)} (no-op)")
        return
    save_team(args.slug, {"slug": args.slug, "team": empty_team_map()})
    print(f"initialized {p.relative_to(REPO_ROOT)}")


def cmd_reset(args: argparse.Namespace) -> None:
    data = load_team(args.slug)
    if data is None:
        print(f"error: no product folder for slug '{args.slug}'", file=sys.stderr)
        sys.exit(1)
    data["team"] = empty_team_map()
    save_team(args.slug, data)
    print(f"reset all names for `{args.slug}` to unnamed")


def cmd_roles(args: argparse.Namespace) -> None:
    for i, (role, label) in enumerate(ROLES, 1):
        print(f"{i}\t{role}\t{label}")


def cmd_path(args: argparse.Namespace) -> None:
    p = team_path_for(args.slug)
    if p is None:
        print(f"error: no product folder for slug '{args.slug}'", file=sys.stderr)
        sys.exit(1)
    print(p.relative_to(REPO_ROOT))


def main() -> None:
    p = argparse.ArgumentParser(
        description="Manage per-product senior-engineer team-member names.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_get = sub.add_parser("get", help="print the name for a role (empty + exit 1 if unnamed)")
    p_get.add_argument("slug")
    p_get.add_argument("role")
    p_get.set_defaults(func=cmd_get)

    p_set = sub.add_parser("set", help="set the name for a role (validates)")
    p_set.add_argument("slug")
    p_set.add_argument("role")
    p_set.add_argument("name")
    p_set.set_defaults(func=cmd_set)

    p_list = sub.add_parser("list", help="print the team")
    p_list.add_argument("slug")
    p_list.add_argument("--json", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_init = sub.add_parser("init", help="create empty team.json if missing")
    p_init.add_argument("slug")
    p_init.set_defaults(func=cmd_init)

    p_reset = sub.add_parser("reset", help="clear all names; file stays (no delete)")
    p_reset.add_argument("slug")
    p_reset.set_defaults(func=cmd_reset)

    p_roles = sub.add_parser("roles", help="print the fixed role list")
    p_roles.set_defaults(func=cmd_roles)

    p_path = sub.add_parser("path", help="print the team.json path for this slug")
    p_path.add_argument("slug")
    p_path.set_defaults(func=cmd_path)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
