---
id: rule--nexus--cleanup
type: cleanup
context: global
extends: rule--nexus--master
description: Deployment öncesi gereksiz dosya temizliği ve secret süzme protokolü.
---
# NEXUS CLEANUP PROTOCOL (PRE-DEPLOY)

## 🧹 TEMİZLENECEK DOSYALAR
1. **Python Cache:** `**/__pycache__/`, `**/*.pyc`
2. **Test Cache:** `.pytest_cache/`, `.ruff_cache/`
3. **Local Env:** `.venv/`, `.env.local`
4. **Logs:** `logs/*.log`, `tmp/*.tmp`

## 🔐 SECRET SCAN (ZORUNLU)
- Kodda asla `PASS`, `KEY`, `TOKEN` gibi değerler **açık yazılmaz**.
- Bulunan tüm sızıntılar `rule--nexus--vault` pointer'ına çevrilmelidir.
- Deployment öncesi `grep` ile secret taraması yapılması zorunludur.

## 📦 SERVER-ONLY (FILTER)
- Sadece `core/`, `scripts/`, `satellites/` ve `data/memory/` dizinleri ZimaOS'a gönderilir.
- Lokal `tests/` dizini üretim ortamına (production) taşınmaz.
