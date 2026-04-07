# Dinamik Tema Rengi (Primary Color) Entegrasyonu

Bu plan, kullanıcının uygulama ana rengini (Primary Color) 5 farklı seçenek arasından değiştirebilmesini ve bu seçimin kalıcı olmasını sağlar.

## User Review Required

> [!IMPORTANT]
> **AppState Yapılandırması:** Renk seçimi `AppState` üzerinden yönetilecek ve `FlutterSecureStorage` ile kaydedilecektir.
> **Tema Uyumluluğu:** `AppTheme.primary` sabit değişkeni, dinamik bir yapıya dönüştürülecektir. Tüm UI bileşenlerinin bu yeni yapıya uyumlu olduğundan emin olunacaktır.

## Proposed Changes

### [Mobile App Base]

#### [MODIFY] [main.dart](file:///c:/projects/SportApp/mobile_app/lib/main.dart)
- `AppState` sınıfına `primaryColorValue` (default: `0xFF00E5A0`) eklenecek.
- `setPrimaryColor(int value)` metodu ile renk güncellenecek ve `FlutterSecureStorage`'a kaydedilecek.
- `_loadSettings` içinde kaydedilen renk değeri yüklenecek.

#### [MODIFY] [theme.dart](file:///c:/projects/SportApp/mobile_app/lib/theme.dart)
- `static const Color primary` ifadesi yerine, `AppState`'den gelen rengi kullanan dinamik bir yapı kurulacak.
- `getTheme` fonksiyonu artık `primaryColor` parametresi alacak.
- Diğer statik metotlar (getDecoration vb.) için `primary` rengi doğrudan `Theme.of(context).primaryColor` üzerinden okunacak şekilde düzenlenebilir veya statik bir helper eklenebilir.

#### [MODIFY] [settings_screen.dart](file:///c:/projects/SportApp/mobile_app/lib/screens/settings_screen.dart)
- "GÖRÜNÜM & TEMA" bölümüne "ANA RENK SEÇİMİ 🌈" başlığı altında bir renk paleti eklenecek.
- Kullanılabilecek 5 ana renk:
  1. **Mint Green (Varsayılan):** `0xFF00E5A0`
  2. **Sky Blue:** `0xFF00C4FF`
  3. **Sunset Red:** `0xFFFF6B6B`
  4. **Royal Purple:** `0xFFA78BFA`
  5. **Amber Gold:** `0xFFFBBF24`
- Seçilen rengi gösteren onay işareti (Check icon) içeren dairesel butonlar kullanılacak.

## Open Questions

- Renk seçenekleri için özel bir "Renk Çubuğu" (Slider) mı istersiniz, yoksa sunduğumuz 5 premium renk paleti yeterli mi? (Şu an 5 adet kaliteli renk seçeneği planlandı).

## Verification Plan

### Automated Tests
- `flutter test` (mevcutsa) çalıştırılacak.
- Manuel olarak `AppConfig` üzerinden port doğrulaması ile backend bağlantısı kontrol edilecek.

### Manual Verification
1. Ayarlar ekranına gidip farklı renkler seçilecek.
2. Butonların, Dashboard ikonlarının ve alt navigasyon çubuğunun renginin değiştiği doğrulanacak.
3. Uygulama kapatılıp açıldığında seçilen rengin korunduğu kontrol edilecek.
