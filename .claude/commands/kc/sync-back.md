---
name: sync-back
description: Sync changes from a KahnClaude-installed project back into the framework
scope: framework
---

Sync changes from a target project (installed with `/kc:install`) back into KahnClaude.

**Usage:** `/kc:sync-back <project-path>`

The argument is the path to the target project. If omitted, ask the user for it before proceeding.

## Steps

1. **Resolve the target project path** from the argument (or ask if not provided).

2. **Read the install manifest** from `<target>/.claude/.kahnclaude`. If it does not exist, tell the user this is not a KahnClaude-installed project and stop.

3. **Map installed components** using the manifest structure:
   - `manifest.agents` lists which agents were installed
   - Commands, skills, hooks, and docs follow standard paths

4. **Scan for changes** by comparing project files against KahnClaude equivalents:

   | Project path | KahnClaude path |
   |--------------|-----------------|
   | `<target>/.claude/commands/*.md` | `.claude/commands/*.md` |
   | `<target>/.claude/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` |
   | `<target>/.claude/agents/*.md` (in manifest) | `.claude/agents/*.md` |
   | `<target>/.claude/hooks/*.py` | `.claude/hooks/*.py` |
   | `<target>/docs/**` | `project/docs/**` |

   For each file pair:
   - If **identical**: skip (no change)
   - If **project has changes**: mark as candidate for sync
   - If **project file is new** (no KahnClaude equivalent): mark as candidate for create

5. **Detect new components** in the project that don't exist in KahnClaude:
   - New commands, skills, agents, or hooks added in the project
   - New docs files

6. **Show a summary** of all candidates:
   ```
   Changes found in <project-name>:
   
   Modified (project differs from KahnClaude):
     - .claude/commands/foo.md
     - .claude/skills/bar/SKILL.md
   
   New (exists in project, not in KahnClaude):
     - .claude/commands/custom.md
     - docs/my-guide.md
   
   Unchanged: <N> files
   ```

7. **Review each candidate** one at a time:
   - Show a diff between project version and KahnClaude version
   - Ask: "Sync this change into KahnClaude? (yes/skip/show full)"
   - Offer a "sync all" shortcut if there are many changes

8. **For modified files**: overwrite the KahnClaude version with the project version.

9. **For new files**: 
   - Copy to the correct KahnClaude location
   - For commands: check frontmatter for `scope` to determine if it goes to `.claude/commands/` or `.claude/commands/kc/`
   - For new agents: add to `.claude/agents/` (or appropriate subfolder)

10. **Report a summary** of what was synced:
    ```
    Sync complete.
    
    Synced:
      - <N> modified files
      - <N> new files
    
    Skipped: <list>
    
    Next steps:
      - Review synced changes for framework-specific adjustments
      - Update README.md if new components were added
      - Commit: feat(sync-back): sync changes from <project-name>
    ```

## Notes

- Never auto-sync without showing diffs first
- For new components, warn if they contain project-specific paths or names that need generalization
- `scope: framework` commands stay in `.claude/commands/kc/`; `scope: project` commands go to `.claude/commands/`
- If a file was modified in both KahnClaude and the project since the last install/update, show both versions and ask which to keep (or merge manually)
- Always verify file differences by actual comparison — use `git diff` or explicit line-by-line comparison
