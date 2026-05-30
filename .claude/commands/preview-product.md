---
description: Preview the current state of a product's UI in the browser. Tries real preview (the running app) first; falls back to dummy preview (Jinja template + fixture data) if dependencies aren't connected yet. Always tells you which mode you got and why. Web only — for mobile, see EAS preview build instructions in `guides/mobile/eas-build-and-update.md`.
argument-hint: <product-slug> [page-name]
---

You are about to preview a product's UI for the user. Two modes are possible:

- **Real preview** — the actual running app at `http://localhost:5000/<page>`. Requires the dev server to be up (`docker compose up`) AND the page's route + dependencies wired.
- **Dummy preview** — the Jinja template rendered with fixture demo data and opened in Chrome via the `web-preview` skill. Always possible if the template file exists.

Your job: detect which mode is currently possible, do that mode, and tell the user clearly which mode they're getting and why.

**Arguments:** $ARGUMENTS — `<product-slug> [page-name]`.
- `<product-slug>` is required.
- `[page-name]` defaults to `main/home` (or `main/index`). It's the template name without `.html` (e.g., `main/dashboard`, `auth/login`).

### Pre-flight

1. **Verify the product exists.** Check `web-apps/<slug>/`. If it doesn't exist, tell the user:
   > No web app at `web-apps/<slug>/`. Did you run `/scope-mvp <slug>` and `/start-build <slug>` yet? (Or, for mobile: `mobile-apps/<slug>/` — mobile previews go through EAS preview builds, not this command.)

2. **Verify the template exists.** Check `web-apps/<slug>/app/blueprints/<area>/templates/<page>.html` or similar. If not found, search the template folders:
   ```bash
   find web-apps/<slug> -name "<page>.html" -path "*/templates/*"
   ```
   If still not found, tell the user the page doesn't exist yet and offer to list available templates.

### Step 1 — Determine which preview mode is possible

**Check if real preview is possible:**

1. Is the dev server running? Try:
   ```bash
   curl -fsS http://localhost:5000/healthz 2>/dev/null && echo "up" || echo "down"
   ```
2. Is the page's route registered? Check `web-apps/<slug>/app/blueprints/<area>/routes.py` for a route handler that renders the template. If no handler, the page isn't accessible at a URL even if the template exists.
3. Are the page's data dependencies in place? Check whether any models / services the route calls actually exist. Heuristic: look at the route handler's imports and see if those service files exist.

If **all three** are true → real preview is possible.
If any is false → fall back to dummy preview.

### Step 2A — Real preview (when possible)

Tell the user:

> **Real preview** — dev server is running and all dependencies for `<page>` look wired. Opening in Chrome.

Then open the URL:

```bash
open -a "Google Chrome" "http://localhost:5000/<page-route>"
```

Note the route may not match the template name 1:1 — read the route handler to find the actual URL path. If you can't determine it, fall back to dummy preview with a note that the route mapping was unclear.

### Step 2B — Dummy preview (fallback or when real not possible)

Tell the user **clearly and concisely** why real preview isn't possible:

> **Not yet ready for live preview** — <reason: "dev server not running" / "no route handler for <page> yet" / "the X service the route depends on doesn't exist yet" / "scaffold-done tag not present">.
>
> Falling back to **dummy preview**: rendering `<page>.html` with fixture demo data so you can see the styling and structure as they stand right now.

Then invoke the `web-preview` skill (per `.claude/skills/web-preview/SKILL.md`):

```bash
cd web-apps/<slug>
test -f previews/render.py || python3 << 'EOF'
# Scaffold render.py if missing — see .claude/skills/web-preview/SKILL.md
EOF
test -f previews/fixtures/<page-with-slashes-as-underscores>.py || python3 << 'EOF'
# Scaffold a minimal fixture if missing
EOF
python previews/render.py <page>
```

Open the rendered HTML in Chrome:

```bash
open -a "Google Chrome" web-apps/<slug>/previews/_rendered/<latest-render>.html
```

If `render.py` or the fixture doesn't exist, scaffold them per the `web-preview` skill's instructions (see the skill body for the templates) before rendering. After scaffolding a fixture from scratch, tell the user the demo data is generic and they can edit the fixture for richer previews.

### Step 3 — Tell the user what they got

After the browser opens (or even if it doesn't, e.g., `--no-open`):

> Previewed: **`web-apps/<slug>/.../<page>.html`**
> Mode: **<real | dummy>**
> Why: <one sentence on why this mode was selected>
>
> What you're seeing:
> - <real mode: "the actual page from the running app — live data, real routes">
> - <dummy mode: "the page's styling and structure with fixture demo data — no live behavior; useful for visual review while the rest is being built">
>
> <If dummy mode: brief mention of what would unblock real preview, e.g., "Real preview will become possible once: (a) docker compose is up, (b) the route handler is implemented, (c) the User service exists.">

### Mobile note

For mobile products in `mobile-apps/<slug>/`, this command does not apply. Mobile previews go through:

- **Expo Go / dev client** while developing — `npx expo start` in the project, then scan the QR code on a device.
- **EAS preview builds** for tester distribution — per `guides/mobile/eas-build-and-update.md` §3 (the `preview` build profile).

If the user asks `/preview-product <mobile-slug>`, surface those two options and don't attempt anything else.

### Notes

- This command never modifies anything in the app code. It only reads + scaffolds preview helpers (`previews/render.py`, `previews/fixtures/<page>.py`) if missing, then renders or opens.
- The dummy preview is always opt-in — if it would scaffold a fixture from scratch, the user is told and offered the chance to fill it in first for richer demo data.
