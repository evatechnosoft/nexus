# [Home Assistant] Bluetooth ve HACS Altyapısı Hazır

Home Assistant (HA) konteyneriniz, Xiaomi Bluetooth sensörleri görebilecek ve özel topluluk eklentilerini (HACS) çalıştırabilecek şekilde yapılandırıldı.

## Yapılan İşlemler

1.  **Bluetooth Passthrough**: `docker-compose.yml` dosyasına `/run/dbus` bağlaması eklendi. Bu sayede HA, ZimaOS'un Bluetooth donanımına tam erişim kazandı.
2.  **HACS Kurulumu**: Home Assistant Community Store (HACS) otomatik script ile kuruldu ve `custom_components` dizinine yerleştirildi.
3.  **Konteyner Yeniden Yapılandırma**: Ayarların aktif olması için HA konteyneri yeniden oluşturuldu ve başlatıldı.

---

## ⚡ Senin Yapman Gereken Son Adımlar (HA Arayüzünde)

HACS ve Bluetooth'un aktif olması için HA içinde şu adımları izle:

### 1. HACS'ı Aktifleştir
- HA arayüzünde **Ayarlar > Cihazlar ve Hizmetler > Entegrasyon Ekle** kısmına git.
- **HACS** araması yap ve seç.
- Ekrana gelen kutucukları onaylayıp karşına çıkan GitHub kodunu ilgili linkte doğrula.

### 2. Xiaomi Sensörleri Ekle
- HACS yüklendikten sonra sol menüden HACS'a gir.
- "Integrations" kısmından **Xiaomi Miot Auto** veya **Xiaomi BLE** eklentisini kur.
- Mi Temp V2 cihazların otomatik olarak keşfedilecektir. (Eğer Bind Key isterse, "Xiaomi Cloud" üzerinden login olarak bunu otomatik çekebilirsin).

### 3. Eksik "Add-on" Sorunu (MQTT vb.)
Giriş kısmında belirttiğin "Add-on yok" sorununu şu şekilde profesyonelce çözebiliriz:
- Bir Add-on'a (örneğin Mosquitto MQTT veya Zigbee2MQTT) ihtiyacın olduğunda, bunu Portainer veya CasaOS üzerinden **ayrı bir uygulama** olarak kuracağız.
- Ardından Home Assistant içinden "MQTT Integration" ekleyip bu konteynerin IP'sini (192.168.1.186) girmen yeterli olacak.

---

## Sonuç
Altyapı artık hazır. Sensörlerini eklerken veya yeni bir "Add-on" (konteyner) kurmak istediğinde söylemen yeterli, hemen kurabiliriz!
