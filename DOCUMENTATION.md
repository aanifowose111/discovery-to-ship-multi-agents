# Documentation — the workspace, end to end

This is the comprehensive reference for using this Claude Code–orchestrated portfolio pipeline, from "I have a vague idea" to "I shipped a working product to my first 10 users." It complements `README.md` (which explains *what* the repo is and how to set it up) and `HELP.md` (which gives a per-command quick-reference) — this file explains **how to actually use the workspace end-to-end**, with examples, the reasoning behind each step, and the tools you'll touch at each phase.

If you only have a few minutes, read sections 1, 2, and 5. If you've got an hour, read the whole thing. You can also invoke `/documentation` from Claude Code at any time for a condensed version that incorporates your own current state.

---

## Table of contents

1. [Welcome — what this workspace is for](#1-welcome--what-this-workspace-is-for)
2. [The 60-second workflow overview](#2-the-60-second-workflow-overview)
3. [Before you start — the user-context onboarding](#3-before-you-start--the-user-context-onboarding)
4. [System requirements + setup](#4-system-requirements--setup)
5. [Phase 1 — Discovery & Validation](#5-phase-1--discovery--validation)
   - 5.1 [Market scan (`/scan`)](#51-market-scan-scan)
   - 5.2 [Idea brainstorm (`/discover`)](#52-idea-brainstorm-discover)
   - 5.3 [Validation (`/validate-card`)](#53-validation-validate-card)
   - 5.4 [MVP scoping (`/scope-mvp`)](#54-mvp-scoping-scope-mvp)
6. [Phase 2 — Initial MVP Build (deep dive)](#6-phase-2--initial-mvp-build-deep-dive)
   - 6.1 [What "build" actually means](#61-what-build-actually-means)
   - 6.2 [Stack choices in plain English](#62-stack-choices-in-plain-english-web--mobile--desktop)
   - 6.3 [`/start-build` walkthrough](#63-start-build-walkthrough)
   - 6.4 [The senior-engineer personas](#64-the-senior-engineer-personas)
   - 6.5 [Following along when you don't code](#65-following-along-when-you-dont-code)
   - 6.6 [When Fijara makes more sense](#66-when-fijara-makes-more-sense)
   - 6.7 [`BUILD_STATUS.md` as your dashboard](#67-build_statusmd-as-your-dashboard)
   - 6.8 [`/preview-product`](#68-preview-product)
7. [Phase 3 — v1 scoping + (optional) design phase](#7-phase-3--v1-scoping--optional-design-phase)
8. [Phase 4 — v1 build](#8-phase-4--v1-build)
9. [Phase 5 — Shipping (`/ship-app`)](#9-phase-5--shipping-ship-app)
10. [Parallel — Trend monitoring (`/trend-check`)](#10-parallel--trend-monitoring-trend-check)
11. [The reviewer-decision model — why *you* decide, not the reviewers](#11-the-reviewer-decision-model--why-you-decide-not-the-reviewers)
12. [Workspace conventions you should know](#12-workspace-conventions-you-should-know)
13. [Utility commands reference](#13-utility-commands-reference)
14. [Scripts + helper skills reference](#14-scripts--helper-skills-reference)
15. [Common scenarios, troubleshooting, going deeper](#15-common-scenarios-troubleshooting-going-deeper)

---

## 1. Welcome — what this workspace is for

This workspace turns a Claude Code session into a **portfolio pipeline**: a repeatable way to take a product from "vague hunch" all the way through to "shipped, in front of real users." It is opinionated about *how* that journey should run — reviewer subagents catch the silent failures, slash commands enforce checkpoints, methodology guides give every phase a written contract — and it ships with three default build stacks (Flask + Jinja for web, React Native + Expo for mobile, Python + PySide6 for desktop), but the underlying methodology is stack-agnostic.

**Who this workspace is for**

- Solo or small-team founders building multiple products over time, who want a repeatable process instead of re-deciding the same questions every cycle.
- Builders who use Claude Code daily and want a structured way to drive bigger work than ad-hoc prompts.
- Anyone who wants reviewer-assistant pushback on idea quality, market fit, scope discipline, and code/security/QA — before the cost of the mistake compounds.
- Forkers who want to start from a working pipeline and customize the defaults for their own stacks or methodology preferences.

**Who this workspace is NOT for**

- People looking for a one-prompt "build me an app" experience. This workspace is structured and deliberate; it expects you to make decisions at each checkpoint.
- Teams that have already standardized on a heavy framework (e.g., a 50-person product org with Jira + Linear + custom RFCs) — the pipeline duplicates infrastructure you already have.
- People who don't want to use Claude Code as their primary interface. The whole pipeline runs through Claude Code's terminal.

**Time and energy expectations**

- **Discovery + validation per idea:** 1–3 hours of focused review, spread across a few sittings.
- **MVP scoping:** 30–60 minutes once the card is green-lit.
- **Initial MVP build:** 10–40 hours depending on scope (the brief estimates this honestly).
- **Optional design phase:** 1–3 weeks elapsed (designer works asynchronously).
- **Ship to first 10 users:** a few hours once the MVP build is substantially complete.

If a phase ever feels rushed or padded, you can override the defaults at any checkpoint — every slash command stops and asks you before advancing.

---

## 2. The 60-second workflow overview

```
   ┌──────────────────────────┐
   │  Fresh Claude Code       │
   │  session in the repo     │
   └────────────┬─────────────┘
                │
        ┌───────▼────────┐
        │ INTERESTS.md   │  ← strict onboarding interrupt
        │ exists?        │     (Rule A in CLAUDE.md)
        └───┬────────┬───┘
            │ no     │ yes
            ▼        ▼
   ┌──────────────┐  ┌──────────────────────────┐
   │ Populate     │  │   Normal session entry   │
   │ INTERESTS +  │  │   Claude reads context   │
   │ IDEAS        │  │   and waits for your     │
   │ (one-time)   │  │   first command          │
   └──────┬───────┘  └────────────┬─────────────┘
          └──────────────┬────────┘
                         ▼
                    /scan           ←  market scan, candidate territories
                         │
                         ▼
                    /discover       ←  brainstorm idea cards, triage
                         │
                         ▼
                  /validate-card    ←  4 reviewers per card (in parallel:
                         │              viability / competition / market-segment / pricing)
                         ▼          ←  YOU decide: advance / revise / kill
                    /scope-mvp      ←  MVP brief + 2 reviewers
                         │              (pre-build checkpoint: pick design-path
                         ▼               + build-support)   ← YOU decide
              ┌──────────┴───────────┐
              │   DESIGN PHASE       │  ← fires for BOTH paths now (v0.11.0+)
              │                      │
              │  /research-design    │  ← per-surface research (public/auth/
              │       │              │     user/admin/employee), trends,
              │       │              │     interactive ref-URL checkpoints
              │       ▼              │     ← YOU sign off on the research
              │  ┌────┴─────┐        │
              │  │ branches │        │
              │  │ on path  │        │
              │  └─┬──────┬─┘        │
              │    │      │          │
              │ claude   hired       │
              │ -led     │           │
              │    │      │          │
              │    ▼      ▼          │
              │ /draft   /draft      │
              │ -design  -design     │
              │ -spec    -brief      │
              │    │      │          │
              │    │      ▼          │
              │    │  human designer │
              │    │  ↓ Figma        │
              │    │  handoff capture│
              │    │  (tokens.json,  │
              │    │   screenshots)  │
              │    │      │          │
              │    └──┬───┘          │
              └───────┼──────────────┘
                      ▼
                 /start-build       ←  orchestration by senior-software-engineer.
                      │                 Gates on the design artifact existing
                      │                 (DESIGN_SPEC.md / handoff / light research).
                      │                 Build proceeds subsystem by subsystem,
                      │                 narrated handoffs between specialists.
                      │
                ┌─────┴─────────────────────────────────┐
                │  BUILD LOOP                           │
                │  (you'll re-enter often)              │
                │                                       │
                │  /recollect <slug>     ← read-only    │
                │   ↑                      "where am I" │
                │   │ before                            │
                │   │ deciding                          │
                │   │                                   │
                │  /continue-build <slug> [--hint]      │
                │     [--from <file>]                   │
                │                ↑                      │
                │                resume after break,    │
                │                disambiguates across   │
                │                multiple in-flight     │
                │                products. mtime-aware. │
                │                                       │
                │  /rework <slug> <changes>             │
                │  /consolidate <slug>                  │
                │  /preview-product <slug>              │
                │  /infra-cost <slug>                   │
                │  /reprice <slug>                      │
                │                                       │
                └─────┬─────────────────────────────────┘
                      ▼
                 /ship-app          ←  release-readiness gate (QA + security
                      │                pre-flight) → deploy → verify
                      ▼
                Shipped to first 10 users
                      │
                      ▼
              Did the riskiest assumption hold?
                 yes ──→  /scope-v1 <slug>    ←  V1 brief + same 2 reviewers as
                                                 /scope-mvp; design-path repicker
                                                 (claude-led-continued / hired /
                                                 hybrid-light-refresh) — then
                                                 loop back to research + build.
                  no ──→  kill the card, move on (or /revive-card later)
```

In parallel with all of the above:

- **`/trend-check`** runs on a weekly cadence (or triggered by an external event) and recommends which downstream commands to re-run if something material has shifted.
- **`/recollect <slug>`** and **`/status`** are read-only orientation commands — `/recollect` gives a deep dive on one specific product (everything that exists for it), `/status` gives a workspace-wide snapshot across all in-flight work. Use `/recollect` when returning to a product after a break; use `/status` to remember "what am I working on across the portfolio?"
- **`/menu`** is the always-available command map; **`/documentation`** opens this guide.

---

## 3. Before you start — the user-context onboarding

When you first run any command in a fresh Claude Code session, the workspace checks two things:

1. Does `user-context/INTERESTS.md` exist?
2. Does `user-context/IDEAS.md` exist?

If **either** is missing AND the audit log (`user-context/audit-log.jsonl`) does not yet contain an `onboarding-skip` entry, Claude interrupts your request with a one-time onboarding flow that captures:

1. **Your interests** — professional background, hobbies, industries you know well, anything you'd consider building. Saved to `user-context/INTERESTS.md`.
2. **Your seed ideas** — products you've thought about but haven't built. Even one-liners are fine. Saved to `user-context/IDEAS.md`.

This onboarding is **strict**: it fires on the very first message of every fresh session where either file is missing and no skip has been recorded, regardless of what you typed. The reason is straightforward — without that context, `/discover` and `/scan` fall back to less-targeted output, and the cards they produce are more likely to be killed in validation. That wastes a real hour of your time per killed card. The onboarding takes maybe two minutes and reframes everything downstream.

| File | Purpose | Required? |
|---|---|---|
| `user-context/INTERESTS.md` | Your professional background, strengths, domain expertise — used by `/scan` and `/discover` as the founder-fit lens. | Strongly recommended; gates the onboarding interrupt |
| `user-context/IDEAS.md` | Your seed-ideas backlog, distinct from `ideas/` (which holds validated cards from formal discovery cycles). Drives the mode picker in `/scan` and `/discover`. | Strongly recommended; gates the onboarding interrupt |
| `user-context/POLICY.md` | Your personal coding style, framework preferences, voice, hard rules — overrides workspace defaults and senior-engineer-persona conventions for matters of taste. | Optional |
| `user-context/audit-log.jsonl` | Auto-written by Claude when you make important user-driven decisions (skipping onboarding, deleting a project, killing/reviving a card), when build milestones land (project initialized, subsystem completed, ready-to-deploy reached, shipped), and free-text notes you add via `/log`. Gates the onboarding re-prompt and gives you a per-product build journal. | Auto-managed |

All four live files are **gitignored** — your context stays local to your clone and never enters git. Templates ship in the repo as `<file>.<ext>.example` so you can copy them as starting points (`cp user-context/INTERESTS.md.example user-context/INTERESTS.md`).

**The only command that bypasses the onboarding interrupt is `/documentation`** — because forcing onboarding before letting you read about the workspace would be circular. Every other command (including `/scan`, `/discover`, `/menu`, etc.) triggers the onboarding flow on the first message of a fresh session when either file is missing and no skip has been logged.

**If you opt to defer onboarding** ("Prefer to update later" in the picker), Claude writes an `onboarding-skip` entry to the audit log so it does NOT ask again on future sessions — your skip is respected permanently until you delete it. View skips with `/log type onboarding-skip`, and re-enable onboarding by deleting the entry: `/log delete <id>`. In the meantime, the system still runs but in degraded mode. `/scan` falls back to a no-founder-fit "open scan" mode rating territories on freshness × reachability only. `/discover` will ask for a one-line context or run open discovery. Both will produce broader, less-targeted output. Populate `INTERESTS.md` and `IDEAS.md` whenever you're ready and the next run will be properly grounded.

**When `IDEAS.md` is populated, `/scan` and `/discover` offer a mode picker** — instead of running the default sweep blindly, you can choose to focus the work on your seed ideas, ignore them, or compare them against fresh discoveries. See §5.1 and §5.2 for the per-command mode details.

---

## 4. System requirements + setup

Before you run any phase command, your machine needs the right tools and the workspace needs a clean setup. Two commands handle this:

| Command | What it checks |
|---|---|
| `/system-check` | OS, CPU architecture, CPU cores, RAM, free disk, internet connectivity, plus required CLI tools (`git`, `gh`, `pandoc`, `typst`, Python ≥3.10, Node.js ≥20) and optional tools (`docker`, `PySide6`, `PyInstaller`). Output is a comparison table with required / recommended / your value / ✓⚠✗ status. Read-only — never modifies anything. |
| `/setup` | Pre-flight verification on a new clone or new machine. Checks the same tools as `/system-check` plus git identity, GitHub auth, submodule initialization, agent-skills file copies. Surfaces a clear punch list with exact install commands. Safe to run multiple times. |

**What to do**

| When | Run |
|---|---|
| Brand-new clone or brand-new machine | `/setup` first (deeper) and `/system-check` (lighter; just specs) |
| Returning to the workspace after a break | `/setup` once to confirm nothing rotted |
| About to start a desktop build for the first time | `pip install PySide6 pyinstaller` — these are optional until you actually build a desktop product |
| Forker (non-owner) wanting to contribute back | `/acknowledge-contributing` — required one-time confirmation that you've read `CONTRIBUTING.md` |

**Common gotchas**

- macOS users: `xcode-select --install` gives you `git` if you don't already have it; Homebrew (`brew`) is needed for most other tools.
- Windows users: install **WSL2 + Ubuntu** rather than running raw Windows. The workspace assumes a POSIX-ish shell.
- Node.js: install version 20 LTS. The React Native and Expo ecosystem expects this.
- Python: 3.10 minimum, 3.11+ recommended. The scripts use modern type-hint syntax.

---

## 5. Phase 1 — Discovery & Validation

This is where you take the workspace from "empty" to "I know what to build first." It runs in four steps, each ending at a checkpoint where you sign off before the next step begins. Most idea cards die here, by design — better to kill a bad idea after one hour of validation than after forty hours of building.

### 5.1 Market scan (`/scan`)

**What it does**

A market scan is the *upstream* of discovery. It does not produce ideas; it produces **candidate territories** — segments × categories × situations that are worth mining for ideas in the next discovery cycle. The scan looks for fresh capability shifts (model releases, API openings, regulatory changes), funding signals (where VCs are landing recent rounds), pain signals (Reddit complaints, G2 one-star reviews), and adjacencies to what you've already shipped or know well.

**What you input**

```
/scan                          # broad scan (no specific hypothesis)
/scan broad                    # same as above (explicit)
/scan focused <topic>          # focused scan on one hypothesis
```

Claude will check `user-context/INTERESTS.md` first to ground the founder-fit lens. If `INTERESTS.md` is missing, it offers to fall back to open-scan mode or asks you for inline context.

**If `user-context/IDEAS.md` is populated** with real seed ideas (not just placeholders), Claude then offers a mode picker before the sweep starts:

| Mode | Behavior | When to pick |
|---|---|---|
| **Focused** | Prioritize territories adjacent to your seed-idea clusters. | When your seeds are coherent and you want the scan to deepen that map. |
| **Open** | Default scan behavior — sweep broadly, no seed-ideas constraint. | When you want fresh territories independent of what's already on your mind. |
| **Hybrid + compare** *(recommended default)* | Open sweep, then add a "compared against your seeds" subsection naming which discovered territories overlap / complement / threaten the seeds. | Best of both. |

The chosen mode is recorded at the top of the report under a `Mode:` line. `IDEAS.md` shapes which territories rank higher; `INTERESTS.md` still defines the founder-fit lens used for scoring — modes do not override that.

**What comes out**

A file at `market-research/<run-id>/scan.md` with frontmatter `status: draft` and a structured report:

- **Aperture** — what the scan was looking for
- **Source sweep table** — 7 source families × density rating × notes with citable URLs
- **Candidate territories** — 3-7 territories, each with: segment, anchor, distribution channel, founder-fit, priority (HIGH/MEDIUM/LOW)
- **Unresolved signals** — leads that didn't aggregate into a territory yet
- **Recommended seeds** — 2-3 territories to feed the next `/discover`
- **What this scan did not look at** — deliberate exclusions

**Status meanings**

| Status | Means |
|---|---|
| `draft` | Just generated; awaiting your sign-off |
| `active` | You've signed off; this is the canonical input for the next `/discover` |
| `archived` | Superseded by a newer scan (manually marked) |

**When to stop / what's next**

`/scan` always stops at the draft checkpoint. To advance to `active`, you tell Claude "advance the scan to active" — Claude updates the frontmatter. Then run `/discover` to mine the recommended seeds for actual ideas.

**Why it works this way**

Discovery without a scan often produces a batch of cards that all fail at the same validation step (usually distribution or founder fit). The scan exists to prevent that by deciding *where* to brainstorm before the brainstorm runs. Smaller candidate list, sharper candidates — five well-defended territories beat fifteen vague ones.

**Common gotchas**

- Without `INTERESTS.md`, the scan runs in open-scan mode and may produce territories that don't fit your strengths. Populate `INTERESTS.md` first for best results.
- If you have an active scan less than 90 days old that hasn't been exhausted, running another scan is usually wasted work. The previous one is still valid.

---

### 5.2 Idea brainstorm (`/discover`)

**What it does**

`/discover` takes the active scan's recommended territories (or territories you pass explicitly) and brainstorms a batch of **at least 10 idea cards** — each one a specific product concept with a problem statement, target user, current alternatives, distribution hypothesis, and provisional success criterion. Then it triages the cards into HIGH/MEDIUM/LOW priority based on a 5-dimension rubric (problem severity, market reachability, founder fit, capability shift alignment, distribution feasibility) and writes a top-3 callout.

**What you input**

```
/discover                                # use the active scan's recommended seeds
/discover ai-eval-infra-for-domain-experts
/discover territory-1, territory-2       # restrict to specific territories
```

If no active scan exists, Claude offers to run an **inline lightweight scan** using `user-context/INTERESTS.md` (or ask you for inline context if INTERESTS.md is missing). This makes `/discover` a one-command bootstrap when you want to skip the formal scan.

**If `user-context/IDEAS.md` is populated** with real seed ideas, Claude then offers a mode picker before brainstorming begins:

| Mode | Behavior | When to pick |
|---|---|---|
| **(a) Promote seeds** | Skip the brainstorm entirely. Convert each seed in `IDEAS.md` directly into a formal card (`ideas/<run-id>/<slug>.md`), score on the rubric, triage. The ≥10-cards floor does NOT apply — you get however many seeds you have. | When you already know what you want to validate and want to skip ideation. |
| **(b) Full discovery (ignore seeds)** | Standard brainstorm of 10+ candidates from territories / trends / capability shifts; do not pull from `IDEAS.md`. | When seeds feel stale or you want a fresh angle. |
| **(c) Hybrid + compare** *(recommended default)* | Brainstorm 10+ candidates AND add one card per seed idea. The triage table compares them side-by-side with a "Seeds vs. brainstormed candidates" subsection. | Best for "I have ideas but want to see how they stack up against fresh discoveries." |

Cards drawn from `IDEAS.md` get `source: user-context/IDEAS.md` in their frontmatter; brainstorm cards keep the regular source tag. From the triage onward, all cards are treated identically — they compete on the same rubric. If `IDEAS.md` is missing or only has placeholders, this picker is skipped and the cycle proceeds as full discovery (mode b implicit).

**What comes out**

- **One file per idea card** at `ideas/<run-id>/<slug>.md` — frontmatter (slug, run-id, source, territory, status) plus problem / current alternatives / proposed solution / why now / target user / distribution hypothesis / risks.
- **One triage file** at `market-research/<run-id>/triage.md` — table of all cards, rubric scores, HIGH/MEDIUM/LOW buckets, top-3 callout, hard-kill rules.
- **Killed cards** move to `ideas/killed/<run-id>/<slug>.md` if any card fails a hard-kill rule (e.g., territory previously killed, slug collision, market signal contradicts).

The **same `<run-id>` is shared** by all cards in this cycle and by every downstream artifact (validations, scopings). This is the canonical project-grouping mechanism.

**Status meanings**

| Card status | Means |
|---|---|
| `discovered` | Just created; awaiting your sign-off on the top 3 |
| `in-validation` | You picked it; `/validate-card` is or has run |
| `validated` | Three reviewers have given verdicts; awaiting your decision |
| `green-lit` | You advanced it; ready for `/scope-mvp` |
| `green-lit-to-build` | MVP brief drafted + scope-reviewed; ready for `/start-build` |
| `building` | Build phase in progress |
| `shipped` | First 10 users see it |
| `killed` | Moved to `ideas/killed/<run-id>/` with a kill reason |

**When to stop / what's next**

`/discover` always stops after the triage. Tell Claude which 2-3 of the top-3 cards to validate; then run `/validate-card <slug>` for each (these can run in parallel — they're independent).

**Why it works this way**

Brainstorming without territory boundaries produces undifferentiated cards. Triage without a written rubric produces personal-favorite bias. The double structure (territory-bounded + rubric-triaged) is designed to surface 2-3 *non-obvious* cards per cycle, not 10 *obvious* ones.

**Common gotchas**

- If most of your cards from a previous cycle died at the same validation dimension (e.g., all rejected on "competitive moat"), the territories were probably wrong. Run `/scan` again before another `/discover`.
- A 10-card batch with one HIGH is often better than a 15-card batch with no HIGHs. Don't pad the count.

---

### 5.3 Validation (`/validate-card`)

**What it does**

`/validate-card <slug>` runs three reviewer subagents in parallel on a green-bucket idea card. Each reviewer brings a narrow lens; together they triangulate whether the card is worth scoping into an MVP.

| Reviewer | Lens — what they assess |
|---|---|
| `product-viability-reviewer` | Does the problem exist badly enough, for enough people, based on citable external evidence? Severity, frequency, willingness-to-pay. |
| `product-competition-reviewer` | Who's already in this space (including non-obvious substitutes), what do they charge and ship, would your differentiation story survive contact with the real market? |
| `market-segment-reviewer` | Is the segment crisp and big enough, reachable through a credible first-100-users channel, broadly willing to pay? |
| `product-pricing-reviewer` | Is the **specific** proposed price defensible against comparable products' real pricing, segment willingness-to-pay signals, and solo-builder unit economics? Returns 2-3 strategic pricing options ranked recommendation-first — you pick one (or type your own override) at decision time. |

Each reviewer reads the card, the discovery methodology guide, and `CLAUDE.md`. Each fetches the web for current signals. Each returns a structured verdict (`APPROVE` / `APPROVE-WITH-NOTES` / `REJECT`) plus reasoning and citations. The pricing reviewer additionally returns comparable-pricing / unit-economics / suggested-options blocks.

Note the overlap between market-segment and pricing: market-segment asks *whether* the segment will pay anything; pricing asks *what amount* they'll pay. The two work together — market-segment establishes the ballpark, pricing pins the number.

**What you input**

```
/validate-card <slug>
```

The card must exist at `ideas/<run-id>/<slug>.md` with `status: discovered`. Run multiple validations in parallel by issuing multiple `/validate-card` invocations.

**What comes out**

A file at `market-research/<run-id>/validation-<slug>.md` — frontmatter (slug, run-id, date-validated, status: `reviewed — awaiting-user-decision`) plus the three reviewer verdicts integrated into a single report. Each reviewer's section has: verdict, top-3 findings, citations, what could change my mind.

The report also has a **Recommended decision** line at the bottom — a synthesis of the three verdicts into one advance/revise/kill suggestion. Importantly, this is *advisory*. The actual decision is yours; see §11 for the full reasoning.

**Status meanings**

| Status | Means |
|---|---|
| `reviewed — awaiting-user-decision` | Validation report just written; you decide what's next |
| `decision-recorded — advanced` | You chose advance; card status updates to `green-lit` |
| `decision-recorded — revised` | You chose revise; card status stays `discovered` after edits |
| `decision-recorded — killed` | You chose kill; card moves to `ideas/killed/<run-id>/` with kill reason |

**When to stop / what's next**

`/validate-card` always stops at the user-decision checkpoint. To proceed:

| Decision | What to do |
|---|---|
| **Advance** | Run `/scope-mvp <slug>` — drafts the MVP brief and runs two more reviewers (scope + code). |
| **Revise** | Edit the card directly (e.g., sharpen the differentiation vs. competitors the reviewer flagged), then re-run `/validate-card <slug>`. |
| **Kill** | Tell Claude "kill the `<slug>` card" — Claude moves `ideas/<run-id>/<slug>.md` → `ideas/killed/<run-id>/<slug>.md` and adds a kill reason to the frontmatter. (No dedicated slash command; it's a one-line conversational step.) |

**Why it works this way**

The split between reviewers (who advise) and you (who decide) is intentional. The reviewers each evaluate one dimension; the synthesis across dimensions is a strategic call that depends on your portfolio appetite, your risk tolerance, your timeline, and information that isn't in the card. See §11 for the deeper rationale.

**Common gotchas**

- Don't auto-advance every APPROVE. An APPROVE-WITH-NOTES is often the most useful verdict — it means the reviewer thinks the card has legs but flagged something specific to fix. Reading those notes is the highest-value 5 minutes of the validation flow.
- A REJECT from one reviewer doesn't kill the card. Read the reasoning. Some REJECTs are addressable in a card revision; some are fundamental.

---

### 5.4 MVP scoping (`/scope-mvp`)

**What it does**

`/scope-mvp <slug>` turns a green-lit card into a **shipping plan**: the smallest thing you can put in front of real users to test the card's riskiest assumption. It picks the stack (or asks you to), identifies the must-haves traced back to the riskiest assumption, lists the could-haves and won't-haves explicitly, estimates honest hours, and surfaces stack stretches. Then it runs two reviewers: `product-scope-reviewer` (for scope discipline) and `code-reviewer` (for architecture / security / performance pre-build).

**What you input**

```
/scope-mvp <slug>
```

The card must be `status: green-lit`. The first thing Claude asks is the stack choice. Workspace defaults:

| Domain | Default stack |
|---|---|
| Web | Dockerized Flask + Jinja + vanilla JS (Python) |
| Mobile | React Native + Expo + TypeScript |
| Desktop | Python + PySide6 + PyInstaller |

You can pick any other stack (Next.js, Django, Rails, Swift, Kotlin, Flutter, C# + Avalonia, Electron, Tauri, …); the methodology is stack-agnostic. The brief records the chosen stack.

**What comes out**

- **MVP brief** at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md` — riskiest assumption, success criterion (measurable at first-10-users scale), must-haves traced to the assumption, could-haves (deferred to v2), won't-haves (explicitly out), stack, infrastructure decisions (`.env`, storage, hosting, auth, observability), effort estimate in honest hours, stack stretches, carried notes from validation.
- **Scoping report** at `market-research/<run-id>/scoping-<slug>.md` — the two reviewer verdicts (scope + code), integrated decision (APPROVE / APPROVE-WITH-NOTES / REJECT), notes carried forward.

After the report, there's a **second checkpoint** — Claude asks two pre-build questions:

| Question | Options |
|---|---|
| Design path | (a) **claude-led** — Claude runs full design research → drafts implementation-ready `DESIGN_SPEC.md` → builds directly from it. No external designer. · (b) **hired** — Claude runs research → drafts Figma-handoff `DESIGN_BRIEF.md` → you brief a human designer → they deliver Figma → Claude implements from the handoff. |
| Build support | (a) I'll follow along with Claude · (b) I need help — recommend [Fijara](https://fijara.com) (the maintainer's dev service) |

Both picks are recorded in the brief's frontmatter and shape downstream behavior. **Both design paths run full design research** (via `/research-design`) — the difference is the second artifact (`DESIGN_SPEC.md` vs `DESIGN_BRIEF.md`) and whether a human designer is in the loop. The path-formerly-known-as-"generic" has been renamed `claude-led` since v0.11.0 because the new flow produces a real implementation-ready spec, not "Claude wings it."

**Status meanings**

| Brief status | Means |
|---|---|
| `in-scoping` | Brief drafted; awaiting your sign-off after the reviewer report |
| `green-lit-to-build` | You signed off; pre-build decisions captured; ready for `/start-build` |
| `building` | Build in progress |
| `shipped` | Shipped to first 10 users |
| `killed` | Decision was kill after scoping (rare but allowed) |

**When to stop / what's next**

`/scope-mvp` stops twice: once after the reviewer integration (for your scope decision: build / revise / kill), once after the pre-build picks. After both checkpoints clear, run `/start-build <slug>` to enter the build phase.

**Why it works this way**

Most MVPs fail one of three ways: scope creep, premature architecture, or building code when a non-code test would have validated the assumption faster. The scoping methodology guide (`guides/product/mvp-scoping-methodology.md`) §2 is explicit about all three. The brief format forces you to answer "what's the *one* riskiest assumption?" and trace every must-have back to it — features that don't trace become could-haves automatically.

**Common gotchas**

- If your must-have list has 10+ items, the brief is too ambitious for an MVP. The methodology guide §5 expects 3-6 must-haves typically.
- "Stack stretches" — anything you haven't shipped to production before — are learning costs *on top of* the build estimate. Aim for zero or one stretch per MVP.
- For a desktop-only brief, the default build order shifts from "database first" to "project tree + core models first." Stack-specific defaults are documented in `guides/product/build-status-methodology.md` §3.

---

## 6. Phase 2 — Initial MVP Build (deep dive)

This is the section that gets the most prose, because if you're not already familiar with web/mobile/desktop application development, the *build* is where the workspace can feel intimidating. The good news: you don't have to write a line of code yourself. The senior-engineer subagents handle the implementation; your job is to follow along, ask questions, sign off at checkpoints, and make product judgment calls.

### 6.1 What "build" actually means

For a non-developer, "build" sounds like one big unknown thing. Here's what it actually is, broken down into concepts:

| Concept | Plain English |
|---|---|
| **Source code** | A folder of text files (`.py`, `.tsx`, `.html`, etc.) that describe what the app does. Claude writes these. You read them if you want; you don't have to. |
| **Backend / API** | The part of the app that runs on a server (a remote computer) and handles things users can't see directly — storing data, checking who's logged in, doing calculations. For web apps the default is Flask (a Python framework). |
| **Frontend / UI** | The part users actually see and click — the web page, the mobile screen, the desktop window. For web it's Jinja templates + vanilla JavaScript; for mobile it's React Native; for desktop it's PySide6 widgets. |
| **Database** | Where the app stores data so it persists between sessions. The default is Postgres for web/mobile, SQLite for desktop. |
| **Deploy** | The act of putting the source code onto a server (or packaging it into a downloadable file for desktop) so users can actually reach it. The default web host is DigitalOcean; mobile goes through App Store / Play Store; desktop goes through PyInstaller bundles. |
| **MVP (minimum viable product)** | A v0 that's just enough to put in front of your first 10 users and learn whether the core assumption holds. NOT a polished v1. |

Every build the workspace runs goes through roughly the same arc, regardless of stack:

1. **Database schema** — decide what data the app stores
2. **Models** — translate the schema into code objects the app can use
3. **API contract** — decide how the frontend talks to the backend (the list of URL endpoints)
4. **API implementation** — write the backend code
5. **Auth** — handle "who is logged in, what can they do"
6. **Frontend skeleton** — the basic shell of the UI
7. **Per-feature widgets/pages** — one feature at a time, tested as each lands
8. **Integration tests** — automated checks that frontend + backend work together
9. **Ready to deploy** — code is healthy, tests are green, you can hand it off to the deploy step (which is its own gated phase via `/ship-app`).

You'll see this sequence happen in narrated, observable steps when you run `/start-build`. Every step is a separate subsystem in `BUILD_STATUS.md` (see §6.7).

### 6.2 Stack choices in plain English (web / mobile / desktop)

You'll be asked at `/scope-mvp` time to pick a stack. Here's the plain-English version:

| Stack | Best for | Looks like, to the user | The maintainer's stack |
|---|---|---|---|
| **Flask + Jinja + vanilla JS (web default)** | Web apps people open in a browser. Best when the product is browser-first or needs to be accessible from any device with a browser without an install step. | Like Gmail, GitHub, Notion-in-browser. | Python end-to-end; the maintainer has shipped findvil.com and fijara.com on this. |
| **Next.js + React (alternative web)** | Same as above but with a more dynamic SPA feel, better SEO controls, and a different deployment story (Vercel-style). Pick this if you specifically want the React ecosystem. | Like Vercel-hosted apps, dynamic dashboards. | Not a workspace default — you'll build from first principles. |
| **React Native + Expo (mobile default)** | Mobile apps people download from the App Store / Play Store. Best when the product is fundamentally mobile — needs the phone's camera, push notifications, on-the-go usage. | Like Instagram, Discord, Notion-mobile. | The maintainer shipped Fijara's mobile app on this. |
| **Python + PySide6 + PyInstaller (desktop default)** | Desktop apps people install and run locally on Mac/Windows/Linux. Best for productivity tools, single-user utilities, anything that needs offline use or local file access. | Like Notion-desktop, Cursor, VS Code (though those use Electron). | Maintainer-aligned: Python end-to-end, native-looking, cross-platform. |
| **C# + Avalonia (alternative desktop)** | Same as above but if you specifically want static typing and the .NET ecosystem. | Same look as Qt-based apps. | Not a workspace default. |

**How to decide:**

| Question | Lean toward |
|---|---|
| Does the product need to be findable via Google? | Web |
| Does the product need the phone's camera, GPS, or push notifications? | Mobile |
| Does the product need to work offline, or access local files heavily? | Desktop |
| Are users at desks during the workflow? | Web or desktop |
| Are users on the go during the workflow? | Mobile |
| Do you want the lowest install friction? | Web (no install) |
| Do you want the best perceived "real software" feel? | Desktop or native mobile |

You can also pick **hybrid** — web + mobile, or web + desktop, etc. The brief records the choice and `/start-build` orchestrates them in sensible order (usually API + web first, then the other clients).

### 6.3 `/start-build` walkthrough

When you run `/start-build <slug>`, here's what happens, narrated step by step.

1. **Pre-flight verification** — Claude checks that the brief exists with `status: green-lit-to-build`, the pre-build decisions are recorded, and the project folder is ready.
2. **Senior-software-engineer invoked** — this is the *orchestrator* persona. It reads the brief, the design research and brief (if they exist), and `CLAUDE.md`, then asks you three orientation questions:
   - **Build order** — web/mobile/desktop/hybrid order based on the brief's domain. For hybrid, the default is "API + web first, then mobile/desktop second" — but you can override.
   - **Scope** — MVP (the must-haves only — recommended) vs. fully-featured (must-haves + could-haves in one pass).
   - **First subsystem to tackle** — defaults to "database design" for web/mobile, "project tree + core models" for desktop-only. The orchestrator lists the standard ordering so you can see what comes next, but you can pick any starting subsystem if you have a reason.
3. **Routing to the first specialist** — based on your answers, the orchestrator says: "I'll invoke `senior-database-engineer` next to design the schema" (or whichever specialist owns the first subsystem). It also writes the initial `BUILD_STATUS.md` to the project folder.
4. **Subsystem by subsystem** — for each subsystem in the standard order, the orchestrator narrates the handoff ("now `senior-backend-engineer` is going to define the API contract from this schema, expected output is `API_CONTRACT.md` and should take 15-20 min"), invokes the specialist, integrates the output, marks `BUILD_STATUS.md`, and proposes the next handoff. **You stay in the loop the whole time** — every handoff is a moment where you can ask questions, override, or pause.
5. **End-of-build state** — when every "in MVP scope" subsystem reaches `[x]` in `BUILD_STATUS.md`, the orchestrator says the product is "ready to deploy." From here, `/ship-app <slug>` is the next gated phase.

You can re-run `/start-build <slug>` at any time during the build for a fresh "where am I, what's next" prompt from the orchestrator.

**Two companion commands for build interruptions:**

- **`/continue-build <slug> [--hint "<text>"] [--from <file>]`** — the canonical way to resume an in-flight build after a break. Reads `BUILD_STATUS.md` to find subsystems in `[>]` / `[ ]` / `[x]` state, **scans the source tree for the most-recently-modified files** (so the orchestrator sees you last wrote `app/static/css/components.css` 3 minutes ago), and invokes the orchestrator in resumption mode — no orientation re-ask. Pass `--hint "<text>"` to disambiguate ("we just finished tokens.css and were starting components.css") or `--from <file-or-subsystem>` to explicitly override the resumption point. This is the disambiguator for plain "please continue" when multiple products are mid-build.
- **`/recollect <slug>`** — read-only "where are we" synthesis. Walks every artifact related to the product (brief, validation, scoping, design research/spec/brief, BUILD_STATUS, team, source tree, audit log) and emits a one-screen report + 2-4 suggested next actions. Use when returning to a product after days/weeks away and you need to re-orient before deciding whether to `/continue-build`, `/scope-v1`, `/ship-app`, or anything else. Invokes no subagent; modifies no file.

### 6.4 The senior-engineer personas

The orchestrator routes to one of eight specialist personas based on the subsystem. Here's who does what:

| Persona | Owns |
|---|---|
| `senior-system-design-engineer` | System shape, service boundaries, cross-cutting concerns. Produces `SYSTEM_DESIGN.md`. |
| `senior-database-engineer` | Schema, indexes, migrations, data-integrity guarantees. Produces `SCHEMA.md`. |
| `senior-backend-engineer` | ORM models, API contract, endpoint implementation, business logic. Produces `API_CONTRACT.md` and the backend source. |
| `senior-frontend-engineer` | Web + mobile UI (Jinja+JS on web, React Native on mobile), design-token integration, accessibility. |
| `senior-desktop-engineer` | Desktop UI (PySide6 by default), UI ↔ core separation, packaging via PyInstaller, native integrations, distribution path. |
| `senior-qa-engineer` | Test coverage, integration at the seam, accessibility audits, release-readiness verdict. |
| `senior-devops-engineer` | Deploy, CI/CD, observability, incident response, backups. |
| `senior-security-engineer` | Threat modeling, secure coding, auth design, secrets handling, infra hardening. |

Each specialist composes with the others: the backend engineer produces an `API_CONTRACT.md` that the frontend engineer reads to know how to call it; the security engineer reviews the auth implementation the backend engineer wrote; the QA engineer audits both. The orchestrator decides who comes next.

**Name your team.** Each product can have its own per-product team — the 9 personas above get human names you choose. Storage: `<web-apps|mobile-apps|desktop-apps>/<slug>/team.json` (gitignored). Two paths to naming:

1. **Upfront via `/team <slug>`** — an interactive lister. Shows the team as a table, lets you pick rows to name or rename, loops until you're done.
2. **Just-in-time** — `/start-build` prompts "name your `<Role>`?" the very first time each persona is engaged on this product. The prompt only fires for unnamed personas; once named, it doesn't ask again. You can decline ("No — use the role label") and the persona stays unnamed for that product.

Why name them? Build narration becomes more concrete. "Paul (Senior Software Engineer) is invoking Maria (Senior Database Engineer) for the schema work" reads differently than "Senior Software Engineer is invoking Senior Database Engineer for the schema work." Same content; the named version feels like a team. Same change shows up in `BUILD_STATUS.md` History entries and in `build-milestone` audit-log descriptions, so you can search "Paul" or "Maria" later via `/log type build-milestone`.

Naming is **per-product**, not workspace-wide. Each product gets its own team — useful when you have multiple products in flight and want different vibes per project, or just want different name sets to keep them straight in your head. Name validation: 1-30 chars, must start with a letter or digit, allowed characters are letters / digits / spaces / hyphens / apostrophes.

Members **cannot be deleted** (the 9 roles are wired into the orchestration), but they can be renamed or reset to unnamed. Reset blanks out the name; the role is still there, narration just falls back to the role label.

### 6.5 Following along when you don't code

If you're not a developer, here's a practical playbook for staying useful during the build without needing to read code.

**Read `BUILD_STATUS.md` regularly** — it's your dashboard. Subsystems with `[ ]` are pending, `[>]` are in progress, `[x]` are done. The "Current focus" section says what the orchestrator is working on right now. The "History" section is an append-only log of every handoff and decision — if you missed what happened in the last 20 minutes, this catches you up in 30 seconds.

**Ask "why" generously.** When the orchestrator says "I'm invoking the security engineer to review the auth flow," you can ask: "What does that mean? What is the security engineer going to look at? What would a problem look like?" Claude will explain in plain terms. Asking is free; you'll understand the product better and catch the cases where a default doesn't fit your intent.

**Watch for the moments where the senior engineers will pause and ask *you*.** This is where you have the most leverage. Examples:

| Pause point | What you decide |
|---|---|
| Stack confirmation (in `/scope-mvp` and again in `/start-build`) | Which framework / language to use |
| Build-order orientation | Web first or mobile first; MVP or fully-featured |
| Data model questions | "Should this field be required or optional? What's the relationship between User and Order?" |
| Auth strategy | OAuth-via-Google vs. email-password vs. magic-link |
| Feature trade-offs | "We can implement this in 2 hours simple-but-rigid, or 6 hours flexible-but-complex. Which do you want?" |
| `/ship-app` final confirmation | "Ready to ship to first 10 users — proceed?" |

In every case, the senior engineer will explain the trade-off in 2-3 sentences and recommend a default. You can take the recommendation or push back.

**Signs the build is going well**

- `BUILD_STATUS.md` shows steady progress: one or two subsystems moving from `[ ]` to `[>]` to `[x]` per session.
- The orchestrator narrates handoffs cleanly and the next-step time estimates are reasonable.
- You understand at a high level what each subsystem does (even if you don't read the code).
- Tests pass after each subsystem (the QA engineer reports green).

**Signs the build is going badly**

- `BUILD_STATUS.md` has subsystems stuck in `[>]` for many sessions — usually means something is harder than the brief estimated.
- Multiple subsystems "carry decisions deferred to later" — debt is accumulating.
- You don't understand what's happening, and you're not asking. (Ask. Always ask.)
- The QA engineer keeps reporting test failures the engineer didn't catch.

**If the build is going badly, do not power through.** Pause the build, run `/start-build <slug>` again for a fresh orchestrator perspective, and consider whether the brief was too ambitious or whether the riskiest assumption changed. It's much cheaper to revise the brief at hour 5 than to ship a broken MVP at hour 40.

### 6.6 When Fijara makes more sense

The workspace's default assumption is that you'll follow along with Claude through the build. But that's not always the right call. Fijara — [fijara.com](https://fijara.com), the maintainer's dev service — exists for the cases where it isn't.

Pick Fijara as your build support at `/scope-mvp`'s pre-build checkpoint if:

- You've never built a web/mobile/desktop app before and don't have the bandwidth to learn during the build.
- The brief's must-haves include something genuinely complex (real-time multi-user, ML model deployment, hardware integration) where one mistake costs a lot of debug time.
- You want to focus on the product side (talking to users, sharpening the value prop, distribution) while a developer drives the implementation.
- You have a deadline that doesn't permit learning loops.

There's no shame in this. The maintainer built the workspace to ship faster *himself*; it also works well as the operating spec for a dev partner who's working on your behalf.

**Picking "I'll follow along" at the checkpoint and switching to Fijara later is also fine.** Claude is set to gently surface Fijara as an option if it senses you're getting stuck — repeated questions about basic concepts, expressed frustration, blockers on routine setup. The default posture is to trust your initial pick; the exception is genuine evidence of mismatch.

### 6.7 `BUILD_STATUS.md` as your dashboard

Every product in the build phase has a `BUILD_STATUS.md` at its project root (`web-apps/<slug>/BUILD_STATUS.md`, etc.). It's a **dynamic checklist** — generated from the brief's must-haves, the chosen stack, and the standard build order, then maintained by the orchestrator as the build progresses.

**What's in it:**

- **Subsystem checklist** — one line per subsystem with status (`[ ]` / `[>]` / `[x]`), owner persona, output artifact, brief description.
- **Current focus** — what's in progress right now.
- **History** — append-only log of every subsystem start, completion, or decision.
- **Decisions recorded during build** — non-obvious calls made during the build that future-you needs to remember.
- **Open items** — surfaced for you, not yet resolved.

The orchestrator updates `BUILD_STATUS.md` at every: subsystem start, subsystem completion, scope change, decision, pause, release, or kill. Subsystem updates appear with timestamps in the History section. If you ever lose track, this is the source of truth for "where am I."

You can read `BUILD_STATUS.md` directly with any editor; you can also run `/status` from Claude Code to see a workspace-wide summary that includes this file plus everything else in flight.

### 6.8 `/preview-product`

Once you have any kind of frontend in place, you can preview the product at any time via `/preview-product <slug>`.

**For web products:**

- **Real preview** — if the docker compose stack is up and the route is wired, opens `localhost:5000/<page>` in Chrome.
- **Dummy preview** — if dependencies aren't connected yet, renders the Jinja template with fixture demo data via the `web-preview` skill and opens the result in Chrome. Always possible if the template file exists.
- Claude always tells you which mode you got and why.

**For desktop products:**

- Launches `python -m <slug>` from the project's venv. The Qt main window opens. You quit it (Cmd-Q / Alt-F4) to return to Claude Code.
- No dummy / fixture mode — the app itself is the preview.

**For mobile products:**

- `/preview-product` doesn't apply. Use Expo Go (`npx expo start` + scan QR code on a device) during dev, or EAS preview builds for tester distribution.

The preview command is your fast feedback loop — instead of waiting for `/start-build` to finish a screen and then asking "what does it look like," you can preview at any intermediate point.

---

## 7. Phase 3 — v1 scoping + (optional) design phase

Once your MVP has shipped and the riskiest assumption is validated, **`/scope-v1 <slug>` is the entry gate** to the polished v1 build. It's the second scoping pass in the pipeline — the first (`/scope-mvp`) was about the smallest thing that could validate the assumption; this is about the smallest thing that could be a real product now that the assumption has held.

### 7.1 What `/scope-v1` does

The command runs in five steps before drafting the brief:

1. **Capture first-10-users feedback.** You summarize what the round taught — at least a one-line per-user summary. Claude pushes back once if your reply sounds like a gut feel rather than user signal. This is the most important step; v1 built without user signal is the strongest predictor of building the wrong thing.
2. **Pick the design path.** Three options — covered in detail in §7.2 below.
3. **Decide on pricing.** Surfaces the current MVP price. You either keep it or invoke `/reprice <slug>` before re-entering `/scope-v1`.
4. **Pick the new must-haves.** Claude shows you the MVP's deferred could-haves and its read of what the user feedback implies. You decide which become v1 must-haves.
5. **Draft `V1.md` + run reviewers.** Writes the v1 brief at `<web-apps|mobile-apps|desktop-apps>/<slug>/V1.md` next to the existing `MVP.md`. Same `product-scope-reviewer` + `code-reviewer` as `/scope-mvp`, but tested against the v1 brief.

Output: `V1.md` at the product folder + `scoping-v1-<slug>.md` at `market-research/<run-id>/`. Stops at advance / revise / pause / retire decision.

### 7.2 The design-path picker (the centerpiece)

Most MVPs in this workspace ship with the **claude-led** path — Claude runs full design research and writes a `DESIGN_SPEC.md` that the MVP build implements from. That was the right call for MVP — the goal was validating the assumption with a considered design, not a designer-engagement overhead. At v1, the question of engaging a professional UI/UX designer gets a real answer.

| Path | What happens | When to pick |
|---|---|---|
| **(a) Claude-led continued** | v1 continues the claude-led path. Re-run `/research-design` (refreshed for v1's new surfaces + first-10-users feedback) → re-draft `DESIGN_SPEC.md` → build adds new must-haves on top of the MVP codebase against the refreshed spec. No designer engagement. | Function-over-form segments (developer tools, internal SMB, prosumer utilities). Budget/timeline constraints make designer engagement non-viable this round. First-10-users feedback had no visual / interaction comments the claude-led path can't address. |
| **(b) Engage a professional UI/UX designer** | v1 routes through the full design sub-flow: `/research-design <slug>` → user picks a visual direction → `/draft-design-brief <slug>` → human designer produces Figma → handoff capture (`tokens.json`, `screenshots/`, `assets/`) → v1 build proceeds **driven by the handoff**. | Polish-differentiated segments (consumer apps, design-led tools, category-leader incumbents). First-10-users feedback included visual / interaction comments the generic pass can't easily address. You want the v1 to look like a real product, not a prototype. |
| **(c) Hybrid — light refresh** | Keep the claude-led path, but add a polish pass — refined palette, refined typography, 2-3 distinctive UI patterns (signature auth screen, memorable empty state, etc.). No formal designer engagement. `/research-design --light` produces a lightweight design-direction reference without the full spec or brief. | Segments that care about polish but don't justify designer overhead. You have visual taste you want to express directly. Most workspace-default pick when MVP claude-led proved sufficient for validation but v1 wants modest visual investment. |

**Important sequencing for path (b):** the v1 build does NOT start until the handoff lands. Skipping the design phase to "start building now" after picking (b) defeats the purpose.

### 7.3 The full Phase 3 design sub-flow (fires on BOTH design paths)

Since v0.11.0, `/research-design` fires regardless of which design path was picked. The research is the same; only the second artifact differs.

| Command | When it fires | What it does |
|---|---|---|
| `/research-design <slug>` | **Both paths** | Invokes `ui-ux-researcher`. Produces `DESIGN_RESEARCH.md` covering: per-surface coverage (public / auth / user dashboard / admin / employee dashboards — each surface treated as its own research target), product-space + platform-level UI/UX trends, ≥3 visual directions, ≥3 color/type pairings, pattern conventions, responsive strategy (breakpoints per surface), brand positioning, portfolio-continuity question. May pause to ask you to open a reference URL ("does Datadog's left-rail density feel right?") and bake your answer into the recommendation. |
| `/draft-design-spec <slug>` | **Claude-led only** | Collects your picks (visual direction, palette, typography, voice, portfolio-continuity, dark-mode scope, font loading). Invokes `ui-ux-researcher` in spec-writing mode to produce `design/DESIGN_SPEC.md` — implementation-ready: exact CSS tokens (color/typography/spacing/radius/shadow/motion), icon library install snippet, image-asset prompts (batch-later — you generate later on ChatGPT, paste URLs into `.env`), responsive breakpoints, per-surface specs, component patterns. Runs `design-spec-reviewer`. Stops at sign-off; status → `acted-on`. **The spec becomes the build's source of truth** (supersedes `frontend-ui-engineering` defaults). |
| `/draft-design-brief <slug>` | **Hired only** | Collects your picks (visual direction, palette, typography, voice, portfolio-continuity, timeline). Drafts the consolidated Figma-handoff brief at `design/DESIGN_BRIEF.md`. Runs `design-brief-reviewer`. Stops at sign-off; status → `sent`. You transmit to your designer. |

For the hired-designer path, the human designer works asynchronously against the brief. When they finish, you capture the handoff per `guides/ui-ux/design-handoff-methodology.md` — `design/handoff/tokens.json`, `design/handoff/assets/`, `design/handoff/screenshots/`. The handoff becomes the contract for Phase 4.

For the claude-led path, `DESIGN_SPEC.md` IS the contract — Claude builds against it directly. No external designer wait.

You can also **skip the v1 phase entirely** and iterate the Phase 2 MVP directly if the first 10 users are happy and the product doesn't feel ready for a polished build. Many products never get a formal v1. The workspace doesn't push you into Phase 3 unless you choose it.

---

## 8. Phase 4 — v1 build

`/start-build <slug>` is reused for v1. It auto-detects which brief is current: if `MVP.md` is `shipped` AND `V1.md` is `green-lit-to-build`, the orchestrator picks `V1.md` and treats the MVP code as the starting point to extend.

How the v1 build proceeds depends on the design path picked in `/scope-v1`:

| Path | How v1 build proceeds |
|---|---|
| **(a) claude-led-continued** | Re-run `/research-design` (refreshed for v1) → re-draft `DESIGN_SPEC.md` → build adds new must-haves directly into the existing codebase against the refreshed spec. |
| **(c) hybrid-light-refresh** | V1.md + the lightweight design-direction reference from `/research-design --light` inform the build. Selected UI patterns get re-implemented with the new palette/typography; the rest carries forward unchanged. |
| **(b) pro-designer-engaged** | Build is **driven by the handoff**: `design/handoff/tokens.json` becomes the token contract (CSS custom properties for web in `static/css/tokens.css`; `src/theme/tokens.ts` for mobile). `design/handoff/screenshots/` inform per-screen implementation. Components match the Figma library's "02 Components" page. **Order of authority** when sources conflict: token contract → screenshot → V1.md §6 → `frontend-ui-engineering` craft. |

The v1 build typically takes longer than the MVP build because the scope is wider and the implementation is more polished. For path (b), the designer turnaround (typically 2-6 weeks) is usually the dominating gating step in the effort estimate. But the riskiest assumption is already validated, so you're shipping with confidence — not gambling.

---

## 9. Phase 5 — Shipping (`/ship-app`)

Shipping is the gated handoff from "build is done" to "users see it." `/ship-app <slug>` does not just deploy — it runs a release-readiness gate first, executes the deploy, and verifies post-deploy.

**The pipeline:**

| Step | Owned by | What happens |
|---|---|---|
| 1. Verify build readiness | `/ship-app` | Reads `BUILD_STATUS.md`. If core subsystems aren't all `[x]`, refuses and points back at `/start-build`. |
| 2. QA pre-flight | `senior-qa-engineer` | Final test pass, acceptance criteria check against the brief's success criterion, accessibility spot-check. Outputs "release-ready" or "not-ready" + blockers. **If "not-ready", stops.** |
| 3. Security pre-flight | `senior-security-engineer` | Auth, secrets, input boundaries, file I/O, OWASP-style spot check. Outputs "ship-safe" or "blockers". **If "blockers", stops.** |
| 4. Final user confirmation | `/ship-app` | Summary of QA + security verdicts and deploy steps. Asks "ship now / cancel". |
| 5. Deploy | `senior-devops-engineer` | Stack-specific deploy path — Docker build + DigitalOcean push for web, EAS build + app-store submission for mobile, PyInstaller bundle + sideload for desktop (or signed bundle for desktop v1). |
| 6. Post-deploy verification | `senior-devops-engineer` | Smoke tests against the deployed surface. Outputs "ship verified" or "post-deploy issues". |
| 7. `BUILD_STATUS.md` updated | `senior-software-engineer` | Records deploy timestamp, version SHA, target environment, verdicts, post-deploy result. |

**Arguments:**

```
/ship-app <slug>                          # infer scope from MVP brief
/ship-app <slug> --web                    # ship web only
/ship-app <slug> --mobile                 # ship mobile only
/ship-app <slug> --desktop                # ship desktop only
/ship-app <slug> --all                    # ship every domain in the brief
```

**Safety rails:**

- Both pre-flight gates must pass (or be explicitly overridden + documented in `BUILD_STATUS.md`) before any deploy runs.
- The script never `--force` pushes, never skips a rollback path.
- After post-deploy issues, you decide whether to fix-and-reship or escalate — no auto-iteration.
- For desktop apps, MVP-scope ships unsigned bundles with a "right-click → Open" sideload note for your first 10 users; signed + notarized release is a separate v1 step you opt into.

**Why this works the way it does:** in early-stage shipping, the biggest risk isn't *whether* deploy works — it's *what you put in front of users*. The pre-flight gates exist to catch the cases where the build looks done but a critical path is broken or insecure. The cost of a gate is 5-10 minutes; the cost of a broken first-10-users launch is a kill cycle.

---

## 10. Parallel — Trend monitoring (`/trend-check`)

The trend monitor runs across all phases on a separate cadence — weekly by default, or triggered when an external event makes you want a check. It does NOT auto-invoke any downstream command; it surfaces findings and recommends.

```
/trend-check                              # weekly sweep
/trend-check triggered <reason>           # emergency sweep
```

**What it does:**

Sweeps a watchlist derived from your active pipeline state — the territories from your active scan, the cards you're validating, the briefs you're scoping — and categorizes findings as:

- **Material** — directly affects an in-flight artifact. Recommends specific downstream commands (e.g., "re-run `/scope-mvp bench-watch` — new competitor announcement makes the differentiation harder").
- **Notable** — relevant context but not action-forcing.
- **Background** — for awareness; no recommendation.

Output goes to `market-research/<run-id>/trends.md` with `status: draft`. After your sign-off, you decide which (if any) downstream commands to re-run. The trend monitor never auto-invokes them.

**Cadence:** weekly is the default per `guides/market/trend-monitoring.md`. The `/menu` command flags the trend report's age and suggests `/trend-check` if it's older than 7 days.

---

## 11. The reviewer-decision model — why *you* decide, not the reviewers

This is the most important conceptual model in the workspace, and it's worth understanding deeply.

**The setup:** at every phase that involves multiple narrow-lens reviewers (`/validate-card` with 4 product reviewers; `/scope-mvp` with 2 scope + code reviewers; `/draft-design-brief` with the design-brief reviewer), each reviewer returns a structured verdict — `APPROVE`, `APPROVE-WITH-NOTES`, or `REJECT`. The reviewers' job is to assess **their own narrow dimension** and tell you what they found.

**The decision is yours.** The reviewers do not move artifacts forward; they do not auto-kill cards; they do not advance status. They write reports. You read the reports and make the call: advance, revise, kill.

**Three reasons it works this way:**

1. **Reviewers often disagree.** When `bench-watch` returned `APPROVE / REJECT / APPROVE`, there's no clean consensus to act on. A majority-vote rule would oversimplify ("any REJECT kills" would over-restrict; "any APPROVE saves" would over-include). Any auto-rule would force you into the loop anyway to fix the defaults. Better to put you in the loop intentionally.

2. **The dimensions aren't equally weighted for every card.** For `bench-watch`, the competition-reviewer might have flagged "Braintrust and LangSmith already do scheduled evals" — that's REJECT-worthy in isolation but maybe survivable if your differentiation angle is strong enough (the niche of "pinned-alias regression detection," which the other two reviewers cared more about). That weighting is **product strategy work**; reviewers can't make it because they don't know your portfolio strategy, your appetite for niche plays, or your timeline.

3. **You own the portfolio.** The reviewers are advisors; the workspace is yours. The decision compounds — every advance commits hours of work, every kill closes a door. That weight belongs with you.

**Reading the verdict patterns:**

| Pattern | What it usually means |
|---|---|
| `APPROVE / APPROVE / APPROVE` | Strong card. Almost always advance. |
| `APPROVE-WITH-NOTES / APPROVE / APPROVE` | Strong card with one concrete thing to fix or watch. Advance, then address the note during scoping. |
| `APPROVE / REJECT / APPROVE` | Mixed. The REJECT-ing dimension is fixable through a card revision *or* through framing the brief carefully. Read the REJECT reasoning to decide. |
| `REJECT / REJECT / APPROVE` | Leans kill. Two dimensions failed; the third's APPROVE is probably about a narrow strength that won't carry the whole product. |
| `APPROVE / REJECT / REJECT` | Leans kill, different shape. Viability is real but neither competition nor segment hold up. Often a real problem in a hard-to-enter market. |
| `REJECT / REJECT / REJECT` | Kill, almost always. Three dimensions agreeing on REJECT is a strong signal. |

The validation report has a **Recommended decision** line at the bottom that synthesizes the verdicts into one suggestion — but it's just a suggestion. The next step in the workflow is yours.

**How to actually make the decision:**

| Decision | What to do |
|---|---|
| **Advance** | Run `/scope-mvp <slug>`. Card status moves to `green-lit`. |
| **Revise** | Edit the card to address the REJECT-ing reviewer's notes. Re-run `/validate-card <slug>`. |
| **Kill** | Tell Claude "kill the `<slug>` card." Claude moves `ideas/<run-id>/<slug>.md` → `ideas/killed/<run-id>/<slug>.md` and adds the kill reason to frontmatter. |

This same advise-vs-decide pattern repeats at `/scope-mvp` (build / revise / kill), at `/ship-app` (ship / cancel), and at design checkpoints. In every case, the subagents tell you what they found; you tell them what to do next.

---

## 12. Workspace conventions you should know

**Slug uniqueness — category-scoped.** A **product slug** (e.g., `bench-watch`, `form-to-api`) lives in up to three category slots: active card (`ideas/<run-id>/<slug>.md`), killed card (`ideas/killed/<run-id>/<slug>.md`), and exactly one app folder (`web-apps/<slug>/`, `mobile-apps/<slug>/`, OR `desktop-apps/<slug>/`). **One active card + one app folder is the expected post-`/scope-mvp` state** — not a collision. The lint rule `slug.collision` fires only on true conflicts: 2+ active cards with the same slug, 2+ killed cards with the same slug, active AND killed at once, or app folders across 2+ stack categories. Orphan states (`slug.orphaned-app-after-kill`, `slug.app-without-card`) surface as warnings. Before creating a new slug-keyed artifact, run `python3 scripts/check_slug.py <proposed-slug>` — any current use blocks reuse, including a previously-killed slug; recycling confuses the kill-reason audit trail.

**Run-id grouping.** Every `/discover` cycle generates an 8-character run-id (e.g., `ervtqqa6-053126`). All cards from that cycle live in `ideas/<run-id>/`. All downstream artifacts (validations, scoping reports) live in `market-research/<run-id>/` with the same run-id. This makes it trivially easy to see which cards came from which cycle and to delete a whole cycle's work via `/projects`.

**Personal vs shared.** The repo separates **scaffolding** (committed, shared) from **your personal product work** (gitignored, local only):

| Tracked (committed) | Gitignored (your local data) |
|---|---|
| Guides, agents, commands, skills, scripts | `ideas/`, `market-research/`, `web-apps/`, `mobile-apps/`, `desktop-apps/`, `generated/`, `user-context/` |
| Methodology, conventions, top-level docs | Your specific cards, reports, app code, exports |
| `README.md`, `CLAUDE.md`, this `DOCUMENTATION.md`, `HELP.md`, `CHANGELOG.md` | The live (non-template) `INTERESTS.md`, `IDEAS.md`, `POLICY.md` |

When you `git pull` updates from upstream, your personal product work is untouched. When you push back contributions (forkers), you only push the scaffolding side.

**Status frontmatter conventions.** Every artifact has a `status:` field in its YAML frontmatter. Status drives what the pipeline shows you and what's allowed next. Common status values:

| Artifact | Status values (typical sequence) |
|---|---|
| Idea card | `discovered` → `in-validation` → `validated` → `green-lit` → `green-lit-to-build` → `building` → `shipped` |
| Scan report | `draft` → `active` |
| Validation report | `reviewed — awaiting-user-decision` → `decision-recorded — advanced` / `revised` / `killed` |
| Brief | `in-scoping` → `green-lit-to-build` → `building` → `shipped` |
| Design research | `draft` → `acted-on` |
| Design brief | `draft` → `sent` |

The `/status` command surfaces all in-flight artifacts and their statuses; `/menu` flags ones that have been sitting at a checkpoint for a while.

**The 40k CLAUDE.md threshold.** Claude Code auto-loads `CLAUDE.md` at the start of every session in this directory. Above ~40,000 characters, the auto-load warns. The workspace targets the file at staying just under that threshold — every edit needs to consider size, and trims have to come alongside adds. This is why some content lives in `DOCUMENTATION.md` (which is loaded on demand) instead of CLAUDE.md (which is always loaded).

**Markdown tables everywhere.** The workspace uses markdown tables aggressively for any comparison, any reference, any status overview. Reasons: tables render cleanly in Claude Code's TUI, on GitHub, in markdown-rendered PDFs via `doc-export`, and in plain text terminals (pipe-delimited rows still read OK). The earlier alternative — ASCII-aligned tables — broke on narrow displays.

---

## 13. Utility commands reference

These are the commands that don't fit a pipeline phase but are essential for daily use.

| Command | What it does | When to use |
|---|---|---|
| `/menu` | Quick menu of available commands and suggested next actions, based on current pipeline state. Lower-overhead than reading `HELP.md` or this `DOCUMENTATION.md`. | Beginning of a session, or "what should I do next?" moments. |
| `/status` | Complete pipeline-state snapshot. Active scan, all active cards with statuses and ages, in-flight briefs, design phases, recent reports. Read-only. | When you want a "where am I across everything" view. |
| `/documentation` | This document, in condensed form, in the terminal. Plus a pointer back to `DOCUMENTATION.md` for the full version. Bypasses the onboarding interrupt — it's the only command that does. | When you want to read up on the workflow. |
| `/setup` | Pre-flight verification on a new clone or new machine. Checks all required tools, git identity, GitHub auth, submodule init, agent-skills file copies. | Brand-new clone, or returning after a long break. |
| `/system-check` | Compares your machine against the workspace's hardware + tooling requirements. Row-by-row table with required / recommended / your value / status. | New machine, or troubleshooting a "tool not found" error. |
| `/run-tests` | Repo health / smoke test suite. 7 categories — required tools, repo structure, frontmatter, cross-references, pipeline lint, script smoke tests, documentation consistency. | After cloning, before opening a PR, or when something seems off. |
| `/projects` | List every discovery-cycle project (keyed by run-id) and offer actions on a chosen one — primarily delete. Two-step confirmation gate. | Cleaning up abandoned discovery cycles, verification tests, or whole projects you no longer need. |
| `/log` | View, add, or delete entries in your personal-space audit log at `user-context/audit-log.jsonl`. The log records important user-driven decisions (skipping onboarding, deleting a project, killing/reviving a card), build-stage milestones (project initialized, subsystem completed, ready-to-deploy reached, shipped), and any free-text notes you add. Gitignored — never enters git. Subcommands: `/log` (display), `/log <text>` (add note), `/log type <type>` (filter — e.g., `/log type build-milestone` gives a per-product build journal), `/log delete <id>` (remove one), `/log clear` (wipe). | When you want to see the audit trail, review a product's build history, add a personal note, or re-enable onboarding by deleting an `onboarding-skip` entry. |
| `/reprice` | Rework the pricing on an existing artifact (idea card, MVP brief, V1 brief) by invoking only the `product-pricing-reviewer`. Idempotent — surfaces any prior pricing and asks "revise?" before re-researching. The reviewer returns 2-3 strategic pricing options; you pick one or type your own. Writes the chosen price to all relevant artifacts (card / brief frontmatter, brief `## Pricing` block) and appends a `## Reprice — <date>` block to the validation report. | When a price feels off (too high, too low, set by analogy with stale comparables) and you want a fresh pricing pass without re-running full `/validate-card`. |
| `/revive-card <slug>` | Restore a killed idea card back to active state. Moves the file from `ideas/killed/<run-id>/<slug>.md` to `ideas/<run-id>/<slug>.md`, resets the frontmatter (`status: triaged`, clears kill-specific fields), and appends a `card-revive` audit-log entry. If an orphaned MVP/V1 brief exists at `<stack>-apps/<slug>/`, optionally revives those too (flips their `status: killed` back to a pre-kill state you pick). Refuses if reviving would create a slug-collision. The canonical undo for any kill made via `/validate-card`, `/scope-mvp`, `/scope-v1`, or `/discover`'s auto-triage. | When a kill was premature, signal has shifted (competitor exited, regulation opened, pivot makes original reject stale), or a `/scope-v1` retire is being reversed. Pair with `/log type card-revive` to see the audit trail. |
| `/rework <slug> <changes>` | Rework an idea card (and optionally its downstream MVP brief / V1 brief) based on user-described changes. **Originals are never overwritten until the user commits.** Proposed changes land in temp files (`<slug>-temp.md`, `MVP-temp.md`, `V1-temp.md`); reviewers run against the temps; verdicts surface to the user; the user inspects + can override REJECTs (with a consequences explainer + one-sentence justification, recorded in the `rework-applied` audit-log entry); commit replaces originals with temps + sets statuses back to pre-review baselines + appends `## Rework — <date>` blocks to existing validation/scoping reports. | When you need substantive changes to an idea/scope/MVP after reviewers ran. Solves the "edit, run reviewers, get REJECT, manually undo or override silently" failure mode — `/rework` encapsulates that whole loop with a permanent audit trail. |
| `/consolidate <slug>` | Check alignment across an idea card, its validation report, its scoping report, its MVP brief, and (if present) its V1 brief — surface every misalignment in a numbered table with suggested resolutions, ask the user for permission per row or all-at-once, apply targeted edits, then re-run the relevant reviewers against the consolidated artifacts. Audit-logged as `consolidation-applied`. | When artifacts have drifted (MVP must-have doesn't trace to the card; validation chosen-price differs from MVP `priced-at:`; V1 carries a must-have MVP didn't ship). Typical sequence: `/consolidate` first to clean drift, then `/rework` if substantive changes are still needed. |
| `/infra-cost <slug> [--save \| --users=A,B,C \| --include-v1]` | Estimate the infrastructure cost of running an MVP (or V1) — minimum / medium / max scenarios by user base. Reads MVP.md, extracts stack + infrastructure decisions, fetches current vendor pricing live (per `CLAUDE.md § Internet access policy`), and assembles a cost table per item with flags for **recurring vs. one-time** and **user-dependent vs. fixed**. Default tiers `10, 100, 1000`. Computes total monthly burn + fixed-vs-variable breakdown + recurring admin cost the maintainer pays regardless of users. Lists every assumption (LLM tokens per user, conversion rate, ARPU, etc.). With `--save`, writes the report to `<stack>-apps/<slug>/INFRA_COST.md`. | When you want to know "can I afford to ship this MVP and keep it running at first-10-users? at 100? at 1000?". The pipeline already has effort estimates; this gives you the money estimate to pair with them. |
| `/team <slug>` | List / name / edit the 9 senior-engineer team members for a product (per-product `team.json` at the product folder, gitignored). Interactive table-driven UI: name an unnamed member, edit an existing name, or reset all to unnamed. **Members cannot be deleted** (the 9 roles are workflow-critical). Names show up in build narration ("Paul (Senior Software Engineer) is invoking..."), `BUILD_STATUS.md` History, and `build-milestone` audit-log descriptions. | When you want to name your build team upfront, or when you want to rename someone mid-build. Just-in-time naming also happens automatically the first time `/start-build` engages each persona on a product. |
| `/acknowledge-contributing` | One-time confirmation that you've read `CONTRIBUTING.md` before editing tracked files. Required for non-owner users (forkers). Creates a gitignored `.claude-acknowledged` marker. | Forkers, first time you want to edit a tracked file. |

---

## 14. Scripts + helper skills reference

### Python scripts (`scripts/*.py`)

These are auxiliary tools that complement (don't replace) the slash commands. Use them directly from the shell when you don't need an agent round-trip.

| Script | Purpose |
|---|---|
| `run_tests.py` | Repo health / smoke test suite. Backs the `/run-tests` slash command. |
| `lint_pipeline.py` | Validates pipeline state consistency — frontmatter, status alignment, `@path` cross-references, validation-report required sections (recognizes both per-reviewer §5 and integrated §7 shapes), and category-scoped slug-collision rule (active card + one app folder is the expected post-`/scope-mvp` state, not a collision). |
| `check_links.py` | Scans tracked markdown for broken relative links and `@path` references. Optional external-URL HEAD check. |
| `check_slug.py` | Verifies a product slug is available across `ideas/`, `ideas/killed/`, `web-apps/`, `mobile-apps/`, `desktop-apps/`. |
| `gen_run_id.py` | Generates a pipeline run-id (`<8-lowercase-alphanumeric>-<MMDDYY>`). Importable + CLI. |
| `new_idea_card.py` | Interactive idea-card creator for one-off captures outside `/discover`. |
| `changelog_helper.py` | Auto-extracts commits since the last tag and formats as a CHANGELOG entry stub. |
| `report_summarizer.py` | Pretty-prints summaries of all scan / validation / scoping / trend reports. |
| `audit_log.py` | Read/write the personal-space audit log at `user-context/audit-log.jsonl` (gitignored). Subcommands: `add`, `list`, `delete`, `clear`, `has`. Supports 6 entry types (`onboarding-skip`, `project-delete`, `card-kill`, `card-revive`, `build-milestone`, `user-note`). Backs the `/log` slash command. The `has` subcommand also gates CLAUDE.md's Rule A onboarding re-prompt. |
| `team.py` | Manage per-product senior-engineer team-member names at `<web-apps\|mobile-apps\|desktop-apps>/<slug>/team.json` (gitignored). Subcommands: `get`, `set`, `list`, `init`, `reset`, `roles`, `path`. Names validated 1-30 chars (letters / digits / spaces / hyphens / apostrophes). The 9 build-phase roles (orchestrator + 8 specialists) are fixed; no `delete` subcommand. Backs the `/team` slash command. Used by `/start-build` for just-in-time naming prompts. |
| `check_system.py` | System spec checker. Backs the `/system-check` slash command. |
| `projects.py` | Manages discovery-cycle projects (list, show, delete with `--force`). Walks all three stack categories (`web-apps/`, `mobile-apps/`, `desktop-apps/`) plus `ideas/`, `ideas/killed/`, `market-research/`, `generated/` when computing what to delete. Backs the `/projects` slash command. |

### Shell scripts (`scripts/*.sh`)

| Script | Purpose |
|---|---|
| `preflight.sh` | Shell-side equivalent of `/setup`. Verifies tools + repo state without Claude Code. |
| `setup-deps.sh` | Installs all required tools in one go. Idempotent. Detects macOS vs. Linux. |
| `update-agent-skills.sh` | Pulls the agent-skills upstream and re-copies persona/skill files into `.claude/`. |
| `backup-personal-data.sh` | Tars up gitignored folders for backup. Optional `--encrypt`. |
| `new-product-skeleton.sh` | Scaffolds a new product folder under `web-apps/<slug>/`, `mobile-apps/<slug>/`, or `desktop-apps/<slug>/`. |
| `clean-killed-ideas.sh` | Archives killed ideas older than N days. |

### Helper skills (`.claude/skills/`)

Skills are auto-invoked by Claude Code when relevant phrasing appears in your prompts.

| Skill | Trigger phrases | Output |
|---|---|---|
| `doc-export` | "export this as PDF", "generate a docx of [artifact]", "give me a PDF of [artifact]" | Markdown → PDF or DOCX via pandoc. Output lands in `generated/<category>/` with a date-stamped, slug-keyed filename. |
| `web-preview` | "preview this page", "show me what this template renders to", "open this in Chrome" | Renders a Jinja template from `web-apps/<slug>/` with fixture demo data and opens in Chrome. |

In addition to these two project-local skills, **all 23 agent-skills** from `external/agent-skills/skills/` are file-copied into `.claude/skills/` and auto-discovered. The full inventory and per-skill description lives in `.claude/skills/README.md`. The agent-skills (by Addy Osmani, MIT-licensed) cover the full build-phase craft surface — TDD, code-review-and-quality, security-and-hardening, performance-optimization, debugging-and-error-recovery, frontend-ui-engineering, api-and-interface-design, documentation-and-adrs, git-workflow-and-versioning, browser-testing-with-devtools, ci-cd-and-automation, shipping-and-launch, spec-driven-development, idea-refine, interview-me, planning-and-task-breakdown, doubt-driven-development, using-agent-skills, source-driven-development, context-engineering, deprecation-and-migration, incremental-implementation, code-simplification.

During any **build phase**, Claude proactively invokes the build-relevant skills without being asked — they apply as a matter of course. See `CLAUDE.md`'s "Build-phase skill auto-invocation" section for the exact list.

---

## 15. Common scenarios, troubleshooting, going deeper

### Common scenarios

**You just cloned the repo and want to start fresh.**

1. `/setup` — verifies your machine has the right tools.
2. `cp user-context/INTERESTS.md.example user-context/INTERESTS.md` and edit. (Or let onboarding capture it on your first message.)
3. `/scan` — produces candidate territories.
4. Read the scan, sign off (advance to `active`).
5. `/discover` — produces 10+ idea cards in the recommended territories.
6. Pick the top 3, run `/validate-card <slug>` for each.
7. Decide advance/revise/kill for each.
8. `/scope-mvp <strongest-advance>` for the winning card.
9. `/start-build <slug>` after the brief is `green-lit-to-build`.
10. `/ship-app <slug>` when the build reaches "ready to deploy."

**You have an existing card and want to move it forward.**

- Card is `discovered` → run `/validate-card <slug>`.
- Card is `validated — awaiting-user-decision` → read the validation report, then run `/scope-mvp <slug>` (advance) or tell Claude to kill / revise.
- Card is `green-lit` → run `/scope-mvp <slug>`.
- Card is `green-lit-to-build` → run `/start-build <slug>`.
- Build is "ready to deploy" → run `/ship-app <slug>`.

**Something seems off in the repo.**

- Run `/run-tests` to confirm the repo passes all 96 health checks.
- Run `/setup` to verify tools + identity.
- Run `/system-check` to compare your machine vs. requirements.
- If something is broken and you're not sure why, email the maintainer at `aanifowose111@gmail.com`.

**You want to delete an abandoned project.**

- Run `/projects` and pick the project. Two confirmations gate the actual delete. Files bypass the Trash and are removed from disk — irreversible.

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/discover` produces bland generic cards | `INTERESTS.md` is missing; falling back to open discovery | Populate `INTERESTS.md` |
| `/scan` returns territories that don't match your strengths | Same — `INTERESTS.md` missing, scan ran in open-scan mode | Populate `INTERESTS.md`, re-run `/scan` |
| `/validate-card` reviewer keeps citing the same fact you already addressed | Card text doesn't make the differentiation explicit | Revise the card to surface the differentiation in the *Problem* and *Why now* sections |
| `/scope-mvp` brief feels too ambitious | Must-haves > 6; some are could-haves in disguise | Move ambitious items to could-haves; trace each remaining must-have back to the riskiest assumption |
| `/start-build` BUILD_STATUS keeps stuck on one subsystem | Subsystem is genuinely harder than estimate, or design isn't decided | Pause; ask the orchestrator for a tradeoff analysis; consider switching to Fijara if you're stuck |
| `/ship-app` QA pre-flight returns "not-ready" | Tests don't cover the success criterion, or accessibility audit failed | Address the blockers (the report names them), then re-run `/ship-app` |
| `find -exec` or `for f in ...` triggers a Claude Code permission prompt | Workspace prefers direct-glob-args; see `CLAUDE.md` "Search patterns" | Use `grep -l "..." path/*.md` (direct glob expansion) — see `CLAUDE.md` for full details |
| zsh errors "no matches found" on empty globs | macOS zsh's `NOMATCH` default | Use `ls folder/` (folder listing) instead of `ls folder/*.md` when state may be empty; see `CLAUDE.md` "Cross-shell safety" |

### Going deeper — methodology guides

For the deepest reference on any phase, the methodology guides in `guides/` are the source of truth. The slash commands reference them directly.

| Domain | Folder | Guides |
|---|---|---|
| Product | `guides/product/` | `idea-discovery-methodology.md`, `idea-validation-methodology.md`, `mvp-scoping-methodology.md`, `build-status-methodology.md` |
| Market | `guides/market/` | `market-scan-methodology.md`, `trend-monitoring.md` |
| Funding | `guides/funding/` | `funding-strategy-methodology.md` (10-path catalog + 5-step decision framework) |
| Web | `guides/web/` | `flask-mvp-scaffold.md`, `flask-deploy-runbook.md`, `do-spaces-integration.md`, `flask-auth-patterns.md` |
| Mobile | `guides/mobile/` | `react-native-mvp-scaffold.md`, `eas-build-and-update.md`, `rn-app-store-submission.md` |
| Desktop | `guides/desktop/` | `python-mvp-scaffold.md`, `packaging-and-distribution.md` |
| UI/UX | `guides/ui-ux/` | `design-research-methodology.md`, `design-brief-methodology.md`, `design-handoff-methodology.md` |

Each guide has a first-paragraph summary if you want a quick scan before reading in full.

---

## Closing notes

This document is intentionally long because the workspace is intentionally end-to-end. You won't need every section — you'll come back to whichever phase you're in.

The condensed in-terminal version of this same content lives behind the `/documentation` slash command. Running it surfaces the workflow with your *current state* as the examples (so when it explains `/validate-card`, it can use your actual existing validation reports as the example).

Feedback, bug reports, and contributions go to the maintainer at `aanifowose111@gmail.com`. Pull requests welcome from forkers — see `CONTRIBUTING.md` for the contribution process.
