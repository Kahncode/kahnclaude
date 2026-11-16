---
name: burn-tokens
description: "Spare-capacity planner. ALWAYS invoke when the user has tokens or quota left and wants big, useful ways to spend them: 'tokens to burn before reset', 'what can you grind on overnight', 'useful things to do with spare capacity'. Checks what is still open, returns 10 ranked work and growth ideas with sizes and a launch plan. Not for one known task (task-planning)."
allowed-tools: Read, Grep, Glob, Bash, PowerShell, Agent, Skill, Workflow, mcp__atlassian__searchJiraIssuesUsingJql
---

# Burn Tokens: spend spare capacity on things that matter

The user has budget left before a usage reset. Unspent budget is wasted, but busywork is worse because it eats their review time. The goal is **10 ideas where heavy token use buys real value**: work that is nearly done, problems too costly to attempt on a normal day, and learning that compounds.

A good list beats a generic one in three ways:
1. **It is grounded and current.** Every work idea names a real CL, ticket, crash or past estimate, and has been checked as still open. Suggesting work that was already shelved last week costs the user trust and a wasted session.
2. **It favours unattended work.** The user has tokens, not necessarily attention. Background agent loops (flake reruns, sweeps, build-and-test passes) are the best kind of burn. Ideas that need many mid-way decisions score lower.
3. **It makes a call.** Give one top pick and a concrete parallel plan, not a menu.

## Step 1: Freshness check (about 10–15 calls, mostly in parallel)

Memory is a snapshot and goes stale fast. Memory often lists CLs and tickets that have since landed or closed. Suggesting finished work wastes the user's session, so verify before suggesting.

**1a. Collect memory's claims.** The MEMORY.md index is already in context. Scan it for words that mark unfinished value: *owed, pending, unbuilt, UBT owed, shelve owed, Horde owed, repro owed, unproven, mechanism unknown, PAUSED, follow-ups*, plus past estimates or reviews whose results were never acted on. Note every CL number, {{JIRA_PROJECT_KEY}} key, and the oldest date among those entries. Open an individual memory file only when you need detail to describe an idea.

