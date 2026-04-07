$ErrorActionPreference = "Stop"

$watchItems = @(
    @{ Name = "claude-core"; Type = "file"; Path = "C:/Users/Deacjx/.claude/CLAUDE.md" },
    @{ Name = "claude-rules"; Type = "dir"; Path = "C:/Users/Deacjx/.claude/rules" },
    @{ Name = "claude-skills"; Type = "dir"; Path = "C:/Users/Deacjx/.claude/skills" },
    @{ Name = "claude-commands"; Type = "dir"; Path = "C:/Users/Deacjx/.claude/commands" },
    @{ Name = "claude-library"; Type = "dir"; Path = "C:/Users/Deacjx/.claude/library" },
    @{ Name = "gemini-core"; Type = "file"; Path = "C:/Users/Deacjx/.gemini/GEMINI.md" },
    @{ Name = "gemini-manifest"; Type = "file"; Path = "C:/Users/Deacjx/.gemini/manifest.yaml" },
    @{ Name = "gemini-memory"; Type = "dir"; Path = "C:/Users/Deacjx/.gemini/memory" },
    @{ Name = "gemini-guides"; Type = "dir"; Path = "C:/Users/Deacjx/.gemini/guides" },
    @{ Name = "gemini-skills"; Type = "dir"; Path = "C:/Users/Deacjx/.gemini/skills" },
    @{ Name = "gpt-core"; Type = "file"; Path = "C:/Users/Deacjx/.gpt/GPT.md" },
    @{ Name = "gpt-manifest"; Type = "file"; Path = "C:/Users/Deacjx/.gpt/manifest.yaml" },
    @{ Name = "gpt-mcp"; Type = "file"; Path = "C:/Users/Deacjx/.gpt/mcp.json" },
    @{ Name = "gpt-memory"; Type = "dir"; Path = "C:/Users/Deacjx/.gpt/memory" },
    @{ Name = "gpt-guides"; Type = "dir"; Path = "C:/Users/Deacjx/.gpt/guides" },
    @{ Name = "gpt-skills"; Type = "dir"; Path = "C:/Users/Deacjx/.gpt/skills" },
    @{ Name = "deanos-guides"; Type = "dir"; Path = "C:/projects/deanos/guides" },
    @{ Name = "deanos-scripts"; Type = "dir"; Path = "C:/projects/deanos/scripts" },
    @{ Name = "bridge-core"; Type = "file"; Path = "C:/projects/deanos/.agent-bridge/README.md" },
    @{ Name = "bridge-manifest"; Type = "file"; Path = "C:/projects/deanos/.agent-bridge/mcp-bridge.json" },
    @{ Name = "bridge-source-map"; Type = "file"; Path = "C:/projects/deanos/.agent-bridge/source-map.json" }
)

$statePath = "C:/projects/deanos/.agent-bridge/state/nexus-state.json"
$reportPath = "C:/projects/deanos/.agent-bridge/reports/nexus-report.md"
$guidePath = "C:/projects/deanos/guides/NEXUS-UPDATE-GUIDE.md"

$ignoreSegmentPattern = '(?i)(\\cache\\|\\debug\\|\\file-history\\|\\logs\\|\\history\\|\\tmp\\|\\state\\|\\reports\\|\\backups\\|\\session-env\\|\\sessions\\|\\telemetry\\|\\paste-cache\\|\\shell-snapshots\\|\\node_modules\\|\\.git\\)'
$allowedExtensions = @('.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ps1', '.sh')

function Get-FileFingerprint {
    param([string]$Path)
    $item = Get-Item -LiteralPath $Path
    [pscustomobject]@{
        path = $Path
        length = $item.Length
        lastWriteTimeUtc = $item.LastWriteTimeUtc.ToString("o")
    }
}

function Get-WatchItems {
    foreach ($item in $watchItems) {
        if (-not (Test-Path $item.Path)) { continue }

        if ($item.Type -eq 'file') {
            Get-FileFingerprint -Path $item.Path
            continue
        }

        Get-ChildItem -LiteralPath $item.Path -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch $ignoreSegmentPattern } |
            Where-Object { $allowedExtensions -contains $_.Extension.ToLowerInvariant() } |
            ForEach-Object { Get-FileFingerprint -Path $_.FullName }
    }
}

function Convert-ListToMap {
    param($List)
    $map = @{}
    foreach ($item in @($List)) {
        if ($null -eq $item) { continue }
        if ([string]::IsNullOrWhiteSpace($item.path)) { continue }
        $map[$item.path] = $item
    }
    $map
}

$current = @((Get-WatchItems))
$previous = $null
if (Test-Path $statePath) {
    $previous = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
}

$currentMap = Convert-ListToMap -List $current
$previousMap = Convert-ListToMap -List $previous.items

$added = @()
$removed = @()
$modified = @()

