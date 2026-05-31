#!/usr/bin/env python3
"""
gen_run_id.py — generate a pipeline run-id.

A run-id uniquely names the folder a single command invocation
(`/scan`, `/discover`, `/validate-card`, `/scope-mvp`, `/trend-check`)
writes its outputs into. Every run gets a unique folder so that
artifacts from different runs never mix.

Format: <8-lowercase-alphanumeric>-<MMDDYY>
Example: csi48s2t-053026

The 8-char alphanumeric is cryptographically random (Python `secrets`),
chosen from a-z + 0-9 = 36^8 ≈ 2.8 trillion combinations — collisions
are astronomically unlikely.

Usage from shell:
  python3 scripts/gen_run_id.py                # prints one run-id
  python3 scripts/gen_run_id.py --count 3      # prints 3 (rare)
  python3 scripts/gen_run_id.py --json         # JSON array output

Importable from other Python scripts:
  from gen_run_id import generate_run_id
  run_id = generate_run_id()  # returns "csi48s2t-053026"

The slash commands call this via Bash:
  RUN_ID=$(python3 scripts/gen_run_id.py)
  mkdir -p market-research/$RUN_ID
"""

import argparse
import json
import secrets
import string
import sys
from datetime import date


ALPHABET = string.ascii_lowercase + string.digits  # 36 chars


def generate_run_id(today: date | None = None) -> str:
    """Return a fresh run-id: 8 lowercase alphanumeric + '-' + MMDDYY."""
    rand = "".join(secrets.choice(ALPHABET) for _ in range(8))
    d = today or date.today()
    return f"{rand}-{d.strftime('%m%d%y')}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a pipeline run-id (8-alphanumeric + MMDDYY)."
    )
    parser.add_argument(
        "--count", type=int, default=1,
        help="Number of run-ids to generate (default: 1).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as a JSON array instead of one per line.",
    )
    args = parser.parse_args()

    if args.count < 1:
        print("--count must be at least 1", file=sys.stderr)
        return 1

    ids = [generate_run_id() for _ in range(args.count)]
    if args.json:
        print(json.dumps(ids))
    else:
        for run_id in ids:
            print(run_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
