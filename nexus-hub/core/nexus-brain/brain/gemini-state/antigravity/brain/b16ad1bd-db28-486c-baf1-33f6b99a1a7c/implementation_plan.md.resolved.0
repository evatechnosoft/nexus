# Flutter Proje Düzeltme ve Çalıştırma Planı

Kullanıcının "düzelt çalıştır" talebi doğrultusunda, `flutter analyze` ile tespit edilen 33 hatayı gidermek ve projeyi çalışır hale getirmek için aşağıdaki adımlar uygulanacaktır.

## User Review Required

> [!IMPORTANT]
> Proje içerisindeki tüm ekran sınıfları (achievementsScreen, adminScreen vb.) küçük harfle başladığı için Flutter standartlarına uygun hale getirilerek (AchievementsScreen, AdminScreen) güncellenecektir. Bu, kullanıldıkları her yerde değişiklik gerektirir.

## Proposed Changes

### Core Configuration

#### [MODIFY] [routes.dart](file:///c:/projects/kizimin_arkadasi/kizimin_arkadasi/lib/config/routes.dart)
- Yanlış olan göreceli (relative) import yolları `package:kizimin_arkadasi/...` şeklinde güncellenecek.
- `OnboardingScreen`, `HomeScreen`, `ChatScreen`, `ProfileScreen` sınıflarının doğru import edildiğinden emin olunacak.

#### [MODIFY] [theme.dart](file:///c:/projects/kizimin_arkadasi/kizimin_arkadasi/lib/config/theme.dart)
- `CardTheme` parametresi `CardThemeData` olarak değiştirilecek.
- `withOpacity` yerine `withValues(alpha: ...)` kullanımı (yeni Flutter sürümü uyumu için) güncellenebilir veya mevcut haliyle bırakılabilir (analiz uyarısı ise).

### Screens & Models

#### [MODIFY] Tüm Screen Dosyaları
- `achievementsScreen` -> `AchievementsScreen`
- `adminScreen` -> `AdminScreen`
- `authScreen` -> `AuthScreen`
- ... (diğer tüm ekranlar)

#### [MODIFY] [app_provider.dart](file:///c:/projects/kizimin_arkadasi/kizimin_arkadasi/lib/providers/app_provider.dart)
- Kullanılmayan importlar temizlenecek.

### Tests

#### [MODIFY] [widget_test.dart](file:///c:/projects/kizimin_arkadasi/kizimin_arkadasi/test/widget_test.dart)
- `MyApp` sınıfı bulunamadığı için `main.dart` import edilecek ve gerekirse `MyApp` sınıf ismi kontrol edilecek.

## Open Questions

- Projeyi hangi hedefte (Windows, Web, Android vb.) çalıştırmamı istersiniz? Mevcut ortam Windows 11 olduğu için "Windows" desktop olarak çalıştırmak en kolayı olacaktır.

## Verification Plan

### Automated Tests
- `flutter analyze` komutu tekrar çalıştırılacak ve 0 hata elde edilene kadar düzeltmelere devam edilecek.
- `flutter build windows` veya `flutter run -d windows` ile uygulamanın ayağa kalktığı doğrulanacak.

### Manual Verification
- Uygulamanın splash ekranından onboarding ekranına geçişi kontrol edilecek.
