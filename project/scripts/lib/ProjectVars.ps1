# Dot-source, then Get-ProjectVar NAME [-Default x]. Reads <project>/.claude/rules/project-vars.md
# (```ini blocks of KEY=VALUE). Order: non-empty env var > file. {{NAME}} inside values expands.

function Find-ProjectVarsFile {
    param([string]$Start = (Get-Location).Path)
    $rel = Join-Path '.claude' (Join-Path 'rules' 'project-vars.md')
    if ($env:CLAUDE_PROJECT_DIR -and (Test-Path (Join-Path $env:CLAUDE_PROJECT_DIR $rel))) {
        return (Join-Path $env:CLAUDE_PROJECT_DIR $rel)
    }
    $dir = Get-Item -LiteralPath $Start
    while ($dir) {
        $candidate = Join-Path $dir.FullName $rel
        if (Test-Path $candidate) { return $candidate }
        $dir = $dir.Parent
    }
    return $null
}

function Read-ProjectVars {
    param([string]$File = (Find-ProjectVarsFile))
    $values = @{}
    if (-not $File) { return $values }
    $inIni = $false
    foreach ($raw in Get-Content -LiteralPath $File -Encoding UTF8) {
        $line = $raw.Trim()
        if ($line.StartsWith('```')) {
            if ($inIni) { $inIni = $false } else { $inIni = ($line.Substring(3).Trim() -eq 'ini') }
            continue
        }
        if (-not $inIni -or -not $line -or $line[0] -in '#', ';' -or -not $line.Contains('=')) { continue }
        $key, $value = $line.Split('=', 2)
        $values[$key.Trim()] = $value.Trim()
    }
    return $values
}

function Expand-ProjectVar {
    param([string]$Value, [hashtable]$Vars, [int]$Depth = 0)
    if ($Depth -gt 10) { throw "project-vars: {{...}} nesting too deep in '$Value'" }
    return [regex]::Replace($Value, '\{\{([A-Z][A-Z0-9_]*)\}\}', {
        param($m)
        $name = $m.Groups[1].Value
        $inner = [Environment]::GetEnvironmentVariable($name)
        if (-not $inner) { $inner = $Vars[$name] }
        if ($null -eq $inner) { return $m.Value }
        return (Expand-ProjectVar -Value $inner -Vars $Vars -Depth ($Depth + 1))
    })
}

function Get-ProjectVar {
    param([Parameter(Mandatory)][string]$Name, [string]$Default, [string]$File = (Find-ProjectVarsFile))
    $vars = Read-ProjectVars -File $File
    $value = [Environment]::GetEnvironmentVariable($Name)
    if (-not $value) { $value = $vars[$Name] }
    if ($value) { return (Expand-ProjectVar -Value $value -Vars $vars) }
    if ($PSBoundParameters.ContainsKey('Default')) { return $Default }
    $where = if ($File) { $File } else { '<project>/.claude/rules/project-vars.md (not found)' }
    throw "$Name is not set: add it to $where (template: ~/.claude/templates/unreal-project/project-vars.md)"
}
