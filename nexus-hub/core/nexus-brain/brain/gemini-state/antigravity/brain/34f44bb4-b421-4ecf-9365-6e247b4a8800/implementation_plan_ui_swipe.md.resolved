# UI Modernizasyonu ve Mobil Deneyim İyileştirme Planı

Kullanıcı geri bildirimlerine dayanarak, karanlık temanın eksik kalan kısımlarını düzeltecek, masaüstü ve mobil kullanım kolaylığını artıracak geliştirmeler yapılacaktır.

## Kullanıcı İncelemesi Gerektiren Konular

> [!IMPORTANT]
> Mobil cihazlarda "Sağa Kaydır -> Sil" özelliğinin çalışması için bir silme endpoint'i eklenecektir. Silme işlemi geri alınamaz (veya onay kutusu ile yapılabilir).

## Önerilen Değişiklikler

### 1. Görsel Düzeltmeler (Dark Theme)

Ekran görüntülerinde görülen beyaz blokların ve düşük kontrastlı metinlerin kalıcı olarak düzeltilmesi.

#### [DEĞİŞTİR] [style.css](file:///c:/projects/it-inventory/it-inventory/inventory_app/static/style.css)
- `th`, `td`, `.card` ve `.table` elementleri için `background: transparent !important` ve `color: var(--text-main) !important` zorlaması.
- Input ve Badge sınıflarındaki Bootstrap varsayılan açık renklerinin override edilmesi.

### 2. Kullanılabilirlik (Tıklanabilir Satırlar)

Kullanıcının sadece küçük oklara tıklamak yerine tüm satıra basarak detaya girebilmesi.

#### [DEĞİŞTİR] [requests.html](file:///c:/projects/it-inventory/it-inventory/inventory_app/templates/requests.html)
- `<tr>` etiketlerine `cursor: pointer` stili ve `onclick="window.location.href='/requests/{{ req.id }}/detail'"` özelliği eklenecektir.

### 3. Mobil Deneyim (Swipe Actions)

Dokunmatik cihazlarda hızlı işlem yapabilmek için kaydırma hareketleri eklenecektir.

#### [YENİ] [swipe_actions.js] (Veya template içine script)
- **Sola Kaydır:** Talebin detay sayfasına git (`/requests/id/detail`).
- **Sağa Kaydır:** Talebi silme/iptal etme aksiyonunu tetikle.

### 4. Backend (Silme Yeteneği)

#### [DEĞİŞTİR] [requests.py](file:///c:/projects/it-inventory/it-inventory/inventory_app/routers/requests.py)
- `@router.post("/delete/{req_id}")` veya `@router.get("/delete/{req_id}")` endpoint'i eklenerek talebin silinmesi sağlanacaktır.

## Doğrulama Planı

### Otomatik Testler
- Tarayıcı alt aracı ile mobil görünümde (`device scale factor` / `viewport` simülasyonu ile) "clickable rows" özelliğinin çalıştığı test edilecektir.
- Renklerin ekran görüntüsü alınarak "beyaz blok" kalmadığı teyit edilecektir.

### Manuel Doğrulama
- Kullanıcıdan mobil cihazında sağ/sol kaydırma yaparak işlemleri test etmesi istenecektir.
