---
description: Run design research for a product by invoking the ui-ux-researcher. Produces a comprehensive design research report covering per-surface coverage (public / auth / user / admin / employee dashboards), product-space + platform trends, ≥3 visual directions, ≥3 color/type pairings, pattern conventions, responsive strategy, brand positioning, and portfolio-continuity. Fires for BOTH design paths (claude-led and hired). Per guides/ui-ux/design-research-methodology.md.
argument-hint: <product-slug>
---

You are about to run design research for one product. Follow the methodology in @guides/ui-ux/design-research-methodology.md exactly. The work is delegated to the `ui-ux-researcher` subagent (see @.claude/agents/ui-ux-researcher.md for its instructions).

**This command fires for BOTH design paths** — `claude-led` and `hired`. The research is the same; only the next-step artifact differs (`DESIGN_SPEC.md` for claude-led, `DESIGN_BRIEF.md` for hired). For the v1 `hybrid-light-refresh` path, the researcher takes a lighter pass — see the `--light` flag below.

**Arguments:** $ARGUMENTS — the product slug (and optionally `--light` for the v1 hybrid-light-refresh path). An MVP brief OR V1 brief must exist at `web-apps/<slug>/`, `mobile-apps/<slug>/`, or `desktop-apps/<slug>/`.

### Pre-flight checks (do these before invoking the researcher)

1. **Verify the brief exists.** Check `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, `desktop-apps/<slug>/MVP.md` (and `V1.md` variants). If none exists, stop and tell the user: "No MVP or V1 brief found at `<web-apps|mobile-apps|desktop-apps>/<slug>/`. Run `/scope-mvp <slug>` first."
2. **Note the brief's status.** Read the frontmatter. If `status` is *not* `green-lit-to-build`, surface that to the user before proceeding:
   > Brief status is `<current-status>`, not `green-lit-to-build`. Design research is normally run *after* the brief has been finalized — running it on a not-yet-final brief is fine for early exploration but you may end up redoing it. Continue?

   Wait for the user's confirmation if status is not `green-lit-to-build`.
3. **Read the `design-path` from the brief's frontmatter** — `claude-led`, `hired`, `claude-led-continued`, `pro-designer-engaged`, or `hybrid-light-refresh`. This determines the next-step suggestion you'll surface at the checkpoint. If `design-path` is missing, surface to the user: "No `design-path` set in `<brief path>` frontmatter. The research itself doesn't need it, but the next-step suggestion does. Want to set it now (claude-led / hired / claude-led-continued / pro-designer-engaged / hybrid-light-refresh)?" Default to claude-led if user is unsure.
4. **Detect prior research.** If `<product-folder>/design/DESIGN_RESEARCH.md` already exists, tell the user: "Prior research found at `<path>`. The researcher will treat this as a re-research, not from-zero — refreshing the reference landscape and revising directions where shifts warrant. Continue?" Wait for confirmation.

### Do

1. Confirm which domain the brief is in (`web-apps`, `mobile-apps`, or `desktop-apps`).
2. **Invoke the `ui-ux-researcher` subagent** with the slug as input, **using the custom-subagent invocation pattern in `CLAUDE.md`** — `subagent_type: "general-purpose"`, instruct the agent to read and follow `.claude/agents/ui-ux-researcher.md`. Pass enough context in the prompt that it can proceed without re-asking the user — it should already have everything it needs from the brief, the validation report, the idea card, and `CLAUDE.md`. **Pass the `design-path` value** so the researcher tailors §9 open questions accordingly (claude-led → all questions are For-user; hired → split into For-designer / For-user).
3. **If the researcher pauses to ask an interactive reference-URL checkpoint question** (per methodology §4.2.3), relay it verbatim to the user, capture their answer, and pass it back to the researcher.
4. Wait for the researcher to write the report and return its summary.
5. Read the produced file at `<product-folder>/design/DESIGN_RESEARCH.md` to confirm it exists and has the expected sections (surfaces, trends, reference landscape, visual direction options, color/type, pattern conventions, per-surface direction notes, responsive strategy, brand positioning, portfolio-continuity, open questions, sources).

### Stop here — user checkpoint

After the researcher returns, **stop**. Do not draft the next-step artifact, do not change the brief's `status`, and do not contact any designer. Show the user:

> Design research at `<product-folder>/design/DESIGN_RESEARCH.md`.
>
> Surfaces covered: <comma-separated list from §Surfaces, e.g., public landing, auth, user dashboard, admin>.
>
> Three visual-direction options:
> 1. **<Option A name>** — <one-line mood description>
> 2. **<Option B name>** — <one-line mood description>
> 3. **<Option C name>** — <one-line mood description>
>
> Portfolio-continuity question: <one sentence — "does this product visually echo findvil/fijara or stand independent?" with a note on what would carry across vs. what would make it independent>
>
> Open questions for you to resolve before next step:
> - <question 1>
> - <question 2>
> - ...
>
> Your call:
> - **Sign off** → research advances to `acted-on`; next step branches on `design-path`:
>   - `claude-led` / `claude-led-continued` → `/draft-design-spec <slug>` (implementation-ready spec)
>   - `hired` / `pro-designer-engaged` → `/draft-design-brief <slug>` (Figma-handoff brief)
>   - `hybrid-light-refresh` → directly to `/start-build <slug>` (research is the design artifact for this path)
> - **Request a re-research** with specific feedback (which direction is off, which references are missing, etc.) → I run the researcher again with your notes
> - **Pause** — you want to think about it before next step

Only after the user signs off, update the research file's `status` field from `draft` to `acted-on`.

### Notes for the main Claude

- The researcher's report is **input to** the design brief, not the brief itself. Do not skip directly to drafting the brief — the user signs off on the research first, because the brief consolidates the research and that consolidation needs the user's directional input.
- If the user wants to provide direction *before* invoking the researcher (e.g., "I want this to feel like \<reference URL\>"), capture that in the prompt to the researcher so the researcher's first option is anchored on the user's reference, with two genuinely distinct alternatives alongside it.
