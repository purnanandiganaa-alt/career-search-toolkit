---
name: follow-up-check
description: Scan the application tracker for anything past a reasonable follow-up window with no response, and draft a follow-up message. Use periodically or when the user asks "should I follow up with anyone" / "what's overdue".
metadata:
  trigger: User asks about follow-ups, application status, or what needs attention in the pipeline
  author: adapted from santifer/career-ops's "followup" mode (MIT), reimplemented and scoped for a one-person job search
---

# Follow-Up Check

Small, but this is exactly the kind of thing that quietly falls through the cracks.

## Steps

1. Run `python3 scripts/pipeline_summary.py` to see the current tracker state.

2. Read `Applications/application_index.csv` directly for the `date` and `status` columns.
   For every row with status `Applied`, compute business days since the `date` column.

3. **Follow-up window: 10 business days.** If an `Applied` row has had no status change
   (still `Applied`, not `Responded`/`Interview`/`Rejected`) after 10 business days, flag it.

4. For each flagged application, draft a short, low-pressure follow-up message (email or
   LinkedIn, ask the user which) that:
   - References the specific role and application date
   - Restates interest briefly, doesn't re-pitch the whole cover letter
   - Asks a simple, answerable question ("wanted to check if there's any update on timeline")
   - Stays under 150 words

5. Present flagged applications + drafts. Never send anything — draft-only, same as every
   other candidate-facing output in this system.

## Output format

```
## Follow-Up Check

**Overdue (10+ business days since applying, no response):**

### {Company} — {Role}
Applied: {date} ({N} business days ago)

**Draft follow-up:**
{message}

---
```

If nothing is overdue, say so plainly — don't manufacture urgency where none exists.

## Never

- Never send a follow-up on the user's behalf.
- Never flag something as overdue based on a status other than `Applied` (an `Interview` or
  `Responded` row is not "stuck," it's progressing).
