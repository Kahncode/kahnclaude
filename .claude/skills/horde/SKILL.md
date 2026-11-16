---
name: horde
description: "Horde CI question and link handler. ALWAYS invoke when the user pastes a Horde link with a question other than 'why is this step red', or asks about Horde behaviour or config: 'why didn't the nightly build run', 'why was this step skipped', 'how do I chain a template', 'which Horde version is live'. Also '/horde learn <doc>'. Not for a red step or failure paste (horde-artifact)."
---

# Horde: links and questions

Knowledge home: `{{HORDE_DOC}}` (this project's server, config, agents) and `docs/tech-stacks/horde.md` (generic Horde). Link table: `references\link-shapes.md`.
Work: `{{TEMP_BASE}}\horde-scratch\`. Read-only: GET requests only. No reruns, no preflights, no config edits.

## 1. Route
- `/horde learn …` or "load / read the new Horde docs" → step 5.
- Slack `:x:` paste, `/artifact/<id>`, a step-saved zip, or "why did this step fail / go red" → invoke `horde-artifact` and stop.
- A link → step 2. A question with no link → step 4 without JSON.

## 2. Parse the link
Read `references\link-shapes.md`. Pull out the ids (jobId, stepId, batchId, issueId, logId, agentId, streamId, templateId). Say what the link points to in one line.

## 3. Fetch the JSON (Chrome)
- One ToolSearch: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__tabs_close_mcp`.
- `tabs_context_mcp` → `tabs_create_mcp` → navigate to `{{HORDE_URL}}/`.
- `javascript_tool`: `fetch('<endpoint>?filter=<fields>', {credentials:'include'})`, returning `status + ' ' + text`. Use the `filter` param from link-shapes.md to keep the body small. Fetch only what the question needs (a job, plus the issue if `issue=` is present, plus agent history if the question is about the machine).
- Write each body to `{{TEMP_BASE}}\horde-scratch\<kind>-<id>.json` with Write. Close the tab.
- 401/403 or the extension isn't connected → tell the user (log into Horde in Chrome / open Chrome with the extension) and stop.

## 4. Ask horde-guide
Spawn the `horde-guide` agent (foreground). Prompt:
- the user's question, verbatim
- what the link is plus the ids
- the saved JSON paths
- "Mode: Q&A"
If it replies `Route: horde-artifact`, invoke `horde-artifact` with the job/step.

## 5. Learn mode
1. Save pasted text to `{{TEMP_BASE}}\horde-scratch\learn-<yyyymmdd>.md`. A URL or file path is passed as-is. "After engine sync" needs no input.
2. Spawn `horde-guide` with "Mode: Learn" and the source.
3. Show the proposals table to the user, with contradictions first.
4. Write only the rows the user approves into the file the agent named (Edit): generic facts → `docs/tech-stacks/horde.md`, project facts → `{{HORDE_DOC}}`. Update its Sources table row.
5. A new red signature belongs in `{{HORDE_RUNBOOK}}` only when a memory file backs it (runbook rule).

## 6. Report
1. **Answer**: the agent's answer line.
2. **Evidence**: its top 2-4 citations.
3. **Next step**: one action, or none.

When the answer revealed a new stable fact, offer to add it to horde.md (not memory).

## Config change requests
"Make template X run at Y", "add a chain", "change escalation": answer how (horde-guide), then stop. Editing `{{P4_DEVTOOLS_STREAM}}` goes live on submit with no staging. That work needs its own plan, a `{{P4CLIENT_DEVTOOLS}}` CL, and a dry run with `$KC_PROJECT_ROOT/.claude/skills/horde/scripts/listonly_templates.py` before the user submits.
