# Nexus Safe Workflow

Bu belge, Claude/Gemini/GPT alanlarini bozmadan birlikte calismak icin minimum guvenli akis tanimlar.

## Hedef
- Birbirini bozmayan ayrik katmanlar.
- Tum degisiklikten once dogrulama.
- Siskin context yerine lazy secim.

## Komutlar
- Safety validation:
  `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/validate-nexus-safety.ps1`
- Context resolver (tool):
  `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/resolve-nexus-context.ps1 -Mode tool -ToolName mcp -AsJson`
- Context resolver (citation):
  `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/resolve-nexus-context.ps1 -Mode citation -RefText "@rule:memory-decisions @guide:NEXUS-UPDATE-GUIDE" -AsJson`
- Snapshot/report update:
  `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/update-nexus-knowledge.ps1`

## Kurallar
- `.claude` ve `.gemini` read-only kabul edilir.
- Workspace tarafinda degisiklikler `deanos` ve `deanos/.gpt` altinda tutulur.
- Her buyuk degisiklikten once `validate-nexus-safety.ps1` calistirilir.
