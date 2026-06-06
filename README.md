# Discovery-to-Ship Multi-Agents

<p align="center">
  <img src="https://scriptvil-cdn.nyc3.cdn.digitaloceanspaces.com/agents/discovery-to-ship-multi-agents.png" alt="Discovery-to-ship pipeline: six stages — discovery, validation, MVP scoping, design, build, ship — with reviewer subagents and senior-engineer personas collaborating across each phase" width="100%">
</p>

A Claude Code–orchestrated portfolio pipeline for discovering, validating, scoping, designing, and shipping distinctive web, mobile, and desktop products. Built around opinionated methodology guides, narrow-lens reviewer subagents, helper skills, and pipeline slash commands.

The name reflects what's in the box: many specialized agents (worker, reviewer, and code-review personas), composed into one pipeline that takes a product from **discovery** all the way through **ship**.

This repo is the *scaffolding*. Your products (ideas, market research, builds) live in the same workspace but are gitignored — they stay on your disk, never enter git. The shared part is the workflow itself: how to think about discovery, how to validate, how to scope, how to design without producing generic-looking output, and (if you use the workspace defaults) how to build dockerized Flask backends, React Native frontends, and PySide6 desktop apps in a repeatable way.

## Stack flexibility — this is important

This workspace ships with **opinionated defaults**:

- **Web:** dockerized Flask (Python) + Jinja templates + vanilla JavaScript.
- **Mobile:** React Native with Expo + TypeScript, paired with the Flask backend.
- **Desktop:** Python + PySide6 (Qt for Python) + PyInstaller. Cross-platform-capable; MVP-default is macOS-first.

These are the **maintainer's** stack choices, not requirements baked into the workflow. The methodology guides (discovery, validation, scoping, design, market research, funding) are **stack-agnostic** — they work whether you ship in Flask, Next.js, Django, Rails, Phoenix, Go, Java/Spring, Swift native, Kotlin native, Flutter, C# + Avalonia, Electron, Tauri, or anything else.

**Before any build or design work, Claude will ask you what stack you want.** The MVP brief records the choice. From there:

