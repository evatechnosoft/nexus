# OpenAI Ajan Geliştirme Kuralları

Bu belge, OpenAI'nin resmi ajan rehberine dayalı olarak sistem tasarımında uyulması gereken kuralları tanımlar.

## 1. Tasarım ve Model Seçimi
- **Doğru Model:** Prototip ve tasarım aşamasında her zaman en yetenekli model (örn. GPT-4o) ile başlayın. Temel performans belirlendikten sonra maliyet ve hız optimizasyonu için daha küçük modellere geçiş test edilmelidir.
- **Modülerlik:** Sistem çok fazla karmaşık mantık veya araç (tool) içeriyorsa, bunları tek bir modele yüklemek yerine çoklu uzman aracılara (Multi-agent orchestration) bölün.

## 2. Talimatlar ve Operasyon (Instructions)
- **Açık ve Net Adımlar:** Modelin yapacağı işleri belirsizlikten uzak, numaralandırılmış küçük adımlara bölün. Mevcut SOP (Standart Operasyon Prosedürü) belgelerini doğrudan talimata dönüştürün.
- **Uç Durumlar (Edge Cases):** Eksik veri veya beklenmedik girdiler için net dallanma (if-then-else) mantıkları tanımlayın. 

## 3. Araç Kullanımı (Tools)
- **Veri ve Eylem Ayrımı:** Araçları ikiye ayırın:
  1. **Data Tools:** Sisteme dışarıdan salt okunur (read-only) veri getiren araçlar (örn. `read_sensor_data`, `fetch_weather`).
  2. **Action Tools:** Sistem durumunu değiştiren eylem araçları (örn. `update_database`, `turn_on_device`).
- **Açıklama:** Araçların ve parametrelerin açıklamalarını, modelin doğru bağlamı kurabilmesi için detaylı yazın.

## 4. Güvenlik ve İnsan Denetimi (Guardrails & Human-in-the-loop)
- **Manager Pattern (Yönetici Deseni):** Merkezi bir yönetici ajan (Orchestrator), diğer alt ajanları yönetmelidir.
- **Korkuluklar:**
  - *Relevance Classifier:* Konu dışı veya anlamsız istekleri ilk aşamada tespit edip engelleyin.
  - *Safety Classifier:* Güvenlik açıklarını ve prompt injection girişimlerini önleyin.
- **Human-in-the-loop:** Kritik ve geri döndürülemez işlemlerde (örn. bir cihazı kalıcı olarak kapatmak, büyük veri silmek) ajanın kararı mutlaka insan (kullanıcı) onayına sunulmalıdır.
