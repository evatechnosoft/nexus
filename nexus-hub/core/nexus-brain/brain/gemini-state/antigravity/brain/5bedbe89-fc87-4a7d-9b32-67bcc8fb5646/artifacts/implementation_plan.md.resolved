# Arkadaşım AI (Kızımın Arkadaşı) - Tamamlama ve Onarım Planı

Bu plan, `code.sh` scriptinin hata vererek yarım bıraktığı "Kızımın Arkadaşı" projesini devralır, bozuk dosyaları düzeltir ve eksik olan tüm servisleri ve ekran taslaklarını tamamlar.

## Kullanıcı İncelemesi Gerekli

> [!IMPORTANT]
> `code.sh` içerisindeki modeller (UserProfile, LocationTask vb.) korunacak ancak içlerindeki sözdizimi hataları (typos) ve karakter bozulmaları temizlenecektir.

> [!TIP]
> Proje tam anlamıyla "tak-çalıştır" (plug-and-play) hale getirilecektir. OpenAI ve Gemini API anahtarları için bir config yapısı kurulacaktır.

## Önerilen Değişiklikler

### 1. Temel Yapı Onarımı
- **[MODIFY] `pubspec.yaml`**: `google_sign_in` ve `flutter_test` arasındaki birleşme hatası giderilecek.
- **[MODIFY] `lib/config/theme.dart`**: `BorderRadius` ve `dev_dependencies` içeren bozuk satırlar temizlenecek.
- **[MODIFY] `lib/app.dart`**: `AppProvider` entegrasyonu düzeltilecek.

### 2. Eksik Servislerin Yazılması
`code.sh` scriptinin hata verip oluşturamadığı kritik servisleri oluşturacağız:
- **[NEW] `lib/services/storage_service.dart`**: SharedPreferences tabanlı yerel veri saklama.
- **[NEW] `lib/services/api_service.dart`**: OpenAI, Gemini ve DeepSeek entegrasyonu.
- **[NEW] `lib/services/location_service.dart`**: GPS takibi.
- **[NEW] `lib/services/geofence_monitor.dart`**: Akıllı hatırlatıcı mantığı.
- **[NEW] `lib/providers/app_provider.dart`**: Uygulamanın ana durum (State) yönetimi.

### 3. Ekranların Tamamlanması
`setup.txt`'deki 32 ekranlık yapıyı şu şekilde dolduracağız:
- **Ana Ekranlar (Full UI)**: `SplashScreen`, `OnboardingScreen`, `HomeScreen`, `ChatScreen`.
- **Destekleyici Ekranlar (Template)**: `Profile`, `Settings`, `Notes`, `Quiz`, `Map`, `Diary`.
- **Erişim Noktaları (Routes)**: Tüm 32 ekranın birbiriyle bağlantısı `routes.dart` üzerinden sağlanacak.

## Doğrulama Planı

### Otomatik Kontroller
- `flutter analyze` ile kod hataları denetlenecek.
- `flutter pub get` ile bağımlılıkların uyumluluğu test edilecek.

### Manuel Doğrulama
- Chat ekranında AI karakterinin (kizimin_arkadasi) doğru "prompt" ile başlayıp başlamadığı kontrol edilecek.
- `GeofenceMonitor`'ün sahte (mock) konum verileriyle tetiklenmesi test edilecek.
