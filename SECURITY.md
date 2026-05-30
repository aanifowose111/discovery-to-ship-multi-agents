# Security Policy

## Supported versions

This project is in active development. Security fixes are applied to the `main` branch. There are no long-term-support versions; users should track `main` for the latest fixes.

## Reporting a vulnerability

If you discover a security vulnerability — credentials exposure, injection-style risks in the Flask scaffold defaults, code-execution risks in the web-preview or doc-export skills, supply-chain concerns in the agent-skills submodule reference, or anything else that could harm a user of this workspace — **please report it privately first**, before opening a public issue or PR.

📧 **Email: aanifowose111@gmail.com**

**Subject line:** `[discovery-to-ship security]`

In your report, include:

- A clear description of the issue.
- Steps to reproduce (or proof-of-concept).
- The impact you observed or believe possible.
- Any suggested mitigation, if you have one.
- Whether you'd like to be credited in the eventual fix's commit / CHANGELOG entry.

## What to expect

- **Acknowledgment** within 7 days of your report (usually faster).
- An initial **assessment** within 14 days — whether the issue is reproducible, what its scope is, and a rough estimate of the fix timeline.
- The fix landed in `main` (or a clear explanation of why we're not fixing it — e.g., a documented known limitation rather than a bug).
- **Credit** in the CHANGELOG entry for the fix, unless you've asked not to be credited.

## Scope

This project is documentation + slash commands + agent personas + a couple of helper Python scripts. The attack surface is small but non-zero. Examples of in-scope issues:

- A slash command that could be tricked into writing to an unintended path.
- A skill (like `web-preview` or `doc-export`) whose default invocation could execute arbitrary code on the user's machine without their consent.
- Documented patterns in the Flask auth guide (`guides/web/flask-auth-patterns.md`) or the storage guide (`guides/web/do-spaces-integration.md`) that, if followed exactly, would produce insecure production code.
- A reviewer persona that could be coerced into leaking the user's private content through web-fetched URLs.
- The agent-skills submodule reference pointing to a compromised commit.

Out of scope:

- Issues in **products built using this workspace** — those are the product author's responsibility; this workspace provides scaffolding, not application security guarantees.
- Issues in the [upstream agent-skills repo](https://github.com/aanifowose111/agent-skills) — report those to that repo separately.
- Issues in third-party services we link to (DigitalOcean, Stripe, Expo, etc.) — report to those vendors.
- Best-practice debates about specific code style choices in the guides — those go through the normal `CONTRIBUTING.md` flow, not the security flow.

## Disclosure timeline

The default expectation is **coordinated disclosure**: we fix the issue in `main` first, then you (the reporter) can publicly discuss it. If a fix is taking longer than 90 days and you'd like to disclose anyway, we'll work with you on a date.

For low-severity issues with no realistic exploit path, public discussion can happen immediately — but please still report to the email first so we can acknowledge.

## Thanks

This project's value depends on trust. If you take the time to report a security issue here instead of exploiting it or going straight to public disclosure, that matters. Thank you.
