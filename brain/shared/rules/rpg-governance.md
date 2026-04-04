# RPG Ajan Yönetimi ve "Yorgunluk" Kuralları

Bu belge, sistemin teknik metriklerini RPG (Stamina, Vitality, Strength) mantığıyla nasıl yöneteceğini tanımlar.

## 1. Karakter Kartı Metrikleri (Bağımsız Ajanlar)
Her ajan (Analist, Fetch, Design vb.) kendi Stamina ve Luck değerlerine sahiptir.
- **⚡ STAMINA:** Ajanın yaptığı işe göre (örn. DesignAgent çizim yaparken daha hızlı yorulur) bağımsız azalır.
- **🍀 LUCK:** Akıl yürütme kalitesi. Düşükse halüsinasyon riski yüksektir.

## 2. Komutlar ve Dinlenme
- **/compress <AgentName>:** Belirtilen ajanın bağlamını özetleyerek mühürler (Checkpoint) ve Stamina'sını %100'e (Rested) çıkarır.
- **/party-status:** Tüm aktif ajanların RPG kartlarını ve yorgunluk durumlarını listeler.

## 3. Uzman Ajan Rolleri
- **AnalistAgent:** Derin araştırma ve veri sentezi yapar.
- **FetchAgent:** Web tarama ve ham veri çekme görevlerini üstlenir. (Stamina'sı veri yoğunluğuna göre azalır).
- **DesignAgent:** Görselleştirme ve mimari tasarım yapar. (Yüksek işlem gücü harcar, hızlı yorulur).

## 3. Ajan Davranış Standartları
- Ajanlar her işlem sonunda kendi Stamina'larını kontrol etmeli ve kullanıcıya kısa bir "Karakter Durumu" sunmalıdır.
- Gereksiz bilgi (noise) Stamina'yı (gereksiz token harcayarak) hızlı tüketir. Bu yüzden "Gerekli Bağlam" (Relevant Context) ilkesine sadık kalınmalıdır.
