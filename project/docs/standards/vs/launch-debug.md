# Launch Debug Reference

## Build Configurations

| Configuration | Use Case |
|--------------|----------|
| `DebugGame Editor` | Default — full debugging with editor, optimized engine code |
| `Debug Editor` | Full debug symbols everywhere (slow, large binaries) |
| `Development Editor` | Optimized game code with editor, faster iteration |

Platform is almost always `Win64`.

## PowerShell Scripts

| Script | Purpose |
|--------|---------|
| `launch-editor-from-vs.ps1` | Full orchestration: opens VS if needed, waits for solution, launches editor |
| `launch-vs.ps1` | Triggers F5 in an already-running VS instance |

Both scripts live at `$KC_PROJECT_ROOT/scripts/vs/`.

## VS COM/DTE Automation

The scripts use the Windows COM Running Object Table (ROT) to find the Visual Studio instance that has `KC_UE_SOLUTION` loaded. They then:

1. Get the `DTE` (Development Tools Environment) COM object
2. Set `SolutionConfiguration` to the requested config
3. Call `ExecuteCommand("Debug.Start")` to trigger F5
4. Poll for the Unreal Editor window via `Get-Process`

### COM Object Access

```powershell
# Find VS instance by solution path
$dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject("VisualStudio.DTE")
```

## Retry Logic

VS may reject COM calls while busy (compiling, loading solution, etc.):

| Error | Meaning | Handling |
|-------|---------|----------|
| `RPC_E_CALL_REJECTED` (0x80010001) | VS is busy | Auto-retry with backoff |
| `RPC_E_SERVERCALL_RETRYLATER` | VS processing another call | Auto-retry with backoff |

Scripts handle these automatically — no user intervention needed.

## Timeout Expectations

| Scenario | Expected Time |
|----------|--------------|
| VS already running, editor cached | 30-60 seconds |
| VS already running, full build needed | 2-5 minutes |
| VS not running, first launch | 5-15 minutes |
| VS not running, clean build | 10-20 minutes |

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "No VS instance found" | VS not running or wrong solution | Script auto-launches VS when using full launch |
| Build fails | Compilation errors | Check Output window in VS, fix errors, retry |
| Editor doesn't appear | Build succeeded but editor crashed on startup | Check `Saved/Logs/` for crash logs |
| COM timeout | VS frozen or unresponsive | Kill VS via Task Manager, relaunch |
