# Build status methodology

How the `BUILD_STATUS.md` file is generated, maintained, and surfaced during the build phase. The file is the **living dashboard** of a product's build — at any moment, you can open it (or run `/status`) and see what's done, what's in progress, what's next, and what was decided along the way.

The checklist is **dynamic, not static**. It's generated from the product's specific brief — stack, must-haves, scope (MVP vs. fully-featured), domain (web / mobile / hybrid) — so two products at the same stage have *different* checklists tailored to what each one actually needs.

---

## 1. Purpose

When a build is in flight, "what's next" is the most-asked question. Without a visible dashboard, the answer lives only in Claude's head and your memory — and after a session restart, the read-state-from-disk path means Claude reconstructs it each time.

`BUILD_STATUS.md` solves this:

- **Visible at a glance** — open the file, see the whole build state.
- **Tailored to this product** — the checklist reflects this brief's specifics, not a generic template.
- **Maintained as work happens** — each completed subsystem updates the file with timestamp + outcome.
- **History preserved** — a chronological log of what happened when, who did it (which persona), and what was decided.

---

## 2. Where it lives and who owns it

**Location:** `<web-apps|mobile-apps|desktop-apps>/<slug>/BUILD_STATUS.md`. For hybrid products, the canonical file is on the side that's being built first (per the `/start-build` orientation question); the other side gets a thin pointer to it.

**Owned by:** `senior-software-engineer`. Other senior personas report subsystem completion in their output; `senior-software-engineer` is the one writing/updating `BUILD_STATUS.md`.

**Lifecycle:** created when `/start-build` first runs and the orientation questions are answered. Updated on every subsystem start, completion, decision, or scope change. Frozen (status set to `released`) when the product ships to first users.

---

## 3. Generating the initial checklist (dynamic, not static)

When `senior-software-engineer` writes the first `BUILD_STATUS.md` for a product, it generates the checklist by walking three sources:

### Source 1 — The brief's must-haves

For each must-have, identify which subsystems it requires. Common mappings:

| Must-have phrasing | Subsystems required |
|---|---|
| "users can create accounts / log in / sign up" | Auth |
| "users can upload files / attach photos" | File storage (DO Spaces); upload-handling |
| "the system emails users when…" | Background jobs (email queue) |
| "users can search…" | Search index |
| "users can pay…" | Payment integration |
| "real-time updates / live chat / notifications" | WebSockets / push notifications |
| "users see content from other users" | Multi-tenant data model + auth (privacy) |
| "data is exported / imported" | Bulk operations + background jobs |
| "admin can manage users / content" | Admin interface |

**Subsystems NOT in any must-have are NOT in the checklist.** A product without file uploads doesn't get a "DO Spaces integration" line.

### Source 2 — The stack (per `mvp-scoping-methodology.md` §6.0)

The checklist items use stack-specific language and reference stack-specific guides:

