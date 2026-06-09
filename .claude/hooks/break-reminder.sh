#!/usr/bin/env bash
# Break-reminder hook for Claude Code (UserPromptSubmit event).
#
# Fires once when active session has been running >2 hours, throttled to 1 hour
# between subsequent reminders. Output: JSON via `hookSpecificOutput.additionalContext`
# per Claude Code hook spec — Claude sees the reminder as a system note and decides
# how to surface it (per CLAUDE.md § Break-reminder convention, that means
# AskUserQuestion at the next natural conversation boundary).
#
# State files (gitignored, user-private):
#   ~/.claude/.session-start         epoch seconds, set on first hook fire (or by SessionStart hook)
#   ~/.claude/.last-prompt           epoch seconds, updated on every prompt — for idle detection
#   ~/.claude/.last-break-reminder   epoch seconds, set when reminder fires
#
# Idle detection: if the gap between the previous prompt and now is > IDLE_THRESHOLD,
# the user was almost certainly away (laptop closed, took a break, etc.). Reset
# `.session-start` to now so the timer reflects active session time, not wallclock.
#
# Pairs with .claude/hooks/session-start-reset.sh (SessionStart hook) which
# resets `.session-start` at every fresh Claude Code session start.
#
# To reset the timer manually: rm -f ~/.claude/.session-start
# To temporarily disable: chmod -x ~/.claude/hooks/break-reminder.sh

set -euo pipefail

STATE_DIR="${HOME}/.claude"
SESSION_START_FILE="${STATE_DIR}/.session-start"
LAST_PROMPT_FILE="${STATE_DIR}/.last-prompt"
LAST_REMINDER_FILE="${STATE_DIR}/.last-break-reminder"

# Tunables (seconds)
INTERVAL_SECONDS=7200    # 2 hours before first reminder
THROTTLE_SECONDS=3600    # 1 hour between subsequent reminders
IDLE_THRESHOLD=1800      # 30 min gap between prompts means user was away — reset timer

mkdir -p "${STATE_DIR}"
NOW=$(date +%s)

# Initialize session-start on first run of a fresh session
if [ ! -f "${SESSION_START_FILE}" ]; then
  echo "${NOW}" > "${SESSION_START_FILE}"
  echo "${NOW}" > "${LAST_PROMPT_FILE}"
  exit 0
fi

# Idle detection: if the gap from last prompt to now is huge, the user was away
# (closed laptop / went to lunch / left for hours). Reset session-start to now.
if [ -f "${LAST_PROMPT_FILE}" ]; then
  LAST_PROMPT=$(cat "${LAST_PROMPT_FILE}")
  IDLE_GAP=$((NOW - LAST_PROMPT))
  if [ "${IDLE_GAP}" -gt "${IDLE_THRESHOLD}" ]; then
    echo "${NOW}" > "${SESSION_START_FILE}"
    rm -f "${LAST_REMINDER_FILE}"   # also clear so the throttle doesn't block the next reminder
  fi
fi

# Always update last-prompt
echo "${NOW}" > "${LAST_PROMPT_FILE}"

SESSION_START=$(cat "${SESSION_START_FILE}")
ELAPSED=$((NOW - SESSION_START))

# Not yet at interval — exit silently
if [ "${ELAPSED}" -lt "${INTERVAL_SECONDS}" ]; then
  exit 0
fi

# Throttle check — don't re-fire within THROTTLE_SECONDS of the last reminder
if [ -f "${LAST_REMINDER_FILE}" ]; then
  LAST_REMINDER=$(cat "${LAST_REMINDER_FILE}")
  SINCE_LAST=$((NOW - LAST_REMINDER))
  if [ "${SINCE_LAST}" -lt "${THROTTLE_SECONDS}" ]; then
    exit 0
  fi
fi

# Fire reminder
HOURS=$((ELAPSED / 3600))
MINUTES=$(((ELAPSED % 3600) / 60))
echo "${NOW}" > "${LAST_REMINDER_FILE}"

# Build a single-line additionalContext string (JSON-escaped: no literal newlines in the value).
# Cap stays well under the 10k char limit.
CONTEXT="[BREAK-REMINDER HOOK FIRED] This Claude Code session has been active for ${HOURS}h ${MINUTES}m. Per CLAUDE.md § Break-reminder convention, surface the following to the user via AskUserQuestion at the next natural conversation boundary — do NOT interrupt your current task; finish what you are doing first, then surface. Question: 'You have been working for ~${HOURS}h ${MINUTES}m. Want to take a break?' Options: (a) 'Caffeinate — keep going' → on pick, run shell 'rm -f ${SESSION_START_FILE}' to reset the timer, then continue normally. (b) 'Pause now' → wrap up cleanly; suggest the user run /recollect <slug> when they return. (c) 'Stop after X and Y' → ask the user what X and Y are, complete those, then re-prompt with the same question. (d) 'Other — describe what you want' → honor the user's custom plan. Do NOT mention the hook by name; surface this naturally as a workspace check-in."

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "${CONTEXT}"
  }
}
EOF
