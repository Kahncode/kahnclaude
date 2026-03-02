---
name: import
description: Analyze a repository's Claude Code components and selectively integrate them into KahnClaude
scope: framework
---

Analyze a target repository for Claude Code components and selectively integrate them into
KahnClaude. The workflow has two hard phases separated by a plan approval gate:

- **Planning phase** — read-only analysis, ends with a written plan the user approves
- **Execution phase** — artifact-by-artifact integration, confirmed one at a time

**Never write any file during the planning phase.** Never batch-execute the plan without
per-artifact confirmation.

---

## Planning Phase

Use `EnterPlanMode` at the start. All steps in this phase are read-only.

### Step 1: Target Resolution

If the user hasn't provided a path or URL, ask:
> "What is the path or URL of the repository you want to import from?"

For a local path: explore it directly.
For a URL: ask the user to clone it locally first, then provide the path.

### Step 2: KahnClaude Inventory (Existing State)

Before touching the source repo, record what KahnClaude already has.
This is the baseline for duplicate detection throughout the plan.

Scan and record:
- `.claude/commands/*.md` and `.claude/commands/kc/*.md` — name, description, scope, what it does
- `.claude/skills/*/SKILL.md` — name, triggers, what it does
- `.claude/agents/*.md` — name, tools, specialization
- `.claude/hooks/*.py` — event, matcher, behavior
- `@.claude/settings.json` — hook wiring
- `@project/CLAUDE.md` and `@global/CLAUDE.md` — existing rules and patterns

### Step 3: Source Repository Discovery

> **CRITICAL — READ BEFORE STARTING THIS STEP:**
> Step 2 scanned KahnClaude (this framework). Step 3 scans the **source repo** — a
> completely different directory at the path provided in Step 1. Every file read, every
> path listed, and every artifact recorded in this step MUST come from that source path.
> **NEVER reference KahnClaude's own `.claude/` directory here.** If you catch yourself
> listing a path that does not start with the source repo path, stop and correct it.

Do not assume any particular structure. The source repo may organize things very
differently from KahnClaude or may not use Claude Code at all in a conventional way.

**Broad scan first** — all operations rooted at `<source-repo-path>`:

1. List all files in `<source-repo-path>/` (root only, not recursive)
2. If `<source-repo-path>/.claude/` exists, list its full contents recursively
3. Search for `CLAUDE.md` files at any depth under `<source-repo-path>/`
4. Search for `CLAUDE.local.md`, `settings.json` inside `.claude/`, or similar config files
5. Scan for Markdown files anywhere under `<source-repo-path>/` that might be commands,
   skills, or agents — look for YAML frontmatter with `name`, `description`, `triggers`,
   `tools`, or `scope` fields
6. Scan for Python, bash, or other scripts under `<source-repo-path>/` that read from
   stdin and exit with codes 0/1/2 (these may be hooks regardless of location)
7. Read `<source-repo-path>/README.md` and any docs about Claude Code usage
8. Look for memory-related files: `memory/` directories, `MEMORY.md`, or persistent-state
   instructions in any CLAUDE.md under `<source-repo-path>/`

**For each file found, record** — using full absolute paths from the source repo:
`{ type_guess, actual_path, name_if_any, description_if_any, language, raw_purpose }`

Do not force the source structure to match KahnClaude's layout. Classify what you find
based on what it actually does, not where it lives.

**After completing the scan**, present the full artifact list and confirm before proceeding.
Every path shown MUST be from the source repo, not from KahnClaude:

> "I found [N] artifact(s) in `<source-repo-path>`:
> - `<source-path/to/file>` ([type]) — [one-line description]
> - ...
>
> Are these the artifacts you intended to import? If not, describe what you're looking for
> and I'll search more broadly."

Wait for confirmation before continuing to Step 4. If the user says the artifacts don't
match their intent, re-run the discovery with the corrected target or search criteria.

### Step 4: Feature Synthesis

Group discovered artifacts into **features** — named capabilities, not individual files.
One feature may span multiple artifacts. Annotate each with its overlap against KahnClaude's
existing inventory from Step 2.

Feature format:
```
[N] Feature Name
    What it does: <one sentence>
    Artifacts: <list of source files — paths must be from the source repo, not KahnClaude>
    KahnClaude overlap: none | partial — <existing component> | full duplicate of <component>
```

Feature categories to consider (not exhaustive):
- Memory Management (cross-session persistence, auto-memory)
- Quality Gates (code review, lint-on-write, test generation)
- Security Enforcement (secrets scanning, file access blocking, dependency audit)
- Git Workflows (commit messages, PR creation, branch management)
- Agent Delegation (specialist subagents)
- Documentation (README gen, explanation, inline docs)
- Technology Support (language-specific or stack-specific components)
- Project Scaffolding (CLAUDE.md templates, onboarding)
- Hook Patterns (novel lifecycle enforcement)
- CI/CD Integration

After the feature list, add a **Recommendation** section:

```
Recommendation: Start here: N,M,...
  [N] Include — <one-line rationale>
  [M] Include — <one-line rationale>
  [X] Skip — <one-line rationale (full duplicate, proprietary, too specific, etc.)>
```

Then ask:
> "Which features do you want to integrate? Reply with numbers (e.g. `1,3,5`), `all`, or `none`.
> Recommendation above is a starting point — full duplicates are flagged but still selectable."

Wait for response.

