---
id: rule--nexus--pointers
type: rule
context: global
version: 1.0
tags: root, core, pointers
---
# ⚠️ NEXUS ROOT POINTERS (MANDATORY HOOKS) ⚠️

Bu dosya sistemdeki EN KRİTİK dosyadır. Tüm AI operatörleri (Claude, Gemini, Cursor vb.) işleme başlamadan önce bu **düğümleri (pointers)** takip etmeli ve ilgili kuralları **on-demand (ihtiyaç anında)** okumalıdır. Hafızanı (context) temiz tutmak için tüm kuralları ezberleme, sadece aşağıdakileri uygula!

## 1. BAŞLANGIÇ HOOK'U (Pre-Use)
Yeni bir oturum açıldığında, kullanıcının nerede kaldığını anlamak için hemen şu dosyayı oku:
👉 **`data/memory/sync/resume-state.md`** (Okuduktan sonra hafızandan temizle, sadece yönlendirmeyi takip et).

## 2. DALLANMA VE KODLAMA HOOK'U (Pre-Commit / Pre-Code)
- **ASLA `dev` veya `prod` branch'lerinde doğrudan kod yazma!**
- Kod yazmadan önce her zaman `git status` ile nerede olduğuna bak.
- Branch kurallarının tamamı için şu pointer'ı oku:
👉 **`data/memory/rules/rule--nexus--branching.md`**

## 3. YETENEK VE SKILL HOOK'U (Pre-Task)
Sıfırdan script veya workflow (Örn: deploy, auth, dashboard) yazmadan önce "Bunun için bir skill var mı?" diye kontrol et.
👉 **`nexus_discover`** aracını kullan veya **`data/memory/skills/`** dizinine bak.

## 4. YÖNETİM VE KISAYOL HOOK'U (The "G" System)
Kullanıcı `g`, `gc`, `gn`, `gd`, `gall` yazdığında ne yapman gerektiğini bilmiyorsan:
👉 **`data/memory/rules/rule--nexus--master.md`** dosyasını oku.

## 5. DİKKAT DAĞILMASI VE SIKIŞTIRMA HOOK'U (Stop / Limit)
AI olarak hafızan (Context Window) sınırlıdır.
- Her **5-6 uzun/karmaşık işlemden sonra (Turn Limit)** KESİNLİKLE dur.
- Kullanıcıya şu uyarıyı yap: *"Hafıza/Context şişiyor, token tasarrufu için lütfen `gc` veya `n-compress` çalıştırın."*
- Unutma: Sen "compress" yapamazsın, bu komutları kullanıcı PowerShell'den veya senin tetiklediğin bir script ile (`python scripts/nexus-compress.py`) çalıştırmalıdır.

## 6. GÜVENLİK HOOK'U (Vault)
Şifre, API key veya token gördüğünde ASLA koda gömme.
👉 Detaylar için: **`data/memory/rules/rule--nexus--vault.md`**

---
**ÖZET:** Bu dosya senin navigasyon haritandır. Hata yapmamak için önce Pointer'ı bul, sonra o kural dosyasını okuyarak işlem yap.
