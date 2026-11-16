---
description: "Open-work view: unshelved and pending CLs memory cites, pending CLs no memory names, Next: lines, and the Jira status of the project's Jira keys in MEMORY.md"
scope: project
allowed-tools: Read, Bash(python -I -X utf8 $KC_PROJECT_ROOT/.claude/scripts/p4/progress_view.py*), mcp__atlassian__searchJiraIssuesUsingJql
---

# Progress — where is all the open work?

For "where are we?" about **this session**, don't run this: answer in the 6-line shape from CLAUDE.local.md. This command is the whole-backlog view.

1. From `{{PROJECT_ROOT}}`, run in the background (about 30-60 s, read-only): `python -I -X utf8 $KC_PROJECT_ROOT/.claude/scripts/p4/progress_view.py`
2. In parallel, one JQL query for the {{JIRA_PROJECT_KEY}} keys the script prints last: `key in (<keys>)`, fields `summary,status`.
3. Reply in this order, max ~25 lines:
   1. **At risk** — every UNSHELVED and SHELF BEHIND DISK CL (work that exists only on disk), plus default-CL files (flag exclusive locks), one line each.
   2. **Next actions** — the `Next:` lines, grouped by topic, most actionable first.
   3. **Tickets** — key, status, summary; flag a Closed/Done ticket whose memory still has a Next: line.
   4. **Pending CLs no memory names** — count, plus the newest 5 titles; offer to triage them.
   5. **Cited pending CLs** — count only, unless the user asks for the list.
4. Don't edit memory or Perforce from this command. Offer the follow-ups (shelve, archive, file a ticket) as a numbered list.
