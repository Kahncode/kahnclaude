# Tech Stack Guide: Visual Studio

<!-- detection: auto | signal: .uproject present AND vswhere.exe found | prerequisite: unreal -->
<!-- prompt: "Do you use Visual Studio to build this project?" -->

---

## Setup — Environment Variables

Store in `.claude/rules/project-vars.md` (machine-specific, never committed); `PROJECT_ROOT`, `UE_ENGINE`, `UE_PROJECT` and `UE_SOLUTION` also go in `.claude/settings.local.json` → `env`. `UE_PROJECT` is set by `unreal.md` — do not ask again.

### Required

| Variable | How to Obtain |
|----------|---------------|
| `UE_SOLUTION` | Full path to `*.sln` — scan project root and one level up |
| `UE_ENGINE` | UE root directory — read `.uproject` `EngineAssociation` + registry lookup |
| `PROJECT_ROOT` | Workspace root (parent of `.claude/`) — default to current working directory |

### Auto-Detection

- **UE_SOLUTION:** `Get-ChildItem -Path "<root>", "<root>\.." -Filter "*.sln" -Depth 0` — offer first match, list if multiple
- **UE_ENGINE:** Read `EngineAssociation` from `.uproject` -> query `HKLM:\SOFTWARE\EpicGames\Unreal Engine\<version-or-GUID>` -> `InstalledDirectory`; if relative path, resolve from root; ask user if lookup fails
- **PROJECT_ROOT:** Default to cwd, confirm with user

### Verification

- `UE_SOLUTION`: file exists
- `UE_ENGINE`: contains `Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`
- `PROJECT_ROOT`: contains `.claude/`

---

## Setup — Auto-Detection + Confirmation

Most configuration is auto-detected. Only the build configuration warrants a quick confirmation.

| Step | Method | CLAUDE.md Section |
|------|--------|-------------------|
| 1. Detect VS version | `vswhere.exe -latest -format json` -> `displayName` + `installationVersion` | Tech Stack Details |
| 2. Detect platform | Read `TargetPlatforms` from `.uproject`; default to `Win64` | Tech Stack Details |
| 3. Detect .sln policy | Check `.gitignore`/`.p4ignore` for `*.sln` (excluded -> Regenerated); check VCS for tracked `.sln` (found -> Committed) | Project Rules |

### Confirmation

Present the build configuration using `AskUserQuestion` (single-select, NOT `multiSelect`), with the detected default listed first and marked "(Recommended)":

- **Option 1 label:** `DebugGame Editor (Recommended)` — **description:** `Gameplay debugging, faster iteration (detected)`
- **Option 2 label:** `Debug Editor` — **description:** `Full debugging, slow iteration`
- **Option 3 label:** `Development Editor` — **description:** `Optimized, limited debugging`
- **Option 4 label:** `Shipping` — **description:** `Final build, no editor`

Question: "Which default build configuration?"

Maps to **Service Ports** and **Notes for Claude** in CLAUDE.md.

### Defaults (no question needed)

- Regenerate project files after adding modules
- Never modify `.vcxproj` or `.sln` by hand
- Use `DebugGame` not `Debug`

---

## Operational Reference — Visual Studio

### Required Environment Variables

Set these in `.claude/rules/project-vars.md` and in `.claude/settings.local.json` → `env` (machine-specific, never committed to version control):

```ini
UE_SOLUTION=C:\path\to\UE5.sln
UE_ENGINE=C:\path\to\UnrealEngine
PROJECT_ROOT=C:\path\to\project
UE_PROJECT=C:\path\to\MyProject.uproject
```

These are read by all VS scripts at runtime. If any are missing, the script exits with an error message naming the missing variable.

### Available Skills

| Skill | What It Does |
|-------|-------------|
| `/unreal-project-compilation` | Build project via VS DTE with UBT fallback, error analysis, and fix loop |

Accepts optional `[Configuration] [Platform]` arguments (e.g., `/unreal-project-compilation Development Editor Win64`).

### How the COM/DTE Automation Works

The PowerShell scripts (`build-editor-from-vs.ps1`, `launch-editor-from-vs.ps1`, `launch-vs.ps1`) use the Windows COM Running Object Table (ROT) to find the Visual Studio instance that has `UE_SOLUTION` loaded. They then:

1. Activate the requested solution configuration (`Configuration|Platform`)
2. Trigger a build (`SolutionBuild.BuildProject`) or debug session (`Debug.Start`)

**Windows only** — COM/DTE is not available on macOS or Linux.

### Regenerating Project Files

After adding or removing a C++ module, Source file, or plugin, regenerate the VS solution:

```powershell
& "$PROJECT_ROOT\GenerateProjectFiles.bat"
```

Or right-click the `.uproject` file in Explorer -> **Generate Visual Studio project files**.

### Build Fallback (UBT)

If VS is not running, `/vs:build-editor` automatically falls back to UnrealBuildTool:

```powershell
dotnet "$UE_ENGINE/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll" `
  -Target="<ProjectName>Editor Win64 <Configuration> -Project=`"$UE_PROJECT`"" `
  -WaitMutex -architecture=x64
```

This requires `UE_ENGINE` to be set correctly.

### Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "UE_SOLUTION is not set" | Env var missing | Add to `.claude/rules/project-vars.md` and `.claude/settings.local.json` → `env` |
| "No running Visual Studio instance found" | VS not open, or wrong `.sln` loaded | Open VS with the correct `.sln` |
| "Configuration not found in solution" | Config name mismatch | Verify the config name in VS -> Build -> Configuration Manager |
| RPC_E_CALL_REJECTED retries | VS busy (loading, building) | Script retries automatically; wait for VS to become idle |
| Editor window timeout (15 min) | First build or slow machine | Normal on clean build — wait for compilation to finish |
