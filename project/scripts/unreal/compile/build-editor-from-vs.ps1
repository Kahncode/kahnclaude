<#
.SYNOPSIS
    Triggers a build of the UE5 project in the running Visual Studio instance.
    Reads $env:KC_UE_SOLUTION for the .sln path.
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

# Read project paths from environment
$solutionPath = $env:KC_UE_SOLUTION
if (-not $solutionPath) {
    Write-Error "KC_UE_SOLUTION is not set. Set it to your UE5.sln path (e.g. C:\p4\MyProject\UE5.sln)"
    exit 1
}

$projectPath = $env:KC_UE_PROJECT
if (-not $projectPath) {
    Write-Error "KC_UE_PROJECT is not set. Set it to your .uproject path"
    exit 1
}

# Derive project name from .uproject filename
$projectName = [IO.Path]::GetFileNameWithoutExtension($projectPath)
$projectUnique = "Engine\Intermediate\ProjectFiles\$projectName.vcxproj"

# Enumerate all VS DTE instances from the COM Running Object Table
Add-Type @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;

public class ROTHelper {
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
"@

$configName = "$Configuration|$Platform"

# Find the VS instance that has our solution loaded
$dte = $null
foreach ($obj in [ROTHelper]::GetDTEInstances()) {
    try {
        if ([IO.Path]::GetFullPath($obj.Solution.FullName) -ieq [IO.Path]::GetFullPath($solutionPath)) {
            $dte = $obj
            break
        }
    } catch {}
}

if ($null -eq $dte) {
    Write-Error "No running Visual Studio instance found with: $solutionPath"
    exit 1
}

Write-Host "VS $($dte.Version) - $($dte.Solution.FullName)"
Write-Host "Building: $configName"

# Activate the target solution configuration
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
    Write-Error "Configuration '$configName' not found in solution."
    exit 1
}
$targetConfig.Activate()

# Build just the project and wait for completion
$dte.Solution.SolutionBuild.BuildProject($configName, $projectUnique, $true)

$failed = $dte.Solution.SolutionBuild.LastBuildInfo
if ($failed -eq 0) {
    Write-Host "Build succeeded."
    exit 0
} else {
    Write-Error "Build failed: $failed project(s) failed."
    exit 1
}
