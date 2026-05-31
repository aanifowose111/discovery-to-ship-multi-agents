# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

This project does not yet follow strict semantic versioning. Pre-1.0, breaking changes happen as the methodology evolves. Once the system stabilizes through use, this will move to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Mercor referral note in `README.md` simplified — removed both the non-referral mercor.com fallback line *and* the parenthetical aside (per maintainer's preference; the referral link stands on its own).

### Fixed
- `scripts/check_links.py` now strips inline-code spans (text between single backticks) before matching markdown links. Fixes a false positive where documented `[text](path)` examples inside inline code were being treated as real broken links.
- `scripts/lint_pipeline.py` validation-report section check now accepts both heading-style (`## Verdict`) and bold-label-style (`**Verdict:**`) formats. The bold-label style is what reports use when integrating three reviewers (each reviewer's section uses bold labels under a numbered subheading); the previous check only recognized headings and flagged false positives.
- `scripts/run_tests.py` documentation-consistency check now excludes generic placeholders (`/command`, `/cmd`, `/name`, `/foo`, `/bar`) that appear in documentation as literal example tokens, not actual commands.
- **All 23 agent-skills skills now symlinked into `.claude/skills/`** so Claude Code auto-discovers them. Previously only the 3 personas were wired in; the skills sat in the submodule but were not picked up by Claude Code's skill discovery (which only scans `.claude/skills/`). With the symlinks in place, skills like `frontend-ui-engineering`, `idea-refine`, `interview-me`, `spec-driven-development`, `test-driven-development`, `code-review-and-quality`, `security-and-hardening`, etc. are now auto-invoked when their trigger conditions match.
- **Build-phase skill auto-invocation policy added** to `CLAUDE.md` — 15 skills are now applied *proactively by Claude during build phases* without the user having to ask (incremental-implementation, TDD, code-review-and-quality, code-simplification, security-and-hardening, performance-optimization, debugging-and-error-recovery, frontend-ui-engineering, api-and-interface-design, documentation-and-adrs, git-workflow-and-versioning, browser-testing-with-devtools, ci-cd-and-automation, shipping-and-launch, spec-driven-development). Skills like `idea-refine`, `interview-me`, `planning-and-task-breakdown`, `doubt-driven-development`, etc. remain situational. The Flask and RN scaffold guides got dedicated "Skills Claude applies automatically during the build" sections at §6.
- **Slash command `/help` renamed to `/menu`** because Claude Code has a built-in `/help` command that shadows custom ones. All cross-references in `CLAUDE.md`, `README.md`, `HELP.md`, and the other slash commands updated. The built-in `/help` still works for Claude Code's own help dialog; our project command is `/menu`.
- **`.claude/skills/` symlink layout fixed.** The previous round used directory symlinks (the whole skill folder symlinked to the agent-skills counterpart). Directory symlinks render awkwardly in editors and on GitHub (shown as text containing the target path rather than navigable folders). Replaced with the same pattern used for the persona symlinks: each skill is now a real directory (`.claude/skills/<name>/`) containing a `SKILL.md` **file symlink** to `../../../external/agent-skills/skills/<name>/SKILL.md`. Claude Code's auto-discovery works the same way; the rendering is clean.

- **Symlinks replaced with file copies for the 3 personas and 23 skills.** Even after the file-symlink fix above, GitHub's web UI still rendered file symlinks as text containing the target path rather than the resolved content — clicking them on GitHub didn't show the file. Switched to file-level copies: `.claude/agents/<persona>.md` and `.claude/skills/<name>/` are now regular files / directories with copied content from the agent-skills submodule. Trade-off: upstream updates no longer propagate automatically, but `scripts/update-agent-skills.sh` was updated to pull the submodule AND re-copy the personas + skills in a single command — so the user-facing sync experience is unchanged (still one command). Full attribution to **Addy Osmani** ([`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills), MIT-licensed, Copyright 2025) added in `.claude/agents/README.md`, `.claude/skills/README.md`, the top-level `README.md` (both the "what ships in the box" table and the License section), and the workspace's clone-and-update instructions.

- **Mercor referral wording in `README.md`:** "the pay is fair" → "the pay is good".
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
- Mercor referral link in `README.md` with a personal note from the maintainer (Abiodun's AI Chemistry Evaluation work at Mercor).

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

[Unreleased]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/aanifowose111/discovery-to-ship-multi-agents/releases/tag/v0.1.0
