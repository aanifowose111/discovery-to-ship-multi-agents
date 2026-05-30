# Agents Workspace

A Claude Code–orchestrated portfolio pipeline for discovering, validating, scoping, designing, and shipping distinctive web and mobile products. Built around opinionated methodology guides, narrow-lens reviewer assistants, and pipeline slash commands.

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
| **Pipeline slash commands** | `/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/research-design`, `/draft-design-brief`, `/trend-check` | `.claude/commands/` |
| **Reviewer assistants** | Product viability / competition / market-segment / scope reviewers, design-brief and design-fidelity reviewers, UI/UX researcher | `.claude/agents/` |
| **Agent-skills personas** | `code-reviewer`, `security-auditor`, `test-engineer` from [aanifowose111/agent-skills](https://github.com/aanifowose111/agent-skills) | symlinked into `.claude/agents/` from `external/agent-skills/` (git submodule) |
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

### Clone

```bash
# With submodules in one command (recommended):
git clone --recurse-submodules https://github.com/aanifowose111/agents.git
cd agents

# Or if you cloned without --recurse-submodules:
git submodule update --init --recursive
```

The submodule pulls down the [agent-skills](https://github.com/aanifowose111/agent-skills) fork into `external/agent-skills/`. Three personas (`code-reviewer`, `security-auditor`, `test-engineer`) are symlinked from there into `.claude/agents/` so Claude Code auto-discovers them.

### First run

Open Claude Code in the repo directory. Try one of these:

- **`/scan`** — start a market scan. Produces a list of candidate territories for the next discovery cycle. Stops at a sign-off checkpoint.
- **`/discover`** — brainstorm idea cards. If no active scan exists yet, this command runs an inline lightweight scan first, so you can bootstrap from a single command.
- **`/trend-check`** — sweep for recent capability/regulatory/funding shifts relevant to your active pipeline state.

Then check `CLAUDE.md` for the full pipeline orchestration and `HELP.md` (when present) for command-by-command reference.

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

## Recommended git workflow for personal use

When you're using this repo for your own products:

1. **Work directly on `main`** locally. Your personal data is gitignored, so it can't accidentally enter a commit.
2. **When you make a general improvement** (a new guide, a fix to a reviewer, an additional skill), commit it on a feature branch:
   ```bash
   git checkout -b feat/<short-name>
   # make the edit
   git add <changed files>
   git commit -m "<message>"
   git push -u origin feat/<short-name>
   ```
   Then open a PR (or push to `main` directly if you're solo).
3. **Pull updates** with `git pull` on `main`. Personal data is untouched.

You don't need a separate "personal branch" — gitignoring the personal-data folders is what keeps your work out of git, not branch discipline.

---

## How to contribute

If you'd like to contribute improvements (new guides, fixes to reviewers, additional skills, methodology critiques), reach out first:

📧 **aanifowose111@gmail.com**

Most non-trivial improvements should be discussed before opening a PR, so we don't end up with two people doing similar work in parallel or solving problems differently. Bug fixes (typos, broken links, obviously-wrong examples) can come in as PRs directly.

Standard workflow:

1. Fork this repo.
2. Create a feature branch.
3. Make the change.
4. Open a PR with a clear title and description; reference the email discussion if there was one.

By contributing, you agree that your contributions are licensed under the same MIT license as the rest of this repo (see [LICENSE](LICENSE)).

---

## License

MIT — see [LICENSE](LICENSE).

The agent-skills fork in `external/agent-skills/` is itself MIT-licensed by its upstream author; consult its own LICENSE for that submodule.
