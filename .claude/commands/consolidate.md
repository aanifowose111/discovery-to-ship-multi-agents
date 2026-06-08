---
description: Check alignment between an idea card, its validation report, its scoping report, its MVP brief, and (if present) its V1 brief — surface every misalignment, ask the user for permission to consolidate (per row or all-at-once), then re-run the relevant reviewers against the consolidated artifacts. The goal is "MVP faithful to scope, scope faithful to idea." Audit-logged as `consolidation-applied`.
argument-hint: <slug>
---

You are about to consolidate the alignment between an idea card and its downstream artifacts. The product pipeline produces multiple linked documents (idea card → validation report → scoping report → MVP brief → V1 brief if present), and over time they can drift — e.g., the MVP brief adds a must-have that doesn't trace to anything in the card, or the card's pricing differs from the MVP brief's `priced-at:`, or the v1 brief's design path doesn't match what was actually shipped at MVP.

This command finds those misalignments, asks the user which to consolidate, applies the consolidation, and then re-runs reviewers to verify the consolidated state still passes.

**Arguments:** `$ARGUMENTS` — the slug. The card must exist at `ideas/<run-id>/<slug>.md` (active, not killed).

### Inputs to read before starting

1. **Locate the card.** Same find pattern as `/rework`: `find ideas -name "<slug>.md" -not -path "*/killed/*"`.
2. **Extract `<run-id>`** from the path.
3. **Read every existing artifact** for this slug:
   - Idea card: `ideas/<run-id>/<slug>.md`
   - Validation report: `market-research/<run-id>/validation-<slug>.md` (if exists)
   - Scoping report: `market-research/<run-id>/scoping-<slug>.md` (if exists)
   - MVP brief: `<stack>-apps/<slug>/MVP.md` (one stack folder; check web/mobile/desktop)
   - V1 brief: `<stack>-apps/<slug>/V1.md` (if exists)

   **Always check current content first** — never assume; reading the artifact tells you what's actually in it.

### Do

#### Step 1 — Run the alignment checks

For each pair of artifacts, evaluate the alignment dimensions below. Record every misalignment found.

##### Card ↔ MVP brief (most common drift)

| Check | What to verify | Misalignment if... |
|---|---|---|
| Must-haves trace to card | Each MVP must-have should map to a claim in the card's *Problem*, *Proposed solution*, or *Distribution hypothesis* sections | A must-have has no traceable origin in the card |
| Success criterion tests the risk | MVP's "Success criterion" should test the card's "Riskiest assumption" (or the top risk from the card's *Top risks / unknowns*) | The success criterion measures something else (vanity metric, easy-to-meet bar) |
| Stack matches the card | MVP's chosen stack should align with the card's *Tech-stack fit* section | The MVP picks a stack the card didn't anticipate (and no rationale in the brief) |
| Pricing match | MVP frontmatter `priced-at:` matches the validation report's `Chosen price` (and the card's frontmatter if set there too) | The numbers diverge |
| Stack stretches honest | MVP "Stack stretches" should include anything the card flagged as a stretch | Card flagged a stretch the MVP doesn't carry forward |

##### Validation report ↔ MVP brief

| Check | What to verify | Misalignment if... |
|---|---|---|
| "What I could not verify" → carried into MVP | Validation reviewer's gaps should be in MVP's *Open questions* or *Carried notes from validation* | A validation gap doesn't appear anywhere in MVP |
| Validation REJECT findings → addressed in MVP | If validation had any REJECT or APPROVE-WITH-NOTES, MVP should explicitly address the concern | MVP silently ignores a validation finding |
| Pricing path | Validation's Chosen price → MVP `priced-at:` | Differ without `/reprice` block explaining the change |

##### Scoping report ↔ MVP brief

| Check | What to verify | Misalignment if... |
|---|---|---|
| Scope reviewer notes addressed | If scoping had APPROVE-WITH-NOTES, MVP should reflect the notes | A note isn't visibly addressed (e.g., scope-reviewer said "auth needs MFA" but MVP says basic auth) |
| Code-reviewer concerns addressed | Same for the code/architecture review | An architectural concern is ignored |

