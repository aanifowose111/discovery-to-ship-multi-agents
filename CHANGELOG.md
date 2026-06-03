# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

This project does not yet follow strict semantic versioning. Pre-1.0, breaking changes happen as the methodology evolves. Once the system stabilizes through use, this will move to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Conventions for entries under `[Unreleased]`:**

- New batches added on a dev day where **no version has yet been cut** are grouped under a `### YYYY-MM-DD` subheader inside the Added / Changed / Fixed buckets so chronology stays visible before the version is cut.
- If **today already has a cut version section** (e.g., `## [0.4.0] - 2026-05-31`), do NOT duplicate the date under `[Unreleased]`. Instead, the new same-day batch should be cut as a **patch bump** (`v0.4.0 → v0.4.1`). Patch bumps cleanly handle same-day add-ons and concurrent-contributor scenarios (each push gets its own version), and avoid the confusing "two sections with the same date" layout.
- Cross-day work simply waits in `[Unreleased]` under its own date subheader until cut.

## [Unreleased]

_No entries yet — next batch lands here under a `### YYYY-MM-DD` subheader (or, if today already has a cut version, as a patch bump per the convention above)._

## [0.6.0] - 2026-06-02

### Added

- **`DOCUMENTATION.md`** (new top-level reference, ~880 lines) — comprehensive end-to-end walkthrough of using the workspace, from `user-context` onboarding through `/scan` → `/discover` → `/validate-card` → `/scope-mvp` → `/start-build` → `/ship-app`. Each pipeline command gets a consistent treatment: what it does → what you input → what comes out → status meanings → when to stop → why → gotchas. Heavy focus on the build phase (§6, eight subsections) for readers with some technical background but no specific web/mobile/desktop expertise — including §6.5 "Following along when you don't code" with practical signs-of-going-well-vs-badly tables and §6.6 "When Fijara makes more sense" with an honest opt-out framing. §11 "The reviewer-decision model" covers the advise-vs-decide pattern in depth, with the verdict-pattern interpretation table.
- **`/documentation` slash command** (`.claude/commands/documentation.md`) — renders a condensed in-terminal walkthrough (~350 lines) that personalizes against the user's actual current state (existing scans, cards, validation reports, etc.). When the user has real artifacts at a given phase, the in-terminal version uses them as concrete examples rather than placeholders — so `/validate-card` is explained using the user's actual `validation-bench-watch.md`, not a generic stand-in. Closes by pointing to `DOCUMENTATION.md` for the deeper reference.
- **Onboarding-override exception for `/documentation`** in CLAUDE.md §Session continuity Rule A. `/documentation` is the **only** command that bypasses the first-launch onboarding interrupt — forcing onboarding before letting users read about the workspace (and the onboarding workflow itself) would be circular. Every other command still triggers the onboarding flow on the first message of a fresh session when `user-context/INTERESTS.md` is missing.
- **`run_tests.py`** verifies `DOCUMENTATION.md` and `.claude/commands/documentation.md` exist (96 → 98 checks).
- **`README.md` slash-command list and utility-commands table** + **`HELP.md` §2** updated to include `/documentation`.

### Changed

- **CLAUDE.md trimmed** for headroom under the 40 k auto-load threshold while accommodating the new `/documentation` references and onboarding-override exception. Trims were structural compressions that don't lose load-bearing info: the Specialist Personas line moved to "8 specialists" with a parenthetical list instead of 9 explicit names; the Phased plan §3 sub-bullet shortened; the Build-phase skill auto-invocation closing paragraph compressed; the Flask caveat tightened. Final: 39,960 chars.

This is a **minor version bump** (0.5.x → 0.6.0), not a patch — a new top-level reference document + a new slash command + a new behavioral rule (onboarding override) is more than a fix.

## [0.5.1] - 2026-06-02

### Fixed

