---
description: Draft the implementation-ready DESIGN_SPEC.md for a product on the claude-led design path. Reads the signed-off design research, collects the user's picks (visual direction / palette / typography / pattern conventions to break / brand voice / portfolio continuity / answers to research's open questions), invokes the ui-ux-researcher in spec-writing mode to produce the spec, then invokes the design-spec-reviewer. Per guides/ui-ux/design-spec-methodology.md.
argument-hint: <product-slug>
---

You are about to draft the design spec for one product on the **claude-led** design path. Follow the methodology in @guides/ui-ux/design-spec-methodology.md exactly. The work is delegated to the `ui-ux-researcher` subagent in spec-writing mode (see @.claude/agents/ui-ux-researcher.md § Spec-writing mode). The reviewer is `design-spec-reviewer`.

**This command is the claude-led counterpart of `/draft-design-brief`** (which fires on the hired-designer path). The spec it produces is the build's source of truth — supersedes the `frontend-ui-engineering` skill's defaults.

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight checks

1. **Verify the brief exists** at `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, `desktop-apps/<slug>/MVP.md`, or any of those with `V1.md`. If none exists, stop and tell the user to run `/scope-mvp <slug>` first.
2. **Verify the brief's `design-path`** is `claude-led` (for MVP) or `claude-led-continued` (for V1). If it is `hired` / `pro-designer-engaged`, surface to the user:
   > Brief `design-path` is `<value>`. `/draft-design-spec` is for the claude-led path. For the hired-designer path, run `/draft-design-brief <slug>` instead. Continue anyway? (If the user wants to switch paths, they should update the brief's frontmatter first.)
3. **Verify design research exists** at `<product-folder>/design/DESIGN_RESEARCH.md` with `status: acted-on`. If the file is missing, tell the user to run `/research-design <slug>` first. If the file exists but `status` is not `acted-on`, tell the user to sign off on the research first (per `/research-design` checkpoint).
4. **Detect prior spec.** If `<product-folder>/design/DESIGN_SPEC.md` already exists, surface that to the user:
   > Prior spec found at `<path>`. This will be treated as a revision — the new draft will preserve the version log, increment a revision entry, and incorporate your new picks. Continue?

   Wait for confirmation.

### Step 1 — Collect the user's picks

Read the research's open questions (§Open questions in `DESIGN_RESEARCH.md`) and the three visual-direction options, three palette options, three typography pairings, and pattern-conventions list. Then ask the user, in **one structured message**, for the picks the spec depends on. Use this exact template (filling in the specifics from the research):

> Before I draft the spec, I need your picks. Reply with the following:
>
> 1. **Visual direction:** Option A (\<name\>), Option B (\<name\>), Option C (\<name\>), or a hybrid (specify what you'd combine).
> 2. **Color palette:** Option 1 (\<name\>), Option 2 (\<name\>), or Option 3 (\<name\>).
> 3. **Typography pairing:** Pairing 1, 2, or 3.
> 4. **Pattern conventions to break (with reasons):** of the "open for distinctive choice" patterns the research listed (\<list them\>), which do you want to break, and why?
> 5. **Brand voice (1-2 sentences, specific):** "Sober and direct, never enthusiastic" beats "friendly and professional." Give me the version copywriting works from.
> 6. **Portfolio continuity decision:** Echo findvil / fijara (name what carries across — typography, color family, logo style) OR stand independent (name what makes it independent).
> 7. **Answers to the research's open questions:** \<list each open question and ask for the answer\>.
> 8. **Dark mode scope:** Light-only at MVP / Light + dark from day one / Dark-only.
> 9. **Self-host fonts or CDN:** Self-host (recommended; privacy + speed) or use Google Fonts / Adobe Fonts CDN.

Stop and wait for the user's reply.

### Step 2 — Invoke the ui-ux-researcher in spec-writing mode

Once the user replies, invoke `ui-ux-researcher` using the custom-subagent invocation pattern in `CLAUDE.md`:

```
Agent({
  subagent_type: "general-purpose",
  description: "Draft DESIGN_SPEC.md for <slug>",
  prompt: "You are about to act as the ui-ux-researcher in SPEC-WRITING MODE. Step 1: read .claude/agents/ui-ux-researcher.md in full and treat its body as your role — pay particular attention to the 'Spec-writing mode' section. Step 2: read guides/ui-ux/design-spec-methodology.md for the exact format. Step 3: read <product-folder>/design/DESIGN_RESEARCH.md (must be status: acted-on), <product-folder>/MVP.md (or V1.md), and CLAUDE.md. Step 4: use these user picks to lock §1 of the spec: visual direction=<X>, palette=<Y>, typography=<Z>, pattern-conventions-to-break=<list>, brand-voice=<exact text>, portfolio-continuity=<exact text>, dark-mode-scope=<X>, font-loading=<self-host|cdn>, plus answers to research's open questions: <list>. Step 5: write DESIGN_SPEC.md at <product-folder>/design/DESIGN_SPEC.md using the §3 format from the spec methodology — all sections required: tokens (color + typography + spacing + radius + shadow + motion), icon library + install + usage convention, image-asset prompts (BATCH-LATER: write all prompts at once with _IMG_<NAME>_URL env-var slots; do NOT pause per image), responsive specs, per-surface specs (one block per surface from DESIGN_RESEARCH.md §Surfaces), component patterns, a11y floor, implementation notes, open questions (if any), version log initialized. Step 6: verify every text-on-background combo passes WCAG AA contrast (cite the ratio for each). Step 7: set frontmatter status: in-review. Step 8: return the path to the file and a short summary (locked direction, surfaces covered, components specced, any open questions left)."
})
```

Wait for the researcher to return.

### Step 3 — Invoke the design-spec-reviewer

Once the spec is written, invoke `design-spec-reviewer` using the same custom-subagent pattern:

```
Agent({
  subagent_type: "general-purpose",
  description: "Review DESIGN_SPEC.md for <slug>",
  prompt: "You are about to act as the design-spec-reviewer. Step 1: read .claude/agents/design-spec-reviewer.md in full and treat its body as your role, lens, process, and output format. Step 2: read the spec at <product-folder>/design/DESIGN_SPEC.md and the research at <product-folder>/design/DESIGN_RESEARCH.md and the brief at <product-folder>/MVP.md (or V1.md). Step 3: apply your completeness + accessibility + implementation-readiness tests. Step 4: return your output in the locked verdict format (APPROVE / APPROVE-WITH-NOTES / REJECT with confidence level + top findings)."
})
```

Wait for verdict.

### Step 4 — Integrate the verdict

Add the verdict + date to the spec's §11 version log as a "Reviewed by design-spec-reviewer" entry. Carry the reviewer's findings forward as notes attached for the user to address.

### Stop here — user checkpoint

After the reviewer returns, **stop**. Do not advance the spec's `status` past `in-review`. Do not start the build. Show the user:

> Design spec at `<product-folder>/design/DESIGN_SPEC.md`.
>
> Reviewer verdict: **\<APPROVE | APPROVE-WITH-NOTES | REJECT\>**
> Confidence: \<LOW | MEDIUM | HIGH\>
>
> Locked direction: \<visual direction\> + \<palette\> + \<typography pairing\>
> Surfaces covered: \<list\>
> Components specced: \<count\>
> Image prompts to generate (batch later): \<count\> — env vars: \<list\>
>
> Top findings:
> 1. \<finding 1\>
> 2. \<finding 2\>
> 3. \<finding 3\>
>
> (If REJECT or APPROVE-WITH-NOTES, surface the specific gaps for you to address.)
>
> Your call:
> - **Sign off** → I update §11 with your sign-off and set `status: acted-on`. Next step: `/start-build <slug>` (the build will use this spec as authority — supersedes `frontend-ui-engineering` defaults).
> - **Revise specific sections** → tell me what to change; I edit and re-invoke the reviewer.
> - **Reject and re-draft from scratch** → rare; usually means your picks have shifted. Tell me which picks have changed.

Only after the user signs off, update the spec's `status` field to `acted-on` and add the sign-off date to §11.

### Notes for the main Claude

- The spec's job is to be the *one document* the build implements UI from. Resist any urge to also produce a separate Figma file or component code from this command — that comes during build.
- **Image-asset prompts use the batch-later default** — Claude writes all prompts into §4 of the spec with env-var slots. The user generates the images at their own pace and pastes URLs into `.env`. The build proceeds with placeholder colored blocks until URLs are set.
- If the user's picks contradict the research (e.g., they want a palette the research did not surface), surface that before drafting — they may want a fresh research pass or to anchor the contradiction explicitly. Do not invent a fourth direction silently.
- The spec is Markdown — same readability win as the brief. Tokens are real CSS so they can be copy-pasted into `static/css/tokens.css` (or the RN/PySide6 equivalent) when the build starts.

### Audit-log auto-append (optional)

This command does not auto-append to the audit log. The user can run `/log type design-milestone "Spec acted-on for <slug>"` if they want to mark it.
