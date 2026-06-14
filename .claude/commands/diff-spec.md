---
description: Diff a product's built UI against its `DESIGN_SPEC.md` — catches drift (tokens missing from CSS, surfaces named in spec but not rendered, type ramps off-spec, etc.). REPORTS divergence neutrally; does NOT penalize improvements over the spec. User decides per finding whether it's an intentional improvement, an unintended drift, or a fix to make. Per the claude-led design path.
argument-hint: <product-slug>
---

You are about to diff the built UI of one product against its design spec. The goal is to surface divergence, not to enforce strict spec compliance. **Improvements are surfaced neutrally — never flagged as bad.**

**Use this when:**
- The build has been progressing for a while and you want to confirm UI work hasn't silently drifted from `DESIGN_SPEC.md`
- You added padding / spacing / a component variant the spec didn't include and want to confirm Claude noticed
- Before `/ship-app`, as a final design-coverage check
- After a refactor of the frontend, to verify the design-system layer didn't lose anything

**Don't use this for:**
- Hired-designer-path products — that path uses Figma + handoff folder, not DESIGN_SPEC.md. (If hired-light-refresh path with DESIGN_RESEARCH.md, this command falls back to research-vs-built; surface that.)
- Initial design-spec drafting — that's `/draft-design-spec`.

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight

1. **Locate the product folder** under `web-apps/`, `mobile-apps/`, `desktop-apps/`. Stop if not found.

2. **Locate the spec** at `<product-folder>/design/DESIGN_SPEC.md`. If missing:
   - **If `<product-folder>/design/DESIGN_RESEARCH.md` exists** (hybrid-light-refresh path), surface to user: "No `DESIGN_SPEC.md`; diff will compare against `DESIGN_RESEARCH.md` instead (lighter signal). Continue?"
   - **If neither exists**, stop: "No design artifact found. This command is for products with `/draft-design-spec` output or research."

3. **Locate the built UI surface**:
   - Flask web: `app/static/css/tokens.css`, `app/static/css/components.css`, `app/templates/`
   - RN mobile: `src/theme/tokens.ts`, `src/components/`, `src/screens/`
   - Desktop: stylesheets + widget definitions

4. **Parse `DESIGN_SPEC.md`** key sections per `guides/ui-ux/design-spec-methodology.md §3`:
   - §1 locked direction
   - §2 tokens (color, type, spacing, radius, shadow, motion)
   - §3 icon library + install
   - §4 image-asset prompts + env-var slots
   - §5 responsive specs
   - §6 per-surface specs (one block per surface)
   - §7 component patterns
   - §8 a11y floor
   - §11 version log

### Do — the diff

For each spec section, compare against the built artifacts. Categorize findings into 4 buckets — **never single-categorize as "violation":**

#### 🟢 In-spec — matches

The build implements the spec correctly. List counts only (e.g., "12 of 14 color tokens present in tokens.css"). Don't enumerate every match; that's noise.

#### 🟡 Improvement-over-spec (NEUTRAL — not a problem)

The build includes something the spec did not specify. **This is not a violation.** Examples:
- A new spacing scale value (`--space-7: 56px`) added in tokens.css that the spec's §2 didn't list.
- A new component variant (Button -- ghost) implemented in components.css that the spec's §7 didn't cover.
- A new responsive breakpoint added.
- A new utility class.

For each, surface as: "**Improvement:** `<description>`. **Spec coverage:** the spec did not cover this; it's an addition the build introduced. **Next:** (a) keep + update spec, (b) keep + leave spec as-is, (c) revert to spec-only, (d) discuss."

#### 🟡 Drift — built differs from spec

The build implements something the spec specified, but differently. Examples:
- Spec says `--space-4: 16px`; tokens.css says `--space-4: 18px`.
- Spec says button border-radius `4px`; components.css says `6px`.
- Spec's per-surface §6.3 names a 3-column dashboard layout; the dashboard template uses 2 columns.

