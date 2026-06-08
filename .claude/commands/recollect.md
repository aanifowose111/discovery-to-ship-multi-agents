---
description: Read-only "where are we" synthesis for a specific product. Reads every artifact related to the product (brief, validation, scoping report, design research, design spec, design brief, build status, team file, source tree) and emits a one-screen synthesis + 2-4 plausible next actions. Distinct from /continue-build (which actually invokes the orchestrator to resume work) and /status (which reports across ALL products in the workspace, not one specifically).
argument-hint: <product-slug>
---

You are about to produce a comprehensive read-only synthesis of the current state of one product. **Do not invoke any subagent.** Do not edit any files. This command is pure orientation — for the user who's coming back to a product after a break and needs to remember "where was I?" before deciding whether to `/continue-build`, `/scope-v1`, `/ship-app`, or anything else.

**Use this when:**
- You're returning to a product after days/weeks away and need to re-orient.
- You want to assess "is this product ready for `/continue-build` or does something earlier need attention?" without committing to an action.
- Sharing context with a collaborator — the output of `/recollect` is a self-contained brief on the product's state.

**Arguments:** $ARGUMENTS — the product slug.

### Pre-flight

1. **Locate the product folder.** Check `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`. If none exists, look for the slug among idea cards (`ideas/*/<slug>.md` or `ideas/killed/*/<slug>.md`):
   - **Card exists but no product folder** → tell the user: "Card found at `<path>` with status `<value>`. No product folder yet. Suggested next: `/scope-mvp <slug>` if `green-lit`; `/validate-card <slug>` if `triaged`; `/revive-card <slug>` if killed." Then stop.
   - **Killed card only** → "Card was killed (`<path>`). To revisit: `/revive-card <slug>` or pick a fresh slug for a new card." Then stop.
   - **No card and no product folder** → "No artifacts found for `<slug>` anywhere in the workspace. Did you mean a different slug?" Then stop.

2. **Resolve `<product-folder>` and `<stack>`** (web/mobile/desktop).

### Do — gather everything

Read these in parallel where possible (independent reads):

