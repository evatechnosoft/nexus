---
extends:
  - rule--nexus--docker
  - rule--nexus--pip
  - rule--nexus--npm
user: dean
privilege: sudo
base_path: /DATA/AppData/nexus-hub
---
# NEXUS MASTER PROTOCOL (ZIMAOS)
Bu kural, ZimaOS (192.168.1.186) üzerindeki tüm operasyonlar için ana rehberdir. 
Tüm alt kurallar (Docker, Pip, NPM) bu protokole tabidir.
ROOT (/) dizinine yazma. Sadece /DATA/AppData kullan.

# NEXUS G-SYSTEM (MASTER MENU)
Bu sistem, Nexus Hub'ın ana yönetim arayüzüdür. Her AI operatör bu kısayolları bilmeli ve kullanmalıdır.

- **G** : Master Menu'yü tetikler.
- **[n] Context Status**: Token ve Turn takibi. (`scripts/nexus-stats.py`)
- **[c] Master Compress**: Oturumu mühürle ve sıkıştır. (`scripts/nexus-compress.py`)
- **[a] Sync Rules**: Kuralları senkronize et. (`scripts/nexus-sync.py build`)
- **[d] System Doctor**: Sistem sağlık kontrolü. (`scripts/nexus-doctor.py`)
- **[b] Light Dream**: Dream raporu oluştur ve Hub'a gönder. (`scripts/nexus-dream.py --light`)
- **[all] G-ALL**: `git add .`, `git commit`, `git push` işlemlerini tek seferde yapar.

**NOT:** AI operatörler doğrudan bu fonksiyonları simüle etmeli veya scriptleri çalıştırmalıdır.