# CasaOS'tan ZimaOS'a Göç Planı (casatozima)

Bu plan, mevcut çalışan Flask ve Docker yapısını "temiz ve şişmemiş" (lean) bir şekilde yeni bir bilgisayardaki ZimaOS kurulumuna taşımak için hazırlanmıştır.

## Taşınacak Temel Parçalar

Yeni `casatozima` klasörüne sadece sistemin çalışması için gereken kritik dosyalar alınacaktır:
- `Dockerfile` ve `docker-compose.yml` (Altyapı)
- `requirements.txt` (Bağımlılıklar)
- `src/` klasörü (Tüm uygulama kodu, CSS ve HTML şablonları)

## Uygulama Adımları

### 🏗️ Yeni Yapının Kurulması
1. **[NEW]** `c:\projects\github\casatozima` dizini oluşturulacak.
2. Mevcut projedeki temiz içerikler bu klasöre kopyalanacak.
3. **[NEW]** `.gitignore` dosyası eklenerek gereksiz dosyalar (logs, pycache vb.) temiz tutulacak.

### 🐙 Git ve GitHub Hazırlığı
1. Yeni klasörde `git init` komutu çalıştırılacak.
2. Tüm dosyalar ilk commit olarak eklenecek.
3. **[NEW]** `README.md` dosyasına ZimaOS'ta projeyi tek komutla nasıl ayağa kaldıracağına dair (örneğin: `docker compose up -d`) basit bir rehber yazılacak.

## 💿 ZimaOS Kurulum Fazı

Yeni bilgisayara temiz bir ZimaOS kurulumu yapmak için şu adımları izleyeceğiz:

1. **İndirme:** ZimaOS x86_64 "Installer" imajı indirilecek. (Güncel sürüm: 1.2.4 veya 1.3.3)
2. **Yazma:** Rufus ile USB'ye yazılacak.
3. **BIOS:** Hedef bilgisayarda "Secure Boot" kapatılacak ve "UEFI" modunda USB'den başlatılacak.

## Kullanıcı Onayı Gerekenler
- GitHub'a `casatozima` deposunu yüklemek için bir 'Personal Access Token' veya giriş yapmanız gerekebilir, yerel hazırlıklar tamam.
- ISO dosyasını indirdiğinizde Rufus ayarlarında yardımcı olabilirim.
