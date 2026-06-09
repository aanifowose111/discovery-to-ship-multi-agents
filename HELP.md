# HELP — discovery-to-ship-multi-agents

Command-by-command reference, common scenarios, gotchas, and recovery paths for this workspace. Pairs with `README.md` (which is the public-facing landing) and `CLAUDE.md` (which is the Claude-facing context).

If you just want a quick menu of "what can I do right now," run **`/menu`** inside Claude Code instead of reading this end-to-end. (Why `/menu` and not `/help`? Claude Code has a built-in `/help` command that shows its own dialog; our custom command lives under `/menu` to avoid the collision.)

---

## Table of contents

1. [Common scenarios](#1-common-scenarios)
2. [All slash commands](#2-all-slash-commands)
3. [Skills](#3-skills)
4. [Reviewer and worker subagents](#4-reviewer-and-worker-subagents)
5. [Folders and where things live](#5-folders-and-where-things-live)
6. [Common gotchas](#6-common-gotchas)
7. [Recovery paths](#7-recovery-paths)
8. [Stack flexibility — quick reference](#8-stack-flexibility--quick-reference)
9. [Internet access policy — quick reference](#9-internet-access-policy--quick-reference)

---

## 1. Common scenarios

### 1.1 Starting a brand-new session

1. Open a terminal in the repo directory.
2. Run `claude`.
3. Claude auto-loads `CLAUDE.md` and accumulated `MEMORY.md` context.
4. **A welcome banner displays** at the top of the session — "Welcome to discovery-to-ship-multi-agents — by Abiodun Anifowose…" — confirming you're in the right workspace and surfacing the three most common starting commands. This is configured via `companyAnnouncements` in `.claude/settings.json`; edit there if you want to customize the message for your fork.
5. If you state your intent in the first message (e.g., "let's continue the findvil scoping"), Claude proceeds. If you greet generically or ask "what's the status?", Claude briefly summarizes in-flight work and offers a short menu.
6. Pick an option or override with a specific command.

### 1.2 Continuing from a previous session

Same as 1.1. Claude reads:

- The latest reports in `market-research/`.
- Active idea cards in `ideas/` (anything not in `ideas/killed/`).
- In-flight MVP briefs in `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, and `desktop-apps/<slug>/MVP.md`.
- Active design phases at `<web-apps|mobile-apps|desktop-apps>/<slug>/design/`.

If a phase is in progress, Claude picks up at the right checkpoint per the pipeline orchestration in `CLAUDE.md`.

### 1.3 Starting product discovery without any specific idea

Just type:

```
/discover
```

By itself, no arguments. Claude does an inline lightweight scan from your founder context (in `CLAUDE.md`) + recent trends + recent kills, picks 2-3 territories, and brainstorms 10+ idea cards. You see a top-3 list at the end and sign off.

For more rigorous discovery, run `/scan` first to map territories deliberately.

### 1.4 Validating an idea you've drafted

```
/validate-card <slug>
```

The card must already exist at `ideas/<slug>.md`. The command runs the four product reviewers in parallel:

- `product-viability-reviewer` — does the problem exist with external evidence?
- `product-competition-reviewer` — real differentiation vs. actual competitors?
- `market-segment-reviewer` — segment crisp, sized, reachable, broadly willing-to-pay?
- `product-pricing-reviewer` — is the *specific* proposed price defensible against comparable products, segment WTP, and solo-builder unit economics? Returns 2-3 strategic pricing options; you pick one or type your own.

Each returns a verdict with cited sources. You see the integration summary, then decide: advance to `green-lit`, revise, send back to discovery, or kill.

### 1.5 Scoping an MVP for a `green-lit` card

```
/scope-mvp <slug>
```

Claude **asks you to confirm the stack first** (workspace defaults: dockerized Flask for web, React Native + Expo for mobile, Python + PySide6 for desktop — but other stacks are supported; see §8). Then drafts the MVP brief and runs the scope + code reviewers.

**After you sign off on the scoping verdict and advance to `green-lit-to-build`, Claude asks two more questions before any build work begins:**

1. **Design path** — *claude-led* (Claude runs full design research → drafts an implementation-ready `DESIGN_SPEC.md` → builds against it; no external designer engaged) vs. *hired designer* (Claude runs research → drafts a Figma-handoff `DESIGN_BRIEF.md` → you brief the designer → they deliver a Figma → Claude implements from the handoff). Both paths now run full design research; the difference is the second step (`DESIGN_SPEC.md` vs `DESIGN_BRIEF.md`) and whether a human designer is in the loop. Claude-led is faster and recommended for first-pass MVPs; hired is recommended once the product has been validated with first users.
2. **Build support** — *I'll follow along* (you review code, run things on your machine, deploy) vs. *I need help* (Claude surfaces [Fijara](https://fijara.com), Abiodun's development service, as a friendly option to take the build on). You can change your mind later either direction.

Both picks are recorded in the brief's frontmatter so future sessions know what was decided.

### 1.6 Running design research for a validated product

```
/research-design <slug>
```

Runs the `ui-ux-researcher`. Produces a design-direction report with at least three visual directions, color and typography options, pattern conventions, brand positioning, and a portfolio-continuity question. Lives at `<web-apps|mobile-apps|desktop-apps>/<slug>/design/DESIGN_RESEARCH.md`.

### 1.7 Drafting the design brief after research

```
/draft-design-brief <slug>
```

Claude asks for your picks (visual direction, palette, typography, voice, portfolio-continuity decision, answers to the research's open questions, timeline), drafts the consolidated brief, and runs the `design-brief-reviewer`. The brief lives at `<web-apps|mobile-apps|desktop-apps>/<slug>/design/DESIGN_BRIEF.md`. You sign off before it goes to the human designer.

### 1.8 Monitoring trends between scans

```
/trend-check
```

Runs a weekly sweep across active state (active scan + active cards + active briefs). Categorizes findings as material / notable / background. Material findings recommend a downstream command (`/scan`, `/validate-card`, `/scope-mvp`) — but never auto-invoke.

For an emergency sweep:

```
/trend-check triggered <one-line reason>
```

### 1.9 Killing an idea

The `/validate-card` flow gives you the option to kill at the decision step. To kill manually:

1. Move the card: `mv ideas/<slug>.md ideas/killed/<slug>.md`
2. Add a one-line `killed-reason:` field to the frontmatter.
3. The kill is invisible to future sessions except that `/discover` will respect the filter signal (avoid surfacing similar ideas).

### 1.10 Exporting an artifact as PDF or DOCX

Ask in plain English:

> Export the findvil MVP brief as PDF.

The `doc-export` skill triggers. Output lands in `generated/<category>/<YYYY-MM-DD>-<slug>-<doc-type>.<ext>`.

### 1.11 Previewing a Jinja template in Chrome

Ask:

> Preview the dashboard page in findvil.

The `web-preview` skill triggers. It loads the Jinja template, renders it with fixture demo data from `web-apps/findvil/previews/fixtures/dashboard.py`, and opens the result in Chrome.

If the fixture or `render.py` doesn't exist yet, the skill scaffolds them and prompts you to fill in demo data.

---

## 2. All slash commands

### `/scan [broad|focused <topic>]`

Market scan per `guides/market/market-scan-methodology.md`. Default is broad. For focused: `/scan focused indie-saas-tools`. Output: `market-research/scan-<YYYY-MM-DD>.md`. **Stops at:** sign-off; status → `active`. **Next:** `/discover`.

### `/discover [optional comma-separated territory names]`

Discovery cycle per `guides/product/idea-discovery-methodology.md`. Works as a one-command bootstrap when run with no args (uses founder fit + trends). Output: idea cards in `ideas/<slug>.md` + triage at `market-research/triage-<YYYY-MM-DD>.md`. **Stops at:** top-3 sign-off. **Next:** `/validate-card <slug>` for each.

### `/validate-card <slug>`

Validation per `guides/product/idea-validation-methodology.md`. Invokes the four product reviewers in parallel (viability, competition, market-segment, pricing). Output: `market-research/<run-id>/validation-<slug>.md`. **Stops at:** decision (advance / revise / kill) and price pick (pick from the pricing reviewer's options or type your own). **Next:** `/scope-mvp <slug>` if advanced.

### `/scope-v1 <slug>`

Drafts the **v1 brief** at `<web-apps|mobile-apps|desktop-apps>/<slug>/V1.md` — the polished build that lives past the MVP's first-10-users validation. Per `guides/product/v1-scoping-methodology.md`.

**Preconditions:** `MVP.md` exists with `status: shipped`, and the riskiest assumption was validated by the first-10-users round. If either fails, the command stops and surfaces what's missing.

**The flow** (5 steps before the brief is drafted):

1. **Capture first-10-users feedback.** You summarize what the round taught (at least a one-line per-user summary). Claude pushes back once if the reply sounds like a gut feel rather than user signal.
2. **Design-path picker.** Three options:
   - **(a) Continue generic design** — handle v1 UI in code, same patterns as MVP. Fastest. Right for dev tools / internal SMB / function-over-form segments.
   - **(b) Engage a professional UI/UX designer** — kicks off the full Phase 3 (`/research-design` → `/draft-design-brief` → designer → handoff) before v1 build starts. Right for consumer / design-led products and category-leaders with polish-as-moat.
   - **(c) Hybrid — light refresh** — keep the claude-led path but apply a polish pass (refined palette/typography, 2-3 distinctive UI patterns). Middle path; no formal designer engagement.
3. **Pricing decision.** Surfaces the current MVP price. You either keep it or invoke `/reprice <slug>` first (recommended if first-10-users showed price friction or comparables shifted).
4. **Surface new must-haves.** Shows you the MVP's deferred could-haves + Claude's read of what the user feedback implies. You pick which become v1 must-haves.
5. **Draft V1.md + run reviewers.** Same `product-scope-reviewer` + `code-reviewer` as `/scope-mvp`, but tested against the v1 brief.

**Output:** `V1.md` brief at the product folder + `scoping-v1-<slug>.md` report in the run's `market-research/` folder. **Stops at:** advance / revise / pause / retire decision. **Next:** depends on the design path picked:
- `(a) claude-led-continued` → `/research-design <slug>` (refreshed for v1) → `/draft-design-spec <slug>` (refreshed) → `/start-build <slug>` (reads V1.md + refreshed spec, extends MVP code).
- `(c) hybrid-light-refresh` → `/research-design <slug> --light` first, then `/start-build`.
- `(b) pro-designer-engaged` → `/research-design <slug>` (full) → `/draft-design-brief <slug>` → designer → handoff → `/start-build`.

**`/start-build` auto-detects which brief to build.** If both `MVP.md` (status `shipped`) and `V1.md` (status `green-lit-to-build`) exist, the orchestrator picks `V1.md` and treats the MVP code as the starting point to extend.

### `/scope-mvp <slug>`

Scoping per `guides/product/mvp-scoping-methodology.md`. **Asks you to confirm the stack first.** Drafts the MVP brief and runs the scope + code reviewers. Output: `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md` + `market-research/scoping-<slug>-<YYYY-MM-DD>.md`. **Stops at:** decision (build / revise / kill). **Next:** build phase using the relevant scaffold guide.

### `/research-design <slug>`

Design research per `guides/ui-ux/design-research-methodology.md`. Invokes the `ui-ux-researcher`. **Fires for both design paths** (`claude-led` and `hired`). Output: `<web-apps|mobile-apps|desktop-apps>/<slug>/design/DESIGN_RESEARCH.md` — covers per-surface (public/auth/user/admin/employee dashboards), product-space + platform trends, 3+ visual directions, 3+ color/type pairings, pattern conventions, responsive strategy, brand positioning. May pause for interactive reference-URL checkpoints with you. **Stops at:** sign-off. **Next:** branches on the brief's `design-path` — claude-led → `/draft-design-spec`; hired → `/draft-design-brief`; hybrid-light-refresh → `/start-build` directly.

### `/draft-design-spec <slug>`

Implementation-ready spec per `guides/ui-ux/design-spec-methodology.md` (claude-led path). **Asks you for picks first** (visual direction, palette, typography, voice, portfolio-continuity, dark-mode scope, font loading). Invokes the `ui-ux-researcher` in spec-writing mode to produce `DESIGN_SPEC.md`, then runs the `design-spec-reviewer`. Output: `<product-folder>/design/DESIGN_SPEC.md` — exact CSS tokens (color/type/spacing/radius/shadow/motion), icon library install, image-asset prompts (batch-later; user generates later), responsive specs, per-surface specs, component patterns. **The spec is the build's source of truth** — supersedes `frontend-ui-engineering` defaults. **Stops at:** sign-off; status → `acted-on`. **Next:** `/start-build <slug>`.

### `/draft-design-brief <slug>`

Brief per `guides/ui-ux/design-brief-methodology.md` (hired-designer path). **Asks you for picks first** (visual direction, palette, typography, voice, portfolio-continuity, timeline). Drafts the Figma-handoff brief and runs the `design-brief-reviewer`. Output: `<product-folder>/design/DESIGN_BRIEF.md`. **Stops at:** sign-off; status → `sent`. **Next:** transmit to the human designer.

### `/trend-check [optional triggered <reason>]`

Trend sweep per `guides/market/trend-monitoring.md`. Output: `market-research/trends-<YYYY-MM-DD>.md`. **Stops at:** which downstream commands (if any) to run. **Next:** whichever the user picks.

### `/rework <slug> <description of changes>`

The canonical command for substantively changing an idea, scope, MVP brief, or V1 brief **after** reviewers have already run on the originals. Designed to solve the failure mode where Claude edits the original file directly, runs reviewers, gets a REJECT, and the user is stuck explaining how to override + how to undo — every time. `/rework` separates **proposal** from **commit** so the user can iterate safely.

**The flow:**

1. **Locate and read** the card + any downstream artifacts (MVP, V1, validation report, scoping report, BUILD_STATUS).
2. **Confirm scope** — card only, card + MVP, or card + MVP + V1.
3. **Decide strategy per artifact** — targeted edit (one or two sections) or full rewrite (structural).
4. **Create temp files** next to each original — `<slug>-temp.md`, `MVP-temp.md`, `V1-temp.md`. Apply the user's change description to the temps. **Originals are NOT touched.**
5. **Run reviewers against the temps** (4 product reviewers for card, 2 scope/code for MVP, 2 scope/code for V1).
6. **For each REJECT, surface a suggested approach** to get passing — derived from the reviewer's specific findings. User picks: implement recommendations + re-review, make custom changes + re-review, override the REJECT (see below), or cancel.
7. **For each override, surface a consequences explainer** specific to the reviewer's lens (e.g., overriding a competition REJECT → "differentiation story may not survive contact with the market at first-10-users time"). The user must provide a one-sentence justification — recorded permanently in the audit log.
8. **Final user confirm** before any merge. Show the diff summary, status targets, override list, and ask: Commit / Revise more / Cancel.
9. **On Commit**: `mv` each temp over the original, set frontmatter statuses back to pre-review baselines (card → `triaged`, MVP → `in-scoping`, V1 → `in-v1-scoping`), append `## Rework — <date>` blocks to existing validation/scoping reports (don't overwrite), append `rework-applied` audit-log entry.
10. **On Cancel**: delete all temps; no changes were made.

**Why this matters:** the rework command captures override decisions permanently. The audit-log entry says exactly which REJECT was overridden, by whom, and the justification. Future you and any forker see the record — there's no silent override.

**Mid-build awareness:** `/rework` reads `BUILD_STATUS.md` at the start. If a build is in progress (any subsystem at `[>]` or `[x]`), the command surfaces a build-state banner before the scope picker. The Step 2.5 consultation produces a **Subsystem impact** map naming which `[x]` subsystems the rework affects. At Step 8a, the user picks: **(a) flip affected `[x]` subsystems back to `[>]` on commit** (next `/start-build` re-engages the relevant specialists to revisit their work against the reworked brief; per-flip History entries with `(audit: <id>)` annotation make the trigger auditable per `guides/product/build-status-methodology.md` § Special exception), or **(b) leave subsystem states alone** (user reconciles manually — appropriate for brief-only changes like pricing). If MVP is `shipped`, `/rework` warns and suggests `/scope-v1` instead — reworking a shipped brief is rewriting history.

**Use when:**
- You want to address a specific reviewer concern by reworking the artifact (not just overriding silently).
- You want to switch the segment / stack / pricing strategy mid-cycle.
- You realize after scoping that the MVP must-haves don't actually test the riskiest assumption — rework them.
- You want a safe "edit + review + commit" loop instead of edit-and-pray.

**Don't use for:**
- Pure pricing revisions — use `/reprice` (lighter, only runs pricing reviewer).
- Reviving a killed card — use `/revive-card` (different flow).
- Renaming the slug — slugs are immutable; kill the card and create a new one.

### `/consolidate <slug>`

Check alignment across all artifacts for one slug — idea card, validation report, scoping report, MVP brief, and (if present) V1 brief — and consolidate any misalignments. The goal: **MVP faithful to scope, scope faithful to idea.**

**Why drift happens:** the pipeline produces multiple linked documents over time. The MVP brief might add a must-have that doesn't trace to any card claim. The validation chosen-price might be $99 but the MVP frontmatter `priced-at:` says $49. The V1 might list a "carried must-have" that the MVP didn't actually ship. Each artifact was correct in isolation when it was written, but they've diverged.

**The flow:**

1. **Read every existing artifact** for the slug. Always check the current file state — never assume.
2. **Run alignment checks** across artifact pairs (card ↔ MVP, validation ↔ MVP, scoping ↔ MVP, card ↔ V1, MVP ↔ V1). Specific checks include: must-have traceability, success criterion testing the riskiest assumption, stack consistency, pricing match, validation gaps carried into MVP, design-path picked for V1, etc.
3. **Surface every misalignment in one numbered table** with source artifact, target artifact, specific misalignment, and a suggested resolution.
4. **Ask the user which to consolidate** — all-at-once, per-row, a subset, or cancel.
5. **Apply targeted edits** to the affected artifacts. Preserve frontmatter invariants (slug, run-id, date-captured, source, territory).
6. **Re-run reviewers** against the consolidated artifacts — same reviewer set that originally produced the artifact. Surface the new verdicts.
7. **If any REJECT after consolidation:** offer to run `/rework`, override in place (with consequences + justification), or revert the consolidation.
8. **Append `consolidation-applied` audit-log entry** with the misalignment count, resolutions applied, and re-review verdicts.

**Typical sequence:** run `/consolidate` first to clean mechanical drift, then `/rework` if substantive changes are still needed. `/consolidate` is purely about pulling artifacts back into agreement — it doesn't change the underlying claims.

**Use when:**
- You suspect drift between the card and the brief.
- You hand-edited an artifact and want to verify nothing else needs adjusting.
- After a reviewer override or a long break, before committing more time to the product.

**Don't use for:**
- Changing claims (use `/rework`).
- Changing pricing (use `/reprice`).
- Reviving a killed card (use `/revive-card`).

### `/infra-cost <slug> [--save | --users=A,B,C | --include-v1]`

Estimate the infrastructure cost of running a product's MVP (and optionally V1) — minimum / medium / max scenarios, broken down by user base, with each cost item flagged as recurring vs. one-time and user-dependent vs. fixed.

**Why this matters:** the pipeline already produces an effort estimate (per `mvp-scoping-methodology.md` §5); this command produces the **money** estimate. Helps you answer "can I afford to ship this MVP and keep it running at the user counts in my success criterion?"

**The flow:**

1. **Read MVP.md** (and V1.md if `--include-v1` was passed). Extract stack, infrastructure decisions, must-haves that imply cost-bearing dependencies, success criterion (for user-count baseline).
2. **Confirm tiers** with the user (default `10 / 100 / 1000`, override with `--users=A,B,C`).
3. **Fetch current pricing** for each cost item via web fetch (per `CLAUDE.md § Internet access policy` — no permission prompts). Cite each URL and the fetch date.
4. **Build the cost table** — one row per cost item, with columns: vendor, type, min/med/max amounts, recurring?, user-dependent?, source.
5. **Compute summary stats** — total monthly burn per tier, fixed vs. variable burn, recurring admin cost the maintainer pays regardless of users, one-time / setup costs in year 1.
6. **List every assumption** so the user can adjust if their actual usage differs (LLM tokens per user, conversion rate, ARPU, etc.).
7. **Optionally save** the report to `<stack>-apps/<slug>/INFRA_COST.md` with `--save`.

**Cost categories covered (per stack):**

- **Flask web (default):** DO droplet / App Platform; managed Postgres; DO Spaces; domain + DNS; email vendor; LLM API; auth provider; Stripe; monitoring; CDN; backups.
- **RN + Expo (mobile):** EAS Build / Submit / Update; Apple Developer Program; Google Play Console; backend (Flask shape); push notifications; analytics.
- **PySide6 desktop:** Code signing certificate; notarization; auto-updater hosting; telemetry backend; installer distribution.

**Doesn't cover:** founder's time, marketing/ads, customer-acquisition costs, legal/accounting fees, Claude Code subscription. Those are separate budget categories.

**Why fetch pricing instead of baking it in?** Vendor prices change 1-3x per year. Hard-coding would surface stale numbers; fetching makes the report accurate at the moment of estimation.

### `/revive-card <slug>`

Restore a previously-killed idea card back to active state. The canonical inverse of a kill — replaces the older "manual `mv`" workaround.

**What it does:**

1. **Locates the killed card** via `find ideas/killed -name "<slug>.md"`. Extracts the `<run-id>` from the path.
2. **Pre-flights the slug** via `python3 scripts/check_slug.py <slug>`. Refuses if there's an active card with the same slug in any run-folder (would create a `slug.collision` error per `CLAUDE.md § Slug uniqueness`). If only a killed entry + an orphaned app folder are flagged, it's safe to proceed — the kill is what we're undoing.
3. **Shows you the snapshot** — kill date, kill reason (from frontmatter), linked validation report, linked audit-log id (from `card-kill` entry), and any orphaned MVP/V1 brief at `<web-apps|mobile-apps|desktop-apps>/<slug>/` with their current status.
4. **Asks what to revive:**
   - **Restore card only** — moves the file back, resets frontmatter to `status: triaged`, clears `killed-date` / `killed-reason` / `audit-log-id`. Leaves any orphaned brief as-is (the `slug.orphaned-app-after-kill` lint warning will keep flagging it until you address it separately).
   - **Restore card AND revive MVP/V1 briefs** — same as above, plus flips brief `status: killed` → a pre-kill state you pick (`green-lit-to-build`, `building`, or `shipped` depending on context).
   - **Cancel** — stop, no changes.
5. **If reviving briefs, asks for the target status** when there's ambiguity (e.g., was the MVP shipped before the retire? if not, only `green-lit-to-build` makes sense).
6. **Executes atomically:** moves the file, edits frontmatter via Edit (preserves `slug`, `run-id`, `date-captured`, `source`, `territory`, `validation-report`), flips brief statuses if requested, appends a `card-revive` audit-log entry summarizing the revive (with the original kill reason truncated for searchability), then runs `lint_pipeline.py` to verify no new errors.
7. **Stops at a checkpoint**, suggests 2-3 plausible next steps (`/validate-card <slug>` to re-validate against fresh signal, `/scope-mvp <slug>` to re-scope, `/scope-v1 <slug>` if it was a shipped MVP, or `/log type card-revive` to view the audit entry).

**Use when:**
- A card was killed prematurely or based on signal that has since shifted (e.g., a competitor's pricing changed, a regulatory shift opened the segment, your own pivot makes the original kill stale).
- A `/scope-v1` "retire the product" decision is being reversed after fresh user interest emerges.
- You want to bring back a card whose validation was a `REJECT` and you've since done additional research that addresses the reject reason.

**Don't use for:**
- "Recycling a slug" — if you want a new product with the same name, pick a different slug. `/revive-card` brings back the SAME card with its history intact; it doesn't repurpose the slug.
- Reviving an MVP brief whose card was never killed. The brief status flips happen as a SIDE EFFECT of card revive when an orphan exists; if you just want to flip a brief's status, edit the frontmatter directly.

**Audit trail:** the `card-revive` entry includes the new audit-log id (returned by the script), the revived run-id, and the original kill reason. Together with the original `card-kill` entry (linked via `audit-log-id` in the card frontmatter before revive, captured in the revive entry's description), you get a complete kill-and-revive history queryable via `/log type card-revive` and `/log type card-kill`.

### `/reprice <slug>`

Reworks the pricing on an existing artifact (idea card, MVP brief, or V1 brief) using only the `product-pricing-reviewer`. **Idempotent** — when a prior price exists (via `priced-at:` frontmatter or a `## Pricing` block in the brief), the command surfaces it and asks "do you want to revise?" before invoking the reviewer.

**The flow:**

1. Resolve the artifacts for this slug (card / MVP / V1 / validation report / scoping report) and locate the current price.
2. If a prior price exists, confirm with the user before re-researching.
3. Invoke `product-pricing-reviewer` — it does fresh comparable-pricing research, segment WTP signal-mining, and unit-economics math, then returns 2-3 strategic pricing options ranked recommendation-first.
4. User picks one option or types their own price (validated to parse as `$<amount>/<unit>/<interval>` or `$<amount> one-time`).
5. Claude writes the chosen price to every relevant artifact's frontmatter (`priced-at:`, `pricing-strategy:`) and the brief's `## Pricing` block. Appends a `## Reprice — <date>` block to the validation report; the original validation reviewer output is NOT overwritten.

**Use when:**

- A scan or discovery surfaced a price that "doesn't feel right" putting yourself in the customer's shoes.
- Comparable products have repriced (entry tier went up or down) and your price now looks off.
- You shipped an MVP at $X and the first 10 users mostly complained about price.

**Don't use for:** full re-validation of the card. `/reprice` runs only the pricing reviewer — the other three reviewers (viability, competition, market-segment) are not re-invoked. For a full re-validation, run `/validate-card <slug>` again.

### `/preview-product <slug> [page-name]`

Preview the current state of a product's UI in the browser. Auto-detects which mode is possible:

- **Real preview** — opens the actual running app (`http://localhost:5000/<page>`). Requires the dev server up and the route + dependencies wired.
- **Dummy preview** — falls back to rendering the Jinja template with fixture demo data. Useful for visual review while the rest is being built. Always possible if the template file exists.

The command **always tells you which mode you got and why**, so you know whether you're seeing live behavior or just structure + styling. If dummy mode, it briefly mentions what would unblock real preview ("dev server is down" / "no route handler yet" / "the X service this depends on doesn't exist yet").

Web only — for mobile previews, use Expo Go / dev client during development or EAS preview builds for tester distribution (see `guides/mobile/eas-build-and-update.md`).

### `/ship-app <slug> [--web|--mobile|--both]`

Initialize the shipment / release phase for a product whose build is substantially complete. Distinct from `/start-build` (which brings the product *to* ready-to-deploy state); `/ship-app` takes it from there with a gated release-readiness pass + actual deploy + post-deploy verification.

**Flow:**

1. **Verify build readiness** — reads `BUILD_STATUS.md` for the product; if core subsystems aren't all `[x]`, refuses and points you back at `/start-build`.
2. **QA pre-flight** (`senior-qa-engineer`) — final test pass, acceptance criteria check against the MVP brief's success criterion, accessibility spot-check. Outputs "release-ready" or "not-ready" + blockers.
3. **Security pre-flight** (`senior-security-engineer`) — auth, secrets, input boundaries, file I/O, OWASP-style spot check. Outputs "ship-safe" or "blockers".
4. **Final user confirmation** — summary of QA verdict, security verdict, and the deploy steps that will run. Ship-now or cancel.
5. **Deploy** (`senior-devops-engineer`):
   - **Web (Flask default):** Docker build → push → deploy to target → confirm HTTPS via Caddy → confirm health endpoint → confirm DNS.
   - **Mobile (RN default):** `eas build --profile production` → submit to TestFlight / Play Console internal track → confirm reviewer receipt.
   - **Other stacks:** follows the user's documented plan from MVP.md §7.
6. **Post-deploy verification** (same persona) — smoke tests against the deployed surface; outputs "ship verified" or "post-deploy issues".
7. **`BUILD_STATUS.md` updated** — deploy timestamp, version SHA, target environment, verdicts, post-deploy result.

**Args:**

- `<slug>` — required.
- `--web` / `--mobile` / `--both` — optional scope flag; defaults inferred from the MVP brief's must-have surface.

**Use when:** the build is substantially complete and you're ready to put the v0 in front of the first 10 users named in your success criterion.

**Don't use for:** marketing launches, public beta launches, or app-store-feature campaigns — those are downstream of "first 10 users see the product" and aren't part of this workspace's pipeline.

**Safety rails:**

- Both pre-flight gates must pass (or be explicitly overridden + documented in BUILD_STATUS.md) before any deploy runs.
- The script never `--force` pushes, never skips a rollback path.
- After post-deploy issues, the user decides whether to fix-and-reship — there is no auto-iteration.

### `/continue-build <slug> [--hint "<text>"] [--from <file-or-subsystem>]`

Resume an in-flight build for a specific product. **The disambiguator for "please continue" when multiple products are in-flight.** What it does:

1. **Reads `BUILD_STATUS.md`** — identifies subsystems in `[>]` (in progress) vs. `[ ]` (pending) vs. `[x]` (done).
2. **Scans the source tree for most-recently-modified files** (mtime-sorted; top 5-10) — so it knows what *file* was last touched, not just what subsystem. Output looks like `app/static/css/components.css (3 min ago)` → the orchestrator knows CSS work is mid-flight.
3. **Accepts optional `--hint "<text>"`** — free-text disambiguation: "we just finished tokens.css and were starting components.css". Baked into the orchestrator's interpretation.
4. **Accepts optional `--from <file-or-subsystem>`** — explicit override of the resumption point: `--from app/routes/auth.py` or `--from "auth"`. Authoritative; overrides the mtime-based guess.
5. **Invokes `senior-software-engineer` in resumption mode** — which summarizes what's done, names the most recent files touched, proposes the next file + specialist to engage. **Does NOT re-ask the orientation questions** (those were answered at `/start-build` time).

Edge cases: no `BUILD_STATUS.md` → use `/start-build`; all subsystems `[x]` → use `/ship-app`; `build-status: rework-in-progress` → resumes the rework-flipped subsystems first.

**Stops at:** orchestrator's resumption summary + next-action proposal. **Next:** user confirms or overrides.

### `/recollect <slug>`

Read-only "where are we" synthesis for a specific product. Walks every artifact (idea card, validation, scoping reports, MVP/V1 briefs, design research/spec/brief, designer handoff, BUILD_STATUS, team file, source tree, audit-log entries) and emits a one-screen report: pipeline-state table, build progress (if any), source tree at-a-glance, team, recent activity, prose synthesis, and 2-4 suggested next actions specific to the actual state. **Pure read-only — invokes no subagent, modifies no file, appends to no log.** Use when you're returning to a product after a break and want to remember "what was I doing here?" without committing to an action. **Distinct from `/status`** (which reports across ALL products in the workspace) and **`/continue-build`** (which actually invokes the orchestrator). **Stops at:** synthesis shown. **Next:** user decides.

### `/generate-checklist <slug>`

Generate (or regenerate) the **fine-grained `CHECKLIST.md`** for a product — the companion to `BUILD_STATUS.md`. Where `BUILD_STATUS.md` tracks coarse subsystems ("auth subsystem `[x]`", "API contract `[>]`"), CHECKLIST tracks fine deliverables ("Signup form `[x]`", "Verification email template `[x]`", "Resend-verification UI `[ ]`", "Tests for expired-token path `[ ]`"). Reads MVP.md (and V1.md if green-lit-to-build) and decomposes each must-have into 3-8 bite-size deliverables with file-path hints in italics. Per `guides/product/checklist-methodology.md`. **Stops at:** file written + summary shown. **Next:** open the file, or `/read-checklist <slug>` to refresh later.

### `/read-checklist <slug>`

Refresh `CHECKLIST.md` for a product — runs an **mtime-cached** scan: only inspects files modified since the last refresh, so the command is cheap and idempotent. Crosses out completed items (matching the file-path hints), proposes additions for newly discovered work (capped at 5 per pass; user confirms each via `AskUserQuestion`), and updates the Scope changes log. **Auto-triggered by the build orchestrator** after every `BUILD_STATUS.md` subsystem flips to `[x]`. **Stops at:** summary of what changed + pending items to highlight. **Next:** open the file, or `/continue-build <slug>` to resume on a pending item.

### `/push-project <slug> [-m "<msg>"] [--init] [--remote <url>] [--status] [--no-commit] [--branch <name>] [--force-with-lease]`

Push a product (`web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`) to its own **independent GitHub repository**, separate from the parent workspace repo. The parent's `.gitignore` already ignores `web-apps/**` etc. → each nested folder can be its own git repo with its own remote, history, branches, CI. Per `guides/product/project-git-methodology.md`.

- `--init` for first-time setup (creates `.git/`, stack-specific `.gitignore`, `README.md`, optional `LICENSE`, sets remote, initial commit + push)
- `--status` for read-only status check
- `--remote <url>` to set/update remote
- No flags = routine commit + push (asks for commit message via free-text if no `-m` flag)

**Mandatory safety scans** before every commit: refuses if `.env` is staged (only `.env.example` allowed); scans for AWS keys, GitHub tokens, Stripe keys, private keys, Slack tokens; refuses plain `--force` to `main`. **Per-commit Co-Authored-By trailer ask** per CLAUDE.md policy. **Stops at:** commit + push completed + commit SHA + branch reported.

### `/deep-debug <slug> [focus-area-or-file-or-symptom]`

Invoke the **`senior-debugging-engineer`** for deep root-cause analysis on a specific failure. Use when a bug crosses domain boundaries (backend+frontend race, deploy failure with non-obvious cause, intermittent production bug, flaky test that resists standard debugging), when existing `senior-X-engineers` haven't pinned it down, or when reviewer-flagged bugs keep being overridden without understanding the root cause. The persona runs a hypothesis-driven 5-phase process (Reproduce → Hypothesize → Test each hypothesis → Root cause → Fix recommendation) and returns a structured report — **does NOT write the fix** (the relevant `senior-X-engineer` does that, against the report). **Stops at:** report shown + user picks: apply the fix / investigate further / sit on it / reject the diagnosis.

### `/caffeinate` and `/stop-caffeinate`

macOS-only display + system sleep prevention while Claude Code is working. Wraps the built-in `caffeinate -d -i` command — runs it in the background (detached via `nohup`), captures the PID at `~/.claude/caffeinate.pid`, and reports back. **`/stop-caffeinate`** reads the PID, sends SIGTERM, removes the pidfile. Idempotent (running stop when nothing is caffeinated is a benign no-op). Useful during long builds, the design phase, and any time you don't want your screen to dim while Claude is generating code. On Linux/Windows: error gracefully and point at the platform equivalent (`systemd-inhibit` / PowerShell power requests). **Stops at:** confirmation message with PID + start time.

### `/start-build <slug>`

Kicks off the build phase for a `green-lit-to-build` product. Invokes the `senior-software-engineer` persona (see §4) to ask three orientation questions in order:

1. **For hybrid briefs:** which to build first — API + web (recommended) vs. mobile first.
2. **Scope:** MVP build (recommended) vs. fully-featured build.
3. **First subsystem:** typically database design (recommended), with the full ordered list shown so you can override.

After your answers, the senior-software-engineer proposes the right specialist persona to invoke first and the specific first task. You confirm or override. The build then proceeds subsystem-by-subsystem, with the senior-software-engineer routing you to the right specialist at each handoff.

You can re-run `/start-build <slug>` at any point during the build if you want a fresh "where am I" + "what's next" prompt.

### `/documentation`

Renders a condensed in-terminal walkthrough of the workspace — covering the pipeline phases, slash commands, scripts, helper skills, workspace conventions, and the reviewer-decision model. Wraps the permanent **`DOCUMENTATION.md`** at the repo root, which is the deeper full reference.

**Personalized:** if you have existing artifacts (validation reports, scoping reports, briefs, etc.) the in-terminal rendering names them as the concrete examples — so when it explains `/validate-card`, it can reference your actual `validation-bench-watch.md` instead of using a placeholder.

**Special behavior:** **this is the only command that bypasses the first-launch onboarding interrupt** described in `CLAUDE.md` §Session continuity → Rule A. New users can read about the workspace (including the onboarding workflow and why it matters) before being prompted to populate `user-context/INTERESTS.md`. Every other command — `/scan`, `/discover`, `/menu`, etc. — triggers onboarding on the first message of a fresh session when `INTERESTS.md` is missing.

**Read-only:** the command never modifies any file. It surveys current state to personalize the rendering and then produces terminal output.

### `/menu`

Surfaces a quick menu of "what you can do right now" based on the current pipeline state. Lower-overhead than reading `HELP.md` end-to-end. **Stops at:** menu shown.

> Named `/menu`, not `/help`, because Claude Code has a built-in `/help` command that shows its own dialog and would shadow ours.

### `/acknowledge-contributing`

One-time confirmation that you've read `CONTRIBUTING.md` before editing tracked files in this repo. Required for everyone *except* the repo owner (identified by `git config user.email`). Creates a gitignored `.claude-acknowledged` marker. Personal-data folders (gitignored ones) never require this. See `CONTRIBUTING.md` § "Before you start" for the rationale.

### `/setup`

Pre-flight verification for a new clone or new machine. Checks: all required tools (git, claude code, gh, pandoc, typst, python, node), git identity, GitHub authentication, submodule initialization, the agent-skills persona file copies in `.claude/agents/`, and `.claude-acknowledged` status. **Pure verification — never modifies anything.** Surfaces a structured punch list of what's missing with the exact install command for each. Safe to run multiple times.

### `/status`

Complete pipeline-state snapshot — deeper than `/menu`. Shows: active scan with territory count, all active idea cards with statuses and ages, killed-card count, in-flight briefs with their design-path / build-support picks, latest trend report age, active design phases (research / brief / handoff state), and recent generated docs. **Read-only.** Surfaces 2-4 suggested next actions based on the snapshot at the end. Use when you want a full "where am I across all in-flight work" view before deciding what to do next.

### `/system-check`

Compares your machine against the workspace's hardware + tooling requirements. Pure read-only — no permissions needed. Wraps `scripts/check_system.py`.

**Output:** a comparison table with four columns per row — *required*, *recommended*, *your system*, *status* (✓ / ⚠ / ✗). Covers:

- **OS** — macOS 12+, Linux, or Windows+WSL
- **CPU architecture** — x86_64 or arm64
- **CPU cores (logical)** — 4 minimum, 8+ recommended
- **RAM** — 8 GB minimum, 16 GB+ recommended
- **Free disk at workspace** — 10 GB minimum, 25 GB+ recommended
- **Internet** — `api.anthropic.com` reachable (DNS resolution probe)
- **Python** — 3.10+ minimum, 3.11+ recommended
- **Node.js** — 20+
- **Required tools** — git, gh, pandoc, typst
- **Optional tools** — docker (for the dockerized Flask default)

After the table, Claude surfaces a plain-English summary keyed to the result: all-green ("you're ready"), warnings-only ("works but you'll feel limits on heavy tasks"), or failures ("address these before running the pipeline"). For failing rows, install commands are suggested per platform.

**Use when:** setting up a new machine, debugging a pipeline command that fails with cryptic "tool not found" or "version mismatch" errors, or answering the question "will this workspace run on my computer?".

**Read-only guarantees:** the script reads system info via Python stdlib (`platform`, `os`, `shutil`, `socket`) and read-only subprocess calls (`sysctl`, `/proc/meminfo`, `wmic`, `<tool> --version`). No file writes, no paid API calls, no network traffic beyond one DNS lookup.

### `/projects`

Lists every discovery-cycle project in your workspace (keyed by run-id) and offers actions on a chosen one — primarily **delete**. Wraps `scripts/projects.py`.

A *project* = the full set of artifacts keyed by a single run-id: `ideas/<run-id>/`, `ideas/killed/<run-id>/`, `market-research/<run-id>/`, plus for each slug from that run, `web-apps/<slug>/`, `mobile-apps/<slug>/`, and any `generated/**/*<slug>*` exports.

**Flow when you pick "Delete":**

1. Claude lists every file and folder that would be deleted, with a strong warning that the action is irreversible (files bypass the Trash).
2. **First confirmation** — *Continue to final confirmation* or *Cancel — keep this project*.
3. **Final confirmation** — *YES, DELETE PERMANENTLY* or *Cancel — do not delete*.
4. Only after BOTH confirmations does Claude invoke `python3 scripts/projects.py delete <run-id> --force`.

The two-step gate is intentional. The script also refuses (`exit 2`) if you try `delete` without `--force` from the command line — so a typo can't wipe a project.

**Use when:** cleaning up abandoned discovery cycles, verification-test runs, or any project you no longer want to keep on disk.

**Don't use for:** killing a single idea card (`/discover` puts killed cards in `ideas/killed/<run-id>/` automatically; that's the auditable kill path). `/projects` is for nuking whole projects, not individual cards.

### `/team <slug>`

List, name, or edit the **9 senior-engineer team members** for a product. The team is a fixed roster of long-running build-phase collaborators — the orchestrator (`senior-software-engineer`) + 8 specialists (`senior-system-design-engineer`, `senior-database-engineer`, `senior-backend-engineer`, `senior-frontend-engineer`, `senior-desktop-engineer`, `senior-qa-engineer`, `senior-devops-engineer`, `senior-security-engineer`). Backed by `scripts/team.py`.

**Per-product storage:** `<web-apps|mobile-apps|desktop-apps>/<slug>/team.json` — gitignored personal-data, never enters git. Each product gets its own team — useful when you have multiple products in flight and want different names per project to keep them straight in your head.

**Used by the build orchestrator** for narration. Named: "Paul (Senior Software Engineer) is invoking Maria (Senior Database Engineer) for the schema work." Unnamed: "Senior Software Engineer is invoking Senior Database Engineer for the schema work." Same narration shows up in `BUILD_STATUS.md` History entries and `build-milestone` audit-log descriptions.

**Two paths to naming:**

1. **Upfront via `/team <slug>`** — interactive: lists the team, lets you pick a row to name/edit, loops until you say done.
2. **Just-in-time** — `/start-build` prompts "name your `<Role>`?" the first time each persona is engaged on a product. The prompt only fires for personas whose name is still unset in `team.json`.

**`/team` UI loop:**

1. **Display the team** as a numbered table (1-9) with Role | Name (or "(unnamed)").
2. **Pick an action:**
   - **Name an unnamed member** — pick a row with no current name, set one.
   - **Edit an existing name** — pick a named row, replace the name.
   - **Reset all to unnamed** — clears every name in one shot (file stays; values blank out). Requires confirmation.
   - **Done — exit** — stops the command.
3. **For name/edit:** you reply with the row number (1-9) or the role key, then the new name. Validation: 1-30 chars, must start with letter/digit, allowed chars are letters / digits / spaces / hyphens / apostrophes. The check rejects empty strings, names over 30 chars, and special characters (which would break YAML/JSON escaping).

**No delete option.** The 9 roles are wired into the build orchestration; deleting one would break the workflow. You can reset names to unnamed (the role label is used in narration instead), but the role itself stays.

**`/team` requires the product folder to exist** — i.e., `/scope-mvp <slug>` must have run already. If you want to name your team before starting a build, that's fine — just make sure the brief has been drafted first.

### `/log [<text> | delete <id> | clear | type <type>]`

View, add, or delete entries in your personal-space audit log at `user-context/audit-log.jsonl`. The log is gitignored — it never leaves your machine. Wraps `scripts/audit_log.py`.

**What the audit log records (and only these):**

| Type | Auto-appended when | Effect |
|---|---|---|
| `onboarding-skip` | You pick "Prefer to update later" at first-launch onboarding | Gates the Rule A re-prompt — once present, onboarding will not fire again in future sessions until you delete it |
| `project-delete` | You confirm a destructive `/projects delete` | Records which run-id was wiped |
| `card-kill` | A card is killed during `/validate-card` or `/scope-mvp` | Queryable kill history; mirrors the card's frontmatter |
| `card-revive` | A killed card is restored to `ideas/` | Records the revival |
| `build-milestone` | A key build moment lands — project initialized via `/start-build`, a `BUILD_STATUS.md` subsystem flips to `[x]` (e.g., "authentication flow completed", "module X completed"), ready-to-deploy state reached, app shipped via `/ship-app` | Timeline of build achievements per product |
| `user-note` | Only via `/log <text>` | Free-text personal note |

The `build-milestone` description starts with the product's slug (e.g., `"Build milestone for findvil: authentication flow completed (session-cookie + bcrypt)"`), so `/log type build-milestone` gives you a chronological per-product build journal.

**What it does NOT record:** routine file reads, command invocations, status flips, commits. Git history covers those.

**Subcommand surface:**

| Invocation | Effect |
|---|---|
| `/log` | Show every entry, newest first. |
| `/log <free text>` | Append a `user-note` entry; print the new id. |
| `/log type <type>` | Filter the display to one type (e.g., `/log type onboarding-skip`). |
| `/log delete <id>` | Remove a single entry by id (with confirmation). Useful for re-enabling onboarding by deleting the `onboarding-skip` entry. |
| `/log clear` | Remove all entries (with confirmation). |

**File location:** `user-context/audit-log.jsonl` (created lazily on first write; gitignored). Each line is a JSON object: `{"timestamp": "...", "id": "...", "type": "...", "description": "..."}`. The `.example` template at `user-context/audit-log.jsonl.example` documents the format.

---

## 3. Skills

Skills are auto-invoked by Claude when relevant phrasing appears in your prompts.

### `doc-export`

Markdown → PDF (default engine: `typst`) or DOCX via pandoc. Output lands in `generated/<category>/<YYYY-MM-DD>-<slug>-<doc-type>.<ext>`.

**Prerequisites:** `brew install pandoc typst`.

**Trigger phrases:** "export this as PDF", "generate a docx of [artifact]", "give me a PDF of [artifact]".

### `web-preview`

Renders a Jinja template from a Flask project with fixture demo data and opens the result in Chrome. Includes a `render.py` template that gets scaffolded once per project, plus a per-page fixtures convention.

**Trigger phrases:** "preview this page", "show me what this template renders to", "open this in Chrome".

---

## 4. Reviewer and worker subagents

These live at `.claude/agents/<name>.md`. Most are invoked indirectly through slash commands; you don't call them directly. They all follow the same locked verdict format (verdict / confidence / findings / what-I-could-not-verify / sources) for consistency.

### Product domain (workspace-authored)

| Subagent | Lens | Invoked by |
|---|---|---|
| `product-viability-reviewer` | Does the problem exist with external evidence? | `/validate-card` |
| `product-competition-reviewer` | Real differentiation vs. actual incumbents (incl. non-obvious substitutes)? | `/validate-card` |
| `market-segment-reviewer` | Segment crisp / sized / reachable / broadly willing-to-pay? | `/validate-card` |
| `product-pricing-reviewer` | Is the specific proposed price defensible against comparable products, WTP signals, and solo-builder unit economics? Returns 2-3 strategic pricing options. | `/validate-card`, `/reprice` |
| `product-scope-reviewer` | Is the MVP scope honest (must-haves tied to riskiest assumption, no hidden scope creep)? | `/scope-mvp` |

### UI/UX domain (workspace-authored)

| Subagent | Lens | Invoked by |
|---|---|---|
| `ui-ux-researcher` | Produces the design-research report (worker, not reviewer). | `/research-design` |
| `design-brief-reviewer` | Brief completeness, sharpness, consistency with upstream. | `/draft-design-brief` |
| `design-fidelity-reviewer` | Captured Figma handoff against the approved brief (coverage, tokens, direction, accessibility). | (no slash command yet — invoke manually when you have a handoff to review) |

### Engineering (file copies from `external/agent-skills/`, re-synced via `scripts/update-agent-skills.sh`)

| Subagent | Lens | Invoked by |
|---|---|---|
| `code-reviewer` | 5-axis review (correctness, readability, architecture, security, performance). | `/scope-mvp` (at design time) + the agent-skills `/review` / `/ship` flows. |
| `security-auditor` | OWASP-style vulnerability audit. | The agent-skills `/ship` parallel-fan-out, or directly when security is in scope. |
| `test-engineer` | Test strategy, coverage, "Prove-It" pattern. | The agent-skills `/ship` parallel-fan-out, or directly. |

### Senior-engineer personas (workspace-authored — for the build phase)

These are roles, not single-shot reviewers. Invoked via `/start-build` and during the build by the senior-software-engineer as orchestrator.

| Persona | Role |
|---|---|
| `senior-software-engineer` | Generalist orchestrator. Asks orientation questions, routes to specialists, sequences subsystems, catches scope creep. |
| `senior-system-design-engineer` | System shape (monolith vs. split), data flow, cross-cutting concerns, decisions deferred. Produces SYSTEM_DESIGN.md. |
| `senior-database-engineer` | Schema, indexes, migrations, integrity. Produces SCHEMA.md. |
| `senior-backend-engineer` | ORM models, API contract, endpoint implementation, business logic, background jobs. Produces API_CONTRACT.md. |
| `senior-frontend-engineer` | UI implementation faithful to design tokens; covers Jinja+JS on web and RN on mobile. |
| `senior-qa-engineer` | Test coverage audits, integration at the seam, accessibility, release-readiness pass. |
| `senior-devops-engineer` | Deploy, CI/CD, observability, incident response, backups. |
| `senior-security-engineer` | Threat modeling, secure-coding review, auth design, infra hardening, security incident response. |

Each persona's file in `.claude/agents/senior-*.md` lists which agent-skills it commonly invokes. The senior personas are *roles*; the agent-skills are *workflows* those roles execute. They compose: a senior-backend-engineer doing a feature implementation uses `incremental-implementation`, `test-driven-development`, `api-and-interface-design`, and `code-review-and-quality` along the way without being asked.

### How invocation actually works

The Agent tool's `subagent_type` parameter has a fixed enum that does **not** include custom subagent names. The slash commands handle this with a workaround pattern documented in `CLAUDE.md` (the "Invoking custom subagents — the universal pattern" section): call `Agent({subagent_type: "general-purpose", ...})` and instruct the agent to read and follow the persona file at `.claude/agents/<name>.md`. Output is equivalent to a direct invocation. You don't need to do anything; the slash commands handle it.

---

## 5. Folders and where things live

| Folder | Purpose | Tracked by git? |
|---|---|---|
| `.claude/agents/` | Subagent persona files (plus three file copies — `code-reviewer.md`, `security-auditor.md`, `test-engineer.md` — synced from `external/agent-skills/`) | Yes |
| `.claude/commands/` | Slash command definitions | Yes |
| `.claude/skills/` | Project-local skill definitions (`doc-export`, `web-preview`) | Yes |
| `.claude/settings.json` | Project-level Claude Code permissions | Yes |
| `.claude/settings.local.json` | Your personal Claude Code overrides | **No** (gitignored) |
| `guides/` | Methodology + runbook documents | Yes |
| `external/agent-skills/` | git submodule pointing at the [agent-skills](https://github.com/aanifowose111/agent-skills) fork | Yes (as submodule ref) |
| `ideas/` | Your idea cards (`<slug>.md` plus optional `killed/<slug>.md`) | **No** (folder yes, contents no) |
| `market-research/` | Scan, triage, validation, scoping, trend reports | **No** (folder yes, contents no) |
| `web-apps/<slug>/` | Your Flask projects (or other web stack projects) | **No** (folder yes, contents no) |
| `mobile-apps/<slug>/` | Your React Native projects (or other mobile stack projects) | **No** (folder yes, contents no) |
| `generated/<category>/` | PDF/DOCX exports from `doc-export` | **No** (folder yes, contents no) |
| `CLAUDE.md` | Auto-loaded project context for Claude | Yes |
| `HELP.md` | This file | Yes |
| `README.md` | Public-facing landing | Yes |
| `LICENSE` | MIT | Yes |

The gitignored folders ship with a `README.md` (which documents the convention) and a `.gitkeep` placeholder so the directory structure survives even when contents don't.

---

## 6. Common gotchas

### 6.1 "Agent type not found"

You should not see this in normal use — the slash commands work around the Agent tool's enum restriction by invoking `general-purpose` with the persona file referenced. If you see it, you may be running an older slash command — pull the latest from `main`.

### 6.2 Web research permission prompts

The first time Claude runs a `WebFetch` or `WebSearch` in a session, macOS may prompt iTerm (or your terminal) for network access. Approve once; macOS remembers. After that, no further prompts for the same operations.

### 6.3 Submodule out of date after `git pull`

`git pull` doesn't auto-update submodules. If you see weird behavior, run:

```bash
git submodule update --init --recursive
```

To pull the latest agent-skills upstream:

```bash
git submodule update --remote external/agent-skills
git add external/agent-skills
git commit -m "Update agent-skills"
git push
```

### 6.4 `pandoc: typst not found` when exporting

You installed pandoc but not the PDF engine. Run:

```bash
brew install typst
```

If typst fails to render something complex (rare): `brew install tectonic` and pass `--pdf-engine=tectonic` instead. The `doc-export` skill documents both.

### 6.5 Personal data accidentally getting tracked

It shouldn't — the `.gitignore` covers `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `generated/` contents. If `git status` shows a personal file as tracked, check whether it matches a `!` (un-ignore) pattern in `.gitignore`.

### 6.6 `/discover` produces nothing useful with no args

It should produce idea cards even with no scan. If it doesn't, check:

- Is `CLAUDE.md` present and contains founder context?
- Is there a recent trend report at `market-research/trends-*.md`? (Optional but helpful.)
- Are recent kills at `ideas/killed/`? (Used as filter signal.)

If your context is genuinely empty, the lightweight scan will fall back to general SaaS / consumer / dev-tool territories. Improving the output is a matter of running `/scan` once to give it a richer territory map.

### 6.7 The first build is taking forever

Especially on mobile (EAS builds take 10-30 min). This is normal. The "scaffold-done" tag (per `guides/web/flask-mvp-scaffold.md` §5 step 9 and `guides/mobile/react-native-mvp-scaffold.md` §5 step 11) is the marker that you've left scaffolding for feature work — give it the time it deserves.

---

## 7. Recovery paths

### A reviewer's output is broken or ignored your card's claims

Re-read the persona file at `.claude/agents/<name>.md`. The persona's instructions are what's executed. If the instructions are wrong, edit them. If they're right but the reviewer drifted, re-run and add specific guidance in your prompt.

### `/scope-mvp` drafted a brief in the wrong stack

You missed the stack-confirmation step. Re-run `/scope-mvp <slug>` and explicitly state your stack at the start: "Use Next.js for web and Swift native for mobile, not the workspace defaults."

### A design brief went to the designer with mistakes

Update `<web-apps|mobile-apps|desktop-apps>/<slug>/design/DESIGN_BRIEF.md`, add a revision entry in §10 (the version log), re-export with `doc-export`, and re-send. The file in the repo is the source of truth even after copies have been shared.

### A killed card needs to come back

```bash
mv ideas/killed/<slug>.md ideas/<slug>.md
```

Then edit the frontmatter — change `status` back to `draft` and remove the `killed-reason` field. Add a new note about why it's being revisited (often it's a new trend that changes the picture).

### `git push` fails because the remote has new commits

Pull first, then push:

```bash
git pull --rebase origin main
git push origin main
```

If a merge conflict appears, resolve it in the affected files, then `git add` them and `git rebase --continue`.

### Claude Code crashed mid-session

Re-launch with `claude`. CLAUDE.md and MEMORY.md auto-load. State all in flight as files (not just in conversation), so restart is graceful — Claude reads the current state from disk.

---

## 8. Stack flexibility — quick reference

This workspace ships with build-domain guides for **dockerized Flask** (web) and **React Native + Expo** (mobile). These are the maintainer's defaults, not requirements. The methodologies (discovery, validation, scoping, design, market research, funding) are stack-agnostic.

**At `/scope-mvp` time**, Claude asks you which stack you want:

- **Pick the workspace defaults** → the existing `guides/web/flask-*` and `guides/mobile/react-native-*` apply directly.
- **Pick anything else** (Next.js, Django, Rails, Swift native, Kotlin native, Flutter, etc.) → Claude works from first principles + the stack-agnostic agent-skills skills. No `guides/web/<your-stack>-mvp-scaffold.md` exists yet, but you can author one and contribute it.

The brief records the chosen stack explicitly. The `product-scope-reviewer` calibrates effort against your shipped experience with the *chosen* stack, not against Flask/RN.

If you forked this workspace and want different defaults baked in:

- Edit `CLAUDE.md` (the "Stack flexibility" working-style bullet).
- Edit `guides/product/mvp-scoping-methodology.md` §6.0.
- Author new stack-specific scaffold/deploy/storage/auth guides for your stack and reference them from §6.0.
- The methodologies themselves don't need changing.

---

## 9. Internet access policy — quick reference

`WebFetch` and `WebSearch` are first-class tools in this workspace. Routine HTTPS searches and fetches happen **without** permission prompts (pre-approved in `.claude/settings.json`).

Claude asks before fetching only when:

- The URL is non-HTTPS.
- The URL looks unsafe or shortened to obscure the destination.
- The fetch would trigger cost (paid APIs, metered endpoints).
- The fetch is to an authenticated or private resource where you should confirm intent.

This applies to both the main Claude and all reviewer subagents — they're trusted to research freely within their scope. Citations from web research are required to appear inline in every reviewer finding.

---

## Utility scripts (auxiliary, not pipeline)

Scripts live at `scripts/` for tasks without a slash-command equivalent or for use outside Claude Code. **Commands take priority** for the actual pipeline work; scripts are plumbing.

**Python** (run from repo root):

```bash
python3 scripts/lint_pipeline.py        # validate pipeline state consistency (incl. slug collisions)
python3 scripts/new_idea_card.py        # interactive idea-card creator (alt to /discover)
python3 scripts/check_slug.py <slug>    # check if a product slug is available
python3 scripts/check_slug.py --list-all   # list every slug currently in use
python3 scripts/check_links.py          # check markdown links and @path references
python3 scripts/changelog_helper.py     # auto-generate CHANGELOG stub from git log
python3 scripts/report_summarizer.py    # pretty-print all reports in market-research/
```

**Shell** (run from repo root):

```bash
bash scripts/preflight.sh               # dependency + repo-state verification (like /setup)
bash scripts/setup-deps.sh              # install all required tools (idempotent)
bash scripts/update-agent-skills.sh     # pull agent-skills upstream and commit submodule SHA
bash scripts/backup-personal-data.sh    # tar gitignored folders (--encrypt available)
bash scripts/new-product-skeleton.sh <slug> <web|mobile|hybrid>  # scaffold a product folder
bash scripts/clean-killed-ideas.sh      # archive killed ideas older than N days
```

All scripts support `--help` and most support `--no-color`. Each script's source is heavily commented; see **[scripts/README.md](scripts/README.md)** for full descriptions, flags, and examples.

### When to reach for a script vs. a slash command

| Want to... | Use |
|---|---|
| Discover ideas, validate them, scope MVP, etc. | **Slash command** (`/discover`, `/validate-card`, `/scope-mvp`) |
| Set up a new clone or new machine | **Script** (`setup-deps.sh`, `preflight.sh`) — no Claude Code needed |
| Quick read of pipeline state without an agent round-trip | **Script** (`lint_pipeline.py`, `report_summarizer.py`) |
| Capture one specific idea you already have in mind | Either — `/discover` (full flow) or `new_idea_card.py` (faster, single card) |
| Back up your personal data | **Script** (`backup-personal-data.sh`) — no slash-command equivalent |
| Pull the latest agent-skills upstream | **Script** (`update-agent-skills.sh`) — no slash-command equivalent |
| Machine-readable output for tooling | **Script** with `--json` flag |

---

## Need something else?

- The full pipeline orchestration (every checkpoint, the design vs. validation MVP distinction, the parallel trend monitoring lane) is in `CLAUDE.md`'s "Pipeline orchestration & checkpoints" section.
- Each methodology guide in `guides/<domain>/` is a deep-dive into one piece of the pipeline.
- **Want to contribute to this workspace?** See [CONTRIBUTING.md](CONTRIBUTING.md) for the project philosophy, what to change vs. what not to change, required updates per change type, style conventions, and the PR process.
- **Want help with the actual build?** [Fijara](https://fijara.com) — Abiodun Anifowose's development service — can take a build on for you end-to-end. Surfaced at the `/scope-mvp` pre-build checkpoint, but you can ask Claude to bring it up at any point.
- For bugs, missing features, or improvement ideas, email aanifowose111@gmail.com (subject line `[discovery-to-ship feedback]`) or open a PR.
