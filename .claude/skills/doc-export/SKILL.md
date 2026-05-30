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

**Always offer both options unless the user explicitly stated PDF or DOCX.** Default behavior is to ask:

> Output format — PDF or DOCX? (PDF gets the workspace's styled template — Charter body, Helvetica Neue navy headings; DOCX uses pandoc defaults which work cleanly in Word / Google Docs.)

If they said "PDF" or "DOCX" explicitly in their request, skip the ask and use it.

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

**PDF (default — typst + workspace styling overlay):**
```bash
pandoc <source.md> -o <output.pdf> \
  --pdf-engine=typst \
  --include-in-header=.claude/skills/doc-export/style.typ \
  --metadata title="<sensible title from source frontmatter or filename>" \
  --metadata date="<source artifact date if available>"
```

The `style.typ` overlay (kept in this skill folder) applies the workspace's visual identity:
- Charter body text + Helvetica Neue light-navy (`#1e3a8a`) headings on macOS; Liberation Serif / Liberation Sans fallbacks for Linux.
- Subtle slate borders on tables, slate-tinted code blocks.
- Justified paragraphs with comfortable leading.
- Centered page numbers.

You may see typst warnings about unavailable fonts (the fallback chain includes fonts for Linux that don't exist on macOS, and vice versa). These are non-fatal — typst silently picks the first available font in the chain. **Filter them out of the user-facing output** by appending `2>/dev/null` or `2>&1 | grep -v "unknown font family"` to the pandoc command:

```bash
pandoc ... 2>&1 | grep -v "unknown font family" 1>&2
```

**PDF (alternative — tectonic, if typst doesn't render something correctly):**
```bash
pandoc <source.md> -o <output.pdf> \
  --pdf-engine=tectonic \
  -V geometry:margin=1in \
  --metadata title="<sensible title>"
```

Tectonic does not use the typst styling overlay — it produces standard LaTeX output. Use only if typst fails for a specific document.

**DOCX:**
```bash
pandoc <source.md> -o <output.docx> \
  --metadata title="<sensible title>"
```

DOCX uses pandoc's default styles (no custom styling overlay — Word / Google Docs handle styling on their end via the document's built-in styles, which the user can adjust after open).

For documents with a lot of code blocks, also pass `--highlight-style=tango` (PDF) for nicer code-block syntax highlighting.

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
  --include-in-header=.claude/skills/doc-export/style.typ \
  --metadata title="Findvil — MVP Brief" \
  --metadata date="2026-05-29" \
  2>&1 | grep -v "unknown font family" 1>&2
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
  --include-in-header=.claude/skills/doc-export/style.typ \
  --metadata title="Findvil — Design Brief" \
  --metadata date="2026-05-29" \
  2>&1 | grep -v "unknown font family" 1>&2
```

## Common gotchas

- **Frontmatter rendering.** Pandoc treats YAML frontmatter as document metadata, not body content. If the user wants the frontmatter visible in the output, either pass `--include-in-header` with a custom snippet or convert it to a body table before exporting.
- **Image paths.** Markdown image references resolve relative to the source file. If a PDF render shows broken images, run pandoc from the source file's directory: `cd <source-dir> && pandoc <file.md> -o <abs-output-path>`.
- **`generated/` is project-relative.** Always run from the workspace root (`~/Desktop/agents`), not from a subfolder.
