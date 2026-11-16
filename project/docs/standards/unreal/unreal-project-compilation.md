# Compile Project Reference

---

## Build Targets

| Target | Suffix | Use Case |
|--------|--------|----------|
| {ProjectName}Editor | `Editor` | Editor build -- iterative development |
| {ProjectName}Game | _(empty)_ | Standalone game client |
| {ProjectName}Server | `Server` | Dedicated server |
| {ProjectName}Client | `Client` | Network client |
| {ProjectName}<Variant> | `<Variant>` | Project-specific targets (see `Source/*.Target.cs`) |

Project specifics: read {{PROJECT_NOTES_DIR}}\standards-unreal-project-compilation.md if it exists.

## Build Configurations

| Configuration | Use Case |
|--------------|----------|
| DebugGame | Gameplay debugging, faster iteration (recommended for Editor) |
| Debug | Full debugging, slow iteration |
| Development | Optimized, limited debugging |
| Shipping | Final build, no editor, no debug |
| Test | Test builds |

## UBT Command to Compile

```bash
"{{UBT_DOTNET}}" \
  "{{UBT_DLL}}" \
  -Target="${PROJECT_NAME}${SUFFIX} Win64 ${CONFIG} -Project=\"$UE_PROJECT\"" \
  -WaitMutex -architecture=x64
```

## Regenerating Project Files

After adding/removing C++ modules, source files, or plugins:

```powershell
& "$PROJECT_ROOT\GenerateProjectFiles.bat"
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "UE_SOLUTION is not set" | Env var missing | Add to `.claude/rules/project-vars.md` and `.claude/settings.local.json` → `env` |
| "No running Visual Studio instance found" | VS not open or wrong .sln | Open VS with correct `.sln` |
| "Configuration not found" | Config name mismatch | Check VS Build > Configuration Manager |
| RPC_E_CALL_REJECTED retries | VS busy | Script retries automatically; wait |
| Editor window timeout (15 min) | First/clean build | Normal -- wait for compilation |

## Environment Variable Verification

- `UE_SOLUTION`: file exists at path
- `UE_ENGINE`: contains `Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll`
- `PROJECT_ROOT`: contains `.claude/`
- `UE_PROJECT`: file exists, is a `.uproject`
