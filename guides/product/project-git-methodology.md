# Per-project Git methodology

How individual products in `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/` get pushed to GitHub as **independent repositories** while the parent workspace repo continues to ignore them.

This guide is the contract `/push-project <slug>` runs against.

---

## 1. The pattern: nested git repos

This workspace is itself a git repo (`discovery-to-ship-multi-agents`). It pushes to `https://github.com/<user>/discovery-to-ship-multi-agents`. Its `.gitignore` ignores `web-apps/`, `mobile-apps/`, `desktop-apps/`, so the parent repo never tracks anything inside those folders.

A **product** (e.g., `web-apps/ops-audit-agent/`) is its own independent git repository, with its own `.git/` directory, its own remote, its own commit history. The parent repo doesn't see this nested `.git/` (it's inside a gitignored path).

```
~/Desktop/agents/                   ← parent workspace repo (.git here)
├── .gitignore                       ← ignores web-apps/**, mobile-apps/**, etc.
├── CLAUDE.md                        ← tracked by parent
├── web-apps/
│   └── ops-audit-agent/             ← gitignored from parent's perspective
│       ├── .git/                    ← INDEPENDENT git repo (parent never sees this)
│       ├── .gitignore               ← nested repo's own
│       ├── README.md                ← nested repo's own
│       ├── app/
│       └── ...
└── mobile-apps/
    └── another-product/             ← also gitignored
        ├── .git/                    ← also independent
        └── ...
```

**Not git submodules.** Submodules would require the parent to track the nested repo's commit hash, requiring explicit `git submodule update` and adding coupling. This pattern is fully decoupled — each repo has independent history, independent PRs, independent CI.

---

## 2. Why this works

Git's `.gitignore` rules work at the directory level. When the parent's `.gitignore` contains `web-apps/**`, git's working-tree scanner does **not** descend into `web-apps/<slug>/` looking for tracked files OR for a nested `.git/` directory. The parent repo is blind to anything in there, including the nested repo's existence.

This means:

- ✅ The nested repo has its own commit history, branches, tags, GitHub Actions
- ✅ The nested repo can be cloned independently by anyone
- ✅ The parent workspace can be cloned without pulling product-specific code
- ❌ `git status` at the parent shows nothing about nested-repo changes
- ❌ `git pull` at the parent doesn't pull nested-repo updates
- ❌ Pushing the parent doesn't push nested-repo commits

To work with a nested repo, you `cd` into the product folder first, then run git commands. Or use `/push-project <slug>` which handles the `cd` for you.

---

## 3. Setup for a new product repo (one-time per product)

Run **`/push-project <slug> --init`**, which does:

1. **Check the product folder exists** at `web-apps/<slug>/` (or mobile/desktop). Stop if not.
2. **Check no `.git/` already exists** in the product folder. If it does, switch to status mode (`--status`) and tell the user the repo is already initialized.
3. **Run `git init`** inside the product folder. Modern git defaults to the `main` branch.
4. **Create `.gitignore`** appropriate for the stack:
   - **Web (Flask)**: `.env`, `__pycache__/`, `*.pyc`, `.venv/`, `.pytest_cache/`, `.dockerignore`, `instance/`, plus the project's own logs
   - **Mobile (RN + Expo)**: `node_modules/`, `.expo/`, `*.log`, `ios/Pods/`, `android/.gradle/`, `android/app/build/`
   - **Desktop (PySide6)**: `__pycache__/`, `*.pyc`, `.venv/`, `build/`, `dist/`, `*.spec` (PyInstaller temp), `.qt-cache/`
5. **Create `README.md`** stub if it doesn't exist — title, one-line description from `MVP.md`, "Initial repo" placeholder.
6. **Ask the user about LICENSE** (`AskUserQuestion`): MIT (default for personal projects) / Apache-2.0 / Proprietary / Skip. If MIT/Apache, create the LICENSE file.
7. **Ask the user for the GitHub remote URL** — format: `https://github.com/<user>/<repo-name>.git` or `git@github.com:<user>/<repo-name>.git`. The user must have already created the empty repo on GitHub (this command does NOT create remote repos via `gh repo create` unless explicitly asked — different concern).
8. **Run `git remote add origin <url>`**.
9. **Safety scan** (per §6 below) before any staging.
10. **Stage + commit + push:**
    ```
    git add -A
    git commit -m "Initial commit"   # ask about Co-Authored-By per CLAUDE.md
    git push -u origin main
    ```
11. **Report**: project repo is live at `<url>`, branch `main` pushed.

After setup, regular pushes use `/push-project <slug>` without `--init`.

---

## 4. Routine push (after setup)

Run **`/push-project <slug> [-m "<msg>"]`**:

1. **cd** into the product folder.
2. **Run `git status`** to see what's changed since the last commit.
3. **If nothing to commit AND nothing to push**, surface "working tree clean, nothing to push" and stop.
4. **If unstaged changes**, surface them grouped by modified/new/deleted; ask user via `AskUserQuestion` what to do:
   - **Stage all and commit** → continue
   - **Stage some** → user picks files via subsequent message
   - **Cancel** → stop
5. **Safety scan** (per §6).
6. **Commit message**: use the `-m` flag value if provided, else ask via free-text prompt: "Commit message?"
7. **Per CLAUDE.md commit trailer policy**: ask about Co-Authored-By trailer.
8. **Run `git commit -m "<msg>"`** with or without the trailer.
9. **Run `git push`** (default: current branch). If push is rejected (non-fast-forward, branch behind), surface the error and ask: pull + retry / force-push (require explicit confirm) / cancel.
10. **Report**: commit SHA, branch, push target.

