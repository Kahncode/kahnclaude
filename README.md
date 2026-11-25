# KahnClaude

> A personal framework for AI coding agents — skills, agents, hooks, and AGENTS.md templates for effective AI-assisted development across any language or stack. Claude Code first; Codex, OpenCode and pi share the same files.

---

## What Is This?

KahnClaude is an **agent configuration layer**, not a project scaffold or runnable application. It provides the infrastructure that makes coding agents dramatically more effective: skills (including slash-command workflows), specialist agents, enforcement hooks, and AGENTS.md templates.

You use it to **configure** projects, not to run them. Drop it into any existing codebase — C++, Python, Rust, C#, web — and Claude immediately gains structured workflows, quality enforcement, and expert templates.

### Two Ways to Use It

**A. Install into an existing project:**

```bash
# Inside a Claude Code session in your project
/kc-install
```

Non-destructive — only adds what's missing. Creates `AGENTS.md` (plus a one-line `CLAUDE.md` shim), `.agents/skills/`, and the Claude Code agents, hooks and settings under `.claude/`. Existing Claude-only installs migrate with `/kc-update` (see [Harness Support](#harness-support)).

**B. Install global config once:**

```bash
# Inside a Claude Code session (one-time, merges with any existing ~/.claude/)
/kc-install-global
```

> **What NOT to do:** Don't expect a runnable app from this repo. This is the configuration layer that enhances Claude in your projects — it's not a project itself.

---

## What's Included

| Component             | Count | Purpose                                                                   |
| --------------------- | ----- | ------------------------------------------------------------------------- |
| **Skills**            | 28    | Shared workflows and expertise (21 project, 7 framework), `/name` to invoke |
| **Agents**            | 19    | Specialist subagents with restricted tool access                          |
| **Hooks**             | 3     | Claude Code hooks for what the harness lacks natively (Python)            |
| **Project Template**  | 1     | Master `AGENTS.md` with guide comments (used by `/kc-generate-agents-md`) |
| **Tech-Stack Guides** | 4+    | Unreal, Astro, Next.js, FastAPI (+ placeholders for future stacks)        |
| **Global Template**   | 1     | `@~/.claude/CLAUDE.md` for cross-project rules                            |

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

# 4. Customize AGENTS.md for your project

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
| **Context7**   | Version-specific library docs pulled at query time — covers APIs newer than the model's training cutoff. Free tier is rate-limited; add an API key (`--header "CONTEXT7_API_KEY: ..."`, never committed) for heavy use | `claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp`                                                          |
| **GitHub**     | Read issues, PRs, and code from any repo without leaving Claude                               | `claude mcp add-json github '{"type":"http","url":"https://api.githubcopilot.com/mcp","headers":{"Authorization":"Bearer YOUR_GITHUB_PAT"}}'` |

> **No Filesystem MCP needed.** Claude Code's built-in file tools cover it. To give access outside the project root, use `--add-dir`, `/add-dir`, or `permissions.additionalDirectories` in `settings.json`. Unlike the MCP, these keep permission rules, the sandbox, and checkpoints in effect.

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

## Plugins

Plugins extend Claude Code itself — adding slash commands, skills, and automation at the editor level rather than at the MCP/tool level.

### Recommended for Web UI Projects

| Plugin | What It Adds | Install |
| ------ | ------------ | ------- |
| **impeccable** | Frontend design skill — design, critique, audit, polish and harden web UI (typography, layout, color, motion, accessibility) | `/plugin marketplace add pbakaus/impeccable` then `/plugin install impeccable@impeccable` |

> **Why impeccable?** Steers Claude away from generic AI-looking interfaces and gives it structured commands for UX review, visual hierarchy, and design-system work.

### Finding More Plugins

Browse the Claude Code plugin marketplace from inside any session:

