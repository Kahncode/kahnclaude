# KahnClaude Unreal Engine

> Stop Claude from running `p4 submit` on your main branch. A battle-tested Claude Code configuration layer for UE5 + Perforce + Jira game development.

---

## Table of Contents

- [What Is This?](#what-is-this)
- [What's Included](#whats-included)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Supported Stack](#supported-stack)
- [Project Structure](#project-structure)
- [Plugins](#plugins)
- [MCP Servers](#mcp-servers)
- [Commands](#commands)
- [Skills](#skills)
- [Agents](#agents)
- [Hooks](#hooks)
- [Templates](#templates)
- [Team Setup](#team-setup)
- [Key Concepts](#key-concepts)
- [Essential Claude Code Commands](#essential-claude-code-commands)
- [Migrating from Existing Setup](#migrating-from-existing-setup)
- [Troubleshooting](#troubleshooting)
- [Adding Components](#adding-components)
- [Getting Help](#getting-help)
- [Contributing](#contributing)

---

## What Is This?

KahnClaude Unreal Engine is a **Claude Code configuration layer** specialized for Unreal Engine 5 game development with Perforce (Helix Core) for version control and Jira for issue tracking. It provides the infrastructure that makes Claude dramatically more effective: slash commands, specialist agents, enforcement hooks, and CLAUDE.md templates.

**KahnClaude provides:**
- **Guardrails** — Hooks block dangerous commands before they execute
- **Workflow integration** — Skills for P4, Swarm, Jira, Confluence out of the box
- **Team memory** — CLAUDE.md captures lessons learned; mistakes become rules
- **Specialist delegation** — Agents for code review, Blueprint work, production

---

## What's Included

| Component             | Count | Purpose                                                                   |
| --------------------- | ----- | ------------------------------------------------------------------------- |
| **Slash Commands**    | 14    | On-demand workflows invoked with `/command` (6 project + 8 framework)     |
| **Skills**            | 15    | Focused skills with colocated reference docs, auto-triggered + user-invokable |
| **Agents**            | 11    | Specialist subagents with restricted tool access                          |
| **Hooks**             | 11    | Deterministic enforcement scripts (Python)                                |
| **Tech-Stack Guides** | 6     | Compact Q&A + operational reference guides for CLAUDE.md generation       |

---

## Prerequisites

| Requirement | Minimum Version | Check Command |
|-------------|-----------------|---------------|
| [Claude Code](https://code.claude.com/docs/en/desktop) | 1.0.0+ | `claude --version` |
| [Git](https://git-scm.com/install/windows) | 2.30+ (for cloning this depot)| `git --version` |
| [Node.js](https://nodejs.org/en/download) | 18+ (for MCP servers) | `node --version` |
| (optional) [Perforce CLI](https://www.perforce.com/downloads) | — | `p4 -V` |
| (optional) [Atlassian](https://www.atlassian.com/) | — | Jira/Confluence access for producer/designer agents |

---

## Quick Start

### Windows (PowerShell)

```powershell
# 1. Clone KahnClaude somewhere permanent
git clone <repo-url> C:\tools\kahnclaude

# 2. Open Claude Code from your UE5 project directory
cd C:\Projects\YourUE5Project
claude

# 3. Install KahnClaude into this project
/kc:install

# 4. Customize CLAUDE.md for your project
/kc:generate-claude-md

# 5. Configure integrations for Perforce, Jira, etc.
/plugins

# 6. Build Claude's knowledge base of your project
/document
```

> **Step 6:** `/document` creates an `ARCHITECTURE.md` and subsystem docs so Claude understands your codebase from the first session. Run it once after setup. Use `/learn` to update documentation from the current context as you go.

---

## Supported Stack

KahnClaude is specialized for **UE5 + Perforce + Jira** game development.

| Category            | Supported                                           |
| ------------------- | --------------------------------------------------- |
| **Engine**          | Unreal Engine 5 (C++ and Blueprint)                 |
| **Languages**       | C++ (UE5), Python (hooks/tools)                     |
| **Version Control** | Perforce (Helix Core) with Streams                  |
| **Issue Tracking**  | Jira (Atlassian)                                    |
| **Code Review**     | Helix Swarm                                         |
| **Environments**    | Windows, WSL2, macOS, Linux                         |
| **Editors**         | VS Code, Rider, any editor with terminal access     |

---

## Project Structure

```
kahnclaude/
├── .claude/                     # All Claude components (framework + distributable)
│   ├── commands/                # Slash commands
│   │   └── kc/                  # Framework-only commands, invoked as /kc:<name>
│   ├── skills/                  # Focused skills (<skill-name>/SKILL.md)
│   ├── agents/                  # Specialist subagents
│   │   └── core/                # Cross-cutting specialists (including UE5)
│   └── hooks/                   # Enforcement scripts (Python only)
├── docs/                        # Project documentation
├── project/                     # Templates distributed via /kc:install
│   ├── docs/
│   │   ├── tech-stacks/         # Tech-specific Q&A guides (UE5, P4, Swarm, Jira, etc.)
│   │   └── standards/           # Shared reference docs (standards, checklists)
│   └── scripts/
│       ├── unreal/              # UE5 editor automation
│       └── vs/                  # Visual Studio automation
├── global/                      # Global ~/.claude/ config templates
└── inspiration/                 # Third-party reference — read-only
```

---

## Plugins

Plugins add commands, automation, and workflow enhancements to Claude Code. Browse and install via `/plugins`.

### Recommended

| Name | What It Adds |
| ---- | ------------ |
| **Context7** | Up-to-date library docs and code examples pulled at query time — eliminates hallucinated APIs |
| **skill-creator** | Create, edit, and optimize skills with eval-driven development and performance benchmarking |
| **Atlassian** | Read/write Jira issues, Confluence pages — enables Jira skills and producer agent |
| **GitHub** | Create PRs, manage issues, search code, review pull requests — full GitHub workflow integration |
| **claude-warden** | Permission manager — pre-approves safe bash commands to eliminate repetitive allow/deny prompts |

> **Discovery:** Run `/plugins` to browse and install available plugins directly from Claude Code.

---

## MCP Servers

MCP (Model Context Protocol) servers give Claude access to external tools, documentation, and services.

### Recommended

| Name | What It Adds |
| ---- | ------------ |
| **Filesystem** | Lets Claude read/write files outside the project root (cross-repo work, config management) |
| **Perforce** | P4 operations (changelists, shelve, diff, sync, streams) without leaving Claude |
| **UnrealClaude** | 20+ tools for UE5.7 — actor manipulation, blueprint editing, level management, materials |

```bash
# Filesystem — access files outside project root
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allow
```
```bash
# Perforce MCP
claude mcp add perforce -- npx -y mcp-perforce-server@latest
# UnrealClaude — UE5 editor plugin, see https://github.com/Natfii/UnrealClaude
```
### Verifying Installation

Run `/mcp` to list all installed MCP servers and their connection status.

### Finding More

- Official MCP catalog: https://code.claude.com/docs/en/mcp
- Community MCP registry: https://mcpservers.org/

---

## Commands

Invoke with `/command-name` inside any Claude Code session. Commands are Markdown files with YAML frontmatter.

### Project Commands (6)

These are distributed to your project via `/kc:install` — available in any KahnClaude-enabled project.

| Command                    | What It Does                                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `/answer`                  | Research a question using general knowledge, codebase search, Context7 docs, or web search                 |
| `/document`                | Build or update project docs: no args = ARCHITECTURE.md index, with args = subsystem deep-dive             |
| `/explain`                 | Explain code in detail — overview, components, control flow, dependencies, gotchas, usage                  |
| `/learn`                   | Update docs from a P4 changelist number, CL range, a plain-text fact, or auto-detected opened/pending      |
| `/progress`                | Show file counts, test status, recent P4 submitted/pending activity, and next actions                      |
| `/refactor`                | Refactor a file against CLAUDE.md rules — split, extract, clean up                                         |

> **Start with these:** `/document` (build initial knowledge), `/explain` (understand unfamiliar code), `/answer` (research questions)

### Framework Commands (8)

These are only available in the KahnClaude repository itself — for managing and developing the framework.

| Command                    | What It Does                                                                      |
| -------------------------- | --------------------------------------------------------------------------------- |
| `/kc:install`              | Install KahnClaude components into the current project                            |
| `/kc:install-global`       | Install commands, skills, agents, hooks, and config into `~/.claude/`             |
| `/kc:update`               | Update installed components in a target project to the latest versions            |
| `/kc:sync-back`            | Sync changes from a KahnClaude-installed project back into the framework          |
| `/kc:import`               | Analyze a repo's Claude Code components and selectively integrate into KahnClaude |
| `/kc:create-agent-skill`   | Create a new agent, skill, or slash command following framework conventions       |
| `/kc:fix-agent-skill`      | Debug a misbehaving agent or skill — session analysis + convention audit          |
| `/kc:generate-claude-md`   | Auto-detect tech stack (UE5 via `.uproject`) and generate a complete CLAUDE.md    |

---

## Skills

Skills are auto-triggered on keywords AND user-invokable with `/skill-name`. Each lives in `.claude/skills/<name>/` with a `SKILL.md`.

| Skill | Category | What It Does |
| ----- | -------- | ------------ |
| `/task-implementation` | Implementation | Unified implementation orchestrator — routes C++, Blueprint, or mixed tasks to correct agents |
| `/code-review` | Code | Smart orchestrator — resolves diff, spawns concern-based review agents, re-verifies criticals |
| `/perforce-changelog` | Perforce | Generate changelog from P4 history — filter by code system, user, time range |
| `/perforce-changelist-description` | Perforce | Generate CL description from diff + Jira ticket, enforces `[TICKET][Summary] Tech #review` format |
| `/swarm-review-shelve` | Swarm | Write CL description → shelve → report Swarm URL if `#review` present |
| `/swarm-review-comments` | Swarm | Fetch Swarm review comments, fix one-by-one, reply, re-shelve |
| `/to-jira-issue` | Jira | Break a plan into vertical slice issues, delegate to producer for ticket creation |
| `/to-confluence-page` | Confluence | Create, update, or publish Confluence pages including game wiki publishing |
| `/task-planning` | Planning | Clarify requirements, draft implementation plan, architecture review |
| `/unreal-project-compilation` | Unreal | Build + analyze + fix loop, supports all build targets, shelves on success |
| `/game-log` | Unreal | Read + diagnose game logs, auto-detect log file, cross-reference source |
| `/unreal-pie` | Unreal | Manage PIE sessions — start, stop, or execute console commands |
| `/unreal-asset-inspections` | Unreal | Inspect and modify UE5 assets — read/set properties, dump all, find referencers |
| `/editor-python` | Unreal | Execute arbitrary Python code or script files in the running editor |

> **Start with these:** `/code-review` (review your code), `/perforce-changelist-description` (better CL descriptions), `/task-planning` (plan before coding)

> **Listing:** Run `/skills` to list all available skills and their trigger keywords.

---

## Agents

Agents are specialists Claude delegates to automatically. Each has restricted tool access appropriate to its role.

| Agent                         | Tools                                | Specialization                                                               |
| ----------------------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| `blueprint-dev`               | Read, Write, Edit, Grep, Glob, Bash  | Blueprint asset specialist — implements pre-approved plans via Python Remote Execution |
| `blueprint-planner`           | Read, Grep, Glob, Bash               | Blueprint planning agent — inspects assets and produces implementation plans, read-only |
| `blueprint-reviewer`          | Read, Grep, Glob, Bash               | Blueprint asset reviewer — inspects properties via Python Remote Execution, read-only |
| `code-dev`                    | Read, Write, Edit, Grep, Glob, Bash  | UE5 C++ — implements pre-approved plans with P4 changelist discipline, validates via full build |
| `code-planner`                | Read, Grep, Glob, Bash               | UE5 C++ planning agent — gathers context and produces implementation plans, read-only |
| `code-reviewer`               | Read, Grep, Glob, Bash(p4)           | C++/UE5 code reviewer: security, correctness, performance, C++ craft, engine pitfalls, Blueprint boundary |
| `designer`                    | Read, Write, Edit, Grep, Glob, Confluence+Jira MCP | Game design specialist — balance decisions, system design, local game wiki generation, Confluence wiki management |
| `documenter`                  | Read, Write, Edit, Grep, Glob        | Architecture docs, subsystem docs, Mermaid diagrams, Decisions logs          |
| `producer`                    | Read, Grep, Glob, Jira MCP           | Fetches Jira tickets, clarifies technical requirements, identifies cross-team dependencies, gathers estimates, and creates well-structured tickets |
| `python-dev`                  | Read, Write, Edit, Bash, Grep, Glob, WebFetch | Modern Python 3.12+ — architecture, packaging, async, type system         |
| `unreal-guide`                | Read, Grep, Glob, WebSearch, WebFetch | Answers UE5 questions using official Epic docs and forums, cites sources   |

> **Note:** Reviewers are read-only (no Write/Edit) to prevent accidental modifications during review.

---

## Hooks

CLAUDE.md rules are suggestions. Hooks are **deterministic** — they always run as Python scripts at specific lifecycle points.

```
CLAUDE.md rule: "don't read .env"
  → Parsed by LLM → Weighed against context → Maybe followed

PreToolUse hook blocking .env access
  → Always executes → Exit code 2 → Operation blocked. Period.
```

| Hook                            | Event        | Behavior                                                                                                   |
| ------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------- |
| `block-secrets`                 | PreToolUse   | Blocks Read/Edit on `.env`, SSH keys, credentials, and secret path patterns                                |
| `block-write-outside-repo`      | PreToolUse   | Blocks Edit/Write operations targeting files outside the project directory                                  |
| `block-dangerous-commands`      | PreToolUse   | Blocks `p4 submit`, `p4 obliterate`, `rm -rf /`, `chmod 777`, `curl \| sh`, and secret exfiltration       |
| `p4-commands-permission`        | PreToolUse   | Controls permission prompts for P4 CLI commands in Bash                                                    |
| `verify-no-secrets`             | Stop         | Warns if P4 opened files contain secrets (AWS keys, GitHub tokens, Stripe keys, PEM)                       |
| `check-env-sync`                | Stop         | Warns if `.env` has keys missing from `.env.example`                                                       |
| `after-edit`                    | PostToolUse  | Auto-formats files after edit/write: clang-format (C++), black+ruff (Python), prettier (JS/JSON/MD)       |
| `notify`                        | Notification | Sends desktop notifications when Claude needs attention                                                    |
| `lint-on-stop`                  | Stop         | Runs linters at end of turn: clang-tidy (UE), ruff+mypy (Python), cargo (Rust), go vet (Go)               |
| `p4-auto-checkout`              | PreToolUse   | Auto-runs `p4 edit` before code-dev/blueprint-dev agents modify files                                      |
| `p4-auto-add`                   | PostToolUse  | Auto-runs `p4 add` after code-dev/blueprint-dev agents create new files                                    |

### Hook Lifecycle

| Event              | When It Fires                                  |
| ------------------ | ---------------------------------------------- |
| `UserPromptSubmit` | When the user submits a prompt (before Claude responds) |
| `PreToolUse`       | Before Claude reads, writes, or runs a command |
| `PostToolUse`      | After Claude writes or edits a file            |
| `Stop`             | When Claude finishes a turn                    |
| `Notification`     | When Claude sends a notification to the user   |

### Exit Codes

| Code | Meaning                                                  |
| ---- | -------------------------------------------------------- |
| `0`  | Allow — no action                                        |
| `1`  | Warning — shown, operation continues                     |
| `2`  | **Block** — stderr fed back to Claude, operation stopped |

---

## Templates

### `project/CLAUDE.md`

Master template for auto-generating project-specific `CLAUDE.md` files. Used by `/kc:generate-claude-md` command to:

- Auto-detect tech stack (Unreal Engine via `.uproject`)
- Load tech-specific Q&A guides
- Ask guided questions about project configuration (P4 workspace, Swarm URL, etc.)
- Instantiate template with user answers and auto-detected versions
- Populate all sections: Project Overview, Critical Rules, Tech Stack Details, Service Ports, etc.

### Tech-Stack Guides: `project/docs/tech-stacks/`

Specialized Q&A guides loaded by `/kc:generate-claude-md` when a tech stack is detected.

- **`unreal.md`** — Unreal Engine (9 guided questions: version, project type, setup, platforms, C++ vs Blueprint, plugins, content structure, build targets, do's/don'ts)
- **`helix_perforce.md`** — Perforce (Helix Core) workspace, streams, changelist conventions, submit policy, operational reference
- **`helix_swarm.md`** — Helix Swarm code review integration, review workflow, comment handling, API reference
- **`atlassian_jira.md`** — Jira project setup, issue tracking conventions, operational reference
- **`atlassian_confluence.md`** — Confluence documentation publishing conventions, formatting references
- **`visual_studio.md`** — Visual Studio (UE5 integration): env vars (`KC_UE_SOLUTION`, `KC_UE_ENGINE`, `KC_PROJECT_ROOT`), build config, COM/DTE automation reference, UBT fallback

### Coding Standards

Coding standards live in `project/docs/standards/` reference docs (for multi-consumer review criteria) and directly in their consuming agent files (for single-consumer standards like documentation and Python). Agents and skills reference these shared docs via `@docs/standards/` paths.

### `project/CLAUDE.local.md`

Personal overrides — ignored by VCS, never committed. For individual workflow preferences, local environment details, and project-specific personal notes.

### `global/CLAUDE.md`

Installed once at `~/.claude/CLAUDE.md`. Applies security rules and coding standards across **every** project. Merged with any existing global config — never overwrites.

### `global/settings.json`

Installed once at `~/.claude/settings.json`. Wires up global hooks. Merged with existing settings.

---

## Team Setup

### Shared vs Personal Config

| What | Where | Versioned? | Purpose |
|------|-------|------------|---------|
| Project rules | `CLAUDE.md` | Yes | Team-wide conventions, commit to repo |
| Personal overrides | `CLAUDE.local.md` | No | Individual preferences, never commit |
| Global rules | `~/.claude/CLAUDE.md` | No | Cross-project rules (security, etc.) |

### Rolling Out to a Team

1. **Lead installs first:** Run `/kc:install` and `/kc:generate-claude-md` in the project
2. **Commit the generated files:** `CLAUDE.md`, `.claude/` folder (except `settings.local.json`)
3. **Team members pull:** Everyone gets commands, skills, agents, hooks automatically
4. **Personal setup:** Each member runs `/kc:install-global` once for global hooks
5. **Configure MCPs individually:** Atlassian, GitHub tokens are personal credentials

### Keeping Updated

**Windows (PowerShell):**
```powershell
# In the KahnClaude repo, pull latest
cd C:\tools\kahnclaude
git pull

# In your project, update installed components
cd C:\Projects\YourUE5Project
claude
/kc:update
```

**macOS / Linux:**
```bash
# In the KahnClaude repo, pull latest
cd ~/tools/kahnclaude
git pull

# In your project, update installed components
cd ~/projects/your-ue5-project
claude
/kc:update
```

---

## Key Concepts

### Hooks Are Stronger Than Rules

Three layers of enforcement, strongest to weakest:

1. **`.p4ignore`** — last line of defense, filesystem-level (strongest)
2. **Hooks** — guaranteed to run, blocks operations before they happen
3. **`CLAUDE.md` rules** — behavioral suggestions (weakest — Claude can override under context pressure)

### One Task, One Chat

Research shows **39% performance degradation** when mixing unrelated topics in a single Claude session. Use `/clear` between unrelated tasks. A 2% misalignment early in a conversation can cause **40% failure** by the end.

### Plan First, Code Second

For non-trivial tasks, start in plan mode. Don't let Claude write code until you've agreed on the plan. Every plan step must have a unique name so you can reference and replace steps cleanly.

### CLAUDE.md Is Team Memory

Every time Claude makes a mistake, add a rule to prevent it recurring. The file is in version control — the whole team benefits from every lesson learned.

### Hooks Are Python

All KahnClaude hooks are Python. No bash. Reasons: cross-platform (Windows, WSL, macOS, Linux), no shell quoting edge cases, stdlib-only, easy to test.

---

## Essential Claude Code Commands

Built-in commands that ship with Claude Code. Master these before KahnClaude's specialized workflows.

### Start Here — Learn These First

| Command / Key | What It Does | Why It Matters |
| ------------- | ------------ | -------------- |
| `/help` | List all available commands | Starting point for discovery |
| `Esc` + `Esc` | Open rewind menu (`/rewind`) | Your safety net — undo code or conversation |
| `/context` | Show token consumption | Know when you're running low |

### Listing & Verification

| Command | What It Does |
| ------- | ------------ |
| `/skills` | List all available skills and their triggers |
| `/mcp` | List installed MCP servers and connection status |
| `/plugins` | Browse and install available plugins |
| `/agents` | List running agents |
| `/tasks` | List tracked tasks (`Ctrl+T` to toggle panel) |

### Commands by Scenario

#### Debugging & Fixing

| Command | What It Does |
| ------- | ------------ |
| `/doctor` | Environment diagnostics — first stop for config issues |
| `Esc` | Stop a runaway response |
| `/rewind` | Undo changes (choose code-only or conversation-only) |

#### Large-Scale Tasks

| Command / Key | What It Does |
| ------------- | ------------ |
| `Shift+Tab` | Enter Plan Mode — strategic planning before coding |
| `/agents` | Delegate to parallel sub-agents |
| `/tasks` | Persistent task management (`Ctrl+T` to toggle) |

#### Token Management

| Command | What It Does |
| ------- | ------------ |
| `/compact [focus]` | Summarize conversation (e.g., `/compact focus on errors`) |
| `/context` | Check current token usage |
| `/clear` | Reset conversation — use between unrelated tasks |
| `/cost` | Show token spend for current session |
| `/usage` | Show plan limits and rate status |

#### Learning & Understanding

| Command / Phrase | What It Does |
| ---------------- | ------------ |
| `/output-style` | Switch to "learning" mode for detailed explanations |
| "Grill me on changes" | Request tough review of your work |
| "Step by step" | Get step-by-step walkthrough |

#### Efficiency

| Command | What It Does |
| ------- | ------------ |
| `/insights` | Generate usage report (`~/.claude/usage-data/report.html`) — run monthly |
| `/init` | Initialize CLAUDE.md and project config |
| Custom slash commands | Create project-specific workflows |

#### Team Development

| Command | What It Does |
| ------- | ------------ |
| `/export` | Export conversation to file or clipboard |
| Agent Teams | Collaborative work (experimental) |
| `CLAUDE.md` | Share rules across the team |

### Token Management Checklist

- [ ] Check regularly with `/context`
- [ ] Let auto-compact handle long sessions (manual: `/compact`)
- [ ] Use `/clear` when switching tasks
- [ ] Use `/rewind` to remove unnecessary conversation
- [ ] `/export` before starting a new session if you need history

### Working with Agents

| Guideline | Why |
| --------- | --- |
| Start with 2-3 agents | Learn the workflow before scaling |
| Clarify roles in `CLAUDE.md` | Agents read your project rules |
| Maximum 5 running in parallel | Beyond this, coordination overhead dominates |
| Monitor with `/statusline` | Keep visibility on agent activity |
| Use `/compact` when chaotic | Regain context clarity |

---

## Migrating from Existing Setup

### Already have a CLAUDE.md?

`/kc:generate-claude-md` will **append** KahnClaude sections to your existing file, not overwrite. Review the merged result and remove duplicates.

### Using another Claude Code framework?

Run `/kc:import` to analyze your existing `.claude/` folder and selectively import compatible components.

### Coming from Git?

KahnClaude is optimized for Perforce, but the core components (commands, agents, hooks) work in any project. The P4-specific skills (`/perforce-changelog`, `/swarm-review-shelve`, etc.) simply won't activate without a P4 workspace.

---

## Troubleshooting

### Skill doesn't trigger when I type the keyword

- Check `claude --settings` to verify skills are loaded
- Run `/plugins` to see if required MCPs are connected
- Try explicit invocation: `/skill-name` instead of keywords
- Ensure the skill files were copied: check `.claude/skills/` exists

### Hooks aren't blocking anything

- Verify hooks are wired: check `.claude/settings.json` for `hooks` array
- Test hook manually:
  ```bash
  echo '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | py .claude/hooks/block-secrets.py
  ```
- Check exit code: hook must exit with code 2 to block
- Ensure Python 3.10+ is in your PATH

### MCP connection fails

- Verify Node.js 18+: `node --version`
- Check MCP logs: `claude mcp logs <server-name>`
- Restart Claude Code after adding MCPs
- For Perforce MCP: ensure `p4` CLI is in your PATH and authenticated

### `/kc:install` says "not a UE5 project"

- Ensure `.uproject` file exists in project root
- Run from the directory containing the `.uproject` file
- The command auto-detects UE5 via `.uproject` — other project types work but won't get UE5-specific defaults

### P4 commands fail with "not logged in"

- Run `p4 login` in your terminal before using Claude
- Check `p4 info` shows valid client workspace
- Verify `P4CLIENT`, `P4USER`, `P4PORT` environment variables are set

### Blueprint/PIE skills say "editor not running"

- Start Unreal Editor before using these skills
- Enable Remote Execution Plugin in Editor Preferences
- Check the Python Remote Execution port (default: 9997) isn't blocked

---

## Adding Components

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

| Component           | Location                                      | Naming                                          |
| ------------------- | --------------------------------------------- | ----------------------------------------------- |
| Command (project)   | `.claude/commands/<name>.md`                  | kebab-case action verb                          |
| Command (framework) | `.claude/commands/kc/<name>.md`               | kebab-case action verb; invoked as `/kc:<name>` |
| Skill               | `.claude/skills/<theme>/<name>/SKILL.md`      | kebab-case, reference doc in `project/docs/standards/` |
| Agent               | `.claude/agents/<name>.md`                    | kebab-case role                                 |
| Hook                | `.claude/hooks/<name>.py`                     | `block-`, `check-`, `lint-`, `verify-` prefix   |

---

## Getting Help

- **Issues:** Report bugs and request features on GitHub Issues
- **Contributing:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **License:** See [LICENSE](LICENSE)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions of commands, skills, agents, and hooks are welcome. Bash scripts are not — Python only.
