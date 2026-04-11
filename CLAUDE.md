# NEXUS HUB v3 FINAL COMPRESSION REPORT

## 💎 KAZANIMLAR (FINAL GAINS)
- **Global Hiyerarşi:** `data/memory/{rules,handoffs,projects,sync,vault}` yapısı tam kararlılıkla kuruldu.
- **Master Indexer (v3.0):** Metadata (Frontmatter) bazlı süzme ve hiyerarşik tarama aktif. (511+ entry).
- **Zaman Dilimi (TR):** Tüm sistem ve raporlama UTC+3 (Istanbul) saatine sabitlendi.
- **Güvenlik Katmanı:** `vault://` ve `manifest://` pointer sistemleri aktif. Hard-code şifre kullanımı yasaklandı.
- **Otomatik Denetim:** 4 saatlik Dream/Context-Alert (v3.1) mekanizması kuruldu.

## 📌 KRITIK POINTERLAR
- **Master:** `rule--nexus--master`
- **Security:** `rule--nexus--vault`
- **Constants:** `rule--nexus--manifest`
- **Strategy:** `rule--nexus--guides-strategy`

## 🔜 GELECEK AKSİYONLAR
- Context %80 dolduğunda `dream--light` raporu üzerinden süzme yapılması.
- Yeni eklenen tüm `.md` dosyalarının Frontmatter standardına uymasının denetlenmesi.

---

# NEXUS MASTER PROTOCOL (ZIMAOS)
Bu kural, ZimaOS üzerindeki tüm operasyonlar için ana rehberdir.

- User: dean
- Privilege: sudo
- Base Path: /DATA/AppData/nexus-hub
- Docker Config: /DATA/AppData/docker-config
- NPM Config: /DATA/AppData/npm-config
- PIP Config: /DATA/AppData/pip-config

---

# NEXUS WINDOWS PROTOCOL (LOCAL & REMOTE)

## 💻 KABUK (SHELL) STANDARTLARI
Windows ortamında her zaman **PowerShell** kullanılır.

1. **Operatörler:**
   - `&&` veya `||` ASLA KULLANILMAZ.
   - Ardışık komutlar için her zaman `;` (noktalı virgül) kullanılır.
2. **Yollar (Paths):**
   - Windows yerel yolları için her zaman `\` (ters slash) kullanılır.
   - Git/Docker komutları için Linux formatına (`/`) dikkat edilir.
3. **Heredoc:**
   - `cat <<EOF` (Linux) yerine her zaman `@"..."@` (PowerShell Heredoc) kullanılır.

## 🔐 SSH STANDARTLARI (REMOTE ACCESS)
ZimaOS (192.168.1.186) üzerindeki işlemler için her zaman SSH kullanılır.

1. **Sabit SSH Komutu:**
   - `ssh -i ~/.ssh/zimaos_key dean@192.168.1.186 "<komut>"`
2. **Remote Operatörler:**
   - SSH tırnak içindeki komutlarda Linux standartları (`&&`, `||`, `|`) geçerlidir.
3. **Dosya Transferi:**
   - `scp -i ~/.ssh/zimaos_key <kaynak> dean@192.168.1.186:<hedef>`

## 📊 KONTROL LİSTESİ (WINDOWS)
- [ ] Komutlar `;` ile ayrıldı mı?
- [ ] Path `D:\MainProjects\...` formatında mı?
- [ ] `&&` yerine `;` kullanıldı mı?
- [ ] SSH için `dean` kullanıldı mı?

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

---

# NEXUS BRANCHING PROTOCOL (STRICT)

Bu kural 11 Nisan 2026 itibariyle MÜHÜRLENMİŞTİR. Hiçbir AI veya insan operatör doğrudan `dev` veya `prod` branch'lerine commit atamaz.

## 🌿 DALLANMA STANDARTLARI
Tüm değişiklikler için yeni bir dal (branch) açılması ZORUNLUDUR:

1. **feature/**: Yeni özellikler, uydular (satellites) veya büyük hiyerarşi değişiklikleri.
   - *Örnek:* `feature/nexus-curator-v2`
2. **fix/**: Bilinen hataların, bozulan script'lerin düzeltilmesi.
   - *Örnek:* `fix/nexus-sync-script`
3. **bug/**: Beklenmedik davranışların, çakışmaların (conflicts) giderilmesi.
   - *Örnek:* `bug/index-path-conflict`

## 🔐 MERGE KURALLARI
- Hiçbir dal, `nexus-doctor` raporu %100 "HEALTHY" yanmadan `dev` ile birleştirilemez.
- `dev` branch'i her zaman "staging" (test) ortamıdır.
- `prod` branch'i sadece CD (Continuous Deployment) onayıyla güncellenir.

## 🖋️ COMMIT PROTOKOLÜ
- Commit mesajları `feat:`, `fix:`, `refactor:`, `docs:` gibi Conventional Commits standartlarına uygun olmalıdır.
- Değişiklik sonrası `nexus-sync build` ve `build_skill_index.py` çalıştırılmış olmalıdır.

**MÜHÜR TARİHİ:** 11 Nisan 2026, 16:25 (Istanbul UTC+3)
**DURUM:** AKTİF / ZORUNLU

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