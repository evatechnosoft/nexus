# knowledge/it-inventory-deployment-fixes.md

Tarih: 2026-03-28
Proje: IT Inventory (FastAPI / Docker / DeanOS)

## 1. Sunucu ve Infrastructure (ZimaOS / DeanOS)

### Docker Dağıtım Hataları
- **Hata:** `mkdir /root/.docker: read-only file system`
- **Neden:** ZimaOS (CasaOS) ortamında kök dizini genellikle salt okunur (read-only) mount edilmiştir veya `/root` dizini üzerinde yazma yetkisi kısıtlıdır.
- **Çözüm:** `docker compose` komutu çalıştırılırken `DOCKER_CONFIG` değişkenini yazılabilir bir dizine (örn. `/tmp/.docker`) yönlendiriniz.
  - *Örnek:* `sudo DOCKER_CONFIG=/tmp/.docker docker compose up -d --build`

### Port Çakışmaları
- **Hata:** `Bind for 0.0.0.0:8000 failed: port is already allocated`
- **Neden:** Port 8000, CasaOS ortamlarında genellikle **Portainer**'ın (API veya Edge Agent) varsayılan portudur.
- **Çözüm:** Uygulamanın dış portunu (Host Port) **8001** veya **3000** gibi boş bir port ile değiştiriniz. Dahili (Container) port 8000 olarak kalabilir.
  - *Örnek:* `8001:8000`

### Dosya Yolları (Volumes)
- ZimaOS'ta kullanıcı dosyaları genellikle `/DATA/dean/projects/` veya `/DATA/AppData/` altında bulunur. Docker volumes eşleşmelerinde bu yolların doğruluğunu `docker inspect` ile teyit ediniz.

## 2. E-posta Ayrıştırma (Email Parser & Watcher)

### Çoklu Kişi ve Tablo Formatları
- **Header Kayması:** Yatay tablo (Header: Ad, Soyad... | Veri: Ahmet, Yılmaz...) formatlarında regex ile `re.split` yaparken birden fazla boşluk (`\s{2,}`) veya belirgin karakterleri (`|`, `;`, `\t`) dikkate alınız.
- **Toplu İşlem:** `parse_email` fonksiyonu her zaman bir **liste** (`List[dict]`) dönmelidir. `email_watcher.py` bu listeyi döngüye alarak her kişi için ayrı bir `Request` (talep) objesi oluşturmalıdır.
- **Departman Extraction:** Tablo başlıklarında (Headers) "Departman", "Bölüm", "Birim" kelimelerini aratıp, veriyi DB'deki `Department` tablosuyla `ilike` üzerinden eşleştiriniz. Eşleşme yoksa metin bazlı tahminleme (`_detect_department`) fallback olarak kullanılmalıdır.

## 3. UI/UX Tasarım Standartları
- **Dark Mode:** Bootstrap 5.3 native dark mode (`data-bs-theme="dark"`) kullanılmalı.
- **Glassmorphism:** CSS'de `.bg-glass` veya benzeri bir utility class ile `backdrop-filter: blur(10px)` ve `background: rgba(r,g,b, 0.7)` uygulanmalıdır.
- **Mobil Etkileşim:** Talepler listesinde telefondan kolay erişim için "swipe" hissi veren butonlar ve tam satır tıklama özelliği (`onclick`) eklenmelidir.
