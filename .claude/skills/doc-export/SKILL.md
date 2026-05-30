---
name: doc-export
description: Exports any markdown artifact in this workspace (MVP brief, validation report, design brief, scan/trend report, etc.) to PDF or DOCX via pandoc, dropping the output in `generated/<category>/` with a date-stamped name. Use when the user asks to "export this as PDF", "generate a docx of the brief", "give me a PDF of the validation report", or otherwise wants a downloadable/shareable version of a markdown file.
---

# Doc Export

Convert any markdown artifact in this workspace into PDF or DOCX, with a consistent file name and location so the export is findable later.

## When to Use

- User asks to "export," "generate," or "give me a PDF/DOCX of" a markdown file.
- User wants a shareable version of a brief, report, or other artifact (for a designer, investor, advisor, or any external party who isn't in this repo).

## When NOT to Use

- The user wants to *edit* the artifact — markdown is the editing source; PDF/DOCX are export targets.
- The user wants to convert source files between unrelated formats (use pandoc directly).

## Prerequisites

**Pandoc** is required. Check:

```bash
which pandoc
```

If missing, tell the user:

> Pandoc is required for this skill. Install with `brew install pandoc` (macOS) or per https://pandoc.org/installing.html. Re-run once installed.

**For PDF output**, a PDF engine is also required. Default to **typst** (modern, fast, lightweight):

```bash
which typst
```

If missing, tell the user:

> typst is required for PDF output. Install with `brew install typst`. Alternative: `brew install tectonic` (LaTeX-based, larger but mature).

> Note: wkhtmltopdf was the previous recommendation but Homebrew removed it after the upstream project was archived in 2023. typst is the modern replacement.

## Process

### 1. Identify the source markdown file

Either the user named it explicitly, or it's the artifact under discussion. If ambiguous, ask before proceeding.

### 2. Identify the output format

Default to PDF unless the user specified DOCX. If unclear, ask: "PDF or DOCX?"

### 3. Determine the output category

| Source type | Category folder |
|---|---|
| MVP brief, design brief, funding decision | `briefs/` |
| Validation, scoping, scan, trend reports | `reports/` |
| Design research, design handoff notes | `design-docs/` |
| Anything else | `misc/` |

### 4. Build the output path

`generated/<category>/<YYYY-MM-DD>-<slug-or-area>-<doc-type>.<ext>`

- `<YYYY-MM-DD>` — today's date (the date generated, not the date of the source artifact).
- `<slug-or-area>` — product slug if applicable (e.g., `findvil`), or area name for cross-product artifacts (e.g., `market-research`).
- `<doc-type>` — short identifier matching the source's role: `mvp-brief`, `design-brief`, `design-research`, `funding-decision`, `validation-report`, `scoping-report`, `scan-<date>`, `trends-<date>`, etc.

Example: `generated/briefs/2026-05-29-findvil-mvp-brief.pdf`.

### 5. Ensure the category folder exists

```bash
mkdir -p generated/<category>
```

### 6. Run pandoc

**PDF (default — typst):**
```bash
pandoc <source.md> -o <output.pdf> \
  --pdf-engine=typst \
  --metadata title="<sensible title from source frontmatter or filename>"
```

**PDF (alternative — tectonic, if typst doesn't render something correctly):**
```bash
pandoc <source.md> -o <output.pdf> \
  --pdf-engine=tectonic \
  -V geometry:margin=1in \
  --metadata title="<sensible title>"
```

**DOCX:**
```bash
pandoc <source.md> -o <output.docx> \
  --metadata title="<sensible title>"
```

For documents with a lot of code blocks or tables, also pass `--highlight-style=tango` (PDF) or use the default styles (DOCX).

### 7. Verify and report

Confirm the file exists, report its path and size:

```bash
ls -lh <output-path>
```

Tell the user:

> Exported to `<output-path>` (`<size>`). Open it with `open <output-path>`.

## Examples

**"Export the findvil MVP brief as PDF"**

```bash
mkdir -p generated/briefs
pandoc web-apps/findvil/MVP.md \
  -o generated/briefs/2026-05-29-findvil-mvp-brief.pdf \
  --pdf-engine=typst \
  --metadata title="Findvil — MVP Brief"
```

**"Generate a docx of the latest scan"**

```bash
mkdir -p generated/reports
pandoc market-research/scan-2026-05-29.md \
  -o generated/reports/2026-05-29-market-research-scan-2026-05-29.docx \
  --metadata title="Market scan — 2026-05-29"
```

**"Give me a PDF of the design brief for findvil"**

```bash
mkdir -p generated/briefs
pandoc web-apps/findvil/design/DESIGN_BRIEF.md \
  -o generated/briefs/2026-05-29-findvil-design-brief.pdf \
  --pdf-engine=typst \
  --metadata title="Findvil — Design Brief"
```

## Common gotchas

- **Frontmatter rendering.** Pandoc treats YAML frontmatter as document metadata, not body content. If the user wants the frontmatter visible in the output, either pass `--include-in-header` with a custom snippet or convert it to a body table before exporting.
- **Image paths.** Markdown image references resolve relative to the source file. If a PDF render shows broken images, run pandoc from the source file's directory: `cd <source-dir> && pandoc <file.md> -o <abs-output-path>`.
- **`generated/` is project-relative.** Always run from the workspace root (`~/Desktop/agents`), not from a subfolder.
