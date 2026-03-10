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
/kc:install
```

Non-destructive — only adds what's missing. Creates `.claude/` with all components.

**B. Install global config once:**

```bash
# Inside a Claude Code session (one-time, merges with any existing ~/.claude/)
/kc:install-global
```

> **What NOT to do:** Don't expect a runnable app from this repo. This is the configuration layer that enhances Claude in your projects — it's not a project itself.

---

## What's Included

| Component             | Count | Purpose                                                                   |
| --------------------- | ----- | ------------------------------------------------------------------------- |
| **Slash Commands**    | 22    | On-demand workflows invoked with `/command`                               |
| **Skills**            | 0     | Trigger-activated expertise templates                                     |
| **Agents**            | 19    | Specialist subagents with restricted tool access                          |
| **Hooks**             | 8     | Deterministic enforcement scripts (Python)                                |
| **Project Template**  | 1     | Master `CLAUDE.md` with guide comments (used by `/kc:generate-claude-md`) |
| **Tech-Stack Guides** | 1+    | Unreal Engine + placeholders for future stacks                            |
| **Global Template**   | 1     | `@~/.claude/CLAUDE.md` for cross-project rules                            |

---

## Quick Start

```bash
# 1. Clone KahnClaude somewhere permanent
git clone <repo-url> ~/tools/kahnclaude

# 2. Install global config (one-time)
#    Open Claude Code from anywhere and run:
/kc:install-global

# 3. In any project, install the Claude layer:
cd ~/your-project
claude
/kc:install

# 4. Customize CLAUDE.md for your project

# 5. Configure MCPs for your tools and stack (see MCP section below)

# 6. Build Claude's knowledge base of your project:
/document
```

> **Step 6:** `/document` creates an `ARCHITECTURE.md` and subsystem docs so Claude understands your codebase from the first session. Run it once after setup. You may document more subsystems using the /document skill. Use `/learn` to update documentation from the current context as you go.

---

## MCP Servers

MCP (Model Context Protocol) servers extend Claude with real-time access to external tools, docs, and services. Add them globally with `claude mcp add -s user ...` or per-project with `claude mcp add ...`.

### Always Recommended

These MCPs are useful in virtually every project. MCPs are project-scoped by default. We recommend installing those globally using `claude mcp add --scope user`.

| MCP            | What It Adds                                                                                  | Install                                                                                                                                       |
| -------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **Context7**   | Up-to-date library docs and code examples pulled at query time — eliminates hallucinated APIs | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest`                                                                              |
| **GitHub**     | Read issues, PRs, and code from any repo without leaving Claude                               | `claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'` |
| **Filesystem** | Lets Claude read/write files outside the project root (cross-repo work, config management)    | `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /path/to/allow`                                                  |

### Project-Type Recommendations

| Project Type                 | Recommended MCPs                                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Web / SaaS**               | Playwright (browser automation, E2E testing), Figma (design specs), Notion (product docs), Linear or Jira |
| **Game Dev (Unreal Engine)** | Unreal Engine MCP (Blueprint/C++ introspection), Perforce MCP (if using P4)                               |
| **Data / ML**                | PostgreSQL or SQLite MCP (query live data)                                                                |
| **Mobile**                   | Figma MCP (design handoff), Firebase or Supabase MCP                                                      |
| **DevOps**                   | Docker MCP, AWS/GCP/Azure MCPs                                                                            |

### Finding More MCPs

- Official catalog: https://code.claude.com/docs/en/mcp
- Community registry: https://mcpservers.org/

