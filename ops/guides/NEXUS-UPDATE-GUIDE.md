# Nexus Update Guide

Bu rehber, Claude, Gemini, GPT ve deanos uzerindeki bilgi alanlarina eklenen yeni dosyalari kontrol etmek icin kullanilir.

## Amac
- Yeni kural, hatirlatma, skill veya guide dosyalarini tek raporda gormek.
- Ayrik yapilari bozmadan degisiklikleri takip etmek.
- Snapshot alarak bir sonraki kontrolde farklari tespit etmek.

## Calisma Alani
- `C:/Users/Deacjx/.claude`
- `C:/Users/Deacjx/.gemini`
- `C:/Users/Deacjx/.gpt`
- `C:/projects/deanos`

## Komutlar
- `pwsh -NoProfile -ExecutionPolicy Bypass -File C:/projects/deanos/scripts/update-nexus-knowledge.ps1`

## Cikti Dosyalari
- State: `C:/projects/deanos/.agent-bridge/state/nexus-state.json`
- Report: `C:/projects/deanos/.agent-bridge/reports/nexus-report.md`

## Kural
- Script dosya kopyalamaz.
- Yeni eklenen dosyalar raporlanir.
- Gerekirse hafiza notu ve kisa guide guncellenir.
- Ilk calistirmada baseline snapshot olusur; sonraki calistirmalar fark raporu üretir.
