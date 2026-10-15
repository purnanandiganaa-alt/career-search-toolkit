---
name: job-fit-eval
description: Score a job posting against the candidate's actual verified skills and projects, flag gaps honestly, check for ghost-job signals, and give a clear apply/skip recommendation. Use before tailoring a resume or cover letter for any job.
metadata:
  trigger: User pastes a job posting/URL and asks "should I apply", "is this a good fit", "evaluate this job", or before starting any new application
  author: adapted from santifer/career-ops (MIT), reimplemented and scoped for a one-person job search
---

# Job Fit Evaluation

Filter before you invest time, not after. This mirrors career-ops's core discipline:
**quality over quantity, and no fabrication, ever.**

## Source of truth

All fit claims come **exclusively** from `CLAUDE.md` at the root of this project (the
candidate's verified facts, projects, and skills) — never from memory, never from
assumption, never by matching a JD requirement just because it would look better if true.
If a JD asks for something not in that file, it's a gap. Reformulate and reframe existing
real experience; never invent new experience.

Before this skill can do anything useful, `CLAUDE.md` needs to actually contain the
candidate's real background — see `CLAUDE.md.template` in the career-search-toolkit repo for the shape it
should take (who this is for, verified projects/skills, work-authorization status, location
and language facts, etc).

## Steps

1. **Blacklist check.** If `Applications/blacklist.md` exists, check the company against it.
   On a hit, stop and ask: "{Company} is on your do-not-apply list ({reason}). Evaluate anyway?"
   Wait for an explicit answer before proceeding.

2. **Fit scoring (1–5 per dimension, weighted average for Global):**

   | Dimension | What it measures |
   |---|---|
   | Skills match | How many of the JD's actual requirements map to real, verified skills/projects |
   | Level fit | Does the seniority/scope match the candidate's actual level as stated in `CLAUDE.md` (student/entry-level roles score well if that's the candidate's level; "5+ years experience" roles score low unless the JD explicitly welcomes strong juniors) |
   | Work-authorization fit | Cross-check against the `CLAUDE.md` work-status section — does this role type (part-time/full-time, sponsorship needs, visa status) match what's actually permitted right now? |
   | Location/remote fit | Cross-check against the candidate's base location and stated relocation/remote preferences in `CLAUDE.md` — score down only for a genuine mismatch, not just distance, once relocation willingness (if any) is accounted for |

   **Score interpretation:**
   - 4.0+ → Good fit, worth tailoring an application
   - 3.0–3.9 → Marginal — only proceed if there's a specific reason (e.g. dream company, direct referral)
   - Below 3.0 → **Explicitly recommend against applying.** State why. The user can still override, but the recommendation must be clear and not buried.

3. **Gap list.** For every JD requirement not backed by `CLAUDE.md`'s verified facts:
   - Name it plainly.
   - Say whether it's a hard blocker or a nice-to-have.
   - If there's genuinely adjacent experience, say so — but only if it's real, not a stretch.
   - If there's no honest mitigation, say "no direct experience — would need to name this gap
     openly in the cover letter" rather than glossing over it.

4. **Ghost-job / legitimacy check** (lightweight — this is not deep research):
   - Posting age, if visible (very old or "evergreen" postings are lower priority, not necessarily fake)
   - Does the JD name specific tools/team context, or is it generic boilerplate?
   - Any internal contradiction (e.g. "entry-level" title with "5+ years required")?
   - One line verdict: **Looks legitimate** / **Some generic-boilerplate signals, still worth trying** / **Multiple concerning signals, verify before investing time** — always present as observation, never accusation.

5. **Recommendation.** One paragraph: apply or skip, and the single biggest reason why.

## Output format

```
## Fit Evaluation — {Company} — {Role}

**Global score:** {X.X}/5

| Dimension | Score | Note |
|---|---|---|
| Skills match | X/5 | ... |
| Level fit | X/5 | ... |
| Work-auth fit | X/5 | ... |
| Location fit | X/5 | ... |

**Gaps:**
- {gap}: {blocker/nice-to-have} — {mitigation or "no honest mitigation"}

**Legitimacy:** {verdict}

**Recommendation:** {apply/skip + one-sentence reason}
```

## After evaluating

If the recommendation is to apply, ask whether to proceed straight to the `tailor-application`
skill. If below 3.0, state the recommendation against applying clearly — do not silently start
tailoring anyway. The user's call is final either way, but the recommendation must not be buried
under enthusiasm to be helpful.

## Never

- Never invent a skill, metric, or experience to raise a score.
- Never claim solo authorship of team work — check `CLAUDE.md` for how each project's
  attribution (solo vs. team) is actually documented.
- Never present the legitimacy check as an accusation — it's a time-prioritization signal, not a verdict.
