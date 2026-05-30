#!/usr/bin/env bash
# backup-personal-data.sh — tar up the gitignored personal-data folders
# (ideas/, market-research/, web-apps/, mobile-apps/, generated/) into a
# timestamped archive. Optional encryption with openssl AES-256-CBC.
#
# Why this exists: your personal data never enters git, so a backup strategy
# matters. This script makes "back up all my product work" a single command.
#
# Usage: bash scripts/backup-personal-data.sh [--encrypt] [--output DIR]

set -euo pipefail

ENCRYPT=0
OUTPUT_DIR="${HOME}/discovery-to-ship-backups"

while [ $# -gt 0 ]; do
    case "$1" in
        --encrypt) ENCRYPT=1; shift ;;
        --output)  OUTPUT_DIR="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: bash scripts/backup-personal-data.sh [--encrypt] [--output DIR]"
            echo
            echo "  --encrypt        encrypt the tarball with openssl AES-256-CBC"
            echo "                   (prompts for passphrase; required to restore)"
            echo "  --output DIR     where to write the archive"
            echo "                   (default: ~/discovery-to-ship-backups)"
            exit 0
            ;;
        *) echo "Unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [ -t 1 ]; then
    GREEN=$'\e[32m'; YELLOW=$'\e[33m'; CYAN=$'\e[36m'; BOLD=$'\e[1m'; RESET=$'\e[0m'
else
    GREEN=""; YELLOW=""; CYAN=""; BOLD=""; RESET=""
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p "$OUTPUT_DIR"

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
TARBALL_NAME="discovery-to-ship-personal-${TIMESTAMP}.tar.gz"
TARBALL_PATH="${OUTPUT_DIR}/${TARBALL_NAME}"

FOLDERS_TO_BACKUP=(ideas market-research web-apps mobile-apps generated)

# Filter to only folders with real content (more than just README.md + .gitkeep)
existing=()
for d in "${FOLDERS_TO_BACKUP[@]}"; do
    if [ -d "$d" ]; then
        substantive_count=$(find "$d" -mindepth 1 \
                                ! -name '.gitkeep' ! -name 'README.md' \
                                2>/dev/null | head -1 | wc -l)
        if [ "$substantive_count" -gt 0 ]; then
            existing+=("$d")
        fi
    fi
done

if [ ${#existing[@]} -eq 0 ]; then
    echo "${YELLOW}No personal data to back up. All folders empty or contain only placeholders.${RESET}"
    exit 0
fi

echo "${BOLD}Backing up:${RESET} ${existing[*]}"
echo "${BOLD}To:${RESET}         ${TARBALL_PATH}"

# Use tar excludes to skip README.md + .gitkeep (those are already in git)
tar_args=(--exclude='README.md' --exclude='.gitkeep' -czf "$TARBALL_PATH")
for d in "${existing[@]}"; do
    tar_args+=("$d")
done
tar "${tar_args[@]}"

size="$(du -h "$TARBALL_PATH" | cut -f1)"
echo "${GREEN}✓ Archive written ($size).${RESET}"

if [ "$ENCRYPT" -eq 1 ]; then
    if ! command -v openssl >/dev/null 2>&1; then
        echo "${YELLOW}openssl not found; cannot encrypt. Leaving plain tarball.${RESET}"
        exit 0
    fi
    echo "${CYAN}Encrypting with openssl AES-256-CBC (you'll be prompted for a passphrase)...${RESET}"
    openssl enc -aes-256-cbc -salt -pbkdf2 \
        -in "$TARBALL_PATH" -out "${TARBALL_PATH}.enc"
    rm "$TARBALL_PATH"
    echo "${GREEN}✓ Encrypted archive: ${TARBALL_PATH}.enc${RESET}"
    echo "${YELLOW}Remember your passphrase — required to restore.${RESET}"
    echo "${BOLD}To restore:${RESET} openssl enc -d -aes-256-cbc -pbkdf2 -in <archive>.enc | tar -xzf -"
else
    echo "${YELLOW}NOTE: archive is unencrypted.${RESET} Re-run with --encrypt if it contains sensitive data."
    echo "${BOLD}To restore:${RESET} tar -xzf $TARBALL_PATH"
fi
