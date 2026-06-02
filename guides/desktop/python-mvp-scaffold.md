# Python + PySide6 desktop-app scaffold (workspace default)

The workspace-default scaffold for desktop apps. Mirrors `guides/web/flask-mvp-scaffold.md` and `guides/mobile/react-native-mvp-scaffold.md` in spirit: opinionated layout, conventions that let Claude generate consistent code, sensible defaults you can override at the brief level.

If the user picks a non-default stack at `/scope-mvp` (C# + Avalonia, Electron, Tauri, Flet, etc.), **this guide does not apply**. Work from first principles + the agent-skills' stack-agnostic skills (`spec-driven-development`, `frontend-ui-engineering` principles, `test-driven-development`, `shipping-and-launch`); the brief records which stack was picked.

---

## 1. Purpose

Take an MVP brief whose §6 confirms the **Python + PySide6 + PyInstaller** stack and turn it into a runnable desktop app skeleton that:

- Boots a Qt main window from `python -m <slug>` without packaging.
- Separates UI (PySide6, hard to test in isolation) from core logic (pure Python, easy to test).
- Has a smoke test that runs in CI without a display (xvfb-free using pytest-qt's offscreen platform).
- Is packageable into a `.app` bundle on macOS via PyInstaller with one `bash scripts/build.sh`.

The product code that lives inside this skeleton comes from `/start-build`'s subsystem-by-subsystem build, orchestrated by `senior-software-engineer` and routed to `senior-desktop-engineer` for the UI/packaging surface.

---

## 2. Operating principles

1. **`core/` is Qt-free.** Business logic, models, data access, validation — all plain Python with no `from PySide6 import` lines. This is the part you can test exhaustively, ship to a web/CLI version later, or hand to a non-Qt frontend without changing.
2. **`ui/` is thin.** A widget is a button + a signal connection + a one-line call into `core/`. If a widget contains business rules, move them.
3. **Cross-platform code by default; macOS-first by execution.** Don't write `if sys.platform == "darwin"` branches at MVP scope. Run + package on macOS (the maintainer's stack); Windows / Linux paths are documented in `guides/desktop/packaging-and-distribution.md` and deferred to v1 unless the brief demands them at MVP.
4. **No native dependencies until you need them.** Pure Python + PySide6 + a small handful of pip deps. If the product needs SQLite, file watchers, system tray, etc., add them when scoped — not preemptively.
5. **Signals over getters.** Qt's signal/slot pattern is the unit of UI ↔ core communication. Resist the urge to expose getters from widgets to core; emit a signal, let core handle it, signal back to UI.

---

## 3. The target shape

```
desktop-apps/<slug>/
├── MVP.md                  Brief
├── README.md               Per-product overview
├── BUILD_STATUS.md         Subsystem checklist
├── pyproject.toml          Project metadata + deps
├── .gitignore              Per-product (extends repo .gitignore)
├── .python-version         Pinned Python version (pyenv-compatible)
├── src/
│   └── <slug>/
│       ├── __init__.py
│       ├── __main__.py     `python -m <slug>` entry
│       ├── main.py         App bootstrap (QApplication, main window)
│       ├── ui/             PySide6 widgets and layouts
│       │   ├── __init__.py
│       │   └── main_window.py
│       ├── core/           Pure Python business logic (no Qt imports)
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── services.py
│       └── assets/         Icons, fixtures, bundled data
├── tests/
│   ├── __init__.py
│   ├── test_core/          pytest against core/
│   │   ├── __init__.py
│   │   └── test_smoke.py
│   └── test_ui/            pytest-qt against ui/
│       ├── __init__.py
│       └── test_main_window.py
├── scripts/
│   ├── dev.sh              `source .venv/bin/activate && python -m <slug>`
│   └── build.sh            Calls PyInstaller per the packaging guide
├── desktop_app.spec        PyInstaller spec (committed after first build)
├── dist/                   PyInstaller output (gitignored)
├── build/                  PyInstaller intermediates (gitignored)
└── .venv/                  Local venv (gitignored)
```

---

## 4. Default conventions

### 4.1 Entry point — `src/<slug>/__main__.py`

```python
"""`python -m <slug>` entry point."""
from <slug>.main import run

if __name__ == "__main__":
    run()
```

### 4.2 Bootstrap — `src/<slug>/main.py`

```python
"""App bootstrap: QApplication + main window."""
import sys
from PySide6.QtWidgets import QApplication

from <slug>.ui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("<Display Name>")
    app.setOrganizationName("<Org or Maintainer Name>")

    window = MainWindow()
    window.show()

    return app.exec()
```

### 4.3 Main window — `src/<slug>/ui/main_window.py`

```python
"""Main application window. UI only; defers logic to core/."""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("<App Name>")
        self.resize(960, 600)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(QLabel("Hello from <slug>"))
        self.setCentralWidget(central)
```

Subsequent widgets live as siblings in `ui/`: `ui/<feature>_view.py`, etc. Each widget connects its signals (button clicked, text changed) to `core/` services; `core/` emits results back via Qt signals defined on a `QObject` service class — never by importing UI types into `core/`.

### 4.4 Core layout — `src/<slug>/core/`

`core/` is **plain Python.** No PySide6 imports. Models are `@dataclass`es or Pydantic models; services are classes with explicit dependencies passed in (no globals).

```python
# core/services.py
from dataclasses import dataclass


@dataclass(frozen=True)
class GreetingResult:
    text: str


class GreetingService:
    def greet(self, name: str) -> GreetingResult:
        return GreetingResult(text=f"Hello, {name}!")
```

The bridge between `core/` and `ui/` is a `QObject` adapter in `ui/`:

```python
# ui/greeting_bridge.py
from PySide6.QtCore import QObject, Signal

from <slug>.core.services import GreetingService


class GreetingBridge(QObject):
    greeted = Signal(str)

    def __init__(self, service: GreetingService | None = None) -> None:
        super().__init__()
        self._service = service or GreetingService()

    def request(self, name: str) -> None:
        result = self._service.greet(name)
        self.greeted.emit(result.text)
```

### 4.5 Tests — `tests/test_core/` and `tests/test_ui/`

**Core tests are plain pytest:**

```python
# tests/test_core/test_smoke.py
from <slug>.core.services import GreetingService


def test_greet_returns_expected_text() -> None:
    result = GreetingService().greet("World")
    assert result.text == "Hello, World!"
```

**UI tests use `pytest-qt`** which spawns a Qt event loop in a fixture (`qtbot`). With Qt's offscreen platform, these run in CI without a display:

```python
# tests/test_ui/test_main_window.py
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # before any PySide6 import

from <slug>.ui.main_window import MainWindow


def test_main_window_shows_title(qtbot) -> None:
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.windowTitle() == "<App Name>"
```

The `QT_QPA_PLATFORM=offscreen` env var is the cross-platform trick that lets UI tests run in CI without `xvfb` (Linux) or a headed display (macOS). Set it in `conftest.py` to apply globally.

### 4.6 `pyproject.toml`

```toml
[project]
name = "<slug>"
version = "0.1.0"
description = "<one-line description from MVP.md>"
requires-python = ">=3.10"
dependencies = [
    "PySide6>=6.7,<7",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-qt>=4.4",
    "ruff>=0.5",
    "mypy>=1.10",
    "pyinstaller>=6.10",
]

[project.scripts]
<slug> = "<slug>.main:run"

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 4.7 `conftest.py`

```python
# tests/conftest.py
import os

# Run all PySide6/Qt tests with the offscreen platform — no display needed.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
```

### 4.8 Dev / build scripts

```bash
# scripts/dev.sh
#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
python -m <slug>
```

```bash
# scripts/build.sh
#!/usr/bin/env bash
# Calls PyInstaller per guides/desktop/packaging-and-distribution.md
set -euo pipefail
source .venv/bin/activate
pyinstaller --windowed --name "<App Name>" --osx-bundle-identifier "com.<maintainer>.<slug>" \
    src/<slug>/__main__.py
# Output in dist/<App Name>.app on macOS, dist/<App Name>/ + .exe on Windows.
```

Mark both executable: `chmod +x scripts/*.sh`.

### 4.9 Per-product `.gitignore`

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
dist/
build/
*.spec.bak
.DS_Store
```

(The repo-level `.gitignore` already ignores `desktop-apps/<slug>/` entirely; this per-product `.gitignore` matters once the user pushes the product to its own git repo.)

---

## 5. The scaffold sequence

### Step 1 — Create the project root, venv, pyproject

```bash
cd desktop-apps/<slug>
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
# Create pyproject.toml (per §4.6), then:
pip install -e ".[dev]"
```

### Step 2 — Lay down the package skeleton

```bash
mkdir -p src/<slug>/{ui,core,assets} tests/{test_core,test_ui} scripts
touch src/<slug>/{__init__.py,__main__.py,main.py}
touch src/<slug>/ui/{__init__.py,main_window.py}
touch src/<slug>/core/{__init__.py,models.py,services.py}
touch tests/{__init__.py,conftest.py}
touch tests/test_core/{__init__.py,test_smoke.py}
touch tests/test_ui/{__init__.py,test_main_window.py}
touch scripts/{dev.sh,build.sh}
chmod +x scripts/*.sh
```

Then fill each file with the §4 content.

### Step 3 — Smoke run

```bash
python -m <slug>
```

A 960×600 window with "Hello from `<slug>`" appears. Quit it.

### Step 4 — Smoke tests

```bash
pytest
```

Both `test_core/test_smoke.py` and `test_ui/test_main_window.py` pass.

### Step 5 — First package build (macOS)

```bash
bash scripts/build.sh
open dist/"<App Name>.app"
```

The bundled app opens. (Code signing / notarization come at v1, per `guides/desktop/packaging-and-distribution.md` §3.)

### Step 6 — `BUILD_STATUS.md` from the dynamic template

`senior-software-engineer` writes a desktop-flavored `BUILD_STATUS.md` per `guides/product/build-status-methodology.md`. Desktop subsystems include: **project tree**, **core models + services**, **UI shell (main window + navigation)**, **per-feature widgets**, **packaging spec**, **smoke tests**, **CI / signing path**. Auth and remote sync only appear if the brief includes them.

---

## 6. First-week checklist

A product that's healthy after a week of `/start-build` shows:

- [ ] `python -m <slug>` launches a window on the maintainer's machine
- [ ] `pytest` runs green on both core and UI suites in under 10 seconds
- [ ] `bash scripts/build.sh` produces a runnable `.app` (or `.exe` if cross-platform from day 1)
- [ ] `core/` has no `from PySide6` imports
- [ ] `BUILD_STATUS.md` shows ≥3 subsystems at `[x]` and clear next-step `[>]`
- [ ] Git commits are small, focused, and reviewed (per agent-skills `git-workflow-and-versioning`)

### Skills Claude applies automatically during the build

Per `CLAUDE.md`'s build-phase auto-invocation list. Specifically for desktop work:

- **`frontend-ui-engineering`** — *principles* apply (focused widgets, signal/slot composition, no AI aesthetic, state placement); the skill's React examples translate to PySide6 widgets by analogy. The widget = component, signal = callback prop, slot = effect.
- **`test-driven-development`** — write a `core/` test first; let it fail; implement until green. UI tests can come second since they're slower and noisier.
- **`code-review-and-quality`** — same as web/mobile.
- **`security-and-hardening`** — file I/O, OS shell-out, OAuth flow if used, local secret storage (use `keyring` library, not raw `.json` files).
- **`shipping-and-launch`** — at `/ship-app` time, this skill's pre-launch checklist applies; the packaging path differs from web but the checklist generalizes.
- **`debugging-and-error-recovery`** — Qt's signal/slot debugging is tricky; the skill's "narrow the cause, reproduce reliably" loop applies directly.

---

## 7. Common stumbles + fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `python -m <slug>` errors with `ModuleNotFoundError` | venv not activated or package not installed editable | `source .venv/bin/activate && pip install -e ".[dev]"` |
| App window doesn't appear (no error) | `QApplication` instance not held; garbage collected | Hold `app` reference in `run()`; don't return before `app.exec()` |
| pytest-qt tests hang in CI | display backend mismatch | Set `QT_QPA_PLATFORM=offscreen` in `conftest.py` before any PySide6 import |
| PyInstaller build runs but bundle won't open | missing dynamic dep or wrong entry | re-run with `--debug imports`; check `dist/<App Name>/Contents/Resources/PyInstaller-warn-*.txt` |
| Bundle opens then silently quits | bundled Python can't find Qt plugins | typically a stale `.spec` file; delete `desktop_app.spec` + `dist/` + `build/` and rebuild |
| signals fire twice | accidental double `connect()` call (e.g., on every show) | move `.connect()` to `__init__`, not to event handlers |

---

## 8. Why Python + PySide6 (and not the other candidates)

Brief rationale; full discussion is at `CLAUDE.md` and the v0.5.0 CHANGELOG entry.

| Stack | Verdict |
|---|---|
| **Python + PySide6** | Default. Minimum context-switch from the maintainer's Python stack; reads like the rest of the workspace's code; mature Qt ecosystem; cross-platform; LGPL-licensed. |
| Python + Flet | Honorable mention if you want declarative-UI + hot-reload. Switch via `/scope-mvp` stack-confirmation. |
| C# + Avalonia | Strong alternative if static typing matters more than language continuity. Adds .NET SDK to system reqs; more boilerplate per widget. |
| C++ + Qt | Skip for indie / first-product work. Iteration speed and readability lose to Python. |
| Electron / Tauri | Web-stack desktop. Pick if the team's strongest stack is web and "looks native" is negotiable. Outside this guide's scope. |

The stack is a default, not a requirement; the brief picks per product.
