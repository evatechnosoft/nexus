# 🛰️ Satellite Specialist: Nexus Sales (NSP-01)

> **🎯 Core Master**: [nexus](https://github.com/evatechnosoft/nexus) `nexus-brain sadece nexus olacak şekilde düzenlendi`

## 📡 Uydu Bilgileri
- **Modül İsmi**: `nexus-sales`
- **Konum**: `projects/nexus-sales/` (Satellite-Spoke)
- **Port (Server)**: `8901`
- **Metrikler (Grafana)**: `4500`

## ⚖️ Yetki ve Sorumluluk
Bu uydu, `nexus` ana sistemine aşağıdaki uzmanlıkları sağlar:
- [x] **Analyze Site**: Web tarama ve rakip analizi (Scraping logic).
- [x] **Lead Collection**: Satış fırsatlarını toplama ve metrik tetikleme.
- [x] **Prometheus Integration**: Canlı satış istatistiklerini raporlama.

## 🔗 Senkronizasyon (Sync)
Ana Hub (Nexus ) güncellendiğinde, bu uydu modülü de otomatik olarak `/DATA/AppData/nexus/data/` üzerinden beslenir.
