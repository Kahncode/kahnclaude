<#
.SYNOPSIS
    One-shot machine check before building or testing: editor, Live Coding, UBT and automation runs.
    Always exits 0 so the PowerShell tool never reports a failure when nothing is running.
    Names come from project vars (EDITOR_PROCESS, TEST_RUNNER_SCRIPT, TEMP_BASE); stock UE defaults when unset.
#>
$editorProcess = 'UnrealEditor.exe'; $testRunner = ''; $tempBase = '.temp'
try {
    . "$HOME\.claude\scripts\lib\ProjectVars.ps1"
    $editorProcess = Get-ProjectVar EDITOR_PROCESS -Default $editorProcess
    $testRunner = Get-ProjectVar TEST_RUNNER_SCRIPT -Default ''
    $tempBase = Get-ProjectVar TEMP_BASE -Default $tempBase
} catch {
    Write-Output "project vars unavailable ($($_.Exception.Message)); using UnrealEditor defaults."
}
# MyGameEditor-Win64-DebugGame.exe -> MyGameEditor (WMI LIKE '<stem>%').
$editorStem = ([IO.Path]::GetFileNameWithoutExtension($editorProcess) -split '-')[0]
$editorNames = @(@($editorStem, 'UnrealEditor') | Select-Object -Unique)
$runnerNames = @('Run-AutomationTest')
if ($testRunner) { $runnerNames += [IO.Path]::GetFileNameWithoutExtension($testRunner) }
$runnerNames = @($runnerNames | Select-Object -Unique)
$filter = (($editorNames + @('LiveCodingConsole')) | ForEach-Object { "Name like '$_%'" }) -join ' or '
$filter += " or (Name='dotnet.exe' and CommandLine like '%UnrealBuildTool%') " +
           "or (Name='powershell.exe' and (" + (($runnerNames | ForEach-Object { "CommandLine like '%$_%'" }) -join ' or ') + "))"
$procs = @(Get-CimInstance Win32_Process -Filter $filter -ErrorAction SilentlyContinue)
if ($procs.Count -eq 0) {
    Write-Output "IDLE: no editor, Live Coding, UBT or automation run."
    exit 0
}
# Owner = the TEMP_BASE\<agent>-<CL> folder named in the process's (or its parent's) command line; "?" = unknown, so not yours.
$ownerPattern = '[\\/]' + [regex]::Escape((Split-Path $tempBase -Leaf)) + '[\\/]([\w.-]+)'
function Get-Owner($p) {
    foreach ($cmd in @($p.CommandLine, (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue).CommandLine)) {
        if ($cmd -match $ownerPattern) { return $Matches[1] }
    }
    return '?'
}
$procs | ForEach-Object {
    $kind = switch -Wildcard ($_.Name) {
        'LiveCodingConsole*' { 'LiveCoding' }
        'dotnet.exe'         { 'UBT' }
        'powershell.exe'     { 'TestRun' }
        default {
            if ($_.CommandLine -match '-unattended' -and $_.CommandLine -match 'Automation RunTest') { 'Editor(test run)' } else { 'Editor' }
        }
    }
    [pscustomobject]@{ Kind = $kind; PID = $_.ProcessId; Name = $_.Name; Owner = (Get-Owner $_); Started = $_.CreationDate }
} | Format-Table -AutoSize | Out-String -Width 200 | Write-Output
exit 0
