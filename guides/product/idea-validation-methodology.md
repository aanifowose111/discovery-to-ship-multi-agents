# Product idea validation methodology

How a green-bucket idea card (per `idea-discovery-methodology.md`) gets stress-tested before we commit any engineering time to it. Validation is where the **multiple reviewer assistants** earn their keep: each reviewer has a narrow scope and a defined verdict format, and the main Claude integrates their findings into a single decision.

This guide is the contract those reviewers will be built against. The reviewers are:

- **`product-viability-reviewer`** — does the problem exist, badly enough, for enough people?
- **`product-competition-reviewer`** — is there real differentiation against the actual incumbents and substitutes?
- **`market-segment-reviewer`** — is the segment big enough, reachable enough, and (broadly) willing-to-pay enough to support a product?
- **`product-pricing-reviewer`** — is the *specific* proposed price defensible against comparable products, the segment's willingness-to-pay signals, and the unit-economics math? (Standalone-invokable via `/reprice` for already-validated artifacts.)

When these reviewers are created in `.claude/agents/`, their instructions should reference this guide for shared vocabulary and the verdict format.

Note the overlap between `market-segment-reviewer` and `product-pricing-reviewer`: market-segment looks at *whether* the segment will pay *anything*; pricing looks at *what amount* the segment will pay against comparable-product evidence. The market-segment reviewer establishes the ballpark; the pricing reviewer pins the number.

---

## 1. Purpose

Discovery filters out *obvious* losers. Validation is for the **non-obvious** ones — the ideas that look good on the card but fail when stress-tested against real users, real competitors, and real markets.

We validate to answer four questions, in order:

1. **Does the problem exist?** Can we cite people *outside the user's own head* who articulate it?
2. **Do they want it solved badly enough to switch?** Are they currently paying for, hacking around, or actively complaining about the current alternatives?
3. **Can we differentiate?** Is there a real reason we can win against incumbents — or is the space genuinely open?
4. **Can we reach them?** Is the distribution hypothesis from the card plausible at the first-100-users scale?

A card that passes all four advances to MVP scoping. A card that fails any one is either killed or sent back to discovery with a specific question to answer.

---

## 2. Operating principles

1. **Validate by reading, not by building.** A landing-page test, an MVP, or a prototype is *not* validation — it is a later, more expensive form of validation that should only happen after the cheap reading-based validation passes. Web research, review-mining, and incumbent-product analysis come first.
2. **External evidence beats internal conviction.** Every claim a reviewer makes must trace to a citable source: a review, a thread, a forum post, an incumbent's pricing page, a Crunchbase entry, a job posting, a regulatory filing. "I think users probably want X" is not a finding.
3. **Reviewers are narrow on purpose.** Each reviewer has one lens. A reviewer that is asked "is this idea good?" will return mush. A reviewer that is asked "are the listed competitors real, are they weak in the ways the card claims, and what did you find that the card missed?" returns a useful answer.
4. **Disconfirmation is the point.** A reviewer that always returns "approve" is broken. The default posture is skeptical — looking for the reason this idea will fail. If after honest searching nothing fails, *that* is approval.
5. **One round of validation is enough to advance or kill, never enough to start building.** Advancement from validation means "promoted to MVP scoping" — not "start coding". MVP scoping is a separate guide (to be written) that decides the smallest thing we can put in front of real users.

---

## 3. Validation inputs

To run validation on an idea card, the main Claude assembles the following inputs and passes them to each reviewer:

| Input | Source |
|---|---|
| The idea card itself | `ideas/<run-id>/<slug>.md` — locate via `find ideas -name "<slug>.md" -not -path "*/killed/*"` |
| Discovery methodology (for shared vocabulary) | `guides/product/idea-discovery-methodology.md` |
| This guide (for the verdict format) | `guides/product/idea-validation-methodology.md` |
| The user's stack/founder context | `CLAUDE.md` + the user-profile memory |

Reviewers do their own web research from there. They are not given hand-picked sources — that would bias them toward the card's framing. Per the internet access policy in `CLAUDE.md`, reviewers fetch what they need without permission prompts.

---

## 4. The four reviewers and their scopes

