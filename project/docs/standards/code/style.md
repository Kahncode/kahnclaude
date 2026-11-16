# Style

Does this code follow project conventions?

Do not flag personal style preferences — only project standards.

**Critical rule**: Style must match the NEIGHBOR code style, not just global rules. If the surrounding file uses a consistent pattern, new code must follow that pattern even if it differs from the global standard.

## Naming Conventions

Follow the project's established naming conventions. Common patterns:

| Convention | Example | Typical usage |
|------------|---------|---------------|
| PascalCase | `UserAccount`, `GetData` | Classes, methods |
| camelCase | `userName`, `getData` | Variables, functions (JS/TS) |
| snake_case | `user_name`, `get_data` | Variables, functions (Python, Rust) |
| SCREAMING_SNAKE | `MAX_SIZE`, `API_KEY` | Constants, env vars |

## Naming Clarity

Names must communicate intent without requiring context lookup.

**Flags:**
- Single-letter variables outside loop indices
- Abbreviations that aren't universally known (`mgr`, `impl`, `ctx`)
- Generic names (`data`, `info`, `item`, `value`, `temp`)
- Names that don't match what the thing does

**Ask:** "Would a new team member understand this name without reading the implementation?"

## Comments

Comments should explain **why**, never **what** (the code shows what).

**Flags:**
- Stale comments that contradict the code
- Comments that restate the code (`// increment counter` above `counter++`)
- Commented-out code blocks (delete or explain why kept)
- Missing context on non-obvious workarounds

**Ask:** "Does this comment add information the code doesn't already convey?"

## Code Formatting

Follow the project's formatter configuration. Common standards:
- Consistent indentation (tabs or spaces, pick one)
- Consistent brace style
- No trailing whitespace
- Blank lines between logical sections

## Import/Include Order

Follow a consistent order:
1. Standard library / builtin
2. Third-party libraries
3. Project modules
4. Local/relative imports

Group by category with blank lines between groups.

## Modern Language Features

- Use `auto`/`var`/type inference only when the type is obvious from context
- Prefer range-based iteration when clearer
- Mark overrides explicitly
- Use `Optional<T>` or `Result<T, E>` over sentinel values

## Inclusive Terminology

| Avoid | Use instead |
|-------|------------|
| `whitelist` / `blacklist` | `allowlist` / `blocklist` |
| `master` / `slave` | `primary` / `secondary` |

Apply to: variable names, comments, log messages, UI strings, documentation.

---

## Unnecessary Complexity [WARNING]

**Flags:**
- Nested conditionals that could be flattened with early returns
- Boolean logic that could be simplified (`if (x) return true; else return false;`)
- State machines for linear flows
- Multiple variables tracking the same state

**Fix:** Extract guard clauses, flatten nesting, use direct returns.

## Clever Code [WARNING]

**Flags:**
- One-liners that pack multiple operations (ternary chains, compound assignments)
- Bitwise tricks when arithmetic is clearer
- Regex when simple string operations work
- Implicit behavior relying on obscure language features

**Ask:** "Will a new team member understand this immediately?"

## Deep Nesting [WARNING]

**Flags:**
- More than 3 levels of indentation (excluding class/function scope)
- Nested loops with nested conditionals
- Callback pyramids or nested lambdas

**Fix:** Guard clauses for early exit, extract inner blocks to named functions.

## Long Chains [INFO]

**Flags:**
- More than 4 chained method calls
- Chains where intermediate values might need inspection

**Fix:** Assign intermediate results to named variables.

## Defensive Overkill [INFO]

Validating invariants that cannot be violated by design.

**Flags:**
- Null checks after infallible construction
- Range checks on enum values
- Type checks after guaranteed cast

**Ask:** "Can this condition actually fail in practice?"

**Fix:** Remove checks that cannot fail. Add checks only at system boundaries.

---

## Severity Classification

- **CRITICAL**: None typical for style
- **WARNING**: Inconsistent naming, wrong import order, deep nesting
- **INFO**: Formatting suggestions, naming improvements
