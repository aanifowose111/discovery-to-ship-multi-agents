# MVP scoping methodology

How a `green-lit` idea card (per the discovery + validation guides) becomes a **shipping plan**. Scoping is the step between "we believe this is worth building" and the first line of production code.

This guide is intentionally biased against scope creep, against premature architecture, and against building code when a non-code MVP would teach us the same thing faster. It is also intentionally biased *for* using the user's strongest stacks (dockerized Flask for web, React Native for mobile, Python + PySide6 for desktop) unless the idea forces a stretch.

---

## 1. Purpose

A scoped MVP answers four questions in writing, *before* engineering starts:

1. **What is the single riskiest assumption** this product depends on?
2. **What is the smallest thing we can put in front of real users** that tests that assumption?
3. **What is explicitly *not* in the MVP**, so it doesn't creep in mid-build?
4. **What infrastructure and stack decisions** does the MVP commit us to — Flask, RN, DigitalOcean Spaces, `.env` strategy, hosting target, auth, observability?

If any of those four don't have a clear answer at the end of scoping, scoping is not done.

---

## 2. Operating principles

1. **The MVP tests the riskiest assumption, not the full product.** "Minimum viable" means *minimum sufficient to learn whether the assumption is true*. Everything else is deferred.
2. **Code is one option, not the default.** A concierge MVP (manual fulfillment behind a form) or a landing-page-with-waitlist test can validate the same assumption for a fraction of the build cost. See §10.
3. **The user's strongest stacks win ties.** Dockerized Flask backend, Jinja or React Native frontend, Python + PySide6 for desktop, Postgres or SQLite, DigitalOcean for hosting. Pick something else *only* when the idea has a hard requirement that one of these can't meet — and document that requirement.
4. **Estimate in honest hours, not hopeful weeks.** Solo builder working evenings + weekends ≈ 10-15 productive hours per week. A "2-week MVP" usually means 20-30 hours of focused work. Convert.
5. **Won't-haves are first-class.** Listing what is *out* of the MVP is as important as listing what's in. The won't-have list is what you re-read when you catch yourself adding "just one more feature".
6. **Stack stretches are learning costs.** Anything in the MVP that the user has never shipped to production before should be counted as build cost *plus* learning cost. If there are three of them, the MVP is too ambitious — pick one stretch at a time.

---

## 3. Inputs

To scope an MVP, the main Claude assembles:

| Input | Source |
|---|---|
| The green-lit idea card | `ideas/<run-id>/<slug>.md` — find via `find ideas -name "<slug>.md" -not -path "*/killed/*"` |
| The validation report | `market-research/<run-id>/validation-<slug>.md` (same `<run-id>` as the card) |
| User profile (founder fit, shipped stacks) | `CLAUDE.md` + the user-profile memory |
| Discovery + validation methodology guides | for shared vocabulary |

The validation report's "What I could not verify" lists and "Open questions for MVP scoping" section are the primary feedstock for identifying the riskiest assumption.

---

## 4. The riskiest-assumption framing

Every product idea is a stack of assumptions: that the problem exists, that people will pay, that we can build it, that we can reach them, that they'll keep using it after the novelty wears off, and so on. **The MVP only tests the riskiest one.**

To find the riskiest assumption, for each plausible assumption ask:

- **If we got this wrong, how badly does the product die?** (Severity)
- **How sure are we right now that we have it right?** (Inversely: how much risk?)

The assumption with the highest severity × risk is the one the MVP tests. Common candidates:

- *"Will anyone use this at all?"* — when the product depends on solving a problem people may have stopped caring about.
- *"Will they pay?"* — when the problem clearly exists but willingness-to-pay is unclear (B2C especially).
- *"Can we deliver the result reliably?"* — when the technical core is uncertain (LLM-output quality, scraping reliability, data-source coverage).
- *"Can we reach them at reasonable cost?"* — when the distribution hypothesis is shaky.
- *"Will they come back?"* — when retention, not acquisition, is the question (most consumer products eventually).

The MVP is designed to make this assumption visible. Other assumptions ride along on faith for now.

---

## 5. The MVP brief

Every scoped MVP produces one file at `web-apps/<slug>/MVP.md`, `mobile-apps/<slug>/MVP.md`, or `desktop-apps/<slug>/MVP.md` (whichever domain), using this format:

