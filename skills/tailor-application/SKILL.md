---
name: tailor-application
description: Create a new tailored resume and cover letter for a specific job, following the project's established folder structure and process. Use after job-fit-eval recommends applying, or whenever the user asks to prepare an application for a specific posting.
metadata:
  trigger: User asks to apply to, tailor a resume/cover letter for, or prepare an application for a specific company/role
  author: formalized from a project CLAUDE.md's application checklist, adapted from santifer/career-ops (MIT)
---

# Tailor Application

Formalizes the application process into one invocable skill, so it runs the same way every
time instead of being re-read from memory.

**Read `CLAUDE.md` (at the project root) in full before starting** — it should hold the
candidate's verified facts, the folder structure, and any style rules this skill depends on.
See `CLAUDE.md.template` in the career-search-toolkit repo for the shape it should take if it doesn't exist yet.

## Steps

1. Save the job posting to
   `Applications/YYYY-MM-DD_Company_Role/job_posting.md` (create the folder).

2. Compare the posting's requirements against the verified skills/projects in `CLAUDE.md`.
   Do not add anything not actually true to look like a better match. If `job-fit-eval` was
   not already run for this posting, run it first — don't tailor an application for a role
   that hasn't been checked for fit.

3. Copy the resume and cover letter from `Templates/` into the new folder, renamed
   `<CandidateName>_Resume_<Company>.tex` / `CoverLetter_<Company>.tex` (substitute the
   candidate's actual name — see `CLAUDE.md`).

4. Tailor content — reorder/emphasize genuinely relevant existing experience, don't invent
   new experience. If the posting has a real gap (e.g. a tool never used), name it honestly
   in the cover letter rather than omitting it silently.

5. Run the cover letter text through the `stop-slop` skill before compiling to PDF. Fix
   anything it flags until it scores 35/50 or higher. This is not optional polish — it's part
   of writing the letter.

6. Compile both to PDF (`pdflatex`), then clean up `.aux`/`.log`/`.out` build artifacts
   (`rm -f *.aux *.log *.out` in that folder) — keep only `.tex` + `.pdf` + the two `.md` files.

7. Write `notes.md`: what was changed, why, any language-choice reasoning, and current status.

8. Add a row to `Applications/application_index.csv` with status `Drafted` (or `Evaluated`
   if a fit score already exists and drafting hasn't started yet). CSV columns: `date,
   company, position, location, status, resume_path, cover_letter_path, notes_path,
   posting_link` (see `tracker/sample_application_index.csv` in the career-search-toolkit repo for the exact
   shape).

9. If you keep a "ready to upload" shortcut folder on the desktop, refresh it to point at
   this application's two PDFs (delete the previous company's shortcuts first). Keep only the
   current application's files there, not every past one.

## Language choice

Check `CLAUDE.md` for the candidate's actual stated language proficiency before choosing the
cover letter's language — don't assume fluency in a language just because a posting prefers
it. Only switch away from the default language if the posting explicitly requires fluency in
another language as a hard requirement (not just "advantageous") — confirm with the user
before switching.

## Status discipline

Never mark a row `Applied` in `application_index.csv` by hand — use `scripts/set_status.py`,
which asks for explicit confirmation before setting that status, so the tracker only reflects
applications the user has actually sent, not drafts sitting in a folder.

## Never

- Never invent experience or metrics to fill a gap.
- Never hand-edit `application_index.csv` directly — use `scripts/set_status.py` for status
  changes, and append a new row directly only when creating the application for the first time.
- Never skip the `stop-slop` pass on the cover letter.
