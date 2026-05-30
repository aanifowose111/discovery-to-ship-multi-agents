# user-context/

**Your personal context for this clone of the workspace.** Optional but recommended.

When you run `/discover` with no arguments and no active scan, Claude bootstraps a discovery cycle by inferring what to brainstorm about. Without your input, that inference defaults to **open discovery** (broad capability shifts + adjacent workflows + competitor weaknesses, no founder-fit constraint) — which works, but produces less personally-relevant candidates.

Add an `INTERESTS.md` file here to give Claude something to anchor on:

- Your professional background (languages, frameworks, domains you've shipped in)
- Hobbies or personal interests you'd consider building a product around
- Industries or roles you have inside-track knowledge of
- Specific product ideas you've already had but haven't acted on
- Things you explicitly do **not** want to work on

Claude will weight discovery toward founder-market fit signals matching your context.

## How to populate it

```bash
cp user-context/INTERESTS.md.example user-context/INTERESTS.md
# Then edit user-context/INTERESTS.md with your specifics
```

`INTERESTS.md` is gitignored — your personal context stays local, never enters git. Same pattern as `ideas/`, `web-apps/`, etc.

## What about the maintainer's context?

`CLAUDE.md` at the repo root mentions Abiodun Anifowose (the maintainer / original author) and his shipped products. **That line stays as attribution** — it tells contributors who built this workspace. It is *not* the same as your founder context.

When you fork this repo for your own use:
- Optionally edit the `CLAUDE.md` owner intro to reflect *your* identity if you want the workspace fully your own.
- Always (if you want personalized discovery) populate `user-context/INTERESTS.md`.

The `/discover` command checks `user-context/INTERESTS.md` first and falls back to the CLAUDE.md owner intro only as a last resort.

## What stays here

- `INTERESTS.md` — your founder profile + interests (gitignored).
- `IDEAS_BACKLOG.md` — optional; a place to jot product ideas you've had outside `/discover` cycles, for `/discover` to mine later (gitignored).
- `README.md` — this file (committed).
- `INTERESTS.md.example` — the template (committed).
