# Design research methodology

How the `ui-ux-researcher` produces a **product-specific** design-direction report that becomes input to the design brief, which goes to the human designer. The research enables distinctive design — directions grounded in real references and the product's specific context, not generic "what AI thinks designs look like."

This guide is the contract the `ui-ux-researcher` assistant will be built against and the contract `/research-design <slug>` runs against.

---

## 1. Purpose

A human designer producing a unique Figma file for the product is the workspace default for surfaces a user touches (per `CLAUDE.md` working style + the user's explicit preference for distinctive design over the AI-generated look). For that designer to do their best work — and to do it efficiently, in fewer revision rounds — they need a sharp brief. The research report is the *raw material* for that brief.

Research **does**:

- Map the visual landscape of the product's category (direct competitors, adjacent products, awarded work).
- Surface **three or more** visual-direction options with cited references, with their tradeoffs.
- Surface **three or more** color and typography options grounded in real palette / type-pairing sources.
- Identify which design patterns are convention for this product type (forms, dashboards, navigation) and which are open for distinctive choice.
- Position the product in the brand landscape relative to competitors.
- Surface the portfolio-continuity question (does this product visually echo prior work — findvil, fijara — or stand independent?).

Research **does not**:

- Produce final designs. The designer does that.
- Produce wireframes. Also the designer.
- Pick a single direction. The brief and the designer pick.
- Write component code. That is the implementation phase, governed by agent-skills' `frontend-ui-engineering`.

---

## 2. Operating principles

1. **Ground in real references, not generic templates.** Every direction in the report has at least one URL pointing at a real product, design publication, brand work, or palette source. "Modern minimalist with rounded corners" is not a finding; "this look-and-feel, like \<URL\>" is.
2. **Surface options, not single answers.** The designer's taste is what is being purchased. The research provides a curated set of plausible directions; the designer picks (or hybridizes).
3. **Three options minimum per major choice.** Three forces the researcher past the obvious one and exposes tradeoffs.
4. **Resist the LLM aesthetic.** If the research's options all converge on "soft pastels, rounded corners, generous whitespace, friendly type" *regardless of the product*, the researcher has failed. Re-do.
5. **Accessibility is a floor, not a tradeoff.** WCAG AA contrast (4.5:1 for body text, 3:1 for large text and UI components) is the minimum. Distinctive design that fails this constraint is not distinctive — it is exclusionary.
6. **The product's segment, problem, and riskiest assumption shape direction.** A trust-critical financial tool needs different visual cues than a playful social tool. The research must reference the brief, not float free of it.
7. **Per the internet access policy in `CLAUDE.md`, web research happens by default.**

---

## 3. Inputs

To run design research on a product, the researcher reads:

| Input | Source |
|---|---|
| The MVP brief | `web-apps/<slug>/MVP.md` or `mobile-apps/<slug>/MVP.md` |
| The validation report | `market-research/validation-<slug>-*.md` (most recent) |
| The idea card | `ideas/<slug>.md` |
| Founder context and prior shipped products | `CLAUDE.md` and the user-profile memory; specifically: findvil.com, fijara.com, the Fijara mobile app, prior visual choices |
| Any explicit visual preference the user has given | The user prompt that triggered `/research-design`, or notes in the brief |

The research is *for this product*. Sources are mined with that product in mind — not as a generic "what's hot in design right now" sweep.

---

## 4. The research workflow

### 4.1 Restate the product context

In one paragraph, restate from the brief and validation report:

- Segment (who).
- Problem (what feeling does the segment have around this — anxious, frustrated, curious, hopeful?).
- Domain (financial, creative, productivity, communication, healthcare, etc.).
- Trust register (high-stakes trust-critical, medium, low/playful).
- The riskiest assumption — because design that supports validating the assumption beats design that does not.

This paragraph appears at the top of the report so the designer does not have to read the brief twice.

### 4.2 Map the reference landscape

Sweep, with URLs:

- **Direct competitors:** the 3-7 products named in the validation report's competitive section. Capture: a screenshot link (use the live URL if no archive), one-line characterization of their visual language, one observation of what works or doesn't.
- **Adjacent products:** 3-5 products in nearby categories whose users overlap with this segment.
- **Awarded / inspiration sources:** at least 3-5 entries from publications and curation sites — Awwwards, SiteInspire, Mobbin (for mobile patterns), Sidebar, Codrops, Land Book, Page Flows, Designspiration.
- **Anti-references:** 2-3 examples of what to avoid in this category, with reasons.

### 4.3 Surface visual direction options

Produce **at least three distinct visual directions**, each with:

- A name (e.g., "Editorial restraint," "Confident craft," "Calm utility").
- A mood / tone description.
- 2-4 reference URLs that capture the direction's feel.
- What it would communicate to the segment.
- What it would deliberately *not* do.
- Plausible failure mode if mis-executed.

If two of the three options feel similar, replace one with a more distant alternative. The research is most valuable when the options force a real choice.

### 4.4 Color direction

- Note industry conventions (e.g., fintech leans navy + green; healthcare leans white + restrained blue; creative tools lean black + saturated accent). Industry convention is information — sometimes you follow it, sometimes you break it deliberately.
- Produce **at least three palette options** corresponding to (or contrasting with) the visual directions. Each option:
  - Primary, secondary, neutral scale, semantic colors (success, warning, error).
  - Source URL: a real product or a palette source (Coolors.co, Adobe Color, Refactoring UI's color section, Tailwind's palette as a starting reference).
  - WCAG AA contrast notes for body text on background.
- Flag any palette that requires distinctive but uncommon color choices — these reduce stock-photo and icon compatibility.

### 4.5 Typography direction

- Note what type personalities suit the product (reading-heavy interfaces need calmer body type; action-heavy interfaces tolerate more character; trust-critical interfaces lean conservative).
- Produce **2-3 pairings** of (body type, display type). Each pairing:
  - Both fonts named (prefer open-source — Inter, Geist, JetBrains Mono, Fraunces, Söhne are common choices but pick what fits).
  - Source URL: Google Fonts, Adobe Fonts, or a foundry page.
  - License notes (open-source vs. paid; some MVPs cannot afford a $400/year display face).
  - A sample reference URL showing the pairing in use, if available.

### 4.6 Pattern conventions

For the product type, separate:

- **Conventions the product should follow** (because deviation costs cognitive load with no upside). Examples: sidebar + main for SaaS dashboards, tab navigation for consumer mobile main flows, breadcrumbs in deep hierarchies, modals for short focused tasks.
- **Conventions the product can break for distinctive value.** Examples: a SaaS dashboard with no sidebar can feel refreshingly focused; a mobile app with a non-tab primary navigation can read as confident.

Source: Mobbin (mobile), Refactoring UI, Page Flows, and direct observation of references. Cite for each finding.

### 4.7 Brand positioning

Locate the product in the design landscape:

- Are competitors all using a similar visual language? If yes, **distinction is high-value** — note where the white space is.
- Are competitors highly varied? If yes, the product needs to pick which family to join or go orthogonal — note the families.
- Recommend (one paragraph, non-binding): where you'd suggest the product sit, given the segment, the riskiest assumption, and the founder's intent.

### 4.8 Portfolio continuity question

Surface, but do not answer:

- Should this product visually echo findvil / fijara — same logo family, same typography, recognizable as same hand?
- If echo desired: what would carry across? Color family, typography, logo style, illustration treatment, photography style?
- If independent: explicitly note what makes it independent — for the user to decide.

This is a strategic decision (one brand vs. portfolio of distinct brands) that the methodology surfaces but defers to the user.

### 4.9 Open questions for the designer

A short list of questions whose answers will change the designer's work, surfaced for the brief to address (or for the user to answer before the brief goes out):

- Should the product have a name-and-logo treatment? Is a wordmark sufficient or is a mark required?
- Is there a written brand voice (which informs UI copy)?
- Are there platform constraints (iOS Human Interface Guidelines compliance, Material Design conformance) that bind the design?
- Are there partner/integration constraints (e.g., must look "enterprise-ready" for B2B procurement)?

### 4.10 Write the report

Write to `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md`. The `design/` subfolder is created if it doesn't exist.

---

## 5. The design research report format

```markdown
---
slug: <product slug>
domain: web | mobile | hybrid
date-researched: YYYY-MM-DD
status: draft | reviewed | acted-on
---

# Design research: <product name>

## Product context
<one-paragraph restatement of segment / problem / domain / trust register / riskiest assumption — for the designer's quick orientation>

## Reference landscape

### Direct competitors
- **[Product]** — <URL> — <one-line visual characterization> — <one observation>
- ... (3-7 entries)

### Adjacent products
- **[Product]** — <URL> — <characterization>
- ... (3-5 entries)

### Awarded / inspiration
- <URL> — <one-line on why it's relevant to this product>
- ... (3-5 entries)

### Anti-references
- <URL> — <what to avoid here>
- ... (2-3 entries)

## Visual direction options

### Option A: <name>
- **Mood:** <description>
- **References:** <URL list>
- **Communicates:** <what it says to the segment>
- **Deliberately not:** <what it avoids>
- **Failure mode:** <how it goes wrong if mis-executed>

### Option B: <name>
[same structure]

### Option C: <name>
[same structure]

## Color direction

**Industry convention:** <one paragraph>

### Palette option 1: <name>
- Primary: `#......` — source: <URL>
- Secondary: `#......`
- Neutral scale: `#......` to `#......`
- Semantic (success / warning / error): ...
- **Body text on bg contrast:** <ratio>:1 (WCAG AA pass/fail)

### Palette option 2: <name>
[same]

### Palette option 3: <name>
[same]

## Typography direction

### Pairing 1: <name>
- Body: <font name> — <URL> — <license note>
- Display: <font name> — <URL> — <license note>
- **In use at:** <URL of a real product using the pairing, if found>

### Pairing 2: <name>
[same]

### Pairing 3: <name>
[same]

## Pattern conventions

### Follow these (convention earns its place)
- <Pattern> — <reason> — <reference URL>

### Open for distinctive choice
- <Pattern> — <reason it could be broken with upside> — <reference URL of a product that did>

## Brand positioning

**Where competitors cluster:** <paragraph>

**Recommendation (non-binding):** <where this product could sit, with reasoning>

## Portfolio continuity question

- Echo findvil / fijara: <what would carry across if echoed>
- Stand independent: <what would make it independent>
- **Decision deferred to user.**

## Open questions for the designer

- <Question 1>
- <Question 2>
- ...

## Sources
- <every URL used in the report — for audit>
```

The Sources list at the bottom is a hard requirement — same evidence standard as our market and product reviewers.

---

## 6. Handoff to the design brief

The research report is **input to** `design-brief-methodology.md` (next guide in the UI/UX domain). The brief consolidates:

- The relevant parts of the research (visual direction, color direction, typography direction).
- The MVP brief's product context, must-haves, and success criterion.
- User journeys (added at brief time, drawing on the must-haves).
- Functional requirements per screen.
- The designer's deliverables expected.

The research itself stays in `design/DESIGN_RESEARCH.md` for the designer to consult — the brief is the primary document they work from, but the research is the audit trail.

---

## 7. When to re-research

Re-research when **any** of these is true:

- The brief is revised significantly (segment, must-haves, or riskiest assumption changes).
- The designer pushes back on the directions as off-brief or insufficient.
- The competitive landscape shifts materially (per `guides/market/trend-monitoring.md`) — a new entrant, a major redesign of an incumbent.
- More than 6 months have passed since the research and the product has not yet shipped to design.

A re-research is incremental — it re-reads the brief, refreshes the reference landscape, and revises directions where shifts warrant. It does not start from zero.

---

## 8. Integration with the rest of the pipeline

| Upstream | How it feeds research |
|---|---|
| `/scope-mvp` | Produces the MVP brief; this guide reads it. |
| Validation reports | The competitive section names competitors the research must cover. |
| Trend monitoring | Material encroachment findings affect competitor landscape. |

| Downstream | How research feeds it |
|---|---|
| `design-brief-methodology.md` | Brief consolidates research findings into a designer-ready document. |
| `design-brief-reviewer` | Checks the brief incorporates research findings honestly. |
| Designer (human) | Reads brief; research is the audit trail. |
| `frontend-ui-engineering` (agent-skills) | At implementation, code references the chosen direction / palette / typography — translated into design tokens. |

---

*Last meaningful revision: 2026-05-29 (initial draft).*
