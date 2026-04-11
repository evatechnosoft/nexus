# Commit Message Rules

> Guncelleme: 2026-04-07 | Uygulama: evatechnosoft/* tum repolar

## Format

```
<type>(<scope>): <baslik>

## Summary
<1-3 satir: ne degisti, neden>

## Changes
- <dosya>: <ne yapildi>

## Future
- <planlanan is> (opsiyonel)

## Fix
- <root cause> (opsiyonel)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## Type Kategorileri

| Type | Durum |
|---|---|
| feat | Yeni ozellik |
| fix | Bug duzeltme (root cause yaz) |
| refactor | Yeniden yapilandirma |
| test | Test ekleme/duzeltme |
| docs | Dokumantasyon |
| ci | CI/CD degisikligi |
| chore | Bakim/temizlik |
| backup | Otomatik memory backup (bot atar) |
| perf | Performans iyilestirme |

## Kurallar

1. Baslik max 72 karakter
2. Imperative: add / fix / update (added/fixes degil)
3. Scope onerilen: (api) (core) (memory) (ci) (runner)
4. Summary her zaman zorunlu
5. Changes: hangi dosya ne degisti
6. Future: sonraki session notu
7. Fix: bug varsa root cause, semptom degil
8. Co-Author: AI commit'lerde her zaman ekle

## Otomatik Bot Commit

backup-memory job attar:
  backup(prod): memory+skills [abc12345] 2026-04-07T14:30:00Z