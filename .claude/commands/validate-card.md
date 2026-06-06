---
description: Run validation on a green-bucket idea card by invoking the four product reviewers in parallel (viability, competition, market-segment, pricing) and integrating their verdicts, per guides/product/idea-validation-methodology.md.
argument-hint: <card-slug>
---

You are about to validate one idea card. Follow the methodology in @guides/product/idea-validation-methodology.md exactly.

**Arguments:** $ARGUMENTS — the card slug. The card must exist at `ideas/<run-id>/<slug>.md` (locate via `find ideas -name "<slug>.md" -not -path "*/killed/*"`) and be in the `green` triage bucket (i.e., `status: draft` or `triaged`, not `killed`).

### Inputs to read before invoking reviewers
- The idea card: locate via `find ideas -name "<slug>.md" -not -path "*/killed/*"` → gives `ideas/<run-id>/<slug>.md`. **Extract `<run-id>` from the path** — the validation report writes to `market-research/<run-id>/` (same run-id so the validation colocates with the cycle that produced the card).
- @guides/product/idea-discovery-methodology.md (for shared vocabulary)
- @guides/product/idea-validation-methodology.md (for the verdict format and integration rules)
- The most recent `market-research/*/trends.md` (if any) — may affect reviewer findings

### Do
1. Verify the card exists and is in the green bucket. If not, stop and ask the user how to proceed (override / pick a different card).
2. Update the card's `status` field from `triaged` to `in-validation`.
3. Invoke the **four reviewers in parallel**, in a single message with four Agent tool calls. **Use the custom-subagent invocation pattern in `CLAUDE.md`** (the "Invoking custom subagents — the universal pattern" section) — each call uses `subagent_type: "general-purpose"` and instructs the agent to read and follow the persona file:
   - For viability: read and follow `.claude/agents/product-viability-reviewer.md`
   - For competition: read and follow `.claude/agents/product-competition-reviewer.md`
   - For market-segment: read and follow `.claude/agents/market-segment-reviewer.md`
   - For pricing: read and follow `.claude/agents/product-pricing-reviewer.md`

   Each agent should also be told to read the card at `ideas/<run-id>/<slug>.md` (use the resolved path from pre-flight), the discovery and validation methodology guides, and `CLAUDE.md` for founder context — and to return its output in the locked verdict format from `idea-validation-methodology.md` §5. The pricing reviewer additionally returns the Comparable-pricing / Proposed-price / Unit-economics / Suggested-pricing-options blocks per its persona file.
4. Wait for all four verdicts.
5. Integrate per §6 of the validation guide. If verdicts conflict on the same evidence, surface the conflict explicitly; do not silently average. The pricing reviewer's Suggested-pricing-options block is preserved verbatim in the report — the user picks one (or overrides with a hand-typed price) at decision time.
6. Write the validation report to `market-research/<run-id>/validation-<slug>.md` (where `<run-id>` is the SAME run-id resolved from the card's path in pre-flight — multiple validations from cards in the same discovery cycle all share that cycle's market-research folder). Add `slug: <slug>`, `run-id: <run-id>`, and `date-validation: <YYYY-MM-DD>` to the frontmatter. Fill all sections except *Decision* and *Chosen price* (those are the user's).

### Stop here — user checkpoint
After writing the report, **stop**. Do not advance the card to `green-lit` or `killed`. Show the user:

> Validation report at `market-research/<run-id>/validation-<slug>.md`.
>
> Combined verdict: <APPROVE / APPROVE-WITH-NOTES / REJECT>
> Conflicts (if any): <summary>
>
> Pricing reviewer suggested:
>   1. **<Option 1 name>** — $<amount> / <unit> / <interval> — RECOMMENDED
>   2. **<Option 2 name>** — $<amount> / <unit> / <interval>
>   3. **<Option 3 name>** — $<amount> / <unit> / <interval>
>
> Your call:
> - Advance to `green-lit` → next step is `/scope-mvp <slug>`. Also pick a price: Option 1 / 2 / 3 / type your own (e.g., "$49/seat/month").
> - Send back to discovery with a specific question for re-research
> - Override (rare; will be recorded as an override on the card)
> - Kill

When the user picks a price (or types their own), write `priced-at: $<amount> <unit> <interval>` and `pricing-strategy: "<option name or 'user-override'>"` to the card's frontmatter, and update the *Chosen price* section of the validation report with the picked option + rationale. If the user types their own price, validate it parses as a money amount (e.g., `$29/seat/month`, `$199 one-time`) and surface the pricing-reviewer's suggested options' rationales next to it for context — but respect the user's choice.

Update the card's `status` and the report's *Decision* section only after the user has decided.

**If the user picks Kill**, also append a `card-kill` audit-log entry (per `CLAUDE.md` § Audit log): `python3 scripts/audit_log.py add card-kill "Killed card <slug> after validation (run-id: <run-id>). Reason: <one-line user reason>."`. This is in addition to moving the card to `ideas/killed/<run-id>/<slug>.md`.