- **Flask:** items reference `flask-mvp-scaffold.md`, `flask-deploy-runbook.md`, etc. Schema lines say "SQLAlchemy models." Auth lines say "flask-login + sessions."
- **React Native + Expo:** items reference `react-native-mvp-scaffold.md`, `eas-build-and-update.md`. Auth line says "JWT in secure-store."
- **Python + PySide6 (desktop):** items reference `guides/desktop/python-mvp-scaffold.md` + `guides/desktop/packaging-and-distribution.md`. Specific desktop subsystems: project tree + venv + pyproject, core models, core services (Qt-free), UI shell (main window + navigation), per-feature widgets, UI ↔ core bridge (QObject adapters with signals), packaging spec (committed `.spec`), smoke tests (pytest + pytest-qt offscreen), dev / build scripts, optional cross-platform CI, optional v1 code signing / notarization.
- **Other stack (Next.js, Django, Swift, Kotlin, C# + Avalonia, Electron, Tauri, etc.):** items use that stack's idioms; no workspace scaffold guide is referenced.

### Source 3 — The standard build order (per `CLAUDE.md` "Build orchestration")

Always include (these apply to virtually every product):

1. **System design** — `senior-system-design-engineer` → `SYSTEM_DESIGN.md`
2. **Database schema** — `senior-database-engineer` → `schema/SCHEMA.md`
3. **Project scaffold** — `senior-software-engineer` + relevant scaffold guide → `scaffold-done` git tag
4. **Core models** — `senior-backend-engineer` (mapped from schema)
5. **API contract** — `senior-backend-engineer` → `api/API_CONTRACT.md`
6. **API implementation** — `senior-backend-engineer`
7. *…subsystems from Sources 1 + 2 inserted here in order…*
8. **Frontend skeleton** — `senior-frontend-engineer`
9. *…frontend feature subsystems from Source 1 inserted here…*
10. **Integration tests** — `senior-qa-engineer`
11. **Deploy** — `senior-devops-engineer`
12. **First-user release** — `senior-software-engineer`

---

## 4. Output format

```markdown
---
slug: <product slug>
build-started: YYYY-MM-DD
build-status: not-started | in-progress | paused | released | killed
current-focus: <subsystem-id of what's actively being worked on, or null>
stack-web: <stack name or null>
stack-mobile: <stack name or null>
scope: mvp | fully-featured
domain: web | mobile | hybrid
build-order: <"api-web-first" | "mobile-first" | "web-only" | "mobile-only">
pending-reviews: []  # list of "<subsystem-id>: <reviewer>" entries, e.g., ["mh-7-stripe-ingest: security", "mh-8-hubspot-oauth: qa"]
completed-subsystems-since-sweep: 0  # incremented on every [x] flip; resets after a catch-up sweep
---

# Build Status — <product name>

**Stack:** <human-readable stack summary>
**Scope:** <MVP | fully-featured>
**Domain:** <web | mobile | hybrid; if hybrid, note which side is being built first>
**Started:** <date> · **Last activity:** <date>

## Phase 1 — System & Schema
- [x] **System design** (senior-system-design-engineer, <date>) — `SYSTEM_DESIGN.md`
- [x] **Database schema** (senior-database-engineer, <date>) — `schema/SCHEMA.md`
  - Tables: <list>
  - Indexes: <list>

## Phase 2 — Backend
- [x] **Project scaffold** (senior-software-engineer, <date>) — git tag: `scaffold-done`
- [>] **API contract** (senior-backend-engineer, in progress as of <timestamp>) — `api/API_CONTRACT.md`
- [ ] **API implementation** (senior-backend-engineer) — pending
- [ ] **Auth** (senior-security-engineer + senior-backend-engineer) — pending
  - Required for: <which must-haves drove this>
  - `security-review-required: true` · `qa-review-required: false` (tagged per §6.1)
- [ ] **File storage** (senior-backend-engineer + senior-security-engineer) — pending
  - Required for: <must-haves>
  - `security-review-required: true` (file-upload tag) · `qa-review-required: false`
- [ ] **Background jobs** (senior-backend-engineer) — pending
  - Required for: <must-haves>
  - `security-review-required: false` · `qa-review-required: true` (async-pipeline tag)

## Phase 3 — Frontend
- [ ] **Frontend skeleton** (senior-frontend-engineer) — pending
- [ ] **<feature> UI** (senior-frontend-engineer) — pending
- [ ] **<feature> UI** (senior-frontend-engineer) — pending

## Phase 4 — Verification & Release
- [ ] **Integration tests** (senior-qa-engineer) — pending
- [ ] **Deploy** (senior-devops-engineer) — pending
- [ ] **First-user release** (senior-software-engineer) — pending

## Current focus
**<subsystem>** — being worked on by **<persona>**.
<one-line context: what specifically is being done right now>
<one-line ETA when known>

## History (most recent first)
- YYYY-MM-DD HH:MM — <event: subsystem completed / decision recorded / scope changed / handoff>
- YYYY-MM-DD HH:MM — <event>
- ...

## Decisions recorded during build
- **<decision title>** (YYYY-MM-DD, by <persona>): <one-paragraph context + decision>. Why: <rationale>.
- ...

## Open items (surfaced for the user, not yet resolved)
- <item awaiting user decision>
- <item blocked on external dependency>
```

**Conventions:**
- `[x]` = done, `[>]` = in progress, `[ ]` = pending.
- Each item lists the **owner persona** and the **output artifact** (file path or git tag).
- The **Current focus** section always points at exactly one item.
- The **History** section is append-only; never delete past entries.
- **Decisions** are short ADR-style entries — they capture the reasoning behind non-obvious choices.

---

## 5. Update protocol

Who updates the file and when:

| Trigger | Updater | What changes |
|---|---|---|
| `/start-build` orientation completes | `senior-software-engineer` | Initial file created with full dynamic checklist |
| A specialist persona starts a subsystem | `senior-software-engineer` | `[ ]` → `[>]`; `current-focus` updated; History entry added |
| A specialist completes a subsystem | `senior-software-engineer` | `[>]` → `[x]`; timestamp + persona + artifact recorded; History entry added; **`build-milestone` entry appended to the audit log** (per `CLAUDE.md` § Audit log) — gives the user a queryable per-product build journal via `/log type build-milestone` |
| A subsystem is added or removed (scope change) | `senior-software-engineer` | Checklist updated; History entry explains the change |
| A non-obvious decision is made | `senior-software-engineer` | Decisions section appended |
| Build pauses | `senior-software-engineer` | `build-status: paused`; History note |
| Build releases | `senior-software-engineer` | `build-status: released`; final History entry; file becomes frozen |
| Build is killed | `senior-software-engineer` | `build-status: killed`; History note with reason |
| User commits `/rework` with `flip` subsystem decision | **Main Claude** (special exception — see below) | Affected `[x]` subsystems flip back to `[>]`; per-flip History entries with rework-trigger annotation; `build-status: rework-in-progress` |

Specialists do NOT edit `BUILD_STATUS.md` directly. They report completion (per their persona's output format), and `senior-software-engineer` makes the update. This keeps the file's voice consistent and prevents merge conflicts.

### Special exception: rework-triggered flips

The one documented case where **main Claude edits `BUILD_STATUS.md` directly** (vs. via the orchestrator persona) is when `/rework <slug> <changes>` Step 9 applies subsystem flips. The mechanism:

1. The user's rework affects already-completed subsystems (per the Subsystem-impact map produced in `/rework` Step 2.5 consulting consultation, or per main Claude's best-effort map at Step 8a if consultation was skipped).
2. The user opts at Step 8a to flip affected `[x]` subsystems back to `[>]`.
3. Step 9.3a applies the flips: each affected checklist line changes `- [x]` → `- [>]` (other content on the line preserved), and a History entry is appended per flip with the exact format:
   ```
   - <YYYY-MM-DD>: `[x]` → `[>]` for **<subsystem>** triggered by /rework (audit: <audit-log-id>). Reason: <one-line from impact map>. Requires re-invocation of <persona> against the reworked brief.
   ```
4. The frontmatter `build-status` is set to `rework-in-progress`, signalling to `/start-build` that completed work needs revisiting.

**Why main Claude and not the orchestrator?** The rework is a markdown-only command; the orchestrator's normal job is to coordinate builds in progress. A rework-triggered flip is essentially a rollback signal — main Claude applies it with the audit annotation, and `/start-build` later re-engages the orchestrator (and through them, the affected specialists) to do the actual revisit work. The `(audit: <id>)` annotation makes the trigger traceable to the rework event.

**The exception is narrow.** Main Claude does NOT edit `BUILD_STATUS.md` outside of `/rework` Step 9. All other state changes still flow through the orchestrator.

---

## 6. Reviewer checkpoints during build

**Why this exists.** Security and QA reviewers cannot only fire at `/ship-app`. By the time a build reaches release-readiness, weeks of subsystems have been written; finding 8 CRITICAL + HIGH findings then means weeks of rework. The discipline below ensures security and QA reviewers run at strategic in-build checkpoints — close enough to the implementation that findings are cheap to address.

### 6.1 Security-engineer auto-routing (per-subsystem)

The orchestrator MUST tag a subsystem with `security-review-required: true` if it carries ANY of the following surface tags (orchestrator infers tags from the must-have description + scaffold output; user can override):

| Tag | Surfaces it covers |
|---|---|
| `auth` | Signup, login, sessions, password reset, MFA, logout flow |
| `oauth` | Any third-party OAuth flow (Google, GitHub, HubSpot, Stripe Connect, etc.) |
| `encryption-at-rest` | Any data stored encrypted at rest (PII tables, audit logs, encrypted columns) |
| `secret-storage` | `.env` handling, KMS / Vault integration, secret rotation |
| `payment` | Stripe (or alternative) integration — Checkout, Subscriptions, webhooks, refunds |
| `llm-input` | Any prompt-injection-exposed surface (LLM diagnostic, agent runtime, user-message ingest into LLM context) |
| `file-upload` | User-uploaded files (avatars, documents, anything to disk or object storage) |
| `rls-multitenant` | Row-level security additions, multi-tenant data isolation, per-tenant query filtering |
| `webhook-signature` | Webhook handlers with HMAC / signature verification (Stripe, GitHub, etc.) |

When the subsystem implementation completes, the orchestrator MUST invoke `senior-security-engineer` (in build-phase review mode — see persona) on that subsystem. The reviewer returns an APPROVE / APPROVE-WITH-NOTES / REJECT verdict. **The subsystem stays `[>]` until APPROVE or APPROVE-WITH-NOTES is recorded; REJECT loops back to the implementation specialist with the findings.**

### 6.2 QA-engineer auto-routing (per-subsystem)

Parallel structure. Tag with `qa-review-required: true` if ANY of these tags apply:

| Tag | Surfaces it covers |
|---|---|
| `cross-service` | Subsystems that integrate ≥2 existing subsystems (e.g., auth + payment, OAuth refresh + cron worker) |
| `multi-tenant-query` | Queries that must be RLS-bound or per-tenant scoped |
| `async-pipeline` | Cron jobs, background workers, message queues, scheduled tasks |
| `concurrent-race` | Cron + concurrent-request surfaces where ordering / locking matters |
| `integration-of-2-plus` | Catch-all for subsystems that wire together 2+ prior subsystems |

When the subsystem completes, the orchestrator MUST invoke `senior-qa-engineer` (in build-phase review mode) for an integration-seam audit. Same verdict + flip rules as §6.1.

A subsystem can carry BOTH `security-review-required` and `qa-review-required` — both reviewers run in parallel (or sequentially, orchestrator's choice; both verdicts required before flip).

### 6.3 Catch-up sweep at every 5th completed subsystem

The orchestrator maintains a `completed-subsystems-since-sweep` counter in BUILD_STATUS frontmatter. Each `[x]` flip increments. **When the counter reaches 5**, the orchestrator runs a **catch-up sweep**:

- Invoke `senior-security-engineer` (build-phase review mode, scoped to the prior 5 completed subsystems) for a cross-cutting pass — looking for cross-subsystem issues a per-subsystem audit can miss (auth + RLS interaction, secret leakage across services, OAuth scope creep, etc.).
- Invoke `senior-qa-engineer` (build-phase review mode, scoped to the prior 5) for a cross-cutting integration audit — race conditions across subsystems, ordering assumptions, partial-failure handling.
- Reset `completed-subsystems-since-sweep: 0` after the sweep returns verdicts.
- Sweep findings flow into the next implementation slot (orchestrator opens a fix subsystem if findings are CRITICAL/HIGH).

This cadence catches drift that per-subsystem reviews miss because they only see one subsystem at a time.

### 6.4 Backend → frontend pre-transition audit

When ALL backend Phase 2 subsystems are `[x]` AND the **frontend skeleton** subsystem is about to start (its status would flip from `[ ]` to `[>]`), the orchestrator MUST first run a **pre-frontend audit**:

- `senior-security-engineer` runs a comprehensive backend-only security pass (treats backend as if it were release-ready at the backend layer): authn/authz consistent across endpoints, RLS bound everywhere, secrets clean, no insecure deserialization, etc.
- `senior-qa-engineer` runs a comprehensive backend-only integration audit: API contracts honored, edge-case coverage, partial-failure handling, idempotency where required.

This catches whole-backend issues before the frontend starts consuming the API and locking design decisions in. The audit takes 1-3 reviewer turns; the frontend skeleton waits.

### 6.5 Verdict requirements + REJECT loop

Per-reviewer verdict consequences:

| Verdict | Effect on subsystem |
|---|---|
| APPROVE | Subsystem can flip `[>]` → `[x]`. Notes (if any) carried to BUILD_STATUS history. |
| APPROVE-WITH-NOTES | Subsystem can flip `[>]` → `[x]`. The notes get added to **§Decisions recorded during build** + carried forward as follow-up items (orchestrator surfaces to user, may open a fix subsystem). |
| REJECT | Subsystem STAYS `[>]`. The reviewer's findings (with severity tags: CRITICAL / HIGH / MEDIUM / LOW) are passed back to the implementation specialist (`senior-backend-engineer` for backend, etc.). Specialist addresses findings, then re-invokes the reviewer. Loop until APPROVE / APPROVE-WITH-NOTES. |

**The orchestrator MUST NOT flip a subsystem to `[x]` while `security-review-required: true` or `qa-review-required: true` is set AND no APPROVE/APPROVE-WITH-NOTES verdict is recorded.** This is the load-bearing rule of the methodology.

### 6.6 Opt-out per subsystem (`review-deferred`)

The user can opt-out of a specific review on a specific subsystem when the risk is genuinely low and the verdict overhead isn't worth it (e.g., a small CRUD endpoint flagged because it touches a multi-tenant table but the surface is well-understood). The opt-out is **per-subsystem + per-reviewer**, never global:

```markdown
- [>] **<subsystem-name>** (<persona>) — in progress
  - `security-review-required: true` · `review-deferred: true` · `review-deferred-reason: "Low-risk surface; CRUD on already-RLS-scoped table; pattern matches MH #N which was reviewed."`
```

When `review-deferred: true` is set:

1. **User must add `review-deferred-reason: "<text>"`** with at least 10 chars. Orchestrator refuses the deferral without a reason.
2. **Orchestrator appends a `review-deferred` audit-log entry** capturing slug + subsystem + reviewer skipped + reason verbatim. Per `CLAUDE.md § Audit log`:
   ```
   python3 scripts/audit_log.py add review-deferred "Review deferred for <slug>: <subsystem-id>: skipped <reviewer-role>. Reason: <verbatim text>."
   ```
3. **The subsystem flips to `[x]` without the verdict.** History entry includes "review deferred (audit: <id>)" annotation.
4. **Catch-up sweep STILL runs** on deferred subsystems — the user can defer a per-subsystem review but cannot defer a catch-up sweep. This is the workspace's safety net.

If the user repeatedly defers reviews on related subsystems (3+ in a row), the orchestrator surfaces a warning: "You've deferred 3 security reviews in this build. The catch-up sweep at the next 5th flip will be comprehensive on these. Want to also run them individually now?"

### 6.7 One-time catch-up flow for existing products (post-v0.13.0 retrofit)

For products whose builds were in progress BEFORE v0.13.0 landed and have subsystems flipped to `[x]` without security/QA review (gap discovered in `ops-audit-agent` MH #6-10), the methodology supports a one-time recovery:

1. User invokes the orchestrator with: "Run a one-time catch-up sweep on subsystems MH #X to MH #Y that shipped without review."
2. Orchestrator invokes `senior-security-engineer` and `senior-qa-engineer` in build-phase review mode, scoped to the named subsystem range.
3. Findings flow back as if they were per-subsystem reviews — REJECT verdicts loop to the implementation specialist; APPROVE / APPROVE-WITH-NOTES are recorded in BUILD_STATUS history with a "post-hoc review" annotation.

This is not "skipped reviews are forgiven" — it's "the discipline reaches back to cover the prior gap."

### 6.8 Frontmatter and per-subsystem field reference

Recap of the fields this section adds to BUILD_STATUS.md:

**Frontmatter:**
- `pending-reviews: []` — list of `"<subsystem-id>: <reviewer-role>"` strings. Updated by orchestrator on each invocation.
- `completed-subsystems-since-sweep: 0` — counter; resets on catch-up sweep.

**Per-subsystem (in the checklist):**
- `security-review-required: true | false` — set per §6.1
- `qa-review-required: true | false` — set per §6.2
- `review-deferred: true | false` — opt-out per §6.6 (default false)
- `review-deferred-reason: "<text>"` — required when `review-deferred: true`

---

## 7. Surfacing it

- **`/status`** reads `BUILD_STATUS.md` for any in-flight build and surfaces the current focus + recent history as part of the pipeline-state snapshot.
- **`/menu`** mentions the current build's focus when relevant.
- **`/start-build <slug>`** if a `BUILD_STATUS.md` already exists, opens with it visible to the user before asking "want to continue from here, or re-orient?"
- **At any point, the user can `cat BUILD_STATUS.md`** or open it in their editor.

---

## 8. When BUILD_STATUS becomes stale

`BUILD_STATUS.md` going stale (work happens but the file isn't updated) defeats its whole purpose. Two signals it's stale:

1. **Git history shows commits in the product folder but BUILD_STATUS.md hasn't changed** in days.
2. **`/status` shows in-progress subsystems** that the user remembers finishing.

If either happens, `senior-software-engineer` does a reconciliation pass: read recent commits, infer what was done, update the file with backfilled history entries marked "(reconstructed from commit history)."

The reconciliation is a one-shot fix, not a substitute for keeping the file current as work happens.

---

## 9. Handoff to other artifacts

`BUILD_STATUS.md` is the **process** artifact. It cross-references but does not duplicate:

- **What** was built → individual subsystem artifacts (`SYSTEM_DESIGN.md`, `SCHEMA.md`, `API_CONTRACT.md`, code files).
- **What** to build next → the brief's must-haves (still authoritative).
- **Why** decisions were made → linked back to validation report + brief + the Decisions section here.

The file dies when the product is released. Past `BUILD_STATUS.md` files can be archived into the product folder as `BUILD_STATUS-v1.md`, `BUILD_STATUS-v2.md`, etc. for each release cycle.

---

*Last meaningful revision: 2026-05-30 (initial draft).*
