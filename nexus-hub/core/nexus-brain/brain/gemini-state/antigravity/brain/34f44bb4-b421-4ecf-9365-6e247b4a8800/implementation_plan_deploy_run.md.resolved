# "Sorunları Gider ve Çalıştır" — Deployment ve Parser Fix Planı

Bu plan, yereldeki görsel iyileştirmelerin sunucuya aktarılmasını ve e-posta ayrıştırıcısının (parser) hatalı eşleşmelerinin düzeltilmesini kapsar.

## Kullanıcı İncelemesi Gerektiren Konular

> [!IMPORTANT]
> Sunucuya dosya aktarımı sırasında uygulama kısa bir süre (1-2 dakika) çevrimdışı kalacaktır. Docker container'ları yeni kodla yeniden inşa edilecektir.

## Önerilen Değişiklikler

### 1. Parser & Watcher İyileştirmesi (Functional Fix)

#### [MODIFY] [email_parser.py](file:///c:/projects/it-inventory/it-inventory/inventory_app/email_parser.py)
- **Çoklu Satır Desteği:** `parse_email` artık sadece ilk kişiyi değil, tablodaki TÜM satırları bir liste olarak dönecek.
- **Departman Eşleşmesi:** Tablo başlıklarındaki "Departman", "Birim", "Bölüm" sütunları yakalanıp veriye eklenecek.
- **Header Kayması Çözümü:** `re.split` yerine (`|`, `\t`, `;`) gibi belirgin ayırıcılar ve ardından esnek boşluk temizliği kullanılacak.

#### [MODIFY] [email_watcher.py](file:///c:/projects/it-inventory/it-inventory/inventory_app/email_watcher.py)
- **Toplu İşlem:** `_process_message` fonksiyonu, parser'dan gelen listenin her bir elemanı için ayrı bir `Request` oluşturacak.
- **Departman Önceliği:** Parser'dan gelen departman bilgisi varsa o kullanılacak, yoksa metin üzerinden tahmin yürütülecek.

### 2. Sunucu Senkronizasyonu (Deployment)

#### Operasyonel Adımlar:
- **Dosya Transferi:** Yereldeki `inventory_app` klasörü `scp` ile DeanOS `/DATA/AppData/it-inventory` dizinine senkronize edilecektir.
- **Docker Yeniden Başlatma:** 
  ```bash
  cd /DATA/AppData/it-inventory && sudo docker-compose up -d --build
  ```

### 3. Çalıştırma ve Takip (Runtime)

- `docker logs it-inventory` komutuyla Graph API (O365) bağlantısı ve e-posta izleyici (watcher) hataları denetlenecektir.
- `it.evaitec.com` üzerinden yeni tasarımın yansıdığı teyit edilecektir.

## Açık Sorular

> [!CAUTION]
> E-postalardan gelen verilerde "Ad Soyad" yerine sadece "Çalışan İsmi" mi yazıyor? "Header" kayması tam olarak hangi sütunlarda yaşanıyor? (Gerekirse örnek bir e-posta metni parser testi için yararlı olur).

## Doğrulama Planı

### Otomatik Testler
- `test_parsing.py` yeni formata göre güncellenip çalıştırılacaktır.
- Docker container'ın `Up (healthy)` durumunda olduğu sunucuda görülecektir.
