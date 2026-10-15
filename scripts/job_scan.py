#!/usr/bin/env python3
"""
job_scan.py -- zero-token job scanner.

Hits public, unauthenticated ATS APIs (Greenhouse, Ashby) for a curated list
of companies in scripts/companies.json, filters by relevant job titles, and
appends anything new to job_search_log.md so repeat runs don't re-report the
same posting.

This is the "zero-token" half of career-ops's scan.mjs: no LLM calls, no
browser. A posting still open at scan time is not guaranteed open when you
read this later -- verify before spending real evaluation time on it.

Requires: pip install certifi

Usage:
    python3 scripts/job_scan.py            # scan + print + log new matches
    python3 scripts/job_scan.py --dry-run  # scan + print, don't write the log
"""

import json
import re
import ssl
import sys
import urllib.request
from datetime import date
from pathlib import Path

import certifi

ROOT = Path(__file__).resolve().parent.parent
COMPANIES_FILE = ROOT / "scripts" / "companies.json"
LOG_FILE = ROOT / "job_search_log.md"

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "job-scan/1.0"})
    with urllib.request.urlopen(req, timeout=15, context=SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_greenhouse(company: str, slug: str) -> list[dict]:
    data = fetch_json(f"https://api.greenhouse.io/v1/boards/{slug}/jobs")
    out = []
    for job in data.get("jobs", []):
        out.append(
            {
                "company": company,
                "title": job.get("title", ""),
                "location": (job.get("location") or {}).get("name", "Unknown"),
                "url": job.get("absolute_url", ""),
            }
        )
    return out


def fetch_ashby(company: str, slug: str) -> list[dict]:
    data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
    out = []
    for job in data.get("jobs", []):
        out.append(
            {
                "company": company,
                "title": job.get("title", ""),
                "location": job.get("location", "Unknown"),
                "url": job.get("jobUrl") or job.get("applyUrl", ""),
            }
        )
    return out


FETCHERS = {"greenhouse": fetch_greenhouse, "ashby": fetch_ashby}


def title_matches(title: str, positive: list[str], negative: list[str]) -> bool:
    t = title.lower()
    if any(neg in t for neg in negative):
        return False
    return any(pos in t for pos in positive)


def location_matches(location: str, include: list[str]) -> bool:
    loc = location.lower()
    return any(inc in loc for inc in include)


def load_seen_urls() -> set[str]:
    if not LOG_FILE.exists():
        return set()
    text = LOG_FILE.read_text(encoding="utf-8")
    return set(re.findall(r"https?://\S+", text))


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    config = json.loads(COMPANIES_FILE.read_text(encoding="utf-8"))
    companies = config["companies"]
    positive = [p.lower() for p in config["title_filter"]["domain"]]
    negative = [n.lower() for n in config["title_filter"]["negative"]]
    loc_include = [i.lower() for i in config["location_filter"]["include"]]

    seen = load_seen_urls()
    today = date.today().isoformat()

    new_entries = []
    errors = []

    for c in companies:
        fetcher = FETCHERS.get(c["provider"])
        if fetcher is None:
            errors.append(f"{c['name']}: unknown provider {c['provider']!r}")
            continue
        try:
            jobs = fetcher(c["name"], c["slug"])
        except Exception as exc:  # noqa: BLE001 -- report and keep scanning
            errors.append(f"{c['name']}: {exc}")
            continue

        for job in jobs:
            if not title_matches(job["title"], positive, negative):
                continue
            if not location_matches(job["location"], loc_include):
                continue
            if job["url"] in seen:
                continue
            new_entries.append(job)
            seen.add(job["url"])

    print(f"Scanned {len(companies)} companies, {len(new_entries)} new matching postings.")
    if errors:
        print("\nErrors (company skipped, others still scanned):")
        for e in errors:
            print(f"  - {e}")

    if not new_entries:
        return

    print("\nNew postings:")
    lines = []
    for job in new_entries:
        line = f"- [{today}] {job['company']} — {job['title']} — {job['location']} — {job['url']}"
        print(f"  {line}")
        lines.append(line)

    if dry_run:
        print("\n(--dry-run: not written to job_search_log.md)")
        return

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(lines) + "\n")
    print(f"\nAppended {len(new_entries)} entries to {LOG_FILE.name}")


if __name__ == "__main__":
    main()
