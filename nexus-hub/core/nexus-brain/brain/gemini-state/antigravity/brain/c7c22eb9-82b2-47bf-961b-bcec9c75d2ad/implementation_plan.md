# Kritik Hata Düzeltmeleri ve Altyapı İyileştirmeleri

Git repomu başlattım ve `fix/startup-issues` dalında çalışmalara başladım. Mevcut planı, tespit ettiğim diğer hataları da kapsayacak şekilde güncelliyorum.

## Progreş Raporu (Yapılanlar)

1. [x] `.gitignore` oluşturuldu.
2. [x] Git reposu başlatıldı ve ilk commit yapıldı.
3. [x] `fix/startup-issues` dalına geçildi.
4. [x] `.env` dosyası oluşturuldu.
5. [x] `schema.sql` içindeki index hatası düzeltildi.
6. [x] `schema.sql` dosyasına eksik olan `meal_logs` tablosu eklendi.
7. [x] `routes/sync.js` içindeki sözdizimi ve mantık hataları giderildi.
8. [x] `routes/photos.js` içindeki sözdizimi hataları giderildi.

## Proposed Changes (Yapılacaklar)

### Kimlik Doğrulama Katmanı

#### [MODIFY] [auth.js](file:///c:/projects/SportApp/routes/auth.js)
> [!IMPORTANT]
> `auth.js` dosyası şu an tamamen bozuk durumda ve yanlış kod blokları içeriyor. Bu dosyayı aşağıdaki fonksiyonları sağlayacak şekilde yeniden yazacağım:
> - **Google Login**: ID Token doğrulaması ve kullanıcı kaydı.
> - **Email/Password**: Kayıt ve Giriş işlemleri.
> - **Profil**: Kullanıcı bilgilerini getirme (`/me`).

### Sistem Genelindeki Eksikler

- **Middleware Kontrolü**: Tüm rotaların `verify.js` dosyasını doğru şekilde çağırdığından emin olacağım.
- **Sözdizimi Doğrulama**: Tüm dosyaların `node --check` ile geçerliliğini kontrol edeceğim.

## Open Questions

1. Google Login için kullanılacak `GOOGLE_CLIENT_ID` değeri `.env` dosyasında mevcut, ancak backend tarafında Google ID Token doğrulaması yapılacak mı yoksa sadece Client ID yeterli mi? (Hazırladığım kod ID Token doğrulamasını içerecek).

## Verification Plan

### Automated Tests
- `node --check server.js`
- `npm run start` (Yerel veritabanı bağlantısı yoksa bile uygulamanın çökmeden ayağa kalkması hedefleniyor).

### Manual Verification
- Uygulama başladığında console çıktılarını kontrol edeceğim.
