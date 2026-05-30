# Contributing to discovery-to-ship-multi-agents

Thanks for considering a contribution. This guide is the **single source of truth** for what to change, what *not* to change, how to test changes, and how to submit a PR.

If you're using the workspace for your own products and just want to extend it for your own purposes (without contributing back), you don't need to read this — your changes never leave your fork. This guide is for people who want their changes to land in the upstream repo.

---

## Project philosophy (the lens behind "what to change")

Three principles inform every design decision in this workspace. Contributions should respect them or argue convincingly for why they shouldn't:

1. **Methodologies are stack-agnostic; build guides are stack-specific.** The discovery, validation, scoping, design, market-research, and funding methodologies work for any web/mobile stack. The build-domain guides (Flask, RN, EAS) are workspace defaults and live under explicit stack-specific filenames. Don't blend the two — don't bake Flask assumptions into the discovery methodology, and don't make a Flask scaffold guide claim stack-agnosticism.
2. **One source of truth per concept.** When a fact or convention is documented in one place (e.g., the verdict format in `idea-validation-methodology.md` §5), other documents reference it rather than restating it. This keeps the workspace consistent as it evolves.
3. **The user signs off on non-basic outputs.** Reviewers don't advance artifact status; slash commands don't auto-invoke the next phase; the design-fidelity reviewer doesn't accept a Figma on its own. Contributions must respect the checkpoint discipline — see `CLAUDE.md` "Pipeline orchestration & checkpoints" for the canonical list of user checkpoints.

---

## Before you start

### 1. Use Claude Code to edit this repo

This workspace is **designed to be edited through Claude Code**. The CLAUDE.md file (auto-loaded at the start of every Claude Code session in this directory) contains conventions, the required-updates matrix, and the acknowledgment check that keeps changes coherent. Editing files with other tools (vim, VSCode, the GitHub web UI) bypasses those checks — your changes may inadvertently break conventions documented in this file.

**If you must edit outside Claude Code** (you don't have it installed, you're doing a quick typo fix in the GitHub UI, etc.), be especially careful about the *Required updates* matrix in §"Required updates when you make a change" — Claude usually applies that matrix for you, and without it you'll need to do the cross-reference updates by hand.

### 2. Acknowledge you've read this guide (`CONTRIBUTING.md`)

Before you edit any **tracked file** in this repo for the first time, run inside Claude Code:

```
/acknowledge-contributing
```

It will:
- Detect if you're the repo owner (`aanifowose111@gmail.com`) — if so, skip the rest.
- Otherwise, ask you to type a specific confirmation phrase that proves you've read this file.
- Create a `.claude-acknowledged` marker (gitignored, per-clone, per-machine).

