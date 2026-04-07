# Nexus Seans Yapısı (I/O) - Düzeltme ve Standartlaştırma Planı

Kullanıcının yerinde uyarısı üzerine yapılan yeniden değerlendirme sonucunda, seans klasörleme mantığındaki kavramsal hata düzeltilecektir. AI'nın ürettiği analiz ve planlar birer **Çıktı (Output)** iken, kullanıcının verdiği ham veri ve talimatlar **Girdi (Input)**'dur.

## User Review Required

> [!IMPORTANT]
> **Kavramsal Ayrım:**
> *   **INPUT:** Ham bilgi, kaynak dosyalar (örn: `work.md`), gereksinimler. (AI'nın "okuyup" işlemeye başladığı yer).
> *   **OUTPUT:** Analiz raporları, planlar, görev listeleri, üretilen kodlar. (AI'nın "yazıp" teslim ettiği yer).

---

## Proposed Changes

### 1. Klasör Yapısının Düzeltilmesi
`nexus-efficiency` projesi özelinde dosyaların doğru yerlere taşınması.

#### [NEW] [data/sessions/nexus-efficiency/output/](file:///C:/projects/skills/data/sessions/nexus-efficiency/output/)
*   **Taşınacak Dosyalar:** `analysis_results.md`, `implementation_plan.md`, `task.md`. (C ve SSH üzerinden taşınacak).

#### [MODIFY] [data/sessions/nexus-efficiency/input/](file:///C:/projects/skills/data/sessions/nexus-efficiency/input/)
*   **Eklenecek Dosyalar:** `work_source.md` (Asıl `work.md` dosyasının bu seansa özel kopyası).
*   **Silinecek Dosyalar:** Yanlışlıkla buraya atılan `analysis_results.md` vb.

---

### 2. Standart "Nexus Session" Protokolü
Gelecek seanslar için şu protokol izlenecektir:
1.  Kullanıcı bir "Input" verir.
2.  AI, bu inputu `sessions/[proje]/input/` klasörüne "snapshot" olarak kaydeder.
3.  AI, tüm analizi ve planlamayı `sessions/[proje]/output/` klasörüne yazar.
4.  Lazy-load çağrısı yaparken: "Kaynak için `input`'a, mevcut durum için `output`'a bak" denir.

---

### 3. Server-Side Senkronizasyon
Aynı yapının `ssh dean` üzerinden ZimaOS'ta da güncellenmesi.

## Open Questions
1.  **Handoff Dosyası:** Oturum sonu özetini (handoff) `output` klasörü altında mı tutalım yoksa `sessions.md` gibi global bir dosyada mı kalsın? (Önerim: Her ikisi de; detay `output`'ta, özet globalde).

## Verification Plan

### Automated Tests
- `ssh dean "ls -R /DATA/AppData/nexus-brain/data/sessions/nexus-efficiency/"`
- Yerel `tree` çıktısının kontrolü.

### Manual Verification
- AI'nın "Input" ve "Output" arasındaki mantıksal farkı (süzme vs ham veri) doğru ayırt edip etmediğinin test edilmesi.
