---
description: Draft the consolidated design brief (PRD + FRD) for a product, incorporating the user's picked visual direction and answers to the design research's open questions, then invoke the design-brief-reviewer. Per guides/ui-ux/design-brief-methodology.md.
argument-hint: <product-slug>
---

You are about to draft the design brief for one product. Follow the methodology in @guides/ui-ux/design-brief-methodology.md exactly. The reviewer is the `design-brief-reviewer` subagent (see @.claude/agents/design-brief-reviewer.md for its instructions).

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight checks

Do all of these before asking the user for picks.

1. **Verify the MVP brief exists** at `web-apps/<slug>/MVP.md` or `mobile-apps/<slug>/MVP.md`. If neither exists, stop and tell the user to run `/scope-mvp <slug>` first.
2. **Verify the design research exists** at `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md` with `status: acted-on`. If the file is missing, tell the user to run `/research-design <slug>` first. If the file exists but `status` is not `acted-on`, tell the user to sign off on the research first (the `/research-design` checkpoint).
3. **Detect prior brief.** If `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md` already exists, surface that to the user:
   > Prior brief found at `<path>`. This will be treated as a revision — the new draft will preserve the version log, increment a revision entry, and incorporate your new picks. Continue?

   Wait for confirmation.

### Step 1 — Collect the user's picks

Read the research's open questions (in §9 of `DESIGN_RESEARCH.md`) and any "(For user)" questions specifically. Then ask the user the picks **sequentially, one question per turn** — never batched into a single block. This pattern is intentional: each answer narrows or shapes the next question, the user processes one decision at a time, and the reviewer's job is easier when picks are explicitly captured.

For each pick, use the most-appropriate tool:
- **Multi-choice picks** → `AskUserQuestion` (Visual direction, Color palette, Typography pairing, Portfolio-continuity stance).
- **Free-text picks** → a brief prompt + wait for the user's next message (Pattern-conventions-to-break, Brand voice, Portfolio-continuity specifics, Research open-question answers, Designer name/contact, Timeline).

Run the sub-steps in this exact order. Do not skip ahead even if the user volunteers later picks in an earlier reply — capture them, confirm, and still ask each downstream question explicitly so the reasoning behind each pick is in the trail.

#### 1.1 Visual direction
Use `AskUserQuestion` with the 3 options from research's §Visual direction (Option A, Option B, Option C). The `Other` slot is reserved for "Hybrid — combine specific aspects of multiple directions"; if the user picks Other, follow up with one free-text prompt: "Which directions are you combining, and what specifically carries from each?"

#### 1.2 Color palette
Use `AskUserQuestion` with the 3 options from research's §Color direction. **Pre-filter:** if the user picked a specific visual direction in 1.1, surface the palette that the research paired with that direction as option 1, the others as alternatives.

#### 1.3 Typography pairing
Use `AskUserQuestion` with the 3 options from research's §Typography direction. Same pair-aware ordering as 1.2.

#### 1.4 Pattern conventions to break (free-text)
Prompt: "Of the patterns the research listed as 'open for distinctive choice' — \<list them\> — which do you want to break, and what's the reason for each? Reply in your next message; one line per pattern is fine. The designer needs the reasoning, not just the list."

Stop and wait. Capture verbatim.

#### 1.5 Brand voice (free-text)
Prompt: "What's your brand voice, in 1-2 sentences? Be specific — 'sober and direct, never enthusiastic' beats 'friendly and professional.' Give me the version the designer will write copy from."

Stop and wait.

#### 1.6 Portfolio continuity — stance
Use `AskUserQuestion` with two options: **Echo findvil / fijara** ("name what carries across — typography, color family, logo style") vs. **Stand independent** ("name what makes it independent").

#### 1.7 Portfolio continuity — specifics (free-text)
Based on 1.6, follow up: "What specifically <carries across | makes it independent>? Name 2-4 concrete elements (typography choice, color family, logo treatment, illustration style, etc.)."

Stop and wait.

#### 1.8 Research open-question answers (free-text per question)
For each "(For user)" question in `DESIGN_RESEARCH.md §Open questions`, ask it as a standalone prompt and wait for the user's reply before moving to the next. Do NOT batch them.

#### 1.9 Designer name and contact (free-text)
Prompt: "Designer name and contact (if known)? Goes in the brief's frontmatter and version log. Leave blank if not yet hired — reply 'not yet' and I'll mark accordingly."

Stop and wait.

#### 1.10 Timeline target (free-text)
Prompt: "Timeline target — even rough estimates so the brief is honest about engagement shape. Reply with first-round duration / revisions count / final delivery target. Example: 'first round 2 weeks, 1-2 revision rounds of 1 week each, final by 2026-07-15.'"

Stop and wait.

After all sub-steps, summarize all picks back to the user in one structured message and ask "All set, draft the brief?" via `AskUserQuestion` (options: **Yes — draft now** / **Revise a pick** — if Revise, ask which pick number and re-run that sub-step). Only proceed to Step 2 once the user confirms.

