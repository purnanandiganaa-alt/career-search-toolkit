---
name: job-scan
description: Run the zero-token job scanner against a curated list of companies with public ATS APIs, filtered to the candidate's target roles and locations. Use when the user asks to scan for new jobs, check for new postings, or search for openings.
metadata:
  trigger: User asks to scan/search for new jobs, check for new postings, or run the job scanner
  author: adapted from santifer/career-ops's scan.mjs (MIT), reimplemented in Python and scoped for a one-person job search
---

# Job Scan

Zero-token discovery: direct calls to public, unauthenticated ATS APIs (Greenhouse, Ashby) —
no LLM cost for the scan itself, only for reviewing results afterward.

## Steps

1. Run `python3 scripts/job_scan.py` from the project root. This:
   - Hits every company in `scripts/companies.json` via its ATS API
   - Filters to postings matching the domain keywords AND location terms configured in
     `companies.json` (see `title_filter` / `location_filter`), excluding senior/staff/
     principal-level titles
   - Dedupes against everything already in `job_search_log.md`
   - Appends new matches to `job_search_log.md`

2. Present the new matches to the user. For each one, offer to run `job-fit-eval` on it
   directly rather than making the user paste the JD back in — fetch the JD from the posting
   URL if needed.

3. If a company returns an error (API down, slug changed), report it but keep going — don't
   let one company block the rest of the scan.

## Setting up your own company list

`scripts/companies.example.json` in the career-search-toolkit repo is a starting template — copy it to
`scripts/companies.json` and edit the `companies`, `title_filter`, and `location_filter`
sections to match the candidate's actual target roles and locations. Verify the slug
actually resolves **before** adding a company — don't guess:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "https://api.greenhouse.io/v1/boards/{slug}/jobs"
curl -sS -o /dev/null -w "%{http_code}\n" "https://api.ashbyhq.com/posting-api/job-board/{slug}"
```

A `200` confirms the slug is real. Common slug guesses (company name, lowercase, hyphenated)
often 404 — try the company's actual careers-page URL for hints, or check their job board link
directly for the slug in the URL.

## Known limitation — and the honest next step

This scanner only proves a posting **existed** in the ATS at ATS-response time — not that it's
still open when a human reads the digest later, and not that the ATS itself is current (some
companies leave stale postings live after a role closes). career-ops solves the second half of
this with an optional Playwright-based `--verify` pass: after the zero-token discovery, it
launches a real browser against each new posting and drops any that show closed/expired
signals, before the posting ever reaches the user.

This scanner does not have that yet — it was deliberately left out to keep the first version
simple. If false positives (dead postings in the digest) become a real annoyance, the
documented next step is to add a `--verify` flag to `job_scan.py` that uses Playwright
(navigate + a snapshot check for "closed"/"no longer accepting applications"/missing JD body)
on each new match before it's written to `job_search_log.md`.

## Scheduling

Not run on a schedule by default. If the user wants this running automatically, use Claude
Code's `/schedule` feature to run this skill on a recurring cadence — confirm the interval
with the user first rather than assuming daily is right.

## Never

- Never present a scan result as "definitely open" — it's "was returned by the API just now."
- Never add a company to `companies.json` without verifying the slug resolves first.
