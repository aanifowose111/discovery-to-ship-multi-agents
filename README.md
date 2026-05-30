# Discovery-to-Ship Multi-Agents

A Claude Code–orchestrated portfolio pipeline for discovering, validating, scoping, designing, and shipping distinctive web and mobile products. Built around opinionated methodology guides, narrow-lens reviewer subagents, helper skills, and pipeline slash commands.

The name reflects what's in the box: many specialized agents (worker, reviewer, and code-review personas), composed into one pipeline that takes a product from **discovery** all the way through **ship**.

This repo is the *scaffolding*. Your products (ideas, market research, builds) live in the same workspace but are gitignored — they stay on your disk, never enter git. The shared part is the workflow itself: how to think about discovery, how to validate, how to scope, how to design without producing generic-looking output, and (if you use the workspace defaults) how to build dockerized Flask backends and React Native frontends in a repeatable way.

## Stack flexibility — this is important

This workspace ships with **opinionated defaults**:

- **Web:** dockerized Flask (Python) + Jinja templates + vanilla JavaScript.
- **Mobile:** React Native with Expo + TypeScript, paired with the Flask backend.

These are the **maintainer's** stack choices, not requirements baked into the workflow. The methodology guides (discovery, validation, scoping, design, market research, funding) are **stack-agnostic** — they work whether you ship in Flask, Next.js, Django, Rails, Phoenix, Go, Java/Spring, Swift native, Kotlin native, Flutter, or anything else.

**Before any build or design work, Claude will ask you what stack you want.** The MVP brief records the choice. From there:

- **If you pick the workspace defaults**, the existing build-domain guides (`guides/web/flask-*`, `guides/mobile/react-native-*`, etc.) apply directly.
- **If you pick something else**, the build-domain guides do not apply as-is. Claude will work from first principles plus the stack-agnostic skills in [agent-skills](https://github.com/aanifowose111/agent-skills). You can either build without a stack-specific scaffold guide, or contribute one for your chosen stack (e.g., `guides/web/nextjs-mvp-scaffold.md`) — PRs welcome.

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
| **Pipeline slash commands** | `/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/research-design`, `/draft-design-brief`, `/start-build`, `/trend-check`, `/menu`, `/setup`, `/status`, `/acknowledge-contributing` | `.claude/commands/` |
| **Reviewer assistants** | Product viability / competition / market-segment / scope reviewers, design-brief and design-fidelity reviewers, UI/UX researcher | `.claude/agents/` |
| **Senior-engineer personas** | `senior-software-engineer` (orchestrator) + 7 specialists: system-design, database, backend, frontend, QA, devops, security. Each plays a senior-IC role during the build phase. | `.claude/agents/senior-*.md` |
| **Agent-skills personas** | `code-reviewer`, `security-auditor`, `test-engineer` — file copies from [`aanifowose111/agent-skills`](https://github.com/aanifowose111/agent-skills) (fork), originally authored by **Addy Osmani** at [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills), MIT-licensed. | Vendored into `.claude/agents/`; re-sync via `scripts/update-agent-skills.sh`. |
| **Agent-skills skills** (23) | api-and-interface-design, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine, incremental-implementation, interview-me, performance-optimization, planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development, spec-driven-development, test-driven-development, using-agent-skills — same upstream credit. | Vendored into `.claude/skills/`; re-sync via `scripts/update-agent-skills.sh`. |
| **Helper skills** | `doc-export` (markdown → PDF/DOCX), `web-preview` (render Jinja in Chrome) | `.claude/skills/` |
| **Methodology guides** | Product discovery / validation / MVP scoping; market scan + trend monitoring; funding strategy; Flask scaffold + deploy + storage + auth patterns; React Native scaffold + EAS + store submission; UI/UX research + brief + handoff | `guides/` |
| **Project-wide context** | The Claude-facing entry point (auto-loaded by Claude Code) | `CLAUDE.md` |

See `CLAUDE.md` for the full inventory and how the pieces fit together.

---

## Getting started

### Prerequisites

- **macOS, Linux, or WSL.** Most of the runbooks assume macOS for the developer machine; production targets are Linux (DigitalOcean droplet or App Platform).
- **[Claude Code CLI](https://docs.claude.com/en/docs/claude-code/installation)** — this whole workspace is designed to be driven from inside Claude Code.
- **Git ≥ 2.13** (for submodule support).
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

| Tool | Purpose | Install (macOS) | Install (Ubuntu / WSL) |
|---|---|---|---|
| **git** | Version control | comes with Xcode CLI tools (`xcode-select --install`) | `sudo apt update && sudo apt install git` |
| **Claude Code CLI** | The agent runner | [docs.claude.com/en/docs/claude-code/installation](https://docs.claude.com/en/docs/claude-code/installation) | same link |
| **Homebrew** (macOS only) | Package manager for the rest | `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` | n/a (you have `apt`) |
| **GitHub CLI** (`gh`) | Auth with GitHub from the terminal | `brew install gh` | `sudo apt install gh` |
| **pandoc** | Markdown → PDF/DOCX (for `doc-export` skill) | `brew install pandoc` | `sudo apt install pandoc` |
| **typst** | Modern PDF engine for pandoc | `brew install typst` | see [github.com/typst/typst](https://github.com/typst/typst) |
| **Python 3.11+** | For Flask web apps (workspace default) | `brew install python@3.12` | `sudo apt install python3 python3-pip` |
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
git clone --recurse-submodules https://github.com/aanifowose111/discovery-to-ship-multi-agents.git
cd discovery-to-ship-multi-agents
```

If you forgot the `--recurse-submodules` flag, run this once inside the directory to pull the agent-skills submodule:

```bash
git submodule update --init --recursive
```

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
git clone --recurse-submodules https://github.com/aanifowose111/discovery-to-ship-multi-agents.git
cd discovery-to-ship-multi-agents
claude
# Then in Claude Code:
# /discover
```

---

### What the submodule pulls in

The clone command above pulls the [agent-skills](https://github.com/aanifowose111/agent-skills) fork (a fork of [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) by **Addy Osmani**, MIT-licensed) into `external/agent-skills/`. From there, three personas (`code-reviewer`, `security-auditor`, `test-engineer`) and 23 skills are **copied** into `.claude/agents/` and `.claude/skills/` respectively so Claude Code auto-discovers them and GitHub renders them properly.

To update agent-skills to the latest upstream:

```bash
bash scripts/update-agent-skills.sh
```

That single command pulls the submodule from `aanifowose111/agent-skills` (which you can sync to upstream `addyosmani/agent-skills` on GitHub by clicking "Sync fork"), re-copies the persona files + skill folders into `.claude/`, and commits the changes. Push with `git push` afterward.

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
| `/start-build <slug>` | Kicks off the build phase for a green-lit-to-build product. Invokes the senior-software-engineer to ask orientation questions (web/mobile/hybrid order, MVP vs. full, first subsystem) and route to the right specialist. |
| `/preview-product <slug> [page]` | Preview a product's UI in the browser. Tries real preview (running app) first; falls back to dummy preview (Jinja + fixture data) if dependencies aren't connected yet. Always says which mode you got. Web only — mobile previews go through Expo Go / EAS preview builds. |
| `/trend-check [optional triggered <reason>]` | Sweeps a watchlist derived from active pipeline state and recommends downstream commands. |
| `/menu` | Quick menu of available commands and suggested next actions, based on current state. (Named `/menu` because `/help` is shadowed by Claude Code's built-in help dialog.) |

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

The seven specialists are:

| Persona | Owns |
|---|---|
| `senior-system-design-engineer` | System shape, service boundaries, cross-cutting concerns. |
| `senior-database-engineer` | Schema, indexes, migrations, data-integrity guarantees. |
| `senior-backend-engineer` | ORM models, API contract, endpoint implementation, business logic. |
| `senior-frontend-engineer` | UI implementation (Jinja+JS on web, RN on mobile), design-token integration, accessibility. |
| `senior-qa-engineer` | Test coverage, integration at the seam, accessibility, release-readiness. |
| `senior-devops-engineer` | Deploy, CI/CD, observability, incident response, backups. |
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
| `lint_pipeline.py` | Validate pipeline state consistency (frontmatter, status alignment, `@path` cross-references, required sections). |
| `new_idea_card.py` | Interactive idea-card creator for one-off captures outside `/discover`. |
| `check_links.py` | Scan tracked markdown for broken relative links and `@path` references; optional external-URL HEAD check. |
| `changelog_helper.py` | Auto-extract commits since the last tag and format as a CHANGELOG entry stub. |
| `report_summarizer.py` | Pretty-print summaries of all scan / validation / scoping / trend reports. |

**Shell:**

| Script | Purpose |
|---|---|
| `preflight.sh` | Shell version of `/setup` — verify dependencies and repo state. Runnable outside Claude Code. |
| `setup-deps.sh` | Install all required tools in one go (idempotent). Detects macOS vs. Linux. |
| `update-agent-skills.sh` | Pull the latest agent-skills upstream and commit the new submodule SHA. |
| `backup-personal-data.sh` | Tar up gitignored folders (ideas/, web-apps/, etc.); optional `--encrypt`. |
| `new-product-skeleton.sh` | Scaffold a new product folder under `web-apps/<slug>/` or `mobile-apps/<slug>/`. |
| `clean-killed-ideas.sh` | Archive old killed-idea files older than N days. |

See **[scripts/README.md](scripts/README.md)** for full usage, flags, and examples.

---

## Repository layout

```
.
├── CLAUDE.md                      Auto-loaded project context (read first)
├── README.md                      This file
├── HELP.md                        Command-by-command reference (when written)
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
│   └── ui-ux/                     Design research, brief, handoff
├── external/
│   └── agent-skills/              git submodule — aanifowose111/agent-skills fork
├── ideas/                         (gitignored) Your idea cards
├── market-research/               (gitignored) Your reports
├── web-apps/                      (gitignored) Your Flask web apps
├── mobile-apps/                   (gitignored) Your React Native apps
└── generated/                     (gitignored) PDF/DOCX exports
```

---

## Personal vs. shared

The repo is structured so that:

- **Scaffolding** (guides, agents, commands, skills) is **committed and shared**.
- **Your personal product work** (ideas, market research, builds, exports) is **gitignored** — it stays on your disk, never enters git.

The `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, and `generated/` folders each have a `README.md` that ships with the repo (explaining the convention). Their other contents are ignored.

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

Building useful systems takes time, and a lot of the most interesting work right now is in helping frontier AI labs make their models more capable, careful, and trustworthy. The maintainer of this repo (Abiodun Anifowose) currently works as an **AI Chemistry Evaluation expert on [Mercor](https://t.mercor.com/lSU0c)** — designing and implementing Python-based scientific evaluation systems for frontier AI models, including black-box benchmarking functions and chemistry reasoning tasks that directly support major AI research labs.

If you have a technical or specialist background — software engineering, science, mathematics, design, writing, language expertise, medicine, law — Mercor matches you with paid AI-training projects from frontier labs. The work is real, the pay is good, and it's a way for domain experts to contribute meaningfully to where AI is going (and earn while doing so).

**[Join Mercor with my referral link →](https://t.mercor.com/lSU0c)**
