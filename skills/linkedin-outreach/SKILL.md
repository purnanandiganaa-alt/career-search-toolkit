---
name: linkedin-outreach
description: Find a plausible contact at a company (recruiter, hiring manager, or team member) and draft a short, specific LinkedIn outreach message. Draft-only -- never sends or connects on the user's behalf. Use when applying isn't enough and the user wants a warmer path in.
metadata:
  trigger: User wants to reach out on LinkedIn, find a contact at a company, or get "a conversation, not just an application"
  author: adapted from santifer/career-ops's "contacto" mode (MIT), reimplemented and scoped for a one-person job search
---

# LinkedIn Outreach

Applications get you in the queue; a real message to a real person gets you a conversation.
This is draft-only — it never sends a connection request or message. The user always sends
it themselves.

## Steps

1. **Identify contact type.** Given the company + role, use WebSearch to find a plausible
   contact: the hiring manager (if named in the JD or company team page), a recruiter for
   that role, or a team member in a similar role (useful for a "what's it like to work there"
   question rather than a direct ask). Cap at 3 WebSearch queries.

2. **Draft the message**, tuned to contact type:
   - **Recruiter:** Direct, brief, names the specific role and one concrete reason the
     candidate is a fit (pull from `CLAUDE.md`, real facts only).
   - **Hiring manager:** Slightly more substantive — one specific thing about the team's work
     that connects to the candidate's actual experience.
   - **Team member / peer:** Genuinely curious, not transactional — ask one real question
     about the work, don't ask them to refer you in the first message.

3. **Length: ≤300 characters** (LinkedIn's connection-request message cap). No email, no
   phone number in the message — those go in a follow-up if the conversation continues.

4. **No corporate-speak.** Run the draft through the same standard as cover letters — this
   should sound like a real person, not a template. If in doubt, check it against the
   `stop-slop` skill's phrase list.

## Output format

```
## LinkedIn Outreach — {Company} — {Contact name/role, or "recruiter for {role}" if unnamed}

**Contact type:** {recruiter | hiring manager | peer}
**Why this person:** {one line on how they were identified}

**Draft message** ({char count}/300):
{message}
```

## Never

- Never send, connect, or message on the user's behalf — this is a draft only.
- Never fabricate a contact's name or role if it can't be found — say so and suggest the
  generic "recruiter for {role}" framing instead.
- Never include phone number in the initial message.
