---
description: Draft an MVP brief for a green-lit card, invoke the scope and code reviewers, and integrate verdicts, per guides/product/mvp-scoping-methodology.md.
argument-hint: <card-slug>
---

You are about to scope an MVP for a green-lit card. Follow the methodology in @guides/product/mvp-scoping-methodology.md exactly.

**Arguments:** $ARGUMENTS — the card slug. The card must exist at `ideas/<run-id>/<slug>.md` (locate it with `find ideas -name "<slug>.md" -not -path "*/killed/*"`) with `status: green-lit`.

### Inputs to read before drafting
- The card: locate via `find ideas -name "<slug>.md" -not -path "*/killed/*"` → gives you `ideas/<run-id>/<slug>.md`. **Extract `<run-id>` from this path.**
- The validation report: at `market-research/<run-id>/validation-<slug>.md` (same `<run-id>` as the card). If multiple validations exist for this slug (rare — would mean re-validations), use the most recent by mtime.
- @guides/product/mvp-scoping-methodology.md (for the brief format and reviewer pair)
- @CLAUDE.md (for stack defaults and working style)
- The most recent `market-research/*/trends.md` (if any) — check for encroachment findings that affect this card

### Do
1. Verify the card is `green-lit`. If not, stop and surface the gap to the user.
2. Decide `domain: web | mobile | desktop | hybrid` based on the card.
3. **Confirm the stack choice with the user** before drafting. Read §6.0 of `guides/product/mvp-scoping-methodology.md`. If the user has not already stated a stack choice in their prompt to `/scope-mvp`, ask explicitly:

   > Before I draft the brief, what stack do you want to use for this product?
   >
   > Workspace defaults (this is what the build-domain guides cover):
   > - **Web:** dockerized Flask + Jinja + vanilla JS (Python)
   > - **Mobile:** React Native + Expo + TypeScript
   > - **Desktop:** Python + PySide6 + PyInstaller (per `guides/desktop/python-mvp-scaffold.md`)
   >
   > Alternatives you could pick (no workspace guide for these — Claude will work from first principles + the agent-skills stack-agnostic skills):
   > - **Web:** Next.js, Django, Rails, Phoenix, FastAPI, Go (Gin/Echo), Java (Spring), Angular, Vue, SvelteKit, …
   > - **Mobile:** Swift native, Kotlin native, Flutter, …
   > - **Desktop:** C# + Avalonia, Electron, Tauri, Python + Flet, Qt C++, …
   >
   > Reply with your picks (one per domain in the brief). The brief's *Stack* section will record them, and the product-scope-reviewer will assess fit against your shipped experience — not against the workspace defaults.

   Wait for the user's reply before proceeding.

