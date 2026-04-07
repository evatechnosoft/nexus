# Ollama ve Open WebUI Bağlantısı (ZimaOS)

Ollama (host üzerinde) ve Open WebUI (Docker konteyneri içinde) çalışmaktadır. Docker konteynerinin host üzerindeki Ollama API'sine erişebilmesi için ağ yapılandırması gereklidir.

## Kullanıcı İncelemesi Gerekli

- **Ollama API Erişimi**: Ollama'nın `0.0.0.0` (tüm arayüzler) üzerinden dinlemesi sağlanacaktır. Bu, yerel ağdaki diğer cihazların da Ollama API'sine erişebilmesi anlamına gelir.
- **Docker Konteyner Yenileme**: `open-webui` konteyneri yeni ayarlarla (`host.docker.internal` ve `OLLAMA_BASE_URL`) yeniden oluşturulacaktır. `/var/lib/open-webui` içindeki verileriniz korunacaktır.

## Önerilen Değişiklikler

### [Sistem Yapılandırması]

#### [YENİ] [fix_ollama_webui.sh](file:///d:/OS/Zimaos/fix_ollama_webui.sh)
ZimaOS sunucusunda çalıştırılacak, Ollama servis ayarlarını ve Open WebUI konteynerini güncelleyen script.

#### [GÜNCELLE] [setup.sh](file:///d:/OS/Zimaos/setup.sh)
Gelecekteki kurulumların otomatik olarak bağlı gelmesi için Open WebUI kurulum komutunun güncellenmesi.

## Açık Sorular

- Ollama için GPU (NVIDIA) hızlandırma aktif edilsin mi? (NVIDIA GPU varsa önerilir).
- WebUI üzerinde varsayılan bir model (örn: llama3) otomatik çekilsin mi?

## Doğrulama Planı

### Otomatik Testler
- Docker konteyneri içinden host gateway erişimi kontrolü.
- Ollama API yanıtının doğrulanması.

### Manuel Doğrulama
- Open WebUI arayüzüne girilip modellerin listelenip listelenmediğinin kontrolü.
