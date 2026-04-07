# Home Assistant Xiaomi Home Entegrasyonu Yükleme Planı

Bu plan, [Xiaomi Home](https://github.com/XiaoMi/ha_xiaomi_home) resmi entegrasyonunu DeanOS (ZimaOS) üzerindeki Home Assistant konteynerine yüklemek için gerekli adımları içerir.

## Kullanıcı İncelemesi Gerektiren Konular

> [!IMPORTANT]
> Yükleme işlemi tamamlandıktan sonra Home Assistant konteyneri **yeniden başlatılacaktır**. Bu işlem sırasında HA kısa süreliğine erişilemez olacaktır.

## Uygulanacak Adımlar

### 1. Hazırlık ve Klonlama
DeanOS üzerinde geçici bir dizin oluşturulacak ve Xiaomi Home repo'su klonlanacaktır.

#### [KOMUTLAR]
```bash
# Geçici dizine git
cd /tmp
# Var olan klonları temizle
sudo rm -rf ha_xiaomi_home
# Repo'yu klonla
git clone https://github.com/XiaoMi/ha_xiaomi_home.git
```

### 2. Yükleme Scriptinin Çalıştırılması
Klonlanan dizin içerisindeki `install.sh` scripti, HA konfigürasyon dizinini hedef alarak çalıştırılacaktır.

#### [KOMUTLAR]
```bash
cd /tmp/ha_xiaomi_home
sudo chmod +x install.sh
# DeanOS üzerindeki HA config yolu: /DATA/AppData/homeassistant/config
sudo ./install.sh /DATA/AppData/homeassistant/config
```

### 3. Doğrulama ve Yeniden Başlatma
Entegrasyonun `custom_components` altına doğru şekilde yerleştiği kontrol edilecek ve HA konteyneri yeniden başlatılacaktır.

#### [KOMUTLAR]
```bash
# Dosya kontrolü
ls -ld /DATA/AppData/homeassistant/config/custom_components/xiaomi_home
# Home Assistant Yeniden Başlatma
echo 'Eralp123!' | sudo -S docker restart homeassistant
```

## Doğrulama Planı

### Kontrol Listesi
- `/DATA/AppData/homeassistant/config/custom_components/xiaomi_home` dizininin varlığı.
- HA loglarında (`docker logs homeassistant`) hata olup olmadığı.
- HA arayüzünde "Xiaomi Home" entegrasyonunun listelenip listelenmediğinin (kullanıcı tarafından) teyidi.
