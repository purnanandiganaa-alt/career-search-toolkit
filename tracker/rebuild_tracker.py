#!/usr/bin/env python3
"""
rebuild_tracker.py -- regenerates a static, self-contained HTML snapshot of
Applications/application_index.csv. Dark/light aware, badge per status,
follow-up heatmap, streak, filter/sort, "mark applied/rejected" buttons
(browser-local only -- never writes back to the CSV).

Never hand-edit the generated HTML directly -- run this script instead,
every time application_index.csv changes.

Edit the constants below to match your own setup before first use.

Usage:
    python3 tracker/rebuild_tracker.py
"""
import csv
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

# ---- Edit these for your own setup ----
CANDIDATE_NAME = "Your Name"
ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "Applications" / "application_index.csv"
OUT_PATH = ROOT / "Job Applications Tracker.html"  # e.g. point this at ~/Desktop if you want it there
PROJECT_ROOT = str(ROOT) + "/"
# ----------------------------------------

BADGE_COLORS = {
    "Applied": "#2f9e44",
    "Drafted": "#b45309",
    "Rejected": "#e5484d",
    "SKIP": "#6b6975",
    "Skipped": "#6b6975",
}

NEXT_ACTION = {
    "Drafted": ("Applied", "Mark Applied"),
    "Applied": ("Rejected", "Mark Rejected"),
}


def file_url(rel_path: str) -> str:
    abs_path = PROJECT_ROOT + rel_path
    return "file://" + quote(abs_path, safe="/")


def make_row(row: dict) -> str:
    row_date = row["date"]
    company = row["company"]
    position = row["position"]
    location = row["location"]
    status = row["status"]
    display_status = "Skipped" if status == "SKIP" else status
    color = BADGE_COLORS.get(status, "#6b6975")

    key = escape(f"{row_date}|{company}|{position}", quote=True)
    search_blob = escape(f"{company} {position} {location}".lower(), quote=True)

    badge_html = (
        f'<span class="badge status-badge" data-status="{display_status}" '
        f'style="background:{color}">{display_status}</span>'
    )
    action = NEXT_ACTION.get(display_status)
    if action:
        next_status, label = action
        badge_html += (
            f' <button class="tracker-btn" '
            f'onclick="markStatus(this, \'{next_status}\')">{label}</button>'
        )

    links = []
    if row.get("resume_path"):
        links.append(f'<a href="{file_url(row["resume_path"])}">Resume</a>')
    if row.get("cover_letter_path"):
        links.append(f'<a href="{file_url(row["cover_letter_path"])}">Cover Letter</a>')
    if row.get("notes_path"):
        links.append(f'<a href="{file_url(row["notes_path"])}">Notes</a>')
    posting = row.get("posting_link", "")
    if posting:
        if posting.startswith("mailto:"):
            links.append(f'<a href="{escape(posting, quote=True)}">Email</a>')
        else:
            links.append(f'<a href="{escape(posting, quote=True)}" target="_blank">Posting</a>')
    links_html = " &middot; ".join(links)

    return f"""    <tr data-key="{key}" data-date="{escape(row_date)}" data-company="{escape(company)}" data-csv-status="{display_status}" data-search="{search_blob}">
      <td class="nowrap"><span class="date-abs">{escape(row_date)}</span> <span class="date-rel" data-date="{escape(row_date)}"></span></td>
      <td><strong>{escape(company)}</strong></td>
      <td>{escape(position)}</td>
      <td>{escape(location)}</td>
      <td>{badge_html}</td>
      <td class="links">{links_html}</td>
    </tr>"""


