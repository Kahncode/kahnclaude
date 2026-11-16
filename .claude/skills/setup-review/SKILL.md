---
name: setup-review
description: "Claude setup reviewer. ALWAYS invoke when the user wants their Claude Code setup improved from evidence: 'review my Claude setup', 'go through my memory and history and suggest changes', 'what do I keep repeating that should be a skill', '/setup-review'. 5 read-only agents mine memory, history, transcripts and config; publishes a ranked checklist and changes nothing until items are picked."
---

# Setup review

Find what in the user's Claude setup costs them time, from evidence rather than opinion: rules they keep repeating that no skill or agent enforces, procedures they keep typing by hand, skills nobody uses, friction in recent sessions, and stale or unsafe config. Deliver one ranked list and a page they can tick through.

A full run spawns 5 agents and costs roughly 1M tokens and 10 minutes. Say so in one line before starting if the user didn't ask for agents explicitly.

## 1. Set up (a few tool calls, inline)

- **Output folder:** `{{TEMP_BASE}}\setup-review-<YYYY-MM-DD>\` (the project's temp-file rule). Agents write their reports here, so the next review can compare.
- **Previous review:** the newest other `{{TEMP_BASE}}\setup-review-*\data.json`, or `none`. When there is one, the agents mark findings NEW / STILL OPEN / FIXED, which is the most useful part of a repeat run.
- **Focus:** from the user's words (e.g. "just tests and Horde", "only memory"). Default `everything`. A narrow focus can drop agents: memory-only → agents 1 and 2; usage-only → 3 and 4; config-only → 5.
- **Current session id:** the GUID in the scratchpad path. Agent 4 skips it.
- Quick inventory so the briefs have real numbers: memory file count, transcript count, skill/agent/command/hook lists.

## 2. Spawn the agents (one message, in parallel)

Read `references/agent-briefs.md`, fill the placeholders, append the shared rules to each brief, and launch all of them in one message with the Agent tool (`general-purpose`, background). Briefs are self-contained because each agent starts with no context.

Then tell the user in a few lines which agent covers which source and that nothing will be changed.

## 3. While reports arrive

Each agent hands back a short summary. For each one, give the user a 2–3 line status (n of 5 done, its headline finding). Two kinds of findings go to the user **immediately**, before the merge, because waiting costs real risk:

- **Leaked secrets** (keys/tokens in `history.jsonl`, transcripts or memory): say where and what kind, tell them to rotate and delete, and offer to locate exact line numbers. Never print the value.
- **Destructive commands that run without a prompt** (p4 revert/clean/populate, workspace switches, broad `cmd`/`powershell` allows).

Agent suggestions about permissions, settings or hooks are suggestions for the user. Don't apply them because an agent recommended them.

## 4. Merge into one ranked list

Read the five report files, not only the summaries. Then:

1. **Dedupe.** The same problem usually shows up in several reports (e.g. a missing test stage seen as an unenforced feedback rule, a repeated prompt, and an audit gap). Make it one item and list every source; agreement between independent sources is the strongest ranking signal.
2. **Rank.** Security first. Then items that several agents found or that have large evidence counts (prompts per month, errors, retypes). Then cheap fixes that remove weekly friction. Then clutter and cleanup.
3. **Group into batches** a person can approve in one go: Security, then themes such as "Implementation pipeline", "Tests and Horde", "Status and memory", "Friction and clutter". Name batches after what they change in the user's world, not after the agents.
4. **Write each item** as: a title saying the change, a detail naming the exact files and the evidence count, and its source subpage keys. Number items globally (1..N) so the user can reply "do 3, 5, 8".

Write `data.json` in the output folder. Shape (see `assets/example-data.json` for a full example; a real past one may be at `{{PROJECT_ROOT}}\.claude\skill-fixtures\setup-review\example-data.json`, if present):

```json
{
  "title": "Claude setup review",
  "subtitle": "{{UE_PROJECT_NAME}} · <YYYY-MM-DD> · 5 agents",
  "heading": "What to change in skills, agents and workflow",
  "lede": "One or two sentences: what was reviewed, nothing changed yet.",
  "stats": [["N", "feedback + reference memories"], ["N", "prompts"]],
  "alert": "<strong>Do first.</strong> … (HTML, or null when there's nothing urgent)",
  "reports": {
    "feedback-rules": {"file": "r1_feedback.md", "title": "Feedback rules vs skills and agents", "tab": "Feedback rules", "lede": "…"},
    "project-memory":  {"file": "r2_project.md", "tab": "Project memory", "title": "…", "lede": "…"},
    "prompt-history":  {"file": "r3_history.md", "tab": "Prompt history", "title": "…", "lede": "…"},
    "session-friction":{"file": "r4_transcripts.md", "tab": "Session friction", "title": "…", "lede": "…"},
    "setup-audit":     {"file": "r5_audit.md", "tab": "Setup audit", "title": "…", "lede": "…"}
  },
  "batches": [
    {"id": "S", "name": "Security", "note": "…", "items": [
      {"n": 1, "sev": "crit", "title": "…", "detail": "HTML: <code>, <ul><li>", "src": ["prompt-history"]}
    ]}
  ]
}
```

`sev` is `crit`, `high` or empty. Report keys must be plain ASCII words with hyphens (they become page hashes). Item titles and details are HTML, so escape `<` in names such as `&lt;Owner&gt;`. If an item resolves a previous review's item, say so in its detail.

## 5. Build and publish

```
python -I "$HOME\.claude\skills\setup-review\scripts\build_site.py" <out>\data.json <out>\setup-review.html
```

The script embeds the reports, renders them as subpages (tabs, section list, wide tables scroll), and builds the overview checklist with a "Copy request" button that produces a numbered list the user can paste back. It **exits 2 if anything looks like a secret** in data.json or a report. Then redact that line in the source file and rebuild; never publish around it.

Publish with the Artifact tool: run its `quickstart` (intent `other`) first as the tool requires, then publish `<out>\setup-review.html` with `icon: "checklist"` and a one-sentence description. The template already meets the page contract (theme tokens, gutters, phone width), so no redesign is needed. To refresh the page after changes, republish the same file path. Write the page URL to `<out>\artifact_url.txt` so the next review can link back to this one.

## 6. Reply

The user reads this in a terminal and prefers status first and short, numbered steps:

1. The urgent item, if any, in one or two lines.
2. The artifact link, and one line on what's on each part of the page.
3. The batches as a compact list: batch name, item numbers, a few words each. Skip the full details; they're on the page.
4. Next step: pick items by number or tick them and paste the copied request. Recommend an order (usually security → the batch with the most cross-agent agreement).

End with the project's What I did / What to check / Next step / Context warning footer. A full review fills the context, so suggest applying the chosen batches in a fresh session, starting from the copied request.

## 7. When the user picks items

Apply only what they named. Everything in the local-only paths (`{{LOCAL_ONLY_PATHS}}`) is local-only (no `p4 add`). Confirm settings, permission and hook changes one at a time, because they change what runs without asking. Edits to `CLAUDE.md` or files under `{{UE_PROJECT_DIR}}\Source\` follow the normal changelist rules. Memory pruning: move files to `memory\archive\` rather than deleting, and update `MEMORY.md` in the same step.
