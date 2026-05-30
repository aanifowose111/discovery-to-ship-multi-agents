---
description: Run design research for a product by invoking the ui-ux-researcher, producing a design-direction report (reference landscape, ≥3 visual directions, ≥3 color/type pairings, brand positioning, portfolio-continuity question), per guides/ui-ux/design-research-methodology.md.
argument-hint: <product-slug>
---

You are about to run design research for one product. Follow the methodology in @guides/ui-ux/design-research-methodology.md exactly. The work is delegated to the `ui-ux-researcher` subagent (see @.claude/agents/ui-ux-researcher.md for its instructions).

**Arguments:** $ARGUMENTS — the product slug. The MVP brief must exist at either `web-apps/<slug>/MVP.md` or `mobile-apps/<slug>/MVP.md`.

### Pre-flight checks (do these before invoking the researcher)

1. **Verify the brief exists.** Check `web-apps/<slug>/MVP.md` and `mobile-apps/<slug>/MVP.md`. If neither exists, stop and tell the user: "No MVP brief at `web-apps/<slug>/MVP.md` or `mobile-apps/<slug>/MVP.md`. Run `/scope-mvp <slug>` first."
2. **Note the brief's status.** Read the frontmatter. If `status` is *not* `green-lit-to-build`, surface that to the user before proceeding:
   > Brief status is `<current-status>`, not `green-lit-to-build`. Design research is normally run *after* the MVP has been validated with first users — running it on a not-yet-validated brief is fine for early exploration but you may end up redoing it. Continue?

   Wait for the user's confirmation if status is not `green-lit-to-build`.
3. **Detect prior research.** If `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md` already exists, tell the user: "Prior research found at `<path>`. The researcher will treat this as a re-research, not from-zero — refreshing the reference landscape and revising directions where shifts warrant. Continue?" Wait for confirmation.

### Do

1. Confirm which domain the brief is in (`web-apps` or `mobile-apps`).
2. **Invoke the `ui-ux-researcher` subagent** with the slug as input, **using the custom-subagent invocation pattern in `CLAUDE.md`** — `subagent_type: "general-purpose"`, instruct the agent to read and follow `.claude/agents/ui-ux-researcher.md`. Pass enough context in the prompt that it can proceed without re-asking the user — it should already have everything it needs from the brief, the validation report, the idea card, and `CLAUDE.md`.
3. Wait for the researcher to write the report and return its summary.
4. Read the produced file at `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md` to confirm it exists and has the expected sections.

### Stop here — user checkpoint

After the researcher returns, **stop**. Do not draft the design brief, do not change the brief's `status`, and do not contact any designer. Show the user:

> Design research at `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md`.
>
> Three visual-direction options:
> 1. **<Option A name>** — <one-line mood description>
> 2. **<Option B name>** — <one-line mood description>
> 3. **<Option C name>** — <one-line mood description>
>
> Portfolio-continuity question: <one sentence — "does this product visually echo findvil/fijara or stand independent?" with a note on what would carry across vs. what would make it independent>
>
> Open questions for you to resolve before the brief goes out:
> - <question 1>
> - <question 2>
> - ...
>
> Your call:
> - Sign off → status of the research advances to `acted-on`; next step is `/draft-design-brief <slug>`
> - Request a re-research with specific feedback (which direction is off, which references are missing, etc.) → I run the researcher again with your notes
> - Pause — you want to think about it before next step

Only after the user signs off, update the research file's `status` field from `draft` to `acted-on`.

### Notes for the main Claude

- The researcher's report is **input to** the design brief, not the brief itself. Do not skip directly to drafting the brief — the user signs off on the research first, because the brief consolidates the research and that consolidation needs the user's directional input.
- If the user wants to provide direction *before* invoking the researcher (e.g., "I want this to feel like \<reference URL\>"), capture that in the prompt to the researcher so the researcher's first option is anchored on the user's reference, with two genuinely distinct alternatives alongside it.