def main() -> None:
    if not CSV_PATH.exists():
        print(f"No CSV found at {CSV_PATH}. Create it first (see tracker/sample_application_index.csv for the expected columns).")
        return

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    counts = Counter(("Skipped" if r["status"] == "SKIP" else r["status"]) for r in rows)
    total = len(rows)
    applied = counts.get("Applied", 0)
    drafted = counts.get("Drafted", 0)
    skipped = counts.get("Skipped", 0)
    rejected = counts.get("Rejected", 0)

    rows_html = "\n".join(make_row(r) for r in rows)
    generated_on = date.today().isoformat()

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Job Applications Tracker</title>
<style>
  :root {{
    --ink: #14131c;
    --accent: #6d5ef8;
    --accent-fg: #ffffff;
    --nudge: #f2b705;
    --go: #2f9e44;
    --wait: #b45309;
    --stop: #e5484d;

    --bg: #f5f4f8;
    --fg: #201f28;
    --muted: #6b6975;
    --border: #ddd9e8;
    --row-hover: #eeecf5;
    --header-bg: #efedf7;
    --link: #5b46e0;
    --card-bg: #ffffff;

    --seq-1: #cbcef2;
    --seq-2: #8b8de6;
    --seq-3: #6d68db;
    --seq-4: #302878;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #14131c;
      --fg: #ece9f5;
      --muted: #9a97ab;
      --border: #2b2938;
      --row-hover: #1d1b28;
      --header-bg: #1a1826;
      --link: #8f7dff;
      --card-bg: #191722;

      --seq-1: #2d2d55;
      --seq-2: #5f60a6;
      --seq-3: #7a7bd2;
      --seq-4: #cacdf8;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #14131c; --fg: #ece9f5; --muted: #9a97ab; --border: #2b2938;
    --row-hover: #1d1b28; --header-bg: #1a1826; --link: #8f7dff; --card-bg: #191722;
    --seq-1: #2d2d55; --seq-2: #5f60a6; --seq-3: #7a7bd2; --seq-4: #cacdf8;
  }}
  :root[data-theme="light"] {{
    --bg: #f5f4f8; --fg: #201f28; --muted: #6b6975; --border: #ddd9e8;
    --row-hover: #eeecf5; --header-bg: #efedf7; --link: #5b46e0; --card-bg: #ffffff;
    --seq-1: #cbcef2; --seq-2: #8b8de6; --seq-3: #6d68db; --seq-4: #302878;
  }}

  * {{ box-sizing: border-box; }}
  html {{ background: var(--ink); }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  .num {{ font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-variant-numeric: tabular-nums; }}

  /* ---------- Hero: mission control band, always dark ---------- */
  .hero {{
    background:
      radial-gradient(60rem 20rem at 15% -20%, rgba(109,94,248,0.35), transparent 60%),
      var(--ink);
    color: #f2f1fb;
    padding: 2rem 1.5rem 1.75rem;
  }}
  .hero-inner {{
    max-width: 1100px; margin: 0 auto;
    display: grid; grid-template-columns: auto 1fr auto; gap: 2rem; align-items: center;
  }}
  .streak {{ display: flex; align-items: center; gap: 0.75rem; }}
  .flame {{ width: 2.25rem; height: 2.25rem; flex-shrink: 0; }}
  .flame path {{ fill: var(--accent); }}
  @media (prefers-reduced-motion: no-preference) {{
    .streak.active .flame {{ animation: flicker 2.4s ease-in-out infinite; }}
  }}
  @keyframes flicker {{
    0%, 100% {{ transform: scale(1); opacity: 1; }}
    50% {{ transform: scale(1.08) translateY(-1px); opacity: 0.92; }}
  }}
  .streak-num {{ font-size: 2.1rem; font-weight: 700; font-family: ui-rounded, "SF Pro Rounded", -apple-system, sans-serif; line-height: 1; }}
  .streak-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #c9c6e6; margin-top: 0.15rem; }}

  .trail {{ display: flex; gap: 0.28rem; flex-wrap: wrap; align-content: center; justify-content: center; }}
  .trail-dot {{
    width: 0.55rem; height: 0.55rem; border-radius: 50%;
    background: rgba(255,255,255,0.14);
  }}
  .trail-dot.filled {{ background: var(--accent); box-shadow: 0 0 6px rgba(109,94,248,0.7); }}

  .followup {{ min-width: 13rem; text-align: right; }}
  .followup-count {{ font-size: 1.7rem; font-weight: 700; line-height: 1; font-family: ui-rounded, "SF Pro Rounded", -apple-system, sans-serif; }}
  .followup-count.zero {{ color: #a7f3c5; }}
  .followup-count.some {{ color: var(--nudge); }}
  .followup-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #c9c6e6; margin-top: 0.1rem; }}
  .followup-detail {{ font-size: 0.76rem; color: #d8d6ec; margin-top: 0.3rem; }}
  @media (max-width: 720px) {{ .followup {{ text-align: center; }} }}

  @media (max-width: 720px) {{
    .hero-inner {{ grid-template-columns: 1fr; gap: 1rem; text-align: center; }}
    .trail {{ justify-content: center; }}
    .streak {{ justify-content: center; }}
  }}

  /* ---------- Main content ---------- */
  .wrap {{ max-width: 1100px; margin: 0 auto; padding: 1.75rem 1.5rem 3rem; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 0.2rem; }}
  .subtitle {{ color: var(--muted); font-size: 0.88rem; margin-bottom: 1.4rem; }}

  .summary {{ display: flex; gap: 0.7rem; flex-wrap: wrap; margin-bottom: 1.1rem; }}
  .stat {{
    border: 1px solid var(--border); background: var(--card-bg); border-radius: 10px;
    padding: 0.6rem 1rem; font-size: 0.82rem; color: var(--muted); min-width: 5.5rem;
  }}
  .stat strong {{ color: var(--fg); font-size: 1.15rem; display: block; }}

  .controls {{
    display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center;
    margin-bottom: 1rem;
  }}
  .chips {{ display: flex; gap: 0.4rem; flex-wrap: wrap; }}
  .chip {{
    border: 1px solid var(--border); background: var(--card-bg); color: var(--muted);
    border-radius: 999px; padding: 0.32rem 0.85rem; font-size: 0.8rem; font-weight: 600;
    cursor: pointer;
  }}
  .chip:hover {{ border-color: var(--accent); color: var(--fg); }}
  .chip.active {{ background: var(--accent); border-color: var(--accent); color: var(--accent-fg); }}
  #search-box {{
    flex: 1; min-width: 12rem; border: 1px solid var(--border); background: var(--card-bg);
    color: var(--fg); border-radius: 8px; padding: 0.4rem 0.75rem; font-size: 0.85rem;
  }}
  #search-box:focus {{ outline: 2px solid var(--accent); outline-offset: 1px; }}

  /* ---------- Application Activity heatmap ---------- */
  .activity-card {{
    border: 1px solid var(--border); background: var(--card-bg); border-radius: 10px;
    padding: 1rem 1.1rem; margin-bottom: 1.1rem;
  }}
  .activity-head {{
    display: flex; justify-content: space-between; align-items: baseline; gap: 1rem;
    flex-wrap: wrap; margin-bottom: 0.7rem;
  }}
  .activity-head h2 {{ font-size: 0.92rem; margin: 0; font-weight: 600; }}
  .heat-range {{ font-size: 0.76rem; color: var(--muted); }}
  .heat-legend {{ display: flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; color: var(--muted); }}
  .heat-swatch {{ width: 0.7rem; height: 0.7rem; border-radius: 2px; border: 1px solid var(--border); display: inline-block; }}
  .heat-swatch[data-level="1"] {{ background: var(--seq-1); border-color: var(--seq-1); }}
  .heat-swatch[data-level="2"] {{ background: var(--seq-2); border-color: var(--seq-2); }}
  .heat-swatch[data-level="3"] {{ background: var(--seq-3); border-color: var(--seq-3); }}
  .heat-swatch[data-level="4"] {{ background: var(--seq-4); border-color: var(--seq-4); }}
  .heatmap-scroll {{ overflow-x: auto; padding-bottom: 0.15rem; }}
  .heatmap-grid {{ display: flex; gap: 3px; width: max-content; }}
  .heat-week {{ display: flex; flex-direction: column; gap: 3px; }}
  .heat-cell {{
    width: 12px; height: 12px; border-radius: 3px; border: 1px solid var(--border);
    background: transparent; cursor: default;
  }}
  .heat-cell[data-level="1"] {{ background: var(--seq-1); border-color: var(--seq-1); }}
  .heat-cell[data-level="2"] {{ background: var(--seq-2); border-color: var(--seq-2); }}
  .heat-cell[data-level="3"] {{ background: var(--seq-3); border-color: var(--seq-3); }}
  .heat-cell[data-level="4"] {{ background: var(--seq-4); border-color: var(--seq-4); }}
  .heat-cell:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .heat-cell[hidden] {{ visibility: hidden; }}
  .heat-tooltip {{
    position: fixed; z-index: 70; background: var(--ink); color: #f2f1fb; border-radius: 8px;
    padding: 0.4rem 0.6rem; font-size: 0.78rem; box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    pointer-events: none; max-width: 14rem;
  }}
  .heat-tooltip strong {{ font-family: ui-monospace, "SF Mono", Menlo, monospace; }}

  .table-scroll {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 10px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  thead th {{
    position: sticky; top: 0; z-index: 2;
    text-align: left; background: var(--header-bg); padding: 0.6rem 0.75rem;
    border-bottom: 1px solid var(--border); font-weight: 600; white-space: nowrap;
  }}
  th.sortable {{ cursor: pointer; user-select: none; }}
  th.sortable:hover {{ color: var(--accent); }}
  th.sortable .arrow {{ font-size: 0.7em; color: var(--muted); margin-left: 0.2rem; }}
  tbody td {{ padding: 0.6rem 0.75rem; border-bottom: 1px solid var(--border); vertical-align: top; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--row-hover); }}
  tbody tr.stale {{ box-shadow: inset 3px 0 0 var(--nudge); }}
  .nowrap {{ white-space: nowrap; color: var(--muted); }}
  .date-rel {{ font-size: 0.75rem; opacity: 0.75; }}
  .badge {{
    color: white; padding: 0.15rem 0.6rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 600; white-space: nowrap;
  }}
  .links a {{ color: var(--link); text-decoration: none; font-size: 0.85rem; }}
  .links a:hover {{ text-decoration: underline; }}
  .tracker-btn {{
    margin-left: 0.4rem; padding: 0.1rem 0.5rem; font-size: 0.7rem; font-weight: 600;
    border: 1px solid var(--border); border-radius: 999px; background: var(--card-bg);
    color: var(--muted); cursor: pointer;
  }}
  .tracker-btn:hover {{ background: var(--row-hover); color: var(--fg); border-color: var(--accent); }}
  .tracker-btn:focus-visible, .chip:focus-visible, th.sortable:focus-visible {{
    outline: 2px solid var(--accent); outline-offset: 2px;
  }}

  .footer {{ margin-top: 1.4rem; color: var(--muted); font-size: 0.8rem; }}
  .footer .sync-note {{ margin-top: 0.4rem; }}
  .footer .drift-note {{ margin-top: 0.3rem; color: var(--wait); }}

  /* ---------- Toasts ---------- */
  #toast-stack {{
    position: fixed; bottom: 1.25rem; left: 50%; transform: translateX(-50%);
    display: flex; flex-direction: column; gap: 0.5rem; z-index: 50; align-items: center;
  }}
  .toast {{
    background: var(--ink); color: #f2f1fb; border: 1px solid rgba(255,255,255,0.12);
    padding: 0.55rem 1rem; border-radius: 10px; font-size: 0.85rem;
    display: flex; align-items: center; gap: 0.75rem; box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  }}
  .toast.milestone {{ background: linear-gradient(120deg, var(--accent), #9c8cff); border-color: transparent; font-weight: 600; }}
  .toast button {{
    background: none; border: none; color: var(--accent); font-weight: 700; cursor: pointer;
    font-size: 0.85rem; padding: 0;
  }}
  .toast.milestone button {{ color: #fff; text-decoration: underline; }}

  #confetti-canvas {{ position: fixed; inset: 0; pointer-events: none; z-index: 60; }}

  @media (max-width: 700px) {{
    .table-scroll table, .table-scroll thead, .table-scroll tbody,
    .table-scroll tr, .table-scroll th, .table-scroll td {{ display: block; }}
    thead {{ display: none; }}
    tbody tr {{ border: 1px solid var(--border); border-radius: 8px; margin: 0.6rem; padding: 0.5rem; }}
    tbody td {{ border: none; padding: 0.3rem 0.25rem; }}
    tbody td::before {{ content: attr(data-label); font-weight: 600; display: block; font-size: 0.72rem; color: var(--muted); }}
  }}
</style>
</head>
<body>

<div class="hero">
  <div class="hero-inner">
    <div class="streak" id="streak-block">
      <svg class="flame" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M12 2c.6 2.2-.4 3.6-1.7 5-1.6 1.7-3 3.3-3 5.7A4.7 4.7 0 0 0 12 17.4 4.7 4.7 0 0 0 16.7 12.7c0-1.1-.3-2-.8-2.9.9.5 1.6 1.3 2 2.3.5 1.1.6 2.3.3 3.5-.6 2.6-2.9 4.5-5.6 4.7-3.2.3-6.1-1.9-6.7-5-.4-2 .2-3.8 1.5-5.3.5 1 1.4 1.5 2.3 1.2-.4-1.5 0-2.9 1-4 .5-.6 1.1-1 1.3-1.6Z"/>
      </svg>
      <div>
        <div class="streak-num num" id="streak-num">0</div>
        <div class="streak-label" id="streak-label">day streak</div>
      </div>
    </div>
    <div class="trail" id="activity-trail" title="Last 30 days of activity"></div>
    <div class="followup">
      <div class="followup-count num" id="followup-count">0</div>
      <div class="followup-label">need a follow-up</div>
      <div class="followup-detail" id="followup-detail">&nbsp;</div>
    </div>
  </div>
</div>

<div class="wrap">
  <h1>Job Applications Tracker</h1>
  <div class="subtitle">{CANDIDATE_NAME} &middot; generated {generated_on}</div>
  <div class="summary">
    <div class="stat"><strong id="stat-total" class="num">{total}</strong>Total</div>
    <div class="stat"><strong id="stat-applied" class="num">{applied}</strong>Applied</div>
    <div class="stat"><strong id="stat-drafted" class="num">{drafted}</strong>Drafted</div>
    <div class="stat"><strong id="stat-rejected" class="num">{rejected}</strong>Rejected</div>
    <div class="stat"><strong id="stat-skipped" class="num">{skipped}</strong>Skipped</div>
  </div>

  <div class="controls">
    <div class="chips" id="filter-chips">
      <button class="chip active" data-filter="all">All</button>
      <button class="chip" data-filter="Applied">Applied</button>
      <button class="chip" data-filter="Drafted">Drafted</button>
      <button class="chip" data-filter="Rejected">Rejected</button>
      <button class="chip" data-filter="Skipped">Skipped</button>
    </div>
    <input type="search" id="search-box" placeholder="Search company, role, location&hellip;" aria-label="Search applications">
  </div>

  <div class="activity-card">
    <div class="activity-head">
      <h2>Application Activity</h2>
      <span class="heat-range" id="heat-range"></span>
      <div class="heat-legend" aria-hidden="true">
        <span>Less</span>
        <span class="heat-swatch" data-level="0"></span>
        <span class="heat-swatch" data-level="1"></span>
        <span class="heat-swatch" data-level="2"></span>
        <span class="heat-swatch" data-level="3"></span>
        <span class="heat-swatch" data-level="4"></span>
        <span>More</span>
      </div>
    </div>
    <div class="heatmap-scroll">
      <div id="heatmap-grid" class="heatmap-grid"></div>
    </div>
  </div>
  <div id="heat-tooltip" class="heat-tooltip" hidden></div>

  <div class="table-scroll">
  <table>
    <thead>
      <tr>
        <th class="sortable" data-sort="date" tabindex="0">Date<span class="arrow"></span></th>
        <th class="sortable" data-sort="company" tabindex="0">Company<span class="arrow"></span></th>
        <th>Position</th>
        <th>Location</th>
        <th class="sortable" data-sort="status" tabindex="0">Status<span class="arrow"></span></th>
        <th>Files</th>
      </tr>
    </thead>
    <tbody id="tbody">
{rows_html}
    </tbody>
  </table>
  </div>
  <div class="footer">
    Source of truth: Applications/application_index.csv. This file is a static snapshot &mdash; regenerate it after status changes.
    <div class="sync-note">"Mark Applied" / "Mark Rejected" only update this page (remembered in this browser via local storage) &mdash; they do not touch application_index.csv. Update the CSV (and re-run this script, or use scripts/set_status.py) so the two stay in sync.</div>
    <div class="drift-note" id="drift-note" hidden></div>
  </div>
</div>

<div id="toast-stack"></div>
<canvas id="confetti-canvas"></canvas>

<script>
  var BADGE_COLORS = {{ Applied: '#2f9e44', Drafted: '#b45309', Rejected: '#e5484d', Skipped: '#6b6975' }};
  var NEXT_ACTION = {{ Drafted: ['Applied', 'Mark Applied'], Applied: ['Rejected', 'Mark Rejected'] }};
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function toLocalKey(d) {{
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, '0');
    var day = String(d.getDate()).padStart(2, '0');
    return y + '-' + m + '-' + day;
  }}
  function todayKey() {{
    return toLocalKey(new Date());
  }}
  function addDays(dateStr, delta) {{
    var d = new Date(dateStr + 'T00:00:00');
    d.setDate(d.getDate() + delta);
    return toLocalKey(d);
  }}
  function daysBetween(a, b) {{
    var da = new Date(a + 'T00:00:00'), db = new Date(b + 'T00:00:00');
    return Math.round((db - da) / 86400000);
  }}

  // ---------- summary + badge helpers ----------
  function updateSummary() {{
    var badges = document.querySelectorAll('.status-badge');
    var counts = {{ Applied: 0, Drafted: 0, Skipped: 0, Rejected: 0 }};
    badges.forEach(function (b) {{
      var s = b.getAttribute('data-status');
      if (counts.hasOwnProperty(s)) counts[s]++;
    }});
    animateNumber(document.getElementById('stat-applied'), counts.Applied);
    document.getElementById('stat-drafted').textContent = counts.Drafted;
    document.getElementById('stat-rejected').textContent = counts.Rejected;
    document.getElementById('stat-skipped').textContent = counts.Skipped;
    updateFollowup();
    updateDriftNote();
    return counts;
  }}

  function updateDriftNote() {{
    var drifted = 0;
    document.querySelectorAll('tr[data-key]').forEach(function (row) {{
      var badge = row.querySelector('.status-badge');
      if (badge.getAttribute('data-status') !== row.getAttribute('data-csv-status')) drifted++;
    }});
    var note = document.getElementById('drift-note');
    if (drifted > 0) {{
      note.hidden = false;
      note.textContent = drifted + ' status change' + (drifted === 1 ? '' : 's') + ' in this browser not yet reflected in application_index.csv.';
    }} else {{
      note.hidden = true;
    }}
  }}

  function animateNumber(el, target) {{
    var start = parseInt(el.textContent, 10) || 0;
    if (reduceMotion || start === target) {{ el.textContent = target; return; }}
    var t0 = null, dur = 450;
    function step(ts) {{
      if (!t0) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      el.textContent = Math.round(start + (target - start) * p);
      if (p < 1) requestAnimationFrame(step);
    }}
    requestAnimationFrame(step);
  }}

  function setBadge(badge, status) {{
    badge.textContent = status;
    badge.setAttribute('data-status', status);
    badge.style.background = BADGE_COLORS[status] || '#6b6975';
  }}

  function applyButton(cell, status) {{
    var existing = cell.querySelector('.tracker-btn');
    if (existing) existing.remove();
    var action = NEXT_ACTION[status];
    if (!action) return;
    var btn = document.createElement('button');
    btn.className = 'tracker-btn';
    btn.textContent = action[1];
    var nextStatus = action[0];
    btn.onclick = function () {{ markStatus(btn, nextStatus); }};
    cell.appendChild(document.createTextNode(' '));
    cell.appendChild(btn);
  }}

  // ---------- status changes, undo, toasts ----------
  function markStatus(btn, status) {{
    var cell = btn.parentElement;
    var badge = cell.querySelector('.status-badge');
    var prevStatus = badge.getAttribute('data-status');
    var row = cell.closest('tr');
    var key = row.getAttribute('data-key');

    setBadge(badge, status);
    btn.remove();
    applyButton(cell, status);
    saveOverride(key, status);
    recordActivityToday();
    var counts = updateSummary();
    refreshStreakAndTrail();
    applyFilters();

    var rect = btn.getBoundingClientRect ? cell.getBoundingClientRect() : null;
    burstConfetti(rect);
    maybeCelebrateMilestone(status, counts.Applied);
    showUndoToast(row, cell, badge, prevStatus, status);
  }}

  function saveOverride(key, status) {{
    var overrides = JSON.parse(localStorage.getItem('trackerOverrides') || '{{}}');
    overrides[key] = status;
    localStorage.setItem('trackerOverrides', JSON.stringify(overrides));
  }}

  function showUndoToast(row, cell, badge, prevStatus, newStatus) {{
    var stack = document.getElementById('toast-stack');
    var toast = document.createElement('div');
    toast.className = 'toast';
    var msg = document.createElement('span');
    msg.textContent = 'Marked ' + newStatus + '.';
    var undoBtn = document.createElement('button');
    undoBtn.textContent = 'Undo';
    var timer = setTimeout(function () {{ toast.remove(); }}, 5000);
    undoBtn.onclick = function () {{
      clearTimeout(timer);
      setBadge(badge, prevStatus);
      applyButton(cell, prevStatus);
      saveOverride(row.getAttribute('data-key'), prevStatus);
      updateSummary();
      refreshStreakAndTrail();
      applyFilters();
      toast.remove();
    }};
    toast.appendChild(msg);
    toast.appendChild(undoBtn);
    stack.appendChild(toast);
  }}

  function maybeCelebrateMilestone(status, appliedCount) {{
    if (status !== 'Applied') return;
    if (appliedCount > 0 && appliedCount % 5 === 0) {{
      var stack = document.getElementById('toast-stack');
      var toast = document.createElement('div');
      toast.className = 'toast milestone';
      toast.innerHTML = '<span>\\uD83C\\uDF89 ' + appliedCount + ' applications sent</span>';
      var closeBtn = document.createElement('button');
      closeBtn.textContent = 'Nice';
      closeBtn.onclick = function () {{ toast.remove(); }};
      toast.appendChild(closeBtn);
      stack.appendChild(toast);
      setTimeout(function () {{ if (toast.parentNode) toast.remove(); }}, 4500);
    }}
  }}

  // ---------- confetti ----------
  function burstConfetti(originRect) {{
    if (reduceMotion) return;
    var canvas = document.getElementById('confetti-canvas');
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    var ctx = canvas.getContext('2d');
    var cx = originRect ? originRect.left + originRect.width / 2 : window.innerWidth / 2;
    var cy = originRect ? originRect.top : window.innerHeight / 2;
    var colors = ['#6d5ef8', '#9c8cff', '#2f9e44', '#f2b705'];
    var particles = [];
    for (var i = 0; i < 26; i++) {{
      var angle = Math.random() * Math.PI * 2;
      var speed = 2 + Math.random() * 3.5;
      particles.push({{
        x: cx, y: cy,
        vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - 2,
        size: 3 + Math.random() * 3,
        color: colors[i % colors.length],
        life: 1
      }});
    }}
    var start = null;
    function frame(ts) {{
      if (!start) start = ts;
      var elapsed = ts - start;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(function (p) {{
        p.x += p.vx; p.y += p.vy; p.vy += 0.12; p.life -= 0.018;
        ctx.globalAlpha = Math.max(p.life, 0);
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
      }});
      ctx.globalAlpha = 1;
      if (elapsed < 700) {{
        requestAnimationFrame(frame);
      }} else {{
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }}
    }}
    requestAnimationFrame(frame);
  }}

  // ---------- streak + activity trail ----------
  function recordActivityToday() {{
    var manual = JSON.parse(localStorage.getItem('trackerActivityDates') || '{{}}');
    manual[todayKey()] = true;
    localStorage.setItem('trackerActivityDates', JSON.stringify(manual));
  }}

  function collectActivityDates() {{
    var dates = {{}};
    document.querySelectorAll('tr[data-date]').forEach(function (row) {{
      dates[row.getAttribute('data-date')] = true;
    }});
    var manual = JSON.parse(localStorage.getItem('trackerActivityDates') || '{{}}');
    Object.keys(manual).forEach(function (k) {{ dates[k] = true; }});
    return dates;
  }}

  function computeStreak(dates) {{
    var streak = 0;
    var cursor = todayKey();
    if (!dates[cursor]) cursor = addDays(cursor, -1);
    while (dates[cursor]) {{
      streak++;
      cursor = addDays(cursor, -1);
    }}
    return streak;
  }}

  function buildTrail(dates) {{
    var container = document.getElementById('activity-trail');
    container.innerHTML = '';
    var today = todayKey();
    for (var i = 29; i >= 0; i--) {{
      var key = addDays(today, -i);
      var dot = document.createElement('div');
      dot.className = 'trail-dot' + (dates[key] ? ' filled' : '');
      dot.title = key + (dates[key] ? ' \\u2014 activity' : '');
      container.appendChild(dot);
    }}
  }}

  function refreshStreakAndTrail() {{
    var dates = collectActivityDates();
    var streak = computeStreak(dates);
    animateNumber(document.getElementById('streak-num'), streak);
    document.getElementById('streak-block').classList.toggle('active', streak > 0);
    buildTrail(dates);
    buildHeatmap(dates);
  }}

  // ---------- application-activity heatmap ----------
  function levelForCount(count, max) {{
    if (count <= 0) return 0;
    if (max <= 1) return 4;
    var frac = count / max;
    if (frac <= 0.25) return 1;
    if (frac <= 0.5) return 2;
    if (frac <= 0.75) return 3;
    return 4;
  }}

  function formatDateLabel(dateStr) {{
    var d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', {{ month: 'short', day: 'numeric', year: 'numeric' }});
  }}

  function showHeatTooltip(cell) {{
    var tip = document.getElementById('heat-tooltip');
    var rect = cell.getBoundingClientRect();
    tip.textContent = '';
    var label = cell.getAttribute('data-label') || '';
    var parts = label.split(' on ');
    var strong = document.createElement('strong');
    strong.textContent = parts[0];
    tip.appendChild(strong);
    if (parts[1]) tip.appendChild(document.createTextNode(' on ' + parts[1]));
    tip.hidden = false;
    var top = rect.top - 42;
    var left = rect.left + rect.width / 2;
    tip.style.top = Math.max(8, top) + 'px';
    tip.style.left = left + 'px';
    tip.style.transform = 'translateX(-50%)';
  }}
  function hideHeatTooltip() {{
    document.getElementById('heat-tooltip').hidden = true;
  }}

  function buildHeatmap(dates) {{
    var counts = {{}};
    document.querySelectorAll('tr[data-date]').forEach(function (row) {{
      var d = row.getAttribute('data-date');
      counts[d] = (counts[d] || 0) + 1;
    }});
    Object.keys(dates).forEach(function (k) {{ if (!counts[k]) counts[k] = 1; }});

    var allDates = Object.keys(counts).sort();
    var grid = document.getElementById('heatmap-grid');
    if (allDates.length === 0) {{ grid.innerHTML = ''; return; }}

    var start = allDates[0];
    var end = todayKey();
    var max = 0;
    allDates.forEach(function (k) {{ if (counts[k] > max) max = counts[k]; }});

    var startDate = new Date(start + 'T00:00:00');
    startDate.setDate(startDate.getDate() - startDate.getDay());
    var endDate = new Date(end + 'T00:00:00');

    grid.innerHTML = '';
    var cursor = new Date(startDate);
    while (cursor <= endDate) {{
      var week = document.createElement('div');
      week.className = 'heat-week';
      for (var d = 0; d < 7; d++) {{
        var key = toLocalKey(cursor);
        var cell = document.createElement('div');
        cell.className = 'heat-cell';
        if (cursor <= endDate) {{
          var count = counts[key] || 0;
          var level = levelForCount(count, max);
          if (level > 0) cell.setAttribute('data-level', String(level));
          cell.tabIndex = 0;
          cell.setAttribute('role', 'img');
          var label = (count === 0 ? 'No applications' : count + ' application' + (count === 1 ? '' : 's')) + ' on ' + formatDateLabel(key);
          cell.setAttribute('aria-label', label);
          cell.setAttribute('data-label', label);
          cell.addEventListener('pointerenter', function (e) {{ showHeatTooltip(e.currentTarget); }});
          cell.addEventListener('focus', function (e) {{ showHeatTooltip(e.currentTarget); }});
          cell.addEventListener('pointerleave', hideHeatTooltip);
          cell.addEventListener('blur', hideHeatTooltip);
        }} else {{
          cell.setAttribute('hidden', '');
        }}
        week.appendChild(cell);
        cursor.setDate(cursor.getDate() + 1);
      }}
      grid.appendChild(week);
    }}

    var rangeEl = document.getElementById('heat-range');
    if (rangeEl) {{
      rangeEl.textContent = formatDateLabel(start) + ' \\u2013 ' + formatDateLabel(end) + ' \\u00b7 ' + allDates.length + ' active day' + (allDates.length === 1 ? '' : 's');
    }}
  }}

  function updateFollowup() {{
    var today = todayKey();
    var candidates = [];
    document.querySelectorAll('tr[data-key]').forEach(function (row) {{
      var badge = row.querySelector('.status-badge');
      if (badge.getAttribute('data-status') !== 'Applied') return;
      var diff = daysBetween(row.getAttribute('data-date'), today);
      if (diff >= 14) candidates.push({{ company: row.getAttribute('data-company'), days: diff }});
    }});
    candidates.sort(function (a, b) {{ return b.days - a.days; }});

    var countEl = document.getElementById('followup-count');
    var detailEl = document.getElementById('followup-detail');
    animateNumber(countEl, candidates.length);
    countEl.classList.toggle('zero', candidates.length === 0);
    countEl.classList.toggle('some', candidates.length > 0);
    if (candidates.length === 0) {{
      detailEl.textContent = 'nothing pending 14+ days';
    }} else {{
      var oldest = candidates[0];
      detailEl.textContent = 'oldest: ' + oldest.company + ' \\u2014 ' + oldest.days + 'd';
    }}
  }}

  // ---------- relative dates + stale highlight ----------
  function refreshRelativeDates() {{
    var today = todayKey();
    document.querySelectorAll('.date-rel').forEach(function (el) {{
      var d = el.getAttribute('data-date');
      var diff = daysBetween(d, today);
      var label = diff <= 0 ? 'today' : (diff === 1 ? '1d ago' : diff + 'd ago');
      el.textContent = '(' + label + ')';
      var row = el.closest('tr');
      var status = row.querySelector('.status-badge').getAttribute('data-status');
      row.classList.toggle('stale', status === 'Applied' && diff >= 14);
    }});
  }}

  // ---------- filter + search ----------
  function applyFilters() {{
    var activeChip = document.querySelector('.chip.active');
    var activeFilter = activeChip ? activeChip.getAttribute('data-filter') : 'all';
    var query = document.getElementById('search-box').value.trim().toLowerCase();
    document.querySelectorAll('tr[data-key]').forEach(function (row) {{
      var status = row.querySelector('.status-badge').getAttribute('data-status');
      var matchesFilter = activeFilter === 'all' || status === activeFilter;
      var haystack = row.getAttribute('data-search') || '';
      var matchesSearch = !query || haystack.indexOf(query) !== -1;
      row.style.display = (matchesFilter && matchesSearch) ? '' : 'none';
    }});
  }}

  document.getElementById('filter-chips').addEventListener('click', function (e) {{
    var chip = e.target.closest('.chip');
    if (!chip) return;
    document.querySelectorAll('.chip').forEach(function (c) {{ c.classList.remove('active'); }});
    chip.classList.add('active');
    applyFilters();
  }});
  document.getElementById('search-box').addEventListener('input', applyFilters);

  // ---------- sorting ----------
  var sortState = {{ field: null, dir: 'asc' }};
  function sortRows(field) {{
    var tbody = document.getElementById('tbody');
    var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr[data-key]'));
    var dir = (sortState.field === field && sortState.dir === 'asc') ? 'desc' : 'asc';
    sortState = {{ field: field, dir: dir }};

    rows.sort(function (a, b) {{
      var av, bv;
      if (field === 'date') {{ av = a.getAttribute('data-date'); bv = b.getAttribute('data-date'); }}
      else if (field === 'company') {{ av = a.getAttribute('data-company').toLowerCase(); bv = b.getAttribute('data-company').toLowerCase(); }}
      else {{ av = a.querySelector('.status-badge').getAttribute('data-status'); bv = b.querySelector('.status-badge').getAttribute('data-status'); }}
      if (av < bv) return dir === 'asc' ? -1 : 1;
      if (av > bv) return dir === 'asc' ? 1 : -1;
      return 0;
    }});
    rows.forEach(function (r) {{ tbody.appendChild(r); }});

    document.querySelectorAll('th.sortable .arrow').forEach(function (a) {{ a.textContent = ''; }});
    var activeArrow = document.querySelector('th[data-sort="' + field + '"] .arrow');
    if (activeArrow) activeArrow.textContent = dir === 'asc' ? '\\u2191' : '\\u2193';
  }}
  document.querySelectorAll('th.sortable').forEach(function (th) {{
    th.addEventListener('click', function () {{ sortRows(th.getAttribute('data-sort')); }});
    th.addEventListener('keydown', function (e) {{
      if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); sortRows(th.getAttribute('data-sort')); }}
    }});
  }});

  // ---------- init ----------
  document.addEventListener('DOMContentLoaded', function () {{
    var overrides = JSON.parse(localStorage.getItem('trackerOverrides') || '{{}}');
    var legacyApplied = JSON.parse(localStorage.getItem('trackerApplied') || '[]');
    legacyApplied.forEach(function (key) {{ if (!overrides.hasOwnProperty(key)) overrides[key] = 'Applied'; }});

    document.querySelectorAll('tr[data-key]').forEach(function (row) {{
      var key = row.getAttribute('data-key');
      var status = overrides[key];
      if (!status) return;
      var badge = row.querySelector('.status-badge');
      var cell = badge.parentElement;
      if (badge.getAttribute('data-status') !== status) setBadge(badge, status);
      applyButton(cell, status);
    }});

    localStorage.setItem('trackerOverrides', JSON.stringify(overrides));
    localStorage.removeItem('trackerApplied');

    updateSummary();
    refreshStreakAndTrail();
    refreshRelativeDates();
    applyFilters();
  }});
</script>
</body>
</html>
"""

    OUT_PATH.write_text(html, encoding="utf-8")
    print(
        f"Wrote {OUT_PATH} with {total} rows "
        f"({applied} applied, {drafted} drafted, {rejected} rejected, {skipped} skipped)"
    )


if __name__ == "__main__":
    main()
