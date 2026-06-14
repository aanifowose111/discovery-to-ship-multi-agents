---
description: Run the pre-deploy manual smoke playbook for a product — `SMOKE.md`. Creates the file if it doesn't exist (seeded from `VERIFIED.md` + `/_dev/*` route registry + the brief's success criterion). Walks each check interactively; user marks pass / fail / skip per entry. Failed (`[!]`) entries gate `/ship-app`. Per guides/product/smoke-playbook-methodology.md.
argument-hint: <product-slug> [--reseed]
---

You are about to run the manual smoke-test playbook for one product. Follow the methodology in @guides/product/smoke-playbook-methodology.md exactly.

**Use this when:**
- You're about to deploy and want to walk through the critical-path checks first
- You're getting close to `/ship-app` and want to make sure nothing has silently regressed since the last release
- `SMOKE.md` doesn't exist for this product yet and you want to seed it (auto-creation on first invoke)

**Don't use this for:**
- Recording one-off verifications — that's `/do-verify` writing `VERIFIED.md`
- Running pytest tests — that's `/run-tests` or the orchestrator
- Production observability — smoke is pre-deploy, observability is post-deploy

**Arguments:** $ARGUMENTS — the product slug, optionally with `--reseed` to re-pull seed entries from the latest `VERIFIED.md` and `_dev/*` registry (useful when the file is months old and the product has grown).

### Pre-flight

1. **Locate the product folder.** If `<web-apps|mobile-apps|desktop-apps>/<slug>/` doesn't exist, stop.

2. **Check whether `<product-folder>/SMOKE.md` exists.**
   - **If it doesn't exist**, go to "First run — seed the playbook" below.
   - **If it exists**, go to "Subsequent run — walk the playbook" below.

### First run — seed the playbook

1. **Read all seed sources** in parallel:
   - `<product-folder>/VERIFIED.md` if it exists (every `[x]` line becomes a seed)
   - `<product-folder>/BUILD_STATUS.md` (every `[x]` subsystem suggests 1-2 user-facing checks)
   - `<product-folder>/MVP.md` or `V1.md` § Success criterion (the behavior named there becomes a critical-path seed)
   - `<product-folder>/app/blueprints/_dev.py` if Flask web; `<product-folder>/src/screens/_dev/` if RN mobile — each route/screen becomes a seed
   - `<product-folder>/app/blueprints/*.py` for primary user-facing routes

2. **Propose a draft playbook** organized into 3 critical sections + optional non-critical section:
   - **Critical path — auth** (login / logout / `/_dev/whoami`)
   - **Critical path — primary user flow** (from the brief's success criterion)
   - **Critical path — dev routes** (every `/_dev/*` route in the registry)
   - **Non-critical — observability** (`/healthz`, etc.)

3. **Show the draft to the user** as a proposed Markdown block. Ask via `AskUserQuestion`:
   - **Use this draft** — Claude writes the file.
   - **Edit the draft first** — Claude prompts for free-text edits, then writes.
   - **Cancel** — no file written.

4. **On confirmation**, write `<product-folder>/SMOKE.md` with the proposed content + frontmatter per `guides/product/smoke-playbook-methodology.md §3`. Surface to the user: "Created `SMOKE.md` with `<N>` checks. Re-run `/smoke <slug>` to walk through them."

### Subsequent run — walk the playbook

1. **Read `<product-folder>/SMOKE.md`.** Parse the check entries and frontmatter.

2. **Reset all per-check status to `[ ]`** (smoke runs are per-deploy, not cumulative; the previous run's `[x]` / `[!]` / `[-]` don't carry over).

3. **For each check in order**, use `AskUserQuestion` with these options:
   - **Passed** — append `[x]`.
   - **Failed** — append `[!]`; follow up with "What broke?" free-text → recorded as a comment line indented under the entry.
   - **Skipped** — append `[-]`; follow up with "Why?" free-text → recorded as a comment line.
   - **Other / Abort run** — stop the walk; mark remaining entries `[ ]`.

4. **Update frontmatter** `last-run: <today>`.

5. **Append a Run history line**: `- <today> — N passed, M failed, K skipped.`

### Stop here — user checkpoint

After the walk completes, show:

> ✅ SMOKE.md run complete at `<product-folder>/SMOKE.md`.
>
> **This run** (`<today>`):
> - Passed (`[x]`): `<count>`
> - Failed (`[!]`): `<count>`
> - Skipped (`[-]`): `<count>`
> - Not yet checked (`[ ]`): `<count>`
>
> **❌ Failed this run** (gates `/ship-app`):
> 1. `<check description>` — note: "`<user's symptom text>`"
> 2. ...
>
> **⏭ Skipped this run**:
> 1. `<check description>` — reason: "`<user's reason text>`"
> 2. ...
>
> Your call:
> - **Fix failures first**, then re-run `/smoke <slug>` before `/ship-app`.
> - **Override and ship anyway** — run `/ship-app <slug> --skip-smoke "<reason>"` (the override is audited).
> - **All clear** — proceed to `/ship-app <slug>`.

### Notes

- **Failed (`[!]`) entries gate `/ship-app`.** The release-readiness step reads `SMOKE.md`; if any `[!]` exists in the latest run, it surfaces as a release blocker.
- **Smoke runs are per-deploy.** Don't keep stale status from prior runs; each invocation resets to `[ ]` before walking.
- **`--reseed`** re-pulls seed entries from `VERIFIED.md` and `_dev/*` registry. New entries are appended (existing entries preserved). Useful when the product has grown since the playbook was first created.
- **Reading existing failures from prior runs:** if you want to see the history, the Run history section in the file shows the full timeline. The current run's `[!]` entries are surfaced in the checkpoint; older `[!]` entries are in the file's run-history record.
- **Audit-log entry:** if any `[!]` is recorded, append a `build-milestone` entry of subtype "smoke-failure" so it shows up in `/log`. If all pass, append a `build-milestone` of subtype "smoke-passed".
