---
name: generify-to-user
description: "Moves Claude setup items (docs, skills, agents, commands, hooks, scripts) from a project into user-level ~/.claude and generifies them: project values become {{VAR}}s, mixed docs are split, project-only rules go to overlay notes. ALWAYS invoke for 'generify X', 'move X to user level', 'make this skill work on other projects', or a dry run. Not for onboarding a project."
---

# Generify to user

Move project items into `~/.claude`, made project-agnostic. The rules for *how* to rewrite text, scripts and hooks are in `references/rules.md`. Read it before Step 3. It is the distilled result of a large migration, and every rule there exists because breaking it caused a real problem.

The helper `scripts/generify.py` does the mechanical, error-prone parts:
- copies into a staging tree, recording what each file looked like;
- checks for leaks, undefined vars, syntax errors, `KC_` names, caches and gendered pronouns;
- installs only files that nobody else changed in the meantime.

Run it from the project root (it finds `.claude/rules/project-vars.md` there):
```
python -I -X utf8 $HOME/.claude/skills/generify-to-user/scripts/generify.py <stage|edit|check|install> --work <W> ...
```
`W` = `{{TEMP_BASE}}\generify-<slug>\`, a new folder per run. Everything goes into `W\stage\user\...` (→ `~/.claude`) or `W\stage\project\...` (→ project) until Step 7. Nothing live changes before that point, so a dry run is just "stop after Step 6".

## Step 1: Inventory

For each item the user named, plus anything it obviously drags along (a skill's scripts, the doc an agent cites):
1. **Read it fully.** Classify it:
   - **GENERIC**: no project data.
   - **PARAMETERIZE**: generic logic with project literals.
   - **SPLIT**: generic knowledge mixed with project facts.
   - **PROJECT-BOUND**: about this project's own systems, so it stays.

   Most docs are SPLIT. An audio-middleware or Horde doc holds vendor behaviour *and* the project's banks, streams and server changes.
2. **Destination.** Where does it land under `~/.claude` (same subpath as in the project, e.g. `docs/tech-stacks/x.md`)? Does a file already live there? If so, this run merges into it and must not overwrite it.
3. **Callers.** Grep for the item's path and name in the project's `.claude/`, `CLAUDE.md`, `CLAUDE.local.md`, `docs/`, `scripts/`, the project memory folder `{{CLAUDE_MEMORY_DIR}}`, `~/.claude/{agents,skills,commands,docs}` and both `settings.json`. Scope every search to those folders; never grep the workspace root or Content.
4. **External callers** git can't see, for scripts:
   - P4V custom tools: `%USERPROFILE%\.p4qt\customtools.xml`.
   - Task Scheduler jobs: `schtasks /query /fo LIST /v`, filtered on the script name.
   - VS external tools.

   Name the tool and its current arguments. Re-pointing it is the user's step: P4V rewrites `customtools.xml` on exit, so use its Manage Custom Tools dialog. It must happen before the source is removed.
5. **Checking the P4 connection:** use `p4 set -q P4CLIENT P4PORT P4USER` or `p4 -ztag info`. A bare `p4 set` prints the `P4PASSWD` ticket.

Show a short table: item → verdict → destination → callers. Stop for the user's go-ahead when something is PROJECT-BOUND, when a split is not obvious, or when there are external callers. Otherwise continue.

## Step 2: Stage

```
generify.py stage --work W <src>=<dest> ...                 a whole move (GENERIC / PARAMETERIZE): the source is removed later
generify.py stage --work W --keep-source <src>=<dest> ...   a SPLIT: the source keeps the project half and is never removed
generify.py edit  --work W <file> ...                       other project or ~/.claude files you will change
```
- **`stage` on a SPLIT without `--keep-source`** would list the project file for removal at install, and that would delete the project half. `--keep-source` also stages the source as an edit copy, ready to cut down to its project lines.
- **When the user-level file already exists,** `stage` stages *that* file and puts the project file in `W\incoming\` as input. You merge generic lines into the existing file; its old lines stay untouched. Re-migrating a topic that was split before (e.g. a second Horde pass) usually needs only `--keep-source`.
- **Use `edit`** for callers, and for both vars files when you add vars: the project `project-vars.md` and `~/.claude/templates/unreal-project/project-vars.md`.

New project files (overlays) are simply written under `W\stage\project\<path>`. `stage` reports `evals/` fixtures it left behind. Those stay in the project, per rules §4.

## Step 3: Rewrite (in the stage only)

Follow `references/rules.md`:
- `{{VAR}}` in text;
- `get()` / `Get-ProjectVar` in code;
- split or overlay per line, with every line landing in exactly one file;
- neutral examples, no people;
- new vars in both vars files, never `KC_`.

When many files are involved, fan out general-purpose agents by batch. Give them `references/rules.md` and the stage paths. They report new vars to you instead of editing the vars files, so concurrent edits don't collide.

## Step 4: Repoint callers

Edit the staged caller copies:
- old project path → `~/.claude/...`;
- a doc that split → mention both files.

If the project's `CLAUDE.md` is version-controlled and cites the moved path, don't change it without a changelist. Add a redirect line to `CLAUDE.local.md` instead.

## Step 5: Check until clean

```
generify.py check --work W [--extra name1,codename2]
```
- **Leak terms** come from the project's vars file: project name, Jira key, studio domain, ids, workspace names, the contact person. Add people's names or codenames with `--extra`.
- **In edit copies of existing user-level files,** only lines you changed are checked. Old lines that are machine-specific by design are not your leak.
- **Fix every hit** in the stage. A hit you believe is fine (a vendor name that matches a term) needs a one-line reason in the report.
- **Scripts:** also run old vs new on the same real input from the project root (read-only commands) and diff the output.

## Step 6: Review checkpoint

Tell the user, in a few lines:
- what moves where, with the split line counts (generic / project / split);
- new vars and their values;
- overlays written;
- caller edits;
- what stays in the project.

For a dry run, write this as `W\review.md` and stop here; the staged tree is the deliverable. If the write is refused (subagents may not write report files), put the same text in your final message instead. Otherwise get the go-ahead. Install changes live files that other sessions load.

## Step 7: Install

1. `generify.py install --work W --dry`, then without `--dry`. A CONFLICT means someone edited that file after you staged it. Re-`edit` it, redo your change on the new version, re-check. Never overwrite another session's work.
2. **Remove each source `install` lists** (whole moves only; `--keep-source` items are never listed) through the project's Claude repo, so the deletion is recorded. If the project's Claude setup is in its own git repo, `git rm -r -q` the path there. Without such a repo, delete the file. Afterwards, remove any leftover `__pycache__`-only folders.
3. **Hooks only:** rewire both settings.json files first (one edit each, then validate the JSON), and remove the old hook files last (rules §7).

## Step 8: Verify and commit

- Re-run the user-level vars check: `python -I -X utf8 $HOME/.claude/scripts/lib/project_vars.py --check $HOME/.claude/agents $HOME/.claude/skills $HOME/.claude/commands $HOME/.claude/hooks $HOME/.claude/scripts $HOME/.claude/docs --template $HOME/.claude/templates/unreal-project/project-vars.md`.
- Grep that the old path no longer appears in the callers.
- If the project and `~/.claude` setups are under version control, commit both (commit messages via `-F <file>`). Messages name each other: `Move <item> to the user-level setup` / `Move <item> from <project repo>`.

## Report

End with:
- **What I did**: one sentence.
- **Moved / split / stayed**: a table of item → destination → line counts.
- **New vars** and **overlays**.
- **What to check**: usually opening the moved item in a fresh session.
- For a dry run: the path of `review.md` (or "review in this message"), and "nothing installed".
