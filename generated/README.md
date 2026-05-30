# generated/

Date-stamped exports of project artifacts to PDF / DOCX via the `doc-export` skill. These are **outputs** — derived from the markdown sources elsewhere in the repo:

- Regeneratable at any time from source.
- Not a source of truth.
- Treated as artifacts, not as edit targets.

## Folder structure

```
generated/
├── briefs/        MVP briefs, design briefs, funding decisions
├── reports/       Validation, scoping, scan, trend reports
├── design-docs/   Design research, handoff documents
└── misc/          One-off exports
```

Subfolders are created on first use; do not pre-create empty ones.

## Naming convention

`<YYYY-MM-DD>-<slug-or-area>-<doc-type>.<ext>`

- **`YYYY-MM-DD`** — date generated (not the source artifact's date).
- **`slug-or-area`** — product slug (e.g., `findvil`) or area name for cross-product artifacts (e.g., `market-research`).
- **`doc-type`** — short identifier: `mvp-brief`, `design-brief`, `design-research`, `funding-decision`, `validation-report`, `scoping-report`, `scan-<date>`, `trends-<date>`, etc.

Examples:

- `briefs/2026-05-29-findvil-mvp-brief.pdf`
- `briefs/2026-06-01-findvil-design-brief.pdf`
- `reports/2026-05-29-market-research-scan-2026-05-29.docx`
- `design-docs/2026-06-01-findvil-design-research.pdf`

## Generation

Use the `doc-export` skill. Trigger phrases: "export this as PDF", "generate a docx of [artifact]", "give me a PDF of [artifact]". The skill picks the right category folder and runs pandoc with consistent settings.

## Committing exports

Whether to commit exports to git is a project-level call. Defaults:

- **Commit** when the export is being sent to an external party for review (a design brief PDF that goes to the designer); future references back to the document benefit from version history.
- **Gitignore** when exports proliferate (every iteration regenerated; only the latest matters); add `generated/**/*.pdf` and `generated/**/*.docx` to `.gitignore` in that case.

Default to commit-light: keep canonical / sent versions; let in-progress regenerations be ephemeral.
