# desktop-apps/

Your cross-platform desktop applications. **This folder is gitignored** (except this README) — each individual product is its own private workspace.

## Default stack

Python 3.10+ with **PySide6** (Qt for Python, LGPL) for the UI layer, packaged for distribution via **PyInstaller**. Cross-platform-capable (macOS / Windows / Linux); the workspace defaults to **macOS-first** for MVP scope and treats Windows / Linux packaging as "when you need them" follow-ups. Per `CLAUDE.md`'s stack-flexibility working-style bullet, the desktop stack — like web and mobile — is a default, not a requirement: a different stack (C# + Avalonia, Electron, Tauri, etc.) can be picked at `/scope-mvp` time and the build proceeds without the default guides.

Rationale for the Python+PySide6 default is in `guides/desktop/python-mvp-scaffold.md`.

## Per-product layout

When a card reaches `green-lit-to-build` and `/scope-mvp` produces a brief that picks the desktop default stack, the build phase starts here. Each product is a subfolder at `desktop-apps/<slug>/`:

```
desktop-apps/<slug>/
├── MVP.md                  Source-of-truth brief (from /scope-mvp)
├── FUNDING.md              Funding-path decision (if applicable)
├── README.md               Per-product overview
├── BUILD_STATUS.md         Subsystem checklist + history (owned by senior-software-engineer)
├── pyproject.toml          Project metadata + deps
├── src/
│   └── <slug>/
│       ├── __init__.py
│       ├── __main__.py     `python -m <slug>` entry point
│       ├── main.py         App bootstrap (creates QApplication, opens main window)
│       ├── ui/             PySide6 widgets, layouts, signals/slots
│       │   ├── __init__.py
│       │   └── main_window.py
│       ├── core/           Business logic (no Qt imports — testable as plain Python)
│       │   └── __init__.py
│       └── assets/         Icons, fixtures, bundled data
├── tests/
│   ├── test_core/          Plain pytest against core/
│   └── test_ui/            pytest-qt against ui/
├── scripts/
│   ├── dev.sh              Activate venv + `python -m <slug>`
│   └── build.sh            PyInstaller build (per the packaging guide)
├── desktop_app.spec        PyInstaller spec (committed; generated once by the packaging guide)
├── dist/                   PyInstaller output (gitignored)
├── build/                  PyInstaller intermediates (gitignored)
├── .venv/                  Local venv (gitignored)
└── design/                 (only after the optional design phase)
    ├── DESIGN_RESEARCH.md
    ├── DESIGN_BRIEF.md
    ├── figma/
    │   └── README.md       (Figma link record + frame index)
    └── handoff/
        ├── tokens.json
        ├── assets/
        └── screenshots/
```

## What the slash commands do here

- **`/scope-mvp <slug>`** with a desktop pick produces an `MVP.md` whose §6 confirms Python + PySide6 (or whatever the user picked).
- **`/start-build <slug>`** orchestrates the build through `senior-software-engineer`, which routes Qt UI work to `senior-desktop-engineer`, business logic to `senior-backend-engineer`, and tests to `senior-qa-engineer`.
- **`/preview-product <slug>`** for a desktop app launches `python -m <slug>` from the project's venv and tells you where to look.
- **`/ship-app <slug> --desktop`** runs the QA + security pre-flight gates, then invokes `senior-devops-engineer` to build a distributable artifact via PyInstaller per `guides/desktop/packaging-and-distribution.md`.

## Why is this folder gitignored?

Each product belongs to you, not the workspace. The repo ships scaffolding — methodology guides, slash commands, personas, skills — and the products you build on top of it are private until you choose to publish them separately. This README is the only file tracked here.
