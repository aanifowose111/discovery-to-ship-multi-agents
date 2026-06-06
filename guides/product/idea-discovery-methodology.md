# Product idea discovery methodology

A repeatable process for going from "we want to build something useful" to **a prioritized, reviewer-validated list of candidate products** that we can pick the most viable MVP from.

This is the *first* guide in the product domain. Downstream guides (validation criteria, market-research methodology, MVP scoping) and downstream reviewer assistants (`product-viability-reviewer`, `product-competition-reviewer`, etc.) will reference back to this one for shared vocabulary and the idea-card format.

---

## 1. Purpose

We are a small operation (one engineer + Claude). We do not have the budget to build the wrong thing. The purpose of discovery is to make sure that *by the time we open an IDE on a product*, we have already filtered out the ideas that fail on any of these:

- Nobody has the problem badly enough to switch.
- We cannot plausibly reach the people who do.
- We are not differentially well-positioned to build it.
- The effort cost is wildly out of scale with the expected payoff.

Discovery does not try to *prove* an idea is good. That is the job of validation (next guide). Discovery just stops obvious losers from eating downstream cycles.

---

## 2. Operating principles

Every step in this methodology is derived from one of these. If a step does not serve one of these, it should be removed.

1. **Problem before solution.** Capture the problem in its own words before naming the product. Many ideas die the moment the problem is written down clearly because it becomes obvious nobody actually has it.
2. **Distribution is a first-class question, not an afterthought.** A product nobody can find is the same as a product that does not exist. Every idea card must have a distribution hypothesis or it is not a card yet.
3. **Founder-market fit is a multiplier, not a tiebreaker.** If two ideas look equally good but only one leverages what the user already knows how to ship, it is not a coin flip — pick the one that compounds. We have shipped dockerized Flask platforms, React Native apps, and dashboards that wrangle messy data; these are unfair advantages.
4. **Capture is lightweight; triage is rigorous.** It should take ~10 minutes to fill in an idea card, but the triage rubric should be honest enough to cut half of them.
5. **Score and prioritize — do not pick.** Discovery produces a *ranked list*. Picking the actual product to build happens after validation, not at discovery time.
6. **Write things down even when they look obviously bad.** Killed ideas teach you what your filter actually is. Keep them in `ideas/killed/` with a one-line reason.

---

## 3. Where ideas come from

A discovery session should pull from at least three of these sources, not just one. Single-source ideation tends to produce a narrow batch that all fails at the same step.

