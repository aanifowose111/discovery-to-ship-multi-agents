# user-context/

**Your personal context for this clone of the workspace.** Optional but recommended.

When you run `/discover` with no arguments and no active scan, Claude bootstraps a discovery cycle by inferring what to brainstorm about. Without your input, that inference defaults to **open discovery** (broad capability shifts + adjacent workflows + competitor weaknesses, no founder-fit constraint) — which works, but produces less personally-relevant candidates.

Four files live here, all gitignored once you create the live versions. Three are user-populated (`INTERESTS.md`, `IDEAS.md`, `POLICY.md`); the fourth (`audit-log.jsonl`) is written by Claude on important actions and viewable via the `/log` slash command.

**`INTERESTS.md`** — your founder context. Used by `/discover` to anchor brainstorming on territories that fit you. Includes:

- Professional background (languages, frameworks, domains you've shipped in)
- Hobbies or personal interests you'd consider building around
- Industries or roles you have inside-track knowledge of
- Things you explicitly do **not** want to work on

**`IDEAS.md`** — your seed-ideas backlog. **Distinct from `ideas/` at the repo root** (which holds *validated* idea cards from formal `/discover` cycles); this file is your mental staging area — products you've already thought about but not formalized. Used by `/discover` to weight brainstorming toward what's already on your mind. **Strongest single signal** for avoiding generic candidates that get killed in validation.

**`POLICY.md`** — your personal coding-and-build policy. Used by Claude **whenever it writes code, drafts a brief, or proposes architecture** in this workspace. Includes:

- Style basics (indent, line length, naming)
- Patterns to favor / avoid
- Frameworks & libraries you prefer or refuse
- Documentation style and depth
- Testing philosophy (coverage, mocking, TDD, e2e)
- Error-handling defaults
- Performance-vs-readability trade-offs
- Security defaults
- **Hard rules** — things Claude must never do
- Voice / tone for user-facing strings
- Decision-making preferences

Your policy **overrides workspace defaults and senior-engineer-persona conventions** for matters of taste. Correctness and security still win.

**`audit-log.jsonl`** — your personal audit trail. Auto-written by Claude when you make important user-driven decisions (skipping onboarding, deleting a discovery project, killing or reviving a card) and any free-text notes you add via `/log <text>`. JSONL format — one entry per line. View / add / delete via the `/log` slash command (see `CLAUDE.md` § "Audit log" for the full type table). Routine file reads, command invocations, status flips, and commits are NOT logged — git history covers those.

## How to populate them

The fastest path is the **onboarding flow** that fires automatically when you launch Claude Code in this repo with `INTERESTS.md` missing — Claude walks you through it conversationally and writes the files for you (see `CLAUDE.md` § "Session continuity" for the trigger conditions).

If you'd rather do it manually:

```bash
cp user-context/INTERESTS.md.example user-context/INTERESTS.md
cp user-context/IDEAS.md.example     user-context/IDEAS.md
cp user-context/POLICY.md.example    user-context/POLICY.md
# Then edit each with your specifics
```

All three live files are gitignored — your personal context stays local, never enters git. Same pattern as `ideas/`, `web-apps/`, etc.

## What about the maintainer's context?

`CLAUDE.md` at the repo root mentions Abiodun Anifowose (the maintainer / original author) and his shipped products. **That line stays as attribution** — it tells contributors who built this workspace. It is *not* the same as your founder context.

When you fork this repo for your own use:
- Optionally edit the `CLAUDE.md` owner intro to reflect *your* identity if you want the workspace fully your own.
- Always (if you want personalized discovery) populate `user-context/INTERESTS.md`.

The `/discover` command checks `user-context/INTERESTS.md` first and falls back to the CLAUDE.md owner intro only as a last resort.

## What stays here

- `INTERESTS.md` — your founder profile + interests (gitignored).
- `IDEAS.md` — your seed-ideas backlog (gitignored).
- `POLICY.md` — your personal coding-and-build policy (gitignored).
- `audit-log.jsonl` — your personal audit trail, written by Claude on important actions (gitignored).
- `README.md` — this file (committed).
- `INTERESTS.md.example` — the interests template (committed).
- `IDEAS.md.example` — the ideas-backlog template (committed).
- `POLICY.md.example` — the policy template (committed).
- `audit-log.jsonl.example` — the audit-log format template (committed).
