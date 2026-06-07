---
description: Rework an existing idea card (and optionally its downstream MVP brief and V1 brief) based on user-described changes. Proposed changes land in TEMP files (`<slug>-temp.md`, `MVP-temp.md`, `V1-temp.md`); the originals are NEVER overwritten until the user explicitly commits the rework after reviewers pass (or after the user overrides a REJECT with explicit acknowledgment of the consequences). Audit-logged as `rework-applied`.
argument-hint: <slug> <free-text description of the changes you want>
---

You are about to rework an existing idea card and/or its downstream artifacts (MVP brief, V1 brief if present) based on user-described changes. **The original files MUST NEVER be overwritten until the user explicitly commits the rework.** Every proposed change goes into a TEMP file. The user gets to inspect, refine, and override before any merge happens.

This command exists because reworking an idea by hand-editing files and re-invoking reviewers is error-prone — the original gets clobbered before the user has seen the new verdicts, and overrides happen silently with no record. `/rework` separates **proposal** from **commit** so the user can iterate safely.

**Arguments:** `$ARGUMENTS` — parse as `<slug> <description-of-changes>`. The slug must exist as an active card at `ideas/<run-id>/<slug>.md` (NOT killed). The description is free-text — Claude will read it carefully and apply it section-by-section.

### Inputs to read before starting

1. **Locate the active card** with:
   ```bash
   find ideas -name "<slug>.md" -not -path "*/killed/*" 2>/dev/null
   ```
   Stop if not found ("No active card for `<slug>`. If it was killed, run `/revive-card <slug>` first. If you want a brand-new card with this slug, run `python3 scripts/new_idea_card.py` instead.").

2. **Extract `<run-id>`** from the resolved path.

3. **Read the full card.** Note `status`, `priced-at`, `pricing-strategy`, `validation-report` (if set).

