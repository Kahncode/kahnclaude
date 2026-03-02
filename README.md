# KahnClaude

> A personal Claude Code framework — commands, skills, agents, hooks, and CLAUDE.md templates for effective AI-assisted development across any language or stack.

---

## What Is This?

KahnClaude is a **Claude Code configuration layer**, not a project scaffold or runnable application. It provides the infrastructure that makes Claude dramatically more effective: slash commands, triggered skills, specialist agents, enforcement hooks, and CLAUDE.md templates.

You use it to **configure** projects, not to run them. Drop it into any existing codebase — C++, Python, Rust, C#, web — and Claude immediately gains structured workflows, quality enforcement, and expert templates.

### Two Ways to Use It

**A. Install into an existing project:**

```bash
# Inside a Claude Code session in your project
/kc-install
```

Non-destructive — only adds what's missing. Creates `.claude/` with all components.

**B. Install global config once:**

```bash
# Inside a Claude Code session (one-time, merges with any existing ~/.claude/)
/kc-install-global
```

> **What NOT to do:** Don't expect a runnable app from this repo. This is the configuration layer that enhances Claude in your projects — it's not a project itself.

---

## What's Included

| Component            | Count | Purpose                                          |
| -------------------- | ----- | ------------------------------------------------ |
| **Slash Commands**   | —     | On-demand workflows invoked with `/command`      |
| **Skills**           | —     | Trigger-activated expertise templates            |
| **Agents**           | —     | Specialist subagents with restricted tool access |
| **Hooks**            | —     | Deterministic enforcement scripts (Python)       |
| **Project Template** | 1     | `CLAUDE.md` starting point for any project       |
| **Global Template**  | 1     | `~/.claude/CLAUDE.md` for cross-project rules    |

---

## Quick Start

```bash
# 1. Clone KahnClaude somewhere permanent
git clone <repo-url> ~/tools/kahnclaude

# 2. Install global config (one-time)
#    Open Claude Code from anywhere and run:
/kc-install-global

# 3. In any project, install the Claude layer:
cd ~/your-project
claude
/kc-install

# 4. Customize CLAUDE.md for your project
```

---

## Supported Stacks

KahnClaude is **language-agnostic**. Components are designed to work across:

| Category            | Supported                                          |
| ------------------- | -------------------------------------------------- |
| **Languages**       | Python, Rust, C++, C#, TypeScript/JavaScript, Go   |
| **Environments**    | Windows, WSL2, macOS, Linux                        |
| **Editors**         | VS Code (primary), any editor with terminal access |
| **Version Control** | Git                                                |

---

## Project Structure

```
kahnclaude/
├── README.md
├── CONTRIBUTING.md
├── CLAUDE.md                    # This repo's own Claude rules
├── LICENSE
├── .gitignore
│
├── .claude/                     # All Claude components (framework + distributable)
│   ├── settings.json            # Hooks wiring for this framework repo
│   ├── commands/                # Slash commands
│   │   └── <name>.md            # scope: project → distributed | scope: framework → local
│   ├── skills/                  # Triggered expertise templates
│   │   └── <name>/
│   │       └── SKILL.md
│   ├── agents/                  # Specialist subagents
│   │   └── <name>.md
│   └── hooks/                   # Enforcement scripts (Python only)
│       └── <name>.py
│
├── templates/                   # CLAUDE.md templates for new projects
│   ├── CLAUDE.md
│   └── CLAUDE.local.md
│
├── global/                      # Global ~/.claude/ config templates
│   ├── CLAUDE.md
│   └── settings.json
│
└── inspiration/                 # Third-party reference — NEVER MODIFY
```

---

## Commands — On-Demand Workflows

Invoke with `/command-name` inside any Claude Code session. Commands are Markdown files with YAML frontmatter. Two scopes:

- **`scope: project`** — distributed to target projects via `/kc-install`
- **`scope: framework`** — KahnClaude management only, never distributed

### Framework Commands

| Command              | What It Does                                                          |
| -------------------- | --------------------------------------------------------------------- |
| `/kc-install`        | Install KahnClaude components into the current project                |
| `/kc-install-global` | Merge global config into `~/.claude/` (smart merge, never overwrites) |
| `/kc-update`         | Update installed components from the latest framework source          |

