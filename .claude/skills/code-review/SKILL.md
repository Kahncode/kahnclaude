---
name: Code Review
description: Comprehensive code review with security, performance, and best practices focus
triggers:
  - review
  - audit
  - check code
  - security review
---

# Code Review Skill

When reviewing code, follow this systematic approach:

## 1. Security (FIRST — always check)

- [ ] No hardcoded secrets, API keys, or passwords
- [ ] Input validation on all user-provided data
- [ ] SQL/command injection prevention (parameterized queries, no string concatenation)
- [ ] XSS prevention (output properly escaped)
- [ ] Authentication and authorization checks on protected operations
- [ ] CORS properly configured (if applicable)
- [ ] Rate limiting on public endpoints (if applicable)

## 2. Error Handling

- [ ] Try/catch or error returns around all I/O and external calls
- [ ] Errors logged with context (not swallowed silently)
- [ ] User-facing error messages are helpful (not internal stack traces)
- [ ] Unhandled promise rejections or panics are caught at the top level

## 3. Performance

- [ ] No N+1 query patterns
- [ ] Proper pagination on list operations
- [ ] No memory or resource leaks (resources closed, listeners cleaned up)
- [ ] Database indexes exist for common query fields
- [ ] Independent async operations parallelized where possible

## 4. Testing

- [ ] New code has corresponding tests
- [ ] Tests have explicit assertions (not just "it ran without error")
- [ ] Edge cases covered (empty input, null, boundary values)
- [ ] Mocks are realistic — test the right behavior, not implementation details

## 5. Architecture

- [ ] Follow architectural rules from `CLAUDE.md`, `docs/ARCHITECTURE.md` and relevant files
- [ ] No circular dependencies
- [ ] File size within project limits (check `CLAUDE.md` for limits)
- [ ] Function size within project limits

## Output Format

For each issue:

- **Severity**: Critical | Warning | Suggestion
- **Location**: file:line
- **Issue**: What's wrong
- **Fix**: How to fix it
- **Why**: Why this matters

End with: X critical, Y warnings, Z suggestions.
