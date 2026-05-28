# Reference: Changelist Description Standard

Extracted from `perforce-changelist-standard.md` for the `perforce-changelist-description` skill.

---

## Required Format

```
[TICKET][Non-technical summary]

Problem/context sentence.

Changes:
- First change
- Second change

#review
```

### Components

| Part | Required | Rules |
|------|----------|-------|
| `[TICKET]` | Yes | Jira ticket ID in brackets. Uppercase prefix, hyphen, digits. e.g., `[PROJ-1234]` |
| `[Non-tech summary]` | Yes | Plain-language summary describing the BENEFIT, not implementation. Must be understandable by producers/designers. |
| Problem/context | Yes | One sentence explaining what was hard/broken/missing BEFORE this change. |
| Changes list | Yes | Bullet list of what was done. Technical terms OK here. |
| `#review` | Yes | Triggers Swarm notification. Must be on its own line at the end. |

## Non-Technical Summary Quality Rules

The summary must describe the BENEFIT, not the implementation. Ask: "If a producer asked 'what does this do?' — what would I say?"

### Reframe to Benefits

| Technical | Better |
|-----------|--------|
| "Show wave event in debug views" | "Easier debugging of AI behavior" |
| "Add getters for crouch state" | "Better visibility into bot movement issues" |
| "Refactored capsule sweep" | "Fix player getting stuck on ledges" |

### Forbidden in Summary

- Class, function, or variable names (e.g., `UMyComponent`, `OnRep_Health`)
- File paths or extensions (e.g., `.cpp`, `Source/`)
- Code patterns (e.g., `nullptr`, `TArray`, `const`, `override`, `refactor`)
- Engineering-only acronyms (e.g., `GAS`, `RPC`, `CDO`, `UBT`)

**Good examples:**
- "Fix player getting stuck on ledges"
- "Add daily login rewards"
- "Easier debugging of AI behavior"

**Bad examples:**
- "Refactored capsule sweep to two-pass" (describes implementation)
- "Fix nullptr crash in OnRep_Health" (code identifiers)
- "Show wave event in debug views" (jargon, not benefit)

## Full Examples

**Good:**
```
[GAME-451][Fix player getting stuck on ledges]

Previous single-pass collision sweep missed narrow ledge lips.

Changes:
- Capsule sweep now uses two-pass trace
- First pass: reduced radius for tight geometry
- Fallback: full radius if first pass fails

#review
```

**Bad -- wall of text, jargon in summary:**
```
[GAME-451][Adjusted capsule collision sweep to use two-pass trace] First with reduced radius for tight geometry, fallback to full radius. Previous single-pass approach missed narrow ledge lips. #review
```

**Bad -- missing non-tech summary:**
```
[GAME-451] Refactored UCapsuleMovementComponent sweep logic to use two-pass trace #review
```

## Validation Severity

| Severity | Condition |
|----------|-----------|
| **BLOCK** | Missing ticket, ticket does not exist, missing non-tech summary, missing `#review` |
| **BLOCK** | Single paragraph (no line breaks) — must use structured format |
| **WARNING** | Non-tech summary describes implementation instead of benefit |
| **WARNING** | Missing problem/context sentence before Changes list |
| **INFO** | Minor wording suggestions, scope creep detected |

## Jira Linkage

- Every CL must reference a Jira ticket
- If none exists, ask the user to create one before proceeding
- Multiple CLs can reference the same ticket
- Use Jira MCP tools to fetch ticket context (summary, acceptance criteria)

## Setting the Description via CLI

Use `p4 change -i` with a HEREDOC. Description lines must be tab-indented.

## Stream Discipline

- Never work directly on the mainline stream
- Create a task or development stream for each piece of work
- Merge/copy changes up through streams — do not cherry-pick manually
