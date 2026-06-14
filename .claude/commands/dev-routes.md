---
description: List all registered `_dev/*` routes / screens for a product (Flask blueprint, RN screen tree, or desktop dev menu). Cross-references each route against `VERIFIED.md` so you can see which dev routes have been manually verified vs. not. Reminds you of the env-var gating + the 404 contract in production. Per guides/product/dev-routes-convention.md.
argument-hint: <product-slug>
---

You are about to list the dev-route surface for one product and cross-reference it against `VERIFIED.md`.

**Use this when:**
- You want a single view of what `_dev/*` routes exist in the product
- You're about to write smoke tests or backfill `VERIFIED.md` and want a checklist of dev routes
- You're auditing whether the env-var gating is set up correctly (defense-in-depth check)
- You want to see which dev routes have been manually verified vs. not

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight

1. **Locate the product folder.** Stop if not found.

2. **Determine the stack** from the folder root (`web-apps/` → Flask, `mobile-apps/` → RN, `desktop-apps/` → PySide6).

### Do

#### For Flask web apps

1. **Read `<product-folder>/app/blueprints/_dev.py`** if it exists. If it doesn't, surface: "No `_dev` blueprint found. Per `guides/product/dev-routes-convention.md`, every Flask product should have `app/blueprints/_dev.py` gated by `DEV_ROUTES_ENABLED`. Want me to scaffold one?" — and stop if the user declines.

2. **Parse the blueprint** for route decorators (`@bp.route("...")`). Extract:
   - Route path
   - HTTP methods
   - View function name
   - First line of docstring (purpose)

3. **Read `<product-folder>/app/__init__.py`** to confirm the blueprint registration is conditional on `DEV_ROUTES_ENABLED`. Note in the output whether it is or isn't.

4. **Read `<product-folder>/app/config.py`** to confirm the env-var defaults per environment (Dev / Staging / Prod / Test). Note any discrepancy from the convention guide.

#### For RN mobile apps

1. **Read `<product-folder>/src/screens/_dev/`** if it exists. List the screens.

2. **Read `<product-folder>/src/navigation/RootNavigator.tsx`** (or equivalent) and confirm the dev tree is gated on `EXPO_PUBLIC_DEV_ROUTES`.

#### For desktop (PySide6)

1. **Read the dev menu definition** (`app/ui/menus/dev_menu.py` or similar). List the menu actions + their keyboard shortcuts.

2. **Confirm the menu is gated** on `DEV_ROUTES_ENABLED`.

### Cross-reference against VERIFIED.md

1. **Read `<product-folder>/VERIFIED.md`** if it exists. For each dev route / screen / menu item, check whether a corresponding entry exists in `VERIFIED.md`. Fuzzy-match on the route path or description.

2. **Mark each route** as one of:
   - 🟢 **Verified** — `VERIFIED.md` has a `[x]` entry referencing this route
   - 🟡 **Partial** — `VERIFIED.md` has `[~]` or `[?]` entry
   - 🔴 **Not working** — `VERIFIED.md` has `[!]` entry (orchestrator-surfaced)
   - ⚪ **No coverage** — no `VERIFIED.md` entry yet

### Stop here — output

Show the user a table:

> 🛠 Dev-route registry for `<slug>` (`<stack>`):
>
> **Env-var gating**: `DEV_ROUTES_ENABLED` — Dev: `<state>` / Staging: `<state>` / Prod: `<state>` / Test: `<state>`. Conditional registration in `app/__init__.py`: `<yes/no>`. Belt-and-braces 404 in `_dev.py`: `<yes/no>`.
>
> **Routes (`<N>` total):**
>
> | Route | Methods | Purpose | VERIFIED.md status |
> |---|---|---|---|
> | `/_dev/whoami` | GET | Dump current user identity | 🟢 Verified |
> | `/_dev/logout` | GET, POST | Idempotent logout | 🟢 Verified |
> | `/_dev/run_diagnostic` | POST | Trigger diagnostic run | ⚪ No coverage |
> | `/_dev/reset_trial` | POST | Reset trial window for testing | 🔴 Not working ("reset succeeded but trial flag stayed true") |
>
> **Coverage summary:**
> - Verified: `<N>`
> - Not yet checked: `<N>` (consider walking through with `/do-verify <slug>` next)
> - Flagged not-working: `<N>`
>
> **Convention drift findings** (if any):
> - Production config doesn't hard-off `DEV_ROUTES_ENABLED` — recommended fix: set `DEV_ROUTES_ENABLED = bool(os.environ.get("DEV_ROUTES_ENABLED", ""))` in `ProdConfig`.
> - `_dev/` blueprint missing `before_request` 404 fallback — consider adding the belt-and-braces gate.

### Notes

- **Read-only command.** Lists state, doesn't modify the routes or `VERIFIED.md`.
- **Convention reference:** `guides/product/dev-routes-convention.md` — link this to the user if they want to know what the gating should look like.
- **For RN mobile**, the cross-reference is screen-to-VERIFIED.md entry (less precise than route paths, but the same idea).
- **For desktop**, list the menu actions and same cross-reference logic.
- **Suggested next:** "Run `/do-verify <slug>` to add verification entries for the `<N>` uncovered routes."
