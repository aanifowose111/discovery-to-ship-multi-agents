# user-context/

**Your personal context for this clone of the workspace.** Optional but recommended.

When you run `/discover` with no arguments and no active scan, Claude bootstraps a discovery cycle by inferring what to brainstorm about. Without your input, that inference defaults to **open discovery** (broad capability shifts + adjacent workflows + competitor weaknesses, no founder-fit constraint) — which works, but produces less personally-relevant candidates.

Two files you can populate, both optional, both gitignored once you create the live versions:

**`INTERESTS.md`** — your founder context. Used by `/discover` to anchor brainstorming. Includes:

- Your professional background (languages, frameworks, domains you've shipped in)
- Hobbies or personal interests you'd consider building a product around
- Industries or roles you have inside-track knowledge of
- Specific product ideas you've already had but haven't acted on
- Things you explicitly do **not** want to work on

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
- Things to actively flag (scope creep, premature optimization, etc.)

Your policy **overrides workspace defaults and senior-engineer-persona conventions** for matters of taste. Correctness and security still win.

## How to populate them

```bash
cp user-context/INTERESTS.md.example user-context/INTERESTS.md
cp user-context/POLICY.md.example user-context/POLICY.md
# Then edit each with your specifics
```

Both files are gitignored — your personal context stays local, never enters git. Same pattern as `ideas/`, `web-apps/`, etc.

## What about the maintainer's context?

`CLAUDE.md` at the repo root mentions Abiodun Anifowose (the maintainer / original author) and his shipped products. **That line stays as attribution** — it tells contributors who built this workspace. It is *not* the same as your founder context.

When you fork this repo for your own use:
- Optionally edit the `CLAUDE.md` owner intro to reflect *your* identity if you want the workspace fully your own.
- Always (if you want personalized discovery) populate `user-context/INTERESTS.md`.

The `/discover` command checks `user-context/INTERESTS.md` first and falls back to the CLAUDE.md owner intro only as a last resort.

## What stays here

- `INTERESTS.md` — your founder profile + interests (gitignored).
- `POLICY.md` — your personal coding-and-build policy (gitignored).
- `IDEAS_BACKLOG.md` — optional; a place to jot product ideas you've had outside `/discover` cycles, for `/discover` to mine later (gitignored).
- `README.md` — this file (committed).
- `INTERESTS.md.example` — the template (committed).
- `POLICY.md.example` — the template (committed).
