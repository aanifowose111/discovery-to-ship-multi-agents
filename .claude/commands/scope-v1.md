---
description: Draft the v1 brief for a shipped MVP — the polished, feature-complete build that lives past first-10-users validation. Asks the user to pick the design path (claude-led-continued / hybrid-light-refresh / pro-designer-engaged), captures first-10-users feedback, drafts V1.md at the product folder, and invokes the same two reviewers as /scope-mvp. Per guides/product/v1-scoping-methodology.md.
argument-hint: <slug>
---

You are about to scope the v1 of a shipped product. Follow the methodology in @guides/product/v1-scoping-methodology.md exactly. This is the **second scoping pass** in the pipeline — the first was `/scope-mvp` (assumption-validation MVP), this is for the polished v1 that lives past it.

**Arguments:** `$ARGUMENTS` — the product slug. An MVP brief must exist at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md` with `status: shipped`.

### Inputs to read before drafting

1. **Locate the MVP brief.** Check `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, `desktop-apps/<slug>/MVP.md`. Stop if none found ("Run `/scope-mvp <slug>` first" — but check the wording: if no `MVP.md` exists, this is a brand-new product, not a v1 candidate).

2. **Verify preconditions** per `v1-scoping-methodology.md` §2:
   - MVP brief `status` is `shipped` (not `building`, `in-scoping`, etc.). If not, surface: "MVP for `<slug>` is `<current-status>`, not `shipped`. /scope-v1 assumes the MVP has shipped and been validated. Continue anyway?" via `AskUserQuestion` — default to cancel.
   - The riskiest assumption was validated. Ask the user directly: "Was the MVP's riskiest assumption validated by the first-10-users round?" If no, surface: "Then v1 scoping is premature — go back to `/discover` for a different card. Continue anyway?" — default to cancel.

3. **Read the supporting artifacts** (per §3 of the methodology guide):
   - `<slug>'s` MVP.md (full).
   - `market-research/<run-id>/validation-<slug>.md` (extract `Chosen price`, open questions for MVP scoping).
   - `market-research/<run-id>/scoping-<slug>.md` (prior scope-reviewer notes).
   - `<product-folder>/BUILD_STATUS.md` (what shipped, what was cut, history).
   - Audit-log build milestones for this slug: `python3 scripts/audit_log.py list --type build-milestone | grep -i "<slug>"`.

4. **Resolve `<run-id>`** from the MVP brief's `parent-run-id:` frontmatter or from the path of any sibling artifact in `market-research/*/`.

### Do

#### Step 1 — Capture first-10-users feedback

Ask the user to summarize what the first-10-users round taught them. Use `AskUserQuestion` only for the format choice; the actual summary is free-text:

> The MVP shipped to first 10 users. What did the round teach? Reply in your next message with **at least a one-line per-user summary** (their role, what they did with the product, what they asked for or complained about). If you don't have notes per user, summarize the aggregate signal — but please don't wave it off; v1 built without user signal is the strongest predictor of building the wrong thing.

Wait for the user's reply. If their reply is fewer than three sentences AND mentions no specific user action / quote / metric, push back once: "That sounds like a gut feel rather than user signal. Could you share one specific thing a user did, said, or asked for?" Then proceed with whatever they share — don't gate further.

Capture the feedback verbatim into a scratch variable; it'll go in V1.md `## What the MVP taught us` and in the scoping report.

#### Step 2 — Design-path picker

Use `AskUserQuestion` to present the three paths per the methodology guide §4:

> The MVP shipped with **<look up MVP's `design-path:` — claude-led / pro-designer-engaged>**. For v1, you pick the design path. Three options:
>
> **(a) Claude-led continued** — continue the claude-led path. Re-run `/research-design` (refreshed for v1 surfaces + first-10-users feedback) → re-draft `DESIGN_SPEC.md` → build. No external designer engaged. Fastest of the three. Good when polish doesn't differentiate (dev tools, internal SMB tools) or budget/timeline forbids designer engagement.
>
> **(b) Engage a professional UI/UX designer** — full Phase 3 (`/research-design` → `/draft-design-brief` → designer → handoff) before v1 build starts. Right when polish differentiates in your segment (consumer / design-led / category-leader incumbent).
>
> **(c) Hybrid — light refresh** — keep the claude-led path, but add a polish pass: refined palette, refined typography, 2-3 distinctive UI patterns. No formal designer engagement. Middle path; respects budget while investing in look.

Wait for the user's pick. Record it as `design-path: claude-led-continued | hybrid-light-refresh | pro-designer-engaged` in V1.md frontmatter.

#### Step 3 — Pricing decision

Surface the current `priced-at:` value from validation-<slug>.md (under `Chosen price`). Ask via `AskUserQuestion`:

> Your MVP shipped at **<current price>** (strategy: <prior strategy>). For v1:
>
> - **(a) Keep this price** — proceed with V1.md drafting using this price.
> - **(b) Reprice** — run `/reprice <slug>` BEFORE finalizing V1.md (recommended if first-10-users showed price friction or comparables have shifted). You can re-enter `/scope-v1 <slug>` after.

If (b), stop and tell the user: "Run `/reprice <slug>` first, then re-enter `/scope-v1 <slug>`. I'll stop now."

If (a), proceed with the current price.

#### Step 4 — Surface new must-haves

Read the MVP's `## Could-haves (deferred to v2)` section. Show them to the user and ask:

> Your MVP deferred these to v2:
>   <list of MVP's could-haves>
>
> And your first-10-users feedback suggested:
>   <Claude's read of what the feedback implies>
>
> Which of these should be **new must-haves in v1**? You can pick some, add new ones not in either list, or send some back to "deferred to v2".

Capture the agreed-upon new must-haves list.

#### Step 5 — Draft V1.md

Write `V1.md` to the same product folder as MVP.md (`<web-apps|mobile-apps|desktop-apps>/<slug>/V1.md`) using the format in `v1-scoping-methodology.md` §5. Populate:

- Frontmatter: `slug`, `status: in-v1-scoping`, `brief-version: v1`, `parent-mvp: MVP.md`, `design-path: <chosen>`, `priced-at: <kept or revised>`, `pricing-strategy: <copied>`, `stack: <copied from MVP>`, `date-scoped: <today>`.
- `## What the MVP taught us` — paragraph synthesis of the first-10-users feedback you captured in step 1. Cite specific user notes where available.
- `## Validation signal — was the riskiest assumption confirmed?` — one paragraph.
- `## Carried must-haves` — read MVP's must-haves; ask user "any to drop?" Default: keep all.
- `## New must-haves` — the agreed list from step 4. Tag each: `<feature> — because <user-signal-source>`.
- `## Could-haves` — what was discussed but didn't make v1.
- `## Won't-haves` — explicit cuts.
- `## Design path` — the picked path, rationale (one paragraph), and the next-step routing block per the methodology guide.
- `## Pricing path` — carried or revised; if revised, link to the validation report's Reprice block.
- `## Stack` — copied from MVP. If user explicitly wants to change stack, drill in (per methodology §10).
- `## Infrastructure decisions (v1 deltas only)` — what changes from MVP.
- `## Effort estimate` — use the three-scenario table per `mvp-scoping-methodology.md` §5 and `v1-scoping-methodology.md` §5. For Path B (pro designer), name the designer turnaround as a dominating external gate.
- `## Stack stretches`, `## Carried open questions from MVP scoping`, `## New open questions to monitor during v1 build` — fill from inputs.

#### Step 6 — Invoke the two reviewers in parallel

Same pattern as `/scope-mvp`. Use the custom-subagent invocation pattern in `CLAUDE.md`. Two parallel Agent calls:

```
Agent({
  subagent_type: "general-purpose",
  description: "v1 scope review for <slug>",
  prompt: "You are about to act as the product-scope-reviewer. Step 1: read .claude/agents/product-scope-reviewer.md in full and treat its body as your role, lens, process, evidence standards, rationalizations to refuse, red-flag rules, and output format. Step 2: read the v1 brief at <path-to-V1.md>, the methodology guides guides/product/v1-scoping-methodology.md and guides/product/mvp-scoping-methodology.md, and CLAUDE.md for founder context. Step 3: apply your v1-specific tests per v1-scoping-methodology.md §6 — specifically, are the new must-haves user-signal-backed or wishlist items? Step 4: return your output in the locked verdict format from idea-validation-methodology.md §5."
})

Agent({
  subagent_type: "general-purpose",
  description: "v1 code/architecture review for <slug>",
  prompt: "You are about to act as the code-reviewer (the 5-axis Senior Staff Engineer persona). Step 1: read .claude/agents/code-reviewer.md in full and treat its body as your role. Step 2: read the v1 brief at <path-to-V1.md>, the MVP brief at <path-to-MVP.md>, the existing codebase at <product-folder>, BUILD_STATUS.md, and CLAUDE.md. Step 3: apply your v1-specific test per v1-scoping-methodology.md §6 — does extending the existing MVP codebase compromise architecture, or is a small re-architecture justified before adding the new must-haves? Step 4: return your output in the locked verdict format from idea-validation-methodology.md §5."
})
```

Wait for both verdicts.

#### Step 7 — Write the scoping report

Write `market-research/<run-id>/scoping-v1-<slug>.md` (note the `-v1-` infix) per `v1-scoping-methodology.md` §7. Include MVP snapshot, V1 snapshot, first-10-users feedback summary, both verdicts, integration summary. Leave `Decision` empty for the user.

### Stop here — user checkpoint
After writing the report, **stop**. Do not advance V1.md to `green-lit-to-build`. Show the user:

> V1 brief at `<path-to-V1.md>`. Scoping report at `market-research/<run-id>/scoping-v1-<slug>.md`.
>
> Combined verdict: <APPROVE / APPROVE-WITH-NOTES / REJECT>
> Notes: <summary>
>
> Your call:
> - Advance V1 to `green-lit-to-build`
>   - Design path is **<chosen>**, so next step will be:
>     - `claude-led-continued` → `/research-design <slug>` (re-research for v1) → `/draft-design-spec <slug>` → `/start-build <slug>` (reads V1.md, extends MVP codebase, builds from refreshed `DESIGN_SPEC.md`)
>     - `hybrid-light-refresh` → `/research-design <slug> --light` first, then `/start-build`
>     - `pro-designer-engaged` → `/research-design <slug>` (full) → `/draft-design-brief <slug>` → designer → handoff → `/start-build`
> - Revise the brief and re-review
> - Pause v1 plans (e.g., gather more user signal first)
> - Retire the product (rare — usually means the assumption didn't actually hold; revisit)

Update V1.md's `status` and the scoping report's *Decision* section only after the user has decided.

**If the user picks Retire the product**, append a `card-kill` audit-log entry: `python3 scripts/audit_log.py add card-kill "Retired product <slug> at v1 scoping. Reason: <one-line user reason>."`. Also update MVP.md status to `killed` (mirror with V1.md → `killed`). Note that this is an unusual outcome for a `shipped` MVP — call out the rarity to the user when offering the option.

### Important — no auto-actions

- **NEVER** chain into `/research-design`, `/draft-design-brief`, or `/start-build` automatically. After the user signs off on `green-lit-to-build`, surface the next command for them to invoke — do not invoke it yourself.
- **NEVER** advance V1.md status without the user's pick.
- **NEVER** skip the first-10-users feedback step. The whole point of v1 is responding to real user signal; building v1 from imagination is the failure mode this command exists to prevent.
