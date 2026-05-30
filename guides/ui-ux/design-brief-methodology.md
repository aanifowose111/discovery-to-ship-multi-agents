# Design brief methodology

How the **consolidated PRD + FRD document** the human designer actually receives is structured, drafted, and reviewed. The brief is the *one* document the designer works from. Everything else (MVP brief, design research, validation report) is reference material; the design brief is the source of truth on what to design and why.

Per the user-confirmed approach, this workspace produces **one consolidated brief**, not separate PRD and FRD documents. If a hired designer specifically asks for them split, we split at that point. Otherwise, one document means one place to update when scope shifts.

---

## 1. Purpose

The brief exists so the designer can do their best work in the fewest revision rounds. A vague brief produces beautiful designs of the wrong product. An exhaustive brief produces designer disengagement. The right brief is **sharp, opinionated about intent, and lean on prescribed pixels** — it says clearly what each screen exists to do, what the product feels like, and what the constraints are, then lets the designer's craft fill in everything else.

The brief covers, in one document:

- **PRD content** — who the product is for, what problem it solves, what success looks like, what the riskiest assumption is, what voice the product speaks in.
- **Design direction** — the visual direction picked from the research, the chosen palette, the chosen typography, the pattern conventions to follow or break.
- **FRD content** — user journeys end-to-end, the screen inventory, what each screen does, what data and actions each one has, the states each one supports (loading, empty, error, success).
- **Deliverables expected** — exactly what the designer is asked to produce, in what Figma shape, with what file access.
- **Constraints** — platform, technical (must be implementable in Jinja + vanilla JS or in RN), accessibility, brand voice, timeline.
- **Open questions** — anything the brief deliberately leaves to the designer's judgment, plus anything still unresolved that the user needs to answer before the designer starts.

---

## 2. Operating principles

1. **One document. One source of truth.** When scope shifts, the brief is the artifact you edit. Do not keep duplicate copies of any of its sections elsewhere.
2. **Sharpness beats comprehensiveness.** A 5-page sharp brief beats a 20-page exhaustive one. If a section has nothing distinctive to say beyond "make it good," cut it.
3. **Purpose anchors each screen.** Every screen-spec entry begins with *what this screen exists to do*, not *what it shows*. A screen without a purpose statement is a screen the designer cannot honestly design.
4. **User journeys come before screen lists.** A flat list of 12 screens with no journey is hard to design from. Journeys connect intent to screens.
5. **States are first-class.** Loading, empty, error, success — each one designed deliberately. "Just make a loading state" is a sign nobody thought about the loading moment.
6. **Constraints liberate.** "Must be implementable in Jinja + vanilla JS" or "Must look credible to procurement" tightens choices productively. State them.
7. **The brief is opinionated about the product, deferent about the craft.** Tell the designer what the product needs to *do* and *feel like*. Do not tell them which Figma plugin to use or which corner radius to apply.
8. **Per the internet access policy in `CLAUDE.md`, web research happens by default** — the brief may need additional references during drafting.

---

## 3. When to draft a brief

Draft the brief when **all** of these are true:

