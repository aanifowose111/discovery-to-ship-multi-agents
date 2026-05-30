---
description: Show a complete snapshot of pipeline state — active scan, all active and in-flight artifacts with their statuses and ages, latest trend report, and recent activity. Deeper than /menu (which prioritizes the menu over the state). Use when you want to know "where am I" across all in-flight work.
---

You are surfacing a complete pipeline-state snapshot. This is deeper than `/menu` (which focuses on the command menu). The user has run this to get the full picture before deciding what to do.

### Read state from disk (do not modify anything)

#### Market research artifacts

```bash
ls -lt market-research/ 2>/dev/null | head -20
```

Identify:
- Latest **scan** (`scan-*.md`) — read its frontmatter, note `status` (draft / active) and date.
- Latest **triage list** (`triage-*.md`) — date and count of cards.
- All **validation reports** (`validation-*.md`) — for each, note `slug`, date, decision (from the *Decision* section).
- All **scoping reports** (`scoping-*.md`) — for each, note `slug`, date, decision.
- Latest **trend report** (`trends-*.md`) — date, sweep-type, material findings count.

#### Active idea cards

```bash
find ideas -maxdepth 1 -name '*.md' -not -name 'README.md' 2>/dev/null
```

For each card, read frontmatter and note: `slug`, `status` (draft / triaged / in-validation / green-lit / killed — though killed should be in `ideas/killed/`), `date-captured`.

#### Killed cards (count + recency)

```bash
ls ideas/killed/*.md 2>/dev/null | wc -l
ls -t ideas/killed/*.md 2>/dev/null | head -3
```

Note count + most-recent 3 (slug + date killed).

#### In-flight briefs

```bash
find web-apps mobile-apps -maxdepth 2 -name 'MVP.md' 2>/dev/null
```

For each brief, read frontmatter and note: `slug`, `domain`, `status`, `design-path` (if set), `build-support` (if set), `target-ship-date`.

#### Active design phases

```bash
find web-apps mobile-apps -maxdepth 3 -type d -name 'design' 2>/dev/null
```

For each design folder, list what's present:
- `DESIGN_RESEARCH.md` (note `status`)
- `DESIGN_BRIEF.md` (note `status`)
- `figma/README.md` (Figma file linked?)
- `handoff/` contents (tokens.json present? screenshots present?)

#### Recent doc-export outputs

```bash
ls -lt generated/*/*.{pdf,docx} 2>/dev/null | head -5
```

Just the 3-5 most recent generated artifacts (path + date).

### Output format

Print a clean structured snapshot. Use this layout:

```
=== Pipeline State Snapshot — <today's date> ===

📊 MARKET RESEARCH
  Active scan:     scan-2026-05-29.md (5 territories, status: active)
  Latest triage:   triage-2026-06-01.md (12 cards, 4 green / 5 yellow / 3 red)
  Latest trends:   trends-2026-06-15.md (4 days old, 1 material finding)

💡 ACTIVE CARDS (in ideas/)
  • findvil-redux        status: in-validation    age: 12 days
  • dev-task-tracker     status: green-lit        age:  3 days

⚰️ KILLED CARDS (in ideas/killed/)
  3 total; most recent:
  • payment-forms      killed 2026-05-29
  • zoom-clone         killed 2026-06-10
  • another-todo-app   killed 2026-06-14

🛠️ IN-FLIGHT BRIEFS
  • dev-task-tracker (web)
    status: green-lit-to-build
    design-path: generic
    build-support: self
    target ship: 2026-06-30

🎨 ACTIVE DESIGN PHASES
  (none, or list them with their state)

📄 RECENT GENERATED DOCS
  • generated/briefs/2026-06-12-dev-task-tracker-mvp-brief.pdf  (3 days ago)
  • generated/reports/2026-05-29-payment-forms-validation-report.pdf  (17 days ago)

=== Suggested next actions ===

  Based on this state, plausible next steps:
  
  1. <specific action with reasoning, e.g., "Finish validating findvil-redux — it's been
     in-validation for 12 days. Run `/validate-card findvil-redux` to invoke the remaining
     reviewers.">
  2. <another action>
  3. <another action>

  Or run /menu for a full command menu.
```

### Rules

- **Read-only.** Never modify any file in this command.
- **Show what's there; don't infer too aggressively.** If a brief's frontmatter doesn't have `design-path` set, just omit that line — don't guess.
- **If the workspace is empty** (fresh clone, no ideas yet), say so cleanly:
  > Pipeline state: empty. You're on a fresh start.
  > Suggested next action: `/discover` (one-command bootstrap, no setup required) or `/scan` for a deliberate territory map first.
- **Surface 2-4 next-action suggestions**, prioritized by what's most stuck (oldest in-flight artifact) or most actionable (recent material trend finding).
