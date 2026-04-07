$ErrorActionPreference = "Stop"

$base = "C:/Users/Deacjx/.gpt"
$claude = "C:/Users/Deacjx/.claude"
$gemini = "C:/Users/Deacjx/.gemini"
$mcpPath = Join-Path $base "mcp.json"
$statusPath = Join-Path $base "sync-status.json"

$checks = [ordered]@{
    claude = Test-Path $claude
    gemini = Test-Path $gemini
    gpt = Test-Path $base
    mcp = Test-Path $mcpPath
}

if (-not $checks.gpt) {
    throw "GPT root not found: $base"
}

if (-not $checks.claude -or -not $checks.gemini) {
    throw "Required source folders missing. Claude=$($checks.claude) Gemini=$($checks.gemini)"
}

if (-not $checks.mcp) {
    throw "MCP config not found: $mcpPath"
}

$payload = [ordered]@{
    syncedAt = (Get-Date).ToString("o")
    sources = [ordered]@{
        claude = $claude
        gemini = $gemini
        gpt = $base
    }
    status = $checks
}

$payload | ConvertTo-Json -Depth 10 | Set-Content -Path $statusPath -Encoding UTF8
Write-Host "GPT sync check complete"
Write-Host "Status file: $statusPath"
