# Reference: Changelist Description Standard

Extracted from `perforce-changelist-standard.md` for the `perforce-changelist-description` skill.

---

## Required Format

```
[TICKET][Non-technical summary] Technical description #review
```

### Components

| Part | Required | Rules |
|------|----------|-------|
| `[TICKET]` | Yes | Jira ticket ID in brackets. Uppercase prefix, hyphen, digits. e.g., `[PROJ-1234]` |
| `[Non-tech summary]` | Yes | Plain-language summary understandable by non-engineers. Describes user-facing or business impact. |
| Tech description | Yes | Technical explanation of what changed and why. Must explain reasoning, not just list changes. |
| `#review` | Yes | Triggers Swarm notification. MANDATORY on every CL. |

## Non-Technical Summary Quality Rules

The summary must be understandable by producers, designers, and stakeholders. It must NOT contain:

- Class, function, or variable names (e.g., `UMyComponent`, `OnRep_Health`)
- File paths or extensions (e.g., `.cpp`, `Source/`)
- Code patterns (e.g., `nullptr`, `TArray`, `const`, `override`, `refactor`)
- Engineering-only acronyms (e.g., `GAS`, `RPC`, `CDO`, `UBT`)

**Good examples:**
- "Fix player getting stuck on ledges"
- "Add daily login rewards"
- "Reduce loading time on main menu"

**Bad examples:**
- "Refactored capsule sweep to two-pass" (jargon)
- "Fix nullptr crash in OnRep_Health" (code identifiers)

## Full Examples

**Good:**
```
[GAME-451][Fix player getting stuck on ledges] Adjusted capsule collision sweep to use a two-pass trace -- first with reduced radius for tight geometry, fallback to full radius. Previous single-pass approach missed narrow ledge lips. #review
```

**Bad -- missing non-tech summary:**
```
[GAME-451] Refactored UCapsuleMovementComponent sweep logic to use two-pass trace #review
```

## Validation Severity

| Severity | Condition |
|----------|-----------|
| **BLOCK** | Missing ticket, ticket does not exist, missing non-tech summary, missing `#review` |
| **WARNING** | Non-tech summary contains jargon, tech description lacks reasoning |
| **INFO** | Minor wording suggestions, scope creep detected |

## Jira Linkage

- Every CL must reference a Jira ticket
- If none exists, ask the user to create one before proceeding
- Multiple CLs can reference the same ticket
- Use Jira MCP tools to fetch ticket context (summary, acceptance criteria)

## Setting the Description via CLI

```bash
# Get the change spec, modify description, pipe back
p4 change -o <CL#> | <modify description> | p4 change -i
```

The `p4 change -i` command reads a change specification from stdin and updates the changelist.

## Stream Discipline

- Never work directly on the mainline stream
- Create a task or development stream for each piece of work
- Merge/copy changes up through streams — do not cherry-pick manually