Look for MCPs matching **your specific tools and workflow** — project management (Jira, Linear, Notion), design (Figma), communication (Gmail, Slack), version control (GitHub, Perforce), and tech-stack specific (Supabase, Unreal Engine...). A well-chosen MCP can eliminate entire categories of copy-paste between Claude and your tools.

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
│   │   ├── <name>.md            # scope: project → distributed to projects
│   │   └── kc/                  # scope: framework → KahnClaude management only
│   │       └── <name>.md        # invoked as /kc:<name>
│   ├── skills/                  # Triggered expertise templates
│   │   └── <name>/
│   │       └── SKILL.md
│   ├── agents/                  # Specialist subagents
│   │   ├── <name>.md            # Universal agents
│   │   ├── core/                # Cross-cutting specialists
│   │   ├── python/              # Python specialists
│   │   ├── web/                 # Web/React specialists
│   │   └── mobile/              # React Native/Expo specialists
│   └── hooks/                   # Enforcement scripts (Python only)
│       └── <name>.py
│
├── project/                     # CLAUDE.md templates for new projects
│   ├── CLAUDE.md                # Master template with guide comments (used by /kc:generate-claude-md)
│   ├── CLAUDE.local.md
│   └── tech-stacks/             # Tech-specific Q&A guides for auto-generation
│       ├── unreal.md            # Unreal Engine detection + 8 guided questions
│       ├── react-nextjs.md      # (Placeholder for future implementation)
│       └── [more stacks...].md
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

- **`scope: project`** — distributed to target projects via `/kc:install`; live in `.claude/commands/`
- **`scope: framework`** — KahnClaude management only, never distributed; live in `.claude/commands/kc/`, invoked as `/kc:<name>`

### Framework Commands

| Command                  | What It Does                                                                      |
| ------------------------ | --------------------------------------------------------------------------------- |
| `/kc:install`            | Install KahnClaude components into the current project                            |
| `/kc:install-global`     | Merge global config into `~/.claude/` (smart merge, never overwrites)             |
| `/kc:update`             | Update installed components from the latest framework source                      |
| `/kc:import`             | Analyze a repo's Claude Code components and selectively integrate into KahnClaude |
| `/kc:create-agent-skill` | Create a new agent, skill, or slash command following framework conventions       |
| `/kc:fix-agent-skill`    | Debug a misbehaving agent or skill — session analysis + convention audit          |

### Project Commands

| Command                  | What It Does                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `/kc:generate-claude-md` | Auto-detect tech stack and generate a complete CLAUDE.md; use `--additive` to enhance existing |
| `/review`                | Review current diff for bugs, security issues, and best practices                              |
| `/commit`                | Generate a conventional commit message and commit staged changes                               |
| `/worktree`              | Create a git worktree + branch for isolated task work                                          |
| `/refactor`              | Refactor a file against CLAUDE.md rules — split, extract, clean up                             |
| `/progress`              | Show file counts, test status, recent git activity, and next actions                           |
| `/document`              | Build or update project docs: no args = ARCHITECTURE.md index, with args = subsystem deep-dive |
| `/learn`                 | Update docs from a git SHA, SHA range, a plain-text fact, or auto-detected changes             |
| `/linear`                | Implement a Linear issue — set In Progress, branch, plan, code, test, PR                       |
| `/jira`                  | Implement a Jira issue — transition In Progress, branch, plan, code, test, PR                  |
| `/pr`                    | Generate a PR title and description from the current branch diff; optionally create via `gh`   |
| `/explain`               | Explain code in detail — overview, components, control flow, dependencies, gotchas, usage      |
| `/answer`                | Research a question using general knowledge, codebase search, Context7 docs, or web search     |
| `/test`                  | Generate tests by delegating to the `test-writer` agent (single source of truth)               |
| `/security-check`        | Scan for exposed secrets, missing .gitignore entries, and unsafe patterns                      |

---

## Skills — Triggered Expertise

Skills activate automatically when Claude detects trigger keywords in conversation. No explicit invocation needed.

No skills are included yet. Skills activate automatically when Claude detects trigger keywords. Use `/kc:create-agent-skill` to add one.

---

## Agents — Specialist Subagents

Agents are specialists Claude delegates to automatically. Each has restricted tool access appropriate to its role.

### Universal

