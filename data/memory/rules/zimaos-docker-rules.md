# ZimaOS Docker Rules

> Guncelleme: 2026-04-07

## 1. Temel Kisitlar

| Kural | Aciklama |
|---|---|
| Root salt-okunur | Kalici veri = /DATA/AppData/ |
| DOCKER_CONFIG | /DATA/AppData/.docker (yazilabilir) |
| docker compose | Subcommand calisir; docker-compose v1 YOK |
| ZimaOS docker | -f flag bazi versiyonlarda sorun cikarabilir |
| BusyBox sed | Multiline sed calismaz, Python kullan |

## 2. Compose Kurallari

### Yasak (Swarm) anahtarlari - ZimaOS importer fail eder
- deploy: (replicas, mode, resources)
- networks: overlay

### .env dosyasi uyarisi
ZimaOS Web UI .env okumaz. Env var'lari inline YAML'a yaz.

## 3. Dizin Yapisi

/DATA/AppData/
  .docker/              <- DOCKER_CONFIG
  compose/<appName>/    <- Git yonetimli compose dosyalari
  <appName>/            <- Uygulama verisi

## 4. docker run Sablonu

docker run -d \
  --name myapp \
  --restart always \
  --network host \
  -e TZ=Europe/Istanbul \
  -v /etc/localtime:/etc/localtime:ro \
  -v /DATA/AppData/myapp:/app/data \
  myimage:latest

## 5. Zaman Dilimi ve Konum (KRİTİK)

- **Kural:** Tüm konteynerler `-e TZ=Europe/Istanbul` içermelidir.
- **Kural:** Ana makinenin yerel saati bağlanmalıdır: `-v /etc/localtime:/etc/localtime:ro`.
- **Neden:** Logların, alertlerin (Telegram vb.) ve hafıza zaman damgalarının yerel saat (UTC+3) ile uyumlu olması için.

## 6. Restart vs Rebuild

- Sadece kod degisti: docker restart <name>
- Requirements degisti: docker stop + rm + build + run

## 6. CI/CD Notu

cd-test.yml ve cd-prod.yml docker restart kullanir.
Image rebuild gereken degisiklikler icin ZimaOS SSH ile manuel islem.

## 7. Anti-Pattern

- cat <<EOF ile YAML olusturma (heredoc bozar)
- sed multiline ekleme (BusyBox calismaz)
- Root altina veri yazma (read-only)
- .env dosyasina guvenme (UI gormez)
- Swarm anahtarlari (importer fail)