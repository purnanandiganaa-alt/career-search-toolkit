---
name: company-research
description: Produce a structured research brief on a company -- what they do, recent moves, culture signals, likely challenges, and the candidate's specific angle. Use before an interview, before writing a sharper cover letter opener, or whenever the user asks to research a company.
metadata:
  trigger: User asks to research a company, understand a company before interviewing, or wants background before applying
  author: adapted from santifer/career-ops's "deep" mode (MIT), reimplemented and scoped for a one-person job search
---

# Company Research

A bounded research pass — not an open-ended investigation. Cap at 5 total WebSearch queries;
prefer targeted queries that answer more than one question.

## Six-axis brief

1. **What they actually do.** Product/service in plain language, not marketing copy.
2. **Recent moves.** Funding, layoffs, major product launches, leadership changes — anything
   in the last 6–12 months that would come up in conversation.
3. **Engineering/AI culture signals.** Remote policy, team size if discoverable, tech stack
   hints from job postings or engineering blog, how they talk about AI/ML work if relevant.
4. **Likely challenges.** What problem is this role probably hired to solve? Infer from the
   JD and company stage, don't guess wildly.
5. **Competitors / market position.** Who else is in this space, and how does this company
   position itself against them?
6. **Candidate's angle.** Given the verified facts in `CLAUDE.md`, what's the honest, specific
   connection between the candidate's actual background and this company's actual work? Not a
   generic "I'm passionate about your mission" — a real, specific link between something the
   candidate actually built or did and something the company actually works on.

## Output format

```
## Company Research — {Company}

**What they do:** ...
**Recent moves:** ...
**Culture signals:** ...
**Likely challenges this role addresses:** ...
**Competitive position:** ...
**Your angle:** ...
```

## Use

Feed this directly into a cover letter opener (via `tailor-application`) or into interview
prep. Don't research the same company twice in one session — if a brief already exists in
that application's `notes.md`, reuse it.

## Never

- Never spawn nested subagents or delegate to an open-ended research skill — this is bounded,
  inline research with a 5-query cap.
- Never present speculation as fact — if something can't be found, say so rather than guessing.
