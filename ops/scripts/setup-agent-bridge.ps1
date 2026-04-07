$ErrorActionPreference = "Stop"

$bridgeConfig = "C:/projects/deanos/.agent-bridge/mcp-bridge.json"
$userMcpConfig = "C:/Users/Deacjx/.mcp.json"
$backupConfig = "C:/Users/Deacjx/.mcp.json.backup.agent-bridge"

if (-not (Test-Path $bridgeConfig)) {
    throw "Bridge config not found: $bridgeConfig"
}

if (Test-Path $userMcpConfig) {
    Copy-Item -Path $userMcpConfig -Destination $backupConfig -Force
    Write-Host "Backup created: $backupConfig"
}

$bridge = Get-Content -Path $bridgeConfig -Raw | ConvertFrom-Json

if (Test-Path $userMcpConfig) {
    $current = Get-Content -Path $userMcpConfig -Raw | ConvertFrom-Json
} else {
    $current = [pscustomobject]@{ mcpServers = [pscustomobject]@{} }
    Write-Host "No existing .mcp.json found, new one will be created."
}

if (-not $current.mcpServers) {
    $current | Add-Member -NotePropertyName mcpServers -NotePropertyValue ([pscustomobject]@{})
}

$bridgeServerName = "agent-knowledge-filesystem"
$bridgeServerValue = $bridge.mcpServers.$bridgeServerName

if ($current.mcpServers.PSObject.Properties.Name -contains $bridgeServerName) {
    $current.mcpServers.$bridgeServerName = $bridgeServerValue
    Write-Host "Updated MCP server: $bridgeServerName"
} else {
    $current.mcpServers | Add-Member -NotePropertyName $bridgeServerName -NotePropertyValue $bridgeServerValue
    Write-Host "Added MCP server: $bridgeServerName"
}

$current | ConvertTo-Json -Depth 20 | Set-Content -Path $userMcpConfig -Encoding UTF8
Write-Host "MCP bridge merged into: $userMcpConfig"
Write-Host "Source map: C:/projects/deanos/.agent-bridge/source-map.json"
