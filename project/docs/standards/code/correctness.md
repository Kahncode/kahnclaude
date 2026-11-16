# Correctness

Does this code actually work?

This is the most important review dimension. A well-architected, performant, beautifully-styled piece of code is worthless if it has a logic bug.

## Criteria

### Logic Errors
- **Wrong comparisons** — `<` vs `<=`, `==` vs `!=`, inverted conditions
- **Off-by-one** — loop bounds, array indices, range calculations
- **State machine errors** — missing transitions, unreachable states, stuck states
- **Boolean logic** — De Morgan violations, short-circuit assumptions, precedence errors
- **Numeric** — overflow, underflow, division by zero, float comparison with `==`

### Null/Invalid References
- **Unchecked pointers** — dereferencing without null check
- **Stale references** — using pointer/reference after object destruction
- **Invalid casts** — downcasting without checking success
- **Uninitialized** — using variables before assignment

### Edge Cases
- **Empty collections** — accessing index 0 on empty array, `first()` on empty
- **Boundary values** — INT_MAX, zero, negative, empty string
- **Missing cases** — switch without default, enum additions not handled
- **Error paths** — what happens when the operation fails?

### Concurrency (if applicable)
- **Race conditions** — shared state without synchronization
- **Deadlocks** — lock ordering violations
- **Lost updates** — check-then-act without atomicity

## Common Null-Prone Patterns

Always null-check results from:
- Type casting/conversion operations
- Collection lookups (`find`, `get`, `lookup`)
- Optional unwrapping
- Weak reference dereferencing
- Service/dependency lookups
- Resource loading/fetching

### Lifecycle Errors
- Using `this` in constructor (object not fully constructed)
- Accessing dependencies during initialization (they may not be ready)
- Storing raw pointers/references to managed objects (they may be collected/freed)
- Not checking validity before using weak references

## Review Process

For each function modified:

1. **Read the function's purpose** — what should it do?
2. **Trace all code paths** — what happens in each branch?
3. **Check boundary conditions** — empty, null, zero, max
4. **Verify error handling** — what if something fails?
5. **Cross-reference callers** — is the function used correctly?

## What to Look For in Diffs

- **Changed conditions** — did the logic invert correctly?
- **New parameters** — are they validated? defaulted safely?
- **Removed code** — was it actually dead, or needed?
- **Added loops** — correct bounds? early exit conditions?

---

## Severity Classification

- **CRITICAL**: Null deref, use-after-free, infinite loop, data corruption, crash path
- **WARNING**: Off-by-one likely to hit, missing edge case handling, logic that "usually works"
- **INFO**: Defensive suggestions, potential future edge cases