- **CHANGELOG date typo**: v0.5.0 header was dated `2026-06-01`; corrected to `2026-06-02`.
- **CLAUDE.md trimmed for headroom** (~140 chars under the 40 k auto-load threshold). Compressed the "Invoking custom subagents" intro paragraph by dropping the literal enumeration of the Agent tool's built-in subagent-type enum and the literal list of every custom subagent file — neither is load-bearing (Claude can re-derive both by reading `.claude/agents/`). Final: 39,854 chars.
- **Residual web/mobile-only spots updated for desktop awareness:**
  - `README.md` tagline: "web and mobile products" → "web, mobile, and desktop products".
  - `README.md` "What ships in the box" row: senior-engineer count updated 7 → 8 specialists.
  - `README.md` "Install the required tools" table refactored: **Claude Code CLI extracted into a leading callout** above the table so it gets its own width (the wrapped row was visually unbalanced); the Python row now lists "Flask web apps + PySide6 desktop apps (workspace defaults)".
  - `README.md` senior-engineer personas table: added `senior-desktop-engineer` row; `senior-qa-engineer` row notes pytest-qt offscreen extension; `senior-devops-engineer` row notes PyInstaller + cross-platform CI extension.
  - `README.md` repository layout tree: added `guides/desktop/` and `desktop-apps/` lines.
  - `README.md` "Personal vs. shared" paragraph: `desktop-apps/` added to the list of folders that ship a README.
  - `README.md` `new-product-skeleton.sh` row + `/start-build` slash command row: both reference desktop as a third domain.
  - `CLAUDE.md` Phased plan §1 + §3 and Pipeline-orchestration "Build orchestration" line: extended to web/mobile/desktop; senior-desktop-engineer added to the specialist-personas list; "for desktop-only briefs, project tree + core models first" noted in the build-order defaults.
  - `CONTRIBUTING.md` principle #1: "any web/mobile stack" → "any web/mobile/desktop stack"; build-domain examples now list "Flask, RN/EAS, PySide6/PyInstaller".
  - `.claude/agents/senior-software-engineer.md` "When invoked" line: orientation questions now include desktop.

## [0.5.0] - 2026-06-02

### Added

