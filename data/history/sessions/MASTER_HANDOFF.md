# 🧠 Nexus Master Manifest & Handoff (2026-04-05)

Bu dosya, projenin "Universal Nexus Brain" mimarisine geçiş sonrası güncel dosya yapısını, kritik yolları ve operasyonel mantığı içeren ana rehberdir.

## 📡 Sistem Mimarisi (Architectural Overview)
- **Hub:** 192.168.1.186 (ZimaOS / DeanOS)
- **Zekâ Katmanlı (Intelligence):** `brain/shared/` (Tüm modeller için ortak kural ve hafıza havuzu)
- **MCP Gateway:** Port 8900 üzerinden tüm araçlara erişim.

## 📍 Güncel Dosya Haritası (Project Map)

### 1. 📂 `projects/` (Aktif Geliştirme Alanları)
Bağımsız projeler ve servisler burada toplanmıştır.
- `projects/agentops-nexus/` -> Ana orkestratör, dashboard ve messenger köprüsü.
- `projects/ai-config-sync/` -> Konfigürasyon senkronizasyon araçları.
- `projects/nexus-brain/` -> Çekirdek zekâ modülleri.
- `projects/ops-automation-system/` -> Operasyonel otomasyonlar.

### 2. 📂 `scripts/` (Operasyonel Araçlar)
Kritik Python scriptleri ve yardımcı modüller.
- `scripts/nexus_monitor.py` -> Sistem sağlığı ve port izleme.
- `scripts/deploy_enhanced_brain.py` -> Yeni zekâ katmanını dağıtım aracı.
- `scripts/sync_to_mcp.py` -> Yerel değişiklikleri MCP sunucusuna aktarır.
- `scripts/core/` -> Paylaşılan çekirdek mantık (RPG tabanlı ajan yönetimi vb.).

### 3. 📂 `data/` (Durum ve Veri Katmanı)
Sistemin hafızası, state dosyaları ve kalıcı verileri.
- `data/*.json` -> `agent_state.json`, `multi_agent_state.json` vb. aktif durum dosyaları.
- `data/bridge.sql` -> Veritabanı şeması ve başlangıç verileri.
- `data/history/handoffs/` -> Geçmiş el sıkışma (handoff) kayıtları.

### 4. 📂 `skills/` (Beceriler Kütüphanesi)
Yüzlerce uzmanlık alanı (Frontend, Security, Odoo vb.) ve `.skill` dosyaları.
- `skills/nexus-git-ops.skill` -> Git operasyon standartları.
- `skills/nexus-skill-system.skill` -> Sistem beceri tanımları.

### 5. 📂 `deploy/` (Dağıtım Yapılandırmaları)
- `deploy/prod-docker-compose.yml` -> Üretim ortamı Docker yapılandırması.

## 🛠️ Kritik Operasyonel Yollar
- **Ana Kural Seti:** `GEMINI.md` (Kök Dizin - Kesinlikle taşınmamalıdır).
- **Zekâ Paylaşım Yolu:** `/DATA/AppData/nexus-brain/brain/shared/` (ZimaOS üzerinde).
- **Dashboard URL:** [it.evaitec.com/brain-dashboard](https://it.evaitec.com/brain-dashboard)

## 📌 Sonraki Adımlar ve Direktifler
1. **Context Tazeleme:** Her 10-15 turn'de bir bu manifesti ve `GEMINI.md`'yi tekrar oku.
2. **Yol Güncelleme:** Yeni bir script eklenirse `scripts/` altına, yeni bir state dosyası eklenirse `data/` altına alınmalıdır.
3. **Commit Kuralı:** Sadece kullanıcı isterse commit yap, mesajlarda "Nexus Intelligence" standartlarını takip et.

---
**Last Updated:** 2026-04-05 
**Status:** NEURAL MAP UPDATED - READY FOR NEXT AGENT
