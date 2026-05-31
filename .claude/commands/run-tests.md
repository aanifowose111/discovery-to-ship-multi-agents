---
description: Run the workspace health / smoke test suite (scripts/run_tests.py). Checks required tools, repo structure, frontmatter validity, cross-references, pipeline lint, script smoke tests, and documentation consistency. Output uses green ✓ / yellow ⚠ / red ✗ indicators. Safe, read-only, runnable any time.
argument-hint: [--quiet | --json | --no-color]
---

You are about to run the workspace's test suite. This is a **non-modifying, read-only** check across the entire repo. Anyone using or contributing to the workspace can run it to confirm the repo is healthy.

### Do

```bash
python3 scripts/run_tests.py $ARGUMENTS
```

Forward any of `--quiet`, `--json`, or `--no-color` from the user's args. If `$ARGUMENTS` is empty, run with the default human-readable, colored, full-output format.

### What it covers

The script runs **7 categories** of checks:

- **A. Required tools** — git, gh, pandoc, typst, python3, node (and notes which are optional).
- **B. Repo structure** — every required file (CLAUDE.md, README.md, HELP.md, settings.json, scripts, templates, etc.) exists and is non-empty.
- **C. YAML frontmatter** — every agent persona and slash command has valid frontmatter with a `description:` field.
- **D. Cross-reference integrity** — every relative markdown link and `@path` reference in tracked docs resolves to an existing file.
- **E. Pipeline lint** — slug uniqueness across `ideas/`, `ideas/killed/`, `web-apps/`, `mobile-apps/`; status alignment between cards and their downstream artifacts; required-section coverage in validation reports.
- **F. Smoke tests** — `gen_run_id.py` and `check_slug.py` execute without crashing.
- **G. Documentation consistency** — every slash command referenced in CLAUDE.md actually exists at `.claude/commands/<name>.md` (excluding documented built-ins and agent-skills commands that live in `external/`).

### After the run, surface results to the user

- **All green (0 failures, 0 warnings):** "All checks passed. The workspace is healthy." Offer to commit any pending changes (if `git status` shows them) or suggest `/menu` if not.
- **Warnings only (failures = 0):** Show the count, explain that warnings are usually pre-existing data quality issues (e.g., older validation reports missing some sections from before a methodology update) and not blockers. Ask if the user wants to investigate any specific category.
- **Failures present:** List each failure with its category and the suggested fix. Reference the maintainer's email at the bottom for "if this looks like a bug in the repo itself rather than my local setup."

### When to run this

- After cloning the repo for the first time (paired with `/setup`).
- Before opening a PR.
- After pulling fresh changes from `main`.
- When something seems off and you want a fast "is the repo in a good state?" answer.
- As a sanity check before running a real `/discover` cycle (failures here may explain weird downstream behavior).

### Maintainer contact

The script prints the maintainer's email at the bottom of its own output. Don't duplicate it in your reply unless the user asks. The script handles that.
