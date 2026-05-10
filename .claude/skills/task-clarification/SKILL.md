---
name: task-clarification
description: "Requirements clarification expert. ALWAYS invoke when the user asks to clarify a task, break down requirements, or structure a ticket. Do not write Jira descriptions directly — this skill produces structured breakdowns with acceptance criteria and confidence levels."
allowed-tools: Read, Grep, Glob
---

# Clarify Task Description

Use PROACTIVELY when the user says: `clarify task`, `clarify ticket`, `clarify requirements`.

## Reference

See @docs/standards/planning/task-clarification.md for acceptance criteria patterns, ambiguity checklist, and Jira-ready formatting.

## Purpose

Takes a raw, unstructured task description and produces a structured breakdown ready for copy-paste into Jira or any ticket system. No Jira API access -- pure text transformation.

## Input

Raw task description text from any source: verbal notes, Slack messages, meeting notes, rough ideas.

## Flow

### 1. Analyze the Raw Input

Read the task description and identify:
- Core intent (what needs to happen)
- Missing context (who, why, when, where)
- Ambiguous terms (vague scope, undefined boundaries)
- Implicit assumptions the author may be making

### 2. Ask Clarifying Questions

Ask focused questions about detected ambiguities. Ask ONE question at a time. Focus on:
- Scope boundaries ("Does X include Y?")
- Success criteria ("How will you know this is done?")
- Edge cases ("What happens when Z?")
- Dependencies ("Does this require A to be done first?")

### 3. Produce Structured Output

Format the result as a Jira-ready text block:

```markdown
## Context

[Why this work is needed -- the user problem and business impact]

## Task

[Specific, scoped work to be done]

## Acceptance Criteria

- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## Assumptions

- [Assumption 1] (confidence: high/medium/low)
- [Assumption 2] (confidence: high/medium/low)

## Out of Scope

- [Explicitly excluded item 1]
- [Explicitly excluded item 2]
```

### 4. Review with User

Present the structured output and ask: "Does this capture it correctly? Anything to adjust?"

Iterate until the user is satisfied.

### 5. Output Routing

After the user approves the structured output, offer next steps:

- **Done** — just display it here (default)
- **Implement** — hand off to `/task-implementation` with the approved structured output as input. task-implementation will skip its own clarification (Step 0) since the requirements are already structured, and proceed directly to classifying the work type.
- **Create Jira ticket** — hand off to the `producer` agent (subagent_type: `producer`) with the approved structured output as input. The producer will handle dependency analysis, estimation, and Jira creation — skip its own clarification steps since the requirements are already structured.

## Rules

- No external API calls in Steps 1-4 -- this is a pure text-processing skill
- Ask ONE clarifying question at a time (remote control compatibility)
- Every acceptance criterion must be testable and specific
- Always include confidence levels on assumptions
- Always include an "Out of Scope" section to prevent scope creep
- Output must be copy-paste ready for Jira description field
