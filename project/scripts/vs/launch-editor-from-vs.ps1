<#
.SYNOPSIS
    Ensures Visual Studio is open with the UE5 solution, then launches
    the Unreal Editor via Debug.Start (F5).
    Reads $env:KC_UE_SOLUTION for the .sln path, $env:KC_UE_PROJECT for the .uproject.
.PARAMETER Configuration
    Solution configuration name (default: "DebugGame Editor")
.PARAMETER Platform
    Solution platform name (default: "Win64")
#>
param(
    [string]$Configuration = "DebugGame Editor",
    [string]$Platform      = "Win64"
)

$ErrorActionPreference = "Stop"

$solutionPath = $env:KC_UE_SOLUTION
if (-not $solutionPath) {
    Write-Error "KC_UE_SOLUTION is not set. Set it to your UE5.sln path."
    exit 1
}

$projectPath = $env:KC_UE_PROJECT
if (-not $projectPath) {
    Write-Error "KC_UE_PROJECT is not set. Set it to your .uproject path."
    exit 1
}

$projectName = [IO.Path]::GetFileNameWithoutExtension($projectPath)

Add-Type @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

public class ROTHelperEditor {
    [DllImport("ole32.dll")]
    private static extern int GetRunningObjectTable(int reserved, out IRunningObjectTable pprot);

    [DllImport("ole32.dll")]
    private static extern int CreateBindCtx(int reserved, out IBindCtx ppbc);

    public static List<object> GetDTEInstances() {
        var result = new List<object>();
        IRunningObjectTable rot;
        if (GetRunningObjectTable(0, out rot) != 0) return result;

        IEnumMoniker enumMoniker;
        rot.EnumRunning(out enumMoniker);

        var moniker = new IMoniker[1];
        while (enumMoniker.Next(1, moniker, IntPtr.Zero) == 0) {
            IBindCtx ctx;
            CreateBindCtx(0, out ctx);
            string name;
            moniker[0].GetDisplayName(ctx, null, out name);
            if (name.StartsWith("!VisualStudio.DTE")) {
                object obj;
                rot.GetObject(moniker[0], out obj);
                result.Add(obj);
            }
        }
        return result;
    }
}
'@

function Find-DTE {
    foreach ($obj in [ROTHelperEditor]::GetDTEInstances()) {
        try {
            if ([IO.Path]::GetFullPath($obj.Solution.FullName) -ieq [IO.Path]::GetFullPath($solutionPath)) {
                return $obj
            }
        } catch {}
    }
    return $null
}

# Check if VS is already running with our solution
$dte = Find-DTE

if ($null -eq $dte) {
    Write-Host "Visual Studio not running with solution - launching..."
    Start-Process devenv $solutionPath

    # Poll until VS registers in the ROT with our solution loaded
    $timeout = 120
    $elapsed = 0
    $interval = 3
    while ($elapsed -lt $timeout) {
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        $dte = Find-DTE
        if ($null -ne $dte) {
            Write-Host "Visual Studio ready after $elapsed seconds."
            break
        }
        Write-Host "Waiting for Visual Studio... $elapsed seconds elapsed"
    }

    if ($null -eq $dte) {
        Write-Error "Timed out waiting for Visual Studio to load $solutionPath"
        exit 1
    }
} else {
    Write-Host "Found running VS $($dte.Version) with $($dte.Solution.FullName)"
}

# Wait until the solution has fully loaded (projects appear)
Write-Host "Waiting for solution to finish loading..."
$loadTimeout = 180
$loadElapsed = 0
while ($loadElapsed -lt $loadTimeout) {
    try {
        $count = $dte.Solution.Projects.Count
        if ($count -gt 0) {
            Write-Host "Solution loaded ($count projects)."
            break
        }
    } catch {}
    Start-Sleep -Seconds 3
    $loadElapsed += 3
    Write-Host "Still loading... $loadElapsed seconds elapsed"
}
if ($loadElapsed -ge $loadTimeout) {
    Write-Warning "Solution project count still 0 after $loadTimeout seconds - proceeding anyway."
}

# Activate the correct solution configuration
$expectedCtxName = $Configuration -replace ' ', '_'
$targetConfig = $null
foreach ($cfg in $dte.Solution.SolutionBuild.SolutionConfigurations) {
    if ($cfg.Name -ne $Configuration) { continue }
    $ctx = $cfg.SolutionContexts | Where-Object { $_.ProjectName -like "*$projectName.vcxproj" } | Select-Object -First 1
    if ($ctx -and $ctx.ConfigurationName -eq $expectedCtxName) {
        $targetConfig = $cfg
        break
    }
}

if ($null -eq $targetConfig) {
    Write-Error "Configuration '$Configuration|$Platform' not found in solution."
    exit 1
}
$targetConfig.Activate()

Write-Host "Starting debug session: $Configuration|$Platform"

# VS may still be initializing - retry on RPC_E_CALL_REJECTED
$maxAttempts = 10
for ($i = 1; $i -le $maxAttempts; $i++) {
    try {
        $dte.ExecuteCommand("Debug.Start")
        Write-Host "Editor launch initiated. Waiting for editor window..."
        break
    } catch [System.Runtime.InteropServices.COMException] {
        if ($_.Exception.HResult -eq [int]0x80010001 -and $i -lt $maxAttempts) {
            Write-Host "VS busy, retrying in 3s... (attempt $i/$maxAttempts)"
            Start-Sleep -Seconds 3
        } else {
            throw
        }
    }
}

# Wait for the Unreal Editor window to appear
$editorTimeout = 900
$editorElapsed = 0
Write-Host "Waiting for Unreal Editor window (this may take several minutes)..."
while ($editorElapsed -lt $editorTimeout) {
    $proc = Get-Process UnrealEditor -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowTitle -ne "" } |
            Select-Object -First 1
    if ($proc) {
        Write-Host "Unreal Editor is ready: $($proc.MainWindowTitle)"
        break
    }
    Start-Sleep -Seconds 10
    $editorElapsed += 10
    Write-Host "  Still launching... $editorElapsed seconds elapsed"
}
if ($editorElapsed -ge $editorTimeout) {
    Write-Warning "Timed out waiting for Unreal Editor window after $editorTimeout seconds."
}
