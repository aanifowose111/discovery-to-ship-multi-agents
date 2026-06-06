---
description: View, add, or delete entries in your personal-space audit log (`user-context/audit-log.jsonl`). The audit log records important user-driven decisions and actions — onboarding-skip choices (which gate the first-launch re-prompt), discovery-project deletions, card kills/revives, and any free-text notes you add. The log is gitignored — it never leaves your machine.
argument-hint: [<free-text note> | delete <id> | clear | type <onboarding-skip|project-delete|card-kill|card-revive|build-milestone|user-note>]
---

You are about to interact with the audit log at `user-context/audit-log.jsonl`. The log is **personal-space (gitignored)** — it never enters git. The helper script is `scripts/audit_log.py`.

**Arguments:** `$ARGUMENTS`
- (empty) → display the log (newest first)
- `delete <id>` → remove a single entry by its 8-char id (confirm first)
- `clear` → remove all entries (confirm first via `AskUserQuestion`)
- `type <type>` → filter the display to entries of one type
- anything else → append a `user-note` entry with the free text

### Do

Dispatch based on `$ARGUMENTS`.

**1. No arguments (display all):**

Run `python3 scripts/audit_log.py list` and show the output in a code block. If empty, say:

> Your audit log is empty. Add a note with `/log <your note>`. The log is at `user-context/audit-log.jsonl` (gitignored).

After the display, briefly remind the user of the available subcommands (add note / delete / clear / type filter).

**2. `delete <id>`:**

1. Verify the id exists first: `python3 scripts/audit_log.py list --json` and check whether any entry has that id. If not, tell the user and stop.
2. Surface the entry to be deleted (timestamp, type, description).
3. Use `AskUserQuestion` to confirm:
   - **Delete this entry** — proceed.
   - **Cancel** — stop.
4. On `Delete this entry`, run `python3 scripts/audit_log.py delete <id>` and show the result. Note for `onboarding-skip` entries: deleting one will cause Claude to re-fire the onboarding interrupt on the next session if `INTERESTS.md` or `IDEAS.md` is still missing.

**3. `clear`:**

1. Use `AskUserQuestion` to confirm:
   - **Clear the entire log** — irreversible.
   - **Cancel** — stop.
2. On confirmation, run `python3 scripts/audit_log.py clear`.
3. Tell the user: if an `onboarding-skip` entry was in the log and `INTERESTS.md` / `IDEAS.md` are missing, onboarding will re-fire next session.

**4. `type <type>`:**

Validate that `<type>` is one of: `onboarding-skip`, `project-delete`, `card-kill`, `card-revive`, `build-milestone`, `user-note`. If not, tell the user the valid types and stop. Otherwise run `python3 scripts/audit_log.py list --type <type>` and show output in a code block.

**5. Anything else (add user-note):**

1. Treat the full `$ARGUMENTS` as the note text.
2. Run `python3 scripts/audit_log.py add user-note "<arguments>"` (be careful to escape quotes in the argument — use a `$VAR` shell variable if the text contains `"`).
3. Echo the new id and a one-line confirmation: "added user-note entry `<id>`."

### What gets logged automatically (no user action needed)

Claude writes entries on these events without being asked:

| Event | Type | Where in code |
|---|---|---|
| User picks "Prefer to update later" at first-launch onboarding | `onboarding-skip` | `CLAUDE.md` § Session continuity → Rule A |
| User confirms a destructive `/projects delete` | `project-delete` | `.claude/commands/projects.md` |
| User explicitly kills a card after validation/scoping | `card-kill` | `.claude/commands/validate-card.md`, `scope-mvp.md` |
| User restores a killed card | `card-revive` | (no command yet — manual via `mv ideas/killed/<run>/<slug>.md ideas/<run>/`) |
| Project initialized via `/start-build`, `BUILD_STATUS.md` subsystem flips to `[x]`, ready-to-deploy state reached, or app shipped via `/ship-app` | `build-milestone` | `.claude/commands/start-build.md`, `.claude/commands/ship-app.md`, `.claude/agents/senior-software-engineer.md` |

`/log` itself is the only entry point for `user-note`.

**For `type` filtering** (`/log type build-milestone`): valid types are `onboarding-skip`, `project-delete`, `card-kill`, `card-revive`, `build-milestone`, `user-note`.

### Stop here

This command is interactive: dispatch → respond. Do not chain into any other slash command. Do not advance any artifact status as a side effect.
