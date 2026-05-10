---
description: Show project progress — files, tests, recent P4 activity, and next actions
scope: project
allowed-tools: Read, Glob, Bash(p4 changes:*), Bash(p4 opened:*), Bash(p4 info:*), Bash(find:*), Bash(wc:*)
---

# Project Progress

Check the actual state of all components and report status.

## Instructions

1. Read `@docs/ARCHITECTURE.md` for project context (if it exists)
2. Detect the project type from files present (see below)
3. Check source and test file counts
4. Check recent Perforce activity

## Project Type Detection

```bash
# Detect language/stack from root files
ls -1 *.uproject *.sln *.csproj package.json pyproject.toml Cargo.toml go.mod CMakeLists.txt 2>/dev/null
```

## Source and Test Counts

```bash
echo "=== Source Files ==="
# Adjust extensions to match detected project type
find . -not -path './.git/*' -not -path '*/Intermediate/*' -not -path '*/Saved/*' \
  -not -path '*/Binaries/*' -not -path '*/DerivedDataCache/*' \
  \( -name "*.h" -o -name "*.cpp" -o -name "*.hpp" -o -name "*.inl" \
     -o -name "*.py" -o -name "*.rs" -o -name "*.ts" -o -name "*.cs" \
     -o -name "*.go" -o -name "*.java" \) 2>/dev/null | head -30

echo ""
echo "=== Test Files ==="
find . -not -path './.git/*' -not -path '*/Intermediate/*' \
  \( -name "*.test.*" -o -name "*.spec.*" -o -name "test_*.py" -o -name "*_test.go" \
     -o -name "*Tests.cpp" -o -name "*Test.cpp" -o -name "*_test.rs" \) 2>/dev/null | head -30
```

## Perforce Activity

```bash
echo ""
echo "=== Recent Submitted Changes (Last 15) ==="
p4 changes -m 15 -u $P4USER -s submitted 2>/dev/null || echo "No recent submissions"

echo ""
echo "=== Pending Changelists ==="
p4 changes -s pending -u $P4USER -c $P4CLIENT 2>/dev/null || echo "No pending changelists"

echo ""
echo "=== Currently Opened Files ==="
p4 opened 2>/dev/null | head -20 || echo "No files currently opened"
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
