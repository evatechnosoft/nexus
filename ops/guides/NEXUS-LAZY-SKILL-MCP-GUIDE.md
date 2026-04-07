# Nexus Lazy Skill + MCP Guide

Bu yapi, MCP ve skill kaynaklarini tek seferde yuklemek yerine ihtiyac aninda cekmek icin tasarlandi.

## Prensip
- Tool cagrilirsa: sadece o araca bagli rule/guide/skill dosyalari secilir.
- Atif gecerse (`@rule:`, `@guide:`, `@skill:`): sadece atiflanan dosyalar secilir.
- Bu sayede context siskinligi azalir.

## Dosyalar
- Map: `C:/projects/deanos/.agent-bridge/nexus-skill-map.json`
- Resolver: `C:/projects/deanos/scripts/resolve-nexus-context.ps1`

## Kullanim
### 1) Tool bazli secim
`pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/resolve-nexus-context.ps1 -Mode tool -ToolName mcp -AsJson`

### 2) Atif bazli secim
`pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/resolve-nexus-context.ps1 -Mode citation -RefText "@rule:memory-decisions @guide:NEXUS-UPDATE-GUIDE @skill:best-practices" -AsJson`

## MCP ile baglantı akisi
1. Kullanici istegi gelir.
2. Resolver secim yapar (tool veya citation modu).
3. Donen dosyalar MCP filesystem ile okunur.
4. Sadece gerekli skill/rule/guide prompta eklenir.

## Not
- `nexus-skill-map.json` senin ana kontrol dosyan.
- Yeni skill/rule eklendikce map guncellenmeli.
