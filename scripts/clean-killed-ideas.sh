#!/usr/bin/env bash
# clean-killed-ideas.sh — archive killed-idea cards older than N days into
# a timestamped tarball under ideas/killed/, then remove the originals.
# Keeps ideas/killed/ navigable as it accumulates over time.
#
# Killed-but-recent cards are preserved as-is (their kill rationale may
# still be relevant context for new ideas). Old killed cards are archived
# but not deleted — the tarball stays alongside.
#
# Usage: bash scripts/clean-killed-ideas.sh [--days N] [--dry-run]
#
# Defaults: --days 90

set -euo pipefail

DAYS=90
DRY_RUN=0

while [ $# -gt 0 ]; do
    case "$1" in
        --days)    DAYS="$2"; shift 2 ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help)
            echo "Usage: bash scripts/clean-killed-ideas.sh [--days N] [--dry-run]"
            echo
            echo "  --days N    archive files older than N days (default: 90)"
            echo "  --dry-run   show what would be archived without acting"
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [ -t 1 ]; then
    GREEN=$'\e[32m'; YELLOW=$'\e[33m'; CYAN=$'\e[36m'
    BOLD=$'\e[1m';   RESET=$'\e[0m'
else
    GREEN=""; YELLOW=""; CYAN=""; BOLD=""; RESET=""
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KILLED_DIR="$REPO_ROOT/ideas/killed"

if [ ! -d "$KILLED_DIR" ]; then
    echo "${YELLOW}No ideas/killed/ directory. Nothing to do.${RESET}"
    exit 0
fi

cd "$KILLED_DIR"

# Find .md files older than N days (mtime-based)
old_files="$(find . -maxdepth 1 -name "*.md" -mtime "+${DAYS}" | sort || true)"

if [ -z "$old_files" ]; then
    echo "${GREEN}No killed ideas older than ${DAYS} days. Nothing to archive.${RESET}"
    exit 0
fi

count=$(echo "$old_files" | wc -l | xargs)
echo "${CYAN}Found ${BOLD}${count}${RESET}${CYAN} killed ideas older than ${DAYS} days:${RESET}"
echo "$old_files" | sed 's|^\./|  |'
echo

if [ "$DRY_RUN" -eq 1 ]; then
    echo "${YELLOW}--dry-run: nothing moved.${RESET}"
    exit 0
fi

archive_name="killed-archive-$(date +%Y%m%d).tar.gz"
echo "${CYAN}Creating ${archive_name}...${RESET}"

# Use tar with files-from for safety with weird filenames
echo "$old_files" | tar -czf "$archive_name" --files-from -

echo "${CYAN}Removing originals...${RESET}"
echo "$old_files" | xargs rm

echo
echo "${GREEN}✓ Archived ${count} files to ideas/killed/${archive_name}${RESET}"
echo "${BOLD}Restore (if ever needed):${RESET} cd ideas/killed && tar -xzf ${archive_name}"
