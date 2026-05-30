# scripts/

Utility scripts for the discovery-to-ship-multi-agents workspace. **Slash commands take priority** for the actual pipeline work (discovery, validation, scoping, design); these scripts are auxiliary tools you run directly from the shell when you want fine-grained control or when a workflow doesn't have a slash-command equivalent.

All scripts:
- Live at the repo root in `scripts/`.
- Are executable (`chmod +x` already set).
- Are designed to be safe to re-run.
- Use ANSI colors when the output is a terminal; pass `--no-color` for plain output.

Run all of them from the **repo root** unless noted otherwise.

---

## Python scripts

### `lint_pipeline.py` — validate pipeline state

```bash
python3 scripts/lint_pipeline.py
python3 scripts/lint_pipeline.py --json            # machine-readable
python3 scripts/lint_pipeline.py --quiet           # counts only
python3 scripts/lint_pipeline.py --no-suggestions  # hide fix hints
```

Walks the workspace and checks for:

- Idea cards with missing or invalid frontmatter fields (`slug`, `status`, `source`, `date-captured`).
- Status alignment — cards marked `in-validation` that lack a corresponding validation report; cards marked `green-lit` that lack an MVP brief.
- Briefs marked `green-lit-to-build` that haven't recorded `design-path:` and `build-support:` (the pre-build decisions from `/scope-mvp`).
- `@path` references in tracked markdown that don't resolve to real files.
- Validation reports missing required sections from the locked verdict format.

**Exit code:** 0 if clean or warnings-only; 1 if errors. Never modifies any file.

### `new_idea_card.py` — interactive card creator

```bash
python3 scripts/new_idea_card.py
```

Walks you through capturing a single idea card outside the `/discover` flow. Prompts for slug, source, problem, alternatives, etc.; validates the slug; checks for duplicates against `ideas/` and `ideas/killed/`; writes a properly-formatted card to `ideas/<slug>.md`.

Use when you have a specific product in mind and don't want to invoke a full discovery cycle. `/discover` remains the canonical path for brainstorming multiple cards from territories.

### `check_links.py` — markdown link checker

```bash
python3 scripts/check_links.py
python3 scripts/check_links.py --check-urls   # also HEAD-request external URLs (slow)
python3 scripts/check_links.py --json
python3 scripts/check_links.py --quiet
```

Scans every tracked markdown file for `[text](path)` and `@path` references and verifies the targets exist. Optionally HEAD-requests external HTTP(S) URLs.

Catches broken links after refactors, file renames, or deletions. Particularly useful before opening a PR.

### `changelog_helper.py` — CHANGELOG entry stub

```bash
python3 scripts/changelog_helper.py                       # since latest tag
python3 scripts/changelog_helper.py --since v0.3.0        # since a specific tag
python3 scripts/changelog_helper.py --range main..feature # arbitrary range
python3 scripts/changelog_helper.py --header "[0.4.0] — 2026-06-15"
```

Parses `git log` since the latest tag (or a given range), groups commits by Conventional-Commit prefix (feat / fix / docs / refactor / etc.), and prints a CHANGELOG entry stub matching the format in `CHANGELOG.md`.

Output goes to stdout — pipe or copy into CHANGELOG.md.

### `report_summarizer.py` — pretty-print report summaries

```bash
python3 scripts/report_summarizer.py
python3 scripts/report_summarizer.py --type validation
python3 scripts/report_summarizer.py --type scoping --slug findvil
```

Reads `market-research/` and prints a tabular summary of every scan / validation / scoping / trend report, grouped by type. Extracts each report's verdict / decision / status / dates / headline counts.

Useful as a quick "where am I across all reports" overview when state has accumulated.

---

## Shell scripts

### `preflight.sh` — dependency + state verification

```bash
bash scripts/preflight.sh
bash scripts/preflight.sh --no-color
bash scripts/preflight.sh --quiet
```