4. Draft the MVP brief at the right location:
   - `web-apps/<slug>/MVP.md` for web
   - `mobile-apps/<slug>/MVP.md` for mobile
   - `desktop-apps/<slug>/MVP.md` for desktop
   - For hybrid briefs covering multiple domains, the canonical brief lives in the primary-domain folder (whichever was picked as "build-first" per `/start-build`'s orientation); cross-references go in the other domain's folder.
4. Fill the brief per the §5 template in the scoping guide. Set `status: in-scoping`. Identify the riskiest assumption, must-haves (each traced to the assumption), could-haves, won't-haves, stack, infrastructure decisions (`.env`, DO Spaces, hosting, auth), success criterion (first-10-users measurable), effort estimate, stack stretches.
5. Invoke the reviewer pair in parallel, **using the custom-subagent invocation pattern in `CLAUDE.md`** — each call uses `subagent_type: "general-purpose"` and instructs the agent to read and follow the relevant persona file:
   - For scope discipline: read and follow `.claude/agents/product-scope-reviewer.md`
   - For architecture / security / performance: read and follow `.claude/agents/code-reviewer.md` (this is the agent-skills `code-reviewer` persona, file-copied into `.claude/agents/` per `.claude/agents/README.md`)
   - For mobile or hybrid briefs, also invoke `mobile-ux-reviewer` *if and only if it exists in `.claude/agents/`* (we have not built it yet — skip otherwise and note the skip in the report)

   Each agent should be told to read the brief at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md`, the validation report, the scoping methodology guide, and `CLAUDE.md` — and to return its output in the locked verdict format.
6. Integrate per §8 of the scoping guide.
7. Write the scoping report to `market-research/<run-id>/scoping-<slug>.md` (same `<run-id>` as the card's discovery cycle) per §9. Add `slug: <slug>`, `run-id: <run-id>`, `date-scoping: <YYYY-MM-DD>` to the frontmatter. The MVP brief itself (`<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md`) stays where it is — it's a per-product artifact, not a cycle artifact.


### Stop here — user checkpoint #1: review the scoping verdict
After writing the report, **stop**. Do not advance the brief to `green-lit-to-build`. Show the user:

> MVP brief at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md`.
> Scoping report at `market-research/<run-id>/scoping-<slug>.md`.
>
> Combined verdict: <APPROVE / APPROVE-WITH-NOTES / REJECT>
> Notes carried forward: <summary>
>
> Your call:
> - Advance to `green-lit-to-build`
> - Revise the brief and re-review
> - Kill or send back to validation

Update the brief's `status` and the report's *Decision* section only after the user has decided.

**If the user picks Kill**, also append a `card-kill` audit-log entry (per `CLAUDE.md` § Audit log): `python3 scripts/audit_log.py add card-kill "Killed card <slug> at MVP scoping (run-id: <run-id>). Reason: <one-line user reason>."`. This is in addition to moving the card to `ideas/killed/<run-id>/<slug>.md`.

### Stop here — user checkpoint #2: pre-build decisions (only if advanced)

Once the user signs off on `green-lit-to-build`, ask two more questions **before any build work begins**. Both at once:

> Brief is green-lit-to-build. Two quick decisions before the build starts:
>
> **1. Design path** — how do you want the product's look-and-feel handled?
>
>    a) **Generic but unique design** — I'll handle the UI directly in code, with care to avoid the AI-generic aesthetic (no defaulting to soft pastels + rounded corners; tasteful palette and typography choices grounded in the product context, applying agent-skills' `frontend-ui-engineering` principles). **Faster path**; skips the full design phase. Recommended for first-pass MVPs where validation is the primary goal. (If you want, I can still produce a lightweight design-direction *reference* — palette + typography picks — without the full brief and designer handoff.)
>
>    b) **Engage a human UI/UX designer** — Full design workflow: I produce a design research report → a consolidated design brief → you brief the designer → they deliver a Figma → I implement from the handoff. **Slower, more polish.** Recommended once the product has been validated with first users.
>
> **2. Build support** — will you follow along with the build (reviewing the code, running things on your machine, deploying), or would you like expert help?
>
>    - **I'll follow along** → I write the code; you review and run things on your machine. Standard path for software engineers and technical founders.
>    - **I need help** → [Fijara](https://fijara.com) — Abiodun Anifowose's development service — can take the build on for you. (You can still continue with me directly if you prefer; just say the word.)
>
> Reply with your picks for both.

Based on the user's reply:

| Design pick | Next step to surface |
|---|---|
| (a) Generic-but-unique | "No further design command needed. I'll apply a lightweight palette + typography pick when the build starts. You can run `/research-design <slug>` later if you change your mind." |
| (b) Engage designer | "Next step: run `/research-design <slug>` to produce the design-direction report. After you sign off, run `/draft-design-brief <slug>` to draft the brief for the designer." |

| Build pick | Next step to surface |
|---|---|
| I'll follow along | "Proceed with build whenever you're ready — open the brief and the scaffold guide for your chosen stack (per `mvp-scoping-methodology.md` §6.0) and we'll go step by step." |
| I need help | Friendly Fijara message — example: "Got it. [Fijara](https://fijara.com) — Abiodun's dev service — handles builds like this end-to-end. Reach out to them whenever you're ready. If you change your mind and want to drive the build yourself later, just say so and I'll continue with you." |

Record both picks in the brief's frontmatter as `design-path: generic|hired` and `build-support: self|fijara` so future sessions know the choices made. Then stop. Do not auto-invoke `/research-design` or start the build.