### 4.1 `product-viability-reviewer`

**Lens:** Does the problem exist, badly enough, for enough people?

**Specifically tests:**
- Are there citable *outside* voices articulating the problem in the card's terms? Forum threads, Reddit posts, blog complaints, podcast transcripts, support-forum questions, G2/Capterra one-star reviews.
- Do the *Current alternatives* on the card actually describe what people do today? Often the card understates how good "good enough" already is.
- Is the *Why now* claim defensible, or is the honest answer "nothing changed and this could have been built five years ago"?
- Is the problem severity score (1-5) on the card supportable, or inflated?

**Returns:** Verdict + findings (see §5 format).

### 4.2 `product-competition-reviewer`

**Lens:** Is there real differentiation against the actual incumbents and substitutes?

**Specifically tests:**
- Who is *actually* in this space today, including non-obvious substitutes (a spreadsheet someone emails around is a competitor)?
- For each incumbent: pricing, positioning, last meaningful product update, public complaints. Pull from their site, G2/Capterra, Product Hunt, the App Store, and recent Hacker News threads.
- Is the differentiation story on the card real — or is it a difference the user finds compelling that the market won't pay for?
- Are there platform risks (an incumbent that could trivially clone this in a sprint if it took off)?

**Returns:** Verdict + findings.

### 4.3 `market-segment-reviewer`

**Lens:** Is the segment big enough, reachable enough, and (broadly) willing-to-pay enough?

