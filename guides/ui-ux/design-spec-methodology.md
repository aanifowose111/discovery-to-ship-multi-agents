# Design spec methodology

How the `ui-ux-researcher` (in spec-writing mode, invoked via `/draft-design-spec`) produces a **`DESIGN_SPEC.md`** — the implementation-ready design specification that Claude builds the product directly from on the claude-led design path.

The spec is the build's **source of truth** for visual + interaction design. It supersedes the `frontend-ui-engineering` skill's defaults (padding scales, type ramps, color tokens) for the product it covers; the skill's principles apply only to gaps the spec doesn't cover.

This guide is the contract `/draft-design-spec <slug>` runs against and the contract `design-spec-reviewer` reviews against.

---

## 1. Purpose

A claude-led product has no human designer producing a Figma file. The `DESIGN_SPEC.md` substitutes for that Figma by being **complete enough that Claude (and any other engineer) can implement the entire UI from it without inventing tokens or making design decisions ad-hoc during build**.

The spec **does**:

- Lock the visual direction picked by the user (from the research's 3+ options).
- Specify exact CSS-ready tokens for color, typography, spacing, radius, shadow.
- Specify the icon library + install snippet + usage convention.
- Specify image assets as ChatGPT/Midjourney/DALL-E prompts the user runs later (batch-later default — no per-image pause during spec writing).
- Specify responsive breakpoints with per-breakpoint behavior per surface.
- Specify per-surface details (public landing, auth, user dashboard, admin, employee — only those that apply).
- Specify component patterns (buttons, forms, tables, modals, toasts, empty states, loading states, error states) with exact token references.

The spec **does not**:

- Replicate the research's reference URLs in full (it cites the research for that).
- Produce Figma frames (the spec is text + tokens, not pixel coordinates).
- Specify business logic or API contracts (those are the brief's job).
- Lock in component code (implementation happens at build time; the spec tells the build what tokens to use).

---

## 2. Inputs

To write the spec, the researcher reads:

| Input | Source |
|---|---|
| The signed-off research | `<product-folder>/design/DESIGN_RESEARCH.md` (must have `status: acted-on`) |
| The brief | `<product-folder>/MVP.md` or `V1.md` (for must-haves, surfaces, success criterion) |
| The user's picks | Passed in the prompt by the main Claude — visual direction, palette, typography pairing, pattern conventions to break, brand voice, portfolio continuity, answers to research's open questions |
| `CLAUDE.md` | For workspace conventions |
| Prior `DESIGN_SPEC.md` if it exists | For revisions — preserve still-relevant content |

---

## 3. The DESIGN_SPEC.md format

The spec lives at `<web-apps|mobile-apps|desktop-apps>/<slug>/design/DESIGN_SPEC.md`.

```markdown
---
slug: <product slug>
domain: web | mobile | desktop | hybrid
date-spec: YYYY-MM-DD
status: draft | in-review | acted-on | superseded
brief-version: mvp | v1
research-ref: design/DESIGN_RESEARCH.md
---

# Design spec: <product name>

## 1. Locked direction

| Element | Picked | Source |
|---|---|---|
| Visual direction | <Option A name from research §Visual direction> | `DESIGN_RESEARCH.md` §Visual direction |
| Color palette | <Palette 1 name> | `DESIGN_RESEARCH.md` §Color direction |
| Typography pairing | <Pairing 1 name> | `DESIGN_RESEARCH.md` §Typography direction |
| Brand voice | "<one or two sentences — the version copywriting works from>" | User pick |
| Portfolio continuity | echo findvil/fijara on X / stand independent (Y is what makes it independent) | User pick |
| Pattern conventions to break | <list with reasons> | User pick |

## 2. Tokens

### 2.1 Color

CSS custom properties (or React Native theme equivalents — `src/theme/tokens.ts`). Semantic names, not raw hex. Exact values; no "approximately."

```css
:root {
  /* Brand */
  --color-brand-primary: #1a3a5c;
  --color-brand-primary-hover: #15304d;
  --color-brand-accent: #d97757;

  /* Neutral scale */
  --color-bg-base: #fafaf7;
  --color-bg-surface: #ffffff;
  --color-bg-elevated: #ffffff;
  --color-bg-overlay: rgba(20, 20, 22, 0.6);

  --color-text-primary: #1a1a1c;
  --color-text-secondary: #4a4a52;
  --color-text-muted: #8a8a92;
  --color-text-inverse: #ffffff;

  --color-border-subtle: #e8e8e2;
  --color-border-default: #d0d0c9;
  --color-border-strong: #a8a8a1;

  /* Semantic */
  --color-success: #2e7d4f;
  --color-warning: #c97a1c;
  --color-error: #c53030;
  --color-info: #3b6eb3;
}
```

**WCAG AA contrast verified:** body text on `--color-bg-base` = X.X:1 (PASS); secondary text on `--color-bg-surface` = X.X:1 (PASS); ... For every text-on-background combination used, list the ratio. If any pair fails AA, **do not ship the token** — pick a different combination.

**Dark mode (if scoped in MVP/V1):** mirror the above with `@media (prefers-color-scheme: dark)` overrides. If dark mode is deferred, state so explicitly: "Dark mode deferred to v2; no overrides specified."

### 2.2 Typography

```css
:root {
  /* Font families */
  --font-body: 'Inter', system-ui, -apple-system, sans-serif;
  --font-display: 'Fraunces', Georgia, serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;

  /* Type scale (modular, 1.25 ratio from 14px base) */
  --text-xs: 0.75rem;     /* 12px */
  --text-sm: 0.875rem;    /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg: 1.125rem;    /* 18px */
  --text-xl: 1.25rem;     /* 20px */
  --text-2xl: 1.5rem;     /* 24px */
  --text-3xl: 1.875rem;   /* 30px */
  --text-4xl: 2.25rem;    /* 36px */
  --text-5xl: 3rem;       /* 48px */

  /* Line heights */
  --leading-tight: 1.15;
  --leading-snug: 1.35;
  --leading-normal: 1.55;
  --leading-relaxed: 1.7;

  /* Weights */
  --weight-regular: 400;
  --weight-medium: 500;
  --weight-semibold: 600;
  --weight-bold: 700;

  /* Letter spacing */
  --tracking-tight: -0.02em;
  --tracking-normal: 0;
  --tracking-wide: 0.02em;
}
```

**Self-hosting / loading:** specify exactly. Google Fonts CDN vs. self-hosted `.woff2` (recommended for prod — privacy + speed). For self-hosted, list the file paths and the `@font-face` block.

### 2.3 Spacing

Modular scale, 4px base. Use semantic names for layout (`--space-section-y`) on top of the raw scale (`--space-1` etc.).

```css
:root {
  --space-1: 0.25rem;   /*  4px */
  --space-2: 0.5rem;    /*  8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */
  --space-24: 6rem;     /* 96px */

  /* Semantic layout */
  --space-page-x: var(--space-6);     /* horizontal page gutter (mobile) */
  --space-page-x-md: var(--space-8);  /* tablet+ */
  --space-page-y: var(--space-12);    /* vertical section padding */
  --space-card-inner: var(--space-6);
  --space-form-row: var(--space-4);
}
```

### 2.4 Radius + shadow

```css
:root {
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;

  --shadow-sm: 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 10px rgba(0,0,0,0.06);
  --shadow-lg: 0 12px 28px rgba(0,0,0,0.10);
  --shadow-focus: 0 0 0 3px rgba(26, 58, 92, 0.18); /* matches --color-brand-primary at alpha */
}
```

### 2.5 Motion (transitions)

```css
:root {
  --duration-fast: 120ms;
  --duration-normal: 200ms;
  --duration-slow: 320ms;
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
}
```

Honor `prefers-reduced-motion`: collapse durations to 0 in a media query.

## 3. Icon system

**Library:** <Heroicons | Lucide | Feather | Tabler | Phosphor> — pick exactly one, with reason.

**Install (for the chosen stack):**

```bash
# example for web (Flask + vanilla JS)
# Option A: SVG sprite (recommended — single network request)
# - Download lucide.svg sprite to static/icons/lucide.svg
# - Use <svg><use href="/static/icons/lucide.svg#chevron-down"/></svg>

# example for React Native
npm install lucide-react-native
```

**Usage convention:** one component-style wrapper (`{% include 'partials/icon.html' with name='chevron-down' size=16 %}` for web; `<Icon name="chevron-down" size={16} />` for RN). Default size: 16px inline / 20px standalone / 24px primary actions.

**Sizes available:** 12, 14, 16, 18, 20, 24, 32, 48. No arbitrary sizes.

## 4. Image assets — prompts for user generation

This is the batch-later flow: Claude lists prompts; user generates images on ChatGPT / Midjourney / DALL-E / Stable Diffusion at their own pace; user uploads each to DigitalOcean Spaces (or AWS S3) and pastes the URL into `.env` against the env var name listed below. **The build does not wait** — Claude uses tasteful placeholders until URLs are set.

| Slot | Where used | Prompt | Env var name |
|---|---|---|---|
| Hero illustration | Public landing — top section | "Editorial line illustration of <product subject>, single-color, <brand-primary color> on cream background, calm and confident mood, no text, no people's faces, 1600x900px, transparent PNG." | `IMG_HERO_URL` |
| Empty state — no records | User dashboard, empty list views | "Minimalist isometric illustration of an empty desk drawer, muted palette in <brand neutrals>, no text, 600x400px, transparent PNG." | `IMG_EMPTY_STATE_URL` |
| ... | | | |

**For each slot:** Claude writes the prompt verbatim — descriptive enough that a regenerated image stays in the same family. Test the prompt yourself (Claude) by stating what you'd expect the image to look like; if you can't describe the result confidently, the prompt isn't sharp enough.

**Placeholder behavior during build:** templates render with a flat colored block at the slot's intended dimensions until the env var is set. Specify the placeholder color (usually `--color-bg-elevated`) so the build looks intentional even with placeholders.

## 5. Responsive specs

Carry from `DESIGN_RESEARCH.md §Responsive strategy` with concrete CSS values.

```css
/* Breakpoints — mobile-first */
/* sm: default (<640px), no media query needed */
@media (min-width: 640px)  { /* md */ }
@media (min-width: 768px)  { /* lg */ }
@media (min-width: 1024px) { /* xl */ }
@media (min-width: 1280px) { /* 2xl */ }
```

Per-surface pivot table: list each surface and what changes at each breakpoint. **Touch target floor:** 44px for mobile-web; 24-32px acceptable on desktop-only mouse-driven surfaces.

## 6. Per-surface specs

One block per surface enumerated in `DESIGN_RESEARCH.md §Surfaces`. Each block:

### <Surface name>

- **Audience + density tier + tone** — copy from research.
- **Layout pattern** — sidebar + main / top-nav + main / hero + sections / form-stack / table-first / etc. Specify the **container max-width**, **gutter**, **column count** at each breakpoint.
- **Key components used** — reference the §7 component list.
- **State coverage** — loading / empty / error / success behaviors, with token references.
- **A11y notes specific to this surface** — keyboard nav landmarks, focus order, ARIA roles.
- **Image slots used** — reference §4.

## 7. Component patterns

For each common component, specify tokens used + states. Components to spec at MVP minimum:

- **Button** — primary / secondary / tertiary / destructive; sizes sm/md/lg; states default/hover/focus/active/disabled/loading.
- **Form input** — text / textarea / select / checkbox / radio; states default/focus/error/disabled; error message styling.
- **Form field group** — label, help text, error text, spacing.
- **Table** — header style, row hover, row selected, pagination footer, empty state, loading state, error state.
- **Modal / dialog** — overlay, panel, header, body, footer; sizes sm/md/lg/fullscreen-on-mobile.
- **Toast / notification** — success / warning / error / info; position, duration, dismiss interaction.
- **Empty state** — illustration slot, headline, body, primary CTA.
- **Loading state** — spinner / skeleton (pick one as default); per-component placement.
- **Error state** — inline error / page-level error / retry CTA.
- **Navigation** — primary nav, secondary nav (if applicable), breadcrumbs (if applicable), active state.

Each component block uses *exact* token references (`color: var(--color-text-primary);`). No raw hex in component blocks.

## 8. Accessibility floor

- **WCAG AA contrast** — verified in §2.1 for every text-on-bg combo. AA is the floor; AAA is preferred for body text.
- **Keyboard navigation** — every interactive element reachable; visible focus state per §2.4 `--shadow-focus`; logical tab order; no keyboard traps.
- **Screen reader** — semantic HTML; ARIA only where semantics fall short; alt text on every image; proper heading hierarchy (no `h2` without `h1`).
- **Motion** — honor `prefers-reduced-motion`.

## 9. Implementation notes

- **CSS organization (web):** `static/css/tokens.css` for §2 tokens; `static/css/base.css` for reset + typography defaults; `static/css/components.css` for §7; per-template overrides only when truly local.
- **Theme file (React Native):** `src/theme/tokens.ts` exporting a single typed object; consumed via a `useTheme()` hook or styled-components theme.
- **PySide6 desktop:** Qt stylesheet (`.qss`) at `<package>/assets/styles/tokens.qss`; load in `MainWindow.__init__`.
- **Authority order** on conflict during build: this `DESIGN_SPEC.md` → V1.md §6 (per-screen requirements) → `frontend-ui-engineering` skill craft → workspace default.

## 10. Open questions (if any)

If the user's picks left genuine gaps that the spec can't resolve on its own, list them here. (Most claude-led specs resolve everything; gaps usually mean the user's picks were under-specified.)

## 11. Version log

| Date | Author | Change |
|---|---|---|
| YYYY-MM-DD | <user> + Claude | Initial draft (v1.0) |
```

---

## 4. Process the spec writer follows

1. **Read all inputs** (§2 above).
2. **Lock §1 from user picks** verbatim.
3. **Translate research's palette pick → §2.1 tokens** with exact hex + WCAG AA verification.
4. **Translate typography pairing → §2.2 tokens** with self-host or CDN decision.
5. **Pick spacing scale** (default 4px base; bump to 8px if research notes dense-utility UI).
6. **Pick icon library** based on visual direction (sober → Lucide/Feather; warmer/playful → Phosphor; consumer/marketing → Heroicons; dev-tool → Tabler).
7. **Write image-asset prompts (§4)** for each slot the brief implies (hero, empty states, illustrations called out by user journeys). Batch-later — write all prompts at once; do NOT pause per image.
8. **Translate research's responsive strategy → §5** with concrete CSS media queries.
9. **Write per-surface specs (§6)** — one per surface in research's §Surfaces table.
10. **Write component patterns (§7)** — token references only, no raw hex.
11. **Verify accessibility floor (§8)** is met by the chosen tokens.
12. **Set frontmatter `status: in-review`**. Return to the main Claude.

---

## 5. When to re-spec

Re-write or revise the spec when:

- The user revises their picks (different palette, different visual direction).
- The brief adds a new surface that the spec doesn't cover.
- Research is re-run (the research-status flips back to `draft`) and lands materially different directions.
- The build hits a token gap repeatedly (spec is too thin — go back and densify the relevant sections).

Don't re-spec for trivial drift; revise in-place.

---

## 6. Integration with the rest of the pipeline

| Upstream | How it feeds the spec |
|---|---|
| `DESIGN_RESEARCH.md` | Source of all directional options the user picked from. |
| MVP.md / V1.md | Source of surfaces, must-haves, success criterion. |
| User picks | Locked in §1 of the spec. |

| Downstream | How spec feeds it |
|---|---|
| `design-spec-reviewer` | Reviews completeness (tokens, icon library, image prompts, responsive specs, per-surface, components, a11y). |
| `/start-build` | Reads the spec as authority during the build. |
| `senior-frontend-engineer` | Implements against spec tokens; spec supersedes `frontend-ui-engineering` defaults. |

---

*Last meaningful revision: 2026-06-08 (initial draft — claude-led design path).*
