---
name: web-preview
description: Renders a Jinja template from a Flask project in `web-apps/<slug>/` using fixture demo data and opens the result in Chrome. Use when the user wants to see what a page or template will look like without spinning up the full dev server. Triggers on "preview this page", "show me what this template renders to", "open this in Chrome", or similar.
---

# Web Preview

Render a Jinja template with demo fixture data and open the result in Chrome for visual inspection. Useful for iterating on templates or demoing a page to a stakeholder without firing up the backend.

## When to Use

- User wants to see a rendered Jinja template in the browser.
- User is iterating on a template's design and wants quick visual feedback without `docker compose up`.
- User wants to share a static rendering of a page with a stakeholder (designer, advisor) via the resulting HTML file.

## When NOT to Use

- The page depends on real database state or async behavior — spin up the actual dev server with `docker compose up`.
- The page's logic is in JavaScript that requires runtime interactions — preview produces static HTML.
- The user wants to test form submissions end-to-end.

## Prerequisites

The project at `web-apps/<slug>/` must have:

- An `app/` package per `guides/web/flask-mvp-scaffold.md` (with a `create_app("dev")` factory).
- Python with Flask available — typically inside the project's virtualenv or via `docker compose exec web`.
- A `previews/` subfolder with `render.py` (scaffolded once, see below) and `fixtures/` for per-page demo data.

If `web-apps/<slug>/previews/render.py` does not exist, scaffold it (see §"Scaffolding `render.py`" below) before running.

## Folder convention

```
web-apps/<slug>/previews/
├── render.py            # the render helper (scaffolded once per project)
├── fixtures/            # per-page fixture modules
│   ├── home.py          # provides context() for home.html
│   ├── dashboard.py
│   └── ...
└── _rendered/           # rendered HTML output (gitignored)
    └── <page>-<timestamp>.html
```

Add `previews/_rendered/` to the project's `.gitignore`.

## Process

### 1. Identify the slug and the page

User names which template (e.g., "preview the dashboard page in findvil"). Confirm with the user if ambiguous (the "page" should match a Jinja template name like `main/dashboard` for `app/blueprints/main/templates/dashboard.html`).

### 2. Verify scaffolding

```bash
test -f web-apps/<slug>/previews/render.py || echo "render.py missing"
test -f web-apps/<slug>/previews/fixtures/<page>.py || echo "fixture missing"
```

- **If `render.py` is missing:** scaffold it via the template in §"Scaffolding `render.py`" below.
- **If the fixture is missing:** scaffold a minimal fixture (see §"Scaffolding a fixture") and ask the user to fill in realistic demo data.

### 3. Run the renderer

```bash
cd web-apps/<slug> && python previews/render.py <page> [--no-open]
```

The script:
- Loads the fixture's `context()` dict.
- Renders the template via the app's Jinja environment.
- Writes the HTML to `previews/_rendered/<page>-<timestamp>.html`.
- (Unless `--no-open`) opens the file in Chrome via `open -a "Google Chrome" <file>`.

### 4. Report

Tell the user the rendered file path (so they can re-open it later) and whether Chrome was launched.

## Scaffolding `render.py`

If a project doesn't have `previews/render.py`, create it with this content:

```python
#!/usr/bin/env python3
"""Render a Jinja template with fixture data and (optionally) open in Chrome."""
import argparse, importlib.util, os, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_fixture(page: str) -> dict:
    fixture_path = ROOT / "previews" / "fixtures" / f"{page.replace('/', '_')}.py"
    if not fixture_path.exists():
        return {}
    spec = importlib.util.spec_from_file_location("fixture", fixture_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.context() if hasattr(mod, "context") else {}


def render(page: str, no_open: bool = False) -> Path:
    from app import create_app  # imported after sys.path setup
    app = create_app("dev")
    context = load_fixture(page)
    with app.app_context():
        template_name = page if page.endswith(".html") else f"{page}.html"
        html = app.jinja_env.get_template(template_name).render(**context)
    out_dir = ROOT / "previews" / "_rendered"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = page.replace("/", "-").replace(".html", "")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = out_dir / f"{safe_name}-{timestamp}.html"
    out_file.write_text(html)
    if not no_open:
        os.system(f'open -a "Google Chrome" "{out_file}"')
    return out_file


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("page", help="template name, e.g. main/home or auth/login")
    p.add_argument("--no-open", action="store_true", help="skip opening in Chrome")
    args = p.parse_args()
    out = render(args.page, args.no_open)
    print(f"Rendered: {out}")
```

Make it executable:

```bash
chmod +x web-apps/<slug>/previews/render.py
```

## Scaffolding a fixture

A fixture module exports a `context()` function returning the dict passed to the template. Per-page:

```python
# web-apps/<slug>/previews/fixtures/dashboard.py
def context():
    return {
        "user": {"name": "Alice Chen", "email": "alice@example.com"},
        "items": [
            {"id": 1, "title": "First item", "status": "active", "created_at": "2026-05-20"},
            {"id": 2, "title": "Second item", "status": "draft",  "created_at": "2026-05-21"},
            {"id": 3, "title": "Third item",  "status": "active", "created_at": "2026-05-22"},
        ],
        "total": 3,
    }
```

Per-page fixtures keep demo data realistic for the screen being previewed.

If the page name has a `/` (e.g., `main/dashboard`), the fixture filename replaces `/` with `_`: `main_dashboard.py`.

## Examples

**"Preview the dashboard page in findvil"** — render `main/dashboard.html` with `fixtures/main_dashboard.py`, open in Chrome.

```bash
cd web-apps/findvil && python previews/render.py main/dashboard
```

**"Show me main/landing for findvil but don't open it"** — render with `--no-open`, return the path so the user can choose how to open it.

```bash
cd web-apps/findvil && python previews/render.py main/landing --no-open
```

## Limitations

- **Static HTML only.** CSS and JS load from `static/` paths at browser open time; if those paths are absolute or CDN-hosted, they work. If they're relative to the dev server (`/static/...`), they'll 404 — for those cases, run the actual dev server.
- **No database access.** Templates that lazy-load ORM objects via `current_user.posts` etc. will fail; the fixture should provide already-shaped, plain-Python data.
- **No request context features.** `url_for()` works in app context but anything that depends on a real request (cookies, headers, session) will be missing.
- **macOS-only auto-open.** The `open -a "Google Chrome" ...` invocation is macOS. On Linux, replace with `google-chrome <file>`; on Windows, `start chrome <file>`. The `--no-open` flag works universally.

## Dummy mode vs. real mode (when invoked via `/preview-product`)

This skill always operates in **dummy mode** — rendering Jinja with fixture data, no live app behavior. It is one of two preview modes that `/preview-product` orchestrates:

- **Real preview** — the actual running app at `http://localhost:5000/<page>`. Requires the dev server up and all dependencies wired. `/preview-product` opens this directly in Chrome; this skill is NOT used.
- **Dummy preview** — what this skill does. Used when the dev server is down, the route isn't implemented yet, or dependencies aren't connected. The user sees the page's styling and structure with demo data — useful for visual review while the rest is being built.

When `/preview-product` invokes this skill, it explicitly tells the user "dummy preview because: <reason>" so the difference is clear. The user knows they're seeing structure + styling, not live behavior.

If invoked directly (not via `/preview-product`), explain to the user up front that this is the dummy mode — useful for template iteration, not for end-to-end testing.
