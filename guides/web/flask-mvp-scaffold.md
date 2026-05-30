# Flask MVP scaffold

> **Stack note:** This guide applies to projects whose MVP brief picks the workspace default of **dockerized Flask + Jinja + vanilla JS** (per `guides/product/mvp-scoping-methodology.md` §6.0). If a different stack is chosen (Next.js, Django, Rails, etc.), this guide does not apply — Claude will work from first principles + the agent-skills stack-agnostic skills, or you can contribute a new stack-specific scaffold guide. See `README.md` § "Stack flexibility."

The opinionated starting shape for every new dockerized Flask MVP in this workspace. Picks defaults that have worked on findvil and fijara so we are not re-deciding the same questions on every new product.

Used **right after `/scope-mvp` returns `green-lit-to-build`**. The scoping report has named the must-haves; this guide describes the order of work to stand up a deployable shell that the must-haves will be built into.

This guide is **stack-specific**. The *how to build a feature well* questions (incremental implementation, TDD, code review, shipping) are answered by the agent-skills repo at `external/agent-skills/skills/`. This guide answers *what shape the project takes* and *in what order to lay down the skeleton*.

---

## 1. Purpose

Every new Flask MVP should reach a **deployable empty shell** within the first 2-3 working sessions, before any feature work begins. The shell has:

- A factory-pattern Flask app.
- One health-check endpoint returning 200.
- Dockerfile + compose files for dev and prod.
- `.env.example` committed, `.env` gitignored, env vars wired through.
- One test that exercises the health check.
- A working deploy command that puts the shell on the production host.

Feature work begins from this shell. It does not begin from `mkdir`. The shell exists so that "is this deployable?" is answered once, early, before features mask deploy problems.

---

## 2. Operating principles

1. **Conventions over creativity at scaffold time.** The scaffold is not where to be clever. Reuse the shape below; reserve creativity for the product.
2. **Match what worked on findvil and fijara.** Same factory pattern, same blueprint layout, same logging defaults. New patterns only when the new product needs them.
3. **The scaffold produces a deployable shell, not a working product.** Working product comes from the must-haves in the MVP brief. Stay disciplined about this — adding "just one feature" before the deploy works is how deploys break in week three.
4. **Tests exist from day one.** Even if it is one test of the health check. The infrastructure for `pytest` should be live before any business logic.
5. **`.env.example` is documentation; `.env` is local-only.** Production secrets are set via the hosting platform's UI per `guides/product/mvp-scoping-methodology.md` §6.1.
6. **Don't over-architect.** Factory + blueprints + config classes is enough for the first 10 users. Avoid premature abstractions (no service layer until the second blueprint demands it; no DI containers; no event bus).
7. **Per `CLAUDE.md`, web search/fetch is free** — look up Flask docs, package versions, Dockerfile patterns without asking.

---

## 3. The target shape

```
<slug>/
├── .env.example
├── .env                       # gitignored, local-only
├── .gitignore
├── Dockerfile
├── compose.yml                # dev
├── compose.prod.yml           # prod
├── pyproject.toml             # deps + ruff + pytest config
├── README.md
├── MVP.md                     # the brief, from /scope-mvp
├── FUNDING.md                 # iff funding decision is made
├── SECRETS.md                 # gitignored, user-only secret-location notes
├── app/
│   ├── __init__.py            # create_app factory
│   ├── config.py              # Config / DevConfig / ProdConfig / TestConfig
│   ├── extensions.py          # db, login_manager, migrate — initialized in factory
│   ├── logging_config.py      # JSON formatter for prod, human for dev
│   ├── blueprints/
│   │   ├── __init__.py
│   │   └── main/
│   │       ├── __init__.py
│   │       ├── routes.py      # health check lives here at first
│   │       └── templates/
│   ├── models/
│   │   └── __init__.py
│   ├── services/              # external integrations (DO Spaces, email, etc.)
│   │   └── __init__.py
│   └── templates/
│       └── base.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # app, client, db fixtures
│   └── test_health.py         # the first test
├── migrations/                # created by flask-migrate when first model is added
└── scripts/
    └── deploy.sh              # the prod deploy command
```

**Do not deviate from this shape** without recording the reason in `README.md`. The shape is what makes new projects feel familiar; novelty here taxes every future session.

---

## 4. Default conventions

### 4.1 App factory

`app/__init__.py` is *only* the factory. No module-level Flask instance.

```python
from flask import Flask
from app.config import config_for
from app.extensions import db, login_manager, migrate
from app.logging_config import configure_logging

def create_app(config_name: str = "dev") -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_for(config_name))

    configure_logging(app)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
```

