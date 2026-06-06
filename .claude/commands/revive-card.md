---
description: Restore a killed idea card back to active state. Moves the card from `ideas/killed/<run-id>/<slug>.md` to `ideas/<run-id>/<slug>.md`, resets the frontmatter to a safe baseline (`status: triaged`, kill-specific fields cleared), and appends a `card-revive` audit-log entry. Optionally also revives any orphaned MVP/V1 brief at `<stack>-apps/<slug>/`. The canonical undo path for kills made during `/validate-card`, `/scope-mvp`, `/scope-v1`, or `/discover`'s automatic triage.
argument-hint: <slug>
---

You are about to revive a killed idea card. This is the canonical inverse of a kill — replaces the manual `mv` workaround that was previously the only option (see the older note in `.claude/commands/log.md` if you're curious about the history). Follow the rules in `CLAUDE.md` § Slug uniqueness and § Audit log exactly.

**Arguments:** `$ARGUMENTS` — the slug of the killed card. The card must exist at `ideas/killed/<run-id>/<slug>.md` for some run-id.

### Inputs to read before doing anything

1. **Locate the killed card** with:
   ```bash
   find ideas/killed -name "<slug>.md" 2>/dev/null
   ```
   If no result, stop and tell the user: "No killed card at `ideas/killed/**/<slug>.md`. If you meant to revive a different artifact (e.g., a killed MVP brief), say so — those are not handled by `/revive-card`."

2. **Extract `<run-id>`** from the resolved path (`ideas/killed/<run-id>/<slug>.md`).

3. **Refuse if the slug is already active anywhere.** Run `python3 scripts/check_slug.py <slug>`. If exit 0 (slug is available), proceed. If exit 1, parse the reported conflicts:
   - If the ONLY conflict is the killed entry we're about to revive → fine, proceed.
   - If there's also an **active card** at any `ideas/<run-id'>/<slug>.md` → stop and tell the user: "Slug `<slug>` is already active in another run-folder (`<path>`). Reviving would create a `slug.collision` error per CLAUDE.md § Slug uniqueness. Either rename one of them or kill the active one first."
   - If there's an **app folder** at `<stack>-apps/<slug>/` → don't refuse, just note it (an existing orphan from a prior kill — the user gets to decide whether to also revive its brief, see step 6 below).

4. **Read the killed card** in full. Extract from frontmatter:
   - `killed-date`, `killed-reason`, `audit-log-id` (the kill's audit-log entry id, if present), `validation-report` (path to the validation report that fed the kill decision, if present).

5. **Check for orphaned briefs.** Look at `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/` (only one will exist, if any). If a folder is present, read `MVP.md` and `V1.md` if they exist — note their `status` fields (they were likely flipped to `killed` if the kill happened via `/scope-mvp` or `/scope-v1`).

### Do

#### Step 1 — Show the user the snapshot

Present what's about to be touched:

> Killed card found at `ideas/killed/<run-id>/<slug>.md`.
>
> - **Killed on:** `<killed-date>`
> - **Kill reason:** `<killed-reason — wrap long reasons>`
> - **Original validation report:** `<validation-report path, if set>`
> - **Linked audit-log entry:** `<audit-log-id, if set>` (you can view it via `/log` or `python3 scripts/audit_log.py list`)
>
> Orphaned app artifacts at `<stack>-apps/<slug>/`:
> - `<MVP.md path>` — status: `<current status, e.g. killed>`
> - `<V1.md path>` — status: `<current status>` (if present)
> - (or "None — clean revive" if no app folder exists)

#### Step 2 — Ask what to revive

Use `AskUserQuestion` with three options:

- **Restore card only** — moves the file back to active, resets card frontmatter to `status: triaged`. Any orphaned MVP/V1 brief stays as-is (`status: killed`) and will surface as a `slug.orphaned-app-after-kill` warning in `lint_pipeline.py`. Use when you want the card back but the brief is genuinely stale and shouldn't be reused.
- **Restore card AND revive MVP/V1 briefs** — same as above, plus flips the brief(s) `status` from `killed` back to a sensible pre-kill state (you pick: `green-lit-to-build` is the common case; `shipped` if the MVP was already live before the retire). Use when reviving a card that was retired post-ship and you want to pick up where you left off.
- **Cancel** — stop, no changes.

**Don't** offer this option block if the killed card has NO orphaned app folder — in that case, just confirm "Restore `<slug>` to active? (yes / cancel)" with `AskUserQuestion` and skip to step 4 on yes.

#### Step 3 — If reviving briefs, ask for the target status

If the user picked "Restore card AND revive MVP/V1 briefs" AND there's any ambiguity about what the pre-kill brief status should be, ask via `AskUserQuestion`:

> What status should the revived brief(s) carry?
>
> - **`green-lit-to-build`** — ready to (re-)build. Use when the build was never started or you want to restart it.
> - **`building`** — pick up where the build left off mid-flight.
> - **`shipped`** — the MVP was already in production before the retire; restore that fact so `/scope-v1` works again.

If only one option makes sense from context (e.g., MVP.md never had `shipped` status because no `build-milestone: shipped` exists in the audit log), present only the plausible options.

#### Step 4 — Execute the revive (atomic; if any step fails, undo prior steps and surface the error)

1. **Move the file:**
   ```bash
   mkdir -p ideas/<run-id>
   mv ideas/killed/<run-id>/<slug>.md ideas/<run-id>/<slug>.md
   ```

2. **Update the card's frontmatter** via Edit. Specifically:
   - Set `status: triaged`.
   - **Remove** the kill-specific fields: `killed-date`, `killed-reason`, `audit-log-id`. (The audit-log history is preserved in `user-context/audit-log.jsonl` — no need to mirror it on the card.)
   - **Preserve** every other field: `slug`, `run-id`, `date-captured`, `source`, `territory`, `validation-report` (the link to the validation report stays valid; that validation happened, the revive doesn't erase it).
   - **Do NOT add a `revived-date` or `revived-reason` field.** Audit log captures revives; card frontmatter is for current state, not history.

3. **If user picked "Restore briefs":** for each of `<stack>-apps/<slug>/MVP.md` and `V1.md` that exists with `status: killed`, Edit frontmatter to set `status: <chosen-target>`. Do NOT touch any other field on the briefs.

4. **Append the audit-log entry.** Use a single command (escape quotes carefully):
   ```bash
   python3 scripts/audit_log.py add card-revive "Revived card <slug> (run-id: <run-id>). Original kill reason: <reason, truncated to ~200 chars>. Briefs revived: <yes/no>. Linked-prior-kill: <audit-log-id-from-card-frontmatter>"
   ```
   Print the returned new entry id.

5. **Verify with lint** by running `python3 scripts/lint_pipeline.py` and showing the user the result. Expected: no new `slug.collision` errors; if `slug.orphaned-app-after-kill` is gone (because briefs were revived) or remains (because they weren't), that's correct.

#### Step 5 — Stop here

Show the user:

> Revived `<slug>` (run-id: `<run-id>`).
>
> - Card: `ideas/<run-id>/<slug>.md` (status: `triaged`)
> - Briefs: `<list of revived briefs with new status>` (or "left as-is")
> - Audit-log entry: `<new-id>`
>
> **Next steps:**
> - `/validate-card <slug>` to re-run validation against fresh signal (recommended if the kill reason mentioned competitive shifts or pricing issues — the world may have changed).
> - `/scope-mvp <slug>` to re-scope from the current card state (if the kill happened at scoping).
> - `/scope-v1 <slug>` if you revived a shipped MVP and want to plan v1.
> - `/log type card-revive` to view this revive plus any past ones.

### Important — no auto-actions, no destructive shortcuts

- **NEVER** overwrite an active card. The slug-collision check in step 3 (pre-flight) is the safety; respect it.
- **NEVER** delete the killed card's file without moving it. If the move fails partway, leave both copies on disk and surface the error so the user can recover manually.
- **NEVER** edit the validation report or scoping report linked from the card. Those are historical and the revive doesn't change what happened.
- **NEVER** chain into `/validate-card` or any other command automatically. Surface the next-step suggestions; the user picks.
- If the user picks Cancel at any step, leave the workspace untouched and report so explicitly.
