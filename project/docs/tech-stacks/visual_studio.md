# Tech Stack Guide: Visual Studio

<!-- detection: auto | signal: .uproject present AND vswhere.exe found | prerequisite: unreal -->
<!-- prompt: "Do you use Visual Studio to build this project?" -->

---

## Setup — Environment Variables

Store in `CLAUDE.local.md` (machine-specific, never committed). `KC_UE_PROJECT` is set by `unreal.md` — do not ask again.

### Required

| Variable | How to Obtain |
|----------|---------------|
| `KC_UE_SOLUTION` | Full path to `*.sln` — scan project root and one level up |
| `KC_UE_ENGINE` | UE root directory — read `.uproject` `EngineAssociation` + registry lookup |
| `KC_PROJECT_ROOT` | Workspace root (parent of `.claude/`) — default to current working directory |

### Auto-Detection

- **KC_UE_SOLUTION:** `Get-ChildItem -Path "<root>", "<root>\.." -Filter "*.sln" -Depth 0` — offer first match, list if multiple
- **KC_UE_ENGINE:** Read `EngineAssociation` from `.uproject` -> query `HKLM:\SOFTWARE\EpicGames\Unreal Engine\<version-or-GUID>` -> `InstalledDirectory`; if relative path, resolve from root; ask user if lookup fails
- **KC_PROJECT_ROOT:** Default to cwd, confirm with user

### Verification

- `KC_UE_SOLUTION`: file exists
- `KC_UE_ENGINE`: contains `Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.dll`
- `KC_PROJECT_ROOT`: contains `.claude/`

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

Set these in `CLAUDE.local.md` (machine-specific, never committed to version control):

```
KC_UE_SOLUTION=C:\path\to\UE5.sln
KC_UE_ENGINE=C:\path\to\UnrealEngine
KC_PROJECT_ROOT=C:\path\to\project
KC_UE_PROJECT=C:\path\to\MyProject.uproject
```

These are read by all VS scripts at runtime. If any are missing, the script exits with an error message naming the missing variable.

### Available Skills

| Skill | What It Does |
|-------|-------------|
| `/unreal-project-compilation` | Build project via VS DTE with UBT fallback, error analysis, and fix loop |
| `/editor-lifecycle` | Opens VS if needed, sets the build configuration, and launches the editor with F5 (debugger attached) |

Both accept optional `[Configuration] [Platform]` arguments (e.g., `/editor-lifecycle Development Editor Win64`).

### How the COM/DTE Automation Works

The PowerShell scripts (`build-editor-from-vs.ps1`, `launch-editor-from-vs.ps1`, `launch-vs.ps1`) use the Windows COM Running Object Table (ROT) to find the Visual Studio instance that has `KC_UE_SOLUTION` loaded. They then:

1. Activate the requested solution configuration (`Configuration|Platform`)
2. Trigger a build (`SolutionBuild.BuildProject`) or debug session (`Debug.Start`)

**Windows only** — COM/DTE is not available on macOS or Linux.

### Regenerating Project Files

After adding or removing a C++ module, Source file, or plugin, regenerate the VS solution:

```powershell
& "$KC_PROJECT_ROOT\GenerateProjectFiles.bat"
```

Or right-click the `.uproject` file in Explorer -> **Generate Visual Studio project files**.

### Build Fallback (UBT)

If VS is not running, `/vs:build-editor` automatically falls back to UnrealBuildTool:

```powershell
dotnet "$KC_UE_ENGINE/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll" `
  -Target="<ProjectName>Editor Win64 <Configuration> -Project=`"$KC_UE_PROJECT`"" `
  -WaitMutex -architecture=x64
```

This requires `KC_UE_ENGINE` to be set correctly.

### Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "KC_UE_SOLUTION is not set" | Env var missing | Add to `CLAUDE.local.md` |
| "No running Visual Studio instance found" | VS not open, or wrong `.sln` loaded | Open VS with the correct `.sln` |
| "Configuration not found in solution" | Config name mismatch | Verify the config name in VS -> Build -> Configuration Manager |
| RPC_E_CALL_REJECTED retries | VS busy (loading, building) | Script retries automatically; wait for VS to become idle |
| Editor window timeout (15 min) | First build or slow machine | Normal on clean build — wait for compilation to finish |
