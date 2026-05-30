# Design handoff methodology

How the designer's Figma file is **received, reviewed, accepted, captured into the repo, and translated into code**. The handoff is the bridge between "the designer is done" and "the build can proceed with confidence." Without a clear handoff convention, designs get re-interpreted at implementation time and ship looking like generic UI — defeating the point of paying for distinctive design in the first place.

This is the third guide in the UI/UX domain. It assumes the design brief has been sent (per `design-brief-methodology.md`) and the designer is returning work against it.

---

## 1. Purpose

The handoff has to answer four questions before implementation can start:

1. **Has the designer delivered against the brief?** Coverage, fidelity, states, accessibility — verify each.
2. **What lives in the repo to make the design discoverable later?** A Figma share link is not enough; the team (you + Claude) need design artifacts that survive a session restart and a Figma reorganization.
3. **What does Claude read when implementing?** Claude cannot open `.fig` files directly. The handoff must produce artifacts Claude can read (screenshots, exported tokens, exported assets).
4. **How are design tokens and components reflected in code?** A clean mapping from Figma styles to code tokens prevents the "looks roughly like the Figma" failure mode that produces generic-looking implementations.

---

## 2. Operating principles

1. **Figma is the design source of truth; the repo is the implementation source of truth.** Each authoritative for its domain. The handoff is the bridge — it copies the *implementation-facing* artifacts into the repo, leaves the rest in Figma.
2. **Capture what code needs, not what looks pretty in the repo.** Tokens, per-screen screenshots, exported assets. Not the whole Figma file as a static export.
3. **The user is the primary reviewer of the Figma.** Claude assists (against the brief's checklist), but the user signs off. No reviewer assistant auto-approves a Figma delivery.
4. **Fidelity over speed in the first build.** First implementation should match the Figma. Liberties get taken later, deliberately, after the design has shipped and been observed.
5. **Tokens drive everything.** Colors, type scale, spacing, radii, shadows — all centralized. Hardcoded hex values in component code are a sign the token layer is being skipped, and that's where generic-looking drift creeps in.
6. **Per the internet access policy in `CLAUDE.md`, fetch Figma plugin docs freely** when configuring exporters.

---

## 3. Receiving the Figma — first delivery

The designer sends the first round. The artifacts you should expect (and ask for if missing):

- **Figma file URL** — viewer or commenter access initially, edit access once accepted.
- **A walkthrough** — ideally a short Loom (2-5 min) explaining the file structure, the design direction, the per-screen decisions, anything the user should know that isn't visible in the file. Some designers don't do this; ask politely. Even 60 seconds of context saves an hour of confusion.
- **Open questions or design decisions the designer wants you to weigh in on** — usually a Figma comment thread or a separate message.

Do not start review until you have at least the file URL and basic walkthrough context (written is fine — Loom is just preferred).

---

## 4. Reviewing the Figma against the brief

The user does this primarily; Claude can assist by reading the brief and a checklist back. The check covers:

### 4.1 Coverage check

For each screen in the brief's §5 (Screen inventory) marked must-have (M):

- Is it in the Figma?
- Are all states from the brief's §6 designed (loading, empty, error, success)?
- Are the edge cases the brief named addressed (long names, missing data, etc.)?

Deferred (D) screens are not required at this stage — but flag if the designer delivered some D-screens at the cost of M-screen depth.

### 4.2 Direction fidelity

- Does the file's visual treatment match the **visual direction** picked in the brief's §3? (Mood, restraint, presence — does it feel like the chosen direction?)
- Does the palette match the **color picks** in the brief's §3? Spot-check 3-4 colors.
- Does the typography match the **pairing picks** in the brief's §3? Spot-check body and display in two places.

If the file feels different from the brief's direction, this is a *direction* conversation with the designer, not a tweak conversation. Reset before requesting tweaks.

### 4.3 Component organization

The file should have, at minimum:

- **01 Style** page with the design tokens (color styles, text styles, effect styles, optionally spacing/radius variables).
- **02 Components** page with reusable elements organized as Figma components (buttons, inputs, cards, navigation primitives).
- **03+ Screens** pages by area, with frames named per the brief's §7 convention.

If the file is one big flat page with everything scattered, the implementation cost goes up — ask the designer to organize before final acceptance.

### 4.4 Accessibility spot-check

Use a contrast-checking plugin (Stark, A11y - Color Contrast Checker, or the built-in Figma palette tool) on:

- Body text on each background variant.
- Button labels on each button variant.
- Form field labels and placeholders.

WCAG AA minimum: 4.5:1 for body text, 3:1 for large text and UI components. Failures get fixed before acceptance — they don't get fixed in code by "darkening it a bit," because that drifts the design.

### 4.5 Mobile / responsive check (when applicable)

- For mobile MVPs: are the frames sized to a real device (e.g., iPhone 14 width 390px, iPhone SE 375px for the small-end test)?
- For web MVPs: are the breakpoints designed — desktop, tablet, mobile?
- Are touch targets at least 44×44 pt (iOS guideline)?

### 4.6 Brief alignment summary

After the checks above, the user signs off (or sends a revision request) listing:

- **Approved:** what works as delivered.
- **Revisions requested:** specific frames or components with specific asks (not vague — "the dashboard feels heavy" is not a request; "the dashboard's primary card uses the wrong shadow level; please use the level from 01 Style" is).

The reviewer-assistant equivalent for this (a `design-fidelity-reviewer`) is **planned but not built yet**; until it exists, the user runs this check personally, optionally walking through the brief's checklist with Claude reading the brief out loud.

---

## 5. Acceptance — when to sign off

The user signs off when:

- All must-have screens are present with their required states.
- Direction fidelity is right (mood, palette, typography).
- Component organization is clean enough for implementation.
- Accessibility passes WCAG AA spot-checks.
- No revisions are outstanding.

Sign-off does not mean "the design is perfect." It means "this is the design we are implementing now; further changes go through the revision process in §8, not the first-build process."

---

## 6. Capturing the handoff into the repo

This is the step that survives session restarts and Figma reorganizations. The user (or Claude, prompted by the user) does this **once after acceptance**.

### 6.1 Folder structure

```
<web-apps|mobile-apps>/<slug>/design/
├── DESIGN_RESEARCH.md         # already in place (from /research-design)
├── DESIGN_BRIEF.md            # already in place (from /draft-design-brief)
├── figma/
│   └── README.md              # Figma link record + frame index + walkthrough URL
└── handoff/
    ├── tokens.json            # exported tokens (color, type, spacing, radius)
    ├── tokens-source.md       # notes on the export — which plugin, when, who
    ├── assets/                # exported SVGs, PNGs, illustrations
    │   ├── icons/
    │   ├── illustrations/
    │   └── images/
    └── screenshots/           # one PNG per screen + state, named consistently
        ├── 04-login-default.png
        ├── 04-login-error.png
        ├── 04-login-loading.png
        ├── 05-home-default.png
        ├── 05-home-empty.png
        └── ...
```

### 6.2 `figma/README.md` — the link record

```markdown
# Figma file: <slug>

**File URL:** https://www.figma.com/file/...
**Access:** \<view/comment/edit\>
**Designer:** \<name + contact\>
**Walkthrough:** \<Loom URL if provided\>

## Frame index

Cross-references the brief's §5 (Screen inventory) so anyone navigating the file can find each screen quickly.

| Brief # | Screen | Figma frame | Page |
|---|---|---|---|
| 1 | Login | `04-login-default` | 03 Screens — Auth |
| 1 | Login (error) | `04-login-error` | 03 Screens — Auth |
| ... | ... | ... | ... |

## Acceptance log
- YYYY-MM-DD — accepted first round, with notes: \<short\>
- YYYY-MM-DD — revision 1 received, accepted
- ...
```

The link record exists so that *future sessions* — yours and Claude's — can find the file fast. Without it, a Figma URL gets lost in a Slack DM and nobody can find it three weeks later.

### 6.3 `handoff/tokens.json` — design tokens as code

Exported from Figma using one of:

- **Tokens Studio (recommended)** — `https://tokens.studio/` — comprehensive, exports a JSON the next step in this guide reads cleanly.
- **Figma Variables → Export** — built-in for projects using Figma's native variables. JSON output similar shape.
- **A custom plugin or manual extraction** — last resort. Acceptable if the designer didn't use a token system; the user (or Claude) transcribes the styles into JSON manually.

The JSON shape used here (compatible with Style Dictionary / Tokens Studio):

```json
{
  "color": {
    "primary": { "value": "#0F172A" },
    "primary-hover": { "value": "#1E293B" },
    "bg": { "value": "#FFFFFF" },
    "text": { "value": "#0F172A" },
    "text-muted": { "value": "#475569" },
    "border": { "value": "#E2E8F0" },
    "success": { "value": "#16A34A" },
    "warning": { "value": "#F59E0B" },
    "error": { "value": "#DC2626" }
  },
  "spacing": {
    "1": { "value": "4px" },
    "2": { "value": "8px" },
    "3": { "value": "12px" },
    "4": { "value": "16px" }
    // ...
  },
  "radius": {
    "sm": { "value": "4px" },
    "md": { "value": "8px" },
    "lg": { "value": "16px" }
  },
  "type": {
    "body": {
      "family": { "value": "Inter, system-ui, sans-serif" },
      "size": { "value": "16px" },
      "lineHeight": { "value": "24px" }
    },
    "display": {
      "family": { "value": "Fraunces, serif" },
      "size": { "value": "32px" },
      "lineHeight": { "value": "40px" }
    }
    // ...
  }
}
```

(Values above are illustrative — replace with the actual exported tokens.)

### 6.4 `handoff/assets/` — exported SVGs, PNGs, illustrations

Exported via Figma's right-side panel **Export** option, or a plugin like Figma to Code.

- **Icons** as SVG (1x export, named per the design system, e.g., `icon-arrow-right.svg`).
- **Illustrations** as SVG when possible; PNG (2x and 3x for mobile retina) when the illustration is raster.
- **Photographic images** as WebP (with JPG fallbacks for older browsers if the project supports them).

Naming: `<category>-<name>-<variant>.<ext>`. Examples: `icon-search.svg`, `illustration-empty-state.svg`, `image-hero-desktop.webp`.

### 6.5 `handoff/screenshots/` — per-screen exports

One PNG per screen per state, named to match the brief's frame naming convention (`<screen-number>-<screen-name>-<state>.png`).

**Why screenshots:** Claude reads PNGs. When implementing a screen, Claude can look at the screenshot to understand the layout, spacing, and component arrangement. Without screenshots, Claude is implementing from a brief's text description plus the designer's Figma URL it cannot open — and the result drifts toward generic.

Export 2x scale at minimum so detail is preserved. The file size is fine for a handoff folder.

---

## 7. Translation to code

Once the handoff folder exists, the implementation phase starts. Code follows these patterns to preserve fidelity.

### 7.1 Tokens are the contract

The first implementation step is **importing the tokens** into the code's design system.

The examples below show the workspace default stacks. If the brief's chosen stack is different, translate the token contract into your stack's idiomatic config — the *principle* (tokens.json is the single source of truth; hardcoded hex in components is a violation) applies regardless.

**For web (Flask + Jinja + vanilla JS — workspace default):**

Translate `handoff/tokens.json` into a `static/css/tokens.css` file at scaffold time:

```css
:root {
  --color-primary: #0F172A;
  --color-primary-hover: #1E293B;
  --color-bg: #FFFFFF;
  --color-text: #0F172A;
  --spacing-1: 4px;
  --spacing-2: 8px;
  --radius-md: 8px;
  --font-body: Inter, system-ui, sans-serif;
  --font-display: Fraunces, serif;
  /* ... */
}
```

`base.html` loads `tokens.css` first; all subsequent styles reference the variables. Hardcoded hex values in templates or stylesheets are a rule violation — they bypass the token contract.

**For mobile (React Native + Expo — workspace default):**

Translate `handoff/tokens.json` into `src/theme/tokens.ts` (per the RN scaffold guide §4.7):

```ts
export const tokens = {
  color: {
    primary: "#0F172A",
    primaryHover: "#1E293B",
    bg: "#FFFFFF",
    text: "#0F172A",
    // ...
  },
  spacing: { 1: 4, 2: 8, 3: 12, 4: 16 },
  radius: { sm: 4, md: 8, lg: 16 },
  type: {
    body: { family: "Inter", size: 16, lineHeight: 24 },
    display: { family: "Fraunces", size: 32, lineHeight: 40 },
  },
} as const;
```

StyleSheet rules reference `tokens.color.primary`, never raw hex.

### 7.2 Components match the Figma's component library

For each Figma component on the **02 Components** page, there should be a corresponding code component:

- Same name (kebab-case in filenames, PascalCase in code).
- Same variants and states.
- Same props (when a Figma component has properties — variant, state, size — these become props in code).

The mapping does not have to be 1:1 for every Figma layer — only for the components in the Figma library. Frames within a screen don't necessarily become components in code; they become parts of the screen.

### 7.3 Implementation reads the screenshot

When implementing a screen, Claude **looks at** `handoff/screenshots/<screen>-<state>.png` (via the Read tool, which supports images) alongside the brief's §6 entry for that screen. The screenshot resolves layout questions the text brief cannot.

Order of authority when implementing:

1. **Token contract** — `tokens.json` and the in-code token files derived from it are non-negotiable.
2. **Screenshot** — the layout, spacing, and proportions in the screenshot are the visual contract.
3. **Brief §6** — the functional spec (actions, inputs, states).
4. **Frontend craft skill** — agent-skills' `frontend-ui-engineering` for *how* to write the component code well (composition, accessibility, etc.).

When 1-3 contradict each other, surface the contradiction to the user — do not silently average.

### 7.4 What to do when Claude has no Figma access

The expected workflow above does not require Claude to open Figma directly. If a Figma MCP server is configured later (DO/Anthropic ecosystem may add this), the workflow can incorporate it for richer queries — but the handoff folder remains the authoritative implementation source.

---

## 8. Revisions over time

After first build ships:

- **Bug fixes / minor visual tweaks** — Claude edits code directly using the tokens; Figma stays the design source but does not block the fix. Update the Figma later if the change is durable.
- **Major iteration** (new screens, redesign of an existing area) — back to the design brief. Revise `DESIGN_BRIEF.md` (per `design-brief-methodology.md` §8), commission designer revisions, run a new handoff for the changed area only.

The handoff folder grows with each revision. Date the version log entries.

---

## 9. Integration with the rest of the pipeline

| Upstream | How it feeds the handoff |
|---|---|
| `/research-design` | Produced `DESIGN_RESEARCH.md` — kept for context but not directly used in handoff. |
| `/draft-design-brief` | Produced `DESIGN_BRIEF.md` — used as the review checklist. |
| Designer's delivery | Source artifact for the handoff folder. |

| Downstream | How handoff feeds it |
|---|---|
| Web build (`guides/web/flask-mvp-scaffold.md`) | Tokens load into `static/css/tokens.css`; components built from the Figma library; screenshots inform per-screen implementation. |
| Mobile build (`guides/mobile/react-native-mvp-scaffold.md`) | Tokens load into `src/theme/tokens.ts`; components built from the Figma library; screenshots inform per-screen implementation. |
| agent-skills' `frontend-ui-engineering` | Governs *how* the components are written — composition, accessibility, focused components, no AI aesthetic at the code level. |

A future `design-fidelity-reviewer` assistant (not yet built) could automate parts of §4-§5 by comparing the handoff folder to the brief. For now, the user is the primary reviewer.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
