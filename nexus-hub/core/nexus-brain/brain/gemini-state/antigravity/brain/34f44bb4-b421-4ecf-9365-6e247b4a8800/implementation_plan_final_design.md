# Premium Final Tasarım Sistemi ve "Mismatch" Giderilmesi Planı

Kullanıcı geri bildirimlerine ve ekran görüntülerine dayanarak, uygulamada görülen renk uyumsuzlukları (açık/koyu karışıklığı, siyah bloklar, düşük kontrast) kökten temizlenecektir.

## Kullanıcı İncelemesi Gerektiren Konular

> [!IMPORTANT]
> Uygulama artık Bootstrap 5.3'ün yerel karanlık modunu (`data-bs-theme="dark"`) kullanacaktır. Bu, tarayıcı ve sistem tercihlerine tam uyum sağlar.

## Önerilen Değişiklikler

### 1. Global Tema Kilidi (Foundation)

#### [DEĞİŞTİR] [base.html](file:///c:/projects/it-inventory/it-inventory/inventory_app/templates/base.html)
- `<html>` etiketine `data-bs-theme="dark"` eklenecektir.
- Navbar ve Body arka planı tamamen senkronize edilecektir.

### 2. Tasarım Sistemi Yenilenmesi (Design System)

#### [DEĞİŞTİR] [style.css](file:///c:/projects/it-inventory/it-inventory/inventory_app/static/style.css)
- **Renk Paleti:** Slate 900 (Arka Plan), Slate 800 (Kartlar), Indigo (Aksan) şeklinde sabitleme.
- **Glassmorphism:** Kartlar ve Modal'lar için daha yumuşak, gerçekçi blur efektleri.
- **Table Reset:** "Black block" sorunu yaratan manuel tablo stilleri kaldırılarak mdern, temiz bir tablo tasarımı uygulanacaktır.

### 3. Template Temizliği (Clean Code)

#### [DEĞİŞTİR] Tüm HTML Dosyaları
- Manuel eklenen `bg-dark`, `bg-white`, `text-white` gibi sınıflar kaldırılacak.
- Bunun yerine merkezi CSS üzerinden yönetilen `.card`, `.badge` ve `.table` sınıfları kullanılacaktır.
- `request_detail.html` içerisindeki siyah etiket blokları ("Ad Soyad" sütunu gibi) düzeltilecektir.

## Doğrulama Planı

### Otomatik Testler
- Tarayıcı alt aracı ile her sayfa (Dashboard, Requests, Inventory) için renk uyumu ve "mismatch" kontrolü yapılacaktır.
- Metinlerin okunabilirliği (contrast ratio) denetlenecektir.

### Manuel Doğrulama
- Kullanıcıya yeni ekran görüntüleri sunularak "temiz ve uyumlu" bir tasarımın oluştuğu teyit edilecektir.