##### Card ↔ V1 brief (if V1 exists)

| Check | What to verify | Misalignment if... |
|---|---|---|
| V1 "Carried must-haves" = MVP must-haves | The carried set should match what MVP actually shipped | V1 carries something MVP doesn't have, or omits something MVP shipped |
| V1 design path picked | V1 frontmatter `design-path` must be one of claude-led-continued / hybrid-light-refresh / pro-designer-engaged | Field is empty or invalid |
| V1 new must-haves trace to feedback | Per `v1-scoping-methodology.md` §3 — each new V1 must-have should cite a specific first-10-users signal | A new V1 must-have has no user-signal source |
| Riskiest-assumption status | V1 should confirm the MVP's riskiest assumption was validated (per §5 of the v1 guide) | V1 was scoped despite "no" or unclear validation signal |

#### Step 2 — Surface every misalignment in one table

Build a numbered table of every misalignment found:

```
| # | Source artifact | Target artifact | Misalignment | Suggested resolution |
|---|---|---|---|---|
| 1 | Card (Problem) | MVP (must-have "X") | "X" can't be traced to a card claim | Either drop "X" from MVP, OR add a Problem-section paragraph that motivates it |
| 2 | Validation (Chosen price: $99/mo) | MVP (frontmatter priced-at: $49/mo) | Price diverges | Either update MVP priced-at to $99/mo, OR run /reprice to re-derive |
| 3 | ... | ... | ... | ... |
```

If NO misalignments found, surface:

> ✓ All artifacts for `<slug>` are aligned. No consolidation needed.
>
> Last checked: <YYYY-MM-DD>. Want me to write a "consolidation check" entry to the audit log so you can confirm the alignment date later?

…and stop after the user's yes/no.

#### Step 3 — Ask the user which misalignments to consolidate

Use `AskUserQuestion` with these options:

- **Consolidate all** — apply every suggested resolution above
- **Consolidate per-row** — go through each row, asking yes/no
- **Consolidate a subset** — user picks which row numbers to apply (free-text reply)
- **Cancel** — surface the misalignments for the user's reference but don't change anything

#### Step 3.5 — Feasibility consultation (optional; recommended for structural misalignments)

If the misalignment set includes structural items (segment mismatch between card and MVP, stack change implied by validation findings, must-haves that span multiple subsystems), the orchestrator's advisory panel can shape the consolidation before edits are applied. For purely mechanical misalignments (a price typo, a missing carried-note, a frontmatter field drift), skip this step.

Use `AskUserQuestion`:

> Some of the misalignments above are structural:
> - <list of structural rows from Step 2>
>
> Want a feasibility consultation from the senior engineers before consolidating?
>
> - **(a) Yes — consult** (Recommended for structural misalignments)
>   - The orchestrator (`senior-software-engineer`) brings in the right specialists in **consulting mode** per `senior-software-engineer.md` § Consulting mode. Output is a structured advisory note covering feasibility of the proposed resolutions, simpler alternatives, and hidden risks. The user can revise their consolidation picks after seeing the advice.
> - **(b) Skip — apply the consolidation as-is**
>   - Use when misalignments are purely mechanical.

On (a): invoke `senior-software-engineer` in consulting mode (same Agent-tool pattern as `/rework` Step 2.5). Surface the consultation output, then offer the user a chance to revise their consolidation picks before proceeding to Step 4.

#### Step 4 — Apply the consolidation

For each accepted resolution, apply targeted edits to the affected artifact. Use Edit (or rewrite if structural). Always preserve frontmatter invariants (slug, run-id, date-captured, source, territory).

**Important — always check the current content of the file before editing.** Never assume the file's state from memory; re-read it to see what's actually there. Decide targeted edit vs full overwrite per row:
- **Targeted edit** — one section, well-localized resolution
- **Full overwrite** — only when the consolidation touches the whole document (rare)

Most consolidations are targeted edits.

If multiple resolutions affect the same file, batch them into one Edit pass or several Edit calls — don't write the file once per row.

