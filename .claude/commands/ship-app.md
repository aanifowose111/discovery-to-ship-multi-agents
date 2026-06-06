---
description: Initialize the shipment / release phase for a built product. Runs the release-readiness gate (QA + security pre-flight), invokes senior-devops-engineer to execute the actual deploy (web via flask-deploy-runbook.md, mobile via EAS build + app-store submission, desktop via PyInstaller + sideload/signing), then runs post-deploy verification. Distinct from /start-build (which handles build through ready-to-deploy state).
argument-hint: <product-slug> [--web|--mobile|--desktop|--all]
---

You are about to initialize the shipment / release phase for a product whose build is substantially complete. **This is a gated, deliberate phase** — the user explicitly chooses to ship, and the flow forces a release-readiness pass before any production change.

This command is the natural sequel to `/start-build`. `/start-build` brings the product from empty repo through database → models → API → frontend → integration tests → "ready to deploy" state. `/ship-app` takes it from there: pre-flight checks, actual deploy, post-deploy verification.

### Inputs to read before starting

- @CLAUDE.md (working style, pipeline rules)
- `<web-apps|mobile-apps|desktop-apps>/<slug>/MVP.md` — for the success criterion + build-support pick
- `<web-apps|mobile-apps|desktop-apps>/<slug>/BUILD_STATUS.md` — for current build state (must reflect substantially-complete build)
- The relevant runbooks based on stack:
  - **Web (Flask default):** `guides/web/flask-deploy-runbook.md` + `guides/web/do-spaces-integration.md` (if uploads scoped)
  - **Mobile (RN default):** `guides/mobile/eas-build-and-update.md` + `guides/mobile/rn-app-store-submission.md`
  - **Desktop (Python + PySide6 default):** `guides/desktop/packaging-and-distribution.md`
  - **Non-default stack:** the user-confirmed stack from §6 of `guides/product/mvp-scoping-methodology.md`; work from first principles + agent-skills' `shipping-and-launch` + `ci-cd-and-automation` skills

### Do

1. **Resolve scope.** If `$ARGUMENTS` is empty: error and ask for `<slug>`. Parse trailing flag:
   - `--web` → web only (default if MVP brief lists only a web app)
   - `--mobile` → mobile only (default if MVP brief lists only a mobile app)
   - `--desktop` → desktop only (default if MVP brief lists only a desktop app)
   - `--all` → ship every domain present in the brief (default for hybrid briefs spanning 2+ domains; ship in this order if no other signal: web → mobile → desktop)
   - No flag → infer from the MVP brief's must-have surface. For backward compatibility, `--both` is accepted as an alias for `--all`.

2. **Verify build readiness.** Read `BUILD_STATUS.md` for this product. If core subsystems (database, models, API, frontend skeleton, integration tests, deploy slot) are not all `[x]`, **stop and tell the user**: "BUILD_STATUS.md shows N incomplete subsystems (<list>). Finish the build via `/start-build <slug>` (or pick up where it stopped) before shipping." Do not proceed.

3. **Release-readiness gate — Step 1 of 2 (QA pre-flight).** Invoke `senior-qa-engineer` via the custom-subagent pattern (per @CLAUDE.md "Invoking custom subagents"):
   - Final test pass: every integration-test scenario from `BUILD_STATUS.md` passes against the current main branch.
   - Acceptance criteria check: the MVP brief's success criterion (e.g., "first 10 users complete the core flow without help") has a corresponding test or a documented manual verification plan.
   - Accessibility spot-check: critical interactive paths pass basic WCAG (color contrast, keyboard nav, semantic markup).
   - Output: a "release-ready" or "not-ready" verdict + a list of any blocking issues.
   - **If "not-ready", stop**; surface the blockers, suggest `/start-build` resumption to address them, and don't proceed to step 4.

4. **Release-readiness gate — Step 2 of 2 (security pre-flight).** Invoke `senior-security-engineer` via the custom-subagent pattern:
   - Auth: session handling, password storage (if applicable), and JWT/cookie config reviewed.
   - Secrets: no `.env` content committed; production secrets injection mechanism verified (DigitalOcean App Platform env vars or droplet `.env` for Flask; EAS secrets for mobile).
   - Input boundaries: at every user-input surface, validation + escaping is in place.
   - File I/O / external integrations: tight scope, principle of least privilege.
   - OWASP-style spot check: SQL injection, XSS, CSRF, SSRF, IDOR.
   - Output: "ship-safe" or "blockers" + list of any findings.
   - **If "blockers", stop**; surface them, and the user decides whether to address before shipping or accept (rare and should be documented in BUILD_STATUS.md).

