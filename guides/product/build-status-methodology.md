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
- [ ] **File storage** (senior-backend-engineer + senior-security-engineer) — pending
  - Required for: <must-haves>
- [ ] **Background jobs** (senior-backend-engineer) — pending
  - Required for: <must-haves>

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
| A specialist completes a subsystem | `senior-software-engineer` | `[>]` → `[x]`; timestamp + persona + artifact recorded; History entry added |
| A subsystem is added or removed (scope change) | `senior-software-engineer` | Checklist updated; History entry explains the change |
| A non-obvious decision is made | `senior-software-engineer` | Decisions section appended |
| Build pauses | `senior-software-engineer` | `build-status: paused`; History note |
| Build releases | `senior-software-engineer` | `build-status: released`; final History entry; file becomes frozen |
| Build is killed | `senior-software-engineer` | `build-status: killed`; History note with reason |

Specialists do NOT edit `BUILD_STATUS.md` directly. They report completion (per their persona's output format), and `senior-software-engineer` makes the update. This keeps the file's voice consistent and prevents merge conflicts.

---

## 6. Surfacing it

- **`/status`** reads `BUILD_STATUS.md` for any in-flight build and surfaces the current focus + recent history as part of the pipeline-state snapshot.
- **`/menu`** mentions the current build's focus when relevant.
- **`/start-build <slug>`** if a `BUILD_STATUS.md` already exists, opens with it visible to the user before asking "want to continue from here, or re-orient?"
- **At any point, the user can `cat BUILD_STATUS.md`** or open it in their editor.

---

## 7. When BUILD_STATUS becomes stale

`BUILD_STATUS.md` going stale (work happens but the file isn't updated) defeats its whole purpose. Two signals it's stale:

1. **Git history shows commits in the product folder but BUILD_STATUS.md hasn't changed** in days.
2. **`/status` shows in-progress subsystems** that the user remembers finishing.

If either happens, `senior-software-engineer` does a reconciliation pass: read recent commits, infer what was done, update the file with backfilled history entries marked "(reconstructed from commit history)."

The reconciliation is a one-shot fix, not a substitute for keeping the file current as work happens.

---

## 8. Handoff to other artifacts

`BUILD_STATUS.md` is the **process** artifact. It cross-references but does not duplicate:

- **What** was built → individual subsystem artifacts (`SYSTEM_DESIGN.md`, `SCHEMA.md`, `API_CONTRACT.md`, code files).
- **What** to build next → the brief's must-haves (still authoritative).
- **Why** decisions were made → linked back to validation report + brief + the Decisions section here.

The file dies when the product is released. Past `BUILD_STATUS.md` files can be archived into the product folder as `BUILD_STATUS-v1.md`, `BUILD_STATUS-v2.md`, etc. for each release cycle.

---

*Last meaningful revision: 2026-05-30 (initial draft).*
