# 🏗️ ZimaOS Docker Altyapı Şartnamesi ve Kullanım Rehberi

Bu doküman, sistemin karmaşıklığını önlemek, araç çakışmalarını engellemek ve sürdürülebilir bir Docker yapısı oluşturmak için hazırlanmıştır.

---

## 1. Araç Rolleri ve Kullanım Senaryoları

Hangi aracın hangi durumda kullanılacağına dair temel kurallar:

| Araç | Kullanım Alanı (Senaryo) | Neden Bu Araç? |
| :--- | :--- | :--- |
| **Coolify** | Özel Yazılım Geliştirme, CI/CD, Git Projeleri | GitHub entegrasyonu, otomatik build ve karmaşık ortam değişkenleri yönetimi için en iyisidir. |
| **Portainer** | Altyapı Denetimi, Volume & Network Yönetimi | Docker'ın en derin noktalarına hakim olmak, yetim (orphan) paketleri temizlemek ve ağ yapılarını düzenlemek için idealdir. |
| **Dockhand** | CasaOS App Store & Stack Yönetimi | BigBear ekosistemi uygulamalarını ve çoklu konteyner (stack) yapılarını CasaOS ile uyumlu yönetmek için kullanılır. |
| **CasaOS (UI)** | Hazır Ev Sunucusu Uygulamaları | Nextcloud, Home Assistant gibi "tek tıkla kur" servisleri için en hızlı ve görsel çözümdür. |

---

## 2. Altyapı Standartları (Şartname)

Sistemi "bozmadan" yönetmek için aşağıdaki standartlara uyulmalıdır:

### 📡 Port Standartları
Çakışmaları önlemek için port aralıkları kategorize edilmiştir:
- **Altyapı & Yönetim (3000 - 3999)**: Dozzle (8080 - istisna), Uptime Kuma (3002), Dockhand (3003).
- **Geliştirme & Test (8000 - 8999)**: Test veritabanları, geçici API'lar, `it-inventory-test`.
- **Üretim / Canlı (9000 - 9999)**: `quiz-bank-backend` (9308), `it-inventory-prod` (9700).
- **Sistem Servisleri (10000 - 10999)**: Nextcloud (10081), Cloudflare (10081).

### 📂 Dosya ve Dizin Yapısı
- **Persistence (Kalıcı Veri)**: Tüm Docker volume'ları `/DATA/AppData/<Uygulama_Adı>` altında toplanmalıdır.
- **Projeler**: Aktif kod geliştirme dizini `/DATA/projects/` olmalıdır.

### 🔐 Güvenlik ve Erişim
- **SSH Access**: Sadece `dean` kullanıcısı ve yetkili anahtar (`deanos`) ile erişim sağlanmalı, `root` login kapalı tutulmalıdır.
- **Docker Socket**: `/var/run/docker.sock` sadece Portainer ve Dockhand gibi güvenilir yönetim araçlarına bağlanmalıdır.

---

## 3. "Bozmadan Kontrol" Rehberi

Sistemde değişiklik yapmadan önce şu adımları izleyin:

1.  **Duplicate Kontrolü**: Yeni bir konteyner kurmadan önce Portainer'dan o portun veya ismin kullanımda olup olmadığını kontrol edin.
2.  **Coolify Önceliği**: Eğer uygulama bir kod projesiyse (Node.js, Go, Python), Portainer yerine **Coolify** üzerinden kurun.
3.  **ZimaOS Güncellemeleri**: Sistem güncellemesi yapmadan önce mutlaka `/DATA/Backup` dizinine bir `.tar.gz` yedeği (aldığımız gibi) oluşturun.

---

## 4. Pratik Bağlantı Listesi (Hızlı Erişim)

- **Sistem Dashboard**: [192.168.1.186](http://192.168.1.186)
- **Coolify Paneli**: [192.168.1.186:8000](http://192.168.1.186:8000) (Veya yapılandırılan port)
- **Portainer**: [192.168.1.186:9443](https://192.168.1.186:9443)
- **Dockhand**: [192.168.1.186:3003](http://192.168.1.186:3003)

---

> [!NOTE]
> Bu rehber, sistem yöneticisinin (Sizin) ve asistanın (Benim) ortak dilidir. Yeni bir yapı kurarken bu şartnameye sadık kalacağız.