```markdown
---
slug: <same slug as the idea card>
date-scoped: YYYY-MM-DD
target-ship-date: YYYY-MM-DD
domain: web | mobile | desktop | hybrid
status: draft | in-scoping | green-lit-to-build | shipped | killed
---

# <Product name and one-line description>

## Riskiest assumption
The single thing we don't yet know that, if wrong, kills this product. One paragraph.

## Success criteria
What outcome — at first-10-users scale — tells us the assumption is true? Be specific. "1,000 signups" is not a first-10-users criterion. "7 of 10 invited users complete the core flow within 48 hours of signup and at least 4 return within a week" is.

## Must-haves
Features required to test the assumption. Each one tied back to *why* it is required (e.g., "user auth — required because the success criterion depends on identifying returning users"). If a must-have cannot be tied back, it is a could-have.

## Could-haves (deferred to v2)
Features that would make the product nicer but do not affect the success criterion. Explicitly listed so they are remembered, but not built.

## Won't-haves (explicitly out of this round)
Things we are deliberately choosing not to build, with one line of reasoning per item. This list is what we re-read when scope creeps.

## Stack (the choice that gates every infrastructure decision)
- **Web stack:** <workspace default: dockerized Flask + Jinja + vanilla JS | Next.js | Django | Rails | Phoenix | other + reason>
- **Web language:** <Python | TypeScript | Ruby | Elixir | Go | Java | other>
- **Mobile stack** (if any): <workspace default: React Native + Expo | Swift native | Kotlin native | Flutter | other + reason>
- **Mobile language:** <TypeScript | Swift | Kotlin | Dart | other>
- **Desktop stack** (if any): <workspace default: Python + PySide6 + PyInstaller | C# + Avalonia | Electron | Tauri | Flet | Qt C++ | other + reason>
- **Desktop language:** <Python | C# | TypeScript | Rust | C++ | other>
- **Database:** <Postgres | SQLite | MongoDB | other + reason>
- **File storage:** <DigitalOcean Spaces | AWS S3 | Cloudflare R2 | local fs | other + reason>
- **Hosting:** <DigitalOcean droplet | DO App Platform | Vercel | Fly.io | AWS | other + reason>
- **Auth:** <stack-default | OAuth provider | custom | other + reason>
- **Observability:** <stdout + platform logs | Sentry | Datadog | other>

> If the web stack is the workspace default (Flask), the workspace's web guides apply. If a different web stack, see §6.0 for the implications. Same applies to mobile.

## Infrastructure decisions
- **DigitalOcean Spaces:** needed? bucket name? IAM key scope? when configured?
- **`.env` strategy:** which secrets exist? where each one is set in dev vs. production?
- **Domain / DNS:** placeholder subdomain vs. real domain? who registers?
- **CI/CD:** GitHub Actions to DO? manual deploy via SSH? `docker compose pull && up`?

## Effort estimate
- Hours to first-user-shippable: <N>
- Calendar weeks at 10-15 hrs/week: <M>
- Top 3 effort risks (things most likely to blow the estimate)
  1. ...
  2. ...
  3. ...

## Stack stretches
Anything in the MVP that the user has *not* shipped in production before. Each is a learning cost on top of the build cost. Aim for zero or one stretch per MVP.

## Carried notes from validation
Notes from the three product reviewers (viability, competition, market-segment) that need to be monitored or addressed during build.
```

---

## 6. Stack and infrastructure decisions

A few decisions come up at scoping time for almost every MVP. Resolve them in the brief; don't defer them to mid-build.

### 6.0 Stack choice — the first decision

Before any infrastructure decision, the brief picks a **stack** for the web and mobile sides (whichever apply).

**Workspace defaults** (what this repo ships with build-domain guides for):

- **Web:** dockerized Flask (Python) + Jinja templates + small amount of vanilla JavaScript.
- **Mobile:** React Native with Expo (managed workflow) + TypeScript, paired with the Flask backend.
- **Desktop:** Python + PySide6 (Qt for Python) + PyInstaller. Cross-platform-capable; MVP is macOS-first per `guides/desktop/python-mvp-scaffold.md`.

