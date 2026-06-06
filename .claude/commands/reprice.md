---
description: Rework the pricing for an existing artifact (idea card, MVP brief, or V1 brief) using the product-pricing-reviewer. Idempotent — surfaces the prior pricing if one exists and prompts to revise. Use when a price was set too aggressively or too softly and needs a fresh comparable / WTP / unit-economics pass without re-running full /validate-card.
argument-hint: <slug>
---

You are about to revise the pricing for one product. Follow the methodology in @guides/product/idea-validation-methodology.md §4.4 and the persona at `.claude/agents/product-pricing-reviewer.md` exactly.

**Arguments:** `$ARGUMENTS` — the product slug. The slug must exist somewhere in the workspace (idea card under `ideas/<run-id>/<slug>.md`, web/mobile/desktop project folder, or in `ideas/killed/`).

### Inputs to read before invoking the reviewer

1. **Locate every artifact for this slug** that may carry a price. Resolve them in this order:
   - Idea card: `find ideas -name "$ARGUMENTS.md" -not -path "*/killed/*"` → `ideas/<run-id>/<slug>.md`.
   - MVP brief: check `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, `desktop-apps/<slug>/MVP.md` (only one will exist).
   - V1 brief (if scoped post-MVP): `web-apps/<slug>/V1.md` / `mobile-apps/<slug>/V1.md` / `desktop-apps/<slug>/V1.md`.
   - Validation report: `find market-research -name "validation-$ARGUMENTS.md"` → `market-research/<run-id>/validation-<slug>.md` (has the prior pricing reviewer's output if `/validate-card` already ran).
   - Scoping report: `find market-research -name "scoping-$ARGUMENTS.md"` → `market-research/<run-id>/scoping-<slug>.md`.

   List which artifacts were found.

2. **Extract the current price.** Check, in order:
   - The idea card's frontmatter for `priced-at:` and `pricing-strategy:`.
   - The MVP / V1 brief's frontmatter for the same.
   - The MVP / V1 brief body for a `## Pricing` block.
   - The card or brief body for inline price mentions (`$X/month`, `$X/seat`, etc.).

   State the current price you found (or "no prior price found").

3. **If a prior price exists**, surface this to the user via `AskUserQuestion`:

   > This product is already priced at **$<current> / <unit> / <interval>** (set during <which artifact>, strategy: <prior strategy or 'user-override'>). Do you want to revise it?
   >
   > - **Yes — re-research and revise** → invoke the pricing reviewer with the current artifacts + prior reviewer output as additional input.
   > - **No — keep the current price** → stop, no changes made.

   If the user picks "No", stop here.

4. **If no prior price exists**, skip the confirmation and proceed straight to invoking the reviewer.

### Do

1. **Invoke `product-pricing-reviewer` as a single Agent call.** Use the custom-subagent invocation pattern in `CLAUDE.md`:

   ```
   Agent({
     subagent_type: "general-purpose",
     description: "Reprice <slug>",
     prompt: "You are about to act as the product-pricing-reviewer. Step 1: read .claude/agents/product-pricing-reviewer.md in full and treat its body (everything after the YAML frontmatter) as your role, lens, process, evidence standards, rationalizations to refuse, red-flag rules, and output format. Step 2: read the following artifacts: <list of resolved paths>. Step 3: ALSO read guides/product/idea-validation-methodology.md (for the locked verdict format) and CLAUDE.md (for founder context, internet access policy). Step 4: read user-context/INTERESTS.md if present, for founder context only. Step 5: if a prior pricing-reviewer output exists in market-research/<run-id>/validation-<slug>.md, treat it as a prior baseline you may agree or disagree with — be willing to revise the recommended option if comparables or WTP signals have shifted. Step 6: return your output in the locked verdict format from §5 of the validation guide, PLUS the Comparable-pricing / Proposed-price / Unit-economics / Suggested-pricing-options blocks from your persona file."
   })
   ```

2. **Wait for the reviewer's output.**

3. **Surface the suggested options to the user** via `AskUserQuestion`:

   > Pricing reviewer's verdict on **<slug>**: <APPROVE / APPROVE-WITH-NOTES / REJECT> (confidence: <LOW/MEDIUM/HIGH>).
   >
   > Suggested options:
   >   1. **<Option 1 name>** — $<amount> / <unit> / <interval> — RECOMMENDED — <trade-off>
   >   2. **<Option 2 name>** — $<amount> / <unit> / <interval> — <trade-off>
   >   3. **<Option 3 name>** — $<amount> / <unit> / <interval> — <trade-off>
   >
   > Pick one, or type your own price.

   Offer the three options as picker choices via `AskUserQuestion`, plus an "Other" path that lets the user type their own price.

4. **If the user types their own price**, validate it parses as a money amount (e.g., `$29/seat/month`, `$199 one-time`). If it doesn't parse, ask once for a clearer format. Surface the pricing-reviewer's options' rationales next to the user's price for context — but respect the user's choice.

5. **Write the chosen price to every relevant artifact.** Update in place:
   - Idea card frontmatter: `priced-at: $<amount> <unit> <interval>` and `pricing-strategy: "<picked-option-name or 'user-override'>"`.
   - MVP / V1 brief frontmatter: same fields if they exist.
   - MVP / V1 brief body: update the `## Pricing` block (create one if missing).
   - **Append a reprice block to the validation report** at `market-research/<run-id>/validation-<slug>.md` under a new heading `## Reprice — <YYYY-MM-DD>` containing the full reviewer output and the user's pick. Do NOT overwrite the original validation reviewer output — append.

6. **Surface a summary to the user**: what files were touched, what the new price is, and what the prior price was (if any).

### Stop here — no auto-actions

- This command is **read-mostly + write-on-confirm**. The reviewer call is automatic; price application requires explicit user pick.
- Do **NOT** advance any artifact's status as a side effect of repricing.
- Do **NOT** invoke any other reviewers (viability / competition / market-segment) — `/reprice` is pricing-only by design. If the user wants a full re-validation, point them at `/validate-card <slug>`.
- Do **NOT** chain into other commands after the reprice — the user decides what to do next.

### Suggest next steps

After writing changes, propose 2-3 reasonable next actions based on what the user repriced:

- If the slug has an MVP brief but no shipped product: "Re-run `/scope-mvp <slug>` to refresh the effort estimate against the new price (revenue-per-user gates which features are must-have)."
- If the slug has shipped and is in the v1-decision phase: "Use the new price as input to `/scope-v1 <slug>` if you're upgrading."
- Always: "View the reprice in the audit log via `/log` once `card-reprice` is wired (currently not auto-logged)."