4. **Locate downstream artifacts** (any combination may exist):
   - Validation report: `market-research/<run-id>/validation-<slug>.md`
   - Scoping report: `market-research/<run-id>/scoping-<slug>.md`
   - MVP brief: check all three of `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, `desktop-apps/<slug>/MVP.md` (only one will exist if any)
   - V1 brief: `<stack>-apps/<slug>/V1.md`
   - BUILD_STATUS.md: `<stack>-apps/<slug>/BUILD_STATUS.md` (informational only — not reworked, but its existence affects warnings)

5. **Read every artifact found** — you need the full picture to apply the rework correctly. Always check existing content before deciding targeted edit vs full overwrite.

6. **Parse `BUILD_STATUS.md` if present** to determine the build state:
   - Walk the file's checklist sections and count subsystems by status marker (`[ ]` not-started, `[>]` in-progress, `[x]` completed).
   - Record the mapping `{subsystem_name → current_state}` as `<BUILD_STATE>` (used by Steps 2.5, 8, and 9).
   - Determine the **build-state label**: `not-started` (no BUILD_STATUS.md or all `[ ]`), `in-progress` (at least one `[>]` or `[x]`), `shipped` (per MVP.md frontmatter `status: shipped`), or `v1-in-flight` (V1.md exists + status not `shipped`).

### Do

#### Step 1 — Confirm scope of rework

Surface what was found + the user's change description. **If `<BUILD_STATE>` is `in-progress` or `shipped`, surface a build-state banner BEFORE the scope picker** — the user needs to know the rework will impact already-written code or already-shipped artifacts:

If `<BUILD_STATE>` is `in-progress`:

> ⚠ **Build in progress for `<slug>`.** `BUILD_STATUS.md` shows the following completed/in-progress subsystems:
>
> - `<subsystem>` — `[x]` (owner: `<persona>`, completed `<date>`)
> - `<subsystem>` — `[>]` (owner: `<persona>`, started `<date>`)
> - ...
>
> The rework's change description may affect some of these. After commit (Step 9), you'll have the option to flip affected `[x]` subsystems back to `[>]` so the next `/start-build` re-engages the relevant specialists. **Code is NOT automatically modified** — `/rework` is markdown-only; flipping a subsystem is the signal that revisit work is owed. Proceed?

If `<BUILD_STATE>` is `shipped`:

> ⚠ **MVP is shipped for `<slug>`.** Reworking the MVP brief retroactively is *rewriting history* — the brief was the contract for what users actually saw. Consider running **`/scope-v1 <slug>`** instead, which is the canonical path for capturing post-MVP changes as the V1 brief without invalidating the historical MVP record.
>
> If you still want to rework the MVP (rare — e.g., correcting a documentation error), proceed below. The rework will be logged with this warning preserved in the `rework-applied` audit-log entry for future visibility.

Use `AskUserQuestion` to confirm before proceeding (Proceed / Switch to `/scope-v1` / Cancel).

Then surface the scope picker (use `AskUserQuestion`):

> Rework scope for `<slug>` (run-id: `<run-id>`):
>
> - Idea card: `ideas/<run-id>/<slug>.md` (status: `<status>`)
> - MVP brief: `<path>` (status: `<status>`) — [show this row only if MVP exists]
> - V1 brief: `<path>` (status: `<status>`) — [show this row only if V1 exists]
> - BUILD_STATUS.md: `<path>` (build state: `<BUILD_STATE>`) — [show only if exists; informational]
>
> Your requested changes (verbatim):
> > <CHANGES_TEXT>
>
> What should be reworked?
> - **(a) Card only** — useful when only the idea claims changed, not the brief
> - **(b) Card + MVP brief** — both rewritten/edited; MVP needs re-scoping after
> - **(c) Card + MVP + V1** — full chain (only if V1 exists)
> - **(d) Cancel** — stop, no changes

If only the card exists (no MVP yet), skip this picker and default to (a).

If the change description plainly only affects one layer, recommend the corresponding option as "(Recommended)".

#### Step 2 — Decide targeted edit vs full rewrite for each artifact

For each chosen artifact, read the existing content carefully and decide the modification strategy:

| Modification | When | Effect |
|---|---|---|
| **Targeted edit** | Change is localized to one or two sections (e.g., "revise distribution hypothesis", "add a new must-have", "update the pricing strategy") | Edit specific sections in the temp file, preserve everything else verbatim |
| **Full rewrite** | Change is structural (e.g., "switch the segment from solo founders to small agencies", "merge two must-haves and rethink the riskiest assumption", "change the stack") | Rewrite the temp file end-to-end, carrying frontmatter forward |

**Disallowed changes** — refuse and explain to the user:
- Changing the **slug** or **run-id** in the card frontmatter. Slugs are workspace identifiers; if the user wants a different slug, they should kill the card and create a new one with `python3 scripts/new_idea_card.py`.
- Changing **`date-captured`** (historical).

Report your decisions to the user before proceeding:

> Modification strategy:
> - Card (`ideas/<run-id>/<slug>.md`): **targeted edit** to sections [Problem, Proposed solution] (rationale: ...)
> - MVP (`<path>`): **full rewrite** (rationale: stack change cascades through every section)
>
> Proceed? — Yes / Revise plan / Cancel

#### Step 2.5 — Feasibility consultation (optional; recommended for structural changes)

For substantive changes (segment shift, stack change, new must-have spanning multiple subsystems, riskiest-assumption shift, addition of real-time / background-job / external-API capability), invite the orchestrator's advisory panel BEFORE drafting any temp file. The goal is to make the proposal sharper, surface simpler alternatives, and flag hidden risks early — when changing the proposal is cheap.

For minor changes (rewording a section, revising a pricing strategy, swapping a distribution channel), this step is overkill — skip it.

Use `AskUserQuestion`:

> Your proposed change for `<slug>` is:
>
> > `<one-line summary of the change>`
>
> Want a feasibility consultation from the senior engineers before drafting the rework temps?
>
> - **(a) Yes — consult** (Recommended for structural changes)
>   - The orchestrator (`senior-software-engineer`) brings in the right specialists (system-design always; plus database / backend / frontend / desktop / qa / devops / security as the change implies) in **consulting mode** per `senior-software-engineer.md` § Consulting mode. Output is a structured advisory note covering feasibility, suggested approach, simpler alternatives, and hidden risks. The user can revise the change description after seeing the advice; nothing is committed.
> - **(b) Skip — go straight to temp creation**
>   - Use when the change is small, well-understood, or you've already done the design thinking offline.

On (a): invoke `senior-software-engineer` in consulting mode via the custom-subagent invocation pattern in `CLAUDE.md`. **If `<BUILD_STATE>` is `in-progress`, the prompt MUST instruct the orchestrator to additionally produce a Subsystem-impact map** as part of the consultation output:

```
Agent({
  subagent_type: "general-purpose",
  description: "Rework feasibility consultation for <slug>",
  prompt: "You are about to act as the senior-software-engineer in CONSULTING MODE (per .claude/agents/senior-software-engineer.md § Consulting mode — read this section in full first). Step 1: read .claude/agents/senior-software-engineer.md in full and treat its body as your role. Step 2: read the user's proposed change: '<verbatim change description>'. Step 3: read the existing artifacts at <list of paths> to ground the consultation. Step 4: decide which specialists to bring in (each specialist persona file has its own '## Consulting mode' section describing their advisory behavior; invoke them via the same custom-subagent pattern with a consulting-mode prompt). Step 5: if BUILD_STATUS.md shows in-progress build state (build-state-label: <BUILD_STATE>, current subsystems: <BUILD_STATE map serialized>), ALSO produce the 'Subsystem impact' map per your § Consulting mode (output shape) — a table with columns Subsystem / Current state / Expected post-rework state / Reason. Step 6: assemble all notes into the consultation output shape defined in your § Consulting mode."
})
```

Surface the consultation output to the user. Then offer via `AskUserQuestion`:

- **Proceed with the original change description** — go to Step 3 with the user's original change.
- **Proceed with the synthesis recommendation** — go to Step 3 using the orchestrator's recommended path instead of the user's original.
- **Revise the change description** — user types a refined description; Step 2.5 can re-run if they want another consultation.
- **Cancel the rework** — no temps created.

#### Step 3 — Create temp files with proposed changes

For each chosen artifact, create a temp next to the original:

| Original | Temp |
|---|---|
| `ideas/<run-id>/<slug>.md` | `ideas/<run-id>/<slug>-temp.md` |
| `<stack>-apps/<slug>/MVP.md` | `<stack>-apps/<slug>/MVP-temp.md` |
| `<stack>-apps/<slug>/V1.md` | `<stack>-apps/<slug>/V1-temp.md` |

Apply the modification strategy (targeted edit OR full rewrite) to each temp. The temps live in gitignored personal-data folders — no risk of accidentally committing them.

**On the card temp's frontmatter:** keep `slug`, `run-id`, `date-captured`, `source`, `territory` unchanged. Other fields may be updated per the rework.

Show the user a brief summary of what was changed in each temp (one-line per section that changed). The user can request adjustments before reviewers run.

#### Step 4 — Run reviewers against the temps

Based on which temps were created, run the corresponding reviewer set **in parallel** per the methodology guides:

| Temp | Reviewers (in parallel) | Per |
|---|---|---|
| `<slug>-temp.md` | `product-viability-reviewer`, `product-competition-reviewer`, `market-segment-reviewer`, `product-pricing-reviewer` | `guides/product/idea-validation-methodology.md` §4 |
| `MVP-temp.md` | `product-scope-reviewer`, `code-reviewer` | `guides/product/mvp-scoping-methodology.md` §7 |
| `V1-temp.md` | `product-scope-reviewer`, `code-reviewer` (v1-specific tests) | `guides/product/v1-scoping-methodology.md` §6 |

Use the custom-subagent invocation pattern in `CLAUDE.md`. Each reviewer reads the **TEMP file**, not the original. Pass the original + the change description in the prompt for context — but the reviewer's verdict is on the temp.

Wait for all verdicts.

#### Step 5 — Surface verdicts to the user

Present each verdict clearly:

> Verdicts on the reworked temps:
>
> **Card (`<slug>-temp.md`):**
> - Viability: APPROVE (HIGH) — <one-line summary>
> - Competition: REJECT (HIGH) — <one-line summary>
> - Market-segment: APPROVE-WITH-NOTES (MEDIUM) — <one-line summary>
> - Pricing: APPROVE (MEDIUM) — <one-line summary>
>
> **MVP brief (`MVP-temp.md`):**
> - Scope: APPROVE-WITH-NOTES (HIGH) — <one-line summary>
> - Code/architecture: APPROVE (HIGH) — <one-line summary>

#### Step 6 — Handle each REJECT (suggested approach loop)

For **every** REJECT verdict, surface a suggested approach to get a passing verdict, derived from the reviewer's actual findings:

> ⚠ **Reviewer `<reviewer-name>` rejected `<temp-path>`.**
>
> Reject reason: <full reason from the reviewer's verdict>
>
> Suggested approach to get a passing verdict:
> 1. <strategy 1 — derived from the specific finding the reviewer raised>
> 2. <strategy 2>
> 3. <strategy 3 — if applicable>
>
> Options:
> - **(a) Apply these recommendations to the temp + re-run `<reviewer-name>` only**
> - **(b) Apply custom changes to the temp + re-run `<reviewer-name>` only** (user describes the changes in their next reply)
> - **(c) Override this REJECT** — see consequences explainer below
> - **(d) Cancel the entire rework** — delete all temps, restore nothing

If (a): apply the recommendations to the temp via Edit (or rewrite if structural), re-invoke `<reviewer-name>` only, surface new verdict, loop back to step 6 if still REJECT.

If (b): ask the user "What specific changes?", apply them, re-invoke `<reviewer-name>`, loop.

If (c): jump to step 7 (override flow).

If (d): delete all temp files, log nothing, stop.

#### Step 7 — Override flow (per-reviewer; consequences explainer required)

For each REJECT the user wants to override, surface the consequences explainer:

> ⚠ **Overriding REJECT from `<reviewer-name>` on `<temp-path>`.**
>
> The reviewer rejected because: <reason>
>
> **Potential consequences of proceeding without addressing this:**
>
> - <consequence 1 — specific to this reviewer's lens. Examples:>
>   - Viability override → "External evidence didn't support the problem severity claim. Likely: first 10 users won't articulate the pain the way the card claims; retention will be the canary."
>   - Competition override → "Differentiation story may not survive contact with the market at first-10-users time. Likely: prospects will ask 'how is this different from X?' and you won't have a sharp answer."
>   - Market-segment override → "Segment may be too small / unreachable. Likely: even with perfect execution you can't get to 100 paying users in 90 days through the named channel."
>   - Pricing override → "Price may not survive segment WTP signal. Likely: free-tier users won't convert; trial users churn at the price gate."
>   - Scope override → "MVP scope is too big. Likely: build slips by 2-4x; you ship something that doesn't validate the assumption because too many features blurred the signal."
>   - Code/architecture override → "Technical approach has a known risk. Likely: rebuild required between MVP and v1; first-10-users hit a bug that's expensive to fix in the current architecture."
> - <consequence 2 — what re-surfaces at later phases>
> - <consequence 3 — what a future contributor will see in the audit log>
>
> **Long-term risk:** <one sentence summarizing what this override could cost you in time/money/credibility>
>
> **The audit log will permanently record this override**, including the reviewer, the reject reason, and your justification. Future you (and any forker) will see why you proceeded.
>
> Are you sure?
> - **(a) Yes — override this REJECT** (provide a one-sentence justification — required)
> - **(b) No — go back and address the reject**

If (a): collect the justification, record it for the audit log entry in step 9. Proceed past this reject.

If (b): return to step 6 for this reviewer.

Repeat the override flow for each REJECT being overridden.

#### Step 8 — Final user confirmation before commit

Show the consolidated diff summary:

> **Rework summary for `<slug>`:**
>
> Card changes (`<slug>-temp.md`):
> - <one-line per changed section>
>
> MVP changes (`MVP-temp.md`):
> - <one-line per changed section>
>
> V1 changes (`V1-temp.md`):
> - <one-line per changed section>
>
> Reviewer verdicts (all green or accepted-overridden):
> - <list>
>
> Overrides being applied:
> - **`<reviewer>` on `<temp>`** — justification: "<user's justification>"
>
> What status should the artifacts carry post-rework? (sensible defaults shown; user can override):
> - Card: `triaged` (back to pre-validation — the reworked claims need re-validation via `/validate-card`)
> - MVP: `in-scoping` (back to pre-review — needs re-scoping via `/scope-mvp`)
> - V1: `in-v1-scoping` (back to pre-review — needs re-v1-scoping via `/scope-v1`)

##### Step 8a — Subsystem-impact decision (only if `<BUILD_STATE>` is `in-progress`)

If the build is in progress AND the Step 2.5 consultation produced a Subsystem-impact map (or if the user skipped consultation but the build is in progress — in which case main Claude produces a best-effort map from the change description + `<BUILD_STATE>`), surface it now:

> **Subsystem impact summary** (from `BUILD_STATUS.md`):
>
> | Subsystem | Current | Expected post-rework | Reason |
> |---|---|---|---|
> | <subsystem> | `[x]` | `[>]` | <one-line from consultation> |
> | <subsystem> | `[x]` | `[x]` (no change) | <one-line> |
> | <subsystem> | `[>]` | `[>]` (no change, adjust scope) | <one-line> |
> | <subsystem> | `[ ]` | `[ ]` (no change) | <one-line> |
>
> **What to do with affected subsystems on commit?**
> - **(a) Flip affected `[x]` subsystems back to `[>]`** (Recommended for changes that touch already-completed code) — `BUILD_STATUS.md` History gets an entry per flip noting that the rework triggered the revert. Next `/start-build <slug>` re-engages the relevant specialists against the reworked brief.
> - **(b) Leave subsystem states alone** — User takes responsibility for manually flipping or re-running. Useful when the change is brief-only and doesn't actually need code revisits (e.g., a pricing rework, a distribution-hypothesis revision).

Record the user's pick as `<SUBSYSTEM_FLIP_DECISION>` (one of: `flip` / `leave-alone`). If the user skipped Step 2.5 consultation AND the change description is plainly brief-only (e.g., pricing, distribution channel only), default the recommendation to `leave-alone` and explain why.

##### Step 8b — Final commit confirmation

> Confirm via `AskUserQuestion`:
> - **(a) Commit the rework** — overwrite originals with temps, delete temps, append rework blocks to existing validation/scoping reports, apply subsystem flips per `<SUBSYSTEM_FLIP_DECISION>` (if applicable), append audit-log entry
> - **(b) Revise more before commit** — return to step 6
> - **(c) Cancel** — delete all temps, no changes made

#### Step 9 — Commit (or cancel)

**On (a) Commit:**

1. **Overwrite originals from temps** (atomic per-file):
   ```bash
   mv ideas/<run-id>/<slug>-temp.md ideas/<run-id>/<slug>.md
   mv <stack>-apps/<slug>/MVP-temp.md <stack>-apps/<slug>/MVP.md
   mv <stack>-apps/<slug>/V1-temp.md <stack>-apps/<slug>/V1.md
   ```

2. **Update frontmatter statuses** to the defaults from step 8 (unless user overrode):
   - Card → `status: triaged`
   - MVP → `status: in-scoping`
   - V1 → `status: in-v1-scoping`

3. **Append `## Rework — <YYYY-MM-DD>` blocks to existing reports** (do NOT overwrite the original verdicts):
   - In `market-research/<run-id>/validation-<slug>.md`: append the new reviewer verdicts + any overrides + justifications
   - In `market-research/<run-id>/scoping-<slug>.md`: same
   - Same convention as `/reprice`'s `## Reprice — <date>` block

3a. **Apply subsystem flips to `BUILD_STATUS.md`** if `<SUBSYSTEM_FLIP_DECISION>` is `flip`:
   - For each subsystem in the impact map whose Expected-post-rework column is `[>]` (was `[x]`): edit the BUILD_STATUS.md checklist line to change `- [x]` → `- [>]`. Preserve all other content on the line (owner, artifact path).
   - Append a History entry for each flip: `- <YYYY-MM-DD>: \`[x]\` → \`[>]\` for **<subsystem>** triggered by /rework (audit: <to-be-filled-after-step-4>). Reason: <one-line from impact map>. Requires re-invocation of <persona> against the reworked brief.`
   - Update BUILD_STATUS.md frontmatter `build-status` from whatever it was to `rework-in-progress` so subsequent `/start-build` can detect the state.
   - **Per `guides/product/build-status-methodology.md` § 'Special exception: rework-triggered flips'** — this is the one documented case where main Claude edits BUILD_STATUS.md directly (vs. via the orchestrator persona). The clear History annotation makes the rework trigger auditable.

4. **Append audit-log entry:**
   ```bash
   python3 scripts/audit_log.py add rework-applied "Reworked <slug> (run-id: <run-id>). Affected artifacts: <card|MVP|V1>. Build state at rework: <BUILD_STATE>. Subsystem flips applied: <list of subsystems flipped, or 'none'>. Override(s): <reviewer> ('<justification>'); <reviewer> ('<justification>'). Summary: <one-line summary of the change>."
   ```

5. **If subsystem flips were applied in Step 3a**, edit the BUILD_STATUS.md History entries to substitute the actual audit-log id (returned from Step 4) into the `(audit: <id>)` placeholder.

6. **Print the new audit-log id and a brief result summary.**

**On (c) Cancel:**

1. Delete every temp file created in step 3.
2. Tell the user: "Rework cancelled. No changes were made to any artifact. Temps deleted."

#### Step 10 — Stop with next-step suggestions

> Rework committed for `<slug>` (audit-log id: `<id>`).
>
> - Card status: `triaged` (was `<previous>`)
> - MVP status: `in-scoping` (was `<previous>`)
> - V1 status: `in-v1-scoping` (was `<previous>`)
> - Subsystems flipped: `<list, or 'none'>` — [show only when flips were applied]
> - Build state: `rework-in-progress` — [show only when flips were applied]
>
> Next steps:
> - **`/validate-card <slug>`** — re-validate the reworked card. The four product reviewers will run again on the **committed (now-original)** card. Overrides applied during this rework do NOT carry forward — a fresh validation is independent.
> - **`/scope-mvp <slug>`** — refresh the scoping report against the new MVP content (if MVP was reworked).
> - **`/scope-v1 <slug>`** — refresh v1 scoping (if V1 was reworked).
> - **`/start-build <slug>`** — re-engage the team against the reworked brief. The orchestrator will see the flipped `[>]` subsystems in `BUILD_STATUS.md` and re-invoke the relevant specialists to revisit their work. [show only when flips were applied]
> - **`/consolidate <slug>`** — check alignment across all artifacts (recommended after a structural rework, e.g., a stack or segment change).
> - **`/log type rework-applied`** — view this rework + any past ones in the audit log.