**Mode selection when `user-context/IDEAS.md` is populated.** If the user has populated `user-context/IDEAS.md` with seed ideas (their mental backlog of products they've thought about but not formalized), the discovery cycle offers three modes before the brainstorm begins:

| Mode | Behavior | When to pick |
|---|---|---|
| **(a) Promote seeds** | Skip the brainstorm. Convert each seed in `IDEAS.md` directly into a formal card (`ideas/<run-id>/<slug>.md`), score, triage. The ≥10-cards floor does not apply. | When the user already knows what they want to validate and wants to skip ideation entirely. |
| **(b) Full discovery (ignore seeds)** | Brainstorm 10+ candidates from the sources below as usual; do not pull from `IDEAS.md`. | When seeds feel stale, or the user wants a fresh angle. |
| **(c) Hybrid + compare** | Brainstorm 10+ candidates AND add one card per seed idea. Triage compares them side-by-side with an explicit "Seeds vs. brainstormed candidates" subsection. | Default recommendation — best for "I have ideas but want to see how they stack up." |

If `IDEAS.md` is missing or contains only placeholders, the cycle proceeds as full discovery (mode b implicit). Cards drawn from `IDEAS.md` get `source: user-context/IDEAS.md` in frontmatter; cards from the brainstorm get the regular source tag from the table below.

| Source | What it looks like in practice |
|---|---|
| **Personal pain points** | Workflows the user has personally hated, including in prior projects (e.g., findvil, fijara — substitute whatever the *current* user has actually shipped, per `user-context/INTERESTS.md`). The user has already proven willingness-to-build on this kind of problem. |
| **Adjacent workflows** | For each shipped project, ask: "what does the user of this product also do, just before or just after, that is still painful?" Job-search adjacency, dashboard-tooling adjacency, multi-tenant SaaS adjacency. |
| **Competitor weaknesses** | Existing products with bad UX, missing features, or hostile pricing. Look at one-star reviews on G2, Capterra, Product Hunt, App Store. The complaints *are* the product. |
| **Shifts in capability** | Things that became possible recently — cheap LLM inference, better mobile sensors, new API access, regulatory changes. Each shift opens a window before incumbents close it. The most recent `market-research/*/trends.md` (per `guides/market/trend-monitoring.md`) is the canonical source for fresh capability shifts; check it first. |
| **Underserved segments** | Industries or roles where the dominant tool is "an Excel spreadsheet someone emails around." High pain, low competition, but distribution is usually the hard part. |
| **Forced multi-step workflows** | Anywhere a person currently glues 3+ tools together by hand. Each glue point is a potential product. |

A discovery session does not need to be exhaustive across these. It needs to be *plural* — at least three sources represented in the batch so triage has comparable variety.

### 3.1 Web research is part of every source

Discovery cannot be done from a chair with no internet. **Every source listed above requires active web research** — one-star reviews on G2/Capterra/Product Hunt/App Store for competitor weaknesses; release notes, model cards, API changelogs, and policy announcements for capability shifts; subreddits, Indie Hackers threads, niche forums, and Stack Overflow tag activity for underserved segments and multi-step workflows.

Per the internet access policy in `CLAUDE.md`, web search and fetch happen by default without permission prompts. **Cite the URL of every meaningful source** inside the idea card — in the *Problem*, *Current alternatives*, and *Distribution hypothesis* sections especially — so the validation reviewers and the user can audit the evidence chain later.

An idea card whose *Problem* and *Current alternatives* sections contain no external citations is a red flag: either the research has not happened yet, or the idea is being captured from the user's intuition alone. Both are fixable, but they should be visible to triage.

---

## 4. The idea card

Every discovered idea becomes one file in `ideas/<short-slug>.md`. The card is intentionally short — if a section needs more than ~5 sentences, the idea is not understood yet and it is fine to leave the section thin.

```markdown
---
slug: <kebab-case-slug>
date-captured: YYYY-MM-DD
source: <one of: personal-pain | adjacent | competitor-weakness | capability-shift | underserved | multi-step>
status: draft   # draft → triaged → in-validation → green-lit → killed
---

# <One-line description of the product>

## Problem
Who has it, when does it bite, how painful is it on a 1-5 scale, and what evidence do we have that real people experience this?

## Current alternatives
What do people do *today* when they hit this problem? Manual workarounds count. "Nothing — they suffer" is a valid (and informative) answer.

## Proposed solution
1-3 sentences. The minimum thing that solves the problem.

## Why now
What changed in the world that makes this possible, necessary, or differently solvable than it was 2-3 years ago? If the honest answer is "nothing changed", say so — that is a real risk signal.

## Distribution hypothesis
How do the first 100 users find this product? Not the first million — the first hundred. Be specific (which subreddit, which directory, which referral motion, which conference).

## Founder fit
Why is *this* user, with *this* background (Python/Flask, React Native, multi-tenant SaaS, eval engineering), differentially well-positioned to build this versus a generic team?

## Tech-stack fit
Does this fit dockerized Flask + React Native cleanly, or does it require a stack the user does not yet have leverage in? Flag any stretches.

## Top risks / unknowns
The 2-3 things that would most likely kill this idea. Write them as questions validation can answer.

## Rough effort estimate
Solo-build, working evenings + weekends, to MVP that is shippable to first 10 users. Express in weeks.
```

Cards live in `ideas/` and never move once captured. Status field is updated in place.

---

## 5. Triage rubric

After a discovery batch is captured, score each card on the six dimensions below. Use a strict 1-5 scale where **3 = neutral, 5 = exceptional, 1 = disqualifying**. Most ideas will score 2-3 on most dimensions; that is healthy.

| Dimension | What 5 looks like | What 1 looks like |
|---|---|---|
| **Problem severity** | People currently pay for or hack around this; willingness-to-switch is plausible. | Nice-to-have. People shrug. |
| **User reachability** | A specific, accessible channel with low CAC exists. | No identifiable channel; would need a marketing miracle. |
| **Founder fit** | User's prior projects directly transfer; unfair advantage. | Stack and domain are both unfamiliar. |
| **Tech-stack fit** | Clean fit for Flask + RN; no new infra category required. | Requires stack(s) the user has never shipped in. |
| **Differentiation** | A real reason the user can build this better, cheaper, or faster than incumbents — or there is no incumbent. | Crowded space, no edge. |
| **Effort efficiency** | MVP shippable in a few weeks of solo evenings. | Months of build before any user can try anything. |

Sum the six scores → 6-30. Bucket the cards:

- **24-30 — Green:** strong candidate; advance to validation.
- **18-23 — Yellow:** advance only if green tier is thin; flag the lowest-scoring dimension as the thing validation needs to disprove.
- **<18 — Red:** move to `ideas/killed/` with the score and a one-line reason. Do not delete — killed ideas tune the filter.

**Hard kills regardless of total:**
- Any score of **1 on Problem severity or User reachability**. A 5/5/5/5/5/1 idea is still dead; you cannot fix "nobody wants it" or "nobody can find it" with more engineering.

The triage step produces a single ranked list at `market-research/<run-id>/triage.md` — where `<run-id>` is shared with the discovery cycle's cards folder at `ideas/<run-id>/`. Each `/discover` invocation creates a new `<run-id>` so cycles never mix.

---

## 6. Output of a discovery cycle

A discovery cycle is complete when we have:

1. **At least 10 idea cards** in `ideas/`, drawn from at least three of the sources in §3.
2. **A triage list** at `market-research/<run-id>/triage.md` (matching the cards folder `ideas/<run-id>/`) with every card scored and bucketed.
3. **A "top 3" callout** at the top of the triage list — the three highest-scoring greens, with a one-paragraph note on each explaining what the next validation step would be.

The top 3 then become the input to the next phase (validation + market research). The other greens stay warm in case the top 3 die in validation.

---

## 7. Handoff to validation

Once a card is in the green bucket and has been picked into the top 3, its `status` is updated to `in-validation` and it is handed off to the validation reviewer assistants (to be created):

- **`product-viability-reviewer`** — sanity-checks the problem statement, current alternatives, and willingness-to-switch claims.
- **`product-competition-reviewer`** — checks differentiation against actual incumbents and substitutes.
- **`market-segment-reviewer`** — sizes the addressable segment and tests the distribution hypothesis.

Each reviewer returns a verdict (approve / approve-with-notes / reject) and a short list of findings (per the convention in `.claude/agents/README.md`). A card advances to `green-lit` only when all three reviewers approve (with or without notes) *and* the user signs off.

The validation methodology itself lives in a separate guide (to be written next): `guides/product/idea-validation-methodology.md`.

---

## 8. When to re-run discovery

Discovery is not a one-time event. Re-run when:

- The current top 3 have all been killed in validation.
- A major capability shift happens (e.g., a new model release, a new platform API) that opens product spaces that did not exist last cycle.
- 90+ days have passed without a green-lit product, regardless of cause — the filter has drifted and needs to be re-calibrated against fresh inputs.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