**Product artifacts (in `<product-folder>`):**
- `MVP.md` — frontmatter + first 50 lines for the one-line product description.
- `V1.md` if it exists — frontmatter + first 50 lines.
- `BUILD_STATUS.md` if it exists — full file (it's the build map).
- `team.json` if it exists — to use names in the synthesis.
- `INFRA_COST.md` if it exists — last-recorded estimate.
- `design/DESIGN_RESEARCH.md` if it exists — frontmatter only.
- `design/DESIGN_SPEC.md` if it exists — frontmatter only.
- `design/DESIGN_BRIEF.md` if it exists — frontmatter only.
- `design/handoff/` directory listing if it exists.

**Run-folder artifacts (in `market-research/<run-id>/`):**
- Resolve `<run-id>` from MVP.md's `run-id:` frontmatter or `parent-run-id:`.
- `validation-<slug>.md` if it exists — frontmatter only.
- `scoping-<slug>.md` if it exists — frontmatter only.
- `scoping-v1-<slug>.md` if it exists — frontmatter only.

**Idea card** at `ideas/<run-id>/<slug>.md`:
- Full frontmatter.

**Source tree** at `<product-folder>/`:
- Use `Glob` or `ls` to enumerate top-level dirs (`app/`, `src/`, `tests/`, `templates/`, `static/`, `migrations/`, `docker/`, `db/`, etc.) and their top-level files.
- Count files per top-level dir for a "size at a glance" sense.

**Audit log entries for this slug:**
- `python3 scripts/audit_log.py list --type build-milestone 2>/dev/null | grep -i "<slug>"` for build milestones.
- `python3 scripts/audit_log.py list --type rework-applied 2>/dev/null | grep -i "<slug>"` for reworks.
- `python3 scripts/audit_log.py list --type consolidation-applied 2>/dev/null | grep -i "<slug>"` for consolidations.

### Synthesize

Produce a structured report. Use this exact shape so the output is scannable:

```markdown
# Recollect: <slug>

**Stack:** <web | mobile | desktop>  •  **Run-id:** <run-id>  •  **Card status:** <value>

## One-liner
<the product's one-line description from the brief>

## Pipeline state

| Artifact | Path | Status | Last updated |
|---|---|---|---|
| Idea card | `ideas/<run-id>/<slug>.md` | <status> | <date> |
| Validation report | `market-research/<run-id>/validation-<slug>.md` | <decision> | <date> |
| Scoping report (MVP) | `market-research/<run-id>/scoping-<slug>.md` | <decision> | <date> |
| MVP brief | `<product-folder>/MVP.md` | <status> | <date> |
| Design research | `<product-folder>/design/DESIGN_RESEARCH.md` | <status or "not run"> | <date> |
| Design spec (claude-led) | `<product-folder>/design/DESIGN_SPEC.md` | <status or "not run"> | <date> |
| Design brief (hired) | `<product-folder>/design/DESIGN_BRIEF.md` | <status or "not run"> | <date> |
| Designer handoff | `<product-folder>/design/handoff/` | <present or "not received"> | <date> |
| V1 brief | `<product-folder>/V1.md` | <status or "not scoped"> | <date> |
| V1 scoping report | `market-research/<run-id>/scoping-v1-<slug>.md` | <decision> | <date> |
| BUILD_STATUS.md | `<product-folder>/BUILD_STATUS.md` | <build-status frontmatter or "not started"> | <date> |
| Infra cost estimate | `<product-folder>/INFRA_COST.md` | <present or "not run"> | <date> |

*(Omit rows for artifacts that don't exist — keep the table dense.)*

## Build progress (if BUILD_STATUS.md exists)

**Phase:** <building / rework-in-progress / ready-to-deploy / shipped>
**Design path:** `<claude-led | hired | hybrid-light-refresh | claude-led-continued | pro-designer-engaged>`
**Completed subsystems:** <count> / <total>
**In-progress (`[>]`):** <names>
**Next pending (`[ ]`):** <first 2-3 names>

**Most recent History entry:** <date> — <one-line summary>

## Source tree at a glance

```
<product-folder>/
├── app/        (N files)
├── tests/      (N files)
├── templates/  (N files)
├── static/     (N files)
├── migrations/ (N files)
└── ...
```

## Team

| Role | Name |
|---|---|
| Senior Software Engineer (orchestrator) | <name or "unnamed"> |
| Senior System-Design Engineer | <name or "unnamed"> |
| ... <only show roles that are named OR fold all unnamed into a single "Others (unnamed): N" row> |

## Recent audit-log activity (this product)

- <date> — <type> — <description>
- ... (max 5 most recent entries)

## Synthesis

<2-4 sentences in plain prose: what this product is, where it is in the pipeline, what's the most important next decision. Reference specific files and statuses. Avoid generic language ("the project is making progress" — bad; "MVP is green-lit-to-build with claude-led design path, DESIGN_SPEC.md not yet written, build hasn't started" — good).>

## Suggested next actions (2-4)

1. **<command>** — <one-line why this is the natural next>
2. **<command>** — <one-line why>
3. **<command>** — <one-line why>

*(Rank by what would unblock the most downstream work. If the user is mid-build, `/continue-build <slug>` is usually #1. If design is missing and `design-path: claude-led`, `/research-design <slug>` is usually #1. Be specific to the actual state, not boilerplate.)*
```

### Stop

After producing the synthesis, **stop**. Do not auto-invoke any suggested command. Wait for the user to pick one. This command is orientation, not action.

### Notes

- **Pure read-only.** This command never invokes a subagent, never modifies a file, never appends to the audit log. It can be safely run at any time, as many times as the user wants.
- **No team-naming prompt.** Just read what `team.json` says; if a member is unnamed, list as "unnamed" — don't prompt.
- **Output stays in the terminal — no file written.** The synthesis is for the moment; if the user wants a permanent record, they can scroll up or run `/recollect <slug>` again later (state may have changed).
- **For products where the build hasn't started**, the build-progress section is omitted entirely; the source-tree section will be minimal or absent.
- **Multi-product reminder:** for an across-all-products snapshot, use `/status` (which reports across the whole workspace). `/recollect <slug>` is the single-product deep-dive.
