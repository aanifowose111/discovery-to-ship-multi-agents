# Market scan methodology

How we figure out *where to look* before a discovery cycle starts. A market scan produces a short list of **candidate territories** (segments + categories + situations) that are worth mining for product ideas. The discovery cycle then mines those territories for specific ideas, using the methodology in `guides/product/idea-discovery-methodology.md`.

A scan is upstream of discovery. If discovery is "what ideas exist?" a scan is "where should we even look?"

---

## 1. Purpose

We do not have unlimited attention. Brainstorming product ideas without first deciding where to point the brainstorm produces a batch that all fails at the same step (usually distribution or founder fit). A market scan exists to prevent that.

A scan answers three questions:

1. **Which segments / categories are showing fresh pain, fresh capability, or fresh entry conditions** right now, that we are not yet exploring?
2. **Which of those map credibly to the user's strengths** — Python/Flask, React Native, multi-tenant SaaS architecture, evaluation engineering — so we are not chasing a territory where our advantage is zero?
3. **Where should the next discovery cycle aim its brainstorm**, with a defensible reason for each chosen territory?

If a scan does not produce a short list of named territories with reasons, it has failed.

---

## 2. Operating principles

1. **A scan is not the same as a discovery cycle.** A scan produces *territories* (places to look). Discovery produces *ideas* (specific products). Do not collapse the two.
2. **Bias for fresh signal over general truth.** Everyone knows healthcare is big. Nobody knows what specifically changed in independent veterinary practice billing in the last 90 days. The latter is what a scan is for.
3. **Founder fit is a multiplier, not a tiebreaker.** As with discovery, a territory that maps to what the user has already shipped is worth more than an equal-quality territory that requires a stack stretch.
4. **Citable signals, not impressions.** Every territory in the output must be backed by at least one URL — a complaint, a release note, a regulatory filing, a funding announcement, a Census release. "I have a hunch about X" is not a territory.
5. **Smaller candidate list, sharper candidates.** Five well-defended territories beat fifteen vague ones. Aim for 3-7 in the final output.
6. **Per the internet access policy in `CLAUDE.md`, web research happens by default.** Cite every meaningful source inline.

---

## 3. When to run a scan

Run a scan when **any** of these is true:

- We are about to start a discovery cycle and the last scan is older than ~90 days.
- The current candidate-territories list has been exhausted (most territories produced their batch of ideas, and the ideas have been triaged or killed).
- A major capability shift just happened — a model release, a new platform API, a regulatory change — that plausibly opens spaces that did not exist last quarter.
- A previous discovery cycle produced a batch where most ideas died at the same triage dimension (usually *user reachability* or *founder fit*), suggesting the territories we mined were systematically wrong.
- We have a working hypothesis we want to test ("is there enough fresh activity in the LLM-eval tooling space for indie products to break in?") — a *focused* scan.

**Don't scan when:**

- We are mid-build on an MVP. Scans during a build distract from shipping.
- We just ran a scan and have not yet acted on the previous one.
- The user has a strong prior they want to pursue without a scan ("I want to build in space X"). A scan can be skipped or scoped narrowly to confirm/deny the prior.

---

## 4. Inputs

A scan does not start cold. Before running one, the main Claude assembles:

| Input | Source |
|---|---|
| User profile and founder-fit context | `CLAUDE.md` + the user-profile memory |
| Previous scan reports (if any) | `market-research/*/scan.md` (one per scan run folder; newest by folder date) |
| Recent trend reports | `market-research/*/trends.md` — material findings from these feed the scan's *Source sweep* as priority sources |
| Recent killed ideas with reasons | `ideas/killed/` |
| Currently active triage lists | `market-research/*/triage.md` (one per discovery-cycle folder) |
| Any focused-scan hypothesis the user has given | the user prompt that triggered the scan |

Killed ideas, previous scans, and recent trend reports matter especially — they tell you what filters our pipeline applies and what has shifted since the last scan, so the new scan does not produce territories that will fail those filters again and incorporates the freshest signal.

---

## 5. The scan workflow

### 5.1 Set the aperture

Decide first whether this is a **broad scan** or a **focused scan**:

- **Broad scan** — no prior commitment to a space; sweeping for fresh territories across many possible categories. Output is 5-7 territories spanning multiple categories.
- **Focused scan** — a hypothesis or category is given ("LLM eval tooling," "indie SaaS for dental practices"). Output is a deeper read on that one category, with 2-4 sub-territories or a clear "this category is not currently fertile" finding.

Write the aperture down. Everything downstream is judged against it.

### 5.2 Source sweep

Sweep at least four of these source families, with notes on signal density (high / medium / low / none). Per the internet access policy, this is unbroken web research — fetch and search freely.

| Source family | What you are looking for |
|---|---|
| **Capability shifts** | Recent (last 90 days) model releases, API openings, platform changes, hardware shifts, regulatory changes. AI labs' blogs, API changelogs, FDA / SEC / equivalent filings, FCC / equivalent rule changes. |
| **Funding signals** | Where is venture money landing in the last 12-18 months? Crunchbase, Pitchbook (when accessible), VC partner blogs, YC batch announcements. Hot-money signals also flag *saturated* spaces — that is a finding too. |
| **Pain signals** | Public complaints clustered around a workflow or category. Subreddit threads with high engagement, G2/Capterra one-star reviews on category leaders, Stack Overflow tag activity, recent Hacker News threads with "[do not] use X" titles. |
| **Adjacency signals** | What workflows surround the user's already-shipped territory? findvil (job search), fijara (multi-tenant SaaS for service businesses), Intel dashboard work, chemistry-eval work — each has adjacent workflows worth surfacing. |
| **Demographic / behavioral shifts** | US Census BFS (business formation), BLS occupation projections, recent generational behavior reports (Pew, OurWorldInData). Slow signals, but they shift the medium-term map. |
| **Underserved segments** | Categories still dominated by spreadsheets, paper, or unmaintained tooling. Industry-association forum posts, trade publication recent issues. |
| **Regulated-industry shifts** | Healthcare, finance, education, transportation — categories where regulation changes the addressable surface. Federal register notices, state-level rule changes, sector consultants' newsletters. |

