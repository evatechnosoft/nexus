$ErrorActionPreference = "Stop"

$policyPath = "C:/projects/deanos/.agent-bridge/nexus-policy.json"
$mapPath = "C:/projects/deanos/.agent-bridge/nexus-skill-map.json"

if (-not (Test-Path $policyPath)) { throw "Policy file not found: $policyPath" }
if (-not (Test-Path $mapPath)) { throw "Map file not found: $mapPath" }

$policy = Get-Content -LiteralPath $policyPath -Raw | ConvertFrom-Json
$map = Get-Content -LiteralPath $mapPath -Raw | ConvertFrom-Json

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

function Add-Error([string]$m) { $errors.Add($m) }
function Add-Warn([string]$m) { $warnings.Add($m) }

foreach ($required in @($policy.requiredFiles)) {
    if (-not (Test-Path -LiteralPath $required)) {
        Add-Error "Missing required file: $required"
    }
}

$allMapPaths = New-Object System.Collections.Generic.List[string]
foreach ($p in @($map.default)) { if ($p) { $allMapPaths.Add($p) } }

if ($map.tools) {
    foreach ($toolName in $map.tools.PSObject.Properties.Name) {
        foreach ($p in @($map.tools.$toolName)) {
            if ($p) { $allMapPaths.Add($p) }
        }
    }
}

foreach ($p in $allMapPaths) {
    if (-not (Test-Path -LiteralPath $p)) {
        Add-Warn "Mapped path not found: $p"
    }
}

# Validate read-only roots are only referenced, not expected to be written by workspace scripts.
$workspaceScripts = @(
    "C:/projects/deanos/scripts/resolve-nexus-context.ps1",
    "C:/projects/deanos/scripts/update-nexus-knowledge.ps1",
    "C:/projects/deanos/scripts/validate-nexus-safety.ps1"
)

foreach ($script in $workspaceScripts) {
    if (-not (Test-Path -LiteralPath $script)) { continue }
    $content = Get-Content -LiteralPath $script -Raw
    foreach ($ro in @($policy.readOnlyRoots)) {
        if ($content -match [regex]::Escape("Set-Content -LiteralPath $ro") -or $content -match [regex]::Escape("Out-File $ro")) {
            Add-Error "Potential write to read-only root in script: $script => $ro"
        }
    }
}

# Smoke checks for lazy resolver
$toolJson = & pwsh -NoProfile -ExecutionPolicy Bypass -File "C:/projects/deanos/scripts/resolve-nexus-context.ps1" -Mode tool -ToolName mcp -AsJson | Out-String
if ([string]::IsNullOrWhiteSpace($toolJson)) {
    Add-Error "Resolver tool mode returned empty output"
}

$citeJson = & pwsh -NoProfile -ExecutionPolicy Bypass -File "C:/projects/deanos/scripts/resolve-nexus-context.ps1" -Mode citation -RefText "@rule:memory-decisions @guide:NEXUS-UPDATE-GUIDE" -AsJson | Out-String
if ([string]::IsNullOrWhiteSpace($citeJson)) {
    Add-Error "Resolver citation mode returned empty output"
}

$status = if ($errors.Count -eq 0) { "PASS" } else { "FAIL" }

Write-Host "Nexus Safety Validation: $status"
if ($warnings.Count -gt 0) {
    Write-Host "Warnings:"
    foreach ($w in $warnings) { Write-Host "- $w" }
}
if ($errors.Count -gt 0) {
    Write-Host "Errors:"
    foreach ($e in $errors) { Write-Host "- $e" }
    exit 1
}
