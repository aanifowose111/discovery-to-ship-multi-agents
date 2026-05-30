# ideas/

Your idea cards from discovery cycles live here. **This folder is gitignored** (except this README) — your idea pipeline is personal and never enters git.

## Convention

Per `guides/product/idea-discovery-methodology.md`, each idea card is a markdown file at `ideas/<slug>.md` with YAML frontmatter and the card sections defined in §4 of that guide.

Killed cards go to `ideas/killed/<slug>.md` with a one-line reason in the card.

```
ideas/
├── README.md            (tracked — this file)
├── <active-slug>.md     (gitignored)
├── <another-slug>.md    (gitignored)
└── killed/
    └── <slug>.md        (gitignored)
```

## Lifecycle

- `status: draft` → just captured
- `status: triaged` → scored on the §5 rubric, bucketed green / yellow / red
- `status: in-validation` → being reviewed by the three product reviewers
- `status: green-lit` → all three reviewers + user sign-off; ready for `/scope-mvp`
- `status: killed` → moved to `ideas/killed/` with reason

## Commands

- `/discover` — brainstorms and writes new cards here, then triages them.
- `/validate-card <slug>` — invokes the three product reviewers on a card.
- See `CLAUDE.md`'s "Pipeline orchestration & checkpoints" for the full flow.
