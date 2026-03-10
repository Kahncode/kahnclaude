---
name: generate-claude-md
description: Auto-generate or enhance CLAUDE.md by detecting tech stack and asking guided questions
scope: framework
---

# /kc:generate-claude-md

Auto-detect your project's tech stack and generate a complete, annotated `CLAUDE.md`.

**Usage:** `/kc:generate-claude-md [<project-path>]`

If no path is given, the current directory is the target. When invoked by `/kc:install`, the target project path is passed as an argument.

**Mode is determined automatically:**

- Target has no `CLAUDE.md` → generate new file
- Target has existing `CLAUDE.md` → ask whether to enhance it with missing sections

---

## How It Works

### Phase 1: Tech Stack Detection

Scan the **target project root** for manifest files. Check in this priority order:

1. `.uproject` → **Unreal Engine**
2. `package.json` → **Node.js** (inspect `dependencies` for next/react/express/etc.)
3. `pyproject.toml` or `setup.py` → **Python** (inspect for django/fastapi/flask)
4. `Cargo.toml` → **Rust**
5. `*.csproj` or `*.sln` → **C#/.NET**
6. `go.mod` → **Go**
7. `CMakeLists.txt` → **C++**
8. `Gemfile` → **Ruby**
9. `pom.xml` or `build.gradle` → **Java**
10. None found → **Unknown** (use generic questions)

If multiple primary stacks are detected (e.g., Unreal + Python tooling), ask the user which is primary.

### Phase 2: Load Guide & Discover Stack Details

**With a guide (e.g., Unreal):**

- Read `project/tech-stacks/<tech-stack>.md` from KahnClaude source directory
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

Auto-detect project name from: `package.json` name field, `.uproject` DisplayName, git remote `origin` URL, or folder name. Offer the detected value and let the user confirm or override.

### Phase 4: Instantiate Template

Read `project/CLAUDE.md` from the KahnClaude source directory. Replace placeholders with answers and auto-detected values.

**Size constraint:** CLAUDE.md should ideally be **under 200 lines**. Keep it strictly **under 300 lines**. If the generated file exceeds 300 lines:

- Extract long sections into separate docs in `docs/` folder
- Reference them from CLAUDE.md with links (e.g., "See [docs/TECH_STACK.md](docs/TECH_STACK.md)")
- The goal is a concise, scannable CLAUDE.md that points to detailed docs for reference

**Non-negotiable:** The generated file must include in Project Overview:

```markdown
**Documentation:** [See docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — maintained by the documenter agent with system overview, component map, and tech choices.
```

If this line is absent after substitution, insert it after the `## Project Overview` heading.

### Phase 5: Write

**New file:** Write instantiated content to `<target>/CLAUDE.md`. Report: "Generated CLAUDE.md: N sections."

**Enhance existing:** Parse existing `CLAUDE.md` for `## Heading` sections. Compare against template sections. For each missing section, ask: "Missing: [Section]. Add it? (yes/skip)". Append accepted sections. Report: "Enhanced CLAUDE.md: added N sections."

---

## Generic Questions (Non-Unreal Stacks)

1. **Project Name** — auto-detected; confirm or override
2. **Description** — "Describe the project in one sentence"
3. **Tech Stack Summary** — "Summarize your stack (language, framework, database, etc.)"
4. **Key Architectural Patterns** — "MVC? Event-driven? Monolith? Microservices?"
5. **Critical Coding Rules** — "Any rules Claude must follow? (optional)"
6. **Service Ports** — "List local dev services and ports (optional)"

---

## File Paths

All source files are read from the KahnClaude source directory, not from the target project:

- `project/CLAUDE.md` — master template
- `project/tech-stacks/unreal.md` — Unreal Q&A guide
- `project/tech-stacks/<stack>.md` — future guides (load if file exists)

Output is written to `<target>/CLAUDE.md`.

---

## Notes

- Skip any question by leaving the answer empty
- If manifest parsing fails, fall back to generic questions
- Existing sections are never overwritten in enhance mode — only new sections are appended
- Verify no secrets in generated output before writing
