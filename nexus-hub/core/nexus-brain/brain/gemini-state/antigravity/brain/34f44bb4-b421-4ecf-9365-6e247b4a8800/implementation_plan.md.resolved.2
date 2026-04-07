# Okunurluk ve E-posta Ayrıştırma Sorunlarını Giderme

"Premium Next-Gen" karanlık teması ile HTML şablonlarındaki sabit Bootstrap sınıfları (bg-white, bg-light) arasındaki çakışmalar, okunurluk sorunlarına yol açmaktadır. Ayrıca, e-posta ayrıştırıcı gönderen adını çalışan adı ile karıştırmakta ve yatay tablo formatlarını tam desteklememektedir.

## Kullanıcı İncelemesi Gerektiren Konular

> [!IMPORTANT]
> Tasarımın tutarlı olması için `bg-light`, `bg-white` ve `text-dark` gibi standart Bootstrap sınıflarını kaldırıp temanın kendi "glassmorphism" (şeffaf karanlık) yapısına geçiyorum.

## Önerilen Değişiklikler

### UI & UX Standartlaştırma

Karanlık tema ile uyumlu ve okunabilir bir deneyim için şu değişiklikler yapılacaktır:

---

### [Bileşen] Şablon İyileştirmeleri

#### [DEĞİŞTİR] [request_detail.html](file:///c:/projects/it-inventory/it-inventory/inventory_app/templates/request_detail.html)
- Kart başlıklarından ve içerik kapsayıcılarından `bg-white` ve `bg-light` sınıflarını kaldır.
- `#configList` alanındaki `bg-light` yerine `var(--glass)` kullan.
- Tablo etiketlerini `text-muted` yerine daha yüksek kontrastlı bir renk ile güncelle.

#### [DEĞİŞTİR] [requests.html](file:///c:/projects/it-inventory/it-inventory/inventory_app/templates/requests.html)
- E-posta ayrıştırma aracındaki `bg-light` alanlarını kaldır.
- Tablo başlıklarını tema ile uyumlu hale getir.

#### [DEĞİŞTİR] [style.css](file:///c:/projects/it-inventory/it-inventory/inventory_app/static/style.css)
- `.bg-glass` ve `.text-glow` yardımcı sınıfları ekle.
- `text-muted` renginin kontrastını artır.

---

### [Bileşen] E-posta Ayrıştırıcı Optimizasyonu

#### [DEĞİŞTİR] [email_parser.py](file:///c:/projects/it-inventory/it-inventory/inventory_app/email_parser.py)
- **Gönderen/Çalışan Karışıklığını Gider**: "Gönderen", "From" ve "Kimden" etiketlerini çalışan adı aramalarından muaf tut.
- **Yatay/Satır Format Desteği**: Yatay başlıkları (örn: Ad Soyad | E-posta | Telefon) algılayacak ve altındaki veriyi eşleştirecek mantığı ekle.
- **Çoklu Satır Yönetimi**: Adres ve notlar gibi çok satırlı verilerin çekilmesini iyileştir.

#### [DEĞİŞTİR] [email_watcher.py](file:///c:/projects/it-inventory/it-inventory/inventory_app/email_watcher.py)
- `_strip_html` fonksiyonunun tablo yapısını koruyarak (`|` veya `:` gibi ayraçlarla) ayrıştırıcıya iletmesini sağla.

## Doğrulama Planı

### Otomatik Testler
- Tarayıcı alt aracını kullanarak `/requests/` ve `/requests/{id}/detail` sayfalarının ekran görüntülerini alıp okunurluğu doğrulayacağım.
- Belirttiğiniz yatay tablo formatına sahip örnek e-posta metinleriyle `test_parsing.py` scriptini çalıştırıp doğru verinin çekildiğini teyit edeceğim.

### Manuel Doğrulama
- Kullanıcıdan, kendi ekranında "Talep Detay" sayfasının okunabilirliğini kontrol etmesini isteyeceğim.
