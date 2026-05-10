# Compile Project Reference

---

## Build Targets

| Target | Suffix | Use Case |
|--------|--------|----------|
| {ProjectName}Editor | `Editor` | Editor build -- iterative development |
| {ProjectName}Game | _(empty)_ | Standalone game client |
| {ProjectName}Server | `Server` | Dedicated server |
| {ProjectName}Client | `Client` | Network client |
| {ProjectName}GameEOS | `GameEOS` | EOS-enabled game |
| {ProjectName}StreamingClient | `StreamingClient` | Streaming/spectator client |

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
dotnet "$KC_UE_ENGINE/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll" \
  -Target="${PROJECT_NAME}${SUFFIX} Win64 ${CONFIG} -Project=\"$KC_UE_PROJECT\"" \
  -WaitMutex -architecture=x64
```

## Regenerating Project Files

After adding/removing C++ modules, source files, or plugins:

```powershell
& "$KC_PROJECT_ROOT\GenerateProjectFiles.bat"
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "KC_UE_SOLUTION is not set" | Env var missing | Add to `CLAUDE.local.md` |
| "No running Visual Studio instance found" | VS not open or wrong .sln | Open VS with correct `.sln` |
| "Configuration not found" | Config name mismatch | Check VS Build > Configuration Manager |
| RPC_E_CALL_REJECTED retries | VS busy | Script retries automatically; wait |
| Editor window timeout (15 min) | First/clean build | Normal -- wait for compilation |

## Environment Variable Verification

- `KC_UE_SOLUTION`: file exists at path
- `KC_UE_ENGINE`: contains `Engine/Binaries/DotNET/UnrealBuildTool/UnrealBuildTool.dll`
- `KC_PROJECT_ROOT`: contains `.claude/`
- `KC_UE_PROJECT`: file exists, is a `.uproject`
