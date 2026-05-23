# KahnClaude Unreal Engine

> A Claude Code framework for UE5 + Perforce + Jira game development — commands, agents, hooks, and CLAUDE.md templates for effective AI-assisted Unreal Engine workflows.

---

## Table of Contents

- [What Is This?](#what-is-this)
- [What's Included](#whats-included)
- [Quick Start](#quick-start)
- [Supported Stack](#supported-stack)
- [Project Structure](#project-structure)
- [Plugins & MCPs](#plugins--mcps)
- [Commands — On-Demand Workflows](#commands--on-demand-workflows)
- [Skills — Focused Workflows](#skills--focused-workflows-14)
- [Agents — Specialist Subagents](#agents--specialist-subagents-8)
- [Hooks — Enforcement Over Suggestion](#hooks--enforcement-over-suggestion)
- [Templates](#templates)
- [Key Concepts](#key-concepts)
- [Adding Components](#adding-components)
- [Contributing](#contributing)

---

## What Is This?

KahnClaude Unreal Engine is a **Claude Code configuration layer** specialized for Unreal Engine 5 game development with Perforce (Helix Core) for version control and Jira for issue tracking. It provides the infrastructure that makes Claude dramatically more effective: slash commands, specialist agents, enforcement hooks, and CLAUDE.md templates.

---

## What's Included

| Component             | Count | Purpose                                                                   |
| --------------------- | ----- | ------------------------------------------------------------------------- |
| **Slash Commands**    | 14    | On-demand workflows invoked with `/command` (6 project + 8 framework)             |
| **Skills**            | 14    | Focused skills with colocated reference docs, auto-triggered + user-invokable     |
| **Agents**            | 8     | Specialist subagents with restricted tool access                          |
| **Hooks**             | 9     | Deterministic enforcement scripts (Python)                                |
| **Tech-Stack Guides** | 6     | Compact Q&A + operational reference guides for CLAUDE.md generation (UE5, Perforce, Swarm, Jira, Confluence, Visual Studio) |

---

## Quick Start

```bash
# 1. Clone KahnClaude somewhere permanent
git clone <repo-url> ~/tools/kahnclaude

# 2. Install KahnClaude in your UE5 project,
cd ~/tools/kahnclaude
claude
/kc:install your-ue5-project-path

# Open Claude Code from your-ue5-project-path

# 3. Customize CLAUDE.md for your project
/generate-claude-md

# 4. Configure Plugins for Perforce, Jira, and your tools (see Plugins & MCPs section below)
/plugins

# 5. Build Claude's knowledge base of your project
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

## Plugins & MCPs

Plugins and MCPs extend Claude Code with additional capabilities. **Plugins** add slash commands, skills, and automation. **MCPs** (Model Context Protocol servers) connect Claude to external tools, docs, and services.

> **Discovery:** Run `/plugins` to browse and install available plugins and MCPs directly from Claude Code.

### Always Recommended

These are useful in virtually every project. Install globally for convenience.

| Name | Type | What It Adds | Install |
| ---- | ---- | ------------ | ------- |
| **Context7** | MCP | Up-to-date library docs and code examples pulled at query time — eliminates hallucinated APIs | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` |
| **GitHub** | MCP | Read issues, PRs, and code from any repo without leaving Claude | `claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'` |
| **Filesystem** | MCP | Lets Claude read/write files outside the project root (cross-repo work, config management) | `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allow` |
| **claude-warden** | Plugin | Permission manager — pre-approves safe bash commands to eliminate repetitive allow/deny prompts | `/plugins` → search "warden" |
| **skill-creator** | Plugin | Create, edit, and optimize skills with eval-driven development and performance benchmarking | `/plugins` → search "skill-creator" |

### Game Dev Recommendations

| Name | Type | What It Adds | Install |
| ---- | ---- | ------------ | ------- |
| **Perforce** | MCP | P4 operations (changelists, shelve, diff, sync, streams) without leaving Claude | `claude mcp add perforce -- npx -y mcp-perforce-server@latest` |
| **Atlassian** | MCP | Confluence, Read/write Jira issues — enables Jira skills and producer agent | Built-in — enable at [claude.ai/settings/connectors](https://claude.ai/settings/connectors) |
| **UnrealClaude** | MCP | 20+ MCP tools for UE5.7 — actor manipulation, blueprint editing, level management, materials, input systems, and on-demand API docs | UE5 editor plugin — see [UnrealClaude](https://github.com/Natfii/UnrealClaude) |

### Finding More

- **`/plugins`** — browse and install from within Claude Code
- Official MCP catalog: https://code.claude.com/docs/en/mcp
- Community MCP registry: https://mcpservers.org/

---

## Commands — On-Demand Workflows

Invoke with `/command-name` inside any Claude Code session. Commands are Markdown files with YAML frontmatter. Two scopes:

- **`scope: project`** — distributed to target projects via `/kc:install`; live in `.claude/commands/`
- **`scope: framework`** — KahnClaude management only, never distributed; live in `.claude/commands/kc/`, invoked as `/kc:<name>`

### Framework Commands (8)

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

### General Commands (6)

| Command                    | What It Does                                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `/answer`                  | Research a question using general knowledge, codebase search, Context7 docs, or web search                 |
| `/document`                | Build or update project docs: no args = ARCHITECTURE.md index, with args = subsystem deep-dive             |
| `/explain`                 | Explain code in detail — overview, components, control flow, dependencies, gotchas, usage                  |
| `/learn`                   | Update docs from a P4 changelist number, CL range, a plain-text fact, or auto-detected opened/pending     |
| `/progress`                | Show file counts, test status, recent P4 submitted/pending activity, and next actions                      |
| `/refactor`                | Refactor a file against CLAUDE.md rules — split, extract, clean up                                         |

---

## Skills — Focused Workflows (14)

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

---

## Agents — Specialist Subagents (8)

Agents are specialists Claude delegates to automatically. Each has restricted tool access appropriate to its role.

### Core (8)

Cross-cutting specialists used across any tech stack.

| Agent                         | Tools                                | Specialization                                                               |
| ----------------------------- | ------------------------------------ | ---------------------------------------------------------------------------- |
| `core/blueprint-dev`          | Read, Write, Edit, Grep, Glob, Bash | Blueprint asset specialist — manipulates UE5 Blueprint properties via Python Remote Execution |
| `core/blueprint-reviewer`     | Read, Grep, Glob, Bash              | Blueprint asset reviewer — inspects properties via Python Remote Execution, read-only |
| `core/code-dev`               | Read, Write, Edit, Grep, Glob, Bash | UE5 C++ — gathers context, plans, implements with P4 changelist discipline, validates via full build |
| `core/code-reviewer`          | Read, Grep, Glob, Bash(p4)          | C++/UE5 code reviewer: security, correctness, performance, C++ craft, engine pitfalls, Blueprint boundary |
| `core/designer`               | Read, Write, Edit, Grep, Glob, Confluence+Jira MCP | Game design specialist — balance decisions, system design, local game wiki generation, Confluence wiki management |
| `core/documenter`             | Read, Write, Edit, Grep, Glob       | Architecture docs, subsystem docs, Mermaid diagrams, Decisions logs          |
| `core/producer`               | Read, Grep, Glob, Jira MCP          | Fetches Jira tickets, clarifies technical requirements, identifies cross-team dependencies, gathers estimates, and creates well-structured tickets |
| `core/python-dev`             | Read, Write, Edit, Bash, Grep, Glob, WebFetch | Modern Python 3.12+ — architecture, packaging, async, type system         |

---

## Hooks — Enforcement Over Suggestion

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

### `@project/CLAUDE.md`

Master template for auto-generating project-specific `CLAUDE.md` files. Used by `/tool:generate-claude-md` command to:

- Auto-detect tech stack (Unreal Engine via `.uproject`)
- Load tech-specific Q&A guides
- Ask guided questions about project configuration (P4 workspace, Swarm URL, etc.)
- Instantiate template with user answers and auto-detected versions
- Populate all sections: Project Overview, Critical Rules, Tech Stack Details, Service Ports, etc.

### Tech-Stack Guides: `@project/docs/tech-stacks/`

Specialized Q&A guides loaded by `/tool:generate-claude-md` when a tech stack is detected.

- **`unreal.md`** — Unreal Engine (9 guided questions: version, project type, setup, platforms, C++ vs Blueprint, plugins, content structure, build targets, do's/don'ts)
- **`helix_perforce.md`** — Perforce (Helix Core) workspace, streams, changelist conventions, submit policy, operational reference
- **`helix_swarm.md`** — Helix Swarm code review integration, review workflow, comment handling, API reference
- **`atlassian_jira.md`** — Jira project setup, issue tracking conventions, operational reference
- **`atlassian_confluence.md`** — Confluence documentation publishing conventions, formatting references
- **`visual_studio.md`** — Visual Studio (UE5 integration): env vars (`KC_UE_SOLUTION`, `KC_UE_ENGINE`, `KC_PROJECT_ROOT`), build config, COM/DTE automation reference, UBT fallback

### Coding Standards

Coding standards live in `project/docs/standards/` reference docs (for multi-consumer review criteria) and directly in their consuming agent files (for single-consumer standards like documentation and Python). Agents and skills reference these shared docs via `@docs/standards/` paths.

### `@project/CLAUDE.local.md`

Personal overrides — ignored by VCS, never committed. For individual workflow preferences, local environment details, and project-specific personal notes.

### `@global/CLAUDE.md`

Installed once at `@~/.claude/CLAUDE.md`. Applies security rules and coding standards across **every** project. Merged with any existing global config — never overwrites.

### `@global/settings.json`

Installed once at `@~/.claude/settings.json`. Wires up global hooks. Merged with existing settings.

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

## Adding Components

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

| Component           | Location                                      | Naming                                          |
| ------------------- | --------------------------------------------- | ----------------------------------------------- |
| Command (project)   | `.claude/commands/<name>.md`                  | kebab-case action verb                          |
| Command (framework) | `.claude/commands/kc/<name>.md`               | kebab-case action verb; invoked as `/kc:<name>` |
| Skill               | `.claude/skills/<theme>/<name>/SKILL.md`      | kebab-case, reference doc in `project/docs/standards/` |
| Agent               | `.claude/agents/<name>.md`                    | kebab-case role                                 |
| Hook                | `.claude/hooks/<name>.py`                     | `block-`, `check-`, `lint-`, `verify-` prefix   |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions of commands, skills, agents, and hooks are welcome. Bash scripts are not — Python only.