### 4.2 Blueprints from day one

Even if the MVP has one feature, the route goes in `app/blueprints/main/`. The marginal cost is one file; the cost of refactoring from a monolithic `app.py` two months in is much higher.

### 4.3 Config classes

`app/config.py`:

```python
import os

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # all other settings via env vars

class DevConfig(Config):
    DEBUG = True

class ProdConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

def config_for(name: str) -> type[Config]:
    return {"dev": DevConfig, "prod": ProdConfig, "test": TestConfig}[name]
```

All real settings come from env. Never hardcode anything that differs between dev and prod.

### 4.4 Extensions

`app/extensions.py` declares; `app/__init__.py` initializes.

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
```

### 4.5 Logging

`app/logging_config.py` sets up:

- **Dev:** human-readable to stdout, `INFO` level.
- **Prod:** JSON to stdout (DO droplet log forwarder picks it up; App Platform forwards stdout natively), `INFO` level by default, `WARNING` for noisy libraries.

Use stdlib `logging`. Do not add a logging dependency unless DO's native ingestion proves insufficient.

### 4.6 Production server

Gunicorn, not the Flask dev server. Pinned in deps:

```
gunicorn==<latest stable>
```

Run in prod compose:

```
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - 'app:create_app("prod")'
```

`-w 4` is a starting point — tune to the droplet's vCPUs once load is real.

### 4.7 Tests

`pytest` + `pytest-flask`. Tests live in `tests/`.

`tests/conftest.py` provides fixtures:

```python
import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app("test")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
```

The first test exercises the health check, period. Add more tests when the must-haves get built.

### 4.8 Linting and formatting

`ruff` only — handles formatting, import sorting, and linting in one tool. Config in `pyproject.toml`. Optionally a `pre-commit` hook that runs `ruff check --fix` and `ruff format` on commit.

### 4.9 Frontend

**Jinja templates + a small amount of hand-written JavaScript** is the default — same shape as fijara. Add a build step only if the MVP brief explicitly requires it (e.g., the must-haves include a React component for a specific page).

`app/templates/base.html` is the shared layout; per-blueprint templates extend it.

> **Important note re: agent-skills.** The agent-skills `frontend-ui-engineering` skill is written with React/TSX examples throughout. **Do not let that drift the implementation toward React inside a Flask project.** The skill's *principles* — focused components, composition over configuration, accessibility, no AI aesthetic, state placement — apply equally to Jinja partials + vanilla JS. The skill's *examples* are illustrative of the principles, not a prescription for the stack. If a code-review pass on this project surfaces "we should rewrite this as a React component" without an explicit must-have driving it, refuse.

---

## 5. The scaffold sequence

Do these in order. Do not skip ahead to feature work until the sequence is complete.

### Step 1 — Create the project root and git

```bash
mkdir <slug> && cd <slug>
git init
```

Copy the MVP brief from `<web-apps|mobile-apps>/<slug>/MVP.md` into the root if it isn't already there. Read it. The brief's *Must-haves*, *Stack*, and *Infrastructure decisions* are your build target.

### Step 2 — `.gitignore`, `.env.example`, `.env`, `SECRETS.md`

`.gitignore` includes (at minimum):

```
.env
SECRETS.md
__pycache__/
*.pyc
.venv/
.pytest_cache/
.ruff_cache/
instance/
```

`.env.example` lists every key the app will need, with comments. Copy to `.env` and fill local values.

`SECRETS.md` is for the user — a plain note saying where each production secret lives (DO console, Stripe dashboard, etc.). Gitignored.

### Step 3 — `pyproject.toml`

Define deps, ruff config, pytest config. Single source of truth.

### Step 4 — `app/` package skeleton

Create `app/__init__.py` with `create_app()`, `app/config.py`, `app/extensions.py`, `app/logging_config.py`, the `main` blueprint with one health-check route at `/healthz`.

```python
# app/blueprints/main/routes.py
from flask import Blueprint, jsonify
bp = Blueprint("main", __name__)

@bp.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200
```

### Step 5 — Dockerfile and compose

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system .
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('prod')"]
```

`compose.yml` (dev):

```yaml
services:
  web:
    build: .
    command: flask --app 'app:create_app("dev")' run --host 0.0.0.0 --port 5000 --debug
    env_file: .env
    ports: ["5000:5000"]
    volumes: [".:/app"]
    depends_on: [db]
  db:
    image: postgres:16-alpine
    env_file: .env
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```