- **Desktop apps as a peer build domain to web and mobile.** New `desktop-apps/` folder at the top level, parallel to `web-apps/` and `mobile-apps/` (gitignored except for `README.md`); new build-domain guides at `guides/desktop/python-mvp-scaffold.md` and `guides/desktop/packaging-and-distribution.md`; new senior-engineer persona at `.claude/agents/senior-desktop-engineer.md`. Default stack: **Python + PySide6 (Qt for Python) + PyInstaller**, cross-platform-capable with macOS-first MVP target. Stack-flexibility convention extends to desktop the same way it works for web and mobile — defaults are not requirements; the brief can pick C# + Avalonia, Electron, Tauri, Flet, Qt C++, or anything else, and the workspace adapts.
- **Why Python + PySide6 as the default** (not C#, not C++): the maintainer is Python-focused; the web stack is already Python (Flask); the user wants generated code to be easy to read alongside the rest of the workspace's code; Qt produces native-looking apps without per-platform UI rewrites; PySide6 is LGPL-licensed and backed by The Qt Company directly. C# + Avalonia is the documented strong alternative for teams that prefer static typing + .NET; C++ is explicitly skipped due to memory-management overhead and readability cost.
- **Five existing senior personas updated** to know about desktop as a peer domain — `senior-software-engineer` (orchestration now routes web / mobile / desktop / hybrid), `senior-system-design-engineer` (paths reference `desktop-apps/<slug>/`), `senior-qa-engineer` (pytest-qt with `QT_QPA_PLATFORM=offscreen` for CI), `senior-devops-engineer` (PyInstaller packaging + cross-platform CI patterns), and architectural guidance for the new `senior-desktop-engineer` covering UI ↔ core separation, signal/slot composition, packaging, and native integrations.
- **Four slash commands extended for desktop awareness:**
  - `/scope-mvp` — stack picker now has 3 default options (web / mobile / desktop) and lists alternative-stack picks for each domain.
  - `/start-build` — orientation handles `domain: desktop` and `domain: hybrid` variations spanning multiple build domains (web + desktop, mobile + desktop, all three).
  - `/ship-app` — adds `--desktop` and `--all` flags; deploy path for desktop is PyInstaller bundle + sideload (MVP) or code-signed + notarized release (v1 opt-in); post-deploy verification runs the bundled app once.
  - `/preview-product` — for desktop products, launches `python -m <slug>` from the project's venv. (No dummy / fixture mode for desktop — the app itself is the preview.)
- **`scripts/check_system.py`** gains two optional rows: **PySide6** and **PyInstaller** (installable via `pip`). Status reports `(not installed)` as `⚠` rather than `✗` because these are optional unless the user is actively building a desktop product.
- **`scripts/run_tests.py`** verifies the new files exist (`desktop-apps/README.md`, both desktop guides, the new persona, `/ship-app` command, `projects.py`, `check_system.py`) and adds `guides/desktop/` to the frontmatter check.
- **Two product methodology guides extended:** `guides/product/mvp-scoping-methodology.md` §5 brief template + §6.0 stack picker now cover the desktop default and alternatives; `guides/product/build-status-methodology.md` documents the desktop subsystem checklist (project tree + venv, core Qt-free services, UI shell, per-feature widgets, packaging spec, smoke tests with pytest-qt offscreen, dev / build scripts, optional cross-platform CI, optional v1 signing).
- **CLAUDE.md, README.md, HELP.md** all updated for desktop visibility: folder map row, slash-command index, system requirements, stack-flexibility section, intro paragraph.

### Changed

- **CLAUDE.md "Stack flexibility" working-style bullet** tightened to fit under the 40 k auto-load threshold while now covering 3 default stacks instead of 2 (Flask + RN + Python/PySide6).

This is a **minor version bump** (0.4.x → 0.5.0), not a patch — it adds a peer build domain rather than fixing or refining existing capability.

## [0.4.4] - 2026-05-31

### Added

- **`/ship-app <slug>` slash command** — initialize the shipment / release phase for a built product. Distinct from `/start-build` (which brings the product *to* ready-to-deploy state); `/ship-app` runs the release-readiness gate (QA pre-flight via `senior-qa-engineer` + security pre-flight via `senior-security-engineer`), invokes `senior-devops-engineer` to execute the actual deploy (web via `guides/web/flask-deploy-runbook.md`, mobile via `guides/mobile/eas-build-and-update.md` + `rn-app-store-submission.md`), then runs post-deploy verification and updates `BUILD_STATUS.md`. Both pre-flight gates must pass before any deploy; a final "ship now / cancel" user confirmation sits between the gates and the deploy. Args: `<slug>` + optional `--web` / `--mobile` / `--both` scope flag.

### Fixed

- **`/scan` founder-fit leak.** Previously read `CLAUDE.md` as the founder-fit source, which caused a forker without `user-context/INTERESTS.md` to silently inherit the maintainer's domain context (eval engineering, etc.) — producing territories anchored to someone else's strengths. Now mirrors `/discover`'s fallback: check `user-context/INTERESTS.md` → if missing, ask the user for inline context OR fall back to a no-founder-fit "open scan" mode (territories rated on freshness × reachability only). Explicit do-NOT clause warning against pulling the `CLAUDE.md` owner intro into founder-fit. The user's existing scan at `market-research/efl61o1t-053126/scan.md` was generated under the old behavior and reflects the maintainer's context — re-run `/scan` once `INTERESTS.md` is populated for a properly targeted output.
- **CLAUDE.md "Standard build order" line** updated to terminate at "ready-to-deploy state" and route deploy / release to the new `/ship-app` phase (previously, deploy was conflated into the build step itself).

## [0.4.3] - 2026-05-31

### Fixed

- **`scripts/check_system.py` table output switched to markdown format.** The previous ASCII-aligned table forced a wide layout that wrapped awkwardly in Claude Code's TUI (the "Recommended" header got split across two lines as "Recommend|ed"). The new markdown table renders cleanly in the TUI, on GitHub, and in any markdown-aware viewer; raw text in a plain terminal still reads fine because pipe-delimited rows wrap predictably instead of breaking mid-column-header. Status emoji stays uncolored inside cells (some markdown renderers strip ANSI); the colored summary line below the table preserves the visual ✓/⚠/✗ signal.

## [0.4.2] - 2026-05-31

### Added

- **`/system-check` slash command + `scripts/check_system.py` helper** — compare the host machine against this workspace's hardware + tooling requirements. Shows a row-by-row table (required / recommended / your value / status ✓⚠✗) covering OS, CPU architecture, CPU cores, RAM, free disk at workspace, internet connectivity (`api.anthropic.com` DNS probe), Python ≥3.10, Node.js ≥20, required CLI tools (git, gh, pandoc, typst), and optional tools (docker). Stdlib only — no `psutil` or other deps; uses platform-specific commands (`sysctl` on macOS, `/proc/meminfo` on Linux, `wmic` on Windows) for RAM detection with graceful fallback. Read-only (no file writes, no paid API calls, one DNS lookup max). Exit 0 on success or warnings-only; exit 1 on any required-check failure. Backs the `/system-check` slash command, which surfaces a plain-English summary keyed to the result.
- **New "System requirements" section in `README.md`** (under Getting started, before Prerequisites). Documents minimum vs. recommended specs in a table format so anyone considering the workspace can size up fit before cloning. Points at `/system-check` for runtime verification.

### Changed

- **`scripts/delete_project.py` renamed to `scripts/projects.py`** — the script does list + show + delete, not only delete; new name matches the `/projects` slash command. All references updated (slash-command body, scripts/README.md, README.md, HELP.md, CHANGELOG, the script's own docstring).

## [0.4.1] - 2026-05-31

### Added

- **`/projects` slash command + `scripts/projects.py` helper** — manage discovery-cycle projects from the workspace. Lists all projects (keyed by run-id) with a summary of cards/validations/scopings/builds per project; offers to view artifacts or delete; deletion is a multi-step confirmation flow (lists everything that will be deleted → first confirm → final confirmation with strong warning → executes via `projects.py delete <run-id> --force`). A "project" is the full set of artifacts keyed by a run-id: `ideas/<run-id>/`, `ideas/killed/<run-id>/`, `market-research/<run-id>/`, plus for each slug from that run: `web-apps/<slug>/`, `mobile-apps/<slug>/`, and `generated/**/*<slug>*` exports. The helper script can also be invoked directly without the slash command (`python3 scripts/projects.py list|show <run-id>|delete <run-id> --force`) for scripted workflows. Updated `README.md` (utility commands + utility-scripts tables), `HELP.md` (full description), and `CLAUDE.md` (slash command index).
- **Same-day-patch convention added to CHANGELOG preamble + CLAUDE.md CHANGELOG editing rules**: when today already has a cut version section, new same-day changes get a patch bump (v0.4.0 → v0.4.1) rather than a duplicate-dated entry under `[Unreleased]`. Avoids "two sections with the same date" confusion and is friendlier for merges from multiple contributors.
- **Cross-shell safety note (zsh's `NOMATCH`)** added to `CLAUDE.md`'s Search-patterns section. zsh errors at parse time on unmatched globs and `2>/dev/null` can't suppress it, while bash (Linux, Git Bash, WSL) is lenient. Bites survey-style probes against possibly-empty state. Documents two cross-shell-safe alternatives: folder-listing (`ls market-research/`) or Python (`python3 -c "import glob; ..."`). Confirms that our own scripts (`scripts/*.sh` with bash shebangs; `scripts/*.py` with `pathlib`/`glob`) are unaffected — the guidance governs only ad-hoc Bash that Claude generates at runtime.
- **`.claude/commands/discover.md` empty-state probe updated** to use the cross-shell-safe pattern: list `market-research/` first, then drill in with Python. Previous hint used raw globs that error on zsh when no `/scan` has ever been run.

## [0.4.0] - 2026-05-31

### Added
- **Direct-glob-args preference over `for` loops** when scanning run folders — the previous shell-glob guidance recommended `for f in market-research/*/scan.md; do ...` which trips Claude Code's "Contains shell syntax that cannot be statically analyzed" prompt. Replaced with direct glob arguments: `grep -l "status: active" market-research/*/scan.md` (the shell expands the glob into argv before the command runs — no control flow, statically analyzable). Updated in `CLAUDE.md`'s Internet access section and in `/discover`'s inline hint.
- **Retroactive git tags for v0.1.0, v0.2.0, v0.3.0** (`b385f95`, `16e5e14`, `a02b156` respectively) — the CHANGELOG documented these versions but no git tags existed, so the compare links at the bottom of the file 404'd on GitHub. All four tags (v0.1.0–v0.4.0) now exist locally and on origin.
- **GitHub repo About description** set via `gh repo edit` — surfaces what the repo is on the repo homepage, in search results, and in social previews.
- **Commit trailer policy** in `CLAUDE.md` — before every `git commit`, Claude asks via `AskUserQuestion` whether to include the `Co-Authored-By: Claude` trailer. Overrides Claude Code's harness default (which always adds it). The trailer is permanent and surfaces Claude as a co-author in the GitHub contributors graph; the user should make that visibility choice per commit, not silently inherit it. Per-commit ask, not per-push (trailer is fixed at commit time). Session-pin options ("always include this session" / "drop for this session") supported.
- **Shell-glob preference over `find -exec`** for scanning run folders — new subsection in `CLAUDE.md`'s Internet access policy, plus inline note in `/discover`. Claude Code's permission system treats `find -exec` as a higher-permission operation and prompts interactively even when `Bash(find:*)` is allowlisted. (Initial implementation used `for` loops; corrected to direct-glob-args this version — see Added entry above.)
- **Core-file edit confirmation rule** in `CLAUDE.md` — Claude must surface the proposed change and ask the user to confirm before any Write / Edit / NotebookEdit / `git mv` / file deletion on a core repo file (anything not in a gitignored personal-data path). Applies to everyone, including the owner. For non-owners, this is on top of `/acknowledge-contributing`, not a replacement. Batched: one ask per request, not per-file. Exempt: changes to gitignored paths (the user is operating on their own files). New "Core-file edit confirmation rule" section sits just above the existing "CHANGELOG editing rules" section.
- **Run-folder convention for `ideas/` and `market-research/`** — every `/discover` cycle creates a `<8-alpha>-<MMDDYY>` folder; cards live in `ideas/<run-id>/`; triage + validations + scoping reports for those cards share `market-research/<run-id>/`. Killed cards preserve the link at `ideas/killed/<run-id>/<slug>.md`. `/scan` and `/trend-check` each create their own independent run folder. Folder name format: `<8-lowercase-alphanumeric>-<MMDDYY>` (e.g., `csi48s2t-053126`).
- `scripts/gen_run_id.py` — generates `<8-lowercase-alphanumeric>-<MMDDYY>` run-ids (CLI + importable; `from gen_run_id import generate_run_id`).
- `user-context/IDEAS.md` (third optional personal file) with `IDEAS.md.example` template — seed-ideas backlog that `/discover` weights toward. Distinct from `ideas/` at the repo root (which holds *validated* idea cards from formal discovery cycles); this file is the user's mental staging area.
- **First-launch onboarding flow** with strict trigger: every fresh session where `user-context/INTERESTS.md` is missing prompts the user via `AskUserQuestion` regardless of first message. The recommended path uses Claude Code's `TaskCreate` visual checklist to collect interests and seed ideas conversationally, writing properly-formatted files.
- **`/run-tests` slash command + `scripts/run_tests.py`** — repo health / smoke test suite. 7 categories (required tools, repo structure, frontmatter, cross-references, pipeline lint, script smoke tests, documentation consistency). Green ✓ / yellow ⚠ / red ✗ output. Includes maintainer email for bug reports.
- **CHANGELOG editing rules** (new CLAUDE.md section): always ask before adding; never for personal-data changes; never when the user isn't the owner.
- **Welcome announcement** in `.claude/settings.json` now wraps the message in a unicode box-drawing border so it stands out as a framed panel inside Claude Code's TUI.
- `/setup` slash command — pre-flight verification of all required tools, git identity, GitHub auth, submodule init, and symlink resolution. Pure verification (never modifies anything). Surfaces a structured punch list.
- `/status` slash command — complete pipeline-state snapshot deeper than `/help`. Reads all active scans, cards, briefs, design phases, trend reports, and recent generated docs. Read-only.
- `CHANGELOG.md` (this file) — track meaningful changes over time.
- `SECURITY.md` — responsible disclosure path for any security concerns.
- Custom typst styling overlay (`.claude/skills/doc-export/style.typ`) — white background, light navy `#1e3a8a` accent on headings, Charter body + Helvetica Neue headings (macOS native, with Liberation/DejaVu fallbacks for Linux), Menlo monospace, justified text with comfortable leading, slate borders on tables, slate-tinted background on code blocks. Injected via pandoc's `--include-in-header` so all pandoc-typst helpers (horizontalrule, terms.item, etc.) are inherited. Font fallback chain produces non-fatal warnings on each platform (unavailable fonts are skipped); the `doc-export` skill filters those warnings out of user-facing output.
- `doc-export` skill now always asks the user "PDF or DOCX?" when format is ambiguous (instead of silently defaulting to PDF).
- **`scripts/` folder with 5 Python + 6 Shell utility scripts.** Auxiliary tools that complement (do not replace) the slash commands:
  - **Python:** `lint_pipeline.py` (validate pipeline state consistency), `new_idea_card.py` (interactive idea-card creator for one-off captures), `check_links.py` (markdown link + @path reference checker, optional external-URL HEAD check), `changelog_helper.py` (auto-extract commits since last tag, format as CHANGELOG stub), `report_summarizer.py` (pretty-print summaries of scan/validation/scoping/trend reports).
  - **Shell:** `preflight.sh` (dependency + repo-state verification, shell version of `/setup`), `setup-deps.sh` (install all required tools, idempotent, detects macOS vs. Linux), `update-agent-skills.sh` (pull agent-skills upstream and commit new submodule SHA), `backup-personal-data.sh` (tar gitignored folders, optional `--encrypt`), `new-product-skeleton.sh` (scaffold a new product folder), `clean-killed-ideas.sh` (archive killed ideas older than N days).
  - All scripts: executable, color-aware, runnable from the repo root. Documented in `scripts/README.md` plus the index sections of `README.md` and `HELP.md`. Side effect on GitHub: language bar now shows Python and Shell alongside the existing Typst, reflecting the actual code mix in the repo.

### Changed
- All 5 pipeline slash commands (`/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/trend-check`) and 5 methodology guides updated to use the new run-folder paths.
- Filename conventions inside run folders: generic (`scan.md`, `triage.md`, `trends.md`) when one-of-a-kind; slug-suffixed (`validation-<slug>.md`, `scoping-<slug>.md`) when multiple coexist; slug-as-filename (`<slug>.md`) for cards.
- `scripts/lint_pipeline.py`, `check_slug.py`, `new_idea_card.py`, `report_summarizer.py` — now walk nested run folders.
- `user-context/README.md` describes all three personal files (INTERESTS, POLICY, IDEAS) side by side; onboarding flow is the recommended path.
- README "Personalizing the workspace" section rewritten to explain the strict onboarding trigger.
- `README.md` slash commands section reorganized: split into "Pipeline phase commands" (with `/preview-product` added) and a new "Utility commands" subsection (`/menu`, `/status`, `/setup`, `/run-tests`, `/acknowledge-contributing`). Onboarding section rewritten with stronger "please don't skip" framing and detailed why-it-matters reasoning.
- `README.md` utility-scripts table now lists `run_tests.py` and `gen_run_id.py` (previously missing from the documented inventory).
- `CLAUDE.md` trimmed from ~42.9k to ~38.5k chars by condensing the Core-file confirmation rule, BUILD_STATUS + build orchestration sections, and the verbose slash-commands index. Full per-command descriptions and persona detail still live in `HELP.md`, `guides/product/build-status-methodology.md`, and the `.claude/agents/senior-*.md` files — nothing lost, just relocated.

### Fixed
- `scripts/check_links.py` now strips inline-code spans (text between single backticks) before matching markdown links. Fixes a false positive where documented `[text](path)` examples inside inline code were being treated as real broken links.
- `scripts/lint_pipeline.py` validation-report section check now accepts both heading-style (`## Verdict`) and bold-label-style (`**Verdict:**`) formats. The bold-label style is what reports use when integrating three reviewers (each reviewer's section uses bold labels under a numbered subheading); the previous check only recognized headings and flagged false positives.
- `scripts/run_tests.py` documentation-consistency check now excludes generic placeholders (`/command`, `/cmd`, `/name`, `/foo`, `/bar`) that appear in documentation as literal example tokens, not actual commands.
- **All 23 agent-skills skills now symlinked into `.claude/skills/`** so Claude Code auto-discovers them. Previously only the 3 personas were wired in; the skills sat in the submodule but were not picked up by Claude Code's skill discovery (which only scans `.claude/skills/`). With the symlinks in place, skills like `frontend-ui-engineering`, `idea-refine`, `interview-me`, `spec-driven-development`, `test-driven-development`, `code-review-and-quality`, `security-and-hardening`, etc. are now auto-invoked when their trigger conditions match.
- **Build-phase skill auto-invocation policy added** to `CLAUDE.md` — 15 skills are now applied *proactively by Claude during build phases* without the user having to ask (incremental-implementation, TDD, code-review-and-quality, code-simplification, security-and-hardening, performance-optimization, debugging-and-error-recovery, frontend-ui-engineering, api-and-interface-design, documentation-and-adrs, git-workflow-and-versioning, browser-testing-with-devtools, ci-cd-and-automation, shipping-and-launch, spec-driven-development). Skills like `idea-refine`, `interview-me`, `planning-and-task-breakdown`, `doubt-driven-development`, etc. remain situational. The Flask and RN scaffold guides got dedicated "Skills Claude applies automatically during the build" sections at §6.
- **Slash command `/help` renamed to `/menu`** because Claude Code has a built-in `/help` command that shadows custom ones. All cross-references in `CLAUDE.md`, `README.md`, `HELP.md`, and the other slash commands updated. The built-in `/help` still works for Claude Code's own help dialog; our project command is `/menu`.
- **`.claude/skills/` symlink layout fixed.** The previous round used directory symlinks (the whole skill folder symlinked to the agent-skills counterpart). Directory symlinks render awkwardly in editors and on GitHub (shown as text containing the target path rather than navigable folders). Replaced with the same pattern used for the persona symlinks: each skill is now a real directory (`.claude/skills/<name>/`) containing a `SKILL.md` **file symlink** to `../../../external/agent-skills/skills/<name>/SKILL.md`. Claude Code's auto-discovery works the same way; the rendering is clean.

- **Symlinks replaced with file copies for the 3 personas and 23 skills.** Even after the file-symlink fix above, GitHub's web UI still rendered file symlinks as text containing the target path rather than the resolved content — clicking them on GitHub didn't show the file. Switched to file-level copies: `.claude/agents/<persona>.md` and `.claude/skills/<name>/` are now regular files / directories with copied content from the agent-skills submodule. Trade-off: upstream updates no longer propagate automatically, but `scripts/update-agent-skills.sh` was updated to pull the submodule AND re-copy the personas + skills in a single command — so the user-facing sync experience is unchanged (still one command). Full attribution to **Addy Osmani** ([`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills), MIT-licensed, Copyright 2025) added in `.claude/agents/README.md`, `.claude/skills/README.md`, the top-level `README.md` (both the "what ships in the box" table and the License section), and the workspace's clone-and-update instructions.

- **Stale "symlink" references purged from current-tense docs.** After the symlink → copy migration, scattered docs still described the integration in symlink terms. Updated CLAUDE.md (4 spots), HELP.md (3 spots), scripts/preflight.sh (the check logic + label), scripts/README.md, .claude/commands/scope-mvp.md, .claude/commands/setup.md (description + check + summary), guides/web/flask-mvp-scaffold.md, and guides/mobile/react-native-mvp-scaffold.md to say "file copies / file-copied / vendored" with attribution to Addy Osmani. Also removed the stale "Setup prerequisite: code-reviewer not yet in .claude/agents/" note in `guides/product/mvp-scoping-methodology.md` (the prerequisite is met). The three remaining "symlink" mentions — in `.claude/agents/README.md`, `.claude/skills/README.md`, and `scripts/update-agent-skills.sh` — are intentional "Why copies, not symlinks?" explanations preserving the design rationale.
- **`scripts/preflight.sh` check logic updated** from "is it a symlink that resolves?" to "is it a regular file with content?" — matches the new copy-based reality. Failure message now points users at `bash scripts/update-agent-skills.sh` (which re-copies) instead of the old "re-create symlinks" instruction.
- **Welcome banner at session start** — added a `companyAnnouncements` entry to `.claude/settings.json` that displays at every Claude Code session launch in the repo: "Welcome to discovery-to-ship-multi-agents — a product-portfolio pipeline orchestrated by Claude Code, by Abiodun Anifowose. Type /menu for the command map, /status for current pipeline state, or /discover to begin a new product cycle." Confirms you're in the right workspace and surfaces the three most common starting commands. Forkers can customize the message by editing that array.
- **Build-phase UX improvements — narrated orchestration + BUILD_STATUS.md + `/preview-product`:**
  - **Narrated handoffs.** `senior-software-engineer` persona updated with explicit "speak the team's handoffs out loud" pattern: before invoking a specialist, announce *who* is doing *what* next, *from* which input artifacts, *toward* which expected output, with a rough time estimate. After completion, announce what landed + artifact + decisions. Same pattern at every handoff between specialists. The goal: the user reads along and feels the senior engineering team actively working for them, not a black box.
  - **`BUILD_STATUS.md` per product** — a dynamic, product-specific checklist of build subsystems. **Generated dynamically** (not from a static template) by walking the brief's must-haves (auth/uploads/jobs/etc. only included if scoped), the chosen stack (Flask vs. Next.js vs. ...), and the standard build order. Owned by `senior-software-engineer`; specialists report completion, senior-software-engineer writes/updates. New methodology guide at `guides/product/build-status-methodology.md` covers generation, format, update protocol, and how `/status` surfaces it.
  - **`/preview-product <slug> [page-name]` slash command** — preview a product's UI in the browser. Auto-detects which mode is possible: **real preview** (the running app at `localhost:5000/<page>`, requires dev server up + dependencies wired) or **dummy preview** (Jinja template + fixture data via the `web-preview` skill, always possible if the template exists). Always tells the user which mode they got and why. If dummy mode, briefly mentions what would unblock real preview. Web only — mobile previews go through Expo Go / EAS preview builds. The `web-preview` skill itself updated with a "Dummy mode vs. real mode" section explaining its role within `/preview-product`.
- **Slug-uniqueness rule and tooling.** Slugs must be unique across `ideas/`, `ideas/killed/`, `web-apps/`, and `mobile-apps/`. New script `scripts/check_slug.py` enforces this (exit 0 = available; exit 1 = taken with details). Used by `new_idea_card.py` (imports `is_available()`) and `lint_pipeline.py` (new `slug.collision` error rule). CLAUDE.md has a new "Slug uniqueness" section codifying the rule.
- **8 senior-engineer personas added** at `.claude/agents/senior-*.md` to orchestrate the build phase:
  - `senior-software-engineer` — generalist orchestrator; asks orientation questions, routes to specialists, sequences subsystems.
  - `senior-system-design-engineer` — system shape, data flow, cross-cutting concerns, decisions deferred. Produces SYSTEM_DESIGN.md.
  - `senior-database-engineer` — schema, indexes, migrations. Produces SCHEMA.md.
  - `senior-backend-engineer` — ORM models, API contracts, endpoint implementation, business logic. Produces API_CONTRACT.md.
  - `senior-frontend-engineer` — UI implementation (Jinja+JS or RN), design-token integration, accessibility.
  - `senior-qa-engineer` — test coverage audits, integration tests at the seam, release-readiness.
  - `senior-devops-engineer` — deploy, CI/CD, observability, incident response.
  - `senior-security-engineer` — threat modeling, secure coding, auth design, infra hardening.
  Each persona's body lists which agent-skills it commonly invokes (TDD, code-review-and-quality, security-and-hardening, performance-optimization, etc.), so the senior personas compose with the agent-skills.
- **`/start-build <slug>` slash command added.** Entry point for the build phase. Invokes `senior-software-engineer`, which asks the three orientation questions: (1) for hybrid briefs, web/API first (recommended) vs. mobile first; (2) MVP scope (recommended) vs. fully-featured; (3) which subsystem to start with (database design recommended), with the full ordered list shown for override. After answers, proposes the right specialist persona for the first subsystem and the specific first task. The build then proceeds subsystem-by-subsystem, with `senior-software-engineer` routing at each handoff.
- **CLAUDE.md "Build orchestration" subsection** added under Pipeline orchestration & checkpoints. Names the personas, the standard build order (database → project tree → models → API contract → API implementation → auth → background jobs → frontend → tests → deploy → iterate), and clarifies that senior personas are roles and agent-skills are workflows the roles execute.
- README and HELP updated with senior-engineer persona descriptions, the new `/start-build` command, and an explanation of how the build phase flows conversationally through the orchestrator + specialists.

## [0.3.0] — 2026-05-29

### Added
- `/acknowledge-contributing` slash command and the contributor-acknowledgment workflow. Required for non-owner users before editing tracked files; owner exempt via `git config user.email` check. Creates a gitignored `.claude-acknowledged` marker per clone. Documented honestly as a convention, not a technical lock.
- Owner / acknowledgment section in `CLAUDE.md` near the top.

### Changed
- `CONTRIBUTING.md` "Before you start" restructured into three explicit steps: use Claude Code to edit, run `/acknowledge-contributing`, email first for non-trivial.
- `README.md` How to contribute reordered to put the Claude-Code + acknowledgment steps first.

## [0.2.0] — 2026-05-29

### Added
- Pre-build decisions checkpoint in `/scope-mvp` — after the brief reaches `green-lit-to-build`, Claude asks (a) design path: generic-but-unique vs. engage a human designer, and (b) build support: I'll follow along vs. Fijara referral. Both picks recorded in the brief's frontmatter.
- Fijara-referral behavioral rule in `CLAUDE.md` Working style: gently surface Fijara if a "I'll follow" user later signals real struggle (repeated basic questions, expressed frustration, blocked on setup). Never pushy.
- Feedback section in `README.md` directing users to email `aanifowose111@gmail.com` with subject `[discovery-to-ship feedback]`.
- `CONTRIBUTING.md` — comprehensive guide covering project philosophy, what to change vs. not change, the required-updates matrix per change type, style conventions, local testing checklist, PR process, brief code of conduct.
- `HELP.md` scenario 1.5 expanded with the new pre-build decisions description.

### Changed
- payment-forms card moved to `ideas/killed/` with kill reason in the frontmatter (verification-test card that the viability reviewer killed with HIGH confidence; no need to continue the validation cycle on it).

## [0.1.0] — 2026-05-29

### Added
- Initial scaffolding for the workspace pushed to GitHub at https://github.com/aanifowose111/discovery-to-ship-multi-agents
- Pipeline slash commands: `/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/research-design`, `/draft-design-brief`, `/trend-check`, `/help`.
- Reviewer and worker subagents: `product-viability-reviewer`, `product-competition-reviewer`, `market-segment-reviewer`, `product-scope-reviewer`, `ui-ux-researcher`, `design-brief-reviewer`, `design-fidelity-reviewer`.
- Agent-skills personas (`code-reviewer`, `security-auditor`, `test-engineer`) symlinked from the `external/agent-skills/` submodule.
- Helper skills: `doc-export` (markdown → PDF/DOCX via pandoc + typst), `web-preview` (Jinja render in Chrome with fixture data).
- Methodology + runbook guides across six domains: product (discovery / validation / MVP scoping), market (scan / trend monitoring), funding (strategy), web (Flask scaffold / deploy / DO Spaces / auth), mobile (RN scaffold / EAS / app store submission), UI/UX (design research / brief / handoff).
- Personal-data folders gitignored: `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `generated/`. Each with a tracked README explaining the convention and a `.gitkeep` placeholder.
- Top-level files: `README.md`, `CLAUDE.md`, `HELP.md`, `LICENSE` (MIT), `.gitignore`.
- Stack-flexibility framing: workspace defaults are dockerized Flask + RN, but the methodologies are stack-agnostic and `/scope-mvp` asks the user to confirm the stack before drafting.
- Internet access policy: `WebFetch` and `WebSearch` pre-approved in `.claude/settings.json`; permission only requested for non-HTTPS, suspicious, paid, or user-private URLs.

[Unreleased]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.4.4...v0.5.0
[0.4.4]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.4.3...v0.4.4
[0.4.3]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/releases/tag/v0.1.0