- The MVP brief at `<web-apps|mobile-apps>/<slug>/MVP.md` exists with `status: green-lit-to-build` (or earlier, if doing pre-validation design exploration with the user's explicit OK).
- The design research at `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md` exists with `status: acted-on` — i.e., the user has signed off on the research, and a visual direction has been picked (or at least narrowed).
- The "Open questions for the designer" in the research report have been answered by the user (brand voice, name/logo expectations, platform constraints, partner constraints).

If any of these are missing, surface the gap to the user before drafting. Drafting a brief on incomplete inputs produces a brief the user will reject for things that were missing at the input stage.

---

## 4. Inputs

To draft a brief, read:

| Input | Source |
|---|---|
| The MVP brief | `<web-apps|mobile-apps>/<slug>/MVP.md` |
| The design research | `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md` |
| The validation report | `market-research/validation-<slug>-*.md` (most recent) |
| The idea card | `ideas/<slug>.md` |
| Founder context | `CLAUDE.md` + user-profile memory (prior shipped designs as reference) |
| User's answers to the research's "Open questions for the designer" | Provided by the user when invoking the brief drafting |
| User's picked visual direction | Provided by the user (Option A / B / C from the research, or a hybrid) |

The brief consolidates these — it does not summarize all of them. It includes only what the designer specifically needs.

---

## 5. The brief structure (canonical sections)

This is the locked structure of the brief document. Every brief has these sections, in this order. Section bodies vary; the structure does not.

### Frontmatter

```yaml
---
slug: <product slug>
domain: web | mobile | hybrid
date-drafted: YYYY-MM-DD
date-sent-to-designer: <YYYY-MM-DD or null>
designer: <name and contact, when known>
status: draft | in-review | sent | revising | finalized
research-source: design/DESIGN_RESEARCH.md
mvp-source: ../MVP.md
---
```

### Section 1 — Product overview

One paragraph stating: the product name, the one-line description (matches MVP brief), and the riskiest assumption it tests. Designed so the designer knows the *bet* the design has to support.

### Section 2 — Audience and voice

- **Audience:** one paragraph naming the segment (matches the validation report's crisp restatement — designer should see who this design is for).
- **Voice:** one paragraph describing how the product *talks* — sober, warm, confident, technical, playful, urgent, calm. Voice and visual direction co-determine the design.

The voice section gets used for UI copy decisions (button labels, empty-state messages). Sharp voice produces consistent micro-copy across screens.

### Section 3 — Design direction

This is where the design research becomes a directive.

- **Chosen visual direction:** the option name from the research (e.g., "Editorial restraint" — Option A from `DESIGN_RESEARCH.md`) and a paragraph re-stating its mood and what it deliberately does not do.
- **Color palette:** the picked palette from the research, with concrete colors (hex), purpose per color (primary, secondary, neutrals, semantic).
- **Typography:** the picked pairing — body face, display face, with sources and licenses.
- **Pattern conventions:**
  - Follow these: <list from research §6 "Follow these">
  - Break these (with reason): <list from research §6 "Open for distinctive choice" plus the user's pick of which to break>
- **Brand positioning recap:** one paragraph on where this product sits relative to competitors.
- **Portfolio continuity decision:** the user has answered the research's continuity question — record the answer here. If "echo prior products," name what carries across (typography, color family, logo style). If "stand independent," name what makes it independent.

### Section 4 — User journeys

The 1-4 core flows end-to-end. **Journeys come before screen lists.** Each:

```markdown
### Journey N: <first-time user completes [core action]>
1. Arrives at <where> via <how — link, ad, referral, etc.>
2. Sees <what> — first impression should communicate <what>
3. Takes action: <specific action>
4. Receives <feedback>
5. ...
N. Reaches <end state>

**Critical moments (design needs to support):**
- <moment that makes or breaks the journey, with rationale>
- <another moment>
```

The "critical moments" callout flags the screens or interactions whose visual / interaction quality especially matters. The designer prioritizes there.

### Section 5 — Screen inventory

A flat list of the screens the design needs to cover, grouped by journey or by area. Numbered for cross-reference from §6.

```markdown
**Authentication area:**
1. Login
2. Signup
3. Password reset

**Main app:**
4. Home / dashboard
5. <feature> list
6. <feature> detail
...
```

Mark screens that are **must-have for MVP** (M) vs. **deferred** (D) so the designer knows where to invest depth.

### Section 6 — Per-screen requirements

For each screen in the inventory:

```markdown
### Screen N: <name>
- **Purpose:** what this screen exists to do (one sentence)
- **Entered from:** <list of origins>
- **Exits to:** <list of destinations>
- **Shows:** <primary content>
- **Actions available:** <list>
- **Inputs (if any):** <field list with rough type — text, email, file, etc.>
- **States to design:**
  - Loading
  - Empty (if applicable)
  - Error (with one specific error example)
  - Success
- **Edge cases the designer should consider:**
  - <e.g., long names, missing data, very-long lists, mobile keyboard occlusion>
- **Notes for visual treatment:** <one or two lines; only if there is something distinctive — e.g., "this is the trust-critical moment in the journey, lean into legibility over density">
```

If the screen is "deferred" in the inventory, the entry can be shorter — purpose + key actions + a note that detailed states will be added when the screen is promoted to must-have.

### Section 7 — Deliverables

What the designer is asked to produce. Be specific.

```markdown
- Figma file titled `<slug>-design-v1`
- Pages, in this order:
  - **00 Cover** — file overview + version log
  - **01 Style** — design tokens (color, type, spacing scale, shadows, radii)
  - **02 Components** — reusable elements (buttons, inputs, cards, navigation, modals)
  - **03 Screens — Auth**
  - **04 Screens — Main**
  - **05 Screens — <other area>**
- Frame naming convention: `<screen-number>-<screen-name>-<state>` (e.g., `04-login-error`)
- Edit access for the user's Figma account — share link to be created by the designer
- Optional but appreciated: a 1-2 page Loom walkthrough of the file when delivered
```

### Section 8 — Constraints

A short list of binding constraints:

- **Platform and stack:** web / mobile / both, with the **specific stack** named (workspace defaults are Jinja + vanilla JS on web and React Native + Expo on mobile; other stacks are allowed per `mvp-scoping-methodology.md` §6.0). The designer should know which because it constrains what's implementable.
- **Technical:** anything in the brief must be implementable in the chosen stack. No designs that require WebGL animations on a Jinja-based web app unless the brief specifically scopes it. The constraints differ by stack — match what's been chosen.
- **Accessibility:** WCAG AA contrast minimum (4.5:1 body, 3:1 large text and UI). Designed states must be reachable without color-only signaling.
- **Localization:** if applicable, design for languages with longer strings (German, Russian) or right-to-left scripts.
- **Brand voice:** see §2 — UI copy decisions should reflect it.
- **Reference products to study (not copy):** 2-3 URLs.
- **Anti-references (do not look like these):** 1-2 URLs with reasons.
- **Timeline:** target turnaround — first round, revisions, final. Negotiable; declared so both sides know the shape of the engagement.

### Section 9 — Open questions

A short list. Some left for the designer's judgment; others are flagged for the user to answer mid-engagement. Mark each:

- **(For designer)** — designer decides; brief is intentionally open here.
- **(For user)** — user must answer; designer should stop and ask if they hit this.

Examples:

- (For designer) Empty-state illustration style — illustrative vs. typographic vs. iconographic.
- (For user) Should the logo wordmark or the icon mark lead in the header?
- (For designer) Density of the main list — comfortable vs. compact default.

### Section 10 — Sign-off and version log

```markdown
- **Drafted:** YYYY-MM-DD by <user>
- **Reviewed by `design-brief-reviewer`:** YYYY-MM-DD — verdict: APPROVE / APPROVE-WITH-NOTES / REJECT
- **User sign-off:** YYYY-MM-DD — <user>
- **Sent to designer:** YYYY-MM-DD — <designer name + contact>
- **Revisions:** date, what changed, why.
```

The version log keeps the engagement auditable. If the designer asks "did anything change since last week?" the answer is in the brief.

---

## 6. The output file

The brief is written to **`<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md`**. Same `design/` folder as the research. Both live with the product.

The file is the canonical artifact sent to the designer. The format chosen (Markdown) is fine for freelance handoff — designers can read it in any text editor, paste it into Notion, or convert to PDF if their workflow expects that. Most modern designers prefer Markdown or a Notion/Coda doc; ask before assuming.

---

## 7. Handoff to the designer

The brief is **not** sent until:

1. The `design-brief-reviewer` has reviewed it and returned a verdict.
2. The user has signed off on the final brief.
3. The frontmatter's `status` is updated from `draft` to `in-review` (during review), then `sent` (when actually transmitted).
4. The user has provided the designer with a Figma file template (or asked the designer to create one), a payment arrangement, and access to the brief.

Modes of transmission (any of these is fine; pick what suits the designer):
- A link to the file in this repo (if private repo, give the designer time-limited access).
- An emailed copy of the file, in `.md` or `.pdf`.
- A Notion / Coda doc pasted from the file.

Whichever mode is chosen, **the file in `design/DESIGN_BRIEF.md` remains the source of truth**. If the brief is edited mid-engagement, the user updates the file *first*, then re-shares.

---

## 8. When to revise the brief

Revise when **any** of these is true:

- The MVP brief is revised (e.g., scope changes, success criterion shifts).
- The user changes the picked visual direction or pattern conventions.
- The designer surfaces a constraint or open question the brief didn't anticipate (this is normal — note the revision in the version log).
- A material trend finding (per `guides/market/trend-monitoring.md`) affects the brief (rare — but encroachment from a competitor could change positioning notes).

Revisions go in §10's version log with date and reason. **Do not** silently re-export to the designer; tell them explicitly what changed.

---

## 9. Integration with the rest of the pipeline

| Upstream | How it feeds the brief |
|---|---|
| `/scope-mvp` | Produces `MVP.md`; brief reads it for product overview, success criterion, riskiest assumption, constraints. |
| `/research-design` | Produces `DESIGN_RESEARCH.md`; brief reads it for direction options, color, typography, pattern conventions. |
| Validation report | Crisp segment restatement (audience). |
| User picks (direction, continuity, open-question answers) | Direct input via the prompt that triggered `/draft-design-brief`. |

| Downstream | How the brief feeds it |
|---|---|
| `design-brief-reviewer` | Reviews the brief for completeness, sharpness, and consistency before send. |
| Human designer | Produces the Figma file. |
| `design-handoff-methodology.md` (next guide in this domain) | How the Figma comes back, where it lives, how Claude reads it for implementation. |
| `frontend-ui-engineering` (agent-skills, at implementation time) | Translates the chosen direction / palette / typography into design tokens and components. |

---

*Last meaningful revision: 2026-05-29 (initial draft).*
