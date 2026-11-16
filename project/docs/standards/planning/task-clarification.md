# Task Clarification Reference

Patterns and checklists for turning raw task descriptions into structured, Jira-ready breakdowns.

---

## Acceptance Criteria Patterns

### Good Criteria (Specific, Testable, Measurable)

- "User can toggle dark mode from Settings > Display"
- "API returns 200 with valid JSON body containing `id` field"
- "Page load time under 2s on 3G connection"
- "Error message displays when form submitted with empty required fields"
- "Data persists across browser refresh"
- "Admin can export CSV with all columns from the filter view"

### Bad Criteria (Reject These)

- "Make it better" -- vague, no success condition
- "Should work correctly" -- untestable tautology
- "Improve performance" -- unmeasurable without a target
- "Handle edge cases" -- which ones?
- "Clean up the code" -- no definition of done

### Checkbox Format

Always use Jira-compatible checkbox syntax:
```
- [ ] Criterion text here
```

---

## Common Ambiguity Checklist

When analyzing a raw task, check for these common gaps:

### Scope Ambiguities
- [ ] Are the boundaries of the change defined? (which files, modules, pages)
- [ ] Is it clear what is NOT included?
- [ ] Are there multiple interpretations of the requirement?

### User Context
- [ ] Who is the user/actor performing this action?
- [ ] What is their starting state?
- [ ] What is their expected end state?

### Technical Context
- [ ] Are there platform/browser/device constraints?
- [ ] Are there performance requirements?
- [ ] Are there data migration or backward compatibility concerns?
- [ ] Are there security or permissions implications?

### Dependencies
- [ ] Does this depend on other work being completed first?
- [ ] Will other work be blocked until this is done?
- [ ] Are there external system dependencies (APIs, services)?

### Edge Cases
- [ ] What happens with empty/null input?
- [ ] What happens with very large input?
- [ ] What happens when the user cancels mid-flow?
- [ ] What happens during concurrent access?

---

## Jira-Ready Formatting

### Description Template

```markdown
## Context

[1-3 sentences: Why this work is needed. What user problem does it solve?]

## Task

[1-3 sentences: What specific work needs to be done. Keep scope tight.]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Assumptions

- [Assumption 1] (confidence: high)
- [Assumption 2] (confidence: medium)

## Out of Scope

- [Item 1]
- [Item 2]
```

### Assumption Confidence Levels

| Level | Meaning |
|-------|---------|
| **high** | Based on documented facts or direct confirmation |
| **medium** | Reasonable inference from context, but not confirmed |
| **low** | Best guess -- needs validation before implementation |

### Summary Line Rules

- Clear, imperative, max 100 characters
- Start with a verb: "Add", "Fix", "Update", "Remove", "Implement"
- Examples: "Add dark mode toggle to Settings page", "Fix N+1 queries in user listing endpoint"