After acknowledgment, Claude will help you edit tracked files normally. **Personal-data folders** (`ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `generated/`) are gitignored and never require acknowledgment — you can work on your own product ideas without going through this.

This is a Claude-side convention. Direct file edits outside Claude Code bypass it. It exists to make sure contributors have seen these rules before changes propose to land upstream — not as a security boundary.

### 3. For non-trivial changes, email first

📧 Email **aanifowose111@gmail.com** with a one-paragraph description of what you want to change and why. Subject line `[discovery-to-ship contribution]`.

This avoids:
- Two people working on the same problem in parallel.
- A PR that solves a real problem in a way that doesn't fit the project philosophy.
- Wasted time on changes that won't be accepted.

"Non-trivial" means anything beyond: typo fixes, broken-link fixes, obviously-wrong examples, formatting cleanups. If unsure, email first.

---

## What to change vs. what NOT to change

### ✅ Welcome contributions

- **Bug fixes** in existing methodologies, slash commands, or reviewers — when a documented behavior doesn't match the actual behavior, or when an example is wrong.
- **New stack-specific build guides** for stacks the workspace doesn't currently cover (e.g., `guides/web/nextjs-mvp-scaffold.md`, `guides/mobile/swift-mvp-scaffold.md`). Follow the structure of the existing guides; mark clearly as workspace alternatives, not replacements.
- **New methodology guides** for domains the workspace doesn't currently cover (e.g., a `guides/legal/` for contract review, a `guides/sales/` for B2B outreach). Methodology guides must be stack-agnostic.
- **New reviewer / worker subagents** for narrow lenses we don't currently cover (e.g., a `regulatory-compliance-reviewer` for health/fintech products). Use the locked verdict format and the persona-file pattern.
- **New helper skills** that automate recurring workspace operations (e.g., a `git-cleanup` skill, a `dependency-audit` skill).
- **Methodology improvements** — better evidence standards, sharper failure-mode catches, additional rationalizations-to-refuse — in any existing guide or reviewer.
- **Editorial improvements** — clearer prose, better examples, missing cross-references.

### ❌ Discouraged / will likely be rejected

- **Changing workspace defaults** (Flask, RN, DO, MIT license, etc.) without first discussing in an issue or email. These reflect the maintainer's deliberate choices.
- **Adding heavyweight dependencies** to existing skills, commands, or guides without a strong justification. The workspace deliberately leans on simple tooling (pandoc, typst, ruff, gunicorn, Caddy) over complex frameworks.
- **Duplicating functionality that the agent-skills submodule already provides.** If a `code-reviewer`, `security-auditor`, `test-engineer`, `idea-refine`, `interview-me`, `spec-driven-development`, etc. already exists upstream, contribute there, not here.
- **Removing the user checkpoints.** Slash commands must stop at their checkpoints; reviewers must not auto-advance artifact status; design-fidelity must not accept Figma without user sign-off. These are non-negotiable.
- **Bypassing the custom-subagent invocation pattern.** New slash commands that invoke custom subagents must use the pattern in `CLAUDE.md` "Invoking custom subagents — the universal pattern" (call `general-purpose` with the persona file referenced). Don't try to call custom subagent types directly.
- **Committing personal data.** The `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `generated/` folders are gitignored for a reason. Never commit your own ideas, validation reports, or product code to *this* repo. (Use a separate private repo for your own products.)
- **Editing CLAUDE.md as if it were yours.** The CLAUDE.md in this repo represents the maintainer's preferences (Flask, RN, DO, founder context). Forkers who want different defaults edit their *fork's* CLAUDE.md, not the upstream one.

---

## Required updates when you make a change

When you add or modify something, update **all** the places that reference it so the workspace stays internally consistent.

| If you change... | You must also update... |
|---|---|
| **A slash command** | `CLAUDE.md` commands index; `README.md` slash-commands table; `HELP.md` `## 2. All slash commands` section. |
| **A reviewer or worker subagent** (`.claude/agents/`) | `CLAUDE.md` folder-map note about `.claude/agents/`; `HELP.md` `## 4. Reviewer and worker subagents` table. If the verdict format changes, also update `guides/product/idea-validation-methodology.md` §5 (the canonical format) AND every other reviewer's output-format section. |
| **A skill** (`.claude/skills/`) | `CLAUDE.md` skills index; `README.md` helper-skills table; `HELP.md` `## 3. Skills` section. |
| **A methodology guide** | `CLAUDE.md` guides index; cross-references in other guides that link to the changed one (use `grep` to find them). |
| **Pipeline orchestration** (which command leads to which checkpoint to which next command) | `CLAUDE.md` "Pipeline orchestration & checkpoints" section is the canonical source of truth; every other reference must match. |
| **The internet access policy** | `CLAUDE.md` "Internet access policy" section; `HELP.md` `## 9` quick reference; `.claude/settings.json` if tool-allowance changes. |
| **The stack-flexibility framing** | `CLAUDE.md` "Stack flexibility" bullet; `README.md` "Stack flexibility" section; `HELP.md` `## 8` quick reference; `guides/product/mvp-scoping-methodology.md` §6.0; `/scope-mvp` command's stack-confirmation prompt. |
| **The gitignored personal-data folders** | `.gitignore`; each folder's `README.md`; `CLAUDE.md` folder map; `README.md` "Repository layout" + "Personal vs. shared" sections. |
| **Anything contributor-facing** | This file (`CONTRIBUTING.md`) plus `README.md` "How to contribute" section. |

If you change something that has cross-references and you're not sure where they all are, `git grep -l '<term>'` will help. Update everything that matches.

---

## What you should NOT update

- **The license** (`LICENSE` is MIT) — proposing a license change requires a discussion, not a PR.
- **The maintainer's contact info** (`aanifowose111@gmail.com`) — proposing a contact change requires a discussion.
- **CLAUDE.md's founder-context bullets** (mentions of findvil, fijara, Mercor, Abiodun's prior shipped projects). These represent the maintainer; they're not generic project facts.
- **MEMORY.md** — this is the maintainer's auto-memory directory pointer and accumulated content. Forkers have their own.
- **The agent-skills submodule reference** (the SHA in the git submodule index) — unless your PR is specifically to update the submodule, leave it alone.
- **Anyone else's personal data** — if you discover an `ideas/<slug>.md` or similar in your local clone (perhaps left over from your own use), do *not* commit it. The `.gitignore` should prevent this; if `git status` shows personal data as tracked, fix the `.gitignore` rather than removing the data manually.

