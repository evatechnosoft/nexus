# Nexus System Protocol (2026-04-06)

## Mimari: Micro-Satellite & SOLID
Nexus, merkezi bir beyin (Brain) ve ona bağlı uzman uydulardan (Satellites) oluşur.

### 1. Nexus Brain (Port 8900)
- **Kimlik:** Ana Karar Mekanizması.
- **Bellek:** ChromaDB (Universal Memory).
- **Kritik Araç:** `save_memory` -> Tüm uydular bu aracı kullanarak beyne bilgi aktarır.

### 2. Nexus Fetcher (Port 8902)
- **Kimlik:** Dış Dünya (Internet) Sensörü.
- **Yetkinlik:** Web Search (DDGS), URL Fetch, Reddit Analysis.
- **Kural:** Kazandığı bilgiyi `save_memory` protokolüyle beyne raporlar.

### 3. Nexus Sales (Port 8903)
- **Kimlik:** Ticari Zeka.

## Veri Senkronizasyonu
- **Server:** `/DATA/AppData/nexus-brain/`
- **Mirror:** `c:/projects/skills/data/`

## Kod Standartları
- **SOLID:** Her uydu kendi içinde modülerdir (Interfaces, Services, Utils).
- **Communication:** MCP (Stdio/SSE) üzerinden merkezi hub'a bağlıdır.
- **Language:** Kod yorumları İngilizce, iletişim her zaman TÜRKÇE.
