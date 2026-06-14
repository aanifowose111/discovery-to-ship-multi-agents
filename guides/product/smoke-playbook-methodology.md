# SMOKE.md — manual smoke-test playbook methodology

`SMOKE.md` is the **per-product standing playbook of manual smoke checks to run before each deploy**. It is the prescriptive companion to `VERIFIED.md`'s descriptive log: `VERIFIED.md` records what was checked; `SMOKE.md` records what *should* be checked, every time, before a release goes out.

It exists at `<web-apps|mobile-apps|desktop-apps>/<slug>/SMOKE.md`. Gitignored.

---

## 1. Purpose

Before every `/ship-app` invocation, the user should walk through a known sequence of checks: log in, click through the main flow, hit a few `/_dev/*` routes to confirm side effects, watch one transactional email actually arrive. `SMOKE.md` is the **canonical checklist** for this. Each line is a manual action with an expected outcome.

Distinct from:

- **`VERIFIED.md`** (descriptive log of what the user has checked over time).
- **pytest / integration suites** (automated; SMOKE.md is human-only).
- **Production observability** (post-deploy; SMOKE.md is pre-deploy).

---

## 2. When the file is created

| Trigger | Behavior |
|---|---|
| **`/smoke <slug>` invoked with no existing file** | Create the file; populate seed entries from `VERIFIED.md` (the `[x]` lines become the seed playbook) + `/_dev/*` route registry + the brief's success criterion. |
| **`/smoke <slug>` invoked with existing file** | Run the playbook interactively: for each entry, ask the user "did this still work?" via `AskUserQuestion`. |
| **`/ship-app <slug>`** | If `SMOKE.md` exists, the release-readiness checks run through it first as a release gate. |

The file is **not** auto-created by `/draft-design-spec` — it only makes sense once the build has produced something to smoke-test. Most users will create it shortly before their first deploy.

---

## 3. Format

```markdown
---
project: <slug>
created: 2026-06-15
last-run: 2026-06-15
schema: smoke-v1
---

# SMOKE — pre-deploy manual playbook for <slug>

Run through every check below before each `/ship-app`. Each check has an expected outcome.

## Status symbols (per-run, reset on each invocation)

- `[ ]` — Not yet checked this run
- `[x]` — Passed this run
- `[!]` — Failed this run (release blocker)
- `[-]` — Skipped this run (with reason)

## Run history

- 2026-06-15 — 8 of 9 passed; 1 skipped (email send — staging key not configured); 0 failed.

## Smoke checks

### Critical path — auth (must pass to deploy)

- `[ ]` Login with valid credentials redirects to dashboard.
- `[ ]` Logout from any page returns to login screen.
- `[ ]` `/_dev/whoami` after login returns expected JSON shape.

### Critical path — primary user flow

- `[ ]` Founder completes the intake walkthrough (or skips it) and reaches the data-sources screen.
- `[ ]` Founder connects Stripe with a test key; back-fill summary shows non-zero entity count.
- `[ ]` Founder runs `/diagnostic/run`; report page renders with at least one workflow candidate.

### Critical path — dev routes (must respond)

- `[ ]` `/_dev/run_diagnostic` returns 200 JSON with `{status: "queued"}`.
- `[ ]` `/_dev/logout` returns 200 and clears session.

### Non-critical — observability

- `[ ]` `/healthz` returns 200 `{"ok": true}`.

## Version log

- 2026-06-15 — initial playbook seeded from VERIFIED.md (6 entries) + dev-routes (3 entries).
```

---

## 4. The interactive run

`/smoke <slug>` walks each check in order using `AskUserQuestion`:

For each entry:

1. Show the check description.
2. Use `AskUserQuestion` with options:
   - **Passed** → `[x]`
   - **Failed** → `[!]`; follow up with "What broke?" free-text → recorded as a comment line under the entry
   - **Skipped** → `[-]`; follow up with "Why?" free-text → recorded as a comment line
3. Continue to the next entry.

After all entries:

- Update `last-run` in frontmatter.
- Append to "Run history": `<date> — N passed, M failed, K skipped`.
- Reset all entries to `[ ]` for the next run (a smoke run is per-deploy, not cumulative).

### Failed (`[!]`) entries gate `/ship-app`

If `/ship-app <slug>` finds any `[!]` entry in the current run, it surfaces it as a release blocker:

> SMOKE.md has 1 failed check: "Login with valid credentials redirects to dashboard" (note: "redirect targets wrong tenant subdomain"). Resolve this before deploying.

The user can override (`/ship-app <slug> --skip-smoke "<reason>"`) but the override is audited.

---

## 5. Seeding the playbook on first creation

When `/smoke <slug>` runs and `SMOKE.md` doesn't exist, Claude:

1. Reads `VERIFIED.md` if present. Every `[x]` entry becomes a seed smoke check (the verb tense flips from "verified" to a check description).
2. Scans `<product-folder>/app/blueprints/*.py` (Flask) or equivalent for routes under `/_dev/`. Each becomes a seed smoke check.
3. Reads the brief's success criterion (`MVP.md` or `V1.md` §Success criterion). The behavior named there becomes a critical-path seed.
4. Reads `BUILD_STATUS.md` `[x]` subsystems. For each, asks Claude to propose 1-2 user-facing checks (e.g., for "Auth + invitations": "accept an invitation via emailed link," "complete signup with a strong password").
5. Surfaces the full proposed list to the user; user confirms / removes / edits before the file is written.

After first creation, future runs only refresh the playbook if the user adds entries by hand or asks `/smoke <slug> --reseed` (reads the latest `VERIFIED.md` and `_dev/*` registry for new entries).

---

## 6. Relationship to VERIFIED.md

| `VERIFIED.md` | `SMOKE.md` |
|---|---|
| Log of features the user has eyeballed (over time, ad-hoc) | Standing playbook to run before each deploy |
| Per-line status persists across sessions | Per-line status resets each run |
| `[!]` entries surface during `/start-build` and `/continue-build` | `[!]` entries gate `/ship-app` |
| One artifact, growing log | One artifact, reset on each run |
| `/do-verify` appends | `/smoke` runs through it |

The two are complementary — `VERIFIED.md` captures the breadth of what's been checked over time; `SMOKE.md` captures the narrow critical path that must keep working.

---

## 7. Anti-patterns

- **Smoke playbook the user doesn't run:** if `SMOKE.md` becomes stale (no `last-run` for weeks), the orchestrator surfaces it as a release readiness concern.
- **Smoke playbook with everything in it:** keep critical-path entries critical. A 50-entry playbook will be skipped; a 10-entry one will get run.
- **Treating smoke failures as automated test failures:** smoke failures are about the user-facing surface, not internal correctness. A passing pytest suite + failing smoke check is a real signal, not a bug in the smoke check.

---

*Last updated: 2026-06-13.*
