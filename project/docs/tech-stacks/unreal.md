# Tech Stack Guide: Unreal Engine

<!-- detection: auto | signal: .uproject at project root | prerequisite: none -->
<!-- prompt: "Unreal Engine project detected. Configure UE-specific settings?" -->

---

## Setup — Auto-Detection + Confirmation

| Step | Method | CLAUDE.md Section |
|------|--------|-------------------|
| 1. Detect UE version | Read `.uproject` -> `EngineAssociation` or `EngineVersion` | Tech Stack Details |
| 2. Detect project type | Read `*.Target.cs` for `TargetType`; check `.uproject` for `OnlineSubsystem`/replication plugins; `*Server.Target.cs` -> multiplayer | Project Overview, Tech Stack Details |
| 3. Detect engine setup | Check `.uproject` location + `EngineAssociation` value (version string -> Launcher, path -> Local, empty + Engine/ parent -> In-Engine, Engine/ at root -> Source Mods) | Project Structure, Tech Stack Details |
| 4. Detect platforms | Read `*.Target.cs` for platform conditionals; check `Config/Default*.ini`; scan `Platforms/`. Default Win64. | Tech Stack Details |
| 5. Detect plugins | Read `.uproject` -> `Plugins` array; list `"Enabled": true`; exclude engine defaults, highlight marketplace/custom | Tech Stack Details |
| 6. Detect build targets | Glob `*.Target.cs` in `Source/`; parse `Type = TargetType.X` | Service Ports |

### Engine Setup — CLAUDE.md mappings by detected type

- **Standalone (Launcher):** `engine from Epic Launcher`
- **Standalone (Local Path):** `engine at [path]`
- **In-Engine:** root is engine, project in subfolder
- **Engine-Source Mods:** document which subsystems are patched and why

### Defaults (no question needed)

- Don't modify `.generated.h`
- Don't edit `Intermediate/` or `Saved/`
- Test in PIE before committing

If the project also has a web UI, server backend, or other secondary tech, generic questions (Name, Description, Stack Summary, Patterns, Rules, Ports) may also be asked.
