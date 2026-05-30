# Custom slash commands

Each `.md` file in this folder defines one custom slash command for this project. Drop a file here named `foo.md` and Claude Code will expose it as `/foo` in the prompt.

## File format

Each command file is markdown with optional YAML frontmatter:

```markdown
---
description: One-line summary of what this command does (shown in the slash-command menu).
argument-hint: <optional placeholder text shown after the command name, e.g. "<topic>">
---

The body is the prompt that Claude receives when the command is invoked.
Use `$ARGUMENTS` to interpolate whatever the user typed after the command name.
You can reference other files with @relative/path/to/file.md so Claude reads them as context.
```

## Conventions for this project

- **Kebab-case filenames** (`research-idea.md`, not `ResearchIdea.md` or `research_idea.md`).
- **One responsibility per command.** If a command is doing two unrelated things, split it.
- **Reference, don't duplicate.** If a command needs a guide or skill that already exists in this repo, `@`-reference it from the command body rather than copy-pasting the content.
- **Update the index in `CLAUDE.md`** every time a command is added, renamed, or removed, so future sessions can see what is available without scanning this folder.

## When to create a command vs. an assistant vs. a skill

- **Slash command** → a one-shot prompt the user wants to fire repeatedly with consistent framing (e.g., `/validate-idea`, `/market-scan`).
- **Skill** → a reusable capability that Claude itself decides when to invoke; lives under the skills folder (to be set up).
- **Assistant (subagent)** → an independent reviewer/worker with its own context, used for things like reviewing a draft without polluting the main conversation.

When the user asks for a new "thing to run", confirm which of these three it is before creating it.
