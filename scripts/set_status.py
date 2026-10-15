#!/usr/bin/env python3
"""
set_status.py -- the only supported way to update a row's status in
application_index.csv. Prevents hand-editing mistakes (typo'd status,
wrong row, broken CSV quoting).

Usage:
    python3 scripts/set_status.py "Acme Corp" Applied
    python3 scripts/set_status.py "Acme Corp" Interview --note "Phone screen scheduled for next week"
"""

import csv
import sys
from pathlib import Path

from states import CANONICAL_STATES

ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT / "Applications" / "application_index.csv"


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)

    company_query = args[0].lower()
    new_status = args[1]
    note = None
    if "--note" in args:
        note = args[args.index("--note") + 1]

    if new_status not in CANONICAL_STATES:
        print(f"'{new_status}' is not a canonical state. Use one of:")
        for s in CANONICAL_STATES:
            print(f"  - {s}")
        sys.exit(1)

    if not INDEX_FILE.exists():
        print(f"No index file at {INDEX_FILE}")
        sys.exit(1)

    with INDEX_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []

    matches = [r for r in rows if company_query in r["company"].lower()]

    if not matches:
        print(f"No row found matching company '{args[0]}'.")
        print("Companies in the tracker:")
        for r in rows:
            print(f"  - {r['company']} ({r['status']})")
        sys.exit(1)

    if len(matches) > 1:
        print(f"Ambiguous: '{args[0]}' matches multiple rows:")
        for r in matches:
            print(f"  - {r['company']} — {r['position']} (currently {r['status']})")
        print("Be more specific.")
        sys.exit(1)

    row = matches[0]
    old_status = row["status"]

    if new_status == "Applied" and old_status != "Applied":
        confirm = input(
            f"Confirm: mark {row['company']} as 'Applied'? This should only happen "
            f"AFTER you have actually clicked submit. (y/N) "
        )
        if confirm.strip().lower() != "y":
            print("Cancelled.")
            sys.exit(0)

    row["status"] = new_status

    with INDEX_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{row['company']}: {old_status} -> {new_status}")

    if note:
        notes_path = ROOT / row["notes_path"]
        if notes_path.exists():
            with notes_path.open("a", encoding="utf-8") as f:
                f.write(f"\n## Status update — {new_status}\n{note}\n")
            print(f"Note appended to {notes_path.relative_to(ROOT)}")
        else:
            print(f"Warning: notes file {notes_path} not found, note not saved.")


if __name__ == "__main__":
    main()
