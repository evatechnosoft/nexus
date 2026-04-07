# A2A (Agent-to-Agent) Koordinasyon ve Müzakere Protokolü

Bu belge, heterojen ajanların birbiriyle iş birliği yapması için kullanılan A2A (2026) standartlarını tanımlar.

## 1. Aracı Kartları (Agent Cards)
- Her ajan, yeteneklerini ve kısıtlamalarını içeren bir **Agent Card** (JSON-LD) yayınlamalıdır.
- Ajanlar bir görevi delege etmeden önce bu kartlar üzerinden en uygun uzmanı seçer.

## 2. Müzakere Döngüsü (Negotiation Loop)
Ajanlar arası iş birliği şu üç adımla gerçekleşir:
1.  **BID (Teklif):** İstemci ajan, görevi ve token bütçesini açıklar.
2.  **ACCEPT (Kabul):** Uzman ajan, görevi belirtilen bütçe ve süre sınırları içinde yapabileceğini onaylar.
3.  **COMMIT (Taahhüt):** İşlem mühürlenir ve yürütme başlar.

## 3. Kimlik ve Güvenlik (DIDs)
- Ajanlar arası iletişimde **Merkeziyetsiz Kimlik Tanımlayıcılar (DIDs)** kullanılır.
- Uçtan uca şifreleme ve dijital imzalar ile mesajın kaynağı ve bütünlüğü garanti altına alınır.

## 4. Token Ekonomi Yönetimi
- Ajanlar arası veri transferinde "Relevant Context Only" kuralı uygulanır. Devasa metinler yerine sadece sonucun özeti ve kritik kanıtlar paylaşılır.
- Gereksiz "nezaket" mesajları (chitchat) A2A protokolünde yasaktır; sadece yapılandırılmış veri alışverişi yapılır.