**1b. Check them (run in parallel):**
- **Who:** `p4 -ztag -F %userName% info`
- **Pending pile:** `p4 changes -s pending -u <user>` with no `-m` cap, then `p4 changes -s pending -u <user> -l -m 40` for descriptions of the newest. Users can have many pending CLs, so report the count and the oldest date, which can feed the tooling idea.
- **Memory's CLs (run this first):** `python -I -X utf8 $KC_PROJECT_ROOT/.claude/scripts/p4/memory_cl_status.py` (about 40 s). It resolves every CL that memory cites and prints PENDING (with opened/shelved counts), EMPTY, RENUMBERED (old → submitted number), GONE, the files that still claim a state for a landed CL, and archive candidates. Trust it over the memory text. Perforce gives a pending CL a **new number when it is submitted**. For a single number, `p4 -ztag describe -s -O <n1> <n2> …` returns the submitted `change` and its `oldChange`.
- **Jira, open work:** `mcp__atlassian__searchJiraIssuesUsingJql` with cloud ID `{{JIRA_CLOUD_ID}}`, JQL `assignee = currentUser() AND statusCategory != Done AND updated >= -60d ORDER BY priority DESC, updated DESC`, `maxResults: 50` (the tool's minimum), fields `summary,status,priority`.
- **Jira, memory's tickets:** a second JQL `key in (<every {{JIRA_PROJECT_KEY}} key from 1a>)`, same fields. The open-work query can't tell you that a ticket memory still treats as live has closed.

If a Jira result overflows to a file, parse it with Python. Call `sys.stdout.reconfigure(encoding='utf-8')` first: Windows stdout is cp1252, and `python -I` ignores `PYTHONIOENCODING`.

Don't check pending shelves separately: `p4 changes -s shelved` only returns the same pending CLs again.

**1c. Reconcile.** Trust p4 and Jira over memory. Drop ideas whose work has landed or closed. Put the mismatches in one line of the output ("memory stale: 1234→1240, {{JIRA_PROJECT_KEY}}-123 Closed"). If a lot of memory is stale, that becomes a strong tooling idea. Parallel sessions share the workspace, so also expect files to have moved between CLs.

**Unverifiable items** (Sentry-only crashes, Horde state, anything outside p4/Jira) can still be suggested. Label them "status from memory <date>, unchecked" so the user knows to confirm first.

Don't go deeper than this (no Horde, Discord, Sentry or Confluence scans). This step informs the list. It is not the burn.

## Step 2: Build the 10 ideas

Target mix: **about 5 growth, 4 work, 1 tooling.** Shift the mix if the user names a focus ("only work", "learning day").

### Work ideas (about 4): the most value per token
Rank candidates in this order:
1. **Almost done → shipped.** CLs that only lack a build, the affected tests or a shelve. Cheap, certain value. Bundle several into one idea ("clear the owed backlog: CLs A, B, C").
2. **Open crashes and unproven root causes.** These suit `/diagnose` loops and 200-run repros (rare repros need about 200 runs).
3. **Sweeps nobody has time for:** `/qa-bug-sweep Nd`, test-feasibility over open bugs, writing the tests a past feasibility review called testable.
4. **Scoped wins already estimated** in memory (speedups, drift fixes) that were never implemented. If an old feasibility report's bugs have since been fixed, its tests are still worth writing as regression guards. Say that's the purpose, or propose a fresh feasibility run if most of its picks have gone stale.

### Growth ideas (about 5): learning that pays back at work
Assume a UE5 engineer (C++, gameplay, replication, automation, Perforce/CI); adjust to the user's actual role. The best growth ideas use **live work as the textbook**, so the learning also moves a real problem forward. Draw from these, and vary them across runs:

- **Engine deep-dive behind an open bug:** an `/illustrate` page on the engine subsystem a current crash runs through (subobject replication, push-model dirtying, GAS prediction keys, ReplicationGraph, streaming/GC). Cite real engine file:line.
- **Teach-back / quiz:** Claude writes a 10-question quiz on a system the user touched this month, the user answers, and Claude grades with code references. Strong for retention.
- **Design defence:** `/grill-me` on a design the user owns or is about to propose.
- **Architecture study:** `/improve-codebase-architecture` on one subsystem, read as a learning exercise rather than a refactor order.
- **Craft:** a modern-C++/UE idiom study using real diffs from the user's recent CLs (what a senior reviewer would change and why).
- **Comparative reading:** how Lyra or Epic's sample projects solve a problem this project solved differently, and what's worth adopting.
- **Leverage and career:** turn a recent hard-won fix into a team tech talk or Confluence onboarding page (`/confluence-user-guide`, `/create-tutorial`), or draft a proposal/ADR for an improvement the user keeps working around.
- **Tool fluency:** `/latest-updates-info` on Claude Code, UE or Horde, followed by one concrete adoption in the user's own workflow.

Say what the user will be able to do afterwards ("you'll be able to read a replication crash dump unaided"), not just the topic.

### Tooling idea (1)
Something that cuts the cost of every future session: memory consolidation (archive submitted items, merge duplicate Horde entries, verify statuses against p4), skill follow-ups noted in memory, `/fewer-permission-prompts`, or a new skill for a workflow the user keeps repeating.

### Filters
- **Not busywork.** If the output is something nobody will read or ship, drop it.
- **Respect the project rules:** never submit (shelving is fine), no Engine/ edits without approval, and ask before widening scope.
- Don't suggest anything memory marks as done, abandoned or "not code" unless the user can act on it.
- Each idea should be worth at least ~100k tokens. Small chores can be folded into a bundle idea.

## Step 3: Output

Skimmable shape: next action first, short lines, numbered. Use this structure:

```
**Top pick:** #N + #M — <one line why>.
<one line on any memory/p4 mismatches found, if any>

### Work
1. **<Title>** — <what and why now, citing CL#/ticket>. `<skill/agent>` · <S/M/L/XL> · <background|foreground>
...
### Growth
<continue numbering> **<Title>** — <what> → *you'll be able to <outcome>*. `<skill>` · <size> · <bg|fg>
...
### Tooling
10. ...

**Parallel plan:** background: #a, #b · workflow: #c · foreground with you: #d.
Reply with numbers to start.
```

Number the ideas continuously from 1 to 10, whatever the section split.

Token sizes: S < 100k, M 100–300k, L 300k–1M, XL > 1M. Pick one size; a range like "M-L" means you haven't decided.

**Background vs. workflow:** a *background* idea is one agent or one skill running on its own. A *workflow* idea fans out into several agents that run in parallel and get verified, like a multi-CL sweep or a per-system review. Launch it through a skill that already orchestrates (e.g. `/qa-bug-sweep`) or the Workflow tool, keeping under 10 agents.

## Step 4: Launch what the user picks

Once the user replies with numbers, start them; don't re-confirm the list.

- **Background work** (builds, test loops, repros, sweeps): spawn agents with `run_in_background`, or invoke the owning skill (`/diagnose`, `/qa-bug-sweep`, `unreal-project-compilation`, `swarm-review-shelve`). Brief each agent with the CL/ticket and the memory facts it needs. It starts with no context.
- **C++ changes** go through `code-planner` / `code-dev` / `code-reviewer` (never edit C++ directly).
- **Foreground growth** (quiz, grill-me, deep-dive reading): run it in this session with the user.
- Keep the main context lean. Delegate heavy reading so the conversation can host several ideas. If it grows long anyway, say so and suggest a fresh session for the next pick.
- When each finishes, report in the user's standard shape: **What I did / What to check / Next step**, and update the memory entries whose status changed.
