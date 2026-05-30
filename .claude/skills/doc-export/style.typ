// Styling overlay for discovery-to-ship-multi-agents PDF exports via pandoc + typst.
// Injected via pandoc's --include-in-header on top of pandoc's default typst template,
// so all helper definitions (horizontalrule, terms.item, etc.) are inherited.
//
// Visual goals:
//   - White background, clean reading column.
//   - Light navy (#1e3a8a) for headings and link accents.
//   - Bold titles, well-organized sections.
//   - Modern serif body + clean sans headings.
//   - Subtle slate borders for tables; slate-tinted block for code.
//
// Fonts are specified as fallback chains so the same template works on
// macOS, Linux (with Liberation/DejaVu), and most Linux distros.

#set page(
  paper: "us-letter",
  margin: (x: 1.5cm, y: 2cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: ("Charter", "Georgia", "Cambria", "Liberation Serif", "DejaVu Serif"),
  size: 11pt,
  lang: "en",
  hyphenate: false,
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 0pt,
)

// Headings — light navy accent, clean sans-serif.
#show heading.where(level: 1): it => {
  set text(
    font: ("Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"),
    size: 22pt,
    weight: "bold",
    fill: rgb("#1e3a8a"),
  )
  block(above: 1.5em, below: 0.8em)[#it.body]
}
#show heading.where(level: 2): it => {
  set text(
    font: ("Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"),
    size: 16pt,
    weight: "bold",
    fill: rgb("#1e3a8a"),
  )
  block(above: 1.2em, below: 0.6em)[#it.body]
}
#show heading.where(level: 3): it => {
  set text(
    font: ("Helvetica Neue", "Helvetica", "Arial", "Liberation Sans", "DejaVu Sans"),
    size: 13pt,
    weight: "bold",
    fill: rgb("#334155"),
  )
  block(above: 1em, below: 0.5em)[#it.body]
}
#show heading.where(level: 4): it => {
  set text(weight: "bold", fill: rgb("#334155"))
  block(above: 0.8em, below: 0.4em)[#it.body]
}

// Links — navy with subtle underline.
#show link: it => text(fill: rgb("#1e3a8a"))[#underline(it)]

// Code — smaller, monospace, slate-tinted background for blocks.
#show raw: set text(
  font: ("Menlo", "Monaco", "Consolas", "JetBrains Mono", "DejaVu Sans Mono"),
  size: 9.5pt,
)
#show raw.where(block: true): it => block(
  fill: rgb("#f1f5f9"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[#it]

// Tables — slate borders, comfortable padding.
#show table: set table(
  stroke: 0.5pt + rgb("#cbd5e1"),
  inset: 8pt,
)