---

## 5. Status (`/push-project <slug> --status`)

Read-only:

1. **cd** into the product folder.
2. **Run `git status --short`** and report.
3. **Run `git log --oneline -5`** for the last 5 commits.
4. **Run `git remote -v`** to confirm remote.
5. **Run `git diff --stat HEAD`** for a change summary if any.
6. **Stop.** No staging, no commit, no push.

---

## 6. Safety scans (run before every commit)

These checks are MANDATORY before any push and refuse to proceed on a hit:

### 6.1 .env safety

- **REFUSE TO PUSH** if `.env` (NOT `.env.example`) is staged or about to be staged. The user must remove from staging (`git restore --staged .env`) and add to `.gitignore` if not already there.
- Acceptable: `.env.example`, `.env.sample`, `.env.template` — these document required env vars without values.

### 6.2 Secret patterns

Run `git diff --cached` and scan for common secret patterns:

- AWS keys: `AKIA[0-9A-Z]{16}`
- GitHub tokens: `ghp_[a-zA-Z0-9]{36}`, `gho_`, `ghu_`, `ghs_`, `ghr_`
- Generic API keys: 32+ char hex/base64 strings near words like `api_key`, `secret`, `token`, `password`
- Private keys: `-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----`
- Stripe: `sk_live_`, `pk_live_` (test keys `sk_test_` are softer warning)
- Slack: `xox[abp]-[a-zA-Z0-9-]+`

On a hit: **STOP**, name the file + line, ask the user to either (a) remove it and reset that line, (b) move it to `.env` (and confirm `.env` is in `.gitignore`), (c) override-with-acknowledgment if the "secret" is actually a placeholder/example. Override requires the user to type explicit ack text.

### 6.3 Branch + force checks

- **First push to a non-main branch**: surface a confirmation: "You're pushing to `<branch>` which is not `main`. Is this intentional? (Y/n)"
- **`--force` push to main**: **REFUSE** unless `--force-with-lease-on-main-i-understand-the-risk` flag is also passed.
- **`--force-with-lease`**: ask once before proceeding.

---

## 7. Best practices for nested repos

### 7.1 Independent everything

Each nested repo has its own:
- `.git/` (history, branches, tags)
- `.gitignore` (per-stack defaults from §3)
- `README.md` (project-specific)
- `CHANGELOG.md` (project-specific releases, separate from parent workspace's CHANGELOG)
- `LICENSE` (may differ from parent — MVP can be proprietary while parent stays MIT)
- `.github/workflows/` (per-project CI/CD)
- Issues, PRs, GitHub Actions, Releases

### 7.2 Don't cross-stage

Never `cd ~/Desktop/agents && git add web-apps/`. The parent's `.gitignore` would prevent it from staging anything inside `web-apps/<slug>/` — but the **safer rule** is: only run `git add` from inside the relevant repo. Stay aware of which `.git/` you're in.

### 7.3 IDE awareness

Most IDEs (VS Code, JetBrains) auto-detect nested `.git/` directories. Opening the parent workspace shows the parent's git state; opening `web-apps/<slug>/` directly shows the nested repo's git state. Both work.

### 7.4 Backups + clones

Each nested repo on GitHub is its own backup. Losing the parent workspace's local clone doesn't lose the nested repos — you can re-clone each from GitHub independently. This is part of why the pattern is robust.

### 7.5 Naming the GitHub repo

Convention (recommended):
- Parent workspace: `discovery-to-ship-multi-agents`
- Each product: `<slug>` directly (e.g., `ops-audit-agent`, not `discovery-to-ship-multi-agents-ops-audit-agent`)

The slug becomes the canonical product name across both the local folder and the GitHub repo. Pair with a short product domain name later when you ship to first users.

---

## 8. Common gotchas

| Gotcha | Symptom | Fix |
|---|---|---|
| Forgot to `cd` into product folder | `git status` shows parent workspace's state, not the product's | `cd web-apps/<slug>/` first; or use `/push-project <slug>` |
| Accidentally ran `git init` in parent | A `.git/` inside `web-apps/<slug>/.git/` collides with parent's git tracking | Delete the accidental `.git/` (it's gitignored anyway), re-run `/push-project <slug> --init` |
| `.env` got staged before noticing | Files appear in `git status` output that shouldn't be there | `git restore --staged .env`, add `.env` to `.gitignore`, commit `.gitignore` change first |
| GitHub repo doesn't exist yet | `git push` returns "repository not found" | Create the empty repo on GitHub first (or use `gh repo create <name> --private` from the product folder) |
| Pushed a secret by accident | The secret is now in git history | Treat as compromised — rotate immediately. To remove from history: `git filter-repo --invert-paths --path <file>` then force-push (history rewrite). Tells anyone who already cloned to re-clone. |
| Two products with the same slug | `check_slug.py` flags it during pre-flight; `/scope-mvp` refuses to create the brief | Pick a different slug; the workspace enforces slug uniqueness across all stack folders |

---

## 9. Integration with the rest of the pipeline

- **Doesn't change the parent workspace flow** at all. Parent push, parent tag, parent release work the same.
- **Per-product CHANGELOG**: each product has its own under `<product-folder>/CHANGELOG.md`. Use semantic versioning per-product. Parent's CHANGELOG covers workspace-level changes; product CHANGELOG covers product-level changes.
- **Per-product GitHub Actions**: `<product-folder>/.github/workflows/*.yml`. The parent workspace's `.github/workflows/release.yml` is for parent releases only.

---

*Last meaningful revision: 2026-06-09 (initial draft).*