5. **User confirms ship.** Present a summary: target environment (production / staging / sideload), stack, scope (web / mobile / desktop / multiple), QA verdict, security verdict, the deploy steps that will run. Use `AskUserQuestion`:
   - **Ship now** — proceeds to step 6.
   - **Cancel** — exits without shipping.

6. **Execute the deploy.** Invoke `senior-devops-engineer` via the custom-subagent pattern. Hand off the relevant runbook and the product's stack-specific context. The persona executes the deploy per the runbook, narrating each step to the user as it goes. For:
   - **Web (Flask default):** build Docker image → push to registry → deploy to target (App Platform or droplet) → confirm HTTPS via Caddy → confirm health endpoint responds → confirm DNS resolves to deploy.
   - **Mobile (RN default):** `eas build --profile production --platform <ios|android|all>` → wait for build to complete → submit to TestFlight / Play Console internal track → confirm reviewer receipt.
   - **Desktop (Python + PySide6 default):** `bash scripts/build.sh` → confirm `dist/<App Name>.app` (or `.exe`/AppImage) exists and opens → generate the sideload README snippet (right-click-Open instructions for first 10 users). v1 path adds `codesign` + `notarytool` (macOS) or `signtool` (Windows) — only if the user explicitly opts in to signed-shipment mode.
   - **Other stacks:** follow the user's documented deploy plan from MVP.md §7 (or its equivalent).

7. **Post-deploy verification.** Same persona (`senior-devops-engineer`) runs the smoke tests:
   - **Web:** `curl <production-url>/healthz`, hit a few critical pages, check the production error log for new errors in the 5 minutes since deploy.
   - **Mobile:** install the published preview build on a simulator / Expo Go, exercise the core flow once.
   - **Desktop:** `open dist/"<App Name>.app"` (macOS) or run the built binary on the target platform; exercise the core flow once; check for missing-dep warnings in `~/Library/Logs/DiagnosticReports/` (macOS) or Event Viewer (Windows).
   - Output: "ship verified" or "post-deploy issues found".

8. **Update `BUILD_STATUS.md`.** `senior-software-engineer` (the BUILD_STATUS owner) writes an entry recording: deploy timestamp, deployed version (git SHA), target environment, deploy mode (web / mobile / desktop / multi), QA + security verdicts, post-deploy verification result. Status marker changes from `[>]` to `[x]` for the "Deploy" / "Release" subsystem.

9. **Append a `build-milestone` audit-log entry** (per `CLAUDE.md` § Audit log):

   ```
   python3 scripts/audit_log.py add build-milestone "Build milestone for <slug>: shipped to <environment> via /ship-app (<stack>, git SHA <short-sha>, QA: <verdict>, security: <verdict>, post-deploy: <result>)."
   ```

### Stop here — user checkpoint

After post-deploy verification, **stop**. Show the user:

> Shipped `<slug>` to `<environment>` at `<production-url-or-app-store-link>`. QA: <verdict>. Security: <verdict>. Post-deploy: <result>.
>
> **Next steps:**
> - **Hand the link to your first 10 users** (per the MVP brief's success criterion) and watch for the riskiest-assumption signal.
> - If a post-deploy issue surfaced: `/start-build <slug>` to resume in fix mode, then `/ship-app <slug>` again.
> - If the riskiest assumption fails: kill the card and move on; do *not* iterate the design or rebuild the v1.
> - If the riskiest assumption holds: optional `/research-design <slug>` for the design phase before a real v1.

### Important — no auto-actions, no destructive shortcuts

- **NEVER** ship without both pre-flight gates passing (or explicit user override documented in BUILD_STATUS.md).
- **NEVER** push a `--force` or skip a rollback path.
- **NEVER** auto-chain into iteration after a post-deploy issue — the user decides whether to fix-and-reship or escalate.
- If the user's product has no real users yet, "ship to production" means "ship the v0 to the first 10 users named in the success criterion" — not a public marketing launch.
