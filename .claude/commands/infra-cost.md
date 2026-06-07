---
description: Estimate the infrastructure cost of running an MVP (or V1) — minimum / medium / max scenarios, broken down by user base, with each cost item flagged as recurring vs. one-time and user-dependent vs. fixed. Reads MVP.md (and optionally V1.md) to extract stack and infrastructure decisions, then fetches current pricing for each vendor and assembles a cost table. Optionally writes the report to `<stack>-apps/<slug>/INFRA_COST.md`.
argument-hint: <slug> [--save | --users=10,100,1000 | --include-v1]
---

You are about to estimate the infrastructure cost of running a product's MVP (and optionally V1). The goal is to give the user honest numbers so they can answer "can I afford to ship this MVP and keep it running at the user counts in my success criterion?" The pipeline already produces an effort estimate (per the time-estimation framing in `mvp-scoping-methodology.md` §5); this command produces the *money* estimate.

**Arguments:** `$ARGUMENTS` — parse as `<slug> [optional flags]`:
- `--save` → write the report to `<stack>-apps/<slug>/INFRA_COST.md` in addition to surfacing it (default: surface only)
- `--users=A,B,C` → custom user-count tiers for the three scenarios (default: `10,100,1000` keyed to MVP first-10 / post-validation / steady-state)
- `--include-v1` → also estimate V1.md if it exists (default: MVP only)

### Inputs to read before estimating

1. **Locate the product folder** and the briefs:
   - MVP.md at `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md`
   - V1.md at the same folder, if `--include-v1` is passed and the file exists

2. **Extract from the brief(s):**
   - **Stack** (Flask / RN / PySide6 / other) — drives which infra costs apply
   - **Infrastructure decisions** (§6 of `mvp-scoping-methodology.md` — `.env`, DO Spaces / S3, hosting target, auth approach, background jobs?)
   - **Must-haves** — does any must-have require an LLM call, an email send, a file upload, a payment, an outbound API call, a third-party integration?
   - **Success criterion** — gives you the user-count baseline (the `--users` default of 10 comes from "first 10 users")
   - **Stretches** that imply new infra (e.g., "real-time websockets" → managed Redis; "audio transcription" → STT API)

3. **Take a careful inventory of cost-bearing dependencies** the brief mentions explicitly OR implies. Per-stack hints:

   | Stack | Likely cost categories |
   |---|---|
   | Flask web (default) | DO droplet OR App Platform; managed Postgres (or self-hosted on droplet); DO Spaces (if file uploads); domain + DNS; TLS via Caddy (free) or LetsEncrypt; email vendor (Resend, Postmark, SendGrid); LLM API (Claude / OpenAI / Gemini); auth (Clerk / Auth0 / self-hosted); Stripe (if paid); monitoring (Sentry / BetterStack); CDN (Cloudflare); backups |
   | RN + Expo (mobile) | EAS Build (per-build); EAS Submit (per-submission); EAS Update (per-MAU); Apple Developer Program ($99/year); Google Play Console ($25 one-time); backend (same Flask cost shape if applicable); push notifications (Expo / OneSignal / Firebase); analytics |
   | PySide6 desktop | Code signing certificate (~$200-400/year per platform); notarization (free for macOS via Apple Developer); auto-updater hosting (DO Spaces, S3, GitHub Releases); telemetry backend (if any); installer distribution (download host) |

### Do

#### Step 1 — Confirm scope + user-count tiers

Echo back what you read:

> Estimating infra cost for `<slug>`:
> - Stack: <Flask / RN / PySide6 / other>
> - MVP brief: `<path>` (extracted N cost-bearing dependencies — list them)
> - V1 brief: `<path>` (extracted M extra V1-only dependencies — list them) [show only if --include-v1]
> - User tiers: <10, 100, 1000> [or user's --users override]
> - Save report after? <yes if --save, no otherwise>
>
> If any dependency is ambiguous in the brief (e.g., "uses LLM" without specifying which model or how many tokens), I'll flag it and use a sensible default range. Proceed? — Yes / Adjust tiers / Cancel.

#### Step 2 — Fetch current pricing for each cost item

For each cost-bearing dependency, **fetch the current public pricing page** (per `CLAUDE.md § Internet access policy` — web fetches happen by default during this command). Cite the URL and the date of the fetch.

For LLM costs specifically, compute per-user-per-month based on:
- Model picked in the brief (default Claude Sonnet if unspecified — flag the assumption)
- Estimated tokens per user-action × actions per user per month
- If the brief is silent on token volume, use a **range** (low = 5k input + 1k output per user/month; medium = 50k+10k; high = 500k+100k) and surface the bands explicitly.

For each item, decide:
- **Type:** `infra` (server / storage / DNS), `per-use` (LLM / payments / email-per-send), `subscription` (Sentry / Clerk MAU tier), `one-time` (Apple Dev fee paid yearly, but listed once with the yearly amortization)
- **Recurring?** Yes / No (and how often if yes — monthly / yearly / per-action)
- **User-dependent?** Yes (scales with users) / No (fixed) / Stepped (jumps at a tier breakpoint, e.g., free tier ends at 100 MAU)

#### Step 3 — Build the cost table

```
| Cost item | Vendor | Type | Min (<X> users) | Med (<Y> users) | Max (<Z> users) | Recurring? | User-dependent? | Source |
|---|---|---|---|---|---|---|---|---|
| Droplet (basic 1GB) | DigitalOcean | Infra | $6/mo | $12/mo | $48/mo | Yes (monthly) | Stepped (sizes up at ~200 users) | <url> (fetched <date>) |
| Managed Postgres | DigitalOcean | Infra | $15/mo | $15/mo | $30/mo | Yes (monthly) | Stepped (DB-1 → DB-2 at ~500 users) | <url> |
| LLM API (Claude Sonnet @ ~10k tok/user/mo) | Anthropic | Per-use | $0.50/mo | $5/mo | $50/mo | Yes (per-use) | Yes (linear) | <url> |
| Domain (yearly amortized) | Namecheap | Infra | $1/mo | $1/mo | $1/mo | Yes (yearly billing) | No (fixed) | <url> |
| Stripe processing | Stripe | Per-use | $0/mo (no rev) | $30/mo (10% conv × $30 ARPU × 10% fee) | $300/mo | Yes (per-tx) | Yes | <url> |
| Sentry error tracking | Sentry | Subscription | $0/mo (free tier) | $0/mo (free) | $26/mo (Team) | Yes (monthly) | Stepped (free → paid at 5K events/mo) | <url> |
| Email (Resend) | Resend | Per-use | $0/mo (3K free) | $0/mo (10K still free) | $20/mo (50K) | Yes (monthly) | Stepped | <url> |
| Apple Developer Program | Apple | One-time/yearly | $8/mo (annualized) | $8/mo | $8/mo | Yes (yearly) | No | <url> |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

#### Step 4 — Summary stats

After the table, surface:

```
=== Summary ===

Total monthly burn:
  Min (<X> users):    $A.AA/mo  (yearly equiv: $A.AA × 12 = $YEARLY.AA)
  Med (<Y> users):    $B.BB/mo  (yearly equiv: $B.BB × 12 = $YEARLY.BB)
  Max (<Z> users):    $C.CC/mo  (yearly equiv: $C.CC × 12 = $YEARLY.CC)

Of which fixed (not user-dependent):
  ~$F/mo across all tiers — domain, base server, Apple Developer Program, monitoring base, etc.

Of which variable (user-dependent):
  Min:  $V_min/mo
  Med:  $V_med/mo
  Max:  $V_max/mo
  This is the bit that scales with usage. LLM API and per-transaction fees dominate at the Max tier.

Recurring admin/dev costs the maintainer pays regardless of users:
  ~$R/mo — includes domain renewal, Apple Developer fee, base droplet, monitoring base.

One-time / setup costs (year-1 only):
  ~$O — includes Google Play one-time ($25), code-signing cert one-time (~$0 for macOS via Apple Dev, ~$200 for Windows code-sign), domain registration first year (often discounted).
```

#### Step 5 — Caveats & assumptions

List **every assumption** you made — the user needs to see them to judge whether the estimate fits their actual usage:

> **Assumptions used:**
> - LLM tokens per user per month: 10K input + 2K output (Claude Sonnet pricing). If your actual usage differs, multiply proportionally.
> - Stripe conversion rate: 10% (paying users / total users). If your conversion is higher, the Stripe fees scale up.
> - ARPU: $30/month per paying user. Pull from the brief's `priced-at:` if set.
> - Email volume: ~5 emails per user per month. Adjust for your actual flow.
> - No reserved instances or annual prepay discounts applied — these can save 20-40% on infra.
> - Prices fetched on `<YYYY-MM-DD>`. Vendor pricing changes; treat as a 30-day snapshot.
> - Stack-specific costs only listed if the stack was named in the brief. If the brief was silent on a category (e.g., monitoring), I've assumed the typical default and flagged it.

#### Step 6 — Save report (if --save was passed)

If `--save` was in the arguments:

1. Format the table + summary + caveats as a markdown report.
2. Write to `<stack>-apps/<slug>/INFRA_COST.md` with frontmatter:
   ```yaml
   ---
   slug: <slug>
   brief-version: <mvp | v1>
   user-tiers: [<X>, <Y>, <Z>]
   date-estimated: <YYYY-MM-DD>
   ---
   ```
3. Show the user the saved path.

If `--save` was NOT passed, the user can ask to save later or just keep it in the transcript.

#### Step 7 — Stop with next-step suggestions

> Cost estimate complete for `<slug>` at user tiers `<X> / <Y> / <Z>`.
>
> - Min monthly burn: $A.AA → yearly: $YEARLY.AA
> - Med monthly burn: $B.BB → yearly: $YEARLY.BB
> - Max monthly burn: $C.CC → yearly: $YEARLY.CC
>
> Next steps:
> - If the cost looks too high vs. expected revenue: `/reprice <slug>` to revise the price; OR rework the MVP scope via `/rework <slug>` to drop must-haves that drive cost.
> - If a specific cost item dominates (e.g., LLM API): inspect whether you can cache, batch, downgrade to a cheaper model, or move logic server-side.
> - If you want this report saved permanently: re-run `/infra-cost <slug> --save`.
> - If you also want V1 costs: `/infra-cost <slug> --include-v1`.

### Important — no auto-actions, no destructive shortcuts

- **NEVER auto-save the report** unless `--save` was passed.
- **NEVER overwrite an existing `INFRA_COST.md`** without confirming with the user first. Suggest a date suffix (`INFRA_COST-<YYYY-MM-DD>.md`) if a recent estimate already exists.
- **NEVER make up prices.** Every number traces to a URL fetched during this run. If a vendor's pricing isn't public or requires sales contact, flag it as "estimate range" and explain why.
- **NEVER recommend skipping monitoring / backups** to reduce cost. Those are not optional past first-10-users; flag if the brief silently omitted them.

### Notes

- **Why three tiers?** The min tier is the cost of "MVP just shipped to first 10 users" — the floor. The med tier is "validation held, growing toward 100 users." The max tier is "v1 launched, ~1000 users in steady state." If the user has different tier breakpoints in mind (e.g., 5 / 50 / 500), pass `--users=5,50,500`.
- **What's NOT covered.** This estimate is infrastructure only. It does NOT include the founder's time, marketing/ads, customer-acquisition costs, legal/accounting fees, or the agent-skills/Claude Code subscription. Those are separate budget categories.
- **Why fetch pricing instead of baking it in?** Vendor pricing changes 1-3x per year. Hard-coding it would surface stale numbers; fetching makes the report accurate at the moment of estimation. Per `CLAUDE.md § Internet access policy`, web fetches don't require permission prompts.
- **Stack vs. cost.** Mobile is generally more expensive than web (EAS subscriptions, Apple Developer Program, Google Play, push notifications). Desktop is generally cheaper than web (no server, but code signing fees vary). Web is in the middle. The estimate reflects this.
