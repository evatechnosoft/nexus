# KERNEL Prompt Mühendisliği ve Yazım Standartları

Bu belge, 2025-2026 döneminde %89 başarı oranına ulaşan KERNEL framework'ünü temel alır.

## 1. KERNEL Disiplini
- **K (Keep it simple):** Her prompt'un tek bir ana hedefi olmalıdır. Karmaşık hedefler alt promptlara bölünmelidir.
- **E (Easy to verify):** Çıktının doğruluğunu ölçecek net kriterler (örn. "JSON formatında dön", "En az 3 kanıt ekle") tanımlanmalıdır.
- **R (Reproducible):** Promptlar versiyonlanmalı ve aynı girdiyle benzer çıktıyı üretecek kesinlikte olmalıdır.
- **N (Narrow scope):** Bağlam penceresini kirletmemek için sadece ilgili dosyalar ve bilgiler işleme alınmalıdır.
- **E (Explicit constraints):** Negatif kısıtlamalar ("Ne yapmaması gerektiği") açıkça belirtilmelidir.
- **L (Logical structure):** Yazım hiyerarşisi şu sırayla olmalıdır: `[Bağlam] -> [Görev] -> [Kısıtlamalar] -> [Örnek Çıktı Formatı]`.

## 2. Akıl Yürütme (Reasoning) Desenleri
- **ReAct (Reasoning + Acting):** Model önce bir adım düşünmeli (Düşünce: ...), ardından eyleme geçmelidir.
- **Self-Reflection:** Kritik çıktılarda modelin kendi sonucunu eleştirmesi ("3 zayıf noktanı bul ve düzelt") istenmelidir.
- **Confidence Scoring:** Model her yanıt için bir güven skoru (%...) vermeli ve düşük skorlu yerlerde kanıt sunmalıdır.

## 3. Token Optimizasyonu
- **Sistem Talimatı:** "Gereksiz nezaket cümlelerinden kaçın, doğrudan teknik yanıta odaklan."
- **Önbellek Dostu Yazım:** Değişmeyen talimatlar promptun başında tutularak "Prompt Caching" verimliliği artırılmalıdır.
