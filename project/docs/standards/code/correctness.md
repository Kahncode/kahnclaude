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
- **Stale references** — using pointer after object destruction
- **Invalid casts** — `Cast<T>()` without checking return
- **Uninitialized** — using variables before assignment

### Edge Cases
- **Empty collections** — calling `[0]` on empty array, `First()` on empty
- **Boundary values** — INT_MAX, zero, negative, empty string
- **Missing cases** — switch without default, enum additions not handled
- **Error paths** — what happens when the operation fails?

### Concurrency (if applicable)
- **Race conditions** — shared state without synchronization
- **Deadlocks** — lock ordering violations
- **Lost updates** — check-then-act without atomicity

## UE5-Specific

### Null-Prone Patterns
Always null-check results from:
- `Cast<T>()` — returns nullptr if cast fails
- `FindComponentByClass<T>()` — nullptr if not found
- `GetWorld()` — nullptr during shutdown
- `GetOwner()` — nullptr if orphaned
- `TWeakObjectPtr::Get()` — nullptr if collected
- `GetPlayerController(0)` — nullptr on dedicated server
- `GetGameInstance()` — nullptr in editor previews

### Lifecycle Errors
- Using `this` in constructor (object not fully constructed)
- Accessing other actors in `BeginPlay` (they may not have begun play)
- Storing raw pointers to UObjects (GC can collect them)
- Not checking `IsValid()` on `TWeakObjectPtr` before use

### Replication Bugs
- Server-only logic running on client
- Client-only logic affecting server state
- Missing `COND_` checks on replicated properties
- Authority checks (`HasAuthority()`) missing

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
