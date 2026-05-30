---
description: Pre-flight verification for a new clone or new machine. Checks that all required tools are installed, the submodule is initialized, the agent-skills file copies are present in `.claude/agents/` and `.claude/skills/`, and git is configured. Surfaces a clear punch list of what's missing with exact install commands. Safe to run multiple times.
---

You are running the workspace setup verification. Your job is to **check every requirement, never modify anything**, and surface a clear punch list at the end with ✓ for passing checks and ✗ for failing ones (with exact install commands).

### Checks to run (in order)

Run each check via Bash and record the result. Do not stop on a failure — continue all checks so the user sees the full picture in one pass.

#### Tools

1. **git**: `which git && git --version | head -1`
2. **Claude Code CLI**: `which claude || echo "claude CLI not found"` — if Claude Code is running this command, it's installed (note that the `claude` binary is what runs the agent; if `which claude` fails but the agent works, that's fine — note both).
3. **GitHub CLI**: `which gh && gh --version | head -1`
4. **pandoc**: `which pandoc && pandoc --version | head -1`
5. **typst**: `which typst && typst --version`
6. **Python 3.11+**: `which python3 && python3 --version`
7. **Node 20+**: `which node && node --version` (only required if mobile work is planned; flag as optional otherwise)

For each missing tool, surface the install command:

| Tool | macOS install | Ubuntu / WSL install |
|---|---|---|
| git | comes with `xcode-select --install` | `sudo apt install git` |
| GitHub CLI | `brew install gh` | `sudo apt install gh` |
| pandoc | `brew install pandoc` | `sudo apt install pandoc` |
| typst | `brew install typst` | see https://github.com/typst/typst |
| Python 3.11+ | `brew install python@3.12` | `sudo apt install python3 python3-pip` |
| Node 20+ | `brew install node@20` | `curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash - && sudo apt install nodejs` |
| Claude Code | https://docs.claude.com/en/docs/claude-code/installation | same |

#### Git identity

```bash
git config user.email && git config user.name
```

If either is empty, flag and instruct:

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

#### GitHub authentication

```bash
gh auth status 2>&1 | head -5
```

If not logged in, instruct:

```bash
gh auth login
```

(See `README.md` § "Authenticate GitHub in the terminal" for the interactive flow.)

#### Repo state

1. **Submodule initialized?** `test -f external/agent-skills/agents/code-reviewer.md && echo "yes" || echo "no"`

   If "no", instruct: `git submodule update --init --recursive`

2. **Agent-skills persona file copies present?** Check each:
   ```bash
   for f in code-reviewer security-auditor test-engineer; do
     test -f .claude/agents/$f.md && test -s .claude/agents/$f.md && echo "$f.md: OK" || echo "$f.md: MISSING or EMPTY"
   done
   ```

   If missing or empty, instruct: `bash scripts/update-agent-skills.sh` to pull the submodule and re-copy the personas + skills.

3. **`.claude-acknowledged` exists?** `test -f .claude-acknowledged && echo "yes" || echo "no"`

   If "no" AND `git config user.email` is not the repo owner's (`aanifowose111@gmail.com`), instruct: `Run /acknowledge-contributing before editing tracked files.`

   If "no" AND user IS the owner, note: "You're the owner; acknowledgment is waived. No action needed."

#### Optional but useful

1. **wkhtmltopdf** (alternative to typst, no longer the default): `which wkhtmltopdf 2>/dev/null && echo "installed (note: deprecated; typst is now default)" || echo "not installed (typst is the default; this is fine)"`

2. **uv** (faster Python package manager, used in some scaffold guides): `which uv 2>/dev/null && echo "installed" || echo "not installed (optional)"`

### Output format

After running all checks, print a structured punch list:

```
=== discovery-to-ship-multi-agents — setup verification ===

REQUIRED TOOLS
  ✓ git 2.41.0
  ✓ Claude Code (running this command)
  ✓ gh 2.32.1
  ✓ pandoc 3.9.0
  ✓ typst 0.14.2
  ✓ python3 3.12.7
  ✓ node 20.18.0

GIT IDENTITY
  ✓ user.email: you@example.com
  ✓ user.name: Your Name

GITHUB AUTH
  ✓ Logged in to github.com account <your-account>

REPO STATE
  ✓ Submodule initialized (external/agent-skills/)
  ✓ All three agent-skills persona file copies present (code-reviewer, security-auditor, test-engineer)
  ✓ .claude-acknowledged on file (or: ⓘ Owner — acknowledgment waived)

VERDICT
  Ready to use. Try `/discover` or `/menu` to begin.

  Or if items are missing:

  X tools/checks failing. See above for install commands.
  Resolve them, then re-run /setup to confirm.
```

### Rules

- **Never modify anything** in this command — pure verification. Do not run `git submodule update --init` automatically, do not run `gh auth login` automatically, etc. Surface the problem; let the user act.
- **Always run every check** — don't short-circuit on a failure. The user wants the full picture.
- **Be honest about optional checks** — Node is only needed for mobile; uv is convenience only; wkhtmltopdf is deprecated.