### Step 5: Artifact Review List

From the selected features, list each artifact in detail.

For each artifact:
```
[N] <TYPE>  <name>
    Source:    <path in source repo>
    Does:      <one sentence>
    Duplicate: none | partial — <existing component> | full duplicate — <existing component>
    Action:    <see values below>
    Why:       <brief rationale for non-obvious actions — e.g. why rewrite vs adapt, why skip>
    Notes:     <key adaptation decisions>
```

**Action values:**
- `create` — no equivalent exists; add with KahnClaude conventions applied
- `adapt` — no duplicate, but needs rework (generalize, add frontmatter, restructure)
- `rewrite` — hook in a non-Python language; must be fully rewritten in Python
- `merge` — partially duplicates an existing component; extract novel parts only
- `replace` — full duplicate but user wants to replace the existing component
- `skip` — recommended skip (full duplicate with no novel value)

**Duplicate detection rules:**
- Same purpose or name → full duplicate
- Same hook event+matcher with overlapping behavior → partial duplicate
- Same CLAUDE.md rule covering the same constraint → partial duplicate
- Skill triggers that fire in the same context as an existing skill → partial duplicate

Present the list and ask:
> "Which artifacts should I integrate? Reply with numbers, `all`, or `skip N,M,...` to exclude some.
> For `merge` and `replace` actions I'll show the diff before writing anything."

Wait for response.

### Step 6: Integration Plan

Produce the full plan document:

```
INTEGRATION PLAN
================
Source: <repo name/path>
Artifacts to integrate: <N>

[N] <TYPE>  <name>
    Source:  <source path>
    Target:  <target path in KahnClaude>
    Action:  create | adapt | rewrite | merge | replace
    Changes:
      - <specific adaptation>
      - ...

Documentation updates:
  - README.md: add <X> to <table>
  - CONTRIBUTING.md: <only if new conventions introduced>
  - .claude/settings.json: <hook wiring, if any>

Skipped:
  - <name> — <reason>
```

Ask:
> "Does this plan look correct? Reply `yes` to begin, or describe changes you want first."

Revise and re-ask until the user explicitly approves. Then call `ExitPlanMode`.

---

## Execution Phase

Work through the approved plan **one artifact at a time**.
Do not write multiple files in sequence without confirmation between them, unless the user
explicitly says "do them all" or "integrate all".

### Per-Artifact Workflow

For each artifact:

1. Announce which artifact you're working on and its planned action
2. Show the source content (condensed if very long)
3. Show the proposed adapted/rewritten result you will write
4. For `merge` or `replace`: show a before/after diff of the existing file
5. Ask: `"Integrate this artifact as shown? Reply yes, skip, or describe modifications."`
6. Write only after `yes`
7. For hooks: run `python -m py_compile .claude/hooks/<name>.py` immediately after writing;
   report the result before moving on

If the user says `skip`: record it and continue.
If the user requests modifications: apply them, re-show, re-ask.

### Adaptation Rules

**Commands**
- YAML frontmatter: `name`, `description`, `scope`
  - `scope: project` — general-purpose, will be distributed to projects
  - `scope: framework` — KahnClaude management only, never distributed
- Target: `.claude/commands/<name>.md` (scope: project) or `.claude/commands/kc/<name>.md` (scope: framework, invoked as `/kc:<name>`)
- Prompt in imperative form
- Remove hardcoded project paths, project names, stack-specific assumptions

**Skills**
- YAML frontmatter: `name`, `description`, `triggers` (array of specific keywords)
- Target: `.claude/skills/<name>/SKILL.md`
- Triggers must be specific enough to avoid false activations
- Add structured phases if the source has none

**Agents**
- YAML frontmatter: `name`, `description`, `tools` (array)
- Target: `.claude/agents/<name>.md`
- Minimum necessary tool access
- Read-only agents: `Read`, `Grep`, `Glob` only — never `Write` or `Bash`
- Remove project-specific hardcoding

**Hooks**
- Always written in Python — rewrite from any other language without exception
- Naming prefix: `block-` (exit 2), `check-` (conditional), `lint-` (PostToolUse), `verify-` (Stop)
- Exit codes: 0=allow, 1=warn, 2=block; print blocking reason to stderr on exit 2
- Target: `.claude/hooks/<name>.py`
- Follow the hook template from CONTRIBUTING.md exactly
- After writing: wire in `@.claude/settings.json`, then syntax-check immediately

**Merge actions**
- Read the existing KahnClaude file first
- Extract only the novel parts from the source
- Show the merged result and confirm before writing

**Rule: never silently overwrite** — always show the proposed content and get explicit confirmation.

---

## Documentation Updates

After all artifacts are integrated, update (one at a time, with confirmation):

1. **`README.md`** — add each component to the correct table:
   - `scope: framework` commands → Framework Commands table
   - `scope: project` commands → Project Commands table
   - Skills → Skills table
   - Agents → Agents table
   - Hooks → Hooks table

2. **`CONTRIBUTING.md`** — only if genuinely new conventions were introduced

---

## Completion Summary

```
Import complete.

Integrated:
  - <N> commands
  - <N> skills
  - <N> agents
  - <N> hooks

Skipped: <name — reason>, ...
Merged: <name — what was kept>, ...

Next steps:
  - python -m py_compile .claude/hooks/*.py
  - /review on any significantly reworked artifact
  - feat(import): integrate <source-repo-name> components
```
