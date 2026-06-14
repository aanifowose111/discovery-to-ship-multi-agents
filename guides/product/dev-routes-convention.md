# `_dev/` routes convention — Flask + React Native

For web and mobile apps in this workspace, **dev-only test routes live under a registered `_dev/` prefix**, gated by an environment variable, and absent from production builds by default. This is the canonical pattern.

The use case: many actions in a real app are hard to exercise via the normal UI — POST endpoints that don't accept GET (you can't paste them in a browser), side-effecting helpers (clear-cache, reset-trial-window, kill-session), debug helpers (identity dump, current-tenant dump, run-diagnostic-now). The `_dev/` prefix gives these a registered, discoverable home — and a single env var to switch the entire surface on or off per environment.

The example reference is `web-apps/ops-audit-agent/` which already follows this pattern: `/_dev/logout`, `/_dev/run_diagnostic`, `/_dev/whoami`.

---

## 1. Flask web apps

### 1.1 Blueprint structure

Create a `_dev` blueprint under `app/blueprints/_dev.py`:

```python
"""
Dev-only test routes. Gated by DEV_ROUTES_ENABLED env var.

Production: DEV_ROUTES_ENABLED is unset → blueprint is not registered → all
/_dev/* paths return 404.

Dev + staging: DEV_ROUTES_ENABLED=true → blueprint is registered → routes serve.
"""

from flask import Blueprint, jsonify, session, g, abort
from flask_login import current_user, logout_user, login_required

bp = Blueprint("_dev", __name__, url_prefix="/_dev")


@bp.before_request
def _require_dev_mode():
    """Belt-and-braces: even if mounted, refuse if env var is off."""
    from flask import current_app
    if not current_app.config.get("DEV_ROUTES_ENABLED"):
        abort(404)


@bp.route("/whoami")
def whoami():
    """Dump the current user identity for testing auth."""
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False}), 200
    return jsonify({
        "authenticated": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "tenant_slug": g.tenant.slug if g.tenant else None,
    }), 200


@bp.route("/logout", methods=["GET", "POST"])
def dev_logout():
    """Idempotent logout; accepts GET for easy testing via browser."""
    logout_user()
    session.clear()
    return jsonify({"ok": True}), 200


# ... add more routes as needed for testing.
```

### 1.2 Registration in `app/__init__.py`

```python
if app.config.get("DEV_ROUTES_ENABLED"):
    from app.blueprints import _dev
    app.register_blueprint(_dev.bp)
```

### 1.3 Config in `app/config.py`

```python
class BaseConfig:
    DEV_ROUTES_ENABLED = False  # off by default

class DevConfig(BaseConfig):
    DEV_ROUTES_ENABLED = True

class StagingConfig(BaseConfig):
    # On by default for staging too — useful for ops smoke-tests
    DEV_ROUTES_ENABLED = bool(os.environ.get("DEV_ROUTES_ENABLED", "true"))

class ProdConfig(BaseConfig):
    # Hard-off in prod unless deliberately turned on
    DEV_ROUTES_ENABLED = bool(os.environ.get("DEV_ROUTES_ENABLED", ""))

class TestConfig(BaseConfig):
    DEV_ROUTES_ENABLED = True  # tests can exercise the routes
```

### 1.4 The 404 contract

Production with `DEV_ROUTES_ENABLED` unset returns **404 (not 403)** on any `/_dev/*` path. Reason: 403 leaks "this route exists but you can't access it"; 404 leaks nothing. The blueprint either is or isn't registered; there's no per-user gate.

### 1.5 Routes that should exist by default

Every Flask web app following the workspace conventions should at minimum have:

| Route | Method | Purpose |
|---|---|---|
| `/_dev/whoami` | GET | Dump current user identity + tenant context |
| `/_dev/logout` | GET, POST | Idempotent logout for cross-tenant testing |
| `/_dev/healthz` | GET | Dev-mode-only deeper health check (vs. public `/healthz`) |

Add per-product routes as needed: `/_dev/run_diagnostic`, `/_dev/reset_trial`, `/_dev/clear_cache`, etc.

### 1.6 Auth on dev routes

By default, dev routes do **not** require authentication — they're for testing, including testing the unauthenticated surface. If a dev route needs the current user (`/_dev/whoami`), check `current_user.is_authenticated` and respond accordingly.

If a specific dev route needs auth (e.g., `/_dev/dump_current_tenant_audit_events` would be too revealing without an auth check), apply `@login_required` per-route as usual.

