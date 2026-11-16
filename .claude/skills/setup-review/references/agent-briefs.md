# Agent briefs

Five read-only briefs, one per evidence source. Fill the placeholders before sending:

| Placeholder | Value |
|---|---|
| `{OUT}` | this run's output folder, e.g. `{{TEMP_BASE}}\setup-review-<date>` |
| `{MEM}` | `{{CLAUDE_MEMORY_DIR}}` |
| `{PROJ}` | the parent folder of `{{CLAUDE_MEMORY_DIR}}` (session transcripts `*.jsonl`) |
| `{SESSION}` | the current session id (from the scratchpad path), so agents skip it |
| `{PREV}` | previous review's `data.json`, or `none` |
| `{FOCUS}` | the user's focus, or `everything` |
| `{SESSIONS}` | number of recent transcripts to mine (default 60) |

Every brief ends with the same shared rules; paste them in.

## Shared rules (append to every brief)

```
Rules:
- READ-ONLY. Don't edit anything except your report file and scratch scripts in {OUT}\scratch\.
- Big files (transcripts, history.jsonl): stream them with Python scripts saved in {OUT}\scratch\ and run with `python -I`. Never read them raw.
- Never write a secret value (token, key, password) into your report or summary. If you find one, report only where it is (file, date, kind) and that it needs rotating.
- If {PREV} is not "none", read it and mark each of your findings NEW, STILL OPEN or FIXED relative to that review.
- Focus: {FOCUS}. Give findings outside the focus one line each at the end.
- Every suggestion names the exact file and the exact change (≤2 lines of text to add, or what to delete), plus its evidence count.
- Write the full report as markdown to the file named below. Then reply with a ≤25-line summary: top suggestions ranked by how often the problem bites, each with its evidence.
```

## 1. Feedback rules → owning file (`r1_feedback.md`)

```
Goal: find user corrections (feedback/reference memories) that are not yet in the skill, agent, standard or CLAUDE file that should enforce them, so the user stops repeating themselves.

Subagents (code-dev, code-planner, code-reviewer…) never read memory files, so a rule that lives only in memory never reaches the agent writing code. That's the main thing to catch.

Inputs: {MEM}\MEMORY.md and every feedback_*.md and reference_*.md file; .claude/skills/*/SKILL.md and {{PROJECT_ROOT}}\.claude\skills\*\SKILL.md (skip *-workspace); .claude/agents/core/*.md and {{PROJECT_ROOT}}\.claude\agents\**\*.md; {{PROJECT_ROOT}}\CLAUDE.md, CLAUDE.local.md; docs/standards/**; {{PROJECT_NOTES_DIR}}\*.md (project overlays); {{UE_TEST_README}}.

For each memory: owning file, status (enforced — quote the line / partial / missing / conflict / stale-or-duplicate), suggested edit. Also flag memories that contradict each other or a skill, and memories that are general rules that belong in CLAUDE.md or an agent prompt.

Report file: {OUT}\r1_feedback.md (a table: memory | owning file | status | exact edit).
```

## 2. Project memory → workflow gaps and open items (`r2_project.md`)

```
Goal: from the project memories, find recurring work patterns a skill/agent/workflow step would remove, list the open ("owed") items that are still really open, and propose memory pruning.

Inputs: {MEM}\MEMORY.md, every project_*.md and index_*.md file; skill descriptions in .claude/skills/*/SKILL.md and {{PROJECT_ROOT}}\.claude\skills\*\SKILL.md.

1. Recurring task shapes (e.g. Horde red → artifact → investigate → quarantine CL → fix CL → Horde rerun): which steps are manual every time, which skill covers each, what's missing.
2. Owed items (UBT owed, shelve owed, Horde run owed, tests not run, unbuilt, A/B owed). Check every CL number against Perforce: `p4 describe -s -O <n>` resolves a pending number that was renumbered on submit. Split into: moot (submitted), still open, empty pending CLs (no files, no shelf).
3. Memory hygiene: MEMORY.md line count and size (it loads every session; ~4 chars per token), memories for submitted CLs, duplicates, orphans not in the index, entries that belong in an index_*.md or in docs/.
4. Facts repeated across memories that point to a missing doc or runbook.

Report file: {OUT}\r2_project.md.
```