These are the maintainer's choices, not requirements. The methodology guides (discovery, validation, this scoping guide, design, market research) are **stack-agnostic** — they work for any web, mobile, or desktop stack.

**If the brief picks the workspace defaults:** the existing build-domain guides apply directly — `guides/web/flask-mvp-scaffold.md`, `guides/web/flask-deploy-runbook.md`, `guides/web/do-spaces-integration.md`, `guides/web/flask-auth-patterns.md`, `guides/mobile/react-native-mvp-scaffold.md`, `guides/mobile/eas-build-and-update.md`, `guides/mobile/rn-app-store-submission.md`, `guides/desktop/python-mvp-scaffold.md`, `guides/desktop/packaging-and-distribution.md`.

**If the brief picks a different stack** (Next.js, Angular, Django, Rails, Phoenix, Go, Java/Spring on the web; Swift native, Kotlin native, Flutter on mobile; C# + Avalonia, Electron, Tauri, Flet, Qt C++ on desktop):

- Record the chosen stack in the brief.
- The build-domain guides above **do not apply** as-is. You will either:
  - Work without a stack-specific scaffold guide (Claude follows general first-principles + the agent-skills repo's stack-agnostic skills); or
  - Author a new stack-specific guide for your chosen stack (e.g., `guides/web/nextjs-mvp-scaffold.md`) and reference it from this section. Pull requests for new stack guides are welcome.
- The product-scope-reviewer will assess your stack-fit against your shipped experience, not against Flask/RN defaults.

**The brief must record the chosen stack explicitly.** "We will figure it out at build time" is not acceptable — stack choice cascades into every infrastructure decision below.

### 6.1 `.env` and secrets

The default recommendation for every Flask MVP in this project:

- **`.env.example`** committed at project root — template with empty values and inline comments explaining each key.
- **`.env`** at project root, **gitignored**, never committed. Local-only.
- **Production secrets** set via the hosting platform's env-var UI (DigitalOcean App Platform, droplet env file, etc.) — *not* by uploading `.env` to the server.
- **`SECRETS.md`** (gitignored) — a per-project plain-text note for the user only, listing where each secret currently lives (DO console, Stripe dashboard, etc.) so rotation is possible without spelunking.
- **In Flask:** read with `python-dotenv` for local; in production, rely on the platform's env vars being injected.

### 6.2 DigitalOcean Spaces

Default approach when storage is in scope:

- One Space (bucket) per product. Name pattern: `<product-slug>-<env>` (e.g., `findvil-prod`, `findvil-staging`).
- Region picked to match hosting region.
- IAM key scoped to *only* that bucket. Stored as env vars: `DO_SPACES_KEY`, `DO_SPACES_SECRET`, `DO_SPACES_REGION`, `DO_SPACES_BUCKET`, `DO_SPACES_ENDPOINT`.
- Accessed from Flask via `boto3` (DO Spaces is S3-compatible).
- Public vs. signed URLs: default to **signed URLs with short expiry** unless the product genuinely needs public objects.

### 6.3 Hosting target

Default to **DigitalOcean** to match the user's existing footprint. Choose between:

- **Droplet + `docker compose`** — most flexible, most ops. Pick when the product needs background workers, websockets, custom routing, or escapes the App Platform's runtime constraints.
- **App Platform** — managed runtime, less control, faster setup. Pick for stateless web services with a single Docker container and no exotic background work.

Either choice is fine; the brief just needs to say which and why.

### 6.4 Auth

Default to **`flask-login` + server-side sessions** for the simplest case. Move to OAuth (Authlib) only when the product requires third-party identity (Google, GitHub login) for UX reasons or distribution-channel reasons.

---

## 7. Reviewers

MVP scoping is reviewed by **two** assistants, not three. Both narrow:

### 7.1 `product-scope-reviewer`

**Lens:** Is this scope honest?

**Specifically tests:**
- Does each must-have trace back to the riskiest assumption?
- Are any could-haves or won't-haves dressed up as must-haves?
- Is the success criterion something that can plausibly be measured at first-10-users scale?
- Is the effort estimate honest given the solo-evenings cadence and the listed stretches?
- Are there hidden must-haves the brief forgot (auth, basic logging, error handling, deploy story)?

Returns the verdict format defined in `idea-validation-methodology.md` §5.

### 7.2 Code / architecture review — delegated to agent-skills

The technical pass uses **`code-reviewer`** from the cloned `external/agent-skills/agents/` (the 5-axis Senior Staff Engineer persona: correctness, readability, architecture, security, performance). We do not maintain our own web/mobile architecture reviewers — `code-reviewer` covers both domains.

**Lens:** Is this technical approach sound for *this* user shipping *this* MVP in the stated time?

**At MVP scoping, the reviewer specifically tests:**
- Is the stack appropriate, or is there an obvious simpler choice?
- Are there hidden integration risks (auth + storage + payments combinations that bite)?
- Are the stretches genuinely necessary, or is the user reaching for shiny tools?
- Does the deploy story actually work end-to-end?
- Are there security pitfalls in the proposed shape (CORS, CSRF, secret handling, file-upload validation)?

**For mobile MVPs (`domain: mobile` or `hybrid`):** also invoke **`mobile-ux-reviewer`** (ours, to be built later — mobile UX is not covered by the agent-skills personas) for an additional UX-lens pass.

Same verdict format as the validation reviewers.


---

## 8. Verdict integration and outcomes

After both reviewers return:

| Combination | Action |
|---|---|
| 2 × APPROVE | Advance to `green-lit-to-build` once user signs off. Hand off to build. |
| Any APPROVE-WITH-NOTES | Summarize notes. User signs off. Notes carry forward into the build's first-week checklist. |
| Any REJECT | Do not advance. Two options: (a) revise the brief and re-review, (b) drop back to validation if the rejection is "the riskiest assumption is wrong and the MVP cannot test it cheaply." Loop only once or twice; if scope cannot be made honest, the idea may be killed. |

The user signs off on the final brief before any code is written. Per the working style.

---

## 9. The scoping report

Each scoping run produces one file: `market-research/<run-id>/scoping-<slug>.md` (same `<run-id>` as the card's discovery cycle), containing:

1. **Brief snapshot** — the MVP brief at the moment scoping was reviewed.
2. **Reviewer verdicts** — both, full.
3. **Integration summary** — combined verdict + notes + any conflicts.
4. **Decision** — populated by the user (advance / revise / kill) with reasoning.
5. **First-week build checklist** — extracted from the notes, ready to act on once the build starts.

Like validation, the scoping report is dated and immutable; the brief itself may be edited later, but the report records the moment of decision.

---

## 10. When NOT to write code

For some assumptions, code is the wrong test. Two cheaper alternatives:

### 10.1 Landing-page + waitlist test

When the riskiest assumption is *"will anyone want this at all?"* — a single landing page describing the product, with an email-capture form, can answer it in a weekend. Run ads or post in the channel from the distribution hypothesis. If nobody signs up, the assumption was wrong; we did not waste a build cycle.

The MVP brief still gets written — the "stack" section just says "static page + email capture" and the success criterion is a signup count.

### 10.2 Concierge MVP

When the riskiest assumption is *"can we actually deliver the result?"* — and the result is something a human could do manually for a small number of users — do it manually first. The user fills out a form, the human (you, with Claude's help) fulfills the result over email or DM, the user gets the value, you learn whether the value is what they expected.

No production code. The "stack" section of the brief says "Google Form + manual email fulfillment + a notes file" and the success criterion is qualitative feedback from the first 5 users.

**Choose a non-code MVP when:** the riskiest assumption is about user desire or delivery quality, not about scale or polish. Choose to write code when the assumption is about whether the product *experience* — which depends on a working system — is good enough to convert.

---

## 11. Handoff to build

Once a brief is `green-lit-to-build` and signed off:

1. The build domain (`web-apps/<slug>/` or `mobile-apps/<slug>/`) is created with the brief inside.
2. The first-week build checklist (from the scoping report) becomes the initial task list.
3. Skills from the cloned agent-skills repo (especially the stage-specific code review skills) kick in for the actual build process.
4. The infrastructure decisions in the brief get acted on in the order they appear: repo skeleton → `.env.example` → docker compose → bare-bones deploy → first endpoint → first feature.

The brief stays in the product folder for the life of the project as the source of truth on what was promised vs. what was deferred.

---

*Last meaningful revision: 2026-05-29 (initial draft).*
