# Dizin Sadeleştirme ve E-posta Hata Giderme Planı

## Kullanıcı İncelemesi Gerekli
> [!IMPORTANT]
> - `inventory_app` klasörünü bir üst dizine (root) taşıyarak yapıyı sadeleştireceğim. Bu, sunucudaki dosya yollarını ve Docker konfigürasyonunu etkileyecektir.
> - E-posta izleyicinin (watcher) neden kapalı olduğunu `main.py` ve `.env` üzerinden kontrol edip aktif edeceğim.

## Önerilen Değişiklikler

### 1. Dizin Sadeleştirme (Refactoring)
- **Hedef:** `.../My-Personal-Repository/inventory_app/` → `.../My-Personal-Repository/`
- **İşlem:** `inventory_app` içindeki tüm dosyaları kök dizine taşıyıp boş klasörü sileceğim.
- **Konfigürasyon:** `docker-compose.yml` dosyasındaki `build: .` ve volume yollarını bu yeni yapıya göre güncelleyeceğim.

### 2. E-posta İzleyici (Watcher) Fix
- **Kontrol:** `.env` dosyasındaki `EMAIL_PROVIDER=gmail`, `GMAIL_EMAIL` ve `GMAIL_APP_PASSWORD` değerlerinin doğruluğunu (veya eksikliğini) kontrol edeceğim.
- **Ayar:** İzleyicinin devreye girmesi için eksik bilgileri (kullanıcı sağlarsa) ekleyip `main.py` başlangıç mantığını teyit edeceğim.

### 3. Handoff Dokümantasyonu (handoff.md) [NEW]
- **İçerik:** 
  - Sistemi kontrol etme komutları (`docker logs`, `netstat`).
  - E-posta akışının nasıl test edileceği.
  - Port (8001) ve Cloudflare Tunnel ayarları.

## Açık Sorular
- **Soru:** E-posta izleyicinin çalışması için şu an `.env` dosyanızda Gmail adresi ve Uygulama Şifresi (App Password) tanımlı mı? (Eksikse sistem devre dışı kalır).
- **Soru:** Kök dizinde başka projeleriniz var mı? (Hepsini tek dizine toplamak diğer dosyalarla çakışma yaratır mı?)

## Doğrulama Planı
- `docker-compose up -d --build` ile yeni dizin yapısında sistemin çalıştığını doğrula.
- `docker logs` ile "İzleyici aktif" mesajını gör.
- `handoff.md` dosyasını oluşturup kullanıcıya sun.
