---
name: expert-html-developer
description: Writes semantic, accessible, performance-aware HTML (and Jinja templates on Flask). Use when authoring or modifying any markup — Jinja templates, raw HTML, JSX/TSX structure, partials. Use when the page needs to be a11y-correct (proper landmarks, headings, labels, ARIA only where semantics fall short), SEO-correct (semantic tags, meta, OpenGraph), and Core-Web-Vitals-friendly (LCP-aware image markup, no layout shift). Triggers on "writing a template", "structuring markup", "Jinja template", "HTML element choice", "ARIA", "semantic HTML".
---

# Expert HTML Developer

## Overview

Author markup that is semantic, accessible, and performance-aware by default. The goal is HTML a senior frontend engineer would ship to production — not the verbose `<div>`-soup an LLM tends to generate. On Flask projects the canonical surface is Jinja templates; on RN/React the surface is JSX/TSX; on PySide6 there is no HTML at all (skip this skill on desktop).

## When this skill applies

- Authoring any new Jinja template (`templates/**.html`) or React component's JSX/TSX structure.
- Modifying existing markup — refactoring `<div>` soup into semantic tags, fixing heading hierarchy, adding proper form labels.
- Reviewing markup for a11y / SEO / Core-Web-Vitals fitness.

## Principles

### 1. Semantic over div-soup

`<button>` not `<div onclick>`. `<a>` for navigation, `<button>` for actions. `<nav>` / `<main>` / `<aside>` / `<header>` / `<footer>` define landmarks. Every page has exactly one `<main>`. Use `<section>` only when there's a heading; otherwise `<div>`.

Tables are tables (`<table>` / `<thead>` / `<tbody>` / `<th scope="col|row">`). Lists are lists (`<ul>` / `<ol>` / `<dl>`). Forms are forms (`<form>` with `<label for="id">` matching `<input id="id">`).

### 2. Heading hierarchy is real

Exactly one `<h1>` per page. `<h2>` only after `<h1>`. Don't skip levels for styling — that's CSS's job (use a class for visual size, not a different heading tag).

### 3. Forms

Every input has a `<label>`. Either wrap (`<label>Name <input></label>`) or associate (`<label for="x">Name</label><input id="x">`). Required fields use `required` attribute, not just a red asterisk. Error states use `aria-invalid="true"` + `aria-describedby` pointing at the error message. Form submission uses `<button type="submit">`, not a div with JS.

### 4. Images + media

`<img>` always has `alt` (use `alt=""` for purely decorative — that's correct, not omitting). For hero / above-the-fold images add `loading="eager"` + `fetchpriority="high"` to help LCP; for below-the-fold add `loading="lazy"`. Always set `width` + `height` attributes (even when sized by CSS) to prevent CLS. Use `<picture>` for art-directed responsive images.

### 5. ARIA: minimum effective dose

Native semantics beat ARIA. Only reach for ARIA when:
- Building a widget without a native equivalent (custom select, tabs, accordions, dialogs without `<dialog>`).
- Providing context native semantics can't (`aria-label` on icon-only buttons, `aria-live` for dynamic regions).

Wrong ARIA is worse than no ARIA. If unsure, drop it and let the semantic element speak.

### 6. Jinja-specific (Flask)

- Use template inheritance (`{% extends "base.html" %}`) and blocks; avoid duplicating layout.
- `|safe` is dangerous — only on content you've explicitly sanitized. Default-trust Jinja's autoescape.
- Partials in `templates/partials/` for components (`{% include 'partials/button.html' with text='Save' %}`).
- `url_for` for all internal links; never hardcode paths.
- Translation-ready: wrap user-facing strings in `{{ _("...") }}` if i18n is in scope (or note it as a v2 lift).

### 7. SEO + social

Every page: `<title>`, `<meta name="description">`, `<meta property="og:title">`, `<meta property="og:description">`, `<meta property="og:image">`, `<link rel="canonical">`. For SPAs / RN web variants, ensure these are server-rendered or hydrated correctly.

### 8. Performance markup

- `<link rel="preconnect">` for the 1-2 critical third-party origins (font CDN, CDN if used).
- `<link rel="preload" as="font">` for above-the-fold font files.
- Critical CSS inline in `<head>`; deferred CSS via `<link rel="stylesheet">` at end.
- Defer non-critical JS (`<script defer src="...">` or `type="module">`).

## Authority

When `DESIGN_SPEC.md` exists for the product, **the spec is the source of truth** for layout patterns, container max-widths, gutters, column counts. This skill's principles still apply (semantics, a11y, heading hierarchy) — they don't conflict with spec choices, they layer underneath.

## Red flags — fix before commit

- Any clickable `<div>` or `<span>` that isn't `role="button" tabindex="0"` + keyboard handlers (and even then, prefer `<button>`).
- Any `<img>` without `alt`.
- Any `<input>` without `<label>`.
- Multiple `<h1>` tags.
- Headings used for visual size, not structure.
- ARIA on a native element it's redundant with (`role="button"` on `<button>`).
- Missing `width`/`height` on images.
- Inline `style="..."` (use classes; spec tokens are CSS variables).