For each, surface as: "**Drift:** `<description>`. **Spec says:** `<spec value>`. **Built:** `<actual value>`. **Next:** (a) update spec, (b) update build to match spec, (c) discuss, (d) keep both (note the difference is intentional)."

#### 🔴 Missing — spec specifies it, build doesn't have it

The build omits something the spec specified. Examples:
- Spec lists 14 color tokens; tokens.css has 12.
- Spec's §6.5 names a "Settings" surface; no template exists.
- Spec's §7.2 specifies a "Form input — error state"; only the base variant is implemented.

For each, surface as: "**Missing:** `<description>`. **Spec section:** `<§ref>`. **Built status:** not found in code. **Next:** (a) implement to match spec, (b) drop from spec (intentional descope), (c) discuss."

### Stop here — user checkpoint, per finding

After the diff completes, show the user a summary:

> ✅ Diff complete: `<product-folder>/design/DESIGN_SPEC.md` vs. built UI.
>
> **Counts:**
> - 🟢 In-spec matches: `<N>`
> - 🟡 Improvements-over-spec: `<N>`
> - 🟡 Drift: `<N>`
> - 🔴 Missing from build: `<N>`
>
> **🟡 Improvements** (your additions beyond the spec):
> 1. `<description>` (proposed action: (a) update spec to include, (b) leave both as-is, (c) revert to spec-only, (d) discuss)
> 2. ...
>
> **🟡 Drift** (built differs from spec):
> 1. `<description>` — spec: `<value>` / built: `<value>` — proposed action: (a) update spec, (b) update build, (c) keep both, (d) discuss
> 2. ...
>
> **🔴 Missing from build** (spec specifies, code doesn't):
> 1. `<description>` (§ref) — proposed action: (a) implement, (b) drop from spec, (c) discuss
> 2. ...

Then for **each finding** (improvements, drift, missing) use `AskUserQuestion` with the proposed actions for that finding category. The user picks per finding. Apply the decisions:

- For "update spec" / "drop from spec": Claude edits `DESIGN_SPEC.md` directly (record the change in §11 version log: `<today>: updated/dropped <description> based on /diff-spec`). NOT for hired-designer-path products.
- For "implement to match spec" / "update build to match spec" / "revert to spec-only": Claude flips the relevant `BUILD_STATUS.md` subsystem back to `[>]` and notes the diff finding as the rework reason. Specialist persona invocation follows.
- For "keep both" / "leave as-is": no file change; record the decision in `DESIGN_SPEC.md` §11 version log so future runs of `/diff-spec` know not to re-surface this.
- For "discuss": surface to the user as a per-item question and wait.

After all decisions, summarize:

> Applied: `<N>` updates to DESIGN_SPEC.md, `<N>` BUILD_STATUS.md reopens, `<N>` "keep both" decisions logged.

### Notes

- **Improvements are NEVER framed as violations.** The whole design intent is that DESIGN_SPEC.md is a starting contract, not a prison. The build can grow past the spec — `/diff-spec` is for surfacing the deltas so the user can decide what to retain.
- **Hired-designer-path products** are out of scope — that path is governed by Figma + handoff folder, and the build's authority comes from the handoff contract (per `CLAUDE.md` §Phase 4). `/diff-spec` is a claude-led tool.
- **Hybrid-light-refresh path** (`/research-design --light`) has no DESIGN_SPEC.md but has DESIGN_RESEARCH.md. The command can fall back to comparing against the research's visual-direction picks, but findings are necessarily fuzzier — surface this caveat to the user.
- **No audit-log entry by default.** This is an inspection command. If updates result, the underlying `BUILD_STATUS.md` flips and `DESIGN_SPEC.md` edits each log per their own conventions.
- **Token-comparison is the highest-leverage check.** Spec §2 → tokens.css is a 1:1 contract; any diff here is the most actionable signal. Run it first; rest follows.
