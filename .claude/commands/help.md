---
description: Show a quick menu of available commands and suggested next actions based on the current pipeline state. Lower-overhead than reading HELP.md end-to-end.
---

You are about to surface a help menu for the user. Be concise — this command exists so they don't have to open `HELP.md` every time they want to remember a command or check what to do next.

### Pre-flight — read current state

1. Re-read @CLAUDE.md (it's auto-loaded but re-checking pipeline state).
2. Skim `market-research/` for the most recent files (sort by mtime or date in filename):
   - Latest `scan-*.md` and its `status` (draft / active)
   - Latest `triage-*.md`
   - Any `validation-*.md` files (and their decisions)
   - Any `scoping-*.md` files
   - Any `trends-*.md` files (note dates — flag if >7 days old)
3. List `ideas/` (excluding `ideas/killed/`) — count active cards and note their `status` values.
4. List `web-apps/*/MVP.md` and `mobile-apps/*/MVP.md` if any — note `status` values.
5. List `<web-apps|mobile-apps>/*/design/` to see if any design phases are active.

### Do

Present, in this order, **a tight summary** (not a wall of text):

**Pipeline state** — 3-5 lines, e.g.:

> - **Active scan:** `market-research/scan-2026-05-29.md` (status: active, 5 territories)
> - **Active cards:** 2 — `payment-forms` (in-validation), `dev-fortune-cookie` (green-lit)
> - **In-flight briefs:** 1 — `dev-fortune-cookie/MVP.md` (status: green-lit-to-build)
> - **Latest trend report:** 4 days old
> - **Active design phase:** none

If state is empty (fresh repo), say so: "No active state yet — this is a clean slate."

**Quick command menu** — categorized:

> **Pipeline phase commands:**
> - `/scan [broad|focused <topic>]` — market scan
> - `/discover [territories]` — brainstorm idea cards (works one-command without args)
> - `/validate-card <slug>` — 3-reviewer validation pass
> - `/scope-mvp <slug>` — draft the MVP brief + scope/code reviews
> - `/research-design <slug>` — design-direction report
> - `/draft-design-brief <slug>` — consolidated design brief + reviewer
> - `/trend-check [triggered <reason>]` — sweep for shifts
> - `/help` — this menu
>
> **Helper skills (invoked by phrasing):**
> - "export this as PDF" → `doc-export`
> - "preview this page" → `web-preview`

**Suggested next actions** — 2-4 items based on state, prioritized:

For each suggestion, give a one-line "why" so the user can pick informed.

Examples:

- "Validate `payment-forms` (it's been in `in-validation` since 2026-05-29 — finish the 2 remaining reviewers)."
- "Run `/trend-check` (last sweep was 8 days ago; weekly cadence is the default per `guides/market/trend-monitoring.md`)."
- "Start a fresh discovery with `/discover` (no active scan or cards; clean-slate state)."

End with a one-liner pointing to `HELP.md` for the full reference and `CLAUDE.md` for the full pipeline orchestration.

### Stop here — no auto-invocation

After showing the menu, **stop**. Do not auto-run any of the suggested commands. The user picks.
