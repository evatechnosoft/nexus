# Anthropic (Claude) Ajan Geliştirme Kuralları

Bu belge, Claude'un resmi mühendislik prensiplerine dayanarak ajan (agent) tabanlı sistemler geliştirirken uyulması gereken temel kuralları tanımlar.

## 1. Basitlik ve İş Akışları (Simplicity & Workflows)
- **Tercih Sırası:** Her görev için karmaşık otonom ajanlar oluşturmaktan kaçının. Öncelik sırası: Basit Prompt -> Prompt Chaining (Zincirleme) -> Otonom Ajan şeklindedir.
- **Öngörülebilirlik:** İşlemler çoğunlukla `Workflows` (İş Akışları) olarak tasarlanmalıdır. Ajanlar, sadece sürecin model tarafından dinamik olarak yönlendirilmesi gereken durumlarda (esneklik gerektiğinde) kullanılmalıdır.

## 2. Araç Mühendisliği (Tool Engineering)
Ajanların başarısı büyük ölçüde araçların (tools) kalitesine bağlıdır.
- **ACI (Agent-Computer Interface):** Araçları tıpkı bir insana doküman hazırlıyormuş gibi net, eksiksiz ve spesifik olarak tanımlayın.
- **Hata Yönetimi (Error Handling):** Bir araç başarısız olduğunda sadece `false` veya `error` dönmeyin. Modelin hatayı anlayıp düzeltebilmesi için eğitici ve detaylı hata mesajları döndürün.
- **Token Optimizasyonu:** Araç yanıtları kısa olmalıdır. Çok fazla veri dönen araçlar (örn: büyük bir dosya okuma veya geniş veritabanı sorgusu) varsayılan olarak sayfalama (pagination) veya filtreleme yeteneklerine sahip olmalıdır.

## 3. Mimari Desenler (Architectural Patterns)
- **Prompt Chaining:** Bir görevi sıralı adımlara bölün; her adım bir öncekinin çıktısını kullanır.
- **Parallelization:** Birbiriyle bağımsız alt görevleri aynı anda çalıştırarak performansı artırın.
- **Orchestrator-Workers:** Bir ana modelin (Orchestrator) hedefi planladığı ve spesifik görevleri alt uzman modellere (Workers) dağıttığı modüler yapıyı tercih edin.
- **Evaluator-Optimizer:** Kod veya plan oluştururken, bir modelin ürettiği çıktıyı diğer bir modelin (veya fonksiyonun) test edip değerlendirdiği geri bildirim döngülerini kurun.
