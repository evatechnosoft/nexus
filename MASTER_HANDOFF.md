# ðŸ§  Nexus Master Manifest & Handoff (2026-04-05)

Bu dosya, projenin "Universal Nexus Brain" mimarisine geÃ§iÅŸ sonrasÄ± gÃ¼ncel dosya yapÄ±sÄ±nÄ±, kritik yollarÄ± ve operasyonel mantÄ±ÄŸÄ± iÃ§eren ana rehberdir.

## ðŸ“¡ Sistem Mimarisi (Architectural Overview)
- **Hub:** 192.168.1.186 (ZimaOS / DeanOS)
- **ZekÃ¢ KatmanÄ± (Intelligence):** `brain/shared/` (TÃ¼m modeller iÃ§in ortak kural ve hafÄ±za havuzu)
- **MCP Gateway:** Port 8900 Ã¼zerinden tÃ¼m araÃ§lara eriÅŸim.

## ðŸ“ GÃ¼ncel Dosya HaritasÄ± (Project Map)

### 1. ðŸ“‚ `projects/` (Aktif GeliÅŸtirme AlanlarÄ±)
BaÄŸÄ±msÄ±z projeler ve servisler burada toplanmÄ±ÅŸtÄ±r.
- `projects/agentops-nexus/` -> Ana orkestratÃ¶r, dashboard ve messenger kÃ¶prÃ¼sÃ¼.
- `projects/ai-config-sync/` -> KonfigÃ¼rasyon senkronizasyon araÃ§larÄ±.
- `projects/nexus-brain/` -> Ã‡ekirdek zekÃ¢ modÃ¼lleri.
- `projects/ops-automation-system/` -> Operasyonel otomasyonlar.

### 2. ðŸ“‚ `scripts/` (Operasyonel AraÃ§lar)
Kritik Python scriptleri ve yardÄ±mcÄ± modÃ¼ller.
- `scripts/nexus_monitor.py` -> Sistem saÄŸlÄ±ÄŸÄ± ve port izleme.
- `scripts/deploy_enhanced_brain.py` -> Yeni zekÃ¢ katmanÄ±nÄ± daÄŸÄ±tÄ±m aracÄ±.
- `scripts/sync_to_mcp.py` -> Yerel deÄŸiÅŸiklikleri MCP sunucusuna aktarÄ±r.
- `scripts/core/` -> PaylaÅŸÄ±lan Ã§ekirdek mantÄ±k (RPG tabanlÄ± ajan yÃ¶netimi vb.).

### 3. ðŸ“‚ `data/` (Durum ve Veri KatmanÄ±)
Sistemin hafÄ±zasÄ±, state dosyalarÄ± ve kalÄ±cÄ± verileri.
- `data/*.json` -> `agent_state.json`, `multi_agent_state.json` vb. aktif durum dosyalarÄ±.
- `data/bridge.sql` -> VeritabanÄ± ÅŸemasÄ± ve baÅŸlangÄ±Ã§ verileri.
- `data/history/handoffs/` -> GeÃ§miÅŸ el sÄ±kÄ±ÅŸma (handoff) kayÄ±tlarÄ±.

### 4. ðŸ“‚ `skills/` (Beceriler KÃ¼tÃ¼phanesi)
YÃ¼zlerce uzmanlÄ±k alanÄ± (Frontend, Security, Odoo vb.) ve `.skill` dosyalarÄ±.
- `skills/nexus-git-ops.skill` -> Git operasyon standartlarÄ±.
- `skills/nexus-skill-system.skill` -> Sistem beceri tanÄ±mlarÄ±.

### 5. ðŸ“‚ `deploy/` (DaÄŸÄ±tÄ±m YapÄ±landÄ±rmalarÄ±)
- `deploy/prod-docker-compose.yml` -> Ãœretim ortamÄ± Docker yapÄ±landÄ±rmasÄ±.

## ðŸ› ï¸ Kritik Operasyonel Yollar
- **Ana Kural Seti:** `GEMINI.md` (KÃ¶k Dizin - Kesinlikle taÅŸÄ±nmamalÄ±dÄ±r).
- **ZekÃ¢ PaylaÅŸÄ±m Yolu:** `/DATA/AppData/nexus-brain/brain/shared/` (ZimaOS Ã¼zerinde).
- **Dashboard URL:** [it.evaitec.com/brain-dashboard](https://it.evaitec.com/brain-dashboard)

## ðŸ“ Sonraki AdÄ±mlar ve Direktifler
1. **Context Tazeleme:** Her 10-15 turn'de bir bu manifesti ve `GEMINI.md`'yi tekrar oku.
2. **Yol GÃ¼ncelleme:** Yeni bir script eklenirse `scripts/` altÄ±na, yeni bir state dosyasÄ± eklenirse `data/` altÄ±na alÄ±nmalÄ±dÄ±r.
3. **Commit KuralÄ±:** Sadece kullanÄ±cÄ± isterse commit yap, mesajlarda "Nexus Intelligence" standartlarÄ±nÄ± takip et.

---
**Last Updated:** 2026-04-05 
**Status:** NEURAL MAP UPDATED - READY FOR NEXT AGENT

