---
description: Push a product (web-apps/mobile-apps/desktop-apps/<slug>) to its own independent GitHub repository, separate from the parent workspace repo. Supports first-time setup (`--init`), routine push, status-only mode (`--status`), and remote management (`--remote`). Mandatory safety scans for .env files and secrets before every push. Per guides/product/project-git-methodology.md.
argument-hint: <product-slug> [-m "<commit-msg>"] [--init] [--remote <url>] [--status] [--no-commit] [--branch <name>] [--force-with-lease]
---

You are about to push a specific product to GitHub as its own independent repository. Follow the methodology in @guides/product/project-git-methodology.md exactly. The parent workspace's `.gitignore` already ignores `web-apps/`, `mobile-apps/`, `desktop-apps/` — so the nested git repo is invisible to the parent and can have its own history, remote, and CI.

**Use this when:**
- First time pushing a product → use with `--init` flag (creates `.git/`, `.gitignore`, `README.md`, optional LICENSE, sets remote, initial commit + push)
- Routine commit + push → no flags needed
- Read-only status check → `--status`
- Re-setting the remote URL → `--remote <url>`

**Arguments:** $ARGUMENTS

Parse the arg string for:
- `<slug>` (positional, required) — the product folder name
- `-m "<msg>"` — commit message inline
- `--init` — first-time setup mode
- `--remote <url>` — set or update the remote (combine with `--init` for setup; standalone to update an existing repo's remote)
- `--status` — read-only status mode
- `--no-commit` — push existing commits only (skip stage + commit)
- `--branch <name>` — push to a specific branch (default: current branch, usually `main`)
- `--force-with-lease` — force-push with lease (requires confirmation)

### Pre-flight

1. **Locate the product folder.** Check `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`. If none exists, stop: "No product folder for `<slug>`. Run `/scope-mvp <slug>` first."

2. **Resolve `<product-folder>`** and `<stack>` (web/mobile/desktop) for later use.

3. **Mode dispatch:**
   - If `--init`: jump to §A "Init mode"
   - Else if `--status`: jump to §B "Status mode"
   - Else if `--remote <url>` (without `--init`): jump to §C "Update-remote mode"
   - Else: jump to §D "Routine push mode"

---

### §A Init mode

1. **Check for existing `.git/`** in the product folder. If present, stop and tell the user: "`<product-folder>/.git/` already exists — repo is already initialized. To push routine changes, run `/push-project <slug>` (no `--init`). To reset remote, run `/push-project <slug> --remote <url>`."

2. **Run `git init`** inside the product folder. Confirm modern git defaults to `main` branch (if not, run `git checkout -b main`).

3. **Create `.gitignore`** appropriate for the stack. Use these templates (write to `<product-folder>/.gitignore`):

   **Web (Flask):**
   ```
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   .Python
   .venv/
   venv/
   *.egg-info/
   dist/
   build/

   # Env + secrets
   .env
   .env.local
   *.pem
   *.key

   # Flask + Docker
   instance/
   .dockerignore.bak

   # Testing
   .pytest_cache/
   .coverage
   htmlcov/

   # Logs + OS
   *.log
   .DS_Store
   .idea/
   .vscode/
   ```

   **Mobile (RN + Expo):**
   ```
   # Node
   node_modules/
   npm-debug.log
   yarn-error.log
   .pnpm-debug.log

   # Expo
   .expo/
   web-build/
   dist/

   # Native
   ios/Pods/
   ios/build/
   android/.gradle/
   android/app/build/
   android/build/

   # Env + secrets
   .env
   .env.local
   google-services.json
   GoogleService-Info.plist
   *.keystore
   *.jks
   *.p8
   *.p12
   *.mobileprovision

   # OS + IDE
   .DS_Store
   .idea/
   .vscode/
   ```

   **Desktop (PySide6):**
   ```
   # Python
   __pycache__/
   *.py[cod]
   .venv/
   venv/
   *.egg-info/

   # PyInstaller
   build/
   dist/
   *.spec
   *.manifest

   # Env + secrets
   .env
   *.pem
   *.key

   # Qt cache
   .qt-cache/

   # Testing
   .pytest_cache/
   .coverage

   # OS + IDE
   .DS_Store
   .idea/
   .vscode/
   ```

4. **Create `README.md`** stub if it doesn't already exist:
   ```markdown
   # <Product Name>

   <One-line description — read from MVP.md frontmatter or the brief's first sentence>

   ## Status

   - Stage: <MVP / V1 / Shipped>
   - Stack: <Flask / RN+Expo / PySide6>

   ## Running locally

   <TBD — fill in once the build is further along>

   ## License

   <MIT / Apache-2.0 / Proprietary — set during /push-project --init>
   ```

5. **Ask about LICENSE** via `AskUserQuestion`: "What license for this product?"
   - **MIT (recommended for personal projects)** → write standard MIT to `LICENSE` with `<current-year>` and the user's git config name as copyright holder
   - **Apache-2.0** → write standard Apache-2.0 LICENSE
   - **Proprietary** → write a short "All rights reserved" stub
   - **Skip** → don't create a LICENSE file (user can add later)

6. **Ask for the GitHub remote URL** via free-text prompt:
   > What's the GitHub remote URL? Format: `https://github.com/<user>/<repo>.git` or `git@github.com:<user>/<repo>.git`.
   >
   > **Note:** The repo must already exist on GitHub (create it via `gh repo create <repo-name> --private` or via the GitHub web UI). This command does NOT create remote repos.

   Wait for the user's reply. Validate the URL format roughly (`https://github.com/...` or `git@github.com:...`).

7. **Run `git remote add origin <url>`** inside the product folder.

8. **Safety scan** per §6 of the methodology guide (run inline; see §SAFETY below in this command).

9. **Per-commit Co-Authored-By trailer policy** (per CLAUDE.md): ask via `AskUserQuestion`:
   - **Include trailer** — adds `Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>` to this commit
   - **Drop trailer** — solo attribution to git user

10. **Stage + initial commit + push:**
    ```bash
    cd <product-folder>
    git add -A
    git commit -m "Initial commit$<trailer_block_if_picked>"
    git push -u origin main
    ```

11. **Report** to the user:
    > ✅ Project repo initialized and pushed.
    >
    > - **Remote:** `<url>`
    > - **Branch:** `main`
    > - **Commit:** `<short-sha>` "Initial commit"
    > - **Files:** `<count>` files in this commit
    > - **Trailer:** `<included | dropped>`
    >
    > Routine pushes from here: `/push-project <slug>` (no flags needed).
    >
    > Open: `<url>` (with `.git` suffix stripped for the GitHub URL).

---

### §B Status mode

Read-only. Inside the product folder, run:

```bash
cd <product-folder>
git status --short
git log --oneline -5
git remote -v
git diff --stat HEAD 2>/dev/null || true   # may fail on fresh repo
```

Report:
> **Project repo status for `<slug>`:**
>
> - **Remote:** `<url>` (or "no remote set")
> - **Current branch:** `<branch>`
> - **Ahead of origin:** `<X>` commits  ·  **Behind:** `<Y>` commits
> - **Unstaged changes:** `<N>` files
> - **Staged changes:** `<M>` files
>
> **Recent commits:**
> - `<sha>` `<msg>`
> - `<sha>` `<msg>`
> - ...
>
> **Change summary (uncommitted):**
> `<files X+, Y- lines>`

Stop. Do not stage, commit, or push.

---

### §C Update-remote mode

When `--remote <url>` is passed without `--init`:

1. Check `.git/` exists in product folder. If not, tell user to run with `--init` first.
2. Check current remote: `git remote get-url origin 2>/dev/null || echo "none"`.
3. If a remote is already set, surface it and ask: "Current `origin` is `<existing>`. Replace with `<new>`?" via `AskUserQuestion`.
4. Run `git remote set-url origin <new-url>` (or `git remote add origin <new-url>` if none was set).
5. Verify with `git remote -v` and report.
6. Stop. Do not push.

---

### §D Routine push mode

1. **cd** into the product folder.

2. **Check `.git/` exists.** If not, tell the user: "No `.git/` in `<product-folder>`. Run `/push-project <slug> --init` first."

3. **Check remote exists.** If `git remote get-url origin` fails: "No remote set. Run `/push-project <slug> --remote <url>` to set one first."

4. **Run `git status`** and capture:
   - Unstaged files
   - Staged files
   - Branch name + ahead/behind from origin

5. **If `--no-commit`:** skip to step 11 (just push existing commits).

6. **If nothing to commit AND nothing to push** (clean working tree + branch up-to-date with origin): surface "Working tree clean and origin up-to-date. Nothing to do." Stop.

7. **If unstaged changes exist, surface them grouped:**
   > Changes since last commit:
   > - Modified (`<count>`): `<file>`, `<file>`, ...
   > - New (`<count>`): `<file>`, ...
   > - Deleted (`<count>`): `<file>`, ...
   >
   > What do you want to commit?
   - **Stage all** → `git add -A` then continue
   - **Stage some** → ask for a list of files in next message, then `git add <files>`
   - **Cancel** → stop

8. **Safety scan** per §SAFETY below.

9. **Commit message:**
   - If `-m "<msg>"` was passed, use it
   - Else ask via free-text prompt: "Commit message? (one line preferred; reply with multi-line text for detailed messages)"

10. **Per-commit Co-Authored-By trailer:** ask via `AskUserQuestion`. Honor any session-level preference set earlier ("always include this session" / "drop for the rest of this session").

11. **Run `git commit -m "<msg>"`** (with or without trailer).

12. **Run `git push`** (or `git push --force-with-lease` if `--force-with-lease` flag was passed AND the user explicitly confirmed via `AskUserQuestion`):
    - If push rejected (non-fast-forward), surface the error and ask: pull-and-rebase / force-with-lease / cancel
    - If push to a non-main branch and it's the first push there, confirm intent

13. **Report:**
    > ✅ Pushed.
    >
    > - **Commit:** `<short-sha>` "<msg-first-line>"
    > - **Branch:** `<branch>`
    > - **Remote:** `<url>`
    > - **Trailer:** `<included | dropped>`
    >
    > Open on GitHub: `<derived-github-url>` (substituting `git@github.com:X/Y.git` → `https://github.com/X/Y`)

---

### §SAFETY: scans run before every commit (init mode + routine push mode)

**A. `.env` safety.**

```bash
# Scan staged files for .env (not .env.example)
git diff --cached --name-only | grep -E '(^|/)\.env(\.|$)' | grep -v '\.env\.example$\|\.env\.sample$\|\.env\.template$' | head -5
```

If output is non-empty: **STOP, surface the offending files**, and tell the user:
> 🛑 **REFUSING TO COMMIT.** Found `.env` file(s) staged: `<file>`. These should NOT go to GitHub — they hold secrets. To fix:
> 1. `git restore --staged <file>` (unstage)
> 2. Confirm `<file>` is in `.gitignore` (add if not, then commit `.gitignore` change first)
> 3. Re-run `/push-project <slug>`

Wait for the user to fix and rerun. Do not push.

**B. Secret patterns in diff.**

```bash
# Scan staged diff for common secret patterns
git diff --cached | grep -nE '(AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|sk_live_[a-zA-Z0-9]{24,}|-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----|xox[abp]-[a-zA-Z0-9-]+)' | head -10
```

If output is non-empty: **STOP, surface the file + line numbers**, ask the user:
> 🛑 **POSSIBLE SECRET DETECTED.** Pattern matched in staged diff: `<pattern>` at `<file>:<line>`.
>
> Options:
> 1. **Remove + reset** — I'll show you the line; you remove it; re-stage; rerun this command
> 2. **Move to `.env`** — I'll help move the secret to `.env`, add `.env` to `.gitignore` (if not already), then continue without that change
> 3. **Override (the match is a false positive — this is a placeholder/example)** — type "override: this is not a real secret" verbatim to confirm

If override → continue. Else stop and wait for the user to fix.

**C. Branch + force checks.**

- If pushing to a branch other than `main` for the first time: confirm via `AskUserQuestion` "First push to `<branch>` — is this intentional?"
- If `--force-with-lease` was passed: confirm via `AskUserQuestion` "Force-push with lease to `<branch>` — overwrites remote history. Proceed?"
- **Refuse plain `--force` to `main` outright** unless `--force-with-lease-on-main-i-understand-the-risk` was also passed (intentionally verbose flag).

---

### Notes

- **One commit per `/push-project` invocation.** If you want multiple commits, run the command multiple times or commit manually inside the product folder.
- **Audit log:** this command does NOT auto-append to the audit log (it's a routine git op, not a state decision). The user can `/log type user-note "Pushed v0.2 of <slug>"` if they want a record.
- **Multi-product workflow:** to push two products in sequence, run `/push-project ops-audit-agent` then `/push-project invoice-agent-agencies` — each independent commit cycle, each independent confirmation.
- **For mobile + EAS workflows:** EAS builds and submissions are a separate concern. `/push-project` only handles the GitHub side; EAS publish runs via `npx eas build` from within the product folder.
- **GitHub repo creation isn't this command's job.** Create the empty GitHub repo first (via `gh repo create <name> --private` from inside the product folder is the easiest way), then run `/push-project <slug> --init` to wire it up locally + push.
