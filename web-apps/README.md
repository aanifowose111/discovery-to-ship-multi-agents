# web-apps/

Your dockerized Flask web applications. **This folder is gitignored** (except this README) — each individual product is its own private workspace.

## Per-product layout

When a card reaches `green-lit-to-build` and `/scope-mvp` produces a brief, the build phase starts here. Each product is a subfolder at `web-apps/<slug>/`:

```
web-apps/<slug>/
├── MVP.md                  Source-of-truth brief (from /scope-mvp)
├── FUNDING.md              Funding-path decision (if applicable)
├── README.md               Per-product overview
├── Dockerfile
├── compose.yml             (dev)
├── compose.prod.yml        (prod)
├── pyproject.toml
├── app/                    Flask app per `guides/web/flask-mvp-scaffold.md`
├── tests/
├── scripts/
│   └── deploy.sh
├── design/                 (only after the optional design phase)
│   ├── DESIGN_RESEARCH.md
│   ├── DESIGN_BRIEF.md
│   ├── figma/
│   │   └── README.md       (Figma link record + frame index)
│   └── handoff/
│       ├── tokens.json
│       ├── assets/
│       └── screenshots/
└── previews/               (only if using the `web-preview` skill)
    ├── render.py
    ├── fixtures/
    └── _rendered/          (gitignored within the project)
```

## Build guides

- `guides/web/flask-mvp-scaffold.md` — the 9-step scaffold sequence from `mkdir` to a deployable empty shell.
- `guides/web/flask-deploy-runbook.md` — DO droplet + Caddy or DO App Platform.
- `guides/web/do-spaces-integration.md` — file storage via DO Spaces.
- `guides/web/flask-auth-patterns.md` — sessions + Argon2 + CSRF + JWT for mobile clients.

## Each product is its own world

Each `<slug>/` subfolder can have its own dependencies, its own deploy target, its own auth choice. The guides describe the workspace's *defaults* — deviations are recorded in the product's `README.md` with a reason.