Note the date of every source. Stale signals (>24 months in fast categories, >5 years in slow ones) get downweighted.

### 5.3 Categorize what the sweep found

Group raw signals into **candidate territories**. A territory is more abstract than an idea — it is a *place we could send a discovery cycle*. Each territory should have:

- A named segment (specific persona + organization size class + region if relevant).
- A pain or capability anchor (what makes this territory fresh *right now*).
- At least one believable distribution channel (because territories with no reachable channel are dead on arrival).
- A founder-fit angle (or an honest "no founder fit, here for completeness").

Throw away signals that do not aggregate into a territory yet — note them in an "unresolved signals" appendix in case they become coherent later.

### 5.4 Prioritize territories

Rate each territory **HIGH / MEDIUM / LOW** on three dimensions:

| Dimension | What HIGH looks like | What LOW looks like |
|---|---|---|
| **Freshness** | A real shift in the last 90 days, citable. | Nothing has changed in 2+ years. |
| **Founder fit** | Maps to dockerized Flask + RN + multi-tenant SaaS + eval-style work. | Requires stacks/expertise the user has never shipped. |
| **Reachability** | At least one believable channel for the first 100 users at indie scale. | No identified channel; would need a marketing miracle. |

A territory's overall priority is roughly the lowest of the three (a HIGH × HIGH × LOW is still LOW — reachability bottlenecks the whole thing).

Cut LOWs from the output list unless we are deliberately exploring out-of-fit territories (e.g., the user is curious about a new stack and willing to learn). If you keep a LOW for that reason, flag it explicitly.

---

## 6. The market-scan report

Every scan produces one file at `market-research/<run-id>/scan.md` (each scan creates a fresh `<run-id>` folder so multiple scans never mix). Generate `<run-id>` via `python3 scripts/gen_run_id.py`. Format:

```markdown
---
date-scanned: YYYY-MM-DD
aperture: broad | focused
focus (if applicable): <one-line description of the focused hypothesis>
status: draft | reviewed | active
---

# Market scan: <date or codename>

## Aperture
What this scan was looking for. One paragraph.

## Source sweep
| Source family | Density | Notes |
|---|---|---|
| Capability shifts | high/med/low/none | one-line note + 1-2 representative URLs |
| Funding signals | ... | ... |
| Pain signals | ... | ... |
| Adjacency signals | ... | ... |
| Demographic / behavioral shifts | ... | ... |
| Underserved segments | ... | ... |
| Regulated-industry shifts | ... | ... |

## Candidate territories

### Territory 1: <short name>
- **Segment**: <one-sentence specific persona + size + region>
- **Anchor**: <pain or capability signal that makes this fresh — cite at least one URL>
- **Plausible distribution channel(s)**: <named channels, with rough activity sense>
- **Founder fit**: <how this maps to the user's strengths, or honest "no fit, included because freshness is high">
- **Priority**: HIGH | MEDIUM | LOW — <freshness/fit/reachability one-line breakdown>

### Territory 2: <short name>
[same structure]

### Territory N
[3-7 total]

## Unresolved signals
Signals that did not aggregate into a coherent territory yet — kept in case they become coherent in a later scan.

- <signal 1 — one line + URL>
- <signal 2>

## Recommended seeds for the next discovery cycle
Of the territories above, which 2-3 should feed the next discovery cycle (per `guides/product/idea-discovery-methodology.md`)? Why these and not the others?

## What this scan did not look at
Categories deliberately or accidentally excluded. Honest list — it scopes what the next scan should pick up.
```

The report's `status` starts as `draft`. After the user reviews and signs off, it advances to `active` and becomes the input to the next discovery cycle.

---

## 7. Handoff to discovery

Once a scan is `active`:

1. The 2-3 territories named in *Recommended seeds for the next discovery cycle* become the seeds for the brainstorm in the next discovery cycle. The cycle should produce idea cards that, in aggregate, cover those territories — though it does not have to be exclusive to them.
2. The discovery triage list (per `idea-discovery-methodology.md` §6) should record which territory each card came from, so we can tell post-hoc which territories were productive.
3. The remaining territories in the scan stay warm — used as seeds in subsequent cycles if the first batch is exhausted or killed.

---

## 8. When to re-scan

Re-scan when **any** of these is true:

- The active scan is more than ~90 days old.
- The recommended seeds have all produced exhausted or killed batches.
- A capability shift has happened that is plausibly bigger than anything in the active scan's *Source sweep*.
- A pattern emerges across multiple killed batches (e.g., everything dies at the segment-reachability check), suggesting our territories share a hidden flaw.

A re-scan is not a from-scratch redo. It builds on the previous scan: the *Source sweep* table records what changed since last time, the *Candidate territories* list inherits anything still fresh, and new territories are added.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
