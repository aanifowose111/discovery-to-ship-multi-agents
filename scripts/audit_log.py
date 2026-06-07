#!/usr/bin/env python3
"""
audit_log.py — read/write the workspace's personal-space audit log.

The audit log lives at `user-context/audit-log.jsonl` (gitignored, personal-
space) and records important user-driven decisions and actions. It backs the
`/log` slash command and gates the first-launch onboarding re-prompt.

What gets logged (and only these types — see CLAUDE.md § Audit log):
  - onboarding-skip          user deferred populating INTERESTS.md / IDEAS.md
  - project-delete           a discovery project run-folder was deleted via /projects
  - card-kill                a card was killed (mirrors the card's frontmatter)
  - card-revive              a previously-killed card was restored to ideas/
  - build-milestone          a key build-stage achievement (project initialized, subsystem
                             completed, ready-to-deploy state reached, shipped, etc.)
  - rework-applied           the user reworked a card/MVP/V1 via /rework (with the temp-file
                             review-and-commit flow), possibly including overrides of REJECT
                             verdicts (which are recorded with their justifications)
  - consolidation-applied    the user consolidated misalignments between card/scope/MVP/V1
                             via /consolidate
  - user-note                free-text entry added via /log <text>

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
import os
import secrets
import shutil
import sys
import textwrap
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
    "rework-applied",
    "consolidation-applied",
    "user-note",
}

# ANSI color codes (used by the tree renderer; opt out with --no-color).
class _C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GRAY = "\033[90m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"


# Per-type color (None = default terminal color).
_TYPE_COLOR = {
    "onboarding-skip": _C.YELLOW,
    "project-delete": _C.RED,
    "card-kill": _C.RED,
    "card-revive": _C.GREEN,
    "build-milestone": _C.CYAN,
    "rework-applied": _C.MAGENTA,
    "consolidation-applied": _C.MAGENTA,
    "user-note": None,
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


def _supports_color(force_no_color: bool) -> bool:
    """Return True if ANSI colors should be emitted."""
    if force_no_color or os.environ.get("NO_COLOR"):
        return False
    return sys.stdout.isatty()


def _paint(text: str, color: str | None, use_color: bool) -> str:
    """Wrap `text` in ANSI color codes when color output is enabled."""
    if not use_color or not color:
        return text
    return f"{color}{text}{_C.RESET}"


def _format_timestamp(ts: str) -> str:
    """`2026-06-06T18:33:09Z` → `2026-06-06 18:33:09 UTC`."""
    if not ts:
        return "?"
    cleaned = ts.replace("T", " ").rstrip("Z").rstrip()
    return f"{cleaned} UTC"


def _read_entries_with_lines() -> list[dict]:
    """Read entries from the JSONL file and attach each entry's source line number
    under the `_line` key. The line number is the 1-based position in the file —
    useful for jumping to the entry in an editor.
    """
    if not LOG_PATH.exists():
        return []
    entries: list[dict] = []
    for line_num, line in enumerate(LOG_PATH.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            entry["_line"] = line_num
            entries.append(entry)
        except json.JSONDecodeError:
            print(
                f"warning: skipping malformed line {line_num} in {LOG_PATH}: {line[:80]}",
                file=sys.stderr,
            )
    return entries


def cmd_list(args: argparse.Namespace) -> None:
    raw_entries = _read_entries_with_lines()

    # Filter by type
    if args.type:
        raw_entries = [e for e in raw_entries if e.get("type") == args.type]

    # Sort newest first
    raw_entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

    # JSON output drops the internal `_line` field
    if args.json:
        sanitized = [{k: v for k, v in e.items() if k != "_line"} for e in raw_entries]
        print(json.dumps(sanitized, indent=2, ensure_ascii=False))
        return

    # Empty state
    if not raw_entries:
        if args.type:
            print(f"(no entries of type `{args.type}`)")
        else:
            print("(no entries)")
        return

    # Tree rendering
    use_color = _supports_color(force_no_color=getattr(args, "no_color", False))
    term_width = shutil.get_terminal_size((100, 24)).columns
    # Description column starts at col 16 ("│   └── desc   "); wrap to fit.
    desc_indent = "│   " + " " * 11
    desc_wrap_width = max(40, term_width - len(desc_indent) - 1)

    try:
        rel_path = LOG_PATH.relative_to(REPO_ROOT)
    except ValueError:
        rel_path = LOG_PATH

    # Header
    count_str = f"{len(raw_entries)} {'entry' if len(raw_entries) == 1 else 'entries'}"
    header_bits = [
        _paint("audit-log", _C.BOLD, use_color),
        _paint(str(rel_path), _C.DIM, use_color),
        count_str,
        "newest first",
    ]
    if args.type:
        header_bits.append(_paint(f"filter: type={args.type}", _C.CYAN, use_color))
    print("  ·  ".join(header_bits))
    print(_paint("│", _C.GRAY, use_color))

    # Entries
    for i, e in enumerate(raw_entries):
        is_last = i == len(raw_entries) - 1
        branch = "└──" if is_last else "├──"
        continuation = "    " if is_last else "│   "

        line_num = e.get("_line", "?")
        entry_id = e.get("id", "?")
        entry_type = e.get("type", "?")
        timestamp = _format_timestamp(e.get("timestamp", ""))
        description = e.get("description") or "(no description)"

        # Entry parent line: branch + id + line-number badge
        id_part = _paint(entry_id, _C.BOLD, use_color)
        line_part = _paint(f"(L{line_num})", _C.GRAY, use_color)
        print(
            f"{_paint(branch, _C.GRAY, use_color)} {id_part}  {line_part}"
        )

        # Sub-branch: type
        type_color = _TYPE_COLOR.get(entry_type)
        sub_branch_type = "├──"
        print(
            f"{_paint(continuation, _C.GRAY, use_color)}"
            f"{_paint(sub_branch_type, _C.GRAY, use_color)} "
            f"{_paint('type', _C.DIM, use_color)}  "
            f"{_paint(entry_type, type_color, use_color)}"
        )

        # Sub-branch: time
        sub_branch_time = "├──"
        print(
            f"{_paint(continuation, _C.GRAY, use_color)}"
            f"{_paint(sub_branch_time, _C.GRAY, use_color)} "
            f"{_paint('time', _C.DIM, use_color)}  "
            f"{_paint(timestamp, _C.DIM, use_color)}"
        )

        # Sub-branch: desc (last sub-branch; wrapped to terminal width)
        wrapped = textwrap.wrap(description, width=desc_wrap_width) or [""]
        sub_branch_desc = "└──"
        for j, wline in enumerate(wrapped):
            if j == 0:
                print(
                    f"{_paint(continuation, _C.GRAY, use_color)}"
                    f"{_paint(sub_branch_desc, _C.GRAY, use_color)} "
                    f"{_paint('desc', _C.DIM, use_color)}  {wline}"
                )
            else:
                # Continuation lines align under the description text.
                # Parent indent: continuation (4) + "└── " (4) + "desc  " (6) = 14.
                # Continuation indent must match: continuation (4) + 10 spaces.
                print(
                    f"{_paint(continuation, _C.GRAY, use_color)}"
                    f"{' ' * 10}{wline}"
                )

        # Blank gutter between entries
        if not is_last:
            print(_paint("│", _C.GRAY, use_color))


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

    p_list = sub.add_parser("list", help="list entries (newest first) as a tree")
    p_list.add_argument("--type", help="filter by entry type")
    p_list.add_argument("--json", action="store_true", help="machine-readable output")
    p_list.add_argument(
        "--no-color",
        action="store_true",
        help="disable ANSI colors (auto-disabled when stdout isn't a TTY or NO_COLOR is set)",
    )
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
