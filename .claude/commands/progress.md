---
description: Show project progress — files, tests, recent git activity, and next actions
scope: project
allowed-tools: Read, Glob, Bash(git log:*), Bash(find:*), Bash(wc:*)
---

# Project Progress

Check the actual state of all components and report status.

## Instructions

1. Read `@docs/ARCHITECTURE.md` for project context (if it exists)
2. Detect the project type from files present (see below)
3. Check source and test file counts
4. Check recent git activity

## Project Type Detection

```bash
# Detect language/stack from root files
ls -1 package.json pyproject.toml Cargo.toml go.mod *.csproj *.sln CMakeLists.txt 2>/dev/null
```

## Source and Test Counts

```bash
echo "=== Source Files ==="
# Adjust extensions to match detected project type
find . -not -path './.git/*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' \
  \( -name "*.py" -o -name "*.rs" -o -name "*.ts" -o -name "*.tsx" -o -name "*.go" \
     -o -name "*.cpp" -o -name "*.cs" -o -name "*.java" \) 2>/dev/null | head -30

echo ""
echo "=== Test Files ==="
find . -not -path './.git/*' -not -path '*/node_modules/*' \
  \( -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" -o -name "*_test.go" \
     -o -name "*Tests.cs" -o -name "*_test.rs" \) 2>/dev/null | head -30

echo ""
echo "=== Recent Activity (Last 7 Days) ==="
git log --oneline --since="7 days ago" 2>/dev/null | head -15 || echo "No recent commits"
```

## Output Format

| Area          | Files   | Status | Notes |
| ------------- | ------- | ------ | ----- |
| Source code   | N files | ...    | ...   |
| Tests         | N files | ...    | ...   |
| Documentation | ...     | ...    | ...   |

### Next Actions (Priority Order)

Based on what's present and what's missing, suggest the top 3 next actions:

1. ...
2. ...
3. ...