foreach ($path in $currentMap.Keys) {
    if (-not $previousMap.ContainsKey($path)) {
        $added += $path
        continue
    }

    if (
        $currentMap[$path].length -ne $previousMap[$path].length -or
        $currentMap[$path].lastWriteTimeUtc -ne $previousMap[$path].lastWriteTimeUtc
    ) {
        $modified += $path
    }
}

foreach ($path in $previousMap.Keys) {
    if (-not $currentMap.ContainsKey($path)) {
        $removed += $path
    }
}

$timestamp = (Get-Date).ToString("o")
$snapshot = [ordered]@{
    syncedAt = $timestamp
    items = @($current)
}

$snapshot | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $statePath -Encoding UTF8

$report = New-Object System.Collections.Generic.List[string]
$report.Add("# Nexus Knowledge Update Report")
$report.Add("")
$report.Add("- Generated: $timestamp")
$report.Add("- Watched items: $($watchItems.Count)")
$report.Add("- Snapshot: $statePath")
$report.Add("")
$report.Add("## Summary")
$report.Add("- Added: $($added.Count)")
$report.Add("- Modified: $($modified.Count)")
$report.Add("- Removed: $($removed.Count)")
$report.Add("")

if ($added.Count -gt 0) {
    $report.Add("## Added")
    foreach ($item in ($added | Sort-Object)) { $report.Add("- $item") }
    $report.Add("")
}

if ($modified.Count -gt 0) {
    $report.Add("## Modified")
    foreach ($item in ($modified | Sort-Object)) { $report.Add("- $item") }
    $report.Add("")
}

if ($removed.Count -gt 0) {
    $report.Add("## Removed")
    foreach ($item in ($removed | Sort-Object)) { $report.Add("- $item") }
    $report.Add("")
}

$report.Add("## Notes")
$report.Add("- Claude, Gemini, GPT ve deanos alanlari ayrik tutulur.")
$report.Add("- Script kopyalama yapmaz; sadece farklari tespit edip snapshot alir.")
$report.Add("- Volatile klasorler (cache, debug, history, reports, state, backups) izleme disidir.")
$report.Add("- Dizin taramasinda sadece knowledge odakli uzantilar izlenir: .md, .txt, .json, .yaml, .yml, .toml, .ps1, .sh")
$report.Add("- `.claude/projects` operasyonel session gecmisi oldugu icin varsayilan izleme disidir.")

$report | Set-Content -LiteralPath $reportPath -Encoding UTF8

if (-not (Test-Path $guidePath)) {
    @"
# Nexus Update Guide

Bu rehber, Claude, Gemini, GPT ve deanos uzerindeki bilgi alanlarina eklenen yeni dosyalari kontrol etmek icin kullanilir.

## Amac
- Yeni kural, hatirlatma, skill veya guide dosyalarini tek raporda gormek.
- Ayrik yapilari bozmadan degisiklikleri takip etmek.
- Snapshot alarak bir sonraki kontrolde farklari tespit etmek.

## Calisma Alani
- `C:/Users/Deacjx/.claude/CLAUDE.md`
- `C:/Users/Deacjx/.claude/rules`
- `C:/Users/Deacjx/.claude/skills`
- `C:/Users/Deacjx/.claude/commands`
- `C:/Users/Deacjx/.claude/library`
- `C:/Users/Deacjx/.claude/projects`
- `C:/Users/Deacjx/.gemini/GEMINI.md`
- `C:/Users/Deacjx/.gemini/manifest.yaml`
- `C:/Users/Deacjx/.gemini/memory`
- `C:/Users/Deacjx/.gemini/guides`
- `C:/Users/Deacjx/.gemini/skills`
- `C:/Users/Deacjx/.gpt/GPT.md`
- `C:/Users/Deacjx/.gpt/manifest.yaml`
- `C:/Users/Deacjx/.gpt/mcp.json`
- `C:/Users/Deacjx/.gpt/memory`
- `C:/Users/Deacjx/.gpt/guides`
- `C:/Users/Deacjx/.gpt/skills`
- `C:/projects/deanos/guides`
- `C:/projects/deanos/scripts`
- `C:/projects/deanos/.agent-bridge/README.md`
- `C:/projects/deanos/.agent-bridge/mcp-bridge.json`
- `C:/projects/deanos/.agent-bridge/source-map.json`

## Komutlar
- `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/update-nexus-knowledge.ps1`

## Cikti Dosyalari
- State: `C:/projects/deanos/.agent-bridge/state/nexus-state.json`
- Report: `C:/projects/deanos/.agent-bridge/reports/nexus-report.md`

## Kural
- Script dosya kopyalamaz.
- Yeni eklenen dosyalar raporlanir.
- Gerekirse hafiza notu ve kisa guide guncellenir.
"@ | Set-Content -LiteralPath $guidePath -Encoding UTF8
}

Write-Host "Nexus knowledge update complete"
Write-Host "Report: $reportPath"
Write-Host "State: $statePath"
