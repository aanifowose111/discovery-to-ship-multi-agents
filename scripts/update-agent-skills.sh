#!/usr/bin/env bash
# update-agent-skills.sh — pull the latest commits from the agent-skills
# upstream into the submodule and stage + commit the new submodule SHA in
# the parent repo. Push remains the user's choice.
#
# Usage: bash scripts/update-agent-skills.sh [--dry-run]

set -euo pipefail

DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=1 ;;
        -h|--help)
            echo "Usage: bash scripts/update-agent-skills.sh [--dry-run]"
            echo
            echo "  --dry-run   show what would happen without committing"
            exit 0
            ;;
    esac
done

if [ -t 1 ]; then
    GREEN=$'\e[32m'; YELLOW=$'\e[33m'; CYAN=$'\e[36m'; BOLD=$'\e[1m'; RESET=$'\e[0m'
else
    GREEN=""; YELLOW=""; CYAN=""; BOLD=""; RESET=""
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -d external/agent-skills/.git ] && [ ! -f external/agent-skills/.git ]; then
    echo "${YELLOW}external/agent-skills is not a submodule yet. Initializing...${RESET}"
    git submodule update --init --recursive
fi

cd external/agent-skills
old_sha="$(git rev-parse HEAD)"
echo "${BOLD}Current agent-skills SHA:${RESET} $old_sha"

echo "${CYAN}Fetching from upstream...${RESET}"
git fetch --quiet origin

default_branch="$(git symbolic-ref --short HEAD 2>/dev/null || echo main)"
echo "${CYAN}Fast-forwarding $default_branch...${RESET}"
git pull --ff-only origin "$default_branch"

new_sha="$(git rev-parse HEAD)"
echo "${BOLD}New agent-skills SHA:${RESET} $new_sha"

cd "$REPO_ROOT"

if [ "$old_sha" = "$new_sha" ]; then
    echo "${GREEN}Already at the latest upstream commit. Nothing to do.${RESET}"
    exit 0
fi

if [ "$DRY_RUN" -eq 1 ]; then
    echo "${YELLOW}--dry-run: would stage external/agent-skills and commit.${RESET}"
    echo
    echo "Diff in parent repo:"
    git diff external/agent-skills
    exit 0
fi

git add external/agent-skills
git commit -m "Update agent-skills submodule

From ${old_sha:0:12} to ${new_sha:0:12}"

echo
echo "${GREEN}✓ Submodule updated and committed.${RESET}"
echo "${CYAN}Push when ready: ${BOLD}git push origin main${RESET}"
