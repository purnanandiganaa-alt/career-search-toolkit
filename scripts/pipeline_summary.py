#!/usr/bin/env python3
"""
pipeline_summary.py -- prints the application tracker as a clean table,
plus counts by status. A lightweight equivalent of career-ops's Go TUI
dashboard, sized for a pipeline of tens (not thousands) of applications.

Usage:
    python3 scripts/pipeline_summary.py
"""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = ROOT / "Applications" / "application_index.csv"


def main() -> None:
    if not INDEX_FILE.exists():
        print(f"No index file at {INDEX_FILE}")
        return

    with INDEX_FILE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No applications tracked yet.")
        return

    col_widths = {
        "date": max(len("Date"), max(len(r["date"]) for r in rows)),
        "company": max(len("Company"), max(len(r["company"]) for r in rows)),
        "position": max(
            len("Position"), max(len(r["position"][:40]) for r in rows)
        ),
        "status": max(len("Status"), max(len(r["status"]) for r in rows)),
    }

    header = (
        f"{'Date':<{col_widths['date']}}  "
        f"{'Company':<{col_widths['company']}}  "
        f"{'Position':<{col_widths['position']}}  "
        f"{'Status':<{col_widths['status']}}"
    )
    print(header)
    print("-" * len(header))

    for r in rows:
        position = r["position"][:40]
        print(
            f"{r['date']:<{col_widths['date']}}  "
            f"{r['company']:<{col_widths['company']}}  "
            f"{position:<{col_widths['position']}}  "
            f"{r['status']:<{col_widths['status']}}"
        )

    print()
    counts = Counter(r["status"] for r in rows)
    summary = " · ".join(f"{status}: {count}" for status, count in counts.most_common())
    print(f"Total: {len(rows)}  |  {summary}")


if __name__ == "__main__":
    main()