| Agent           | Tools                                                    | Specialization                                                                                        |
| --------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `code-reviewer` | Read, Grep, Glob                                         | Finds real bugs: security → correctness → performance → maintainability                               |
| `test-writer`   | Read, Write, Grep, Glob, Bash                            | Writes behavior tests with explicit assertions and edge cases                                         |
| `documenter`    | Read, Write, Edit, Grep, Glob                            | Architecture docs, subsystem docs, Mermaid diagrams, Decisions logs, READMEs, API specs, user manuals |
| `api-dev`       | Read, Grep, Glob, Write, WebFetch, WebSearch             | Designs REST/GraphQL contracts; produces OpenAPI/GraphQL specs                                        |
| `backend-dev`   | Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch | Polyglot backend implementer; detects stack and ships production-ready features                       |

### Core (cross-cutting)

| Agent                         | Tools                  | Specialization                                                               |
| ----------------------------- | ---------------------- | ---------------------------------------------------------------------------- |
| `core/code-archaeologist`     | Read, Grep, Glob, Bash | Deep codebase explorer; produces 11-section assessment report                |
| `core/performance-optimizer`  | Read, Grep, Glob, Bash | Profiles bottlenecks and applies high-impact fixes with before/after metrics |
| `core/tech-lead-orchestrator` | Read, Grep, Glob, Bash | Orchestrates multi-step tasks by assigning sub-agents; uses Opus 4.6         |

### Python

| Agent                    | Tools                                         | Specialization                                                                     |
| ------------------------ | --------------------------------------------- | ---------------------------------------------------------------------------------- |
| `python/fastapi-dev`     | Read, Write, Grep, Glob, Bash                 | Full-stack FastAPI specialist — endpoints, schemas, auth, and tests; version-aware |
| `python/python-dev`      | Read, Write, Edit, Bash, Grep, Glob, WebFetch | Modern Python 3.12+ — architecture, packaging, async, type system                  |
| `python/security-dev`    | Read, Grep, Glob, Bash, WebFetch              | Cryptography, OWASP audits, auth flows, compliance                                 |
| `python/devops-cicd-dev` | Read, Write, Edit, Bash, Grep, Glob, WebFetch | CI/CD pipelines, Docker/K8s, IaC, cloud deployments                                |

### Web

| Agent                     | Tools                                         | Specialization                                                                      |
| ------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------- |
| `web/frontend-dev`        | Read, Grep, Glob, Bash, Write, Edit, WebFetch | Universal UI builder; React, Svelte, or vanilla JS/TS                               |
| `web/tailwind-css-dev`    | Read, Grep, Glob, Bash, Write, Edit, WebFetch | Tailwind CSS v4+; container queries, OKLCH themes, accessibility                    |
| `web/react-component-dev` | (all)                                         | React 19 + Next.js App Router; RSC, shadcn/ui, accessible components                |
| `web/react-nextjs-dev`    | (all)                                         | Next.js SSR/SSG/ISR, Server Actions, App Router, performance optimization           |
| `web/supabase-dev`        | Read, Write, Edit, Grep, Glob, Bash, WebFetch | Supabase + PostgreSQL — auth, RLS, schema design, Storage, Realtime, Edge Functions |

### Mobile

| Agent                               | Tools                         | Specialization                                                                                    |
| ----------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------- |
| `mobile/react-native-expo-dev`      | Read, Write, Grep, Glob, Bash | Senior Expo/React Native specialist; TypeScript-first; checks SDK version before writing any code |
| `mobile/react-native-component-dev` | Read, Write, Grep, Glob, Bash | Reusable RN UI components; component API design, design systems, Reanimated 3, accessibility      |

---

## Hooks — Enforcement Over Suggestion

CLAUDE.md rules are suggestions. Hooks are **deterministic** — they always run as Python scripts at specific lifecycle points.

```
CLAUDE.md rule: "don't read .env"
  → Parsed by LLM → Weighed against context → Maybe followed

PreToolUse hook blocking .env access
  → Always executes → Exit code 2 → Operation blocked. Period.
```

