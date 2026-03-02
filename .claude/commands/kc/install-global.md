---
name: install-global
description: Install global Claude config from KahnClaude into ~/.claude/
scope: framework
---

Install or merge the KahnClaude global config into `~/.claude/`.

## Steps

1. Check if `@~/.claude/CLAUDE.md` exists
   - If NO: copy `@global/CLAUDE.md` → `@~/.claude/CLAUDE.md`
   - If YES: read both files, identify sections (separated by `---`), append any sections from `@global/CLAUDE.md` that are missing from the existing file. Never overwrite existing sections.

2. Check if `@~/.claude/settings.json` exists
   - If NO: copy `@global/settings.json` → `@~/.claude/settings.json`
   - If YES: deep-merge the hooks arrays — add any hooks from `@global/settings.json` that are not already present. Never remove existing hooks.

3. Create `~/.claude/hooks/` if it doesn't exist

4. Copy hook files from `hooks/` → `~/.claude/hooks/` for any hooks wired in `@global/settings.json`
   - Skip hooks that already exist (ask before overwriting)

5. Report what was installed, merged, or skipped

## Notes

- This is a non-destructive merge — existing config is always preserved
- Never overwrite `@~/.claude/CLAUDE.md` entirely — only append missing sections
- Idempotent: safe to run multiple times
