---
id: rule--nexus--branching
type: workflow
context: global
extends: rule--nexus--master
description: Nexus Hub için kesinleşmiş dallanma (branching) ve commit protokolü.
---
# NEXUS BRANCHING PROTOCOL (STRICT)

Bu kural 11 Nisan 2026 itibariyle MÜHÜRLENMİŞTİR. Hiçbir AI veya insan operatör doğrudan `dev` veya `prod` branch'lerine commit atamaz.

## 🌿 DALLANMA STANDARTLARI
Tüm değişiklikler için yeni bir dal (branch) açılması ZORUNLUDUR:

1. **feature/**: Yeni özellikler, uydular (satellites) veya büyük hiyerarşi değişiklikleri.
   - *Örnek:* `feature/nexus-curator-v2`
2. **fix/**: Bilinen hataların, bozulan script'lerin düzeltilmesi.
   - *Örnek:* `fix/nexus-sync-script`
3. **bug/**: Beklenmedik davranışların, çakışmaların (conflicts) giderilmesi.
   - *Örnek:* `bug/index-path-conflict`

## 🔐 MERGE KURALLARI
- Hiçbir dal, `nexus-doctor` raporu %100 "HEALTHY" yanmadan `dev` ile birleştirilemez.
- `dev` branch'i her zaman "staging" (test) ortamıdır.
- `prod` branch'i sadece CD (Continuous Deployment) onayıyla güncellenir.

## 🖋️ COMMIT PROTOKOLÜ
- Commit mesajları `feat:`, `fix:`, `refactor:`, `docs:` gibi Conventional Commits standartlarına uygun olmalıdır.
- Değişiklik sonrası `nexus-sync build` ve `build_skill_index.py` çalıştırılmış olmalıdır.

**MÜHÜR TARİHİ:** 11 Nisan 2026, 16:25 (Istanbul UTC+3)
**DURUM:** AKTİF / ZORUNLU
