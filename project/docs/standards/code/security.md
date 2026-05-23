# Security

Is this code safe from attack?

## Security Criteria

- **Input validation** on user-provided data and external API responses
- **SQL/command injection** — string concatenation in queries
- **XSS** — unescaped output rendered in UI
- **Hardcoded secrets** — API keys, passwords, tokens in code
- **Missing auth/authz** checks on protected operations
- **Unsafe deserialization** of untrusted data

## Correctness Criteria

- **Edge cases** not handled
- **Off-by-one errors** in loops/indices
- **Null/nullptr dereferences** (especially unchecked `Cast<T>()`)
- **Race conditions** and thread safety issues
- **Wrong comparisons** or logic errors

## Null-Prone UE5 Patterns

Always null-check results from:
- `FindComponentByClass<T>()` — nullptr if component missing
- `GetWorld()` — can be null during shutdown
- `GetOwner()` — can be null if component is orphaned
- `TWeakObjectPtr::Get()` — can be null if object was collected
- `GetPlayerController(0)` — null on dedicated server
- `Cast<T>()` — null if cast fails

---

## Severity Classification

- **CRITICAL**: Server RPC without validation, hardcoded secrets, SQL/command injection
- **WARNING**: Missing input validation, unsafe deserialization, missing auth checks
- **INFO**: XSS prevention opportunities, tighter access controls
