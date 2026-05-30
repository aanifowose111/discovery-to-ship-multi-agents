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

## The cloned agent-skills fork

The user has a fork at `https://github.com/aanifowose111/agent-skills.git` that contains a large set of pre-built skills (including stage-specific code review skills) which we will use rather than re-build.

**Open question (raise with user when we get there):** where does the cloned repo live? Options under consideration:
1. **`external/agent-skills/`** at the project root, treated as a vendored library — we then copy or symlink the specific skills we want into `.claude/skills/` with our naming convention applied.
2. **`.claude/skills/agent-skills/`** directly — simplest to clone, but the repo's internal nested structure means Claude Code's auto-discovery may not pick up the nested skills correctly.

Recommend option 1 once the user is ready to clone, but confirm first.

## Conventions for this project

- **One concern per skill.** If a skill is doing two unrelated things, split it into two folders.
- **`description` field must say *when to use it*** (so Claude can decide on its own), not just what it does.
- **Skills authored here should not duplicate** what is already in the cloned agent-skills repo — check there first; only add a local skill if there is a real gap.
- **Until the user has verified a skill**, treat it as draft. The user signs off before it becomes load-bearing.
- **Update the index in `CLAUDE.md`** whenever a skill is added, renamed, or removed.
