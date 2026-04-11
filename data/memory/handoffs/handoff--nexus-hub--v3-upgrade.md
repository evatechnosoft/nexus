---
id: handoff--nexus-hub--v3-upgrade
type: handoff
context: nexus-hub
extends: rule--nexus--master
tags: upgrade, hierarchy, tr-tz, indexer
---
# NEXUS HUB UPGRADE HANDOFF (v3.0)

## 🎯 KAZANIMLAR (GAINS)
- **Hiyerarşi:** `data/memory/` altında `rules`, `handoffs`, `projects`, `sync` ve `vault` bölümlendirmesi yapıldı.
- **Indexer v3.0:** Artık tüm `.md` dosyalarını Frontmatter (Metadata) ile süzebiliyor.
- **Timezone:** Tüm sistem TR (UTC+3) zaman dilimine sabitlendi.
- **Security:** Vault Pointer sistemi (`vault://`) devreye alındı.

## 📦 AKTARILACAKLAR (TO-DO)
- **Auto-Dream:** Her 4 saatte bir (08, 12, 16, 20) çalışması sağlandı.
- **Context Alert:** Context %80 doluluğa ulaştığında kullanıcıyı uyaracak.
- **Clean-up:** Eski raporlar 7 günde bir otomatik temizlenecek.
