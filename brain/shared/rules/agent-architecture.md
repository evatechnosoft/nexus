# Zeka ve Ajan Mimarisi (IoT ve Yazılım Odaklı)

Bu belge, "Brain" mimarisinin, Anthropic ve OpenAI kurallarıyla nasıl harmanlandığını ve IoT / Yazılım Mimarisi projelerinde nasıl işletileceğini tanımlar.

## 1. Veri Eklemleme ve Token Verimliliği
- **Modüler Yapı:** Tüm kurallar `.md` dosyaları olarak ayrıştırılmalı ve hiyerarşik tutulmalıdır. (@path: `brain/shared/rules/`)
- **MCP Standartları:** Araç ve kaynak entegrasyonunda **MCP (Model Context Protocol)** zorunludur. Bkz: `mcp-standard.md`
- **Bağlam Sıkıştırma (Context Compression):** Bağlam penceresi %80 doluluğa ulaştığında, sistem otomatik olarak özetleme yapmalı ve pencereyi boşaltmalıdır.

## 2. Doğrulama ve Koordinasyon
- **A2A Koordinasyonu:** Çoklu ajan iş birliğinde **A2A Protokolü** (BID/COMMIT) uygulanır. Bkz: `a2a-coordination.md`
- **KERNEL Framework:** Tüm promptlar ve ajan talimatları **KERNEL** disiplinine göre yazılmalıdır. Bkz: `prompt-engineering.md`
- **Durum Kaydı (Check-pointing):** Ajan her kritik adımın sonucunu bir `state.json` dosyasına yazmalıdır.

## 3. Domain Odaklı Ajan Rolleri
Sistemdeki ajanlar şu rollere göre spesifik sınırlandırmalarla çalışmalıdır:

- **IoT Mühendisi (Worker):**
  - Sensör verilerini okumada `Data Tools`, yapılandırma değiştirmede `Action Tools` kullanır.
  - Kritik cihaz değişiklikleri öncesi her zaman insan onayı (Human-in-the-loop) ister.

- **Yazılım Mimarı (Worker):**
  - Modüller tasarlarken SOLID prensiplerini ve Unix-style tooling mantığını uygular.
  - Kodlama aşamasında "Keşfet -> Planla -> Uygula -> Doğrula" döngüsünü takip eder.

- **Veri Analisti (Analyst / Reviewer):**
  - Sistemin "Deep Search" operasyonlarını gerçekleştirir.
  - Verileri analiz eder ve token verimliliği için sadece "Relevant Context" sunar.

## 4. İletişim Protokolü
Ajanlar kendi aralarında ve kullanıcı ile iletişim kurarken kısa, öz ve doğrudan bir dil kullanır. Başarısızlık durumunda sorunu net ifade edip alternatif çözüm yolu önerir.
