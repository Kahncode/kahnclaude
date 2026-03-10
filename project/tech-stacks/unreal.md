# Tech Stack Guide: Unreal Engine

This guide is used by `/kc:generate-claude-md` when an Unreal Engine project is detected (`.uproject` file in root).

The following questions help populate `CLAUDE.md` sections with Unreal-specific configurations and conventions.

---

## Detection Pattern

**File:** `.uproject` (root level)

When detected, this guide is loaded and the user is asked all questions below (optional to skip any).

---

## Questions & Mappings

### 1. Unreal Engine Version

**Question:** What is your target Unreal Engine version?

**Expected Answer:** Version number (e.g., "5.4", "5.3.2", "UE4.27")

**Auto-detection:** The command attempts to read `.uproject` and extract `EngineAssociation` or `EngineVersion`. User can confirm or override.

**CLAUDE.md Mapping:**

- **Section:** Tech Stack Details → Row 1
  - Decision: `Engine`
  - Choice: `Unreal Engine [version]`
  - Why: `[auto-filled with project goals, e.g., "Latest stable with ray tracing support"]`

**Rationale:** Version determines available features, plugin compatibility, and debugging toolchain.

---

### 2. Source Control System

**Question:** Which source control system does your project use?

**Expected Answer:** One of: `Git`, `Perforce`, `SVN`

**Auto-detection:** Check for `.git/`, `.p4ignore`, `.svn/`, or similar markers.

**CLAUDE.md Mapping:**

- **Section:** Tech Stack Details
  - Decision: `Source Control`
  - Choice: `[Git / Perforce / SVN]`
  - Why: `[e.g., "Perforce for large binary assets and team coordination; enforces workspace rules"]`

**Rationale:** Determines tooling and workflow instructions. If Perforce, Claude commands must adapt git-based workflows to Perforce equivalents.

---

### 3. Project Type & Multiplayer Scope

**Question:** What type of project is this, and is it single-player or multiplayer?

**Expected Answer:** One of: `Single-Player Game`, `Multiplayer Game`, `Tool/Editor Plugin`, `VR Application`, `Mobile Game`, `Server-Side Tool` + clarify: `Single-Player` or `Multiplayer`

**CLAUDE.md Mapping:**

- **Section:** Project Overview → Description
  - Enhance: "Unreal Engine [version] [Project Type] ([Scope])"
- **Section:** Tech Stack Details
  - Decision: `Project Type`
  - Choice: `[User Answer]`
  - Why: `[e.g., "Multiplayer with dedicated server; requires replication graphs, network optimization, and rollback handling"]`

**Rationale:** Multiplayer shapes architecture (replication, networking, lag compensation). Single-player allows simpler event-driven logic.

---

### 4. Project Setup: Engine Association & Structure

**Question:** How is your project structured relative to the engine? (Check `.uproject` location and `EngineAssociation`)

**Expected Answer:** One of:

- `Standalone (Launcher)` — `.uproject` at repo root; engine via Epic Launcher version
- `Standalone (Local Path)` — `.uproject` at repo root; engine via hardcoded local path
- `In-Engine` — `.uproject` in subfolder; root is engine source (Epic way); engine association empty or local
- `Engine-Source Mods` — Game-code project with patches to engine source in same tree

**Auto-detection Steps:**

1. Check `.uproject` location: root or subfolder?
2. Read `.uproject` → `EngineAssociation`:
   - Version string (e.g., `"5.4"`) → **Standalone (Launcher)**
   - Absolute/relative path → **Standalone (Local Path)** or **In-Engine**
   - Empty/missing + parent folders contain `Engine/` → **In-Engine**
3. Check for `Engine/` folder at repo root → **Engine-Source Mods**

**CLAUDE.md Mapping:**

- **Section:** Project Structure
  - Add note describing setup:
    - **Standalone (Launcher):** `[Project] / Source / ... ; engine from Epic Launcher`
    - **Standalone (Local Path):** `[Project] / Source / ... ; engine at [engine_path]`
    - **In-Engine:** `Engine / ... ; Source / [ProjectName] / ...` (root is engine)
    - **Engine-Source Mods:** Document which subsystems patched and why
- **Section:** Tech Stack Details
  - Decision: `Project Setup`
  - Choice: `[Setup Type]`
  - Why: `[e.g., "In-Engine for tight integration; monorepo sync required"]`
  - If Local Path: `Engine Path: [path or env var]`

**Rationale:** Project structure determines build pipeline, sync/pull strategy, CI/CD layout, and whether monorepo rules apply. Misidentifying this breaks workflows.

---

### 5. Target Platforms

**Question:** What platforms are you targeting? (e.g., PC, PlayStation, Xbox, VR, Mobile, etc.)

**Expected Answer:** Comma-separated list or bullet list

