---
name: save-task-insight
description: Save important insights about a Jira task to a local findings file. Use when the user says "save this insight", "record this finding", "note this for the task", "save the last finding", or wants to capture discoveries, decisions, or learnings tied to a specific ticket ({{JIRA_PROJECT_KEY}}-XXXXX). Auto-detects task ID from context.
---

Record insights, findings, or decisions about a task to `{{TEMP_BASE}}\task_findings\<TASK_ID>.md`.

## Trigger

Invoke when the user wants to:
- Save an insight about the current task
- Record a finding or discovery
- Note a decision or learning for a ticket
- Capture context for future reference

## Arguments

```
/save-task-insight [TASK_ID] [insight text or "last"]
```

- **TASK_ID** (optional): Explicit task ID like `{{JIRA_PROJECT_KEY}}-1234`. If omitted, auto-detect from:
  1. `JIRA_ACTIVE_EPIC` in .claude/rules/project-vars.md
  2. Recent conversation mentions of `{{JIRA_PROJECT_KEY}}-XXXXX`
  3. Ask user if neither found

- **insight text**: The insight to save. Can be:
  - Explicit text: `/save-task-insight {{JIRA_PROJECT_KEY}}-1234 The spawn system needs a cooldown to prevent overlapping waves`
  - "last" or omitted: Extract from the most recent finding/discovery in conversation

## Behavior

### 1. Resolve Task ID

```
1. Check if TASK_ID provided in args → use it
2. Check JIRA_ACTIVE_EPIC in .claude/rules/project-vars.md → use it
3. Scan recent conversation for {{JIRA_PROJECT_KEY}}-\d+ pattern → use most recent
4. If none found → ask user
```

### 2. Resolve Insight Content

If explicit text provided, use it directly.

If "last" or no text provided, extract from conversation:
- Look for the most recent substantive finding, decision, or discovery
- Summarize in 1-3 sentences, preserving technical detail
- Include file paths or code references if relevant

### 3. Check for Conflicts

Read existing file at `{{TEMP_BASE}}\task_findings\<TASK_ID>.md` if it exists.

**Conflict detection**: Compare the new insight against existing entries:
- If semantically duplicate (same core information), skip and inform user
- If contradictory (opposite conclusion), warn user and ask how to proceed
- If complementary or new information, proceed to append

### 4. Append Insight

Create or append to `{{TEMP_BASE}}\task_findings\<TASK_ID>.md`:

```markdown
## [YYYY-MM-DD HH:MM] — <short title>

<insight content>

---
```

The short title should be 3-5 words summarizing the insight.

## File Structure

```markdown
# {{JIRA_PROJECT_KEY}}-1234 — Task Findings

## [2026-06-01 14:32] — Spawn cooldown needed

The wave spawner triggers overlapping spawns when players move between zones quickly. 
Adding a 2-second cooldown after each wave completes would prevent this.

---

## [2026-06-01 15:10] — Root cause in TriggerVolume

Found the issue in `ASpawnTriggerVolume::OnOverlapBegin` — it doesn't check if a wave 
is already in progress. The `bWaveActive` flag exists but isn't being checked.

---
```

## Examples

**Explicit insight:**
```
User: /save-task-insight {{JIRA_PROJECT_KEY}}-1234 The spawn overlap bug is caused by missing bWaveActive check
→ Appends timestamped entry to {{TEMP_BASE}}\task_findings\{{JIRA_PROJECT_KEY}}-1234.md
```

**Auto-detect task, extract from conversation:**
```
User: /save-task-insight
→ Detects {{JIRA_PROJECT_KEY}}-1234 from JIRA_ACTIVE_EPIC in project-vars.md
→ Extracts last finding from conversation
→ Checks for conflicts
→ Appends if no conflict
```

**With "last" keyword:**
```
User: /save-task-insight last
→ Explicitly requests extraction from conversation
```

## Output

After saving, confirm:
```
Saved to {{TEMP_BASE}}\task_findings\{{JIRA_PROJECT_KEY}}-1234.md:
"[2026-06-01 14:32] — Spawn cooldown needed"
```

If conflict detected:
```
This insight appears to duplicate an existing entry from [2026-06-01 14:32].
Skip, or save anyway?
```
