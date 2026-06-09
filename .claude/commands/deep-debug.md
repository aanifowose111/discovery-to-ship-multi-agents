---
description: Invoke the senior-debugging-engineer for deep root-cause analysis on a specific failure. Use when a bug crosses domain boundaries (backend+frontend race, deploy failure with non-obvious cause, intermittent production bug, flaky test), when existing senior-X-engineers haven't pinned it down, or when reviewer-flagged bugs keep being overridden without understanding. Optional second argument focuses the investigation. Returns a structured report (hypothesis → reproduction → root cause → fix recommendation); does NOT write the fix.
argument-hint: <product-slug> [focus-area-or-file-or-symptom]
---

You are about to invoke `senior-debugging-engineer` for deep root-cause analysis on one specific failure in one product. This is **not** the general-purpose debugging path — for routine bugs, the existing `senior-X-engineer` + `debugging-and-error-recovery` skill is the right tool. Use `/deep-debug` when the failure has resisted normal debugging.

**Use this when:**
- A flaky test fails intermittently and standard approaches haven't pinned it down
- A bug crosses domain boundaries (backend behaves correctly + frontend behaves correctly, but together they fail)
- A deploy fails for non-obvious reasons (Docker layer caching + dependency conflict, env-var differences staging vs. prod)
- An intermittent production bug has no clear pattern
- A reviewer keeps flagging the same concern and the user keeps overriding without understanding

**Don't use this for:**
- Simple bugs where the stack trace points at the line (use `senior-X-engineer` directly)
- Performance issues (use `performance-optimization` skill)
- "Help me understand my code" (different conversation, not debugging)

**Arguments:** $ARGUMENTS

Parse for:
- `<slug>` (positional, required) — the product folder name
- `[focus-area]` (positional, optional) — file path (`api/auth.py`), subsystem name (`auth`), or symptom description (`"login flow hangs after OAuth callback"`). The focus narrows the investigation but doesn't constrain hypotheses.

### Pre-flight

1. **Locate the product folder.** Check `web-apps/<slug>/`, `mobile-apps/<slug>/`, `desktop-apps/<slug>/`. If none exists, stop with explanation.

2. **Verify the product has a build in progress.** Check that `BUILD_STATUS.md` exists. If not, surface to the user: "No `BUILD_STATUS.md` for `<slug>` — has the build started? `/deep-debug` is for runtime/build-time failures, not pre-build issues. Want me to proceed anyway?" Default to confirm.

3. **Capture context the user has already provided.** Scan the conversation history (or ask the user to paste):
   - Error message verbatim
   - Stack trace
   - Log lines
   - What they were doing when it happened
   - What they expected vs. what they observed
   - How often it reproduces

   If the user hasn't provided any of this, ask via free-text: "What's the bug? Paste the error message, stack trace, or log lines if you have them — and tell me what you expected vs. what happened." Wait for the reply before proceeding.

### Do

Invoke `senior-debugging-engineer` using the custom-subagent invocation pattern in `CLAUDE.md`:

```
Agent({
  subagent_type: "general-purpose",
  description: "Deep debug for <slug>",
  prompt: "You are about to act as senior-debugging-engineer. Step 1: read .claude/agents/senior-debugging-engineer.md in full and treat its body as your role, lens, process, evidence standards, rationalizations to refuse, and output format. Step 2: read the brief at <product-folder>/MVP.md (or V1.md if green-lit-to-build), <product-folder>/BUILD_STATUS.md, <product-folder>/design/DESIGN_SPEC.md if it exists (for frontend-adjacent bugs), and CLAUDE.md. Step 3: read the relevant source files in <product-folder> — use Grep + Read targeted at the focus area '<focus-area-or-empty>' and the symptom. Bias toward reading the most-recently-modified files (mtime-sorted). Step 4: capture user-provided context: '<verbatim symptom+context block from user>'. Step 5: run the 5-phase process from the persona (Reproduce → Hypothesize → Test each hypothesis → Identify root cause → Fix recommendation). Step 6: if you add any temporary instrumentation (print statements, log lines, asserts) to test hypotheses, REMOVE them before returning OR explicitly flag each one that remains so the specialist persona can clean up. Step 7: return the report in the EXACT format locked at the bottom of the persona file."
})
```

Wait for the agent to return the report.

### Stop here — user checkpoint

After the agent returns, **stop**. Do NOT auto-invoke any specialist to apply the fix. Show the user:

> 🔍 **Deep-debug report for `<slug>`:**
>
> **Root cause:** <one-line summary from the report's Root cause section>
> **Location:** `<file>:<line>` (or commit `<sha>`)
> **Confidence:** `<HIGH | MEDIUM | LOW>`
>
> **Top hypotheses tested:**
> 1. ✓ **<name>** — <CONFIRMED | RULED OUT, one-line>
> 2. ✓ **<name>** — <CONFIRMED | RULED OUT, one-line>
> 3. ✓ **<name>** — <CONFIRMED | RULED OUT, one-line>
>
> **Fix recommendation:**
> - **Minimal fix:** <one-line>
> - **Defensive additions:** <one-line>
> - **Owner persona:** `<senior-X-engineer>`
>
> Full report shown above. Your call:
> - **Apply the fix** → I invoke `<senior-X-engineer>` with the report as input; they implement against it
> - **Investigate further** → tell me what hypothesis to explore deeper, or what additional context to consider; I re-invoke `senior-debugging-engineer` with the addition
> - **Sit on it** — record the report for later (I can save it to `<product-folder>/debug-reports/<YYYY-MM-DD>-<short-symptom>.md`)
> - **Reject the diagnosis** — you disagree with the root cause; tell me why and I'll re-investigate

Only after the user picks an action, proceed accordingly:
- **Apply the fix** → invoke the named specialist with the report in the prompt as authoritative input
- **Investigate further** → re-invoke `senior-debugging-engineer` with the added context
- **Sit on it** → write the report to `<product-folder>/debug-reports/<date>-<symptom-slug>.md`
- **Reject** → re-invoke with the user's pushback

### Notes

- **No audit-log entry.** Debugging is not a state decision; it's investigation.
- **Temp instrumentation cleanup is the agent's responsibility.** If anything was added (print statements, logs, asserts), the agent removes it OR flags it for the specialist to clean.
- **The specialist (`senior-X-engineer`) is the one who applies the fix.** This command + persona produce the diagnosis only — not the patch. Separation keeps the diagnostic discipline from leaking into "fix-driven development".
- **Cost-conscious:** the senior-debugging-engineer reads many files. If the focus-area is very narrow (e.g., a single file path), the agent reads less. Pass a focus when you can.
- **Cross-product reasoning is out of scope.** This command operates on ONE product at a time. If a bug spans two products (e.g., the parent workspace's scripts + a product), open separate debug sessions for each surface.
