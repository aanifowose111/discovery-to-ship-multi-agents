---
description: Refresh CHECKLIST.md for a product — runs an mtime-cached scan to cross out completed items, proposes additions for newly discovered work, and updates the Scope changes log. Idempotent and cheap (only scans files modified since the last run). Pairs with /generate-checklist for first-time creation. Per guides/product/checklist-methodology.md.
argument-hint: <product-slug>
---

You are about to refresh `CHECKLIST.md` for one product. This is the routine refresh command — fast, mtime-cached, incremental. For first-time generation, use `/generate-checklist <slug>` instead.

**Use this when:**
- Coming back to a build after a break — confirm what's now `[x]`
- After significant code has been written and you want to flip done items
- When you suspect scope has drifted (new files appeared, old items no longer relevant)

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight

1. **Locate the product folder + CHECKLIST.md.** Check `<web-apps|mobile-apps|desktop-apps>/<slug>/CHECKLIST.md`. If the file doesn't exist, stop and tell the user: "No `CHECKLIST.md` at `<expected-path>`. Run `/generate-checklist <slug>` first."

2. **Read frontmatter** for `last-scanned-at`, `last-scanned-mtime`, and `design-artifact-source`. Capture `since-ts` (epoch seconds) and `design-artifact-path`.

3. **Re-read the design artifact** named in `design-artifact-source` (if any). Specifically:
   - If `design-artifact-source: design/DESIGN_SPEC.md` → re-read the spec. Compare its mtime to `last-scanned-mtime`: if the spec was modified after the last refresh, this run MUST surface design-driven additions.
   - If `design-artifact-source: design/handoff/` → re-walk `tokens.json` and the `screenshots/` listing.
   - If `design-artifact-source: design/DESIGN_RESEARCH.md` (hybrid path) → re-read the research's per-surface direction notes.
   - If `design-artifact-source: none` → check whether a design artifact has landed since generation (per the brief's `design-path`). If yes, surface to the user: "The brief is `design-path: <value>` and `<artifact>` now exists. Re-run `/generate-checklist <slug>` (regenerate from scratch is safer than refresh in this case — the original CHECKLIST was generated without the design artifact and likely under-covers UI work)." Then stop. Don't refresh.

### Do

1. **mtime scan.** List files in the product folder modified after `<since-ts>`. Exclude `.git/`, `__pycache__/`, `node_modules/`, `.pytest_cache/`, `.venv/`, `CHECKLIST.md` itself (we wrote it, that doesn't count), `CHECKLIST.md.bak-*`. Use:
   ```bash
   find <product-folder> -type f -newer /tmp/since-ts-anchor \
     -not -path '*/.git/*' -not -path '*/__pycache__/*' \
     -not -path '*/node_modules/*' -not -path '*/.pytest_cache/*' \
     -not -path '*/.venv/*' -not -name 'CHECKLIST.md' \
     -not -name 'CHECKLIST.md.bak-*' \
     | head -200
   ```
   (Create `/tmp/since-ts-anchor` with `touch -t <YYYYMMDDHHMM.SS based on since-ts>` if needed, or use Python `Path.stat().st_mtime` comparison.)

2. **Auto-cross-out pass.** Read CHECKLIST.md. For each pending (`[ ]`) deliverable:
   - **If it has a file-path hint** (italicized after the deliverable, e.g., `*\`app/routes/auth.py:login_handler\`*`): check whether the hinted file exists AND is in the recent-files list. If yes, verify content (file non-empty; if the hint names a Python function/handler, confirm it exists; if a template, confirm it's referenced from a route or imported). On confirmation, flip `[ ]` → `[x]`.
   - **If no file-path hint:** match by keyword. For "Tests for <X>", run `find tests/ -name "test_*<x-keyword>*"` and check matches were recently modified. For "<X> template", same against `templates/`. Etc. Only cross out on a confident match — when uncertain, leave as `[ ]` and surface in the report ("Couldn't auto-verify '<item>' — please check manually").

3. **Scope discovery (auto-propose, don't auto-add):**
   - **BUILD_STATUS subsystem gap:** read `BUILD_STATUS.md`. Any subsystem section that has no corresponding `### <Must-have>` block in CHECKLIST is a candidate. Propose adding it.
   - **Design artifact gap (THE PRIORITY scope-discovery source when a design artifact exists):** walk `DESIGN_SPEC.md` (or the handoff / research) and surface CHECKLIST gaps:
     - **Tokens (§2 of spec)** — is `static/css/tokens.css` (or RN theme / QSS) covered? If a CHECKLIST item doesn't reference it AND the file doesn't exist yet, propose: "Token wiring — `tokens.css` populated from `DESIGN_SPEC.md §2.1-2.5`."
     - **Icon system (§3 of spec)** — is the chosen library installed + wrapper component present? Propose if missing.
     - **Image assets (§4 of spec)** — for each image slot with an `IMG_<NAME>_URL` env-var, propose: "Image asset for `<slot>` — run prompt at `DESIGN_SPEC.md §4`, upload, set `<env-var>` in `.env`."
     - **Per-surface specs (§6 of spec)** — for each surface (public landing, auth, user dashboard, admin, employee, etc.), check if CHECKLIST has frontend deliverables (template, styling, responsive states) covering it. Propose surface-level gaps.
     - **Component patterns (§7 of spec)** — button / form / table / modal / toast / empty / loading / error / nav. For each pattern, check CHECKLIST coverage; propose missing ones.
     - **A11y floor (§8 of spec)** — focus states, keyboard nav, contrast verification. Propose if not present.
     - **Responsive (§5 of spec)** — breakpoints integration. Propose if not present.
   - **Source-tree growth:** new top-level directories in the product folder (e.g., `app/integrations/` newly created) without checklist coverage. Propose adding "Integrations layer" with its known sub-files.
   - **/rework audit-log:** read `python3 scripts/audit_log.py list --type rework-applied | grep -i "<slug>"`. For any rework entry after `last-scanned-at`, propose decomposing its added must-haves into CHECKLIST items.
   - **Cap at 5 proposed additions** total per scan; the rest can wait until next scan. **Prioritize design-artifact gaps** over source-tree gaps when triaging — UI / design coverage is more often under-surfaced than backend coverage.

4. **For each proposed addition**, surface to the user via `AskUserQuestion` (one at a time): "Found a candidate addition: '<item>' under '<must-have or new section>'. Reason: <one-line>. Add to CHECKLIST?" Options: **Add** / **Skip** / **Add + edit text first** / **Stop scope-discovery (skip remaining)**.

5. **Apply the changes:**
   - Cross-outs from step 2 land directly
   - Approved additions from step 4 land under the right section
   - Append one row to the Scope changes log per change
   - Update frontmatter: `last-scanned-at: <now>`, `last-scanned-mtime: <current-epoch>`

6. **Detect completion:** if every MVP-scope deliverable is `[x]` and there are no remaining `[ ]` MVP items, update frontmatter `status: complete` and note in the Scope changes log.

### Stop here — user checkpoint

After applying, **stop**. Show the user:

> Checklist refreshed at `<path>`.
>
> **This pass:**
> - Crossed out: <count> deliverables
> - Proposed additions (approved): <count>
> - Proposed additions (skipped): <count>
> - Items needing manual verification: <count>
>
> **State:**
> - Must-haves complete: <X> / <Y>
> - Could-haves: <Z> tracked, <unchanged>
> - Status: `<in-progress | complete>`
>
> **Pending items needing your attention** (top 5):
> 1. <pending item 1> — *<why it's still pending: missing file, missing function, etc.>*
> 2. ...
>
> Next: open `<path>` for the full picture, or `/continue-build <slug>` to resume work on a pending item.

### Notes

- **Cheap by design.** The mtime gate means after the first refresh, only files touched since then are scanned. For a 10-minute build session with 5 file writes, this command scans 5 files — not the whole tree.
- **Doesn't auto-create CHECKLIST.** If the file doesn't exist, this command exits with a suggestion to run `/generate-checklist <slug>`. We do NOT silently create it because the decomposition logic in `/generate-checklist` is different (reads brief, decomposes each must-have; this command only refreshes).
- **No audit-log entry.** Refresh is a maintenance event, not a milestone.
- **Auto-trigger by orchestrator:** the `senior-software-engineer` orchestrator runs an inline equivalent of this refresh after every `BUILD_STATUS.md` subsystem flips to `[x]`. The Scope changes log notes those refreshes with "Triggered by orchestrator after `<subsystem>` flip".
- **Edge case — file moves:** if the user moves `app/routes/auth.py` to `app/auth/routes.py`, the file-path hints in CHECKLIST become stale. The mtime scan picks up the new file but won't match the old hint. Report this case as "Couldn't auto-verify" — the user can update the hint manually or rerun `/generate-checklist` if many files moved.