`compose.prod.yml` mirrors but without `volumes` mounting the source, with `restart: unless-stopped`, with healthchecks, and pointing at the production DB connection string. (If using DO App Platform, the prod compose is replaced by the platform's own config.)

### Step 6 — Bring it up

```bash
docker compose up --build
```

Hit `http://localhost:5000/healthz`. Expect `{"status": "ok"}`. If not, fix before proceeding.

### Step 7 — First test

```python
# tests/test_health.py
def test_healthz(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}
```

```bash
pytest
```

It passes. If not, fix before proceeding.

### Step 8 — Deploy script and first deploy

`scripts/deploy.sh` is the canonical command. For a DO droplet running docker compose:

```bash
#!/usr/bin/env bash
set -euo pipefail
ssh "$DO_HOST" "cd /srv/<slug> && git pull && docker compose -f compose.prod.yml pull && docker compose -f compose.prod.yml up -d --build"
```

For DO App Platform, the deploy is `doctl apps create-deployment` or a git push to the linked branch.

Run the deploy. Hit `https://<your-domain>/healthz`. Confirm 200.

**Until the deploy works, the scaffold is not complete.** Do not start feature work.

### Step 9 — Commit and tag

```bash
git add . && git commit -m "scaffold: deployable shell"
git tag scaffold-done
```

The tag is a deliberate marker — anything from this point on is feature work. The scaffold is done.

---

## 6. First-week checklist

Once the scaffold is up, the first week's feature work follows the *first-week build checklist* from the scoping report (per `guides/product/mvp-scoping-methodology.md` §9). The scaffold guide just provides the platform on which that checklist runs.

A typical first week looks like:

| Day | Work |
|---|---|
| 1 | Scaffold (steps 1-9 above) |
| 2 | First must-have — the smallest one, end-to-end (route → template → test → deploy) |
| 3 | Second must-have, same shape |
| 4 | Remaining must-haves; close the success-criterion measurement gap |
| 5 | Invite the first 1-3 users; observe |
| weekend | Fix what broke; queue learnings |

Adjust to the brief's specifics, but always go end-to-end on the *first* must-have before adding the second. Half-finished routes everywhere is the failure mode this discipline prevents.

---

## 7. Handoffs

### 7.1 Outward (which workflows pick this guide up)

- `/scope-mvp` returns `green-lit-to-build` → this guide is the next thing the build follows.
- The agent-skills `code-reviewer` persona references project conventions when reviewing diffs — this guide *is* those conventions for Flask MVPs.
- The agent-skills slash commands (`/spec`, `/plan`, `/build`, `/test`, `/review`, `/ship`) operate on top of the scaffold this guide produces.

### 7.2 Inward (which guides this one defers to)

- **agent-skills repo** — `external/agent-skills/skills/incremental-implementation/`, `test-driven-development/`, `api-and-interface-design/`, `git-workflow-and-versioning/`, `ci-cd-and-automation/`, `shipping-and-launch/`. These cover the *how* of building well; this guide does not duplicate them.
- **MVP brief** — the canonical statement of what to build. The scaffold is platform; the brief is product.
- `guides/product/mvp-scoping-methodology.md` §6 — the source of truth for `.env`, DigitalOcean Spaces, hosting, and auth defaults. This guide *applies* those defaults; the scoping guide *defines* them.

### 7.3 Future companion guides (write when needed, not preemptively)

- `flask-deploy-runbook.md` — DO droplet vs. DO App Platform, the actual commands and the DNS + HTTPS path. Becomes necessary when a project is days away from first deploy.
- `flask-auth-patterns.md` — `flask-login` + sessions, OAuth via Authlib, magic-link auth. Becomes necessary when the second MVP picks a different auth than the first.
- `do-spaces-integration.md` — boto3 wrapper, signed URLs, lifecycle policies. Becomes necessary when a project needs file uploads.
- `flask-secrets-handling.md` — deeper than the scoping guide §6.1; rotation, multi-environment, audit. Becomes necessary when the secret count grows past trivial.

---

## 8. When to deviate from the scaffold

Deviations are allowed but must be **recorded in the project's `README.md`** with a one-paragraph reason. Acceptable reasons:

- The product genuinely needs an async framework (FastAPI). Then this guide does not apply; use a fork of it.
- The product is so small (a single static page + form handler) that the full structure is overkill. Document the strip-down.
- A specific must-have requires a structural choice the scaffold does not anticipate (a websocket subsystem, a queue worker, a separate admin process). Add the required structure; do not remove the defaults that still apply.

Not acceptable reasons:

- "I want to try a new pattern." Try it on a side project; this scaffold optimizes for not-re-deciding.
- "The defaults felt heavy." The defaults are calibrated for projects that ship; lighter scaffolds become rewrites at month two.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
