# IT Inventory Ortam İzolasyonu ve İyileştirme Özeti

Bu çalışmada, uygulamanın TEST ve PROD ortamları DeanOS (ZimaOS) sunucusu üzerinde birbirini etkilemeyecek şekilde izole edilmiş, dağıtım süreçleri otomatize edilmiş ve kritik hatalar giderilmiştir.

## Yapılan Temel İyileştirmeler

### 1. Ortam İzolasyonu (Multi-Project Hosting)
*   **Ayrı Dizinler:** Sunucuda `/DATA/AppData/it-inventory-test` ve `/DATA/AppData/it-inventory-prod` klasörleri oluşturularak veritabanları ve dosyalar fiziksel olarak ayrıldı.
*   **Docker Namespace:** `docker compose -p it-inventory-$ENV` parametresi kullanılarak konteyner ve ağ isimleri çakışmayacak hale getirildi.
*   **Port Yönetimi:** 
    *   **TEST:** 9600
    *   **PROD:** 9700
    *   **LOCAL:** 9700 (Varsayılan)

### 2. E-posta Ayrıştırıcı (Email Parser) Hata Giderimi
*   **Sütun Kayması (Header Shifting):** Tablolardaki başlıkların indeks bazlı eşlenmesi sağlandı, böylece sütun sırası değişse bile veriler doğru kolonlarla eşleşiyor.
*   **Çoklu Birey Desteği:** Tablodaki tüm satırların toplu olarak işlenmesi sağlandı.
*   **Esnek Kelime Eşleme:** "e-mail", "posta", "mail" gibi farklı varyasyonlar artık doğru algılanıyor.

### 3. Kullanıcı Arayüzü (UI) ve Görsellik
*   **Glassmorphism Fix:** Modal altındaki butonların görünürlüğü artırıldı.
*   **Z-Index Ayarları:** "Yeni Cihaz Ekle" butonuna basıldığında açılan formun diğer öğelerin üzerinde kalması sağlandı.

### 4. Dağıtım Robotu (Deployment Scripts)
*   **Line Ending Normalizasyonu:** Windows'ta yazılan Bash scriptlerinin (`deploy_deanos.sh`) sunucuda çalışmama sorunu (carriage return) giderildi.
*   **Sudo Gereksinimi:** Docker komutları `sudo` ile çalıştırılacak şekilde güncellendi ve ZimaOS'un kısıtlı root erişimi aşıldı.

---

## Mevcut Durum Kontrol Listesi

| Ortam | URL / Port | Durum |
| :--- | :--- | :--- |
| **TEST** | [192.168.1.186:9600](http://192.168.1.186:9600) | ✅ AKTİF |
| **PROD** | [192.168.1.186:9700](http://192.168.1.186:9700) | ✅ AKTİF |
| **LOCAL DEV** | Port: 9700 | ✅ AKTİF |

> [!TIP]
> Yeni bir geliştirme yaptığınızda **test** branch'inden `.\deploy.ps1` çalıştırmanız yeterlidir. Onay verdiğinizde **main** branch'ine merge edip tekrar `.\deploy.ps1` çalıştırarak PROD ortamını güncelleyebilirsiniz.

> [!IMPORTANT]
> Eski, çakışmaya neden olan `it-inventory-app-1` konteyneri sunucudan güvenli bir şekilde kaldırıldı. Artık sadece ortam bazlı isimlendirmeler (`it-inventory-prod-app-1` vb.) kullanılmaktadır.
