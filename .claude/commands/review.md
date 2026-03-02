---
description: Review code changes for bugs, security issues, and best practices
scope: project
allowed-tools: Read, Grep, Glob, Bash(git diff:*), Bash(git branch:*)
---

# Code Review

Review the current changes.

## Branch Context

```bash
git branch --show-current
```

Report which branch is being reviewed in the output header. Review is read-only — no branch is created, but warn if on `main` or `master`.

## Context

- Current diff: !`git diff HEAD`
- Staged changes: !`git diff --cached`

## Review Checklist

1. **Security** — OWASP Top 10, no hardcoded secrets, proper input validation, injection prevention
2. **Error Handling** — No swallowed errors, errors logged with context, user-facing messages are helpful
3. **Performance** — No N+1 queries, no memory leaks, proper pagination
4. **Testing** — New code has tests, tests have explicit assertions, edge cases covered
5. **Architecture** — Service separation respected, no business logic in route handlers, no circular dependencies
6. **Dead Code** — No commented-out blocks, no unreachable code, no unused imports

## Output Format

For each issue found:
- **File**: path/to/file:line
- **Severity**: Critical | Warning | Suggestion
- **Issue**: Description
- **Fix**: Suggested change

End with a summary: X critical, Y warnings, Z suggestions.

If no issues: "No issues found."
