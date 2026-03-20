---
name: harvest
description: Pull improvements back from a target project into KahnClaude — the reverse of /kc:update
argument-hint: "<project-path>"
scope: framework
---

Pull improvements from a target project back into KahnClaude. The reverse of `/kc:update`: instead of pushing framework changes out, this harvests project-side changes back in.

**Usage:** `/kc:harvest <project-path>`

The argument is the path to the target project. If omitted, ask the user for it before proceeding.

## Steps

### 1. Resolve inputs

Resolve the target project path from the argument (or ask if not provided).

Read the install manifest from `<target>/.claude/.kahnclaude`. If it does not exist, warn the user: "No KahnClaude manifest found. This project may not have been installed with `/kc:install`. Continuing without a baseline — all matching files will be compared as full diffs."

If the manifest exists, note `manifest.commit` as the **baseline** (the KahnClaude commit that was installed into the project).

### 2. Enumerate project components

Scan these directories in the target project:

- `<target>/.claude/commands/` — skip any file with `scope: framework`
- `<target>/.claude/skills/`
- `<target>/.claude/agents/`
- `<target>/.claude/hooks/`

For each file found, determine the **mirror path** in KahnClaude (same relative path under `.claude/`).

### 3. Classify files

Use a Python script to compare all files efficiently. **Always normalize line endings (CRLF → LF) before any comparison** — project files on Windows will often have CRLF while the KahnClaude repo uses LF, causing false positives if raw bytes are compared.

For each file, compute three versions (normalized):
  - The **baseline version**: `git show <manifest.commit>:<mirror-path>` in the KahnClaude repo (what was installed)
  - The **project version**: current file in the target project
  - The **framework version**: current file in KahnClaude on disk

Separate files into two buckets:

**A. Files that exist in KahnClaude** — apply this decision matrix:
  - Project == baseline (normalized) → no project-side change; skip
  - Project != baseline AND project == framework (normalized) → both evolved identically; skip (no delta to harvest)
  - Project != baseline AND framework file no longer exists → note separately: "project modified a file that was removed from KahnClaude"; present to user for a judgment call
  - Project != baseline AND framework == baseline → **straightforward candidate**: project delta applies directly
  - Project != baseline AND framework != baseline AND project != framework → **three-way**: compute the project delta and assess whether it applies cleanly on top of the current framework version; flag as "needs merge"

  The **target for integration is always the current framework version**, not the baseline.

**B. Files that do NOT exist in KahnClaude** — new project-side additions, candidates for porting.

### 4. Show summary

Present a two-section summary:

**Modified files (exist in both):**
List each candidate with:
- File path
- A one-line description of what changed (inferred from the diff)
- Status: `straightforward` or `needs merge`

**New files (project-only):**
List each file not found in KahnClaude, grouped by type (commands / skills / agents / hooks).

If there are no candidates in either bucket, report "Nothing to harvest — no project-side changes found." and stop.

### 5. Review modified files (interview mode)

**Before showing any diffs**, if there are multiple candidates, ask:

> "Found N files to review. Go through them one at a time, or integrate all? (one-by-one / all)"

If the user says **all**: integrate every straightforward candidate automatically (skip three-way cases — those still need per-file review). Then move to Step 6.

If the user says **one-by-one** (or for all three-way cases):

For each file, show **only**:
1. A brief summary of what changed (1–3 sentences)
2. The **project delta** (diff: baseline → project)

Then ask:

> "Integrate into KahnClaude? (y/n)"
>
> Note: integrate only if the change is **generic and not project- or tech-stack-specific**.

Do NOT show the full current framework file unless the user asks. For three-way cases, also describe the framework delta briefly and ask the user to confirm the proposed merge before writing.

If approved, produce the merged result by applying the project delta to the **current framework version**.

### 6. Review new files

For each new file (bucket B), show its full content and ask:

> "Port `<file>` to KahnClaude? (y/n)"

Group by type so the user can batch-approve a whole category (e.g., "Port all 3 new agents? (y/n)").

For each approved new file, ask which subfolder it belongs in (inferred from content where possible, confirmed with the user).

### 7. Apply changes

For each approved file:

- **Modified file**: write the integrated result to the KahnClaude mirror path. If a three-way merge was needed, apply the user-confirmed result.
- **New file**: copy to the appropriate KahnClaude path, preserving subfolder structure. Create subdirectories as needed.

Do NOT modify `project/`, `global/`, `inspiration/`, `CLAUDE.md`, or any non-component files.

### 8. Post-harvest housekeeping

After applying all changes:

- Remind the user: "Run `python -m py_compile .claude/hooks/*.py` if any hooks were modified."
- Remind the user: "Update README.md and CONTRIBUTING.md for any new components added."
- Summarize: X files integrated, Y files skipped, Z new files ported.

## Notes

- Never overwrite KahnClaude files without showing the diff and getting confirmation
- Generic improvements (better prompts, new steps, clearer instructions) are good harvest targets
- Project-specific content (project names, tech-stack assumptions, local conventions) should be skipped
- If unsure whether a change is generic, show it to the user and let them decide
- The `inspiration/` folder is read-only — never harvest into it
- Do not delete KahnClaude files even if they were deleted in the target project
