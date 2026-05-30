# Trend monitoring

How we watch for shifts **between** market scans. A scan produces a snapshot of where to look; trend monitoring keeps that snapshot honest by checking, on a cadence, whether new capability shifts, regulatory changes, funding heat, or incumbent moves have invalidated it.

Trend monitoring is not a substitute for a scan. A scan re-maps the territory; a trend sweep updates the map between mappings.

---

## 1. Purpose

A 90-day scan cadence (per `market-scan-methodology.md`) is too slow for fast-moving categories. A frontier-AI model release can rewrite an eval-tooling territory in a week. A US Federal Register rule change can open or close a regulated-industry territory overnight. An incumbent shipping a feature that overlaps with a green-lit card can kill that card mid-build.

Trend monitoring catches those shifts early enough to act. It produces:

- A **trend report** at `market-research/trends-<YYYY-MM-DD>.md` summarizing what changed.
- **Material findings** that warrant action — re-scan, re-validate a card, re-scope a brief, or kill an active artifact.
- A handoff to the correct downstream command (`/scan`, `/validate-card <slug>`, `/scope-mvp <slug>`) so the action is one command away.

---

## 2. Operating principles

1. **Watch what is active, not the universe.** The watchlist is derived from the active scan's territories and the currently-active idea cards / MVP briefs. Sweeping the whole internet weekly burns attention.
2. **Material vs. notable vs. background.** Every finding gets categorized. Only material findings trigger handoffs; notable and background go to the record but produce no action.
3. **Disconfirmation is the point.** A trend sweep that finds "nothing changed" is a successful sweep. It is not padding. Note it and move on.
4. **Citable shifts only.** Same evidence standard as the scan: every material finding has a URL. "I get the sense X is happening" is not a finding.
5. **Per the internet access policy in `CLAUDE.md`, web research happens by default.** Fetch and search freely.

---

## 3. The watchlist

The watchlist is **not static**. It is derived from current pipeline state. Re-derive it at the start of each sweep.

| Category | What to watch | Sources |
|---|---|---|
| **Capability shifts** | Model releases, API openings, platform changes that affect *active territories* | Anthropic / OpenAI / Google blogs; API changelogs; Hugging Face releases relevant to active eval-style territories |
| **Regulatory shifts** | Federal Register notices, state-level rule changes, agency announcements in *active regulated territories* (health, finance, education, transportation) | Federal Register, EU OJ, sector-specific regulator pages, sector consultants' newsletters |
| **Funding heat** | Recent rounds in *active territories* — both as opportunity signal and as saturation warning | Crunchbase recent rounds, YC batch announcements, VC blog posts, ProductHunt funding announcements |
| **Pain pulse** | Activity changes in the channels named in the *Distribution hypothesis* of active cards | Subreddit activity, Hacker News, Indie Hackers, segment-specific forums |
| **Encroachment** | Incumbents announcing features that overlap with active green-lit cards or in-build MVPs | Incumbent changelogs, roadmaps, blog posts, conference announcements |
| **Adjacency tremors** | Workflow shifts in *adjacencies to the user's prior shipped work* (findvil, fijara, eval engineering) | Domain-specific news, podcasts, trade publications |

If the active scan or the active cards change, the watchlist changes with them.

---

## 4. Cadence and triggers

**Default cadence:** weekly. Fast enough to catch shifts before they bite, slow enough to not consume attention.

**Triggered emergency sweep** (run immediately, do not wait for the next weekly slot) when any of these happens:

- A major model release from a frontier AI lab (Anthropic, OpenAI, Google DeepMind, Meta).
- A regulatory announcement directly naming an active territory.
- An incumbent in an active territory ships a feature mentioned by name in any of our active cards' differentiation sections.
- A funding round larger than ~$10M is announced in an active territory.

**Skip a sweep** when:

- The previous sweep was less than 4 days ago (i.e., a triggered sweep already ran this week).
- We are mid-build with no active cards in validation and no green-lit-to-build briefs in flight. There is nothing for the sweep to act on.

---

## 5. The sweep workflow

### 5.1 Derive the watchlist

Read:

- The most recent `market-research/scan-*.md` with `status: active`.
- All `ideas/<slug>.md` with `status` in `{green-lit, in-validation}`.
- All `web-apps/<slug>/MVP.md` and `mobile-apps/<slug>/MVP.md` with `status` in `{draft, in-scoping, green-lit-to-build}`.

From those, build the watchlist: active territories, active cards' differentiation claims, active briefs' stack and feature set.

### 5.2 Sweep the categories

For each watchlist category in §3, sweep the named sources. For each source, note: date last checked (from previous trend reports if any), what changed since, density of signal.

