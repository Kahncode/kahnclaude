# Generify rules

How to turn a project file into a project-agnostic user-level file. They were distilled from a large migration. Each rule exists because breaking it caused a real problem.

## Contents
1. Where each syntax goes
2. Literal → var mapping
3. Splitting and overlays
4. Examples, people, fixtures
5. Scripts and hooks
6. New vars
7. Things that bit us

## 1. Where each syntax goes

| Where | Write | Why |
|---|---|---|
| Text Claude reads (SKILL.md, references, agents, commands, docs) | `{{NAME}}` | Claude substitutes it from the auto-loaded `.claude/rules/project-vars.md`. |
| Script code (py/ps1/js/bat) | `get("NAME")` from `~/.claude/scripts/lib/project_vars.py`; `Get-ProjectVar NAME` after dot-sourcing `ProjectVars.ps1` | Scripts can't read `{{}}`. These helpers read the env var first, then the vars file, so they work even in sessions started before an env change. |
| Hook commands in settings.json | real paths / `$CLAUDE_PROJECT_DIR` | The shell runs them and no one substitutes `{{}}`. |
| A path to something user-level | `~/.claude/...` in prose, `$HOME/.claude/...` in commands Claude runs | `$HOME` expands in both Bash and PowerShell. |
| A path to something that stays in the project | `{{PROJECT_ROOT}}\...` or a dedicated var (`{{HORDE_DOC}}`) | Never `$CLAUDE_PROJECT_DIR` in text. |

Python import pattern:
```python
sys.path.insert(0, str(Path.home() / ".claude" / "scripts" / "lib"))
from project_vars import get   # get("NAME") raises KeyError with a fix hint; get("NAME", default)
```
An existing CLI arg or param still wins over the var. Turn a hardcoded default into "default from var".

## 2. Literal → var mapping

Read the project's `.claude/rules/project-vars.md` first: it lists every var with its value, so you can match literals to names. Common shapes:

| Literal shape | Var |
|---|---|
| workspace root path | `{{PROJECT_ROOT}}` |
| `<root>\<Project>\Source`, `\Config`, `\Saved`, `\Content` | `{{UE_PROJECT_DIR}}\Source` … |
| engine folder, .uproject, .sln | `{{UE_ENGINE}}`, `{{UE_PROJECT}}`, `{{UE_SOLUTION}}` |
| `.temp\<x>` | `{{TEMP_BASE}}\<x>` (`<agent>-<CL>` pattern → `{{TEMP_ROOT}}`) |
| game / editor / test module names | `{{UE_GAME_MODULE}}`, `{{UE_EDITOR_MODULE}}`, `{{UE_TEST_MODULE}}` |
| `<MODULE>_API` macro | "the game module's `_API` macro" |
| test prefix, test-class macro, test map | `{{UE_TEST_PREFIX}}`, `{{UE_TEST_CLASS_MACRO}}`, `{{UE_TEST_MAP}}` |
| editor exe name, UBT target | `{{EDITOR_PROCESS}}`, `{{UE_DEFAULT_TARGET}}` |
| Jira key / ticket / regex | `{{JIRA_PROJECT_KEY}}`, `{{JIRA_PROJECT_KEY}}-123`, `{{JIRA_PROJECT_KEY}}-\d+` |
| Confluence space / ids, cloud id | `{{CONFLUENCE_SPACE_KEY}}`, `{{CONFLUENCE_SPACE_ID}}`, `{{CONFLUENCE_ROOT_PAGE_ID}}`, `{{JIRA_CLOUD_ID}}` |
| studio URLs | `{{JIRA_URL}}`, `{{CONFLUENCE_URL}}`, `{{HORDE_URL}}`, `{{SWARM_URL}}`, `{{ADMIN_PANEL_URL}}` |
| depot root, streams, workspaces | `{{P4_DEPOT_ROOT}}`, `{{P4_STREAM}}`, `{{P4_DEVTOOLS_STREAM}}`, `{{P4CLIENT}}`, `{{P4CLIENT_DEVTOOLS}}` |
| project memory folder | `{{CLAUDE_MEMORY_DIR}}` |
| "values live in CLAUDE.local.md" | "`.claude/rules/project-vars.md`" |
| project CLAUDE.md rule numbers | "the project's CLAUDE.md test rule" (no number) |
| the project's name in prose | `{{UE_PROJECT_NAME}}` or "this project"; game title → `{{GAME_NAME}}` |
| studio name | "the studio" |

Agent and skill names stay as they are: they are user-level too.

## 3. Splitting and overlays

Most docs mix generic knowledge with project facts. A Horde doc, for example, holds API shapes (generic) next to the studio's stream config (project). Decide per line:

- **Generic** (engine, tool or vendor behaviour that is true in any project) → the user-level file.
- **Project** (this project's paths, ids, schedules, people, server changes, conventions) → stays in the project:
  - **A split doc** (most of a doc is project facts): the project file keeps the project lines and gets a header pointing at the generic file. The generic file gets a header pointing at `{{<DOC_VAR>}}`. Add a `<DOC>_DOC` var for the project file if none exists.
  - **An overlay** (a generic skill/agent/standard with a few project rules): move those lines verbatim to `{{PROJECT_NOTES_DIR}}\<item>.md`. Start it with `# <item>: <Project> notes` plus one line naming the file it extends. Where the text was, leave `Project specifics: read {{PROJECT_NOTES_DIR}}\<item>.md if it exists.`
- **Every original line lands in exactly one file.** Count them and report "N generic / M project / K split". A line holding both, such as a generic rule plus the project's value, splits in two: the rule goes to the generic file, the value to the project file.
- Copy project text, don't summarize it: it is proven knowledge.
- **The user-level file already exists** (a second migration of the same topic): merge new generic lines into it, under the right heading. Never overwrite it.

## 4. Examples, people, fixtures

- Project-specific worked examples (class names, asset paths, CL/ticket numbers, file:line):
  - Prefer a neutral UE example (`UMyComponent`, `/Game/Characters/BP_Hero`), or keep the example's shape with vars.
  - If an example carries knowledge the item needs, move it to the overlay.
- **People:** drop names, or use a var (`{{ADMIN_PANEL_CONTACT}}`). Refer to the user as "the user" / "they", never "she" or "he".
- **Fixtures** (`evals/`, example decks, sample data full of project content) stay in the project under `{{PROJECT_ROOT}}\.claude\skill-fixtures\<skill>\`. The generic file may point there "if present". `generify.py stage` already skips `evals/`.
- Personal things that aren't project data (the user's own artifact URLs, machine tool paths like ffmpeg) can stay.

## 5. Scripts and hooks

- Change values, not logic. Keep the CLI args, and let a CLI value win over the var.
- **Verify by comparison.** Run the old script and the new one on the same real input from the project root (read-only commands only) and diff the outputs. Never launch the editor, UBT or test runs to verify.
- Scripts with a sibling-relative path (`Path(__file__).parents[4] / "docs/..."`) break when moved: replace the path with a var.
- **A hook that moves to user level runs in every repo.** Gate UE-specific hooks so they are a no-op unless a `*.uproject` is in `$CLAUDE_PROJECT_DIR` or one level below. Gate P4 hooks on `.p4config` / `P4CLIENT`. On a missing var, a hook must allow, never crash.
- Python is run as `python -I -X utf8`. Edit or Write files, never `sed -i`, because it changes line endings.

## 6. New vars

- **Names:** plain UPPER_SNAKE: `UE_*`, `P4_*`, `JIRA_*`, `HORDE_*`, `<DOC>_DOC`. **Never a `KC_` prefix.** Reuse an existing name before inventing one.
- **Add each new var to both files, via staged edit copies:**
  - the project's `.claude/rules/project-vars.md`, with the real value;
  - `~/.claude/templates/unreal-project/project-vars.md`, with a one-line comment and an empty value. Template examples use a neutral project (`MyGame`, `C:\p4\MyGame`), never the real one.
- **No secrets** in either file.

## 7. Things that bit us

- **Hooks:** if hook files are deleted while settings.json still points at them, every PreToolUse hook exits 2. That blocks Bash, PowerShell, Read/Edit/Write, Glob and Grep. Rewire settings first, and delete hook files last. If it happens anyway, copy the hooks back with `mcp__filesystem__copy_file`, which those hooks don't cover.
- **`git rm` leaves ignored files behind** (`__pycache__`). After removing a source folder, delete the leftover cache-only folders. Otherwise they look like a duplicate skill.
- **PowerShell 5.1 mangles `"` inside native args.** Commit with `git ... commit -F <file>`, not `-m "..."`.
- **Git whitelists:** a new top-level folder in `~/.claude` needs a `!/<folder>/` line in `~/.claude/.gitignore`, or it is silently untracked.
- **A bare `p4 set` prints the `P4PASSWD` ticket** into the tool output. Check the connection with `p4 set -q P4CLIENT P4PORT P4USER` or `p4 -ztag info`.
- **A split doc's source must not be removed.** Stage it with `--keep-source`; otherwise install lists it for `git rm`, and that deletes the project half (found in an earlier dry run).
- **Small glue code is OK** when a script must find its project at runtime. For example, a P4V tool reads the CL's workspace root from `p4 -ztag info` to load that project's vars, so one tool serves every project. Report it as a logic change.
- **Shared machine:** other sessions edit skills and memory at any time. `generify.py install` refuses any file that changed after you staged it. Re-stage it, don't force it.