### Important — no auto-actions, no destructive shortcuts

- **NEVER overwrite an original file before user explicit confirm in step 8.** All proposed work is in temp files until commit.
- **NEVER skip the override consequences explainer.** If the user wants to override a REJECT, they must see the consequences and provide a one-sentence justification before proceeding. This is the whole point of the command.
- **NEVER chain into `/validate-card`, `/scope-mvp`, or `/scope-v1` automatically after commit.** Surface them as next steps; the user picks.
- **NEVER allow slug or run-id changes** in the card frontmatter. Slugs are workspace identifiers (per `CLAUDE.md § Slug uniqueness`).
- **If the rework fails partway (e.g., a `mv` fails)**, leave the workspace in a recoverable state and surface the error. Do NOT delete temps if the merge didn't complete.

### Notes

- **Where temps live.** Always next to the original (`ideas/<run-id>/<slug>-temp.md`, `<stack>-apps/<slug>/MVP-temp.md`, `<stack>-apps/<slug>/V1-temp.md`). They're in gitignored personal-data folders, so they never enter git. If the user runs `/rework` and cancels, they're cleanly deleted. If the user runs `/rework` and commits, the originals are overwritten and the temps are removed by the `mv`.
- **What changes when the rework commits.** Frontmatter statuses revert to pre-review state for each affected artifact, because the core claims have changed and they need a fresh review pass. The existing validation/scoping reports stay intact (the rework appends `## Rework — <date>` blocks; nothing in the report's history is erased).
- **The audit log is the durable record.** The `rework-applied` entry includes the slug, run-id, what was affected, any overrides with justifications, and a one-line summary. Pair with `/log type rework-applied` to see the full history.
- **Overrides are forever in the audit log.** Future you, and any forker, will see why an override happened. This is intentional — the override consequences explainer warns the user explicitly that the record is permanent.
- **Why temp files instead of git branches?** Personal-data files (`ideas/`, `<stack>-apps/`) are gitignored. A git branch approach wouldn't help here. Temp files are the right level.