- **If you pick the workspace defaults**, the existing build-domain guides (`guides/web/flask-*`, `guides/mobile/react-native-*`, `guides/desktop/python-*`) apply directly.
- **If you pick something else**, the build-domain guides do not apply as-is. Claude will work from first principles plus the stack-agnostic skills in [agent-skills](https://github.com/aanifowose111/agent-skills). You can either build without a stack-specific scaffold guide, or contribute one for your chosen stack (e.g., `guides/web/nextjs-mvp-scaffold.md`, `guides/desktop/avalonia-mvp-scaffold.md`) — PRs welcome.

If you forked this workspace and want different defaults for *your* fork, edit `CLAUDE.md` (the stack-preference bullet under Working style) and `guides/product/mvp-scoping-methodology.md` §6.0. The methodology guides themselves don't need changing — they're already stack-agnostic.

---

## What this is for

You are a solo or small-team founder building multiple products over time, and you want:

- A repeatable process for going from "I have an idea" to "this is a shippable v1" without re-deciding the same questions every time.
- Reviewer assistants that catch the silent failures (saturated markets, undifferentiated designs, scope creep, security gaps) before they cost a build cycle.
- A clear separation between scaffolding (shared, committable) and your actual product work (personal, never committed).
- A design phase that produces *distinctive*, non-generic-looking products — by engaging a human designer for the v1, not by chaining AI tools.

If that matches what you're trying to do, this repo is a head start. If you want something more turnkey, this isn't it — the assumption here is that you'll read the methodologies, push back on them where they don't fit, and evolve them over time.

---

## What ships in the box

| | What | Where |
|---|---|---|
| **Pipeline slash commands** | `/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/research-design`, `/draft-design-brief`, `/start-build`, `/ship-app`, `/preview-product`, `/trend-check`, `/menu`, `/documentation`, `/setup`, `/status`, `/run-tests`, `/system-check`, `/projects`, `/log`, `/acknowledge-contributing` | `.claude/commands/` |
| **Reviewer assistants** | Product viability / competition / market-segment / scope reviewers, design-brief and design-fidelity reviewers, UI/UX researcher | `.claude/agents/` |
| **Senior-engineer personas** | `senior-software-engineer` (orchestrator) + 8 specialists: system-design, database, backend, frontend, **desktop**, QA, devops, security. Each plays a senior-IC role during the build phase. | `.claude/agents/senior-*.md` |
| **Agent-skills personas** | `code-reviewer`, `security-auditor`, `test-engineer` — file copies from [`aanifowose111/agent-skills`](https://github.com/aanifowose111/agent-skills) (fork), originally authored by **Addy Osmani** at [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills), MIT-licensed. | Vendored into `.claude/agents/`; re-sync via `scripts/update-agent-skills.sh`. |
| **Agent-skills skills** (23) | api-and-interface-design, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine, incremental-implementation, interview-me, performance-optimization, planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development, spec-driven-development, test-driven-development, using-agent-skills — same upstream credit. | Vendored into `.claude/skills/`; re-sync via `scripts/update-agent-skills.sh`. |
| **Helper skills** | `doc-export` (markdown → PDF/DOCX), `web-preview` (render Jinja in Chrome) | `.claude/skills/` |
| **Methodology guides** | Product discovery / validation / MVP scoping; market scan + trend monitoring; funding strategy; Flask scaffold + deploy + storage + auth patterns; React Native scaffold + EAS + store submission; PySide6 desktop scaffold + packaging & distribution; UI/UX research + brief + handoff | `guides/` |
| **Project-wide context** | The Claude-facing entry point (auto-loaded by Claude Code) | `CLAUDE.md` |

See `CLAUDE.md` for the full inventory and how the pieces fit together.

---

## Getting started

### System requirements

This workspace runs on top of Claude Code, plus a handful of supporting tools. **Minimum** specs get you through discovery + validation + MVP scoping; **recommended** specs are what you want once you start building real products (Docker for Flask, Metro bundler for React Native, PySide6 + PyInstaller for desktop, multiple browser tabs).

| Component | Minimum | Recommended |
|---|---|---|
| **OS** | macOS 12+, Linux (most distros from 2022+), Windows 10/11 + WSL2 | macOS 13+ or recent Ubuntu / Fedora |
| **CPU** | 4 cores (x86_64 or arm64); Intel 8th gen / AMD Ryzen 2000+ / any Apple Silicon | 8+ cores; Apple Silicon (M1+) preferred on macOS |
| **RAM** | 8 GB | 16 GB+ |
| **Free disk** | 10 GB | 25 GB+ (for Docker images, node_modules, multiple products) |
| **Internet** | Required (Claude Code API, web research, package downloads) | Stable broadband |
| **CLI tools** | `git`, `python3` ≥3.10, `node` ≥20, `pandoc`, `typst`, `gh` | + `docker` for Flask web apps; + `PySide6` and `pyinstaller` (pip) for desktop apps |

**To compare your machine against this table:** run `/system-check` inside Claude Code, or `python3 scripts/check_system.py` from any terminal. The script shows a row-by-row comparison with ✓/⚠/✗ status and uses Python stdlib only (no extra installs).

### Prerequisites

- **macOS, Linux, or WSL.** Most of the runbooks assume macOS for the developer machine; production targets are Linux (DigitalOcean droplet or App Platform).
- **Claude Code** — this whole workspace is designed to be driven from inside Claude Code, which requires a Claude account.
  - **New to Claude?** Use this Claude Max signup link from the maintainer: **<https://claude.ai/referral/4tieocI5Xw>** (3 lifetime passes available, first come first served — once exhausted, sign up normally at [claude.ai](https://claude.ai)).
  - **Install the CLI:** [docs.claude.com/en/docs/claude-code/installation](https://docs.claude.com/en/docs/claude-code/installation).
- **Git** (any modern version).
- **Python 3.11+** if you will build any web apps.
- **Node.js 20+** if you will build any mobile apps.

For PDF / DOCX export from markdown (the `doc-export` skill):

```bash
brew install pandoc           # required, all formats
brew install typst            # recommended PDF engine (modern, lightweight)
# Or alternatively, if typst doesn't render something correctly:
brew install tectonic         # LaTeX-based, larger but mature
```

> Note: this repo previously documented `wkhtmltopdf` as the PDF engine; Homebrew removed it after the upstream project was archived in 2023. Use typst or tectonic instead.

### Step-by-step setup (for people new to git or this workspace)

If you are comfortable with terminals and git, jump to the short version at the end of this section. Otherwise, go through the steps in order.

#### 1. Open a terminal

- **macOS:** open the *Terminal* app (or *iTerm* if you have it). It's in `Applications → Utilities`, or hit Cmd-Space and type "Terminal."
- **Linux:** any shell — Gnome Terminal, Konsole, Alacritty, etc.
- **Windows:** install [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) and run all commands in an Ubuntu shell inside WSL. The workspace assumes a Unix-like environment.

You should see a prompt that looks something like `~ $` or `~ %`.

#### 2. Install the required tools

For everything to work, you need:

**Claude Code CLI** is the agent runner — it's what reads the workspace, drives the slash commands, and writes the files. Install it from the [Claude Code installation docs](https://docs.claude.com/en/docs/claude-code/installation). It requires a Claude account: use [this Claude Max signup link](https://claude.ai/referral/4tieocI5Xw) (3 lifetime passes from the maintainer) or sign up directly at [claude.ai](https://claude.ai).

Then, the rest:

| Tool | Purpose | Install (macOS) | Install (Ubuntu / WSL) |
|---|---|---|---|
| **git** | Version control | comes with Xcode CLI tools (`xcode-select --install`) | `sudo apt update && sudo apt install git` |
| **Homebrew** (macOS only) | Package manager for the rest | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` | n/a (you have `apt`) |
| **GitHub CLI** (`gh`) | Auth with GitHub from the terminal | `brew install gh` | `sudo apt install gh` |
| **pandoc** | Markdown → PDF/DOCX (for `doc-export` skill) | `brew install pandoc` | `sudo apt install pandoc` |
| **typst** | Modern PDF engine for pandoc | `brew install typst` | see [github.com/typst/typst](https://github.com/typst/typst) |
| **Python 3.11+** | For Flask web apps + PySide6 desktop apps (workspace defaults) | `brew install python@3.12` | `sudo apt install python3 python3-pip` |
| **Node.js 20+** | For React Native (workspace default) | `brew install node@20` | `curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash -; sudo apt install nodejs` |

After each install, verify with `<tool> --version`. For example: `git --version`, `gh --version`, `pandoc --version`, `typst --version`, `claude --version`.

#### 3. Authenticate GitHub in the terminal

Even though GitHub repos can be cloned anonymously over HTTPS, you'll need to be authenticated to push your own changes. The GitHub CLI handles this in one interactive flow:

```bash
gh auth login
```

It will ask you a few questions:

1. **Which account?** Choose `GitHub.com` (unless you use GitHub Enterprise).
2. **Protocol?** Choose `HTTPS` (simpler than SSH for new users).
3. **Authenticate via?** Choose `Login with a web browser`. It will print a one-time code (e.g., `1234-ABCD`) and offer to open the browser. Press Enter, paste the code on the GitHub page when prompted, and approve.
4. **Done.** You'll see something like:

```
✓ Authentication complete.
✓ Configured git protocol
✓ Logged in as <your-github-username>
```

To verify any time later:

```bash
gh auth status
```

Expected output (the welcome message is the success signal):

```
github.com
  ✓ Logged in to github.com account <your-github-username>
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: gho_************
```

If you see `Logged in to github.com account ...`, you're good — `git push`, `gh pr create`, etc. will work without prompting for credentials.

#### 4. Clone the repo

```bash
git clone https://github.com/aanifowose111/discovery-to-ship-multi-agents.git
cd discovery-to-ship-multi-agents
```

That's all you need to start using the workspace. The three agent-skills personas (`code-reviewer`, `security-auditor`, `test-engineer`) and all 23 agent-skills are **already file-copied** into `.claude/agents/` and `.claude/skills/`, so Claude Code auto-discovers them immediately on first `claude` launch.

**Optional — initialize the agent-skills submodule** if you want to be able to pull future upstream updates via `bash scripts/update-agent-skills.sh`:

```bash
git submodule update --init --recursive
```

(Or you can clone-and-init in one step with `git clone --recurse-submodules https://github.com/aanifowose111/discovery-to-ship-multi-agents.git`.)

Without the submodule initialized, the workspace works fine for day-to-day use; you just won't be able to sync agent-skills upstream changes until you initialize it.

#### 5. Open Claude Code in the repo

```bash
claude
```

Claude Code will detect `CLAUDE.md` and `MEMORY.md` and auto-load them. You'll be at the Claude Code prompt, ready to type commands.

#### 6. Run your first command

If you don't have any specific idea in mind yet, just try:

```
/discover
```

By itself. No arguments, no idea details. Claude will brainstorm 10+ idea cards drawn from your founder context, recent trends, and the methodology's source families — and surface a top-3 list at the end. The whole flow takes ~5-15 minutes; you sign off on the top-3 cards before the next phase begins.

If you have a specific idea in mind, you can pass it as guidance:

```
/discover indie-saas-tools, dev-productivity
```

Or, for a more rigorous start, run `/scan` first to map territories before brainstorming.

#### Short version (for the experienced)

```bash
brew install git gh pandoc typst python@3.12 node@20  # macOS; adjust for Linux
gh auth login
git clone https://github.com/aanifowose111/discovery-to-ship-multi-agents.git
cd discovery-to-ship-multi-agents
# Optional, only if you want to sync agent-skills upstream later:
# git submodule update --init --recursive
claude
# Then in Claude Code:
# /discover
```

---

### About the agent-skills (and the optional submodule)

The three agent-skills personas (`code-reviewer`, `security-auditor`, `test-engineer`) and all 23 agent-skills (`incremental-implementation`, `test-driven-development`, `code-review-and-quality`, etc.) are **already in the repo as file copies** inside `.claude/agents/` and `.claude/skills/`. You don't need to do anything special to use them — Claude Code auto-discovers them.

These came from the [agent-skills](https://github.com/aanifowose111/agent-skills) fork (a fork of [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) by **Addy Osmani**, MIT-licensed). The fork is also vendored as an optional git submodule at `external/agent-skills/`. The submodule is **only needed if you want to sync future upstream changes** via:

```bash
bash scripts/update-agent-skills.sh
```

That script pulls the latest commits from `aanifowose111/agent-skills` (which you can sync to upstream `addyosmani/agent-skills` on GitHub by clicking "Sync fork" on your fork), re-copies the persona files + skill folders into `.claude/`, and commits the changes. Push with `git push` afterward.

If you don't initialize the submodule, day-to-day use of the workspace is unaffected — you only lose the upstream-sync path. You can initialize it later at any time with `git submodule update --init --recursive`.

---

### Slash commands you can run

Pipeline phase commands (each stops at a user-checkpoint):

| Command | What it does |
|---|---|
| `/scan [broad\|focused <topic>]` | Market scan → produces candidate territories for the next discovery cycle. |
| `/discover [optional territory names]` | Brainstorms idea cards from territories (or from founder fit + trends if no scan exists) and triages them. Single-command bootstrap when run with no args. |
| `/validate-card <slug>` | Runs the three product reviewers (viability, competition, market-segment) in parallel on a card. |
| `/scope-mvp <slug>` | Drafts the MVP brief — asks you to confirm the stack first — and runs the scope + code reviewers. |
| `/research-design <slug>` | Runs the UI/UX researcher to produce a design-direction report (3+ visual directions, color/typography options, brand positioning). |
| `/draft-design-brief <slug>` | Drafts the consolidated design brief (PRD+FRD) for the human designer, with the design-brief-reviewer. |
| `/start-build <slug>` | Kicks off the build phase for a green-lit-to-build product. Invokes the senior-software-engineer to ask orientation questions (web/mobile/desktop/hybrid order, MVP vs. full, first subsystem) and route to the right specialist. Brings the product to ready-to-deploy state. |
| `/ship-app <slug> [--web\|--mobile\|--both]` | Initialize the shipment / release phase. Release-readiness gate (QA pre-flight via senior-qa-engineer + security pre-flight via senior-security-engineer), then deploy via senior-devops-engineer (web via flask-deploy-runbook.md; mobile via EAS build + app-store submission), then post-deploy verification. Distinct from `/start-build` (which stops at ready-to-deploy state). Both pre-flight gates must pass before any deploy; user gets a final "ship now / cancel" confirmation in between. |
| `/preview-product <slug> [page]` | Preview a product's UI in the browser. Tries real preview (running app) first; falls back to dummy preview (Jinja + fixture data) if dependencies aren't connected yet. Always says which mode you got. Web only — mobile previews go through Expo Go / EAS preview builds. |
| `/trend-check [optional triggered <reason>]` | Sweeps a watchlist derived from active pipeline state and recommends downstream commands. |

<p align="center">
  <img src="https://scriptvil-cdn.nyc3.cdn.digitaloceanspaces.com/agents/discovery-to-ship-multi-agents-flowchart.png" alt="Workflow flowchart: from /scan through onboarding, discovery, validation, scoping, optional design, start-build, and ship-app — with decision branches for advance/revise/kill at each gate, and /trend-check running as a parallel cadence" width="80%">
</p>

Utility commands (always safe to run; not part of the pipeline cycle):

| Command | What it does |
|---|---|
| `/menu` | Quick menu of available commands and suggested next actions, based on current state. (Named `/menu` because `/help` is shadowed by Claude Code's built-in help dialog.) |
| `/status` | Complete pipeline-state snapshot — active scan, all active cards with statuses and ages, in-flight briefs, design phases, recent reports. Read-only. |
| `/setup` | Pre-flight verification for a new clone or new machine. Checks every required tool, git identity, GitHub auth, submodule init, agent-skills file copies. Pure verification (modifies nothing); surfaces a punch list of what's missing. |
| `/documentation` | End-to-end walkthrough of the workspace — the pipeline phases, slash commands, scripts, helper skills, conventions, and the reviewer-decision model. Uses your current pipeline state as concrete examples where possible. The full reference lives at `DOCUMENTATION.md` at the repo root; this command renders a condensed in-terminal version. **The only command that bypasses the first-launch onboarding interrupt** — so new users can read about the workspace before being prompted to populate `user-context/INTERESTS.md`. |
| `/run-tests` | Repo health / smoke test suite (`scripts/run_tests.py`). 7 categories: required tools, repo structure, YAML frontmatter, cross-references, pipeline lint, script smoke tests, documentation consistency. Green ✓ / yellow ⚠ / red ✗ indicators. **Run this after cloning, before opening a PR, or any time you want to confirm the repo is healthy.** Output includes the maintainer's email for bug reports. |
| `/system-check` | Compare your machine against the workspace's hardware + tooling requirements. Shows a row-by-row comparison table (OS, CPU arch, cores, RAM, disk, internet, required CLI tools) with required/recommended/your-value/status columns. Pure read-only — no permissions or installs needed. Wraps `scripts/check_system.py`. Run this on a new machine, or any time you want to know "will the workspace work on this computer?". |
| `/projects` | List every discovery-cycle project in your workspace (keyed by run-id) with a one-line summary of each, then offer actions on a chosen one — primarily **delete**. Deletion is **irreversible** (files bypass the Trash) and gated by a two-step user confirmation flow. Wraps `scripts/projects.py`. Use to clean up abandoned discovery cycles, verification tests, or any project you no longer need. |
| `/log` | View, add, or delete entries in your personal-space audit log at `user-context/audit-log.jsonl` (gitignored — never enters git). Records important user-driven actions and key build moments: `onboarding-skip` (gates the first-launch re-prompt), `project-delete`, `card-kill`, `card-revive`, `build-milestone` (project initialized, subsystem completed, ready-to-deploy reached, shipped), and free-text `user-note` entries you add. Subcommands: `/log` (display), `/log <text>` (add note), `/log delete <id>` (remove one), `/log clear` (wipe), `/log type <type>` (filter — e.g., `/log type build-milestone` gives a per-product build journal). |
| `/acknowledge-contributing` | One-time confirmation that you've read `CONTRIBUTING.md` before editing tracked files (required for non-owners). Personal-data folders are exempt; this is a Claude-side convention, not a technical lock. |

Helper skills (Claude invokes these implicitly when relevant phrasing appears):

| Skill | What it does |
|---|---|
| `doc-export` | Markdown → PDF or DOCX via pandoc + typst. Outputs land in `generated/<category>/`. Triggers on "export this as PDF", "generate a docx", "give me a PDF of [artifact]". |
| `web-preview` | Renders a Jinja template from `web-apps/<slug>/` with fixture demo data and opens it in Chrome. Triggers on "preview this page", "show me what this renders to". |

See **[HELP.md](HELP.md)** for the deeper command-by-command reference, common scenarios, gotchas, and recovery paths.

### Senior-engineer personas — how the build phase actually flows

After `/scope-mvp` returns `green-lit-to-build`, run `/start-build <slug>`. That command invokes the **`senior-software-engineer`** persona, which:

1. **Asks orientation questions** (in order): for a hybrid brief, which to build first (API + web is the recommendation); MVP vs. fully-featured (MVP is the recommendation); which subsystem to start with (database design is the recommendation).
2. **Routes each subsystem** to the right specialist persona.
3. **Sequences work** per system-design best practice — database before models, models before API contract, API contract before frontend, frontend skeleton with mocks before integration, integration before deploy.

The eight specialists are:

| Persona | Owns |
|---|---|
| `senior-system-design-engineer` | System shape, service boundaries, cross-cutting concerns. |
| `senior-database-engineer` | Schema, indexes, migrations, data-integrity guarantees. |
| `senior-backend-engineer` | ORM models, API contract, endpoint implementation, business logic. |
| `senior-frontend-engineer` | Web + mobile UI (Jinja+JS on web, RN on mobile), design-token integration, accessibility. |
| `senior-desktop-engineer` | Desktop UI (PySide6 by default; C# + Avalonia / Electron / Tauri if picked), UI ↔ core separation, packaging via PyInstaller, native integrations, distribution path. |
| `senior-qa-engineer` | Test coverage, integration at the seam, accessibility, release-readiness. Adds pytest-qt with `QT_QPA_PLATFORM=offscreen` for desktop UI tests. |
| `senior-devops-engineer` | Deploy, CI/CD, observability, incident response, backups. Adds PyInstaller + cross-platform CI matrix for desktop. |
| `senior-security-engineer` | Threat modeling, secure coding, auth design, infra hardening. |

Each specialist leverages relevant agent-skills (TDD, code-review-and-quality, security-and-hardening, performance-optimization, etc.) without you having to invoke them by name.

The workflow is **conversational and visible**:

- **Narrated handoffs** — at every specialist handoff, the senior-software-engineer announces *who* is doing *what* next, with the input artifacts, the expected output, and a rough time estimate. You feel the team working for you.
- **`BUILD_STATUS.md` per product** — a living checklist (dynamic, generated from this product's specific must-haves + stack + build-order) showing what's done, in progress, pending, and what was decided. Updated on every subsystem start, completion, or decision. Run `/status` to see the latest.
- **Visual preview with `/preview-product <slug> [page]`** — auto-detects whether real preview is possible (running app + wired dependencies) or falls back to dummy preview (Jinja + fixture data). Closes the "what does it actually look like right now" gap during the build.

You're never lost about "what now" or "where am I" during the build.

### Utility scripts

Auxiliary tools at `scripts/` (Python + Shell). Slash commands take priority for the actual pipeline work; these are for plumbing, verification, and tasks without a slash-command equivalent.

**Python:**

| Script | Purpose |
|---|---|
| `run_tests.py` | Repo health / smoke test suite. 7 categories (required tools, repo structure, YAML frontmatter, cross-references, pipeline lint, script smoke tests, documentation consistency). Green ✓ / yellow ⚠ / red ✗ indicators. **Backs the `/run-tests` slash command.** |
| `lint_pipeline.py` | Validate pipeline state consistency (frontmatter, status alignment, `@path` cross-references, required sections). |
| `new_idea_card.py` | Interactive idea-card creator for one-off captures outside `/discover`. |
| `check_links.py` | Scan tracked markdown for broken relative links and `@path` references; optional external-URL HEAD check. |
| `gen_run_id.py` | Generate a pipeline run-id (`<8-lowercase-alphanumeric>-<MMDDYY>`). CLI + importable; used by `/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/trend-check`. |
| `changelog_helper.py` | Auto-extract commits since the last tag and format as a CHANGELOG entry stub. |
| `report_summarizer.py` | Pretty-print summaries of all scan / validation / scoping / trend reports. |
| `projects.py` | Manage discovery-cycle projects: `list` (all projects with summaries), `show <run-id>` (dry-run of what would be deleted), `delete <run-id> --force` (actually delete). Identifies a project by run-id and walks every artifact keyed to it (ideas/, killed/, market-research/, web-apps/<slug>/, mobile-apps/<slug>/, generated/**/<slug>). **Destructive when `--force` is passed.** Backs the `/projects` slash command (which adds two interactive confirmations before invoking `--force`). |
| `check_system.py` | Compare host system against workspace requirements (OS, CPU arch, cores, RAM, free disk, internet, required CLI tools). Outputs a colored comparison table (required/recommended/your-value/✓⚠✗) plus a plain-text summary. Supports `--json` and `--no-color`. Stdlib only — no extra installs. **Backs the `/system-check` slash command.** |

**Shell:**

| Script | Purpose |
|---|---|
| `preflight.sh` | Shell version of `/setup` — verify dependencies and repo state. Runnable outside Claude Code. |
| `setup-deps.sh` | Install all required tools in one go (idempotent). Detects macOS vs. Linux. |
| `update-agent-skills.sh` | Pull the latest agent-skills upstream and commit the new submodule SHA. |
| `backup-personal-data.sh` | Tar up gitignored folders (ideas/, web-apps/, etc.); optional `--encrypt`. |
| `new-product-skeleton.sh` | Scaffold a new product folder under `web-apps/<slug>/`, `mobile-apps/<slug>/`, or `desktop-apps/<slug>/`. |
| `clean-killed-ideas.sh` | Archive old killed-idea files older than N days. |

See **[scripts/README.md](scripts/README.md)** for full usage, flags, and examples.

---

## Repository layout

```
.
├── CLAUDE.md                      Auto-loaded project context (read first)
├── README.md                      This file
├── DOCUMENTATION.md               End-to-end walkthrough; rendered in-terminal via `/documentation`
├── HELP.md                        Command-by-command reference
├── CHANGELOG.md                   Per-version log of workspace-wide changes
├── CONTRIBUTING.md                Contribution rules and required-updates matrix
├── SECURITY.md                    Responsible-disclosure path for security concerns
├── LICENSE                        MIT
├── .gitignore
├── .claude/
│   ├── commands/                  Slash commands — `/scan`, `/discover`, ...
│   ├── agents/                    Subagent definitions — reviewers and workers
│   ├── skills/                    Project-local skills (doc-export, web-preview)
│   └── settings.json              Project-level Claude Code permissions
├── guides/                        Long-form methodology + runbook documents
│   ├── product/                   Discovery, validation, MVP scoping
│   ├── market/                    Market scan, trend monitoring
│   ├── funding/                   Funding strategy
│   ├── web/                       Flask scaffold, deploy, storage, auth
│   ├── mobile/                    RN scaffold, EAS, app store submission
│   ├── desktop/                   PySide6 scaffold, packaging + distribution
│   └── ui-ux/                     Design research, brief, handoff
├── external/
│   └── agent-skills/              git submodule — aanifowose111/agent-skills fork
├── ideas/                         (gitignored) Your idea cards
├── market-research/               (gitignored) Your reports
├── web-apps/                      (gitignored) Your Flask web apps
├── mobile-apps/                   (gitignored) Your React Native apps
├── desktop-apps/                  (gitignored) Your PySide6 desktop apps
└── generated/                     (gitignored) PDF/DOCX exports
```

---

## Personalizing the workspace (recommended)

### First-launch onboarding — please don't skip it

When you launch Claude Code in this repo for the **first time** (with no `user-context/INTERESTS.md` present), Claude runs an interactive onboarding flow **on your very first message of that fresh session — regardless of what you type.** Whether your first message is `hi`, `/discover`, "let's build X", or anything else, the onboarding fires before Claude proceeds with it.

**Why this matters — please take 3 minutes to do the onboarding instead of clicking "Later":**

- `/discover` and every downstream command (validation, scoping, design research) produce **dramatically better-targeted output** when they have your interests + seed ideas to anchor on.
- Without that context, `/discover` brainstorms from generic capability shifts and adjacent workflows — candidates that look fine in isolation but **get killed in validation** for the "polite-shrug" failure mode (real problem, but the existing workarounds are good enough that users won't switch).
- With `INTERESTS.md` + `IDEAS.md` populated, the reviewers have founder-fit signals to weigh against the candidate's distribution and willingness-to-pay claims. **Cards that pass validation become products that ship.** Cards that don't pass waste your time.
- The onboarding takes ~3 minutes. You reply with raw, natural prose ("I'm a Python developer, I built a job board last year, I'm interested in AI eval tooling and indie productivity tools, here are five product ideas I've been chewing on…") and Claude formats it into the right structure for you.

You can pick "Later" if you genuinely need to skip — Claude will proceed with your original message — but the system will run in degraded mode until you populate the files. The picker reminds you each fresh session until both files exist.

The flow:

1. Welcome paragraph (what the workspace does, plus an ack of your original intent if you had one).
2. Picker (interactive): **"(Recommended) Update user-context first"** vs. **"Prefer to update later"**.
3. If you pick **Recommended**: Claude shows a **visual todo list** (via Claude Code's task panel — proper checkmarks that tick as items complete, not static text):
   - **Provide your interests** → you reply in natural prose; Claude formats and writes `user-context/INTERESTS.md`.
   - **Provide your seed ideas** → you reply with one-liners or anything; Claude formats and writes `user-context/IDEAS.md`.

   After both items complete, Claude proceeds with your original request (or `/menu` if you didn't have one).
4. If you pick **Prefer to update later**: Claude proceeds with your original message immediately. You can populate the files any time later via `cp user-context/<file>.example user-context/<file>` and editing, or by re-launching a fresh session.

**Triggers:** any first message in a fresh session where `INTERESTS.md` is missing. Examples: `hi`, `hey`, `what can I do?`, `/discover`, "I want to build a SaaS for…", anything. There's no "magic word" — every fresh-session start triggers the onboarding picker when the file is missing.

**You only see this once.** After you've completed the flow (or picked "Later"), future sessions go straight to normal entry.

**To test it yourself:** if you have `INTERESTS.md` populated and want to see the onboarding once, just rename it (`mv user-context/INTERESTS.md user-context/INTERESTS.md.bak`), launch a fresh `claude` session, and you'll see the picker on your first message.

If you'd rather do it manually (or want to add the third optional file), the `user-context/` folder ships with three templates:

```bash
cp user-context/INTERESTS.md.example user-context/INTERESTS.md
cp user-context/IDEAS.md.example     user-context/IDEAS.md
cp user-context/POLICY.md.example    user-context/POLICY.md
# Edit each with your specifics
```

All three live files are **gitignored** — your personal context stays local and never enters git.

- **`INTERESTS.md`** — your professional background, interests, hobbies, expertise areas. Read by `/discover` when you run it cold (no args, no active scan) so brainstorming anchors on territories that fit *you*.
- **`IDEAS.md`** — your seed-ideas backlog (products you've already thought about but haven't built). Strongest single signal for producing `/discover` candidates that survive validation instead of getting killed for generic-aesthetic mismatch.
- **`POLICY.md`** — your personal coding-and-build preferences. Claude consults it whenever it writes code, drafts a brief, or proposes architecture. Your policy overrides workspace defaults for matters of taste; correctness and security still win.

See `user-context/README.md` for what to put in each and why.

### Pipeline outputs are grouped per discovery cycle

Every `/discover` run creates a fresh `<run-id>` (format: `<8-lowercase-alphanumeric>-<MMDDYY>`, e.g., `csi48s2t-053126`) and uses it for both the cards folder (`ideas/<run-id>/<slug>.md`) and the related market-research folder (`market-research/<run-id>/`). Downstream artifacts from the SAME cycle — `triage.md`, `validation-<slug>.md`, `scoping-<slug>.md` — all land in `market-research/<run-id>/`. Cards from different `/discover` runs never mix; their validations stay grouped with their cycle.

Killed cards move to `ideas/killed/<run-id>/<slug>.md` (preserving the run-id link back to the discovery cycle that produced them).

`/scan` and `/trend-check` each create their own independent run folder.

Use `python3 scripts/gen_run_id.py` to generate a run-id manually if you need one.

## Personal vs. shared

The repo is structured so that:

- **Scaffolding** (guides, agents, commands, skills) is **committed and shared**.
- **Your personal product work** (ideas, market research, builds, exports) is **gitignored** — it stays on your disk, never enters git.

The `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `desktop-apps/`, and `generated/` folders each have a `README.md` that ships with the repo (explaining the convention). Their other contents are ignored.

This means:

- You can use the workflow for confidential or pre-announcement product work without any risk of accidentally pushing it.
- If you clone this repo on a second machine, your two machines have *different* personal data but the *same* scaffolding.
- Contributors and forkers never see anyone's personal work — they see only the scaffolding.

---

## Recommended git workflow

### If you're solo (just you, direct push access to `main`)

1. **Work directly on `main`** locally. Your personal data is gitignored, so it can't accidentally enter a commit.
2. **When you make a general improvement** (a new guide, a fix to a reviewer, an additional skill), commit and push:
   ```bash
   git add <changed files>
   git commit -m "<message>"
   git push origin main
   ```
3. **Pull updates** with `git pull` on `main`. Personal data is untouched.

You don't need branches for solo work — gitignoring the personal-data folders is what keeps your work out of git, not branch discipline.

### If you have collaborators (multiple people contributing)

Once you invite collaborators (via GitHub repo Settings → Collaborators), you'll likely want to require pull requests so changes get reviewed before they land. The pattern is:

1. **Enable branch protection** on `main` (GitHub repo Settings → Branches → Add rule → `main` → require pull request, require approving review, etc.).
2. **Each contributor (including you)** creates a feature branch for their work:
   ```bash
   git checkout -b feat/<short-name>
   # make the edit
   git add <changed files>
   git commit -m "<message>"
   git push -u origin feat/<short-name>
   ```
3. **Open a pull request** on GitHub from the feature branch into `main`.
4. **Someone other than the author reviews and approves**, then merges.

This is also the workflow external contributors (forkers) follow — they fork your repo, create a branch in their fork, push, and open a PR back to your repo. See the *How to contribute* section below.

---

## Feedback

Got an idea for improvement, hit a confusing bit, or just want to share how you're using the workspace? Email:

📧 **aanifowose111@gmail.com**

Subject line `[discovery-to-ship feedback]` so it gets sorted easily. Bug reports, usability friction, missing-but-useful command ideas, methodology critiques, success stories — all welcome.

## How to contribute

If you'd like to contribute improvements (new guides, fixes to reviewers, additional skills, methodology critiques), see **[CONTRIBUTING.md](CONTRIBUTING.md)** for the full guide. Quick version:

1. **Edit through Claude Code.** This workspace is designed to be modified inside Claude Code so CLAUDE.md's conventions and cross-reference rules apply automatically. Editing with other tools is allowed but you take on the cross-reference work manually.
2. **Run `/acknowledge-contributing`** in Claude Code before editing any tracked file. It walks you through a one-time confirmation that you've read `CONTRIBUTING.md` and creates a `.claude-acknowledged` marker (gitignored, per-clone). The repo owner is exempt automatically. Personal-data folders never require this.
3. **Email aanifowose111@gmail.com first** for anything non-trivial. Bug fixes (typos, broken links) can come in as PRs directly.
4. **Fork** this repo.
5. **Read [CONTRIBUTING.md](CONTRIBUTING.md)** — it lists what to update vs. what *not* to update when you make changes, plus the project's dos and don'ts.
6. **Create a feature branch** in your fork.
7. **Make the change**, test locally, commit.
8. **Open a PR** with a clear title and description; reference the email discussion if there was one.

By contributing, you agree that your contributions are licensed under the same MIT license as the rest of this repo (see [LICENSE](LICENSE)).

---

## License

MIT — see [LICENSE](LICENSE).

The agent-skills fork in `external/agent-skills/`, plus the file-level copies in `.claude/agents/` and `.claude/skills/` that derive from it, are originally MIT-licensed by **Addy Osmani** ([`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills), Copyright 2025). The full upstream LICENSE accompanies the source at `external/agent-skills/LICENSE`.

---

## A note from the maintainer — earn by contributing to AI research

Building useful systems takes time, and a lot of the most interesting work right now is in helping frontier AI labs make their models more capable, careful, and trustworthy. The maintainer of this repo (Abiodun Anifowose) currently works at **[Mercor](https://t.mercor.com/lSU0c)**, where he designs and develops advanced algorithms for training AI models to support frontier AI labs.

If you have a technical or specialist background — software engineering, science, mathematics, design, writing, language expertise, medicine, law — Mercor matches you with paid AI-training projects from frontier labs. The work is real, the pay is good, and it's a way for domain experts to contribute meaningfully to where AI is going (and earn while doing so).

**[Join Mercor →](https://t.mercor.com/lSU0c)**
