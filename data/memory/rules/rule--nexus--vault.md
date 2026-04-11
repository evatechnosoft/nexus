---
id: rule--nexus--vault
type: security
context: global
extends: rule--nexus--master
description: Hassas veri (Secrets) yönetim ve erişim protokolü.
---
# NEXUS VAULT PROTOCOL (POINTER SYSTEM)

## 🔐 GİZLİLİK KURALLARI
1. Hiçbir dosyada (code, .env, md) şifre, token veya API Key AÇIK YAZILMAZ.
2. Hassas veriler `/DATA/AppData/vault/secrets.json` içinde HashiCorp/Vault mantığıyla saklanır.
3. Erişim her zaman `vault://[service]/[key]` formatında pointer ile yapılır.

## 🗝️ SABİT POINTERLAR
- **Gmail App Pass:** `vault://google/app_password`
- **Gemini API Key:** `vault://google/gemini_key`
- **Admin Email:** `vault://google/admin_email`
- **SSH Private Key:** `vault://zimaos/ssh_key`

**NOT:** Bir AI modeli bu pointer'ı gördüğünde, Nexus API üzerinden gerçek veriyi çalışma anında talep etmelidir.