**CLAUDE.md Mapping:**

- **Section:** Tech Stack Details
  - Decision: `Target Platforms`
  - Choice: `[Platforms listed by user]`
  - Why: `[e.g., "PC primary, PlayStation 5 stretch; requires platform-specific optimization and DRM"]`

**Rationale:** Platforms influence shader complexity, memory constraints, and input handling.

---

### 6. C++ vs Blueprint Philosophy & Logic Split

**Question:** What's your C++ vs Blueprint philosophy, and where is the logic split?

**Expected Answer:** One of: `Pure C++`, `Mostly Blueprint`, `Pure Blueprint`, `Mixed` + clarify logic split

**If Mixed, ask:** Where should new logic live?

- `Artist-Oriented:` All game logic in C++, all visual/UI/animation logic in Blueprint
- `Modular Framework:` Game code provides modular systems; high-level game logic glues them together in Blueprint
- `[Custom split]`

**CLAUDE.md Mapping:**

- **Section:** Project-Specific Rules
  - Add rule: `C++ vs Blueprint Philosophy: [User Answer]`
    - Pure C++: "No blueprint-only features. All gameplay in C++; blueprints for config only."
    - Mostly Blueprint: "Blueprint is primary; C++ only for performance-critical systems and plugins."
    - Pure Blueprint: "All logic in blueprint; C++ used only for engine extensions."
    - Mixed (Artist-Oriented): "Game logic in C++; visual/animation/UI in Blueprint — enables iterative design."
    - Mixed (Modular Framework): "C++ provides reusable systems; Blueprint orchestrates high-level logic."
  - Add rule: `Logic Split: [User Answer]` with examples per chosen pattern

**Rationale:** Determines where new code lives, code review focus, debuggability, and iteration speed. Mixed approaches require clear conventions to avoid bloat.

---

### 7. Key Plugins (Optional)

**Question:** Are you using any custom or marketplace plugins? (Optional — can be empty)

**Expected Answer:** List of plugin names (e.g., "Advanced Sessions", "Niagara Particle System")

**CLAUDE.md Mapping:**

- **Section:** Tech Stack Details
  - Decision: `Key Plugins`
  - Choice: `[Plugins listed, or "None (engine features only)"]`
  - Why: `[e.g., "Advanced Sessions for cross-platform networking; custom AI plugin for behavior trees"]`

**Rationale:** Plugins affect performance, compatibility, and available APIs for new code.

---

### 8. Content Folder Structure

**Question:** How is your Content/ folder organized? (Describe folder layout, naming convention, etc.)

**Expected Answer:** Description of folder organization (e.g., "Characters/, Maps/, UI/, Blueprint/, Plugins/")

**CLAUDE.md Mapping:**

- **Section:** Project Structure
  - Add to tree:
    ```
    Content/
    ├── Characters/    - [description from user]
    ├── [...]
    └── ...
    ```

**Rationale:** Consistent structure is critical for asset management, team collaboration, and tooling.

---

### 9. Build Targets

**Question:** What build targets are you using? (e.g., "Development, Shipping, Testing")

**Expected Answer:** List of build targets (e.g., "Development, Shipping, Test")

**CLAUDE.md Mapping:**

- **Section:** Service Ports & Configuration
  - Add rows:
    | Build Target | Use Case |
    |---|---|
    | [Target] | [When to use] |

**Rationale:** Developers need to know which build config to use for different scenarios.

---

### 10. Project-Specific Do's and Don'ts (Optional)

**Question:** Any project-specific do's and don'ts for Claude? (e.g., "Never modify .uproject directly", "Always test on console before commit")

**Expected Answer:** Bulleted list of project-specific conventions

**CLAUDE.md Mapping:**

- **Section:** Notes for Claude → Do / Don't
  - Add Unreal-specific items:
    - Do: "Test plugin changes with the `.uproject` regenerated"
    - Don't: "Don't modify generated intermediate files"
    - [User items]

**Rationale:** Captures project-specific tribal knowledge that prevents mistakes.

---

## Generic Questions (If Not Pure Unreal)

If the project also has a web UI, server backend, or other secondary tech, the generic question set (Name, Description, Stack Summary, Patterns, Rules, Ports) may also be asked to document the full architecture.

---

## Notes

- All questions are **optional**; user can skip any.
- If a question cannot be auto-answered (e.g., "Key Plugins"), user sees: "\*\* Not detected. Skip or describe: `_____`"
- **Perforce Consideration:** If the project uses Perforce instead of Git, the framework's git-based skills and hooks may need adaptation. Document the choice so Claude can adjust commands when needed (e.g., `p4 submit` instead of `git push`).
- **Engine-Source Projects:** If the project modifies engine source, document which subsystems are patched and why. This affects build pipelines, merge strategies, and compatibility tracking.
