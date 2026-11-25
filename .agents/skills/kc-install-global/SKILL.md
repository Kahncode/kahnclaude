---
name: kc-install-global
description: Install KahnClaude skills, agents, hooks, and config at user level for Claude Code (~/.claude/)
scope: framework
---

Install or merge the parts of KahnClaude the user picks (global config, hooks, skills, agents) at user level. This installs for Claude Code only: skills, agents, hooks and settings all go to `~/.claude/`. Project installs are what make skills shared with other harnesses.

## Steps

1. Get the current KahnClaude git commit hash by running `git rev-parse HEAD` in the KahnClaude source directory. Save this for the manifest.

2. **Ask what to install.** Inspect `~/.claude/` first (existing `CLAUDE.md`, `settings.json` keys and hooks, `hooks/`, `agents/`, `skills/`, `.kahnclaude` manifest) and show what is already there. Then ask which components to install, multi-select, nothing preselected (if the question tool caps options, ask in plain text and let the user reply with a list):
   - **Global instructions**: merge `@global/CLAUDE.md` sections into `~/.claude/CLAUDE.md`
   - **Permissions**: the `permissions` deny/ask/allow rules from `@global/settings.json`
   - **Status line**: `global/statusline.py` plus the `statusLine` key
   - **Hooks**: list each hook wired in `@global/settings.json` (currently `notify.py`, desktop notifications; `block-write-outside-repo.py`, ask before writes outside the project) and let the user pick individually
   - **Skills**: all `scope: project` skills, or a picked subset
   - **Agents**: by subfolder group (`core/`, stack groups); recommend only broadly useful ones, leave stack-specific agents to per-project installs

   If the user picks nothing, stop without writing anything. Every following step runs only for what was picked; never install an unpicked component.

3. **Global instructions** (if picked): if `~/.claude/CLAUDE.md` does not exist, copy `@global/CLAUDE.md`; otherwise identify sections (separated by `---`) and append the missing ones. Never overwrite existing sections.

4. **Settings** (if permissions, status line or hooks were picked): back up `~/.claude/settings.json` to `settings.json.bak-kc` (create the file if absent), then deep-merge only the picked parts of `@global/settings.json`: the `permissions` entries not already present; the `statusLine` key if absent; for each picked hook, its `hooks` entry if no entry already references that script. `block-write-outside-repo.py` installed globally makes project copies step aside, so it runs once. Never remove existing entries, except:
   - **Retired hooks:** if `~/.claude/settings.json` wires `after-edit.py`, `block-dangerous-commands.py`, `block-secrets.py`, `check-branch.py`, `check-env-sync.py`, `lint-on-stop.py` or `verify-no-secrets.py` (KahnClaude no longer ships them), offer to remove those entries.
   - **Old paths:** older global installs pointed hooks at `$CLAUDE_PROJECT_DIR/.claude/hooks/`, which breaks in projects without KahnClaude: offer to repoint them to `~/.claude/hooks/`.

5. **Files** (if picked): copy each picked hook from `.claude/hooks/` to `~/.claude/hooks/` and, for the status line, `global/statusline.py` to `~/.claude/statusline.py`. Create directories as needed; ask before overwriting an existing file that differs.

6. **Agents** (if picked): copy the picked groups to `~/.claude/agents/`, preserving subfolder structure. Ask before overwriting an existing agent that differs.

7. **Skills** (if picked): copy each picked skill folder from `.agents/skills/` to `~/.claude/skills/` (bundled files included). Never copy `scope: framework` skills. Ask before overwriting an existing skill that differs.

8. **Write the install manifest** to `~/.claude/.kahnclaude` as JSON:

   ```json
   {
     "version": 2,
     "source": "<absolute-path-to-kahnclaude>",
     "commit": "<git-commit-hash>",
     "installed_at": "<ISO-8601-timestamp>",
     "scope": "global",
     "components": ["<picked component, e.g. hook:notify.py, statusline, agents:core>", ...],
     "agents": ["<relative-agent-path>", ...],
     "notes": "<one-line summary of what was installed or merged>"
   }
   ```
   - If `~/.claude/.kahnclaude` already exists, update `commit`, `installed_at`, `components` (union with the existing list), `agents`, and `notes` in place; preserve any other existing fields.

9. Report what was installed, merged, or skipped.

## Notes

- This is a non-destructive merge — existing config is always preserved
- Never overwrite `@~/.claude/CLAUDE.md` entirely — only append missing sections
- Idempotent: safe to run multiple times
- The `.kahnclaude` manifest lets `kc-update` determine which KahnClaude commit was last applied to the global config
