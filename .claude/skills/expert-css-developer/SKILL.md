---
name: expert-css-developer
description: Writes modern, performant, maintainable CSS — using design tokens, modern layout primitives (Grid, Flexbox, Container Queries), and respecting the cascade. Use when authoring or modifying styles — tokens.css, components.css, per-template styling, RN StyleSheet objects, PySide6 QSS. Use when responsive behavior matters, when a layout needs to work across viewports, when colors and spacing need to come from tokens not raw hex. Triggers on "writing styles", "CSS layout", "responsive", "media query", "breakpoint", "tokens.css", "StyleSheet", "QSS".
---

# Expert CSS Developer

## Overview

Author CSS (and stack-equivalents — RN `StyleSheet`, PySide6 QSS) that is token-driven, modern, performant, and maintainable. The goal is styling a senior frontend engineer would ship — not the brittle nested-class casseroles or arbitrary hex values an LLM tends to produce.

## When this skill applies

- Writing or editing `static/css/tokens.css`, `static/css/base.css`, `static/css/components.css`, or per-template CSS on Flask.
- Writing or editing `src/theme/tokens.ts`, `StyleSheet.create(...)` blocks, or styled-components on RN.
- Writing or editing `.qss` files on PySide6.
- Reviewing styles for token compliance, responsive correctness, performance.

## Principles

### 1. Tokens, not raw values

When `DESIGN_SPEC.md` exists, every color / spacing / radius / shadow / font-size in component CSS uses `var(--color-...)` / `var(--space-...)` / etc. — never raw hex, never magic numbers. **Raw hex in a component file is a fail.**

If a value you need isn't in the spec, the spec has a gap — surface it, don't invent.

### 2. Modern layout primitives

- **Flexbox** for one-dimensional layouts (nav bars, button rows, form rows).
- **Grid** for two-dimensional layouts (dashboards, card grids, complex forms with side-by-side fields).
- **Container queries** (`@container`) for component-level responsive behavior — components adapt to their container, not the viewport. Use these for components that appear in multiple contexts (sidebar vs. main).
- **`gap`** instead of margins-between-children. Margins on children are an anti-pattern in modern CSS.
- **Logical properties** (`padding-inline`, `margin-block`) for i18n-friendly layouts.

### 3. Mobile-first responsive

Default styles target the smallest viewport. Larger viewports add capabilities via `@media (min-width: ...)`. The breakpoints come from `DESIGN_SPEC.md §5` — don't invent new ones.

### 4. Cascade discipline

- Single-class selectors as the default. Avoid `.parent .child .grandchild` cascades — they're brittle and slow.
- `:where()` to lower specificity when needed (e.g., resetting third-party widget styles without specificity wars).
- BEM-like naming (`block__element--modifier`) OR utility classes — pick one philosophy per product and stick to it.
- `!important` is a code smell. Use it only for utility-class overrides (`.hidden { display: none !important; }`) or third-party widget de-escalation.

### 5. Performance

- **No CSS-in-JS at runtime** for production-perf-critical paths — use build-time CSS or static stylesheets. (Exception: RN's StyleSheet, which is build-time on the JS side.)
- **`will-change` sparingly** — only on elements actively animating; remove after animation completes.
- **`contain`** on isolated subtrees to limit layout work.
- **`content-visibility: auto`** on long below-the-fold sections to defer paint.
- **Critical CSS inline** for above-the-fold; lazy-load the rest.

### 6. Accessibility in CSS

- **Focus states are visible and clear** — never `outline: none` without an alternative (use the `--shadow-focus` token from the spec). The browser's default outline is OK if no spec exists.
- **Don't suppress `prefers-reduced-motion`** — wrap animations/transitions in `@media (prefers-motion-reduce)` to honor.
- **Color isn't the only signal** — error states use color + icon + text. Success same. Status indicators get text labels, not just color dots.
- **Touch targets at least 44px** on mobile-web.
- **Font-size minimums:** body text at least 16px on mobile (smaller triggers iOS zoom on focus); 14px is OK on dense desktop tables.

### 7. Dark mode (if in spec)

`@media (prefers-color-scheme: dark)` overrides on the token layer only. Component CSS shouldn't know it's in dark mode — that's what tokens are for. Test contrast in both modes.

### 8. Stack-specific

- **Flask + Jinja:** `static/css/tokens.css` → `base.css` → `components.css` → per-page. Bundle into one file in prod via the deploy runbook.
- **RN:** `src/theme/tokens.ts` exporting typed objects; consumed via `useTheme()` hook. Avoid inline `{margin: 12}` literals.
- **PySide6:** `.qss` files at `<package>/assets/styles/`. Loaded in `MainWindow.__init__`. Qt's QSS is CSS-like but limited — no Grid, no Flexbox. Use Qt layouts (`QHBoxLayout` etc.) for structure; QSS for appearance.

## Authority

When `DESIGN_SPEC.md` exists, the spec's tokens + per-surface specs + component patterns + responsive specs are authoritative. This skill applies the *how* (modern primitives, perf, a11y), not the *what* (which colors, which sizes — those come from the spec).

## Red flags — fix before commit

- Raw hex / px values in component CSS (should be tokens when a spec exists).
- `margin-bottom` between siblings (use `gap` on the parent).
- Cascaded selectors deeper than 2 levels (`.x .y`).
- `outline: none` without focus alternative.
- Animations without `prefers-reduced-motion` honor.
- `@media (max-width: ...)` (mobile-first means min-width).
- Color-only status signals (error red without an icon or label).
- Body text under 16px on mobile.
- New breakpoints invented outside the spec.