---

## Style and conventions

### Markdown

- **One H1 per file** (the title). Use H2-H6 for nesting.
- **Code fences** must specify the language: `` ```python ``, `` ```bash ``, `` ```jsonc ``. Bare `` ``` `` only for plain text.
- **Tables** are preferred over bulleted lists when the content has 3+ parallel attributes.
- **Cross-references** to other files use relative paths in backticks (e.g., `` `guides/product/idea-validation-methodology.md` ``) or proper markdown links if user-clickable context matters (e.g., the README and HELP).
- **Frontmatter** in YAML, at the top of files that need it (subagent personas, slash commands, idea cards). Required fields are defined per file type.

### Reviewer / worker personas

- Always use the locked verdict format from `guides/product/idea-validation-methodology.md` §5 for outputs (verdict / confidence / findings / what-I-could-not-verify / sources). Single source of truth.
- Persona instructions follow the structure of existing reviewers: role/lens, inputs, process, evidence standards, common rationalizations to refuse, red-flag REJECT rules, output format, composition.
- The persona's `description` field (in YAML frontmatter) is what Claude Code uses to decide when to invoke it. Be specific about the lens.

### Slash commands

- Always reference the custom-subagent invocation pattern in `CLAUDE.md` when calling custom subagents — don't reinvent it.
- Always stop at a user checkpoint with a clear "Your call:" menu and "Next:" pointers.
- Include pre-flight checks for required inputs (existing files, valid statuses) before doing work.
- `argument-hint` should be a one-line example, e.g., `<product-slug>` or `[broad|focused <topic>]`.

### Commit messages

- One-line summary in imperative mood ("Add foo," not "Added foo" or "Adds foo"). 50 chars or less.
- Blank line.
- Body explaining *why* the change is needed and what the impact is. Wrap at 72 chars. Reference issues or email discussions if applicable.

Example:

```
Add nextjs-mvp-scaffold guide

The current workspace ships Flask as the web default. This guide adds
parallel coverage for Next.js (TypeScript + App Router + Vercel) for
forkers who want a JS-stack alternative without writing one from scratch.

Per CLAUDE.md stack-flexibility framing, this is an alternative, not a
replacement. mvp-scoping-methodology.md §6.0 now lists Next.js as a
named option with this guide as the implementation reference.

Discussed via email 2026-06-01.
```

---

## Testing your changes locally

Before opening a PR:

1. **For new guides:** read through your guide in a fresh Claude Code session and verify the cross-references work (`@guides/<your-guide>.md` should resolve, references inside the guide should point to real files).
2. **For new slash commands:** type `/<your-command>` in Claude Code with a realistic argument and verify it behaves per its description. Check the checkpoint message is clear.
3. **For new reviewers:** create a synthetic test artifact, invoke the reviewer via the workaround pattern (`general-purpose` + persona file), confirm the verdict format is correct and the lens stays narrow.
4. **For new skills:** trigger the skill via its declared trigger phrases and confirm it does what the description says.
5. **For doc changes:** `git diff` your change, re-read it as a fresh reader, ask whether the prose is sharper than what it replaced.
6. **For any change:** confirm `git status` does not show any personal data being staged.

---

## Submitting a PR

1. Push your feature branch to your fork.
2. Open a PR on GitHub from your fork's branch into `aanifowose111/discovery-to-ship-multi-agents:main`.
3. PR title: same style as commit message (imperative, under ~70 chars).
4. PR description:
   - **What** the change does (1-3 sentences).
   - **Why** (link to email thread or issue if applicable; otherwise explain the motivation).
   - **What was updated** (per the matrix in §"Required updates when you make a change").
   - **Testing** done (per §"Testing your changes locally").
   - **Breaking changes** (if any) — explicit list.
5. Be patient. The maintainer reviews on a best-effort basis. Substantive PRs typically get a first response within a week.

---

## Code of conduct (brief)

Be kind. Disagree with the change, not the person. Assume good intent. If a PR is closed without merge, it's usually a fit-for-the-project issue, not a quality issue — the reasoning should be in the closing comment. If it isn't, ask.

---

## Questions

Email **aanifowose111@gmail.com** with subject line `[discovery-to-ship contribution]`.