```
/plugin marketplace list
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
├── AGENTS.md                    # This repo's own agent rules
├── CLAUDE.md                    # One-line shim: @AGENTS.md
├── LICENSE
├── .gitignore
│
├── .agents/                     # Harness-neutral components (read by Codex, OpenCode, pi)
│   └── skills/                  # Skills and slash-command workflows
│       └── <name>/
│           ├── SKILL.md         # scope: project → distributed; scope: framework → never distributed
│           └── scripts/         # helper scripts bundled with the skill (e.g. kc-create-project)
│
├── .claude/                     # Claude Code components (framework + distributable)
│   ├── settings.json            # Hooks wiring for this framework repo
│   ├── skills/                  # Gitignored projection of .agents/skills (link_skills.py hook)
│   ├── agents/                  # Specialist subagents
│   │   ├── <name>.md            # Universal agents
│   │   ├── core/                # Cross-cutting specialists
│   │   ├── python/              # Python specialists
│   │   ├── frontend/            # Web/React specialists
│   │   └── mobile/              # React Native/Expo specialists
│   └── hooks/                   # Claude Code hooks (Python only)
│       └── <name>.py
│
├── project/                     # Templates for new projects
│   ├── AGENTS.md                # Master template with guide comments (used by /kc-generate-agents-md)
│   ├── CLAUDE.md                # One-line shim: @AGENTS.md
│   ├── CLAUDE.local.md          # Optional Claude-only personal overrides
│   └── tech-stacks/             # Tech-specific Q&A guides for auto-generation
│       ├── unreal.md            # Unreal Engine detection + 8 guided questions
│       ├── astro.md             # Astro detection + questions + create-project recipe
│       ├── nextjs.md            # Next.js detection + questions + create-project recipe
│       ├── fastapi.md           # FastAPI detection + questions + create-project recipe (template-only)
│       └── [more stacks...].md
│
├── global/                      # Global ~/.claude/ config templates
│   ├── CLAUDE.md
│   ├── settings.json
│   └── statusline.py            # Status line script (installed to ~/.claude/statusline.py)
│
└── inspiration/                 # Third-party reference — NEVER MODIFY
```

---

## Skills — Workflows and Expertise

