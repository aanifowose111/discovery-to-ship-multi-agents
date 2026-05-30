---
description: Run validation on a green-bucket idea card by invoking the three product reviewers in parallel and integrating their verdicts, per guides/product/idea-validation-methodology.md.
argument-hint: <card-slug>
---

You are about to validate one idea card. Follow the methodology in @guides/product/idea-validation-methodology.md exactly.

**Arguments:** $ARGUMENTS — the card slug. The card must exist at `ideas/<slug>.md` and be in the `green` triage bucket (i.e., `status: draft` or `triaged`, not `killed`).

### Inputs to read before invoking reviewers
- The idea card: `ideas/<slug>.md`
- @guides/product/idea-discovery-methodology.md (for shared vocabulary)
- @guides/product/idea-validation-methodology.md (for the verdict format and integration rules)
- The most recent `market-research/trends-*.md` (if any) — may affect reviewer findings

### Do
1. Verify the card exists and is in the green bucket. If not, stop and ask the user how to proceed (override / pick a different card).
2. Update the card's `status` field from `triaged` to `in-validation`.
3. Invoke the **three reviewers in parallel**, in a single message with three Agent tool calls. **Use the custom-subagent invocation pattern in `CLAUDE.md`** (the "Invoking custom subagents — the universal pattern" section) — each call uses `subagent_type: "general-purpose"` and instructs the agent to read and follow the persona file:
   - For viability: read and follow `.claude/agents/product-viability-reviewer.md`
   - For competition: read and follow `.claude/agents/product-competition-reviewer.md`
   - For market-segment: read and follow `.claude/agents/market-segment-reviewer.md`

   Each agent should also be told to read the card at `ideas/<slug>.md`, the discovery and validation methodology guides, and `CLAUDE.md` for founder context — and to return its output in the locked verdict format from `idea-validation-methodology.md` §5.
4. Wait for all three verdicts.
5. Integrate per §6 of the validation guide. If verdicts conflict on the same evidence, surface the conflict explicitly; do not silently average.
6. Write the validation report to `market-research/validation-<slug>-<YYYY-MM-DD>.md` per §7 of the guide. Fill all sections except *Decision* (that section is the user's).

### Stop here — user checkpoint
After writing the report, **stop**. Do not advance the card to `green-lit` or `killed`. Show the user:

> Validation report at `market-research/validation-<slug>-<YYYY-MM-DD>.md`.
>
> Combined verdict: <APPROVE / APPROVE-WITH-NOTES / REJECT>
> Conflicts (if any): <summary>
>
> Your call:
> - Advance to `green-lit` → next step is `/scope-mvp <slug>`
> - Send back to discovery with a specific question for re-research
> - Override (rare; will be recorded as an override on the card)
> - Kill

Update the card's `status` and the report's *Decision* section only after the user has decided.