### Project Commands

| Command             | Scope | What It Does |
| ------------------- | ----- | ------------ |
| _(to be populated)_ |       |              |

---

## Skills — Triggered Expertise

Skills activate automatically when Claude detects trigger keywords in conversation. No explicit invocation needed.

| Skill               | Triggers | What It Does |
| ------------------- | -------- | ------------ |
| _(to be populated)_ |          |              |

---

## Agents — Specialist Subagents

Agents are specialists Claude delegates to automatically. Each has restricted tool access appropriate to its role.

| Agent               | Tools | Specialization |
| ------------------- | ----- | -------------- |
| _(to be populated)_ |       |                |

---

## Hooks — Enforcement Over Suggestion

CLAUDE.md rules are suggestions. Hooks are **deterministic** — they always run as Python scripts at specific lifecycle points.

```
CLAUDE.md rule: "don't read .env"
  → Parsed by LLM → Weighed against context → Maybe followed

PreToolUse hook blocking .env access
  → Always executes → Exit code 2 → Operation blocked. Period.
```

| Hook                | Event | Behavior |
| ------------------- | ----- | -------- |
| _(to be populated)_ |       |          |

### Hook Lifecycle

| Event         | When It Fires                                  |
| ------------- | ---------------------------------------------- |
| `PreToolUse`  | Before Claude reads, writes, or runs a command |
| `PostToolUse` | After Claude writes or edits a file            |
| `Stop`        | When Claude finishes a turn                    |

### Exit Codes

| Code | Meaning                                                  |
| ---- | -------------------------------------------------------- |
| `0`  | Allow — no action                                        |
| `1`  | Warning — shown, operation continues                     |
| `2`  | **Block** — stderr fed back to Claude, operation stopped |

---

## Templates

### `templates/CLAUDE.md`

Starting point for a new project's `CLAUDE.md`. Contains numbered critical rules covering:

- Secret management
- Deployment gates
- Quality gates (file/function size limits)
- Branch workflow
- Project-specific slots to fill

### `templates/CLAUDE.local.md`

Personal overrides — gitignored, never committed. For individual workflow preferences, local environment details, and project-specific personal notes.

### `global/CLAUDE.md`

Installed once at `~/.claude/CLAUDE.md`. Applies security rules and coding standards across **every** project. Merged with any existing global config — never overwrites.

### `global/settings.json`

Installed once at `~/.claude/settings.json`. Wires up global hooks. Merged with existing settings.

---

## Key Concepts

### Hooks Are Stronger Than Rules

Three layers of enforcement, strongest to weakest:

1. **`.gitignore`** — last line of defense, filesystem-level (strongest)
2. **Hooks** — guaranteed to run, blocks operations before they happen
3. **`CLAUDE.md` rules** — behavioral suggestions (weakest — Claude can override under context pressure)

### One Task, One Chat

Research shows **39% performance degradation** when mixing unrelated topics in a single Claude session. Use `/clear` between unrelated tasks. A 2% misalignment early in a conversation can cause **40% failure** by the end.

### Plan First, Code Second

For non-trivial tasks, start in plan mode. Don't let Claude write code until you've agreed on the plan. Every plan step must have a unique name so you can reference and replace steps cleanly.

### CLAUDE.md Is Team Memory

Every time Claude makes a mistake, add a rule to prevent it recurring. The file is in git — the whole team benefits from every lesson learned.

### Hooks Are Python

All KahnClaude hooks are Python. No bash. Reasons: cross-platform (Windows, WSL, macOS, Linux), no shell quoting edge cases, stdlib-only, easy to test.

---

## Adding Components

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

| Component | Location                         | Naming                                        |
| --------- | -------------------------------- | --------------------------------------------- |
| Command   | `.claude/commands/<name>.md`     | kebab-case action verb                        |
| Skill     | `.claude/skills/<name>/SKILL.md` | kebab-case category                           |
| Agent     | `.claude/agents/<name>.md`       | kebab-case role                               |
| Hook      | `.claude/hooks/<name>.py`        | `block-`, `check-`, `lint-`, `verify-` prefix |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions of commands, skills, agents, and hooks are welcome. Bash scripts are not — Python only.
