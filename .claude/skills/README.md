# Skills

Each subfolder in this directory is one skill. The subfolder must contain a `SKILL.md` file with YAML frontmatter; Claude Code auto-discovers it and decides on its own when the skill is relevant.

## Folder format

```
.claude/skills/<skill-name>/
├── SKILL.md         (required — describes what the skill does and when to use it)
├── <other files>    (optional — supporting scripts, templates, reference docs)
```

`SKILL.md` frontmatter:

```markdown
---
name: flask-docker-setup
description: Use when scaffolding a new dockerized Flask web app from scratch. Produces a working app skeleton with docker-compose, Dockerfile, and a baseline Flask project structure.
---

[The skill body — instructions Claude follows when the skill is invoked.]
```

## Naming convention

Subfolder names use the pattern **`<domain>-<topic>`**, kebab-case throughout. Same domain prefixes as `.claude/agents/`:

| Prefix | Domain |
|---|---|
| `web-` | Web app development |
| `mobile-` | Mobile app development |
| `product-` | Product idea search/discovery/viability |
| `market-` | Market research |
| `funding-` | Funding strategy/approach/reports |

Examples: `web-flask-docker-setup/`, `web-flask-blueprint-layout/`, `mobile-rn-project-setup/`, `product-idea-brainstorm/`, `market-segment-sizing/`, `funding-pitch-draft/`.

## Agent-skills skills (vendored copies)

The 23 skills from the agent-skills repo live here as **file-level copies** of the source files. Each skill is at `.claude/skills/<name>/`, containing at minimum a `SKILL.md` (plus any supporting files the source skill has, like `scripts/` or `references/`).

**Attribution.** These skills were originally authored by **Addy Osmani** (MIT License, Copyright 2025), maintained at [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills). They reach this workspace via [`aanifowose111/agent-skills`](https://github.com/aanifowose111/agent-skills), a fork by Abiodun Anifowose. The full LICENSE accompanies the source via the git submodule at `external/agent-skills/LICENSE`.

**Why copies, not symlinks?** GitHub's web UI renders file symlinks as text containing the target path rather than the resolved content — clicking them doesn't show the file. Regular-file copies render properly. Upstream updates are brought in by:

```bash
bash scripts/update-agent-skills.sh
```

That script pulls the submodule and re-copies the personas + skills automatically.

**Skills inventory** (all 23): api-and-interface-design, browser-testing-with-devtools, ci-cd-and-automation, code-review-and-quality, code-simplification, context-engineering, debugging-and-error-recovery, deprecation-and-migration, documentation-and-adrs, doubt-driven-development, frontend-ui-engineering, git-workflow-and-versioning, idea-refine, incremental-implementation, interview-me, performance-optimization, planning-and-task-breakdown, security-and-hardening, shipping-and-launch, source-driven-development, spec-driven-development, test-driven-development, using-agent-skills.

Plus the two project-local skills authored in this workspace: `doc-export`, `web-preview` (described elsewhere in this README).

## Conventions for this project

- **One concern per skill.** If a skill is doing two unrelated things, split it into two folders.
- **`description` field must say *when to use it*** (so Claude can decide on its own), not just what it does.
- **Skills authored here should not duplicate** what is already in the cloned agent-skills repo — check there first; only add a local skill if there is a real gap.
- **Until the user has verified a skill**, treat it as draft. The user signs off before it becomes load-bearing.
- **Update the index in `CLAUDE.md`** whenever a skill is added, renamed, or removed.

## Build-phase auto-invocation

CLAUDE.md § Build-phase skill auto-invocation is the canonical reference — the proactive vs. situational lists + the Flask caveat for `frontend-ui-engineering` live there. The per-persona spec (in each `.claude/agents/senior-*.md`) wins on any disagreement.
