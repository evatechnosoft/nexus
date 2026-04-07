# TEST ve PROD İzole Host Etme Planı

Şu anki durumda DeanOS üzerinde `/DATA/AppData/it-inventory` klasörü her iki ortam tarafından da ortak kullanılmaktadır. Bu durum `docker compose` projelerinin ve özellikle `.env` dosyalarının birbirini ezmesine neden olmaktadır. Bu plan ile ortamları fiziksel olarak ayıracağız.

## Kullanıcı İncelemesi Gerekli

> [!IMPORTANT]
> - **Klasör Ayrıştırma**: Sunucudaki `/DATA/AppData/it-inventory` klasörü yerine `/DATA/AppData/it-inventory-test` ve `/DATA/AppData/it-inventory-prod` klasörlerini kullanacağız. Bu, stabilite için en kesin çözümdür.
> - **Yerel Docker**: Docker Desktop'ınızın kapalı olduğunu tekrar hatırlatmak isterim. Yerel DEV ortamı için lütfen Docker'ı başlatın.

## Önerilen Değişiklikler

### 1. Dağıtım Scripti (Local PowerShell)

#### [MODIFY] [deploy.ps1](file:///c:/projects/it-inventory/deploy.ps1)
- `sshTargetDir` değişkenini `$envName`'e göre dinamik hale getireceğiz.
- TEST -> `/DATA/AppData/it-inventory-test`
- PROD -> `/DATA/AppData/it-inventory-prod`

### 2. Sunucu Scripti (Deploy Deanos)

#### [MODIFY] [deploy_deanos.sh](file:///c:/projects/it-inventory/deploy_deanos.sh)
- Proje isimlerini (-p) kullanmaya devam edeceğiz, ancak artık her biri kendi izole klasöründe çalışacağı için `.env` çakışması yaşanmayacak.

## Doğrulama Planı

### Otomatik Testler
1. `ssh deanos "sudo docker ps"` -> Aynı anda hem `it-inventory-test` hem de `it-inventory-prod` konteynırlarının ayakta olduğu görülecek.
2. 9600 ve 9700 portlarının doğru Badge'leri (Kırmızı/Yeşil) gösterdiği kontrol edilecek.

### Manuel Doğrulama
- 9600: http://192.168.1.186:9600
- 9700: http://192.168.1.186:9700
adresleri test edilecek.
