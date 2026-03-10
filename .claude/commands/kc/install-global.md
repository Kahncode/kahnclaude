---
name: install-global
description: Install KahnClaude commands, skills, agents, hooks, and config into ~/.claude/
scope: framework
---

Install or merge the KahnClaude global config, skills, and agents into `~/.claude/`.

## Steps

1. Get the current KahnClaude git commit hash by running `git rev-parse HEAD` in the KahnClaude source directory. Save this for the manifest.

2. Check if `@~/.claude/CLAUDE.md` exists
   - If NO: copy `@global/CLAUDE.md` → `@~/.claude/CLAUDE.md`
   - If YES: read both files, identify sections (separated by `---`), append any sections from `@global/CLAUDE.md` that are missing from the existing file. Never overwrite existing sections.

3. Check if `@~/.claude/settings.json` exists
   - If NO: copy `@global/settings.json` → `@~/.claude/settings.json`
   - If YES: deep-merge the hooks arrays — add any hooks from `@global/settings.json` that are not already present. Never remove existing hooks.

4. Create `~/.claude/hooks/` if it doesn't exist. Copy hook files from `hooks/` → `~/.claude/hooks/` for any hooks wired in `@global/settings.json`. Skip hooks that already exist (ask before overwriting).

5. Create `~/.claude/commands/` if it doesn't exist. Copy command files from `.claude/commands/` → `~/.claude/commands/`, **preserving subfolder structure**. Skip `scope: framework` commands. Skip commands that already exist (ask before overwriting).

6. **Select agents** to install globally:

   a. **Always copy `core/` agents without asking** — they are universal.

   b. **Present remaining agents grouped by subfolder** and ask the user which groups to include globally. Note: `AskUserQuestion` is capped at 4 options per question. For groups with more than 4 agents, describe them in plain text and ask the user to reply with which to include.

   c. Unlike project installs, global agents apply to all projects — recommend including only broadly useful agents (e.g. general-purpose, devops) and leaving stack-specific ones for per-project installs.

7. Create `~/.claude/agents/` if it doesn't exist. Copy selected agents to `~/.claude/agents/`, **preserving subfolder structure**. Create any needed subdirectories. Skip agents that already exist (ask before overwriting).

8. Create `~/.claude/skills/` if it doesn't exist. Copy all files from `.claude/skills/` → `~/.claude/skills/`, **preserving subfolder structure**. Skip skills that already exist (ask before overwriting).

9. **Write the install manifest** to `~/.claude/.kahnclaude` as JSON:

   ```json
   {
     "version": 1,
     "source": "<absolute-path-to-kahnclaude>",
     "commit": "<git-commit-hash>",
     "installed_at": "<ISO-8601-timestamp>",
     "scope": "global",
     "agents": ["<relative-agent-path>", ...],
     "notes": "<one-line summary of what was installed or merged>"
   }
   ```
   - If `~/.claude/.kahnclaude` already exists, update `commit`, `installed_at`, `agents`, and `notes` in place; preserve any other existing fields.

10. Report what was installed, merged, or skipped.

## Notes

- This is a non-destructive merge — existing config is always preserved
- Never overwrite `@~/.claude/CLAUDE.md` entirely — only append missing sections
- Idempotent: safe to run multiple times
- The `.kahnclaude` manifest lets `kc:update` determine which KahnClaude commit was last applied to the global config
