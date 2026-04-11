---
id: rule--nexus--branching
type: workflow
context: global
extends: rule--nexus--master
description: Nexus Hub iÃ§in kesinleÅŸmiÅŸ dallanma (branching) ve commit protokolÃ¼.
---
# NEXUS BRANCHING PROTOCOL (STRICT)

Bu kural 11 Nisan 2026 itibariyle MÃœHÃœRLENMÄ°ÅžTÄ°R. HiÃ§bir AI veya insan operatÃ¶r doÄŸrudan `dev` veya `prod` branch'lerine commit atamaz.

## 🌿 DALLANMA STANDARTLARI
TÃ¼m deÄŸiÅŸiklikler iÃ§in yeni bir dal (branch) aÃ§Ä±lmasÄ± ZORUNLUDUR:

1. **feature/**: Yeni Ã¶zellikler, uydular (satellites) veya bÃ¼yÃ¼k hiyerarÅŸi deÄŸiÅŸiklikleri.
   - *Ã–rnek:* `feature/nexus-curator-v2`
2. **fix/**: Bilinen hatalarÄ±n, bozulan script'lerin dÃ¼zeltilmesi.
   - *Ã–rnek:* `fix/nexus-sync-script`
3. **bug/**: Beklenmedik davranÄ±ÅŸlarÄ±n, Ã§akÄ±ÅŸmalarÄ±n (conflicts) giderilmesi.
   - *Ã–rnek:* `bug/index-path-conflict`

## 🔐 MERGE KURALLARI
- HiÃ§bir dal, `nexus-doctor` raporu %100 "HEALTHY" yanmadan `dev` ile birleÅŸtirilemez.
- `dev` branch'i her zaman "staging" (test) ortamÄ±dÄ±r.
- `prod` branch'i sadece CD (Continuous Deployment) onayÄ±yla gÃ¼ncellenir.

## 🖋️ COMMIT PROTOKOLÃœ
- Commit mesajlarÄ± `feat:`, `fix:`, `refactor:`, `docs:` gibi Conventional Commits standartlarÄ±na uygun olmalÄ±dÄ±r.
- DeÄŸiÅŸiklik sonrasÄ± `nexus-sync build` ve `build_skill_index.py` Ã§alÄ±ÅŸtÄ±rÄ±lmÄ±ÅŸ olmalÄ±dÄ±r.

**MÃœHÃœR TARÄ°HÄ°:** 11 Nisan 2026, 16:25 (Istanbul UTC+3)
**DURUM:** AKTÄ°F / ZORUNLU
