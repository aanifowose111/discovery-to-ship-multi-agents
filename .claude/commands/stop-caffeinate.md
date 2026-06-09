---
description: Stop the backgrounded `caffeinate` process started by /caffeinate. Reads the PID from `~/.claude/caffeinate.pid`, sends SIGTERM, removes the pidfile. macOS-only (no-op on other platforms — same caveat as /caffeinate).
argument-hint: (no arguments)
---

You are about to stop the backgrounded `caffeinate` process started earlier by `/caffeinate`.

### Pre-flight

1. **Platform check.** Run `uname -s`. If the result is NOT `Darwin`, stop and tell the user:
   > `/stop-caffeinate` is macOS-only (pairs with `/caffeinate`). If you used a Linux/Windows equivalent, stop it the way you started it.

   Then stop.

2. **Check for pidfile.** Run:
   ```bash
   if [ -f ~/.claude/caffeinate.pid ]; then
     PID=$(cat ~/.claude/caffeinate.pid)
     if kill -0 "$PID" 2>/dev/null; then
       echo "FOUND_ALIVE|$PID"
     else
       echo "FOUND_DEAD|$PID"
     fi
   else
     echo "NOT_FOUND"
   fi
   ```

   - **FOUND_ALIVE:** continue to Step 1.
   - **FOUND_DEAD:** the pidfile points at a PID that no longer exists. Tell the user: "Caffeinate process (PID `<pid>`) was already gone. Cleaning up the stale pidfile." Then `rm ~/.claude/caffeinate.pid`. Done — no kill needed.
   - **NOT_FOUND:** tell the user "No caffeinate process is running (no pidfile at `~/.claude/caffeinate.pid`). If you started caffeinate manually outside `/caffeinate`, kill it with `pkill caffeinate` or `kill <pid>`." Then stop.

### Do

1. **Kill the process.** Run:
   ```bash
   PID=$(cat ~/.claude/caffeinate.pid)
   kill "$PID" 2>&1 || echo "KILL_FAILED|$PID"
   ```

2. **Wait briefly + verify.** Run:
   ```bash
   sleep 1
   if kill -0 "$PID" 2>/dev/null; then
     echo "STILL_RUNNING|$PID"
   else
     echo "STOPPED|$PID"
   fi
   ```

   - **STOPPED:** good. Remove the pidfile: `rm ~/.claude/caffeinate.pid`.
   - **STILL_RUNNING:** process didn't respond to SIGTERM in 1 second. Send SIGKILL: `kill -9 "$PID"`, then remove the pidfile. Surface this as a (minor) warning — the process resisted graceful shutdown for some reason but is now gone.

### Report to user

> ☕ Caffeinate stopped. Display + system will sleep normally again.
>
> - PID released: `<pid>`
> - Pidfile cleaned up: `~/.claude/caffeinate.pid`

### Notes

- **Idempotent.** Running `/stop-caffeinate` when nothing is caffeinated is safe — surfaces a benign "nothing to stop" message and does nothing else.
- **No audit log entry.** Same as `/caffeinate`.