| Hook                       | Event        | Behavior                                                                                                                    |
| -------------------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `block-secrets`            | PreToolUse   | Blocks Read/Edit on `.env`, SSH keys, credentials, and secret path patterns                                                 |
| `block-dangerous-commands` | PreToolUse   | Blocks `rm -rf /`, force-push to main, `chmod 777`, `curl \| sh`, `mkfs`, and secret exfiltration                           |
| `verify-no-secrets`        | Stop         | Warns if staged files contain secrets (AWS keys, GitHub tokens, Stripe keys, PEM)                                           |
| `check-branch`             | PreToolUse   | Blocks `git commit` on `main`/`master` when `KC_BRANCH_PROTECT=true` or marker file present                                 |
| `check-env-sync`           | Stop         | Warns if `.env` has keys missing from `.env.example`                                                                        |
| `after-edit`               | PostToolUse  | Auto-formats files after edit/write: prettier (JS/TS/JSON/MD/CSS), black+ruff (Python), gofmt (Go), rustfmt (Rust)          |
| `notify`                   | Notification | Sends desktop notifications when Claude needs attention (Windows toast, macOS, Linux, terminal bell fallback)               |
| `lint-on-stop`             | Stop         | Runs linters at end of turn: ruff+mypy (Python), cargo check+clippy (Rust), go vet+staticcheck (Go), npm lint+tsc (Node/TS) |

### Hook Lifecycle

| Event          | When It Fires                                  |
| -------------- | ---------------------------------------------- |
| `PreToolUse`   | Before Claude reads, writes, or runs a command |
| `PostToolUse`  | After Claude writes or edits a file            |
| `Stop`         | When Claude finishes a turn                    |
| `Notification` | When Claude sends a notification to the user   |

### Exit Codes

| Code | Meaning                                                  |
| ---- | -------------------------------------------------------- |
| `0`  | Allow — no action                                        |
| `1`  | Warning — shown, operation continues                     |
| `2`  | **Block** — stderr fed back to Claude, operation stopped |

---

## Templates

### `@project/CLAUDE.md`

Master template for auto-generating project-specific `CLAUDE.md` files. Used by `/kc:generate-claude-md` command to:

- Auto-detect tech stack (Unreal, Node.js, Python, Rust, etc.)
- Load tech-specific Q&A guides (e.g., Unreal Engine)
- Ask guided questions about project configuration
- Instantiate template with user answers and auto-detected versions
- Populate all sections: Project Overview, Critical Rules, Tech Stack Details, Service Ports, etc.

Every section includes `<!-- GUIDE: ... -->` comments explaining purpose, format, and examples so users understand what to put where.

### Tech-Stack Guides: `@project/tech-stacks/`

Specialized Q&A guides loaded by `/kc:generate-claude-md` when a tech stack is detected.

- **`unreal.md`** — Unreal Engine (8 guided questions: version, project type, platforms, C++ vs Blueprint, plugins, content structure, build targets, do's/don'ts)
- **`react-nextjs.md`** — React / Next.js (placeholder for future; guides in progress)
- **`[more stacks].md`** — Additional stacks (Django, Rust, C#/.NET) can be added following the same pattern

When `/kc:generate-claude-md` detects a manifest file (`.uproject`, `package.json`, `pyproject.toml`, etc.), it loads the matching guide and asks all questions to build a complete, annotated CLAUDE.md.

### `@project/CLAUDE.local.md`

Personal overrides — gitignored, never committed. For individual workflow preferences, local environment details, and project-specific personal notes.

### `@global/CLAUDE.md`

Installed once at `@~/.claude/CLAUDE.md`. Applies security rules and coding standards across **every** project. Merged with any existing global config — never overwrites.

### `@global/settings.json`

Installed once at `@~/.claude/settings.json`. Wires up global hooks. Merged with existing settings.

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

| Component           | Location                         | Naming                                          |
| ------------------- | -------------------------------- | ----------------------------------------------- |
| Command (project)   | `.claude/commands/<name>.md`     | kebab-case action verb                          |
| Command (framework) | `.claude/commands/kc/<name>.md`  | kebab-case action verb; invoked as `/kc:<name>` |
| Skill               | `.claude/skills/<name>/SKILL.md` | kebab-case category                             |
| Agent               | `.claude/agents/<name>.md`       | kebab-case role                                 |
| Hook                | `.claude/hooks/<name>.py`        | `block-`, `check-`, `lint-`, `verify-` prefix   |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions of commands, skills, agents, and hooks are welcome. Bash scripts are not — Python only.
