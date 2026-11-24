---
name: kc-generate-agents-md
description: Auto-generate or enhance AGENTS.md (plus a one-line CLAUDE.md shim) by detecting tech stack and asking guided questions
scope: framework
---

# /kc-generate-agents-md

Auto-detect your project's tech stack and generate a complete, annotated `AGENTS.md`, the harness-neutral instruction file read by Codex, OpenCode, pi and Claude Code. A one-line `CLAUDE.md` containing `@AGENTS.md` is written alongside so Claude Code loads it regardless of version.

**Usage:** `/kc-generate-agents-md [<project-path>]`

If no path is given, the current directory is the target. When invoked by `/kc-install`, the target project path is passed as an argument.

**Mode is determined automatically:**

- Target has no `AGENTS.md` → generate new file
- Target has existing `AGENTS.md` → ask whether to enhance it with missing sections
- Target has only a `CLAUDE.md` with real content → `git mv CLAUDE.md AGENTS.md` first, then enhance

---

## How It Works

### Phase 1: Tech Stack Detection

Scan the **target project root** for manifest files. Check in this priority order:

1. `.uproject` → **Unreal Engine**
2. `astro.config.*` or `package.json` with `astro` → **Astro** (guide: `astro.md`)
3. `next.config.*` or `package.json` with `next` → **Next.js** (guide: `nextjs.md`)
4. `package.json` → **Node.js** (inspect `dependencies` for react/express/etc.)
5. `pyproject.toml` or `setup.py` → **Python** (inspect for django/fastapi/flask; `fastapi` → guide `fastapi.md`)
6. `Cargo.toml` → **Rust**
7. `*.csproj` or `*.sln` → **C#/.NET**
8. `go.mod` → **Go**
9. `CMakeLists.txt` → **C++**
10. `Gemfile` → **Ruby**
11. `pom.xml` or `build.gradle` → **Java**
12. None found → **Unknown** (use generic questions)

If multiple primary stacks are detected (e.g., Unreal + Python tooling), ask the user which is primary.

### Phase 2: Load Guide & Discover Stack Details

**With a guide (e.g., Unreal):**

- Read `project/tech-stacks/<tech-stack>.md` from KahnClaude source directory
- Ignore the `## Create Project` section (used only by `/kc-create-project`)
- Use its guided questions tailored to this type of projects

**Without a guide (other stacks):**

- Use code discovery: scan source files, `README.md`, `package.json`, `.toml` files, etc. to infer:
  - Language and version (e.g., Python 3.11, Node 20)
  - Key frameworks and libraries (e.g., Express, FastAPI, React)
  - Database and infrastructure choices (infer from imports, config files, or comments)
- Delegate to `/explore` agent (or equivalent code-scanning capability) to quickly analyze the codebase
- Ask the user clarifying questions about aspects the code analysis couldn't determine unambiguously
- Build a tech-stack summary from discovered + user-supplied information

### Phase 3: Ask Questions

Present questions one by one. All questions are optional — user can skip any.

When invoked by `/kc-create-project`, the project description and interview answers are passed in. Use them to fill the template and do not ask those questions again; ask only what is still unanswered.

Auto-detect project name from: `package.json` name field, `.uproject` DisplayName, git remote `origin` URL, or folder name. Offer the detected value and let the user confirm or override.

### Phase 4: Instantiate Template

Read `project/AGENTS.md` from the KahnClaude source directory. Replace placeholders with answers and auto-detected values.

**Size constraint:** AGENTS.md should ideally be **under 200 lines**. Keep it strictly **under 300 lines**. If the generated file exceeds 300 lines:

- Extract long sections into separate docs in `docs/` folder
- Reference them from AGENTS.md with links (e.g., "See [docs/TECH_STACK.md](docs/TECH_STACK.md)")
- The goal is a concise, scannable AGENTS.md that points to detailed docs for reference

**Non-negotiable:** The generated file must include in Project Overview:

```markdown
**Documentation:** [See docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — maintained by the documenter agent with system overview, component map, and tech choices.
```

If this line is absent after substitution, insert it after the `## Project Overview` heading.

### Phase 5: Write

**New file:** Write instantiated content to `<target>/AGENTS.md`. Report: "Generated AGENTS.md: N sections."

**Enhance existing:** Parse existing `AGENTS.md` for `## Heading` sections. Compare against template sections. For each missing section, ask: "Missing: [Section]. Add it? (yes/skip)". Append accepted sections. Report: "Enhanced AGENTS.md: added N sections."

**Shim:** if `<target>/CLAUDE.md` does not exist, write it with the single line `@AGENTS.md` (copy `project/CLAUDE.md`). If it exists with other content, do not touch it; tell the user to merge it into AGENTS.md.

---

## Generic Questions (Non-Unreal Stacks)

1. **Project Name** — auto-detected; confirm or override
2. **Description** — "Describe the project in one sentence"
3. **Tech Stack Summary** — "Summarize your stack (language, framework, database, etc.)"
4. **Key Architectural Patterns** — "MVC? Event-driven? Monolith? Microservices?"
5. **Critical Coding Rules** — "Any rules the coding agent must follow? (optional)"
6. **Service Ports** — "List local dev services and ports (optional)"

---

## File Paths

All source files are read from the KahnClaude source directory, not from the target project:

- `project/AGENTS.md` — master template
- `project/CLAUDE.md` — one-line shim template
- `project/tech-stacks/unreal.md`, `astro.md`, `nextjs.md`, `fastapi.md` — stack Q&A guides
- `project/tech-stacks/<stack>.md` — future guides (load if file exists)

Output is written to `<target>/AGENTS.md` and `<target>/CLAUDE.md`.

---

## Notes

- Skip any question by leaving the answer empty
- If manifest parsing fails, fall back to generic questions
- Existing sections are never overwritten in enhance mode — only new sections are appended
- Verify no secrets in generated output before writing
