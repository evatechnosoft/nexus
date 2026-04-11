---
id: rule--nexus--manifest
type: manifest
context: global
extends: rule--nexus--vault
description: Proje sabitleri ve servis haritası (Pointer Mapping).
---
# NEXUS MANIFEST MAP (CONSTANTS)

## 🌐 GLOBAL SERVİS SABİTLERİ
- **Admin Email:** `manifest://global/admin_email` -> (Vault: `vault://google/email`)
- **Nexus Hub URL:** `http://192.168.1.186:8900`
- **Ollama API:** `http://192.168.1.186:4602`

## 📑 KULLANIM REHBERİ
Bir projede "Mail gönder" dendiğinde; 
- `FROM_ADDR` olarak `manifest://global/admin_email` kullanılır.
- `PASSWORD` olarak `rule--nexus--vault` üzerinden ilgili pointer çağrılır.
- Kodda asla gerçek mail adresi veya şifre GEÇMEZ.
