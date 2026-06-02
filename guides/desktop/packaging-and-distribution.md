# Packaging and distribution — desktop apps

How to turn a Python + PySide6 desktop app from `python -m <slug>` into a distributable bundle. Counterpart to `guides/web/flask-deploy-runbook.md` for the web stack.

The workspace defaults to **macOS-first** at MVP scope (one `.app` bundle, sideload to first 10 users). Windows + Linux paths exist as "when you need them" sections at the end and are deferred to v1 unless the brief demands them at MVP.

---

## 1. Scope of this guide

| Stage | Tool | Output | Where in pipeline |
|---|---|---|---|
| **MVP, dev distribution** | PyInstaller | Unsigned `.app` bundle | `/ship-app <slug> --desktop` first run |
| **MVP, first-users sideload** | PyInstaller + ad-hoc signing | `.app` + a "right-click → Open" install note | `/ship-app` post-deploy verification |
| **v1, signed + notarized** | PyInstaller + `codesign` + `notarytool` | Notarized `.app` + DMG | After validation of riskiest assumption |
| **v1, app-store** | Outside this guide (see Apple's Mac App Store docs) | `.pkg` for App Store Connect | Optional follow-up |

`/ship-app` orchestrates the first two stages by default. v1 signing + notarization is its own gated step the user opts into.

---

## 2. PyInstaller — the workspace default

`PyInstaller` is in the dev deps of the scaffold (`pip install -e ".[dev]"`). For a fresh build:

```bash
pyinstaller --windowed \
    --name "<App Name>" \
    --osx-bundle-identifier "com.<maintainer>.<slug>" \
    --icon assets/icon.icns \
    src/<slug>/__main__.py
```

Output: `dist/<App Name>.app` on macOS.

The first build writes a `desktop_app.spec` (actually `<App Name>.spec`) file at the project root. **Commit this spec.** Subsequent builds use the spec and produce consistent output: `pyinstaller <App Name>.spec`.

`scripts/build.sh` from the scaffold does this. After it runs, the bundle is at `dist/<App Name>.app` and can be opened with `open dist/"<App Name>.app"`.

### 2.1 Common spec edits

After the first build, edit the generated `.spec` to:

- **Add data files** (bundled fixtures, templates):
  ```python
  datas=[('src/<slug>/assets', '<slug>/assets')],
  ```
- **Add hidden imports** (PyInstaller misses dynamic imports):
  ```python
  hiddenimports=['<slug>.ui.late_loaded_module'],
  ```
- **Exclude modules** to slim the bundle:
  ```python
  excludes=['tkinter', 'unittest', 'pydoc'],
  ```

### 2.2 Slimming the bundle

A naive PySide6 bundle is ~150 MB. To get under 80 MB:

- Exclude unused Qt modules in the `.spec` `Analysis(excludes=...)`.
- Run `pyinstaller --onedir` (default; faster startup than `--onefile`).
- Use `--strip` to strip debug symbols from native binaries (Linux/macOS).

Don't optimize prematurely — at MVP scope, a 150 MB bundle is acceptable for sideload to first 10 users.

---

## 3. The macOS path (MVP default)

### 3.1 First run — ad-hoc signed bundle

```bash
bash scripts/build.sh
open dist/"<App Name>.app"
```

If macOS Gatekeeper blocks the app ("can't be opened because the developer cannot be verified"), the first 10 users right-click → Open → confirm. This is the **sideload** path; appropriate for MVP scope and the success-criterion's "first 10 users named in the brief."

Include a one-line note in your distribution message:

> "macOS blocks unsigned apps by default. Right-click the app and choose 'Open' — then click 'Open' on the warning. This is a one-time step per app."

### 3.2 v1 — signed + notarized

When the riskiest assumption holds and you're moving toward a real v1, this is the path. **All commands assume an Apple Developer ID** (\$99/year) and a Developer ID Application certificate installed in Keychain.

```bash
# Sign the bundle
codesign --force --deep --options runtime \
    --sign "Developer ID Application: <Your Name> (<TEAM_ID>)" \
    dist/"<App Name>.app"

# Verify the signature
codesign --verify --deep --strict --verbose=2 dist/"<App Name>.app"
spctl --assess --type execute --verbose dist/"<App Name>.app"

# Create a DMG for distribution
hdiutil create -srcfolder dist/"<App Name>.app" -volname "<App Name>" \
    -fs HFS+ -format UDZO dist/"<App Name>.dmg"

# Notarize (requires app-specific password from appleid.apple.com)
xcrun notarytool submit dist/"<App Name>.dmg" \
    --apple-id "<your-apple-id>" \
    --team-id "<TEAM_ID>" \
    --password "<app-specific-password>" \
    --wait

# Staple the notarization to the DMG
xcrun stapler staple dist/"<App Name>.dmg"
```

After staple, the DMG opens on a stock Mac with no Gatekeeper warning.

`/ship-app` does NOT run this path at MVP scope — the user explicitly opts in (a "ship-signed" sub-mode or follow-up). The MVP path stops at the unsigned-bundle sideload.

---

## 4. Windows path (deferred to v1 unless scoped at MVP)

The same `bash scripts/build.sh` on a Windows host produces `dist/<App Name>/<App Name>.exe`. For distribution:

- **Unsigned**: just zip the `dist/<App Name>/` folder. Windows SmartScreen warns first-time users; they click "More info → Run anyway."
- **Signed**: requires a code-signing certificate (\$200-400/year from DigiCert, Sectigo, etc.). The `signtool` workflow is documented at [Microsoft's code-signing docs](https://learn.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools); add specifics here when a real product needs it.
- **Installer**: use [Inno Setup](https://jrsoftware.org/isinfo.php) (free) to wrap the `dist/` folder in a `.exe` installer.

Dev on macOS, distribute on Windows: cross-platform packaging via CI (GitHub Actions with a `windows-latest` runner) is the cleanest pattern. The CI YAML lives at `desktop-apps/<slug>/.github/workflows/build.yml` when needed.

---

## 5. Linux path (deferred to v1 unless scoped at MVP)

PyInstaller on Linux produces `dist/<App Name>/` (a directory of binaries). For distribution:

- **AppImage** (recommended): use [appimagetool](https://github.com/AppImage/AppImageKit) to wrap `dist/<App Name>/` into a single `<App Name>.AppImage`. Users `chmod +x` and run.
- **Flatpak / Snap**: distribution channels, more involved; defer until there's user demand from Linux first 10 users.
- **deb / rpm**: distribution-specific; use [fpm](https://github.com/jordansissel/fpm) for the simplest path.

Same CI pattern as Windows: a `ubuntu-latest` runner builds the Linux artifact alongside the macOS / Windows ones.

---

## 6. Cross-platform CI (when MVP demands it)

If the brief's success criterion needs cross-platform from day 1, set up GitHub Actions early. Minimum YAML:

```yaml
# desktop-apps/<slug>/.github/workflows/build.yml
name: build

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, windows-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: bash scripts/build.sh
      - uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.os }}-bundle
          path: dist/
```

This is enough to produce three artifacts per push. Wire signing into the matrix later, per-platform.

`senior-devops-engineer` writes and maintains this file (per `CLAUDE.md`'s build-orchestration routing).

---

## 7. What `/ship-app --desktop` does

When the user runs `/ship-app <slug> --desktop`, `senior-devops-engineer` executes:

1. **Build** — `bash scripts/build.sh` (or `pyinstaller <App Name>.spec`).
2. **Verify** — confirm `dist/<App Name>.app` exists and runs (`open dist/"<App Name>.app"`; bundle launches without errors).
3. **Sideload prep** — generate the distribution README snippet with the right-click-Open instructions for first 10 users.
4. **Post-deploy verification** — smoke-test the bundled app once; check for missing-dep warnings in `~/Library/Logs/DiagnosticReports/` (macOS).
5. **`BUILD_STATUS.md` update** — record bundle version, build SHA, platform, distribution mode (sideload / signed / etc.).

The user gets:

```
Built <App Name>.app at desktop-apps/<slug>/dist/<App Name>.app (<size> MB).
Smoke-test passed. Ready for sideload.

Distribute to your first 10 users with this message:
  "Download <App Name>.app, drag to Applications, then right-click → Open
  on first launch to bypass macOS Gatekeeper. This is a one-time step."
```

If the user later runs `/ship-app <slug> --desktop --signed`, the v1 signing + notarization flow from §3.2 runs instead.

---

## 8. What this guide does NOT cover

- **Auto-update mechanisms** (Sparkle for macOS, Squirrel for Windows). Add when there's a second release and the user has actual installed-base care-abouts.
- **Crash reporting** (Sentry, Bugsnag, custom). Add when MTTR matters more than shipping the next feature.
- **In-app analytics**. Out of scope by default — desktop privacy expectations are higher than web.
- **App-store submission** (Mac App Store, Microsoft Store, Snap Store). Each has its own review process and constraints; document when a product targets one.
- **Hardware-accelerated graphics, video, audio** — these need Qt modules that complicate packaging; address per-product when scoped.

Add follow-up guides at `guides/desktop/` only when a real product demands them.
