---
name: generate-claude-md
description: Auto-generate or enhance CLAUDE.md by detecting tech stack and asking guided questions
scope: project
---

# /tool:generate-claude-md

Auto-detect your project's tech stack and generate a complete `CLAUDE.md`.

**Usage:** `/tool:generate-claude-md [<project-path>]`

Defaults to the current working directory if no path is given. If no `CLAUDE.md` exists, generate new. If one exists, offer to enhance with missing sections.

---

## Phase 1: Detect Tech Stack

Scan the target project root for manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`, `*.sln`, etc.) to identify the primary tech stack. If unclear, ask the user which stack they want to configure. Check in this priority order:

1. `.uproject` → **Unreal Engine** (guide: `project/docs/tech-stacks/unreal.md`, picked up by the Phase 2 scan)
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

---

## Phase 2: Load Guides (Dynamic)

Scan every `*.md` file in `project/docs/tech-stacks/`. Each guide has HTML comment metadata in its header:

```
<!-- detection: auto|opt-in | signal: <what to look for> | prerequisite: <guide name or none> -->
<!-- prompt: "<question to ask user>" -->
```

For each guide, parse `detection`, `signal`, `prerequisite`, and `prompt` from the header comments.

Also, if Phase 1 matched a primary-stack guide in `project/tech-stacks/<stack>.md` (Astro, Next.js, FastAPI), load it as auto-detected (these guides have no metadata header). Ignore its `## Create Project` section (used only by `/kc:create-project`).

### Step 2: Presentation rules

- **Always use `AskUserQuestion` with `multiSelect: true`** — never render fake markdown checkboxes or ask individual yes/no questions
- `AskUserQuestion` supports max 4 options per question. If there are more than 4 stacks in a category, split across multiple questions (e.g., "Auto-detected stacks (1/2)" and "Auto-detected stacks (2/2)")
- One interaction for auto-detected, one for opt-in — two interactions maximum (per 4-option batch)
- Use the option `label` for the stack name, and `description` for the detection signal (e.g., "package.json found at project root")
- If there are no auto-detected stacks, skip Step 2a
- If there are no eligible opt-in stacks, skip Step 2b

### Step 2a: Auto-detected stacks

Evaluate all `detection: auto` guides whose signals match (and whose prerequisites are satisfied). Present them using `AskUserQuestion` with `multiSelect: true`. The question should tell the user all items are included by default — deselect any to exclude.

### Step 2b: Opt-in stacks

After auto-detected stacks are confirmed, gather all `detection: opt-in` guides whose prerequisites are satisfied by the selected auto-detected stacks. Present them using `AskUserQuestion` with `multiSelect: true`. The question should tell the user to select any they want to add.

---

## Phase 3: Collect Setup Info

**Shared rules (apply to all guides):**
- All questions are **optional** — user can skip any
- Environment variables go in `CLAUDE.local.md`, never in `CLAUDE.md`
- For each env var, explain what it is and how to find it
- Auto-detect values where possible; offer detected values and let user confirm or override
- When invoked by `/kc:create-project`, the project description and interview answers are passed in. Use them to fill the template and do not ask those questions again; ask only what is still unanswered.

Auto-detect project name from: `package.json` name field, `pyproject.toml`, `.uproject` DisplayName, git remote `origin` URL, or folder name. Offer the detected value and let the user confirm or override.

### Grouping: one stack at a time

Process each loaded tech stack guide **sequentially, one stack per interaction**. For each stack:

1. Run all auto-detection steps from the guide's **Setup — Auto-Detection** table
2. Present the guide's questions/confirmations using multi-choice format (as defined in the guide)
3. Show auto-detected values inline for the user to confirm or override
4. Use the guide's **Auto-Detection** methods when the user says "I don't know"

**Never mix questions or variables from different stacks in the same prompt.** Each stack gets its own clearly labeled section:

```
── Node.js / TypeScript ───────────────────────

  <auto-detected info + multi-choice questions for this stack>

── Helix Perforce ─────────────────────────────

  <auto-detected info + multi-choice questions for this stack>
```

Process stacks in prerequisite order (e.g., primary stack before dependent stacks, Perforce before Swarm).

---

## Phase 4: Write CLAUDE.md

Read `project/CLAUDE.md` template from the KahnClaude source directory. Fill in placeholders with collected answers.

**Size constraint:** Keep CLAUDE.md under 200 lines (hard limit: 300). If over 300 lines, extract long sections into `docs/` and link from CLAUDE.md.

**Required line in Project Overview:**
```markdown
**Documentation:** [See docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — maintained by the documenter agent with system overview, component map, and tech choices.
```

Insert it after `## Project Overview` if absent.

Report: "Generated CLAUDE.md: N sections."

---

## Phase 5: Configure CLAUDE.local.md

Walk the user through setting up every environment variable from the loaded tech stack guides.

**Procedure:**

1. Create or open `CLAUDE.local.md` in the target project root. Verify it is listed in `.gitignore` / `.p4ignore` (add if missing).

2. **Group by tech stack** — process each loaded guide sequentially (in prerequisite order). For each stack, present all its variables together in one labeled block:

```
── Helix Perforce ─────────────────────────────

  P4PORT    — server address (e.g., ssl:perforce.company.com:1666)
             Run `p4 info` or check P4V connection settings.
  P4USER    — your Perforce username
  P4CLIENT  — your workspace/client name

── Atlassian Jira ─────────────────────────────

  JIRA_CLOUD_ID          — UUID from https://<company>.atlassian.net/_edge/tenant_info
  JIRA_PROJECT_KEY       — short key prefix (e.g., PROJ-123)
  JIRA_ASSIGNEE_ACCOUNT_ID — run MCP tool `atlassianUserInfo`
```

3. Within each stack block:
   - List Required variables first, then Optional
   - Show the **How to Obtain** hint from the guide inline with each variable
   - Show a concrete example of the expected value format
   - Attempt **auto-detection** using the guide's Auto-Detection / Verification methods
   - If auto-detected: show the detected value and ask the user to confirm or override
   - If not auto-detected: list it for the user to provide
   - User can skip any variable

4. **Never mix variables from different stacks in the same prompt.** Each stack is a separate, clearly labeled section.

5. After collecting values for a stack, run the guide's **verification checks** (file existence, registry lookups, etc.) and warn if verification fails.

6. Write all values into `CLAUDE.local.md`, organized by stack with section headers:
   ```
   # ── Helix Perforce ──
   P4PORT=ssl:perforce.company.com:1666
   P4USER=jdoe
   P4CLIENT=jdoe_workspace

   # ── Atlassian Jira ──
   JIRA_CLOUD_ID=abc12345-de67-890f-abcd-1234567890ab
   JIRA_PROJECT_KEY=PROJ
   # JIRA_ASSIGNEE_ACCOUNT_ID=<account-id> — run MCP tool atlassianUserInfo
   ```
   - Set values as real entries: `VAR_NAME=value`
   - Skipped values as commented placeholders with a "how to obtain" hint

7. Report: "CLAUDE.local.md configured: X variables set, Y skipped (across N stacks)."

---

## File Paths

All source files are read from the KahnClaude source directory:

- `project/CLAUDE.md` — master template
- `project/docs/tech-stacks/` — tech stack guides with metadata headers (enumerated dynamically at runtime)
- `project/tech-stacks/astro.md`, `nextjs.md`, `fastapi.md` — primary-stack Q&A guides (matched in Phase 1)
- `project/tech-stacks/<stack>.md` — future guides (load if file exists)

Output is written to `<target>/CLAUDE.md`.

---

## Notes

- Skip any question by leaving the answer empty
- If manifest parsing fails, fall back to generic questions
- Existing sections are never overwritten in enhance mode — only new sections are appended
- Verify no secrets in generated output before writing
