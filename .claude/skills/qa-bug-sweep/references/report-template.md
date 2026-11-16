# Report template

Fill in and write to `report.md`. Leave out a section that would be empty,
except "Not reviewed", which always appears.

```markdown
# QA Bug Sweep: {since} → {until} ({N}d, {{P4_STREAM}})

**Start here:** {one line: the single bug to hand QA first, and why}

| Severity | New | Ticketed | Regressed | Related |
|----------|-----|----------|-----------|---------|
| Crash    | …   | …        | …         | …       |
| Blocker  | …   | …        | …         | …       |
| Major    | …   | …        | …         | …       |
| Minor    | …   | …        | …         | …       |

Reviewed {code CL count} code CLs in {batch count} batches. Verifier rejected
{n} of {m} raw findings. Workspace at CL {have}{, behind window if so}.

## Bugs

### 1. {Title: what the tester sees}
**{Severity}** · {confirmed|likely} · Jira: {new | {{JIRA_PROJECT_KEY}}-n (ticketed/regressed/related)}
CL {n} ({user}){, with CL m} · `{file}:{line}`

**Repro**
1. …
2. …

**Expected:** …
**Actual:** …
**Why:** {≤2 lines}

### 2. …

## Not reviewed: asset-only CLs ({count})

| CL | Author | What it changes | Risk note |
|----|--------|-----------------|-----------|
| … | … | {first line of description} | {one line, or "–"; flag overlap with reviewed code CLs} |

## Skipped

- Tooling/automation-only: {count} CLs ({list})
- Other (build scripts, docs, binaries): {count} CLs
- Bots: {count} CLs

## Rejected by verifier

- {id} CL {n}: {title} ({reason})
```
