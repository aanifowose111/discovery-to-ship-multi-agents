# Guides

Long-form reference documents for both the user and Claude. Unlike skills (which Claude auto-invokes) and assistants (which the main Claude delegates to), guides are **passive reference material** — read on demand, not auto-loaded.

Use guides for things that are too big for a skill body, too narrative for a slash command, or that the user wants to be able to read end-to-end themselves: architectural standards, vendor-specific runbooks, market-research methodology writeups, funding strategy playbooks, deployment checklists, etc.

## Folder layout

Organized by domain. Subfolders nest freely since guides are plain markdown and there is no auto-discovery to worry about.

```
guides/
├── web/         (web app development guides)
├── mobile/      (mobile app development guides)
├── product/    (product discovery/viability guides)
├── market/     (market research methodology, frameworks)
└── funding/    (funding strategy, pitch, reporting playbooks)
```

(Subfolders will be created as guides are written — no need to pre-create empty ones.)

## File format

Plain markdown. No required frontmatter. A short H1 title at the top is enough; deeper structure as needed.

## When to write a guide vs. a skill vs. an assistant vs. a command

- **Guide** → reference material humans and Claude read on demand. Long, narrative, evolves slowly.
- **Skill** → a reusable capability Claude can decide to invoke on its own; concise and action-oriented.
- **Assistant (subagent)** → an independent worker/reviewer with its own context window.
- **Slash command** → a one-shot prompt template the user fires repeatedly with consistent framing.

A guide and a skill can complement each other: the skill stays short and says *what to do*, and `@`-references the guide for the deeper context.

## Conventions for this project

- **One topic per guide.** A guide called `web-flask-everything.md` is a sign it should be three guides.
- **Cross-link** related guides with relative markdown links.
- **Date major revisions** at the bottom of the file when the underlying recommendation changes, so we can tell what is fresh.
- **Update the index in `CLAUDE.md`** when a guide is added or substantially restructured.
