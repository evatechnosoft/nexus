# Kapsamlı Görsel Hataların Giderilmesi ve Renk Uyumluluğu Planı

Kullanıcının ilettiği "renkler uyumsuz" ve "hataları gider" taleplerine istinaden, uygulamanın her köşesindeki manuel stil kalıntıları temizlenecektir.

## Kullanıcı İncelemesi Gerektiren Konular

> [!IMPORTANT]
> Tüm sayfalardaki (Envanter, Atamalar, Excel vb.) manuel arka plan renkleri kaldırılacaktır. Bu sayede uygulama tam bir bütünlük kazanacaktır.

## Önerilen Değişiklikler

### 1. Global Stil Arındırma (Universal Sanitization)

Aşağıdaki dosyalardan tüm `bg-white`, `bg-light`, `bg-dark`, `text-dark` ve `text-white` sınıfları temizlenecektir:
- `base.html`, `dashboard.html`, `requests.html`, `request_detail.html`
- `inventory.html`, `assignments.html`, `shipment.html`, `excel_import.html`, `departments.html`

### 2. Premium Tasarım Standartlaştırma

#### [DEĞİŞTİR] [style.css](file:///c:/projects/it-inventory/it-inventory/inventory_app/static/style.css)
- Navbar arka planı ve blur miktarı artırılarak daha premium bir hava verilecek.
- Tablo başlıkları (`thead`) ve hücreleri (`td`) için şeffaflık zorlanacaktır.
- Form elemanları (input, select) tamamen karanlık temaya göre modernize edilecektir.

### 3. Dashboard ve Liste Sayfaları

#### [DEĞİŞTİR] [dashboard.html](file:///c:/projects/it-inventory/it-inventory/inventory_app/templates/dashboard.html)
- Stat kartlarındaki simge renkleri ve metin kontrastları yeniden ayarlanacaktır.

## Doğrulama Planı

### Kontrol Listesi
- Tarayıcı üzerinden tüm sayfalarda (özellikle `request_detail` ve `inventory`) "beyaz blok" kalıp kalmadığı kontrol edilecektir.
- Navbar'ın her sayfada (dashboard, liste, detay) aynı koyulukta olduğu teyit edilecektir.
- Metinlerin her arka planda okunabilir olduğu (Contrast Check) doğrulanacaktır.
