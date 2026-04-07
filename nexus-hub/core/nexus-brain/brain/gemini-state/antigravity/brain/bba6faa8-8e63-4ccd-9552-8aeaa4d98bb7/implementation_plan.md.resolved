# ESPHome ve Dashboard Restorasyon Planı

Kullanıcının "kurulu" verileri saptandı. Şimdi bu verileri konteynere bağlayıp Dashboard linklerini (Port 8123, 6052, 3000 vb.) pürüzsüz hale getireceğiz.

## Kullanıcı Bilgilendirmesi (KRİTİK)
- **Verileriniz Hazır:** `/var/lib/casaos_data/AppData/esphome/` altındaki `.yaml` dosyalarınızın yerinde olduğu doğrulandı. 📂
- **Port ve Link Tamiri:** Dashboard simgelerinin sizi "Settings" yerine doğrudan uygulamaya (Port 6052, 8123 vb.) atması sağlanacak.

## Proposed Changes

### 1. ESPHome Restorasyonu (Müdahale)
- Mevcut `esphome` konteyneri durdurulup silinecek.
- Konteyner **-v /var/lib/casaos_data/AppData/esphome:/config** parametresiyle ("kurulu" verilerinizle) yeniden başlatılacak.

### 2. Dashboard Link Tamiri (SQLite Güncelleme)
- `/var/lib/casaos/db/management.db` veri tabanı üzerinden `apps` tablosundaki simge linkleri saniyeler içinde şu portlara güncellenecek:
  - **Home Assistant:** Port `8123`, Index `/`
  - **ESPHome:** Port `6052`, Index `/`
  - **AdGuard Home:** Port `3000`, Index `/`
  - **Grafana:** Port `3001`, Index `/`

## Verification Plan

### Automated Tests
- `docker inspect esphome` ile mount yolu doğrulanacak.
- Browser subagent ile Dashboard linklerinin (8123, 6052) çalıştığı teyit edilecek.

### Manual Verification
- Kullanıcıdan Dashboard simgelerine tıklayarak doğrulaması istenecek.
