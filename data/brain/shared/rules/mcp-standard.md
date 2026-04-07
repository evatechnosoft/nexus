# Model Context Protocol (MCP) Uygulama Standartları

Bu belge, Anthropic tarafından başlatılan ve 2026'da evrenselleşen MCP standartlarına dayalı araç ve veri entegrasyon kurallarını tanımlar.

## 1. Mimari Roller (Roles)
- **Host (Gemini CLI):** Ana orkestratör; güvenlik politikalarını dayatır ve kaynakları yönetir.
- **Client:** Ajanın sunucuyla kurduğu stateful (durumlu) oturum.
- **Server:** Spesifik yetenekleri (Tools) ve verileri (Resources) sağlayan hafif servisler.

## 2. Temel Bileşenler (Primitives)
- **Tools:** Ajanın çağırabileceği yürütülebilir fonksiyonlar (örn. `send_email`).
- **Resources:** Salt okunur veri kaynakları (örn. `logs`, `db_schema`).
- **Prompts:** Yeniden kullanılabilir talimat şablonları.

## 3. Araç Tasarım Kuralları (Best Practices)
- **Yüksek Seviyeli Araçlar:** Düşük seviyeli API'leri sarmalayan, iş odaklı araçlar tasarlayın (örn. `get_user` + `get_orders` yerine doğrudan `track_order`).
- **Düz Parametreler (Flattened Arguments):** İçiçe geçmiş karmaşık JSON yerine, basit string ve enum/literal değerleri kullanın. Bu, halüsinasyonu %30 azaltır.
- **Hata Mesajları:** Bir araç hata verdiğinde, hata mesajı ajana girdisini nasıl düzelteceğini (örn. "Geçersiz tarih formatı, YYYY-MM-DD kullanın") açıkça söylemelidir.
- **Sayfalama (Pagination):** Hiçbir zaman büyük veri setlerini doğrudan bağlama (context) basmayın. `limit` ve `offset` kullanın; `has_more` flag'i ile ajanı bilgilendirin.

## 4. Güvenlik ve İzinler
- **Least Privilege (En Az Yetki):** Her sunucuya sadece işi için gereken minimum izni verin.
- **Human-in-the-Loop:** Mutasyon yapan (silme, değiştirme, ödeme) tüm işlemler kullanıcı onayı gerektirir.
- **Input Validation:** Ajanlardan gelen tüm girdiler "prompt injection" riskine karşı valide edilmelidir.
