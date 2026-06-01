---
description: Check the host system against this workspace's hardware + tooling requirements. Shows a comparison table (required / recommended / your system / status) covering OS, CPU, RAM, disk, network, and required CLI tools. Pure read-only — no permissions needed.
argument-hint: (no arguments)
---

You are about to surface a system-spec comparison report — the user's machine versus what this workspace needs.

### Do

1. Run `python3 scripts/check_system.py` (no flags — let it render the colored table directly to the user).
2. After the script's output, add a brief plain-English summary based on what the table showed:
   - **All green (13/13 passed):** "Your system is well-matched to this workspace's needs. Nothing to do."
   - **Warnings only (no failures):** Name each warning row in 1-2 sentences and what it implies in practice (e.g., "8 GB RAM works for discovery + validation flows but will feel tight once Docker + the React Native bundler + a browser are all open during a build"). Don't lecture — the table already says what's what; just translate severity.
   - **Any failures:** Name each failing row and the most likely fix:
     - **Tool missing** → install command (`brew install <tool>` on macOS, `apt install <tool>` on Debian/Ubuntu, the language-specific installer for Node/Python).
     - **Python <3.10 or Node <20** → upgrade instructions.
     - **No internet** → check VPN / firewall / DNS; the workspace cannot function without Anthropic API access.
     - **Low RAM / disk** → there's no fix from inside the workspace; surface it as a hardware constraint the user should plan around.
   - Point to `README.md` "System requirements" for the full install / upgrade reference.
3. End with 2-3 reasonable next actions:
   - `/setup` (deeper tool + identity verification — useful right after `/system-check` to confirm git config and submodule init too)
   - `/run-tests` (workspace health, runs the lint + smoke tests)
   - `/menu` (current pipeline state, if the user wants to know "what now")

### Important — read-only, no permissions needed

This command modifies nothing. The script reads system info using Python stdlib (`platform`, `os`, `shutil`, `socket`) and read-only subprocess calls (`sysctl` on macOS, `/proc/meminfo` on Linux, `wmic` on Windows, `<tool> --version` for each CLI tool). It never writes a file, never calls a paid API, never sends network traffic outside a single DNS lookup. Anyone running the repo can run this safely.

### When to suggest this command

- A new contributor cloned the repo and you sense their environment may not be ready.
- A pipeline command failed in a way that hints at a missing tool or wrong version (Node 18 errors, pandoc not found, etc.).
- The user asks "will this work on my Mac/Linux/Windows?" — `/system-check` answers concretely.
- Right after `/acknowledge-contributing` (for forkers, paired with `/setup`).
