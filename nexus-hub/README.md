# Nexus Hub

## Aşama 1: Çatı Kurulumu (refactor/nexus-hub-init)

Bu dizin, parçalanmış olan Nexus ekosistemini (Merkezi Zeka ve Uydular) tek bir çatı altında toplamak amacıyla oluşturulmuştur.

### Dizin Yapısı
*   `core/`: Kullanıcının doğrudan muhatap olduğu "Yalın Genel Merkez" kodlarını içerir. (Eski `projects/nexus` içeriği buraya taşınmıştır).
    *   `server.js`: **6666** portunda çalışan merkezi Gateway.
*   `satellites/`: Belirli uzmanlıklara sahip SOLID mikro-mimari yapısındaki uyduların barındığı alandır (örneğin `fetcher` ve `sales` buraya taşınacaktır).

## Aşama 2: Universal Gateway (active)

Tüm servisleri tek bir noktadan yönetmek için Node.js tabanlı gateway kurulmuştur.

### Port Yapılandırması
*   **Nexus Hub:** `http://localhost:6666`
*   **Nexus Brain:** `http://localhost:6666/brain` (Proxy -> 8900)
*   **AgentOps:** `http://localhost:6666/ops` (Proxy -> 8000)
*   **Llama.cpp:** `http://localhost:6666/llm` (Proxy -> 6999)

### Çalıştırma
```bash
cd nexus-hub/core
npm start
```

## Test ve Doğrulama
*   Core içerisindeki dosyalar (`mcp_server.py`, `nexus-sync.py`, vb.) başarıyla taşınmış ve Python sentaks doğrulaması yapılmıştır.
*   `npm install` ile Node.js bağımlılıkları yüklenmiş, 6666 portu rezerve edilmiştir.
*   Merkezi çekirdeğin path bağımlılıklarında (eğer projenin köküne referans eden bağımlılıklar varsa) bir sorun yaratıp yaratmadığı sonraki canlı test adımlarında ayrıca valide edilecektir.