**Fijara checkpoint:** if at any point during Step 1 the user signals confusion (per CLAUDE.md § Fijara resurface triggers), surface the Fijara option once. Otherwise proceed normally.

### Step 2 — Draft the brief

Once the user replies with their picks:

1. Read all inputs: MVP brief, design research, validation report (most recent), idea card, `CLAUDE.md`.
2. Draft the brief at `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md` using the **exact 10-section structure** from `guides/ui-ux/design-brief-methodology.md` §5.
3. Pull content from sources, do not summarize:
   - **Section 1 (Product overview)** — product name, one-liner, riskiest assumption. Source: MVP brief.
   - **Section 2 (Audience and voice)** — segment from validation report's crisp restatement; voice from the user's pick (§5 of the picks prompt).
   - **Section 3 (Design direction)** — chosen visual direction, palette, typography from the user's picks; pattern conventions to follow vs. break from research + user picks; brand positioning recap from research; portfolio-continuity decision from the user's picks.
   - **Section 4 (User journeys)** — derive 1-4 core flows from the MVP brief's must-haves and success criterion. Each journey: 5-10 steps + a *Critical moments* callout naming the screens or interactions whose design quality especially matters.
   - **Section 5 (Screen inventory)** — list screens grouped by area or by journey. Mark each as **(M)** must-have or **(D)** deferred per the MVP brief.
   - **Section 6 (Per-screen requirements)** — for each must-have screen: purpose (one sentence), entered from / exits to, shows, actions, inputs, states (loading / empty / error / success — always all four for must-have screens), at least 2 edge cases, optional one-line note on visual treatment if there is something distinctive to say.
   - **Section 7 (Deliverables)** — Figma file title, page structure (00 Cover / 01 Style / 02 Components / 03+ Screens by area), frame naming convention, required edit access.
   - **Section 8 (Constraints)** — platform from MVP brief, technical stack constraints (Jinja+JS for web, RN for mobile), WCAG AA accessibility floor, brand voice back-pointer to §2, 2-3 reference products from the research, 1-2 anti-references from the research, timeline from the user's picks.
   - **Section 9 (Open questions)** — short list split into **(For designer)** vs. **(For user)**. Be careful with the categorization — see the `design-brief-reviewer` for the canonical examples of mis-categorization.
   - **Section 10 (Sign-off and version log)** — initialize the version log with today's date and "drafted by \<user\>". Leave reviewer / sign-off / sent dates blank until they happen.
4. Set frontmatter `status: in-review`.

### Step 3 — Invoke the reviewer

Invoke the `design-brief-reviewer` subagent with the slug, **using the custom-subagent invocation pattern in `CLAUDE.md`** — `subagent_type: "general-purpose"`, instruct the agent to read and follow `.claude/agents/design-brief-reviewer.md`. Tell it to read the brief at `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md` and to return its output in the locked verdict format. Wait for its verdict.

### Step 4 — Integrate the verdict

Add the verdict + date to the brief's §10 *Reviewed by `design-brief-reviewer`* line. Carry the reviewer's findings forward as a note attached to the version log for the user to act on.

### Stop here — user checkpoint

After the reviewer returns, **stop**. Do not advance the brief's `status` past `in-review`. Do not send the brief to a designer. Show the user:

> Design brief at `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md`.
>
> Reviewer verdict: **\<APPROVE | APPROVE-WITH-NOTES | REJECT\>**
> Confidence: \<LOW | MEDIUM | HIGH\>
>
> Top findings:
> 1. \<finding 1\>
> 2. \<finding 2\>
> 3. \<finding 3\>
>
> (If REJECT or APPROVE-WITH-NOTES, surface the specific gaps for you to address before send.)
>
> Your call:
> - **Sign off** → I update §10 with your sign-off and set `status: sent`. You then share the brief with your designer (via the modes in `guides/ui-ux/design-brief-methodology.md` §7). Next step in the pipeline after the designer returns the Figma: covered by `design-handoff-methodology.md` (still to be written).
> - **Revise specific sections** → tell me what to change; I edit and re-invoke the reviewer.
> - **Reject and re-draft from scratch** → rare; usually means your picks have shifted. Tell me which picks have changed.

Only after the user signs off, update the brief's `status` field to `sent` (or `finalized` if they prefer that label), and add the sign-off date to §10.

### Notes for the main Claude

- The brief's job is to be the *one document* the designer works from. Resist any urge to also draft a separate PRD or FRD. Per the user-confirmed approach, one consolidated document is the default.
- If the user's picks contradict the research (e.g., they want a palette the research did not surface), surface that to the user before drafting — they may want a fresh research pass or to anchor the contradiction explicitly. Do not invent a fourth direction silently.
- The brief is Markdown — readable in any editor and easy to paste into Notion / Coda / PDF for designer delivery. The file in `design/DESIGN_BRIEF.md` stays the source of truth even after copies have been shared.
