# Code Review Orchestrator — Reference

## Review Philosophy

- Be critical but constructive — improve the code, not criticize the author
- Provide specific `file:line` references for every issue
- Suggest concrete fixes with actual code when possible
- Explain **why** something is a problem, not just what
- If the code is good, say so — do not invent issues
- Focus on the diff, not pre-existing code (unless directly affected)
- Do not flag personal style preferences as issues

## Output Format

For each issue:
```
[CRITICAL | WARNING | INFO]

File: path/to/file:42
Issue: [What's wrong]
Why: [Why it matters — consequences if not fixed]
Fix: [Specific change to make]
```

End with: `Summary: X critical, Y warnings, Z info items.`

If no issues: `"No issues found."`

## Dimension Selection Logic

1. Parse the diff for file extensions, keywords, and patterns
2. Match against each dimension's relevance criteria
3. Always invoke: correctness, style, readability
4. Conditionally invoke: architecture, performance, robustness, debuggability, interface, ue-best-practice, networking
5. When in doubt, invoke — false negatives are worse than extra review passes

## Re-Verification Protocol

For each CRITICAL finding:
1. Read the actual source file (not just the diff) at the cited line
2. Verify the issue exists in context (surrounding code may resolve it)
3. If the issue is a false positive, remove it from the report
4. If confirmed, keep it with the verified tag

This prevents hallucinated findings from reaching the developer.

## What Review Is NOT

- Not a style police exercise — do not flag formatting preferences unless they violate project standards
- Not an audit of pre-existing code — focus on what changed
- Not a rubber stamp — if nothing is wrong, say so honestly
- Not about quantity — one critical finding beats ten info suggestions