**Specifically tests:**
- Rough segment sizing — order of magnitude is fine, false precision is worse than no number. Cite the data source.
- Is the *Distribution hypothesis* on the card plausible at the first-100-users scale? Inspect the proposed channel (subreddit activity, directory traffic, conference attendance) and judge whether 100 users could plausibly be reached there in 60-90 days.
- Broad willingness-to-pay signals: do incumbents charge? what tier? do segment members talk publicly about budget for this category? (The *specific* proposed price is the pricing reviewer's job, §4.4 below.)
- Is the segment growing, flat, or contracting? Contracting segments are not automatically disqualifying, but they should be flagged.

**Returns:** Verdict + findings.

### 4.4 `product-pricing-reviewer`

**Lens:** Is the *specific* proposed price defensible against comparable products, segment willingness-to-pay signals, and solo-builder unit economics?

**Specifically tests:**
- What does the artifact actually propose as a price, and how was it set (by analogy / by value-based math / unstated)?
- Comparable products' real pricing — pull a small table of 3-7 rows, each row a vendor / tier / price / unit / interval / source URL.
- Segment-specific willingness-to-pay: public complaints about price ("X is too expensive at $Y"), public budget benchmarks, substitution-up and substitution-down patterns, procurement-gate friction.
- Solo-builder unit economics: variable cost per user, gross margin at proposed price, break-even user count at proposed price + fixed infra, headroom for churn. The price has to support a one-person operation paying their own infrastructure.
- Auto-REJECT cases: price below variable cost; price >3x cheapest comparable with no value-based math; enterprise-WTP assumption applied to an SMB segment (or vice versa).

**Returns:** Verdict + findings, **plus** a required `## Suggested pricing options` block with 2-3 strategic options ranked recommendation-first, each with price/model, strategy framing, trade-off, and one-line evidence chain. The user picks one (or types their own override) at validation decision time.

---

## 5. Verdict format

Every reviewer returns exactly this structure (matches the convention in `.claude/agents/README.md`):

```markdown
## Verdict
APPROVE | APPROVE-WITH-NOTES | REJECT

## Confidence
LOW | MEDIUM | HIGH — based on how much corroborating evidence the reviewer found

## Findings
1. <Finding one — most important first. Each finding cites a source URL.>
2. <Finding two.>
3. <Finding three. Three to five total; more than seven means the reviewer is padding.>

## What I could not verify
- <Specific gaps in evidence. This list is as important as the findings — it is what the next round of validation or the user-facing version of the product will need to confirm.>

## Sources
- <URL 1>
- <URL 2>
- ...
```

Verdicts mean:

- **APPROVE** — The card's claims on this reviewer's lens are supported by external evidence. No major concerns.
- **APPROVE-WITH-NOTES** — Mostly supported, but specific concerns are flagged. The notes describe what to monitor or fix during MVP scoping.
- **REJECT** — The card's claims on this lens are contradicted, unsupported, or rest on assumptions the reviewer could not validate.

---

## 6. Integration: how the main Claude assembles a decision

After all four reviewers return:

| Combination | Action |
|---|---|
| 4 × APPROVE | Advance card status to `green-lit` once user signs off **and picks a price** from the pricing reviewer's suggested options (or types an override). Hand off to MVP scoping. |
| Any mix of APPROVE and APPROVE-WITH-NOTES | Summarize the notes into a single list. Present to the user for sign-off. On approval, advance to `green-lit` with the notes carried forward to MVP scoping. **The pricing reviewer's suggested options are still surfaced for the user's pick** even when its verdict is APPROVE-WITH-NOTES. |
| Any REJECT | Do **not** advance. Present the rejection reason to the user. The user decides whether to (a) kill the card, (b) send it back to discovery with a specific question for re-research, or (c) override the rejection (rare, and should be recorded as an override on the card). A pricing-only REJECT is often a "revise pricing and re-validate" case rather than a kill — surface the options. |
| Conflicting verdicts on the same evidence | Surface the conflict explicitly to the user with the evidence chain. Do not silently average. |

**The user always signs off on the final decision**, per the working style in `CLAUDE.md`. Reviewers do not advance cards on their own. The user's chosen price is recorded as `priced-at: $<amount> <unit> <interval>` in the card's frontmatter, with `pricing-strategy: "<chosen-option-name>"` or `pricing-strategy: "user-override"`.

---

## 7. The validation report

Each validation run produces one file: `market-research/<run-id>/validation-<card-slug>.md` — where `<run-id>` is the same as the card's discovery-cycle folder (`ideas/<run-id>/<slug>.md`). This colocates the validation with all other artifacts from the same cycle (triage, sibling validations, downstream scoping).

It contains, in order:

1. **Card snapshot** — the idea card's content at the moment validation ran (so the report stays meaningful even if the card is later edited).
2. **Reviewer verdicts** — all four, full. The pricing reviewer's *Comparable pricing*, *Proposed price*, *Unit-economics sanity check*, and *Suggested pricing options* blocks are included verbatim.
3. **Integration summary** — the main Claude's synthesis: combined verdict, combined notes, conflicts surfaced.
4. **Decision** — populated by the user (kill / advance / override / re-research) with a one-paragraph reason.
5. **Chosen price** — populated by the user (picked option name or user-override) with the final `priced-at:` value written here. Used by `/scope-mvp` and `/reprice` as the canonical price for the artifact.
6. **Open questions for MVP scoping** — extracted from the "What I could not verify" sections of the four reviewers, so they don't get lost.

A killed card moves from `ideas/<run-id>/<slug>.md` to `ideas/killed/<run-id>/<slug>.md` (preserving the `<run-id>` link back to the cycle), with `status: killed` and a `killed-reason` field linking the validation report. An advanced card's status updates to `green-lit` with the link, and the card stays in its `ideas/<run-id>/` folder.

---

## 8. What validation does *not* do

Validation does not:

- **Pick the product to build.** Multiple cards can be green-lit simultaneously; product selection happens during MVP scoping, with cost and timing factored in.
- **Size the MVP.** MVP scoping is a separate phase with its own guide.
- **Replace user judgment.** The reviewers exist to make sure the user is not the only filter, not to remove the user from the decision.

---

## 9. When to add or change reviewers

The three reviewers above are the **minimum**. Add a fourth reviewer when a recurring failure mode in validated cards is not being caught by any of the existing three. Examples we might hit:

- A `product-regulatory-reviewer` if we start exploring categories where compliance is the dominant constraint (healthcare, finance, education).
- A `product-tech-risk-reviewer` if we start exploring ideas where the technical core itself is uncertain (e.g., LLM-output quality at scale).

Adding a reviewer is a scaffolding-phase action: write the reviewer, the user verifies it (per `feedback-workflow`), then it becomes part of the default loop.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