Skills follow the [Agent Skills](https://agentskills.io) format: `.agents/skills/<name>/SKILL.md` with YAML frontmatter. Slash commands are skills; user-invoked ones are invoked as `/name` (`$name` in Codex). Two scopes:

- **`scope: project`** — distributed to target projects via `/kc-install`
- **`scope: framework`** — KahnClaude management only, never distributed

The `kc-` name prefix marks skills that manage KahnClaude itself (invoked as `/kc-<name>`); it does not imply scope. `kc-create-agent-skill` and `kc-fix-agent-skill` are `scope: project` so they are installed into projects too. The tables below are grouped by `scope`.

### Framework Skills (`scope: framework`)

| Skill                    | What It Does                                                                      |
| ------------------------ | --------------------------------------------------------------------------------- |
| `/kc-install`            | Install KahnClaude components into the current project                            |
| `/kc-create-project`     | Create a new project (astro, nextjs, fastapi): init CLI, template overlay, targeted interview + install, AGENTS.md |
| `/kc-install-global`     | Pick which global config, hooks, skills and agents to merge into `~/.claude/` (never overwrites) |
| `/kc-update`             | Update installed components from the latest framework source; migrates Claude-only installs to the `.agents/` layout |
| `/kc-import`             | Analyze a repo's agent components and selectively integrate into KahnClaude |
| `/kc-harvest`            | Pull improvements back from a target project into KahnClaude (reverse of update) |
| `/kc-generate-agents-md` | Auto-detect tech stack and generate AGENTS.md (+ CLAUDE.md shim); enhances an existing file |

### Project Skills (`scope: project`)

| Skill                    | What It Does                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `/kc-create-agent-skill` | Create a new skill (or slash command) or agent following framework conventions |
| `/kc-fix-agent-skill`    | Debug a misbehaving agent or skill — session analysis + convention audit          |
| `/review`                | Review current diff for bugs, security issues, and best practices                              |
| `/commit`                | Generate a conventional commit message and commit staged changes                               |
| `/worktree`              | Create a git worktree + branch for isolated task work                                          |
| `/refactor`              | Refactor a file against AGENTS.md rules — split, extract, clean up                             |
| `/progress`              | Show file counts, test status, recent git activity, and next actions                           |
| `/document`              | Build or update project docs: no args = ARCHITECTURE.md index, with args = subsystem deep-dive |
| `/learn`                 | Update docs from a git SHA, SHA range, a plain-text fact, or auto-detected changes             |
| `/linear`                | Implement a Linear issue — set In Progress, branch, plan, code, test, PR                       |
| `/jira`                  | Implement a Jira issue — transition In Progress, branch, plan, code, test, PR                  |
| `/github-issue`             | Implement a GitHub issue via `gh` — assign, branch, plan, code, test, PR                       |
| `/pr`                    | Generate a PR title and description from the current branch diff; optionally create via `gh`   |
| `/linear-plan`           | Brainstorm and create or update Linear issues (planning only, no implementation)               |
| `/jira-plan`             | Brainstorm and create or update Jira issues (planning only, no implementation)                |
| `/github-issue-plan`          | Brainstorm and create or update GitHub issues via `gh` (planning only, no implementation)      |
| `/explain`               | Explain code in detail — overview, components, control flow, dependencies, gotchas, usage      |
| `/answer`                | Research a question using general knowledge, codebase search, Context7 docs, or web search     |
| `/test`                  | Generate tests by delegating to the `test-writer` agent (single source of truth)               |
| `/security-check`        | Scan for exposed secrets, missing .gitignore entries, and unsafe patterns                      |

---

## Harness Support

Instructions and skills live in files every supported harness reads. Claude-specific pieces stay under `.claude/`.

| Piece | Location | Claude Code | Codex | OpenCode | pi |
| ----- | -------- | ----------- | ----- | -------- | -- |
| Instructions | `AGENTS.md` | via `CLAUDE.md` shim (`@AGENTS.md`) | native | native | native |
| Skills | `.agents/skills/` | via `.claude/skills` projection | native | native | native |
| Agents | `.claude/agents/` | native | not used | not used | not used |
| Hooks and settings | `.claude/` | native | not used | not used | not used |
| Personal overrides | `CLAUDE.local.md` | native | not used | not used | not used |

Claude Code does not read `.agents/skills/`, so the `link_skills.py` SessionStart hook projects it into `.claude/skills/` (a junction on Windows, a symlink elsewhere, a copy as fallback). The projection is gitignored and recreated every session. Claude-only frontmatter (`allowed-tools`, `argument-hint`, `$ARGUMENTS`) is ignored by other harnesses.

**Migrating a Claude-only repo:** run `/kc-update <path>`. A v1 install (manifest at `.claude/.kahnclaude`) is migrated first, one commit per phase: `CLAUDE.md` becomes `AGENTS.md` plus the shim, `.claude/commands/` and `.claude/skills/` move into `.agents/skills/`, the projection is created, and the manifest becomes v2 at `.agents/.kahnclaude`. Skills KahnClaude ships are installed from KahnClaude's `.agents/skills` (an old locally modified copy is diffed first); your own skills and commands are moved unchanged (only `name:` is set when a command becomes a skill). Anything that is not a KahnClaude skill, including a renamed one, is treated as yours and never modified. `/kc-install` offers the same move for repos that already have `.claude/skills` or `.claude/commands`. KahnClaude slash commands are renamed from `/kc:name` to `/kc-name`.

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

## Hooks and Permissions

KahnClaude keeps Claude Code hooks to what the harness does not do natively. Safety comes from `permissions` deny rules, auto mode and the sandbox; linting, formatting, secret scanning and branch policy belong to each project's own git hooks and CI, not to KahnClaude.

| Hook                       | Event        | Behavior                                                                                                                              |
| -------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| `link_skills`              | SessionStart | Projects `.agents/skills/` into `.claude/skills/` (junction, symlink or copy)                                                         |
| `block-write-outside-repo` | PreToolUse   | Asks before Edit/Write/NotebookEdit outside the project, `~/.claude/`, the temp dir or `permissions.additionalDirectories`, or into `.git/` |
| `notify`                   | Notification | **Global only** (`/kc-install-global`), never installed in projects. Desktop notification when Claude needs attention (Windows toast, macOS, Linux, WSL, bell fallback) |

`block-write-outside-repo` limits:

- It only sees the file tools; Bash redirections and `cp`/`mv` bypass it (the sandbox covers those).
- Directories added with `--add-dir` or `/add-dir` are invisible to hooks, so writes there still ask. Put permanent ones in `permissions.additionalDirectories`.
- If it is wired both globally and in the project, the project copy exits early so the check runs once.

### Permissions

The shipped `settings.json` relies on Claude Code's own layers and only adds what they lack:

- **Read-only commands** (`ls`, `cat`, `grep`, `head`, `tail`, `wc`, read-only `git`, ...) never prompt, so they are not in `allow`. `allow` only lists routine writes (`git add`, `git commit`, `git tag`, `mkdir`) and Context7.
- **No `ask` rules.** Ask rules run before the auto-mode classifier and force a prompt in every mode; the classifier already blocks force pushes and other irreversible actions, and default mode prompts for them anyway.
- **`deny`** (holds in every mode, including auto and `bypassPermissions`):
  - Read: `.env` variants (`.env.example` stays readable; Write stays allowed so setup can create `.env`)
  - Read and Edit: `secrets/` and `.secrets/` folders, `*credential*`, `service-account*.json`, `.npmrc`, `.pypirc`, `.pgpass`, `.my.cnf`, `.git-credentials`, `.netrc`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, SSH private keys, `~/.ssh/`, `~/.aws/`, `~/.azure/`, `~/.config/gcloud/`, `~/.docker/config.json`
  - Bash: `rm -rf` on `/`, `~` or `$HOME`, as a backstop for `bypassPermissions`
- **No filesystem MCP.** MCP tools are not covered by `Read`/`Edit` deny rules; use `--add-dir` or `additionalDirectories` instead.

Read deny rules also apply to Bash commands Claude Code can analyze (`cat`, `head`, `tail`, `sed`, redirections), but not to `grep -r` over a folder or to scripts that open files themselves. For OS-level enforcement, enable the sandbox (`/sandbox`, macOS, Linux and WSL2): it merges these deny rules into its filesystem policy.

### Exit Codes

| Code      | Meaning                                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------------------------- |
| `0`       | Proceed. stdout may carry JSON: `permissionDecision` (`allow`/`deny`/`ask`), `decision: "block"`, `additionalContext`  |
| `2`       | **Block**: stderr is fed back to Claude                                                                                |
| `1`/other | Non-blocking error, shown to the user only; Claude never sees it. Never use it to warn                                 |

---

## Templates

### `@project/AGENTS.md` and `@project/CLAUDE.md`

Master template for auto-generating project-specific `AGENTS.md` files; `project/CLAUDE.md` is the one-line `@AGENTS.md` shim written next to it. Used by `/kc-generate-agents-md` command to:

- Auto-detect tech stack (Unreal, Node.js, Python, Rust, etc.)
- Load tech-specific Q&A guides (e.g., Unreal Engine)
- Ask guided questions about project configuration
- Instantiate template with user answers and auto-detected versions
- Populate all sections: Project Overview, Critical Rules, Tech Stack Details, Service Ports, etc.

Every section includes `<!-- GUIDE: ... -->` comments explaining purpose, format, and examples so users understand what to put where.

### Tech-Stack Guides: `@project/tech-stacks/`

Specialized Q&A guides loaded by `/kc-generate-agents-md` when a tech stack is detected.

- **`unreal.md`** — Unreal Engine (8 guided questions: version, project type, platforms, C++ vs Blueprint, plugins, content structure, build targets, do's/don'ts)
- **`astro.md`** — Astro (9 questions: description, rendering mode, content source, islands, styling, deploy, package manager, testing, SEO)
- **`nextjs.md`** — Next.js (9 questions: description, router, data, auth, styling, deploy, package manager, testing, env)
- **`fastapi.md`** — FastAPI (9 questions: description, database, auth, storage, deploy, environments, tooling, testing, structure); scaffolds from `Kahncode/py-fastapi-template` with no init CLI
- **`[more stacks].md`** — Additional stacks (Django, Rust, C#/.NET) can be added following the same pattern

When `/kc-generate-agents-md` detects a manifest file (`.uproject`, `astro.config.*`, `next.config.*`, `pyproject.toml`, etc.), it loads the matching guide and asks all questions to build a complete, annotated AGENTS.md.

### Creating New Projects: `/kc-create-project <stack> <path> [description]`

Guides with a `## Create Project` section (astro, nextjs, fastapi) can scaffold a new project. Flow, one git commit per phase: git init, official init CLI (skipped when the guide says `none`), overlay of a per-stack template repo (`kc-create-project/scripts/apply_template.py`, template files win), then an interview limited to questions the template does not already answer (resolved via each question's auto-detection) run together with `/kc-install`, dependency install and build, then `/kc-generate-agents-md` with the interview answers, and a rewrite of the template's `README.md` for the new project. Requires git. Template repos are normal functional projects (own `package.json`, optional `AGENTS.md`); URLs are set in the guide.

### `@project/CLAUDE.local.md`

Optional personal overrides for Claude Code — gitignored, never committed (other harnesses do not read it). For individual workflow preferences, local environment details, and project-specific personal notes.

### `@global/CLAUDE.md`

Installed once at `@~/.claude/CLAUDE.md`. Applies security rules and coding standards across **every** project. Merged with any existing global config — never overwrites.

### `@global/settings.json`

Installed once at `@~/.claude/settings.json`. Wires up global hooks and configures the status line. Merged with existing settings — top-level keys like `statusLine` are added only if absent.

### `@global/statusline.py`

Installed to `~/.claude/statusline.py`. Renders the Claude Code status line showing: `cwd | branch | model | ctx% | $cost | rate-limit %`. Reads JSON from stdin (Claude Code's `StatusLine` event). No dependencies beyond stdlib.

---

## Key Concepts

### Hooks Are Stronger Than Rules

Three layers of enforcement, strongest to weakest:

1. **`.gitignore`** — last line of defense, filesystem-level (strongest)
2. **Permissions and hooks** — guaranteed to run, block or ask before an operation happens
3. **`AGENTS.md` rules** — behavioral suggestions (weakest — Claude can override under context pressure)

### One Task, One Chat

Research shows **39% performance degradation** when mixing unrelated topics in a single Claude session. Use `/clear` between unrelated tasks. A 2% misalignment early in a conversation can cause **40% failure** by the end.

### Plan First, Code Second

For non-trivial tasks, start in plan mode. Don't let Claude write code until you've agreed on the plan. Every plan step must have a unique name so you can reference and replace steps cleanly.

### AGENTS.md Is Team Memory

Every time Claude makes a mistake, add a rule to prevent it recurring. The file is in git — the whole team benefits from every lesson learned.

### Hooks Are Python

All KahnClaude hooks are Python. No bash. Reasons: cross-platform (Windows, WSL, macOS, Linux), no shell quoting edge cases, stdlib-only, easy to test.

---

## Adding Components

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

| Component           | Location                         | Naming                                          |
| ------------------- | -------------------------------- | ----------------------------------------------- |
| Skill (project)     | `.agents/skills/<name>/SKILL.md` | kebab-case action verb or category              |
| Skill (KahnClaude management) | `.agents/skills/kc-<name>/SKILL.md` | `kc-` prefix; `scope` decides distribution |
| Agent               | `.claude/agents/<name>.md`       | kebab-case role                                 |
| Hook                | `.claude/hooks/<name>.py`        | kebab-case; `block-` if it denies or asks       |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions of skills, agents, and hooks are welcome. Bash scripts are not — Python only.