#### Step 5 — Re-run reviewers after consolidation

After consolidation is applied, the artifacts have been modified — their original reviewer verdicts no longer apply. Re-run the relevant reviewer set against the consolidated artifacts:

| Modified artifact | Re-run |
|---|---|
| Card | 4 product reviewers (viability, competition, market-segment, pricing) — same parallel pattern as `/validate-card` |
| MVP brief | 2 scope/code reviewers — same parallel pattern as `/scope-mvp` |
| V1 brief | 2 scope/code reviewers (v1-specific tests) — same pattern as `/scope-v1` |

If only card was consolidated, run only the 4 product reviewers. If only MVP was consolidated, run only the 2 scope/code reviewers. Etc.

Use the custom-subagent invocation pattern from `CLAUDE.md`.

#### Step 6 — Surface re-run verdicts + decision

Show the verdicts to the user:

> Verdicts on consolidated artifacts:
>
> **Card:**
> - Viability: <verdict>
> - Competition: <verdict>
> - Market-segment: <verdict>
> - Pricing: <verdict>
>
> **MVP:**
> - Scope: <verdict>
> - Code/architecture: <verdict>

If any REJECT: do NOT block — surface the REJECT and ask the user to either:
- **Run `/rework <slug>`** to address the reject(s) properly (recommended)
- **Override the REJECT in place** — same override flow as `/rework` step 7, including the consequences explainer + required justification
- **Revert the consolidation** — restore files to pre-consolidation state (the original frontmatter statuses are preserved in your Read-tool memory of the original content; or, if you didn't save them, use git diff if files were tracked, but most aren't)

#### Step 7 — Append audit-log entry

```bash
python3 scripts/audit_log.py add consolidation-applied "Consolidated <slug> (run-id: <run-id>). Misalignments found: <N>. Resolutions applied: <M>. Re-review verdicts: <summary>. Overrides: <list if any>."
```

#### Step 8 — Stop with next-step suggestions

> Consolidation committed for `<slug>` (audit-log id: `<id>`).
>
> Artifacts touched:
> - <list>
>
> Re-review verdicts: <summary>
>
> Next steps:
> - If everything passed: you're in a clean post-consolidation state. **`/validate-card <slug>`** is the natural next step if you want a fresh full-validation pass beyond the per-modification re-review just done.
> - If any REJECT was overridden during consolidation: `/rework <slug> <description>` is recommended as the proper way to address the underlying concern.
> - If you want to inspect the consolidation history: `/log type consolidation-applied`.

### Important — no auto-actions, no destructive shortcuts

- **NEVER apply a consolidation without user permission** for that row (or for the "all" bundle).
- **NEVER overwrite frontmatter invariants** (slug, run-id, date-captured, source, territory).
- **ALWAYS read the current artifact content before editing** — never assume the state from memory.
- **NEVER skip the re-review pass.** Consolidation may have introduced new issues; the reviewers catch them.
- **If a re-run reviewer REJECTs**, present the override flow with consequences — same as `/rework`. Don't silently approve.

### Notes

- **When to use `/consolidate` vs `/rework`:**
  - **`/consolidate`** is for fixing drift between artifacts that were each individually correct at their time of creation. The change is mostly mechanical — pulling them back into alignment.
  - **`/rework`** is for changing the underlying claims (the idea itself, the segment, the stack, the pricing strategy). The change is substantive and requires fresh reviewer judgment.
  - A typical sequence: run `/consolidate <slug>` first to clean up drift, then `/rework <slug> <changes>` if you want substantive changes.

- **What this command does NOT do:**
  - Does not change pricing — use `/reprice` for that.
  - Does not change kill state — use `/revive-card` for that.
  - Does not auto-invoke `/rework` even when consolidation triggers a REJECT.

- **Re-review uses the same reviewers as the original pass.** If you want to add a new reviewer (e.g., a domain-specific one), edit the methodology guide and `/validate-card` / `/scope-mvp` / `/scope-v1` first; `/consolidate` will pick the change up the next time it runs.
