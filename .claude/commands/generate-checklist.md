---
description: Generate (or regenerate) the fine-grained CHECKLIST.md for a product. Reads MVP.md (and V1.md if green-lit) and decomposes each must-have into 3-8 bite-size deliverables with file-path hints for mtime-based auto-cross-out later. Per guides/product/checklist-methodology.md. Pairs with /read-checklist for refresh.
argument-hint: <product-slug>
---

You are about to generate `CHECKLIST.md` — the fine-grained companion to `BUILD_STATUS.md` — for one product. Follow the methodology in @guides/product/checklist-methodology.md exactly.

**Use this when:**
- Build is starting or already in progress and `CHECKLIST.md` doesn't exist yet
- You want a from-scratch regenerate (existing CHECKLIST will be backed up)

**Don't use this for:** routine refresh (use `/read-checklist <slug>` instead — that's the incremental, mtime-cached path).

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight

1. **Locate the product folder.** Check `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`. If none exists, stop: "No product folder for `<slug>`. Run `/scope-mvp <slug>` first."

2. **Locate the active brief.** Same logic as `/start-build` and `/continue-build`:
   - `MVP.md` exists and `green-lit-to-build` → use MVP.md
   - `MVP.md` `shipped` + `V1.md` `green-lit-to-build` → use V1.md (and pull carried must-haves from MVP.md)
   - Else stop with an explanatory message.

