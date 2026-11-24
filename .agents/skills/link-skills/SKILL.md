---
name: link-skills
description: Expose .agents/skills to Claude Code by linking (or copying) it to .claude/skills. Run after cloning, or when Claude Code does not list this project's skills. Other harnesses read .agents/skills directly.
scope: project
disable-model-invocation: true
---

Claude Code only reads `.claude/skills/`; Codex, OpenCode and pi read `.agents/skills/` directly. This skill projects the shared folder into `.claude/skills/`.

A SessionStart hook in `.claude/settings.json` already runs the script every session, so you normally never invoke this by hand.

## Steps

1. Run from the project root:

   ```
   python .agents/skills/link-skills/scripts/link_skills.py . [--mode auto|link|copy] [--force]
   ```

   - `auto` (default): symlink, or a junction on Windows (no admin needed); falls back to a copy if linking fails
   - `copy`: always copy; re-run after skill changes
   - `--force`: replace an unmanaged `.claude/skills` (its contents are lost)

2. Read the last output line, `PROJECTION=<symlink|junction|copy>`, and report it.

3. If the script reports unmanaged files in `.claude/skills/`, move those skill folders into `.agents/skills/` (ask on name collisions), then re-run.

## Notes

- `.claude/skills/` is generated output and is gitignored; edit skills in `.agents/skills/` only
- Stdlib only; works on Windows, macOS, Linux and WSL