## 3. Prompt history → usage and repeated asks (`r3_history.md`)

```
Goal: from what the user actually types, find repeated manual prompts that should be skills or commands, skills that are never used, and triggers that miss.

Input: ~/.claude/history.jsonl (one JSON object per line: display, pastedContents, timestamp ms, project, sessionId). Filter to project == `{{PROJECT_ROOT}}` (the decoded path string). history.jsonl only records skills typed by name, so also count Skill tool calls (tool_use name "Skill", input.skill) in {PROJ}\*.jsonl to see auto-triggered use.

1. Usage per skill/command (typed and auto), all time and last 30 days, against the lists in {{PROJECT_ROOT}}\.claude\skills\, {{PROJECT_ROOT}}\.claude\commands\, .claude/skills/, .claude/commands/. Which are never or no longer used?
2. Cluster non-slash prompts by intent; counts plus 2-3 short verbatim examples (redact secrets). Highlight clusters with no skill, or where the user spells out a multi-step procedure.
3. Corrections and frustration ("no,", "I said", "again", "stop", "why did you") grouped by theme.
4. Long prompts pasted repeatedly with the same template.
5. Secrets: check `pastedContents` and `display` for keys or tokens; report location and kind only.

Report file: {OUT}\r3_history.md.
```

## 4. Session transcripts → friction (`r4_transcripts.md`)

```
Goal: mine recent transcripts for friction a skill, agent, hook or settings change would remove.

Input: the {SESSIONS} most recently modified {PROJ}\*.jsonl files, skipping {SESSION} (this session). Files total several GB. Records: type "user" with string content or text blocks = real user turns; tool_result blocks = tool output (is_error flag); type "assistant" has tool_use blocks (name, input). Resumed/forked sessions copy earlier records, so dedupe by message uuid.

Count and show short excerpts for:
1. Interruptions and corrections ("[Request interrupted", turns starting no/stop/don't/wrong/why/again) and what the assistant was doing just before.
2. Repeated tool errors grouped by tool + normalized message (hook blocks, timeouts, p4 read-only, UBT exit codes, Live Coding stalls, classifier denials).
3. Agent and Skill usage by type/name; agents re-spawned for the same task; user asking to use or not use agents.
4. Long loops: many consecutive identical shell commands (build/test retries, wait loops).
5. Permissions: denials and repeated approvals, compared with {{PROJECT_ROOT}}\.claude\settings.json, settings.local.json and ~/.claude/settings.json. Note rules that can never match. The user often runs auto mode, so missing prompts don't mean missing rules.

Report file: {OUT}\r4_transcripts.md.
```

## 5. Setup audit → skills, agents, commands, hooks (`r5_audit.md`)

```
Goal: audit the skills, agents, commands and hooks for overlap, gaps, staleness, quality and safety.

Inputs: {{PROJECT_ROOT}}\.claude\skills\* (and *-workspace leftovers), .claude/skills/*, {{PROJECT_ROOT}}\.claude\agents\**\*.md, .claude/agents/**/*.md, {{PROJECT_ROOT}}\.claude\commands\*.md, .claude/commands/*.md, {{PROJECT_ROOT}}\.claude\hooks\*.py, .claude/hooks/*, the three settings files, the CLAUDE files, {MEM}\feedback_*.md.

1. Overlapping triggers between skills and commands; propose merges, retirements or sharper description boundaries.
2. Agent definitions: tool lists too broad or narrow, missing rules that CLAUDE.md and feedback memories require, missing agents.
3. Skill quality: frontmatter that doesn't parse, descriptions over 1024 chars, very long bodies, stale hardcoded values (CL numbers, paths, URLs, transition IDs), references to files that don't exist. Check each path you cite.
4. Hooks and permissions: what each hook does and whether it's wired in settings; confirm gaps by piping sample tool inputs to the hook scripts. Look hard at destructive commands (p4 revert/clean/populate/submit, workspace switches, Engine/ edits) that run without asking.

Report file: {OUT}\r5_audit.md.
```
