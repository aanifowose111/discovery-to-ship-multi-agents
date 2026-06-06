#!/usr/bin/env python3
"""
audit_log.py — read/write the workspace's personal-space audit log.

The audit log lives at `user-context/audit-log.jsonl` (gitignored, personal-
space) and records important user-driven decisions and actions. It backs the
`/log` slash command and gates the first-launch onboarding re-prompt.

What gets logged (and only these types — see CLAUDE.md § Audit log):
  - onboarding-skip   user deferred populating INTERESTS.md / IDEAS.md
  - project-delete    a discovery project run-folder was deleted via /projects
  - card-kill         a card was killed (mirrors the card's frontmatter)
  - card-revive       a previously-killed card was restored to ideas/
  - build-milestone   a key build-stage achievement (project initialized, subsystem
                      completed, ready-to-deploy state reached, shipped, etc.)
  - user-note         free-text entry added via /log <text>

What does NOT get logged: routine file reads, command invocations, status
flips, commits. Git history covers those. The audit log is for state
decisions and intentional records, not telemetry.

Each line is a JSON object:
  {"timestamp": "2026-06-06T14:32:00Z", "id": "a3f2b1c8",
   "type": "user-note", "description": "..."}

Run from the repo root:
  python3 scripts/audit_log.py add <type> "<description>"   # append entry, print id
  python3 scripts/audit_log.py list                          # all entries, newest first
  python3 scripts/audit_log.py list --type <type>            # filter by type
  python3 scripts/audit_log.py list --json                   # machine-readable
  python3 scripts/audit_log.py delete <id>                   # remove entry by id
  python3 scripts/audit_log.py clear                         # remove all entries (no confirm — caller asks)
  python3 scripts/audit_log.py has <type>                    # exit 0 if any entry of that type exists, else 1

Exit codes:
  0 = success (or, for `has`, the type was found)
  1 = failure (entry not found, or `has` did not find the type)
  2 = usage error (unknown type, etc.)
"""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = REPO_ROOT / "user-context" / "audit-log.jsonl"

VALID_TYPES = {
    "onboarding-skip",
    "project-delete",
    "card-kill",
    "card-revive",
    "build-milestone",
    "user-note",
}


def now_iso() -> str:
    """ISO-8601 UTC timestamp, second precision, Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_id() -> str:
    """8-char hex id. Collisions are astronomically unlikely at our entry volume."""
    return secrets.token_hex(4)


def read_entries() -> list[dict]:
    if not LOG_PATH.exists():
        return []
    entries: list[dict] = []
    for line in LOG_PATH.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"warning: skipping malformed line in {LOG_PATH}: {line[:80]}", file=sys.stderr)
    return entries


def write_entries(entries: list[dict]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not entries:
        LOG_PATH.write_text("")
        return
    LOG_PATH.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n")


def cmd_add(args: argparse.Namespace) -> None:
    if args.type not in VALID_TYPES:
        print(
            f"error: unknown entry type '{args.type}'. Valid: {', '.join(sorted(VALID_TYPES))}",
            file=sys.stderr,
        )
        sys.exit(2)
    entries = read_entries()
    entry = {
        "timestamp": now_iso(),
        "id": new_id(),
        "type": args.type,
        "description": args.description,
    }
    entries.append(entry)
    write_entries(entries)
    print(entry["id"])


def cmd_list(args: argparse.Namespace) -> None:
    entries = read_entries()
    if args.type:
        entries = [e for e in entries if e.get("type") == args.type]
    entries = sorted(entries, key=lambda e: e.get("timestamp", ""), reverse=True)
    if args.json:
        print(json.dumps(entries, ensure_ascii=False, indent=2))
        return
    if not entries:
        print("(no entries)")
        return
    for e in entries:
        print(
            f"{e.get('id', '?')}  {e.get('timestamp', '?')}  {e.get('type', '?'):<16}  {e.get('description', '')}"
        )


def cmd_delete(args: argparse.Namespace) -> None:
    entries = read_entries()
    matching = [e for e in entries if e.get("id") == args.id]
    if not matching:
        print(f"error: no entry with id '{args.id}'", file=sys.stderr)
        sys.exit(1)
    entries = [e for e in entries if e.get("id") != args.id]
    write_entries(entries)
    print(f"deleted {args.id}")


def cmd_clear(args: argparse.Namespace) -> None:
    if LOG_PATH.exists():
        LOG_PATH.unlink()
    print("audit log cleared")


def cmd_has(args: argparse.Namespace) -> None:
    entries = read_entries()
    if any(e.get("type") == args.type for e in entries):
        sys.exit(0)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Read/write the workspace's personal-space audit log.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="append an entry; print the new id")
    p_add.add_argument("type", help=f"entry type. one of: {', '.join(sorted(VALID_TYPES))}")
    p_add.add_argument("description", help="free-text description")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="list entries (newest first)")
    p_list.add_argument("--type", help="filter by entry type")
    p_list.add_argument("--json", action="store_true", help="machine-readable output")
    p_list.set_defaults(func=cmd_list)

    p_del = sub.add_parser("delete", help="delete an entry by id")
    p_del.add_argument("id", help="the 8-char hex id printed by `add` or `list`")
    p_del.set_defaults(func=cmd_delete)

    p_clear = sub.add_parser("clear", help="delete all entries (no confirm — caller asks)")
    p_clear.set_defaults(func=cmd_clear)

    p_has = sub.add_parser("has", help="exit 0 if any entry of given type exists, else 1")
    p_has.add_argument("type")
    p_has.set_defaults(func=cmd_has)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
