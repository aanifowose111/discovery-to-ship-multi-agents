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

Read the research's open questions (in §9 of `DESIGN_RESEARCH.md`) and any "(For user)" questions specifically. Then ask the user, in **one structured message**, for the picks the brief depends on. Use this exact template (filling in the specifics from the research):

> Before I draft the brief, I need your picks. Reply with the following:
>
> 1. **Visual direction:** Option A (\<name\>), Option B (\<name\>), Option C (\<name\>), or a hybrid (specify what you'd combine).
> 2. **Color palette:** Option 1 (\<name\>), Option 2 (\<name\>), or Option 3 (\<name\>).
> 3. **Typography pairing:** Pairing 1, 2, or 3.
> 4. **Pattern conventions to break (with reasons):** of the "open for distinctive choice" patterns the research listed (\<list them\>), which do you want to break, and why?
> 5. **Brand voice (1-2 sentences, specific):** "Sober and direct, never enthusiastic" beats "friendly and professional." Give me the version the designer should write copy from.
> 6. **Portfolio continuity decision:** Echo findvil / fijara (name what carries across — typography, color family, logo style) OR stand independent (name what makes it independent).
> 7. **Answers to the research's open questions for you:** \<list the research's "(For user)" questions and ask for each answer\>.
> 8. **Designer name and contact (if known):** so the brief's frontmatter and version log are accurate. Leave blank if not yet hired.
> 9. **Timeline target:** first round / revisions / final — even rough targets, so the brief is honest about the engagement shape.

Stop and wait for the user's reply.

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
