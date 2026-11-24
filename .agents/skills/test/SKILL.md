---
name: test
description: Generate tests for the specified file, function, or recently changed code by delegating to the test-writer agent.
scope: project
---

# Generate Tests

Delegate this task to the `test-writer` agent via the Agent tool.

Pass the following as context:
- The target from `$ARGUMENTS` (file path, function name, or "recently changed files" if no argument given)
- Any flags: `--unit`, `--integration`, `--edge`, `--coverage`

The agent will detect the test framework from the codebase, write tests following the AAA pattern with explicit assertions, and cover happy path, error cases, and edge cases.