3. **Detect existing CHECKLIST.md.** If `<product-folder>/CHECKLIST.md` exists, use `AskUserQuestion`:
   > A `CHECKLIST.md` already exists at `<path>`. Generating from scratch will overwrite it. What do you want?
   - **Refresh in place** → switch to running `/read-checklist <slug>` instead (don't regenerate). Stop this command and tell the user to run it.
   - **Regenerate from scratch** → back up the existing file to `CHECKLIST.md.bak-<YYYY-MM-DD>` first, then proceed.
   - **Cancel** → stop.

### Do

1. **Read all inputs (design artifacts are REQUIRED, not optional, when the brief's `design-path` indicates one should exist):**
   - The active brief (`MVP.md` or `V1.md`) — every must-have, could-have, won't-have, success criterion. **Extract the `design-path` value** from frontmatter.
   - If V1: also read `MVP.md` for carried must-haves.
   - **Design artifact authoritative for the design-path** (mandatory if the path indicates one):
     - `design-path: claude-led` or `claude-led-continued` → **MUST read `<product-folder>/design/DESIGN_SPEC.md`**. If it doesn't exist or its `status` is not `acted-on`, stop and tell the user: "Brief is `design-path: <value>` but `DESIGN_SPEC.md` is missing or not signed off. Run `/research-design <slug>` then `/draft-design-spec <slug>` first — the checklist depends on the spec to surface frontend / icon / CSS / image-asset deliverables. Without it, the checklist will be backend-heavy and miss the UI work."
     - `design-path: hired` or `pro-designer-engaged` → **MUST read `<product-folder>/design/handoff/tokens.json` + `screenshots/` listing** if the handoff exists. If not, surface to the user: "Brief is `design-path: hired` but the designer handoff hasn't been captured yet. Continue with backend-only decomposition for now, and re-run `/generate-checklist <slug>` (or `/read-checklist <slug>`) after the handoff lands to surface UI deliverables."
     - `design-path: hybrid-light-refresh` → read `<product-folder>/design/DESIGN_RESEARCH.md` if it exists with `status: acted-on`. Less detail than a full spec, but still informs UI decomposition.
     - No design path set / unknown path → tell the user and ask if they want to proceed with brief-only decomposition (the checklist will be backend-heavy).
   - `BUILD_STATUS.md` if it exists (to cross-reference subsystems)
   - `CLAUDE.md` for workspace conventions
   - `guides/product/checklist-methodology.md` for the §2 format and §3 decomposition rules

2. **Decompose each must-have into 3-8 deliverables** per §3 of the methodology guide. **The decomposition MUST surface frontend / UI / design deliverables when the design artifact is present** — don't bias toward backend just because routes and handlers are easier to name. For each must-have:
   - Walk the must-have against `DESIGN_SPEC.md §6 Per-surface specs` (or the design-research surfaces): if a surface touches this must-have, surface its deliverables (template / component / styling / per-surface state coverage).
   - Walk the must-have against `DESIGN_SPEC.md §2 Tokens`, `§3 Icon system`, `§4 Image assets`, `§7 Component patterns`, `§5 Responsive specs`: surface deliverables for token wiring, icon library install + usage, image-asset prompt generation + env-var slots, component pattern implementation, responsive breakpoint integration.
   - For each top-level must-have, after surfacing the backend deliverables (routes / handlers / migrations / tests), surface the **matching frontend deliverables**: templates, JS interactions, CSS tokens consumption, responsive states, a11y notes per surface, icon usage, image slots.
   - Each deliverable:
     - One-line noun phrase
     - File-path hint in italics (`*\`app/routes/X.py:handler_name\`*` or `*\`app/templates/Y.html\`*` or `*\`app/static/css/components.css\`*` or `*\`design/DESIGN_SPEC.md#hero-image\`*` for spec-anchored items)
     - Group by user-visible feature, not technical layer (e.g., "Signup form" includes template + handler + styling + tests; not separate "Templates / Routes / Styling / Tests" sections)
     - Sub-bullets only for genuinely nested deliverables (e.g., test cases under "Tests"; per-breakpoint behavior under "Responsive")

3. **Also surface a dedicated `## Design-spec deliverables` section** when `DESIGN_SPEC.md` was read. This section captures the spec-wide deliverables that aren't tied to a single must-have:
   - Icon library install + wrapper component (per §3 of the spec)
   - Token wiring (`static/css/tokens.css` from §2.1-2.5 of the spec; per stack equivalent for RN / PySide6)
   - Image-asset prompts to run + env-var slots (per §4 of the spec) — one deliverable per image slot, with the env-var name in italics so the user can find it during build
   - Responsive baseline (breakpoints into base CSS / RN theme; per §5 of the spec)
   - Component patterns implementation (button / form / table / modal / etc., per §7 of the spec)
   - A11y floor pass (focus states, keyboard nav, contrast verification, per §8 of the spec)

4. **Initial auto-cross-out pass:** for any deliverable whose file-path hint points at an existing file, mark it `[x]` immediately. Use this rule: file exists AND has content > 0 bytes AND (if it's a Python file) the named function/handler exists AND (if it's a template) it's referenced from a route. For ambiguous cases, leave as `[ ]` — the user will know whether to flip it.

5. **Write `<product-folder>/CHECKLIST.md`** using the §2 template exactly. Populate frontmatter with current timestamp, set `last-scanned-mtime` to the current epoch (so the first `/read-checklist` will only need to scan files modified after this point). **Add a `design-artifact-source:` frontmatter field** capturing which design artifact was used (`design/DESIGN_SPEC.md` / `design/handoff/` / `design/DESIGN_RESEARCH.md` / `none`) — `/read-checklist` uses this to know which artifact to re-scan during refreshes.

6. **Initialize the Scope changes log** with one row: today's date, "Initial generation from `<brief>` + `<design-artifact-source>`", "Generated by /generate-checklist".

### Stop here — user checkpoint

After writing the file, **stop**. Show the user:

> Checklist at `<product-folder>/CHECKLIST.md`.
>
> - **Design artifact source:** `<DESIGN_SPEC.md | handoff | DESIGN_RESEARCH.md | none>`
> - **Must-haves decomposed:** <count> from MVP, <count> from V1 (if applicable)
> - **Design-spec deliverables surfaced:** <count> (tokens / icons / image prompts / responsive / components / a11y)
> - **Total deliverables:** <total count>
> - **Auto-marked done (file exists + content):** <count>
> - **Could-haves tracked:** <count>
>
> **Sample of decomposed must-haves:**
> 1. **<Must-have 1 title>** — <count> deliverables (backend: X, frontend: Y, tests: Z)
> 2. **<Must-have 2 title>** — <count> deliverables (backend: X, frontend: Y, tests: Z)
> 3. **<Must-have 3 title>** — <count> deliverables (backend: X, frontend: Y, tests: Z)
>
> Open the file to inspect the full list. To refresh statuses later: `/read-checklist <slug>`.
> The orchestrator will also auto-refresh after every `BUILD_STATUS.md` subsystem completes.

### Notes

- **No audit-log entry.** Generation is a setup event, not a milestone.
- **Regeneration nuances:** if the user picks "Regenerate from scratch", any user-added items in the prior CHECKLIST are lost. The backup file (`CHECKLIST.md.bak-<date>`) preserves them; the user can manually re-merge.
- **For mobile/desktop builds**, the decomposition lens shifts: instead of templates+routes+models, it's screens+actions+state. Adjust file-path hints accordingly.
- **If the brief has NO must-haves** (rare — a brief that's all could-haves), stop and tell the user: "MVP.md has no must-haves. CHECKLIST is empty by definition. Verify the brief is correct."
