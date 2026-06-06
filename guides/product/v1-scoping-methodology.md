# Product v1 scoping methodology

How a product transitions from a shipped MVP to a real v1 — the polished, feature-complete build that lives past the first-10-users validation. This is the **second scoping pass** in the pipeline; the first one (`/scope-mvp`) was about the smallest thing that could validate the riskiest assumption, and the v1 pass is about the smallest thing that could be a real product *now that the assumption has held*.

The companion command is `/scope-v1 <slug>`. The companion file format is `V1.md`, written next to the existing `MVP.md` at `<web-apps|mobile-apps|desktop-apps>/<slug>/V1.md`.

This guide is paired with `mvp-scoping-methodology.md`; many sections share rules. Where this guide is silent, the MVP guide applies.

---

## 1. Purpose

The MVP brief tested the riskiest assumption. The v1 brief plans the product that exists once the assumption survived contact with the first 10 users. The questions this round answers:

1. **What did the MVP teach us?** First-10-users behavior, validation signal, what they asked for, what they paid for, what they complained about. (If the MVP failed to validate the assumption, you don't write a v1 — you go back to discovery.)
2. **What goes in v1?** The MVP must-haves stay; the deferred could-haves become candidates; the v1 also adds whatever the first-10-users feedback demands. The result is wider scope than MVP — multi-week build instead of multi-day, typically.
3. **What's the design path?** The MVP almost always ships with **generic-but-unique** design (handled directly in code per agent-skills `frontend-ui-engineering`). v1 is where the question of engaging a **professional UI/UX designer** gets a real answer. The design-path picker happens here, not at `/scope-mvp` time.
4. **What's the pricing?** The MVP shipped at some price (recorded in the validation report's `Chosen price` section or in the brief's `priced-at:` frontmatter). v1 is the moment to ask whether that price still holds given real-user signal — and to optionally invoke `/reprice <slug>` if it doesn't.

A v1 brief is **not** a marketing launch plan — it's a build brief. Marketing/launch sequencing belongs to `/ship-app` and (later) a launch checklist.

---

## 2. Preconditions — when /scope-v1 is allowed

The user can run `/scope-v1 <slug>` when:

1. **An MVP brief exists** at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md` with `status: shipped`.
2. **The riskiest assumption has been validated** by the first-10-users round. The MVP brief's success criterion was met (or substantially met — call that out and proceed if so).
3. **The user has decided to invest in v1.** Not every shipped MVP becomes a v1. If first-10-users showed the assumption held *but the segment is too small to scale to* or *the pricing math doesn't work*, the right call is to retire the MVP and pick a different card, not write a v1.

If any precondition fails, `/scope-v1` stops and surfaces what's missing — the user can override (rare) but the default is "you're scoping prematurely."

---

## 3. Inputs

To scope a v1, the main Claude assembles:

| Input | Source |
|---|---|
| The MVP brief | `<web-apps\|mobile-apps\|desktop-apps>/<slug>/MVP.md` |
| The validation report (for chosen price + open questions for MVP scoping) | `market-research/<run-id>/validation-<slug>.md` |
| The scoping report (for prior reviewer notes) | `market-research/<run-id>/scoping-<slug>.md` |
| BUILD_STATUS.md (for what shipped, what got cut, history) | `<web-apps\|mobile-apps\|desktop-apps>/<slug>/BUILD_STATUS.md` |
| Audit-log build milestones for this product | `python3 scripts/audit_log.py list --type build-milestone` filtered to the slug |
| First-10-users feedback | The user's notes (often in `<product>/notes/` or surfaced verbatim into the v1-scoping conversation) — if the user hasn't captured these, `/scope-v1` asks them to summarize before the brief gets drafted |
| Any post-MVP reprice | `market-research/<run-id>/validation-<slug>.md` § Reprice blocks (if `/reprice` was run between ship and v1) |

The user provides the first-10-users feedback. If they wave it off ("they loved it, no feedback needed"), `/scope-v1` insists on at least a one-line per-user summary — running v1 with no user signal is the strongest predictor of building the wrong thing at v1.

---

## 4. The design-path picker

This is the centerpiece of v1 scoping and the question the user most often defers at MVP time.

At `/scope-mvp`, the user picked one of:

- **(a) Generic but unique design** — handled in code via agent-skills' `frontend-ui-engineering`. The default for MVPs because the goal was validating the assumption, not the design. (Most MVPs in this workspace pick this.)
- **(b) Full design phase** — `/research-design` → `/draft-design-brief` → human designer → handoff → build. The MVP shipped with this only when distinctiveness was load-bearing for validation itself.

At `/scope-v1`, the user picks one of three paths:

### 4.1 Path A — Continue generic design

The v1 keeps the existing UI patterns. No designer engagement. Build adds the new must-haves directly into the existing codebase, applying the same `frontend-ui-engineering` principles already in use. Tokens (palette, type) come from what was set in the MVP code; the v1 may refine them but does not re-architect them.

**When this is the right pick:**
- The MVP's segment doesn't differentiate on visual polish (developer tools, internal SMB tools, prosumer utilities where function dominates form).
- The user is comfortable building further on the existing UI conventions and doesn't expect designer-level differentiation to move the needle.
- Budget / timeline constraints make pro-designer engagement non-viable in this round.

### 4.2 Path B — Engage a professional UI/UX designer for the v1

The v1 routes through Phase 3 in `CLAUDE.md`: `/research-design <slug>` → user picks a visual direction → `/draft-design-brief <slug>` → human designer produces Figma → handoff capture (`tokens.json`, `screenshots/`, `assets/`) → v1 build proceeds **driven by the handoff** (per `guides/ui-ux/design-handoff-methodology.md`).

**When this is the right pick:**
- The product's segment cares about polish (consumer apps, design-led tools, anything in a category where the incumbent's UX is the moat).
- First-10-users feedback included visual / interaction comments that the generic-design pass can't easily address.
- The user wants the product to look like a real v1, not a prototype.

**Important sequencing:** if Path B is picked, `/scope-v1` ends after drafting `V1.md` with `design-path: pro-designer-engaged` recorded. The next command is `/research-design <slug>` — the v1 build does **not** start until the handoff lands. Skipping the design phase to "start building now" after picking Path B is a defeat-the-purpose move.

### 4.3 Path C — Hybrid (light refresh, keep generic)

A middle path: keep generic-design, but apply a polish pass — refined palette, refined typography, a couple of high-impact custom UI patterns (a distinctive auth screen, a signature dashboard card, a memorable empty-state illustration). No formal designer engagement, but more effort than Path A.

**When this is the right pick:**
- The product's segment cares about polish but not at the level that justifies a designer engagement.
- The user has visual taste they want to express directly.
- A lightweight `guides/ui-ux/design-research-methodology.md` pass without the full brief and handoff would be enough to anchor the polish (`/research-design --light` invocation — drafts the reference landscape + visual direction options without producing a full brief).

Path C is the most workspace-specific choice — it's the one the workspace defaults expect when generic-MVP-design proved sufficient for validation but the v1 wants modest visual investment without designer overhead.

---

## 5. The v1 brief (V1.md format)

Use this template at `<web-apps|mobile-apps|desktop-apps>/<slug>/V1.md`:

```markdown
---
slug: <slug>
status: in-v1-scoping
brief-version: v1
parent-mvp: MVP.md
design-path: <not-yet-chosen | generic-continued | pro-designer-engaged | hybrid-light-refresh>
priced-at: <$amount / unit / interval — copied from validation report's Chosen price, can be overridden during /scope-v1>
pricing-strategy: <option-name from validation report or "user-override">
stack: <copied from MVP unless explicitly changing>
date-scoped: <YYYY-MM-DD>
---

# v1 Brief: <Product Name>

## What the MVP taught us
<2-4 paragraphs synthesizing first-10-users behavior. Citable: link to BUILD_STATUS.md history entries, audit-log milestones, or specific user notes.>

## Validation signal — was the riskiest assumption confirmed?
<One paragraph. Yes / partially / no. If no, /scope-v1 should not have proceeded — go back to discovery instead.>

## Carried must-haves (from MVP, still in v1)
- ...

## New must-haves (added based on first-10-users signal)
- <feature> — because <which user(s) asked for it / which assumption it tests / which retention metric it improves>
- ...

## Could-haves (deferred to v2)
<Anything the user is tempted to put in v1 but isn't actually needed for v1's success criterion. Listing them here prevents scope creep mid-build.>

## Won't-haves (explicitly out of v1)
<Things you've decided NOT to do. Re-read this when you catch yourself adding "just one more thing".>

## Design path (picked at /scope-v1 time)

**Chosen:** <generic-continued | pro-designer-engaged | hybrid-light-refresh>

**Rationale:** <one paragraph naming the segment, the relevant user feedback, the budget/timeline trade-off.>

**Next step driven by this pick:**
- generic-continued → `/start-build <slug>` (reads V1.md)
- hybrid-light-refresh → `/research-design <slug> --light` first, then `/start-build <slug>`
- pro-designer-engaged → `/research-design <slug>` → `/draft-design-brief <slug>` → human designer → handoff → `/start-build <slug>`

## Pricing path (revised or carried)

**Carried price from MVP:** <copied from validation report's Chosen price>

**Repricing decision:** <kept as-is | revised via /reprice — see market-research/<run-id>/validation-<slug>.md § Reprice block>

If pricing is being revised in this round, run `/reprice <slug>` BEFORE finalizing V1.md so the new price lands in the frontmatter.

## Stack
<Copied from MVP. Changing stack at v1 is exceptional — if proposing it, name the specific MVP-time learning that forced the change.>

## Infrastructure decisions (v1 deltas only)
<What changes from MVP? E.g., "moving from SQLite to Postgres because first-10-users hit concurrent-write contention" / "adding background jobs for the new digest feature" / "introducing a CDN for the new image-heavy gallery".>

## Effort estimate

**Cadence assumption:** Claude writes the code; user follows along daily (~1-2 hours/day for review, decisions, local testing).

| Scenario | Time to v1-ready |
|---|---|
| **Daily follow-along** (workspace default) | <N> days to ~3 weeks (typical for v1 scope) |
| **With breaks or iterations** | <N> weeks |
| **External gating** (Google OAuth verification, App Store review, payment-processor approval, designer turnaround if Path B/C) | <N> weeks to months |

For Path B (pro designer), the designer turnaround (typically 2-6 weeks) is usually the dominating gating step.

Top 3 effort risks
  1. ...
  2. ...
  3. ...

## Stack stretches
<Anything in v1 that the user has NOT shipped in production before. v1 can tolerate more than MVP — but aim for ≤2 stretches.>

## Carried open questions from MVP scoping
<Items from MVP.md or scoping-<slug>.md that were deferred. Resolve or re-defer here.>

## New open questions to monitor during v1 build
- ...
```

---

## 6. Reviewers

v1 scoping is reviewed by the **same two reviewers as MVP scoping** — same personas, same lens, but the input is `V1.md` instead of `MVP.md`:

- **`product-scope-reviewer`** — is the v1 scope honest? Do each of the new must-haves trace to citable user signal from the first-10-users round, not founder enthusiasm?
- **`code-reviewer`** (from `external/agent-skills/agents/`) — is the architecture sound for the wider v1 scope? Does the existing MVP code accommodate the new features without re-architecting?

The two reviewers run in parallel via the custom-subagent invocation pattern in `CLAUDE.md`, same as `/scope-mvp`.

**Additional v1-specific tests the reviewers run:**

- **product-scope-reviewer** at v1: are any *new must-haves* dressed-up wishlist items rather than user-signal-backed features? The MVP-scope review asked the same thing about the MVP must-haves; v1 has more rope because the assumption is validated, but the discipline is the same.
- **code-reviewer** at v1: does extending the existing MVP codebase compromise architecture, or is a small re-architecture justified before adding the new must-haves? Be honest — sometimes the MVP code is a sketch and v1 should rewrite a layer.

Output: each reviewer returns the locked verdict format from `idea-validation-methodology.md` §5.

---

## 7. The scoping report

Each `/scope-v1` run produces one report at `market-research/<run-id>/scoping-v1-<slug>.md` (note the `-v1-` infix to distinguish from the original MVP scoping report at `market-research/<run-id>/scoping-<slug>.md`).

It contains, in order:

1. **MVP brief snapshot** at the moment v1 scoping ran (so the report stays meaningful if MVP.md is later edited).
2. **V1 brief snapshot** as produced by `/scope-v1`.
3. **First-10-users feedback summary** as captured during scoping.
4. **Reviewer verdicts** — both, full.
5. **Integration summary** — combined verdict + notes + conflicts.
6. **Decision** — populated by the user (advance / revise / pause v1 plans / kill the product) with a one-paragraph reason.
7. **Open questions for v1 build** — extracted from "What I could not verify" sections.

---

## 8. Verdict integration and outcomes

| Combination | Action |
|---|---|
| 2 × APPROVE | Advance V1.md to `status: green-lit-to-build` once user signs off. **The next-step routing depends on the design-path pick** in V1.md: `/research-design` (Path B), `/research-design --light` (Path C), or `/start-build` (Path A). |
| Any mix of APPROVE and APPROVE-WITH-NOTES | Summarize the notes. Present to the user. On approval, advance with notes carried forward. |
| Any REJECT | Do not advance. The user decides: kill v1 plans (rare — usually means the assumption didn't actually hold), revise the brief (most common), or override (rare). |

If the user picks Kill at v1 scoping (i.e., decides to retire the product), append a `card-kill` audit-log entry per `CLAUDE.md § Audit log` (mirrors the MVP-time kill convention) and update both `MVP.md` and `V1.md` status to `killed`.

---

## 9. Handoff to build

Once V1.md is `green-lit-to-build` and the design path is settled:

| Design path | Next command |
|---|---|
| **Path A — generic-continued** | `/start-build <slug>` (reads V1.md, picks up where the MVP build left off, expanding the codebase) |
| **Path C — hybrid-light-refresh** | `/research-design <slug> --light` produces a lightweight design-direction reference (no full brief, no designer handoff). Then `/start-build <slug>` reads V1.md AND the light reference. |
| **Path B — pro-designer-engaged** | `/research-design <slug>` (full) → `/draft-design-brief <slug>` → human designer → handoff capture per `guides/ui-ux/design-handoff-methodology.md` → `/start-build <slug>` reads V1.md AND the handoff. |

The build orchestrator (`senior-software-engineer` via `/start-build`) auto-detects which brief is current. If both `MVP.md` (status `shipped`) and `V1.md` (status `green-lit-to-build`) exist, the orchestrator picks `V1.md` and treats the MVP code as the starting point to extend.

---

## 10. What v1 scoping does *not* do

- **It does NOT replace `/research-design`.** When Path B or Path C is picked, design research is a separate downstream phase. `/scope-v1` is the gate, not the work.
- **It does NOT re-pick the stack** unless an MVP-time learning forced the change (rare; if so, name the learning explicitly in the brief).
- **It does NOT re-run validation.** If the MVP shipped and the assumption held, validation is done for this card. If the assumption *didn't* hold, the right call is to go back to `/discover` for a new card, not to write a v1 brief.
- **It does NOT plan v2.** Could-haves go in the v1 brief; they get scoped at the v2 round (which doesn't have a slash command yet; this guide will get a §11 when that round is first encountered).
