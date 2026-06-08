---
name: expert-js-developer
description: Writes modern, performant, accessible JavaScript — vanilla JS for Flask static templates, TypeScript for RN, with proper event handling, no jQuery, no framework-cargo-culting. Use when adding interactivity to a Jinja template, writing an RN component's logic, handling forms / state / fetch / DOM, or debugging a JS issue. Triggers on "vanilla JS", "JavaScript interaction", "fetch", "event handler", "form validation", "TypeScript", "React Native logic".
---

# Expert JavaScript Developer

## Overview

Author JS / TS that is modern, accessible, and performance-aware. The goal is code a senior frontend engineer would ship — clean async, proper event delegation, no unnecessary framework, no jQuery, no over-engineering. Vanilla JS is the default on Flask templates; TypeScript is the default on RN; the principles apply equally.

## When this skill applies

- Writing or editing `static/js/**/*.js` on Flask.
- Writing or editing `src/**/*.ts` / `*.tsx` on RN.
- Adding interactivity to a Jinja template (inline `<script>` block).
- Debugging a JS bug — event not firing, fetch failing, state out of sync.

## Principles

### 1. Vanilla over framework on Flask

Flask + Jinja MVPs do **not** need React. Vanilla JS handles 95% of interactivity well: forms, modals, dropdowns, fetch, simple state. Reach for Alpine.js, htmx, or a tiny custom helper only when vanilla genuinely becomes painful. Never reach for jQuery (2026).

If you find yourself building a SPA inside a Flask app, stop — the brief should have called for an SPA stack (Next.js, etc.) from the start.

### 2. Modern syntax

- `const` / `let` only; never `var`.
- Arrow functions for callbacks; `function` for top-level declarations (better stack traces).
- `async` / `await` over raw promises.
- Template literals over concatenation.
- Optional chaining (`a?.b?.c`) and nullish coalescing (`a ?? b`) over verbose guards.
- Destructuring (`const { x, y } = obj`) over repeated access.
- Spread (`[...arr]`, `{...obj}`) over `Object.assign` / `concat`.

### 3. Events

- **`addEventListener`** with named handlers, not inline `onclick` (testability + removable).
- **Event delegation** on parent for lists (one listener, not 100): `parent.addEventListener('click', e => { if (e.target.closest('.item')) {...} })`.
- **`AbortController`** for cleanup: `addEventListener('click', fn, { signal: controller.signal })` then `controller.abort()` on unmount.
- **`preventDefault()`** for form submit if you're handling via fetch; don't rely on `return false`.

### 4. Fetch

- Use the built-in `fetch` API; no axios needed in 2026.
- Always handle non-2xx: `if (!res.ok) throw new Error(...)`.
- Always handle the loading + error + success states in the UI.
- Use `AbortController` for cancellable fetches (search-as-you-type, etc.).
- CSRF token: read from a `<meta name="csrf-token">` or a cookie, send in `X-CSRFToken` header. The token name comes from Flask-WTF or your auth setup.

### 5. Forms

- Validate on the client AND the server. Client validation is UX; server validation is correctness.
- Use HTML5 form constraints (`required`, `type="email"`, `pattern`) before reaching for JS.
- Show errors inline with `aria-invalid` + `aria-describedby` — see the `expert-html-developer` skill.
- Disable submit during in-flight to prevent double-submits; re-enable on response or error.

### 6. Accessibility in JS

- **Focus management** for dynamically inserted content: when opening a modal, move focus into it; when closing, return focus to the trigger.
- **Trap focus** in modals (Tab cycles within; Esc closes).
- **Announce live updates** to screen readers via `aria-live` regions for status messages, toasts, form errors.
- **Keyboard parity** with mouse — every clickable element responds to Enter/Space if it's not a native button.

### 7. Performance

- **Debounce** rapid events (input typing, scroll, resize) — use a 200-300ms debounce for search-as-you-type.
- **Throttle** event handlers that need to fire during continuous events (scroll, mousemove) — use `requestAnimationFrame` for animations.
- **IntersectionObserver** for lazy-load, infinite scroll, scroll-triggered animations — not scroll listeners.
- **Avoid large synchronous loops on the main thread.** Break long work into chunks via `setTimeout(0)` or Web Workers.
- **`requestIdleCallback`** for non-critical background work.

### 8. TypeScript (RN)

- `strict: true` in `tsconfig.json` — no implicit any.
- Type props + state explicitly; let inference handle local variables.
- Discriminated unions for action types (`{ type: 'load' } | { type: 'save' } | { type: 'cancel' }`).
- Avoid `as` casts — they bypass the type checker. Use type guards (`if (x is Foo)`) instead.
- Don't fight the compiler — if you're casting around an error, the type is probably wrong, not the compiler.

### 9. Error handling

- **Try/catch around `await` for fetches** that can fail (every external call).
- **Don't swallow errors silently** — log to console at minimum; surface to UI for user-visible failures.
- **Distinguish recoverable from non-recoverable** errors — a fetch retry is recoverable; a missing required env var at boot is not.

### 10. No framework cargo-culting

Don't import a state library because you've seen it elsewhere; use it when local state genuinely doesn't fit. Don't write a context provider for a value used in one component. Don't add lodash for `array.find()` — use the native method.

## Authority

`DESIGN_SPEC.md` is source of truth for visual design; this skill is source of truth for the *behavior* layer underneath it. They don't conflict.

## Red flags — fix before commit

- `var` declarations.
- jQuery (anywhere — it's 2026).
- Inline `onclick="..."` handlers (move to addEventListener).
- Fetch without error handling.
- Submit button not disabled during fetch in-flight.
- Modal open without focus trap.
- No focus restoration after closing dynamic UI.
- Scroll listener without throttle.
- Heavy synchronous loop blocking main thread.
- `as` cast around a type error (TS).
- `console.log` left in production paths.
- Silent error swallows (`catch {}`).