Time-box the sweep. A weekly sweep should take ~30-60 minutes of focused web work, not a half-day. If you find yourself going deeper on a single finding, that itself is a material finding — stop sweeping, write it up, hand off.

### 5.3 Categorize each finding

Every concrete thing the sweep surfaces goes into one of three buckets:

- **Material** — a specific change that affects a specific active artifact (scan, card, brief), with a clear recommended action.
- **Notable** — a real change in the broader environment that is worth recording but doesn't yet warrant a pipeline action. Becomes context for the next scan.
- **Background** — interesting but not relevant to the current pipeline. Recorded for completeness.

When in doubt between Material and Notable: only call it Material if you can name the specific active artifact it affects and the specific recommended action.

### 5.4 Write the trend report

Format below in §6. Write it to `market-research/trends-<YYYY-MM-DD>.md`.

### 5.5 Show the user and hand off

Show the report summary. For each material finding, the recommended action is **one slash command away** — `/scan`, `/validate-card <slug>`, `/scope-mvp <slug>`, etc. Let the user decide which actions to take.

---

## 6. The trend report format

```markdown
---
date-swept: YYYY-MM-DD
sweep-type: scheduled | triggered
trigger (if triggered): <one-line reason>
status: draft | reviewed | acted-on
---

# Trend sweep: <date>

## Watchlist derived from
- Active scan: market-research/scan-<date>.md
- Active cards: <slug list>
- Active briefs: <slug list>

## Source coverage
| Category | Sources checked | Density | Last checked previously |
|---|---|---|---|
| Capability shifts | ... | high/med/low/none | <date or "first sweep"> |
| Regulatory | ... | ... | ... |
| Funding heat | ... | ... | ... |
| Pain pulse | ... | ... | ... |
| Encroachment | ... | ... | ... |
| Adjacency tremors | ... | ... | ... |

## Material findings
*(Empty list is a valid, successful sweep.)*

### Finding 1: <short name>
- **What changed**: <one sentence, URL>
- **Date of shift**: YYYY-MM-DD
- **Affects**: <specific active artifact: scan / card slug / brief slug>
- **Recommended action**: `/scan` | `/validate-card <slug>` | `/scope-mvp <slug>` | `kill <slug>` | other
- **Confidence**: HIGH | MEDIUM | LOW
- **Rationale**: <2-3 sentences>

### Finding 2: ...

## Notable findings
- <one-line summary + URL>
- <one-line summary + URL>

## Background findings
- <one-line summary + URL>

## Recommended next commands
- <slash command 1 — for which material finding>
- <slash command 2>
- *(if no material findings: "No actions recommended. Filed for the record.")*
```

---

## 7. Handoffs

A trend report is consumed by the user, but it points at specific downstream commands:

| Finding type | Handoff |
|---|---|
| Scan is stale or a major territory-level shift | `/scan` (re-run the market scan, incorporating the trend finding) |
| Active idea card's viability/competitive/segment claim is now contradicted | `/validate-card <slug>` (re-run validation for that card) |
| Active brief's stack or scope assumptions are invalidated | `/scope-mvp <slug>` (re-scope the brief) |
| Encroachment finding kills an active card or brief | User decides whether to kill — main Claude updates `ideas/<slug>.md` or the brief to `killed` status with a link to the trend report |

The trend monitor itself never advances any artifact. It surfaces findings and recommends commands. The user decides which to run.

---

## 8. When to recalibrate the watchlist

The watchlist is derived from active state, so it auto-recalibrates whenever:

- A new scan is run (`/scan`) — territories change.
- A card is killed or green-lit (`/validate-card`) — active card set changes.
- A brief reaches green-lit-to-build or is killed (`/scope-mvp`) — active brief set changes.

In addition, every ~90 days regardless, audit the watchlist for sources that have stopped producing signal (a subreddit that's gone quiet, a regulator that hasn't shipped a relevant notice in a year) and replace them. Stale sources produce false negatives — they say "nothing changed" because they have nothing to say, which is different from "nothing changed."

---

## 9. Integration with the rest of the pipeline

| Upstream guide / artifact | How it uses trend monitoring |
|---|---|
| `guides/market/market-scan-methodology.md` | A new scan starts by reading the latest trend report — recent material findings feed the scan's *Source sweep* as priority sources. |
| `guides/product/idea-discovery-methodology.md` | Discovery cycles started after a material capability-shift finding should treat that shift as one of the §3 idea sources. |
| `guides/product/idea-validation-methodology.md` | Reviewers may check the latest trend report when forming a verdict, especially if their finding depends on whether the differentiation story still holds against a recent incumbent move. |
| `guides/product/mvp-scoping-methodology.md` | A brief about to be green-lit-to-build is gated on no material encroachment finding having landed since the brief was drafted. |

---

*Last meaningful revision: 2026-05-29 (initial draft).*