Shell-side equivalent of the `/setup` slash command. Verifies all required tools (git, gh, pandoc, typst, python3, node), git identity (user.email + user.name), GitHub authentication, submodule initialization, the three agent-skills symlinks, and the `.claude-acknowledged` marker.

**Pure verification — never modifies anything.** Surfaces a colored ✓/⚠/✗ punch list. Exits 0 if all required checks pass (warnings allowed), 1 otherwise.

Useful when setting up a second machine, or when you want to verify your environment without firing up Claude Code.

### `update-agent-skills.sh` — update the agent-skills submodule

```bash
bash scripts/update-agent-skills.sh
bash scripts/update-agent-skills.sh --dry-run
```

Pulls the latest commits from the agent-skills upstream into `external/agent-skills/`, stages the new submodule SHA in the parent repo, and creates a commit. **Does not push** — that's your call.

Use this when you want to pick up upstream improvements from the agent-skills fork.

### `backup-personal-data.sh` — tar up gitignored folders

```bash
bash scripts/backup-personal-data.sh
bash scripts/backup-personal-data.sh --encrypt
bash scripts/backup-personal-data.sh --output ~/Dropbox/dts-backups
```

Creates a timestamped tarball of `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, and `generated/` (the gitignored folders that hold your personal product work). Defaults to `~/discovery-to-ship-backups/`.

With `--encrypt`, uses `openssl AES-256-CBC` and prompts for a passphrase.

Because your personal data never enters git, a backup strategy matters — this script makes "back up everything I've been working on" a single command.

### `setup-deps.sh` — install all required tools

```bash
bash scripts/setup-deps.sh
bash scripts/setup-deps.sh --no-optional    # skip node@20
```

Idempotent installer for everything in the prerequisites list. Detects macOS (uses Homebrew, installs it if missing) vs. Linux (uses apt; falls back to manual instructions for typst since it's not in apt). Skips tools that are already installed.

The fastest way to bootstrap a new machine after `git clone`. Pair with `bash scripts/preflight.sh` to verify the install worked.

### `new-product-skeleton.sh` — scaffold a new product folder

```bash
bash scripts/new-product-skeleton.sh <slug> <web|mobile|hybrid>
```

Creates the expected per-product layout under `web-apps/<slug>/` and/or `mobile-apps/<slug>/`: README, per-product `.gitignore` for build artifacts, `design/` subfolder for the eventual design phase, and (for web) `previews/fixtures/` for the `web-preview` skill.

**Does not create MVP.md** — that's the `/scope-mvp` slash command's job. This just lays down the directory bones so the brief has a place to land.

### `clean-killed-ideas.sh` — archive old killed ideas

```bash
bash scripts/clean-killed-ideas.sh
bash scripts/clean-killed-ideas.sh --days 60
bash scripts/clean-killed-ideas.sh --dry-run
```

Finds `.md` files in `ideas/killed/` older than N days (default 90), tars them into a timestamped archive that stays in `ideas/killed/`, and removes the originals. Keeps `ideas/killed/` navigable as it grows over months of use.

The archive is not deleted — if you ever want to revisit an old killed card, restore with `tar -xzf ideas/killed/killed-archive-YYYYMMDD.tar.gz`.

---

## When to use scripts vs. slash commands

**Slash commands** (`/scan`, `/discover`, `/validate-card`, `/scope-mvp`, etc.) are the **canonical path** for the actual pipeline work. They orchestrate reviewers, enforce checkpoints, and respect the methodology guides.

**Scripts** are auxiliary tools you reach for when:

- You're not in Claude Code (e.g., setting up a new machine — `preflight.sh`, `setup-deps.sh`).
- You want a quick read of the current state without an agent round-trip (`lint_pipeline.py`, `report_summarizer.py`).
- The task has no slash-command equivalent (`update-agent-skills.sh`, `backup-personal-data.sh`, `clean-killed-ideas.sh`, `new-product-skeleton.sh`).
- You want fine-grained machine-readable output (`--json` flags on the Python scripts).

The two layers complement each other. Use commands for the human workflow; use scripts for the plumbing.
