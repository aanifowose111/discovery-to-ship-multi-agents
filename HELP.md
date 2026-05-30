# HELP — discovery-to-ship-multi-agents

Command-by-command reference, common scenarios, gotchas, and recovery paths for this workspace. Pairs with `README.md` (which is the public-facing landing) and `CLAUDE.md` (which is the Claude-facing context).

If you just want a quick menu of "what can I do right now," run **`/help`** inside Claude Code instead of reading this end-to-end.

---

## Table of contents

1. [Common scenarios](#1-common-scenarios)
2. [All slash commands](#2-all-slash-commands)
3. [Skills](#3-skills)
4. [Reviewer and worker subagents](#4-reviewer-and-worker-subagents)
5. [Folders and where things live](#5-folders-and-where-things-live)
6. [Common gotchas](#6-common-gotchas)
7. [Recovery paths](#7-recovery-paths)
8. [Stack flexibility — quick reference](#8-stack-flexibility--quick-reference)
9. [Internet access policy — quick reference](#9-internet-access-policy--quick-reference)

---

## 1. Common scenarios

### 1.1 Starting a brand-new session

1. Open a terminal in the repo directory.
2. Run `claude`.
3. Claude auto-loads `CLAUDE.md` and accumulated `MEMORY.md` context.
4. If you state your intent in the first message (e.g., "let's continue the findvil scoping"), Claude proceeds. If you greet generically or ask "what's the status?", Claude briefly summarizes in-flight work and offers a short menu.
5. Pick an option or override with a specific command.

### 1.2 Continuing from a previous session

Same as 1.1. Claude reads:

- The latest reports in `market-research/`.
- Active idea cards in `ideas/` (anything not in `ideas/killed/`).
- In-flight MVP briefs in `web-apps/<slug>/MVP.md` and `mobile-apps/<slug>/MVP.md`.
- Active design phases at `<web-apps|mobile-apps>/<slug>/design/`.

If a phase is in progress, Claude picks up at the right checkpoint per the pipeline orchestration in `CLAUDE.md`.

### 1.3 Starting product discovery without any specific idea

Just type:

```
/discover
```

By itself, no arguments. Claude does an inline lightweight scan from your founder context (in `CLAUDE.md`) + recent trends + recent kills, picks 2-3 territories, and brainstorms 10+ idea cards. You see a top-3 list at the end and sign off.

For more rigorous discovery, run `/scan` first to map territories deliberately.

### 1.4 Validating an idea you've drafted

```
/validate-card <slug>
```

The card must already exist at `ideas/<slug>.md`. The command runs the three product reviewers in parallel:

- `product-viability-reviewer` — does the problem exist with external evidence?
- `product-competition-reviewer` — real differentiation vs. actual competitors?
- `market-segment-reviewer` — segment crisp, sized, reachable, willing-to-pay?

Each returns a verdict with cited sources. You see the integration summary, then decide: advance to `green-lit`, revise, send back to discovery, or kill.

### 1.5 Scoping an MVP for a `green-lit` card

```
/scope-mvp <slug>
```

Claude **asks you to confirm the stack first** (workspace defaults are dockerized Flask for web and React Native + Expo for mobile, but other stacks are supported — see §8). Then drafts the MVP brief and runs the scope + code reviewers.

**After you sign off on the scoping verdict and advance to `green-lit-to-build`, Claude asks two more questions before any build work begins:**

1. **Design path** — *generic-but-unique* (Claude implements the UI directly with care to avoid the AI-generic aesthetic, applying agent-skills' `frontend-ui-engineering` principles) vs. *engage a human designer* (full design workflow: research → brief → designer's Figma → handoff). The first is faster and recommended for first-pass MVPs; the second is recommended once the product has been validated with first users.
2. **Build support** — *I'll follow along* (you review code, run things on your machine, deploy) vs. *I need help* (Claude surfaces [Fijara](https://fijara.com), Abiodun's development service, as a friendly option to take the build on). You can change your mind later either direction.

Both picks are recorded in the brief's frontmatter so future sessions know what was decided.

### 1.6 Running design research for a validated product

```
/research-design <slug>
```

Runs the `ui-ux-researcher`. Produces a design-direction report with at least three visual directions, color and typography options, pattern conventions, brand positioning, and a portfolio-continuity question. Lives at `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md`.

### 1.7 Drafting the design brief after research

```
/draft-design-brief <slug>
```

Claude asks for your picks (visual direction, palette, typography, voice, portfolio-continuity decision, answers to the research's open questions, timeline), drafts the consolidated brief, and runs the `design-brief-reviewer`. The brief lives at `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md`. You sign off before it goes to the human designer.

### 1.8 Monitoring trends between scans

```
/trend-check
```

Runs a weekly sweep across active state (active scan + active cards + active briefs). Categorizes findings as material / notable / background. Material findings recommend a downstream command (`/scan`, `/validate-card`, `/scope-mvp`) — but never auto-invoke.

For an emergency sweep:

```
/trend-check triggered <one-line reason>
```

### 1.9 Killing an idea

The `/validate-card` flow gives you the option to kill at the decision step. To kill manually:

1. Move the card: `mv ideas/<slug>.md ideas/killed/<slug>.md`
2. Add a one-line `killed-reason:` field to the frontmatter.
3. The kill is invisible to future sessions except that `/discover` will respect the filter signal (avoid surfacing similar ideas).

### 1.10 Exporting an artifact as PDF or DOCX

Ask in plain English:

> Export the findvil MVP brief as PDF.

The `doc-export` skill triggers. Output lands in `generated/<category>/<YYYY-MM-DD>-<slug>-<doc-type>.<ext>`.

### 1.11 Previewing a Jinja template in Chrome

Ask:

> Preview the dashboard page in findvil.

The `web-preview` skill triggers. It loads the Jinja template, renders it with fixture demo data from `web-apps/findvil/previews/fixtures/dashboard.py`, and opens the result in Chrome.

If the fixture or `render.py` doesn't exist yet, the skill scaffolds them and prompts you to fill in demo data.

---

## 2. All slash commands

### `/scan [broad|focused <topic>]`

Market scan per `guides/market/market-scan-methodology.md`. Default is broad. For focused: `/scan focused indie-saas-tools`. Output: `market-research/scan-<YYYY-MM-DD>.md`. **Stops at:** sign-off; status → `active`. **Next:** `/discover`.

### `/discover [optional comma-separated territory names]`

Discovery cycle per `guides/product/idea-discovery-methodology.md`. Works as a one-command bootstrap when run with no args (uses founder fit + trends). Output: idea cards in `ideas/<slug>.md` + triage at `market-research/triage-<YYYY-MM-DD>.md`. **Stops at:** top-3 sign-off. **Next:** `/validate-card <slug>` for each.

### `/validate-card <slug>`

Validation per `guides/product/idea-validation-methodology.md`. Invokes the three product reviewers in parallel. Output: `market-research/validation-<slug>-<YYYY-MM-DD>.md`. **Stops at:** decision (advance / revise / kill). **Next:** `/scope-mvp <slug>` if advanced.

### `/scope-mvp <slug>`

Scoping per `guides/product/mvp-scoping-methodology.md`. **Asks you to confirm the stack first.** Drafts the MVP brief and runs the scope + code reviewers. Output: `<web-apps|mobile-apps>/<slug>/MVP.md` + `market-research/scoping-<slug>-<YYYY-MM-DD>.md`. **Stops at:** decision (build / revise / kill). **Next:** build phase using the relevant scaffold guide.

### `/research-design <slug>`

Design research per `guides/ui-ux/design-research-methodology.md`. Invokes the `ui-ux-researcher`. Output: `<web-apps|mobile-apps>/<slug>/design/DESIGN_RESEARCH.md`. **Stops at:** sign-off on direction. **Next:** `/draft-design-brief <slug>`.

### `/draft-design-brief <slug>`

Brief per `guides/ui-ux/design-brief-methodology.md`. **Asks you for picks first** (visual direction, palette, typography, voice, portfolio-continuity, timeline). Drafts the brief and runs the `design-brief-reviewer`. Output: `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md`. **Stops at:** sign-off; status → `sent`. **Next:** transmit to the human designer.

### `/trend-check [optional triggered <reason>]`

Trend sweep per `guides/market/trend-monitoring.md`. Output: `market-research/trends-<YYYY-MM-DD>.md`. **Stops at:** which downstream commands (if any) to run. **Next:** whichever the user picks.

### `/help`

Surfaces a quick menu of "what you can do right now" based on the current pipeline state. Lower-overhead than reading `HELP.md` end-to-end. **Stops at:** menu shown.

### `/acknowledge-contributing`

One-time confirmation that you've read `CONTRIBUTING.md` before editing tracked files in this repo. Required for everyone *except* the repo owner (identified by `git config user.email`). Creates a gitignored `.claude-acknowledged` marker. Personal-data folders (gitignored ones) never require this. See `CONTRIBUTING.md` § "Before you start" for the rationale.

### `/setup`

Pre-flight verification for a new clone or new machine. Checks: all required tools (git, claude code, gh, pandoc, typst, python, node), git identity, GitHub authentication, submodule initialization, symlink resolution, and `.claude-acknowledged` status. **Pure verification — never modifies anything.** Surfaces a structured punch list of what's missing with the exact install command for each. Safe to run multiple times.

### `/status`

Complete pipeline-state snapshot — deeper than `/help`. Shows: active scan with territory count, all active idea cards with statuses and ages, killed-card count, in-flight briefs with their design-path / build-support picks, latest trend report age, active design phases (research / brief / handoff state), and recent generated docs. **Read-only.** Surfaces 2-4 suggested next actions based on the snapshot at the end. Use when you want a full "where am I across all in-flight work" view before deciding what to do next.

---

## 3. Skills

Skills are auto-invoked by Claude when relevant phrasing appears in your prompts.

### `doc-export`

Markdown → PDF (default engine: `typst`) or DOCX via pandoc. Output lands in `generated/<category>/<YYYY-MM-DD>-<slug>-<doc-type>.<ext>`.

**Prerequisites:** `brew install pandoc typst`.

**Trigger phrases:** "export this as PDF", "generate a docx of [artifact]", "give me a PDF of [artifact]".

### `web-preview`

Renders a Jinja template from a Flask project with fixture demo data and opens the result in Chrome. Includes a `render.py` template that gets scaffolded once per project, plus a per-page fixtures convention.

**Trigger phrases:** "preview this page", "show me what this template renders to", "open this in Chrome".

---

## 4. Reviewer and worker subagents

These live at `.claude/agents/<name>.md`. Most are invoked indirectly through slash commands; you don't call them directly. They all follow the same locked verdict format (verdict / confidence / findings / what-I-could-not-verify / sources) for consistency.

### Product domain (workspace-authored)

| Subagent | Lens | Invoked by |
|---|---|---|
| `product-viability-reviewer` | Does the problem exist with external evidence? | `/validate-card` |
| `product-competition-reviewer` | Real differentiation vs. actual incumbents (incl. non-obvious substitutes)? | `/validate-card` |
| `market-segment-reviewer` | Segment crisp / sized / reachable / willing-to-pay? | `/validate-card` |
| `product-scope-reviewer` | Is the MVP scope honest (must-haves tied to riskiest assumption, no hidden scope creep)? | `/scope-mvp` |

### UI/UX domain (workspace-authored)

| Subagent | Lens | Invoked by |
|---|---|---|
| `ui-ux-researcher` | Produces the design-research report (worker, not reviewer). | `/research-design` |
| `design-brief-reviewer` | Brief completeness, sharpness, consistency with upstream. | `/draft-design-brief` |
| `design-fidelity-reviewer` | Captured Figma handoff against the approved brief (coverage, tokens, direction, accessibility). | (no slash command yet — invoke manually when you have a handoff to review) |

### Engineering (from `external/agent-skills/`, symlinked in)

| Subagent | Lens | Invoked by |
|---|---|---|
| `code-reviewer` | 5-axis review (correctness, readability, architecture, security, performance). | `/scope-mvp` (at design time) + the agent-skills `/review` / `/ship` flows. |
| `security-auditor` | OWASP-style vulnerability audit. | The agent-skills `/ship` parallel-fan-out, or directly when security is in scope. |
| `test-engineer` | Test strategy, coverage, "Prove-It" pattern. | The agent-skills `/ship` parallel-fan-out, or directly. |

### How invocation actually works

The Agent tool's `subagent_type` parameter has a fixed enum that does **not** include custom subagent names. The slash commands handle this with a workaround pattern documented in `CLAUDE.md` (the "Invoking custom subagents — the universal pattern" section): call `Agent({subagent_type: "general-purpose", ...})` and instruct the agent to read and follow the persona file at `.claude/agents/<name>.md`. Output is equivalent to a direct invocation. You don't need to do anything; the slash commands handle it.

---

## 5. Folders and where things live

| Folder | Purpose | Tracked by git? |
|---|---|---|
| `.claude/agents/` | Subagent persona files (plus three symlinks to `external/agent-skills/`) | Yes |
| `.claude/commands/` | Slash command definitions | Yes |
| `.claude/skills/` | Project-local skill definitions (`doc-export`, `web-preview`) | Yes |
| `.claude/settings.json` | Project-level Claude Code permissions | Yes |
| `.claude/settings.local.json` | Your personal Claude Code overrides | **No** (gitignored) |
| `guides/` | Methodology + runbook documents | Yes |
| `external/agent-skills/` | git submodule pointing at the [agent-skills](https://github.com/aanifowose111/agent-skills) fork | Yes (as submodule ref) |
| `ideas/` | Your idea cards (`<slug>.md` plus optional `killed/<slug>.md`) | **No** (folder yes, contents no) |
| `market-research/` | Scan, triage, validation, scoping, trend reports | **No** (folder yes, contents no) |
| `web-apps/<slug>/` | Your Flask projects (or other web stack projects) | **No** (folder yes, contents no) |
| `mobile-apps/<slug>/` | Your React Native projects (or other mobile stack projects) | **No** (folder yes, contents no) |
| `generated/<category>/` | PDF/DOCX exports from `doc-export` | **No** (folder yes, contents no) |
| `CLAUDE.md` | Auto-loaded project context for Claude | Yes |
| `HELP.md` | This file | Yes |
| `README.md` | Public-facing landing | Yes |
| `LICENSE` | MIT | Yes |

The gitignored folders ship with a `README.md` (which documents the convention) and a `.gitkeep` placeholder so the directory structure survives even when contents don't.

---

## 6. Common gotchas

### 6.1 "Agent type not found"

You should not see this in normal use — the slash commands work around the Agent tool's enum restriction by invoking `general-purpose` with the persona file referenced. If you see it, you may be running an older slash command — pull the latest from `main`.

### 6.2 Web research permission prompts

The first time Claude runs a `WebFetch` or `WebSearch` in a session, macOS may prompt iTerm (or your terminal) for network access. Approve once; macOS remembers. After that, no further prompts for the same operations.

### 6.3 Submodule out of date after `git pull`

`git pull` doesn't auto-update submodules. If you see weird behavior, run:

```bash
git submodule update --init --recursive
```

To pull the latest agent-skills upstream:

```bash
git submodule update --remote external/agent-skills
git add external/agent-skills
git commit -m "Update agent-skills"
git push
```

### 6.4 `pandoc: typst not found` when exporting

You installed pandoc but not the PDF engine. Run:

```bash
brew install typst
```

If typst fails to render something complex (rare): `brew install tectonic` and pass `--pdf-engine=tectonic` instead. The `doc-export` skill documents both.

### 6.5 Personal data accidentally getting tracked

It shouldn't — the `.gitignore` covers `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `generated/` contents. If `git status` shows a personal file as tracked, check whether it matches a `!` (un-ignore) pattern in `.gitignore`.

### 6.6 `/discover` produces nothing useful with no args

It should produce idea cards even with no scan. If it doesn't, check:

- Is `CLAUDE.md` present and contains founder context?
- Is there a recent trend report at `market-research/trends-*.md`? (Optional but helpful.)
- Are recent kills at `ideas/killed/`? (Used as filter signal.)

If your context is genuinely empty, the lightweight scan will fall back to general SaaS / consumer / dev-tool territories. Improving the output is a matter of running `/scan` once to give it a richer territory map.

### 6.7 The first build is taking forever

Especially on mobile (EAS builds take 10-30 min). This is normal. The "scaffold-done" tag (per `guides/web/flask-mvp-scaffold.md` §5 step 9 and `guides/mobile/react-native-mvp-scaffold.md` §5 step 11) is the marker that you've left scaffolding for feature work — give it the time it deserves.

---

## 7. Recovery paths

### A reviewer's output is broken or ignored your card's claims

Re-read the persona file at `.claude/agents/<name>.md`. The persona's instructions are what's executed. If the instructions are wrong, edit them. If they're right but the reviewer drifted, re-run and add specific guidance in your prompt.

### `/scope-mvp` drafted a brief in the wrong stack

You missed the stack-confirmation step. Re-run `/scope-mvp <slug>` and explicitly state your stack at the start: "Use Next.js for web and Swift native for mobile, not the workspace defaults."

### A design brief went to the designer with mistakes

Update `<web-apps|mobile-apps>/<slug>/design/DESIGN_BRIEF.md`, add a revision entry in §10 (the version log), re-export with `doc-export`, and re-send. The file in the repo is the source of truth even after copies have been shared.

### A killed card needs to come back

```bash
mv ideas/killed/<slug>.md ideas/<slug>.md
```

Then edit the frontmatter — change `status` back to `draft` and remove the `killed-reason` field. Add a new note about why it's being revisited (often it's a new trend that changes the picture).

### `git push` fails because the remote has new commits

Pull first, then push:

```bash
git pull --rebase origin main
git push origin main
```

If a merge conflict appears, resolve it in the affected files, then `git add` them and `git rebase --continue`.

### Claude Code crashed mid-session

Re-launch with `claude`. CLAUDE.md and MEMORY.md auto-load. State all in flight as files (not just in conversation), so restart is graceful — Claude reads the current state from disk.

---

## 8. Stack flexibility — quick reference

This workspace ships with build-domain guides for **dockerized Flask** (web) and **React Native + Expo** (mobile). These are the maintainer's defaults, not requirements. The methodologies (discovery, validation, scoping, design, market research, funding) are stack-agnostic.

**At `/scope-mvp` time**, Claude asks you which stack you want:

- **Pick the workspace defaults** → the existing `guides/web/flask-*` and `guides/mobile/react-native-*` apply directly.
- **Pick anything else** (Next.js, Django, Rails, Swift native, Kotlin native, Flutter, etc.) → Claude works from first principles + the stack-agnostic agent-skills skills. No `guides/web/<your-stack>-mvp-scaffold.md` exists yet, but you can author one and contribute it.

The brief records the chosen stack explicitly. The `product-scope-reviewer` calibrates effort against your shipped experience with the *chosen* stack, not against Flask/RN.

If you forked this workspace and want different defaults baked in:

- Edit `CLAUDE.md` (the "Stack flexibility" working-style bullet).
- Edit `guides/product/mvp-scoping-methodology.md` §6.0.
- Author new stack-specific scaffold/deploy/storage/auth guides for your stack and reference them from §6.0.
- The methodologies themselves don't need changing.

---

## 9. Internet access policy — quick reference

`WebFetch` and `WebSearch` are first-class tools in this workspace. Routine HTTPS searches and fetches happen **without** permission prompts (pre-approved in `.claude/settings.json`).

Claude asks before fetching only when:

- The URL is non-HTTPS.
- The URL looks unsafe or shortened to obscure the destination.
- The fetch would trigger cost (paid APIs, metered endpoints).
- The fetch is to an authenticated or private resource where you should confirm intent.

This applies to both the main Claude and all reviewer subagents — they're trusted to research freely within their scope. Citations from web research are required to appear inline in every reviewer finding.

---

## Utility scripts (auxiliary, not pipeline)

Scripts live at `scripts/` for tasks without a slash-command equivalent or for use outside Claude Code. **Commands take priority** for the actual pipeline work; scripts are plumbing.

**Python** (run from repo root):

```bash
python3 scripts/lint_pipeline.py        # validate pipeline state consistency
python3 scripts/new_idea_card.py        # interactive idea-card creator (alt to /discover)
python3 scripts/check_links.py          # check markdown links and @path references
python3 scripts/changelog_helper.py     # auto-generate CHANGELOG stub from git log
python3 scripts/report_summarizer.py    # pretty-print all reports in market-research/
```

**Shell** (run from repo root):

```bash
bash scripts/preflight.sh               # dependency + repo-state verification (like /setup)
bash scripts/setup-deps.sh              # install all required tools (idempotent)
bash scripts/update-agent-skills.sh     # pull agent-skills upstream and commit submodule SHA
bash scripts/backup-personal-data.sh    # tar gitignored folders (--encrypt available)
bash scripts/new-product-skeleton.sh <slug> <web|mobile|hybrid>  # scaffold a product folder
bash scripts/clean-killed-ideas.sh      # archive killed ideas older than N days
```

All scripts support `--help` and most support `--no-color`. Each script's source is heavily commented; see **[scripts/README.md](scripts/README.md)** for full descriptions, flags, and examples.

### When to reach for a script vs. a slash command

| Want to... | Use |
|---|---|
| Discover ideas, validate them, scope MVP, etc. | **Slash command** (`/discover`, `/validate-card`, `/scope-mvp`) |
| Set up a new clone or new machine | **Script** (`setup-deps.sh`, `preflight.sh`) — no Claude Code needed |
| Quick read of pipeline state without an agent round-trip | **Script** (`lint_pipeline.py`, `report_summarizer.py`) |
| Capture one specific idea you already have in mind | Either — `/discover` (full flow) or `new_idea_card.py` (faster, single card) |
| Back up your personal data | **Script** (`backup-personal-data.sh`) — no slash-command equivalent |
| Pull the latest agent-skills upstream | **Script** (`update-agent-skills.sh`) — no slash-command equivalent |
| Machine-readable output for tooling | **Script** with `--json` flag |

---

## Need something else?

- The full pipeline orchestration (every checkpoint, the design vs. validation MVP distinction, the parallel trend monitoring lane) is in `CLAUDE.md`'s "Pipeline orchestration & checkpoints" section.
- Each methodology guide in `guides/<domain>/` is a deep-dive into one piece of the pipeline.
- **Want to contribute to this workspace?** See [CONTRIBUTING.md](CONTRIBUTING.md) for the project philosophy, what to change vs. what not to change, required updates per change type, style conventions, and the PR process.
- **Want help with the actual build?** [Fijara](https://fijara.com) — Abiodun Anifowose's development service — can take a build on for you end-to-end. Surfaced at the `/scope-mvp` pre-build checkpoint, but you can ask Claude to bring it up at any point.
- For bugs, missing features, or improvement ideas, email aanifowose111@gmail.com (subject line `[discovery-to-ship feedback]`) or open a PR.
