param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("tool", "citation")]
    [string]$Mode,

    [string]$ToolName,
    [string]$RefText,
    [switch]$AsJson
)

$ErrorActionPreference = "Stop"
$mapPath = "C:/projects/deanos/.agent-bridge/nexus-skill-map.json"

if (-not (Test-Path $mapPath)) {
    throw "Map file not found: $mapPath"
}

$map = Get-Content -LiteralPath $mapPath -Raw | ConvertFrom-Json
$result = New-Object System.Collections.Generic.List[string]

function Add-IfExists {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return }
    if (Test-Path -LiteralPath $Path) {
        if (-not $result.Contains($Path)) {
            $result.Add($Path)
        }
    }
}

foreach ($item in @($map.default)) {
    Add-IfExists -Path $item
}

if ($Mode -eq "tool") {
    if ([string]::IsNullOrWhiteSpace($ToolName)) {
        throw "Tool mode requires -ToolName"
    }

    $key = $ToolName.ToLowerInvariant()

    if ($map.tools.$key) {
        foreach ($item in @($map.tools.$key)) {
            Add-IfExists -Path $item
        }
    } else {
        foreach ($name in $map.tools.PSObject.Properties.Name) {
            if ($key -like "*$name*" -or $name -like "*$key*") {
                foreach ($item in @($map.tools.$name)) {
                    Add-IfExists -Path $item
                }
            }
        }
    }
}

if ($Mode -eq "citation") {
    if ([string]::IsNullOrWhiteSpace($RefText)) {
        throw "Citation mode requires -RefText"
    }

    foreach ($prefixName in $map.citationPrefixes.PSObject.Properties.Name) {
        $basePath = $map.citationPrefixes.$prefixName
        $escapedPrefix = [regex]::Escape($prefixName)
        $matches = [regex]::Matches($RefText, "$escapedPrefix([A-Za-z0-9_\-\.]+)")

        foreach ($m in $matches) {
            $token = $m.Groups[1].Value
            if ([string]::IsNullOrWhiteSpace($token)) { continue }

            $candidates = @(
                (Join-Path $basePath ($token + ".md")),
                (Join-Path $basePath ($token + ".yaml")),
                (Join-Path $basePath ($token + ".yml")),
                (Join-Path $basePath $token)
            )

            foreach ($candidate in $candidates) {
                Add-IfExists -Path $candidate
            }
        }
    }
}

$output = [ordered]@{
    mode = $Mode
    tool = $ToolName
    count = $result.Count
    files = @($result)
}

if ($AsJson) {
    $output | ConvertTo-Json -Depth 8
} else {
    Write-Host "Mode: $Mode"
    if (-not [string]::IsNullOrWhiteSpace($ToolName)) {
        Write-Host "Tool: $ToolName"
    }
    Write-Host "Selected files: $($result.Count)"
    foreach ($path in $result) {
        Write-Host "- $path"
    }
}
