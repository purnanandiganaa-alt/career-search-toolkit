# Career Search Toolkit

A set of [Claude Code](https://claude.com/claude-code) skills, small Python scripts and an HTML
tracker for running a job search with an AI assistant. The assistant never invents facts about you.

Everything the assistant writes about you (fit scores, résumés, cover letters, outreach
messages) comes from one file you write yourself: `CLAUDE.md`. If a skill isn't in there, the
assistant won't claim it. Nothing gets submitted or sent automatically. Every skill stops at a
draft and you take it from there.

## What's inside

```
career-search-toolkit/
├── CLAUDE.md.template        # your profile: copy to CLAUDE.md and fill in
├── skills/                   # Claude Code skills (copy into ~/.claude/skills/)
│   ├── job-fit-eval/
│   ├── tailor-application/
│   ├── company-research/
│   ├── linkedin-outreach/
│   ├── follow-up-check/
│   ├── job-scan/
│   └── stop-slop/
├── scripts/
│   ├── states.py             # list of allowed application statuses
│   ├── set_status.py         # change an application's status safely
│   ├── pipeline_summary.py   # print your applications as a table
│   ├── job_scan.py           # scan company job boards (no LLM calls)
│   └── companies.example.json
└── tracker/
    ├── rebuild_tracker.py    # build an HTML dashboard from your CSV
    └── sample_application_index.csv
```

### Skills

| Skill | What it does |
|---|---|
| `job-fit-eval` | Scores a job posting against the skills and projects in your `CLAUDE.md`, lists the gaps, checks for ghost-job signs and recommends apply or skip. Run this before tailoring anything. |
| `tailor-application` | Drafts a tailored résumé and cover letter for one posting, saves them in a folder for that application and adds a row to your tracker. |
| `company-research` | A short research brief on a company (at most 5 web searches): what they do, recent news, culture, likely challenges and how your background fits. |
| `linkedin-outreach` | Finds a likely contact at a company and drafts a short message. It only drafts. It never sends or connects. |
| `follow-up-check` | Finds applications with no reply after 10+ business days and drafts follow-ups. |
| `job-scan` | Checks public Greenhouse and Ashby job boards for the companies you list. It makes no LLM calls, so it costs no tokens. |
| `stop-slop` | Strips common AI writing patterns from drafts. Every cover letter and outreach message goes through it. |

## Requirements

- [Claude Code](https://docs.claude.com/en/docs/claude-code/overview) (CLI, desktop app or IDE extension)
- Python 3.9+
- `certifi` (only needed for `job-scan`)

## Setup

### 1. Get the code

Clone the repo. The cloned folder becomes your job-search workspace: the scripts look for
`CLAUDE.md`, `Applications/` and `scripts/` relative to this folder.

```bash
git clone https://github.com/purnanandiganaa-alt/career-search-toolkit.git
cd career-search-toolkit
```

Your personal files (`CLAUDE.md`, `Applications/`, `Templates/`, `scripts/companies.json`,
`job_search_log.md`, the generated tracker HTML) are listed in `.gitignore`, so they stay out
of git if you fork the repo.

### 2. Install the skills

Claude Code loads skills from `~/.claude/skills/`:

```bash
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

Restart Claude Code afterwards. You can call a skill by name ("run job-fit-eval on this
posting"), and Claude also uses one on its own when your request matches, for example when you
paste a posting and ask "should I apply?".

### 3. Write your `CLAUDE.md`

This step matters most.

```bash
cp CLAUDE.md.template CLAUDE.md
```

Open `CLAUDE.md` and replace every `{placeholder}` with real information: your contact
details, work authorization, language levels, projects with their actual stack and metrics, and
your skills. The skills read this file as the only source of facts about you. If something isn't
in it, they won't put it on a résumé.

Be precise about work authorization and language levels. The skills match these against job
requirements.

### 4. Create the folders

```bash
mkdir -p Applications Templates
head -1 tracker/sample_application_index.csv > Applications/application_index.csv
touch job_search_log.md
```

Put your master résumé and cover letter (LaTeX, Word or whatever you use) in `Templates/`.
`tailor-application` starts from these.

After a few applications the folder looks like this:

```
Applications/
  application_index.csv              # one row per application
  2026-10-15_Acme_MLEngineer/
    job_posting.md                   # the posting, saved as-is
    YourName_Resume_Acme.pdf
    CoverLetter_Acme.pdf
    notes.md                         # what was changed and why
```

### 5. Try the tracker

To see the tracker with sample data before you have your own:

```bash
cp tracker/sample_application_index.csv Applications/application_index.csv
python3 tracker/rebuild_tracker.py
open "Job Applications Tracker.html"     # macOS; on Linux use xdg-open
```

Then reset the CSV to its header row (step 4) when you're ready to use your own data. Set
`CANDIDATE_NAME` at the top of `tracker/rebuild_tracker.py` to your name. You can also change
`OUT_PATH` there if you want the HTML somewhere else, such as your Desktop.

The tracker is a single HTML file with status badges, a follow-up heatmap, an application
streak, and search and sort. Its "Mark Applied/Rejected" buttons only save in your browser.
The CSV stays the source of truth, so rerun the script whenever the CSV changes.

### 6. Set up job scanning (optional)

```bash
pip install certifi
cp scripts/companies.example.json scripts/companies.json
```

Edit `scripts/companies.json`:

- `companies`: each company's name, ATS provider (`greenhouse` or `ashby`) and board slug.
  The slug is the company part of the job-board URL, e.g. `boards.greenhouse.io/<slug>` or
  `jobs.ashbyhq.com/<slug>`. Check that a slug works before adding it (see
  `skills/job-scan/SKILL.md`).
- `title_filter.domain`: a job title must contain at least one of these.
- `title_filter.negative`: a job title must contain none of these.
- `location_filter.include`: the location must contain at least one of these.

Then run:

```bash
python3 scripts/job_scan.py --dry-run   # print matches only
python3 scripts/job_scan.py             # print and record them in job_search_log.md
```

Postings already in `job_search_log.md` aren't shown again.

## Day-to-day use

Open Claude Code in this folder and talk to it normally:

| You say | What runs |
|---|---|
| "Scan for new jobs" | `job-scan` |
| *(paste a posting)* "Is this a good fit?" | `job-fit-eval` |
| "Tailor my application for this" | `tailor-application` → `stop-slop` |
| "Research Acme before my interview" | `company-research` |
| "Who could I message at Acme?" | `linkedin-outreach` |
| "Should I follow up with anyone?" | `follow-up-check` |

You can also run the scripts yourself:

```bash
python3 scripts/pipeline_summary.py                               # list applications
python3 scripts/set_status.py "Acme Corp" Applied                 # asks for confirmation
python3 scripts/set_status.py "Acme Corp" Interview --note "Phone screen Tuesday"
python3 tracker/rebuild_tracker.py                                # refresh the HTML tracker
```

Change statuses with `set_status.py` rather than editing the CSV by hand. The allowed statuses
are `Evaluated`, `Drafted`, `Applied`, `Responded`, `Interview`, `Offer`, `Rejected`,
`Discarded` and `SKIP` (defined in `scripts/states.py`).

## Ground rules built into the skills

- **No fabrication.** Every claim about you has to come from `CLAUDE.md`. When a posting asks
  for something you don't have, the skills either leave it out or name the gap honestly.
- **No automatic submissions.** Skills draft. You review and submit, and you send any messages.
- **Low-fit roles get flagged.** If `job-fit-eval` scores a role below 3.0/5, it says so and
  explains why instead of tailoring an application anyway.

## Credits

- Most skills are adapted from [santifer/career-ops](https://github.com/santifer/career-ops)
  (MIT), rewritten in Python and Markdown for a single-person job search.
- `skills/stop-slop/` is by Hardik Pandya (MIT). See [its license](skills/stop-slop/LICENSE).

## License

[MIT](LICENSE)
