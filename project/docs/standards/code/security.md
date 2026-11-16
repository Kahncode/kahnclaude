# Security

Is this code safe from attack?

## Security Criteria

- **Input validation** on user-provided data and external API responses
- **SQL/command injection** — string concatenation in queries
- **XSS** — unescaped output rendered in UI
- **Hardcoded secrets** — API keys, passwords, tokens in code
- **Missing auth/authz** checks on protected operations
- **Unsafe deserialization** of untrusted data
- **Path traversal** — user input in file paths without sanitization
- **CORS misconfiguration** — overly permissive cross-origin access

## Correctness Criteria (Security-Relevant)

- **Edge cases** not handled — may lead to unexpected behavior
- **Off-by-one errors** in loops/indices
- **Null/undefined dereferences** — unchecked optional values
- **Race conditions** and thread safety issues
- **Wrong comparisons** or logic errors in auth checks

## Common Null-Prone Patterns

Always null-check results from:
- Type casting/conversion operations
- Collection lookups and find operations
- Weak reference dereferencing
- Service/dependency lookups
- Resource loading/fetching
- User session/context lookups

---

## Severity Classification

- **CRITICAL**: RPC/API without validation, hardcoded secrets, SQL/command injection, missing auth on sensitive endpoints
- **WARNING**: Missing input validation, unsafe deserialization, missing authorization checks, path traversal
- **INFO**: XSS prevention opportunities, tighter access controls, CORS improvements
