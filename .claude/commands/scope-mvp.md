---
description: Draft an MVP brief for a green-lit card, invoke the scope and code reviewers, and integrate verdicts, per guides/product/mvp-scoping-methodology.md.
argument-hint: <card-slug>
---

You are about to scope an MVP for a green-lit card. Follow the methodology in @guides/product/mvp-scoping-methodology.md exactly.

**Arguments:** $ARGUMENTS — the card slug. The card must exist at `ideas/<slug>.md` with `status: green-lit`.

### Inputs to read before drafting
- The card: `ideas/<slug>.md`
- The validation report: `market-research/validation-<slug>-*.md` (use the most recent)
- @guides/product/mvp-scoping-methodology.md (for the brief format and reviewer pair)
- @CLAUDE.md (for stack defaults and working style)
- The most recent `market-research/trends-*.md` (if any) — check for encroachment findings that affect this card

### Do
1. Verify the card is `green-lit`. If not, stop and surface the gap to the user.
2. Decide `domain: web | mobile | hybrid` based on the card.
3. **Confirm the stack choice with the user** before drafting. Read §6.0 of `guides/product/mvp-scoping-methodology.md`. If the user has not already stated a stack choice in their prompt to `/scope-mvp`, ask explicitly:

   > Before I draft the brief, what stack do you want to use for this product?
   >
   > Workspace defaults (this is what the build-domain guides cover):
   > - **Web:** dockerized Flask + Jinja + vanilla JS (Python)
   > - **Mobile:** React Native + Expo + TypeScript
   >
   > Alternatives you could pick (no workspace guide for these — Claude will work from first principles + the agent-skills stack-agnostic skills):
   > - **Web:** Next.js, Django, Rails, Phoenix, FastAPI, Go (Gin/Echo), Java (Spring), Angular, Vue, SvelteKit, …
   > - **Mobile:** Swift native, Kotlin native, Flutter, …
   >
   > Reply with your picks (one for web, one for mobile if hybrid). The brief's *Stack* section will record them, and the product-scope-reviewer will assess fit against your shipped experience — not against the workspace defaults.

   Wait for the user's reply before proceeding.

4. Draft the MVP brief at the right location:
   - `web-apps/<slug>/MVP.md` for web
   - `mobile-apps/<slug>/MVP.md` for mobile
   - Both for hybrid; the canonical brief is the web one with the mobile-side noted
4. Fill the brief per the §5 template in the scoping guide. Set `status: in-scoping`. Identify the riskiest assumption, must-haves (each traced to the assumption), could-haves, won't-haves, stack, infrastructure decisions (`.env`, DO Spaces, hosting, auth), success criterion (first-10-users measurable), effort estimate, stack stretches.
5. Invoke the reviewer pair in parallel, **using the custom-subagent invocation pattern in `CLAUDE.md`** — each call uses `subagent_type: "general-purpose"` and instructs the agent to read and follow the relevant persona file:
   - For scope discipline: read and follow `.claude/agents/product-scope-reviewer.md`
   - For architecture / security / performance: read and follow `.claude/agents/code-reviewer.md` (this is the agent-skills `code-reviewer` persona, symlinked into `.claude/agents/` per `.claude/agents/README.md`)
   - For mobile or hybrid briefs, also invoke `mobile-ux-reviewer` *if and only if it exists in `.claude/agents/`* (we have not built it yet — skip otherwise and note the skip in the report)

   Each agent should be told to read the brief at `<web-apps|mobile-apps>/<slug>/MVP.md`, the validation report, the scoping methodology guide, and `CLAUDE.md` — and to return its output in the locked verdict format.
6. Integrate per §8 of the scoping guide.
7. Write the scoping report to `market-research/scoping-<slug>-<YYYY-MM-DD>.md` per §9.


### Stop here — user checkpoint
After writing the report, **stop**. Do not advance the brief to `green-lit-to-build`. Show the user:

> MVP brief at `<web-apps|mobile-apps>/<slug>/MVP.md`.
> Scoping report at `market-research/scoping-<slug>-<YYYY-MM-DD>.md`.
>
> Combined verdict: <APPROVE / APPROVE-WITH-NOTES / REJECT>
> Notes carried forward: <summary>
>
> Your call:
> - Advance to `green-lit-to-build` → next step is to start the build per the agent-skills `/build` workflow
> - Revise the brief and re-review
> - Kill or send back to validation

Update the brief's `status` and the report's *Decision* section only after the user has decided.