### 1.7 Tests

`tests/test_dev_routes.py`:

```python
def test_dev_routes_404_when_disabled(client_no_dev):
    """In prod-like config (DEV_ROUTES_ENABLED=False), all /_dev/* paths 404."""
    assert client_no_dev.get("/_dev/whoami").status_code == 404
    assert client_no_dev.post("/_dev/logout").status_code == 404


def test_dev_routes_200_when_enabled(client):
    """In dev config, /_dev/whoami responds."""
    response = client.get("/_dev/whoami")
    assert response.status_code == 200
    assert "authenticated" in response.json
```

---

## 2. React Native + Expo mobile apps

### 2.1 Screen tree structure

Mobile apps use a hidden screen tree mounted only when `EXPO_PUBLIC_DEV_ROUTES=1`:

```
src/screens/_dev/
  index.tsx         # menu of dev screens
  Whoami.tsx
  Logout.tsx
  ResetTrial.tsx
```

### 2.2 Mounting in the navigation stack

```typescript
// src/navigation/RootNavigator.tsx

const DEV_ROUTES_ENABLED = process.env.EXPO_PUBLIC_DEV_ROUTES === "1";

export function RootNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Home" component={Home} />
      {/* ... other screens ... */}
      {DEV_ROUTES_ENABLED && (
        <Stack.Screen
          name="_DevMenu"
          component={DevMenuScreen}
          options={{ title: "Dev Menu" }}
        />
      )}
    </Stack.Navigator>
  );
}
```

### 2.3 Discovery

The dev menu is reachable via:

- **A hidden gesture** on the splash screen (e.g., long-press the logo 5 times) — fires `navigation.navigate("_DevMenu")`.
- **A debug URL scheme** when `EXPO_PUBLIC_DEV_ROUTES=1` — `myapp://dev/menu` opens the menu directly.

The gesture is intentional: it's discoverable to someone who knows about it (the dev team) but invisible to ordinary users even if the build accidentally ships with the env var set.

### 2.4 Production builds

For App Store / Play Store production builds, `EXPO_PUBLIC_DEV_ROUTES` is unset → the screens are not registered → the gesture and URL scheme do nothing.

### 2.5 Routes that should exist by default

| Screen | Purpose |
|---|---|
| `_dev/Whoami` | Dump current user identity (from secure store) |
| `_dev/Logout` | Force logout + clear secure store |
| `_dev/ApiInspector` | Show last 10 API calls + responses (useful for debugging Flask backend) |
| `_dev/EnvDump` | Show resolved env config (which `EXPO_PUBLIC_*` vars are set) — never expose secrets |

---

## 3. Desktop (PySide6)

Desktop apps follow a similar convention — a hidden `Dev` menu in the menubar gated by `DEV_ROUTES_ENABLED=true` env var. Reachable via keyboard shortcut (e.g., `Cmd+Shift+D`) only when enabled.

Less critical than web/mobile (desktop apps are single-user) but still useful for testing modal flows and side-effects.

---

## 4. Anti-patterns

- **Putting prod-only secrets in dev-route responses.** `/_dev/whoami` dumping `current_user.api_key_hash` is wrong even though dev routes are 404 in prod — defense in depth.
- **Treating dev routes as private API endpoints.** They're for testing, not for the real client. If the dashboard needs `/whoami`, build a real `/api/v1/whoami` instead.
- **Forgetting the 404 contract.** A dev route that 403s in prod (because the env var is set but the user isn't admin) leaks the route exists. Either return 404 or don't mount the blueprint.
- **Bundling all `_dev/*` under `@login_required`.** Then you can't test the unauthenticated surface. Default to no auth; require it per-route only when the response would leak something sensitive.

---

## 5. Why this convention exists

POST endpoints that don't accept GET are genuinely hard to test in dev — `curl -X POST` works but is friction. The `_dev/<thing>` convention gives every POST a corresponding GET-accessible test surface, so a developer can paste a URL in a browser and see the side-effect happen.

Across products, the same convention means:

- Cohort 1 founders who poke around in dev mode see consistent affordances.
- The build-phase orchestrator (and `/smoke`) can reliably look for `/_dev/*` routes when seeding playbooks.
- Code review against a new product knows where to find the dev surface — under `app/blueprints/_dev.py` (web) or `src/screens/_dev/` (mobile).
- `VERIFIED.md` can record `/_dev/*` JSON responses verbatim as the "presentation" field for verifying side-effecting flows.

---

*Last updated: 2026-06-13.*
