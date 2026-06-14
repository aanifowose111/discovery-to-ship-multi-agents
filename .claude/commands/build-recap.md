---
description: Generate a delta-since-last-recap summary of a product's build progress. Distinct from `/recollect` (which reconstructs full state from scratch); `build-recap` is the lighter "what changed since last time I ran this" view. Reads `BUILD_STATUS.md`, recent commits, `VERIFIED.md` updates, `ACTION_REQUIRED.md` updates, and surfaces the delta. Renames the historical `/recap` to avoid collision with Claude Code's built-in. Read-only.
argument-hint: <product-slug> [--since <date>]
---

You are about to generate a build-progress recap for one product, scoped to the delta since the last recap (or since `--since <date>` if specified).

**Use this when:**
- You haven't touched the product in a few days and want a quick "what's the state" view without the full `/recollect` synthesis
- You're about to resume work and want a 30-second scan of where things stand
- You're sharing progress with someone (a collaborator, a journal, a tweet) and want the recent-activity slice

**Don't use this for:**
- Full state reconstruction — use `/recollect <slug>` for that (heavier, more thorough)
- Resumption of build — use `/continue-build <slug>` (calls the orchestrator)
- Long-form timeline — `/recollect` covers that

**Arguments:** $ARGUMENTS — the product slug, optionally with `--since <YYYY-MM-DD>` to scope the recap (defaults to: since the last `last-recap-at` frontmatter in `BUILD_STATUS.md`, or last 7 days if none).

### Pre-flight

1. **Locate the product folder.** Stop if not found.

2. **Determine the scope window:**
   - If `--since <date>` is given, use it.
   - Otherwise, read `<product-folder>/BUILD_STATUS.md` frontmatter for `last-recap-at:`; if present, use it as the cutoff.
   - Otherwise, default to **7 days ago**.

### Do — read the delta sources

In parallel, read:

1. **`<product-folder>/BUILD_STATUS.md`** — parse subsystems + History entries; flag any subsystem whose History gained an entry since the cutoff.

2. **Git log** for the product folder: `git log --oneline --since="<cutoff>" -- <product-folder>/`. Capture commit subjects.

3. **`<product-folder>/VERIFIED.md`** if it exists — read frontmatter `last-updated:`. If it's newer than the cutoff, parse new entries since cutoff.

4. **`<product-folder>/ACTION_REQUIRED.md`** if it exists — read frontmatter `last-scanned-at:`. Note any newly-completed items in the history section since cutoff.

5. **`<product-folder>/CHECKLIST.md`** if it exists — count any items flipped to `[x]` since cutoff.

6. **`<product-folder>/SMOKE.md`** if it exists — read Run history; note runs since cutoff.

### Generate the recap

Synthesize a concise (under 250-word) recap with these sections:

```markdown
# Build recap — <slug> — <cutoff> to today

## Subsystems progressed
- <Subsystem name>: `[ ]` → `[>]` (started <date>) / `[>]` → `[x]` (completed <date>)
- ...

## Commits (N total)
- <date>: <commit subject>
- ...

## Verifications recorded
- <count> new entries in VERIFIED.md (X `[x]`, Y `[~]`, Z `[?]`, W `[!]`)
- Notable: <one flagged not-working entry, if any>

## Smoke runs
- <date>: <N pass / M fail / K skip>

## Action items completed
- <count> ACTION_REQUIRED items crossed out
- Outstanding: <count> still pending (<X blocking>)

## Open questions / next actions
- <inferred from the delta — e.g., "auth subsystem still [>]; backend specialist last touched 3 days ago">
- <suggest 1-2 next steps>
```

### Update frontmatter (optional)

Append `last-recap-at: <today>` to `BUILD_STATUS.md` frontmatter. This is the only write the command performs. Subsequent recaps will default to this cutoff unless `--since` overrides.

If the user prefers no frontmatter write (e.g., they're previewing), respect that — just don't update.

### Stop here

Show the recap to the user. No checkpoint question; the command is read-only synthesis.

> Recap done. Want to continue the build? → `/continue-build <slug>`. Want fuller context? → `/recollect <slug>`. Want a deeper review of where things sit? → `/status`.

### Notes

- **Why renamed from `/recap` to `/build-recap`:** Claude Code's built-in handling of `/recap` made it collide; we use the explicit `build-recap` to scope to product builds.
- **Distinction from `/recollect`:** `/recollect` is exhaustive (full state, all artifacts, deep synthesis). `/build-recap` is the delta — what changed since last time. Use `/recollect` first time on a product, then `/build-recap` for incremental check-ins.
- **No audit-log entry.** Recaps aren't milestones; they're a read-only view.
- **Stack-agnostic.** Works for web/mobile/desktop equally; the source files are the same artifacts.
