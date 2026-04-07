# Nexus Token & Maliyet Optimizasyon Planı

`work.md` dosyasındaki 20 kuralın Nexus ekosistemine entegre edilmesi ve mevcut "Token Israfının" durdurulması hedeflenmektedir. En büyük öncelik, 1244 adet skill klasörünün Claude CLI tarafından gereksiz taranmasını engellemek ve "Lazy-Load" yapısına geçmektir.

## User Review Required

> [!IMPORTANT]
> **Skill Kütüphanesi Temizliği:** `c:\projects\skills\skills` klasöründeki 1244 klasörün tamamı her mesajda Claude Code tarafından taranıyor olabilir. Bu, ciddi bir performans gecikmesi ve token maliyeti demektir. Bu klasörü `.claudeignore` kapsamına alıp sadece gerekli olanları "manual loading" ile açmayı öneriyorum.

> [!WARNING]
> **Zero Localism:** Bu dosyalari Windows üzerinde oluşturacağız ancak Nexus kuralı gereği bunların `DeanOS` (ZimaOS) üzerindeki ana çalışma dizinine (`/DATA/AppData/nexus-brain/`) senkronize edilmesi gerekecektir.

## Proposed Changes

### 1. Dosya Filtreleme ve Ignorance
Gereksiz dosyaların okunmasını engelleyerek %90'a varan mesaj başı tasarruf sağlanacaktır.

#### [NEW] [.claudeignore](file:///C:/projects/skills/.claudeignore)
*   `skills/` klasörü (Tamamı sessize alınacak).
*   `node_modules/`, `dist/`, `build/`, `.venv/`.
*   Büyük log dosyaları ve `.git/`.

---

### 2. Context Anchor Kurulumu
AI'nın her başlatıldığında nerede olduğunu ve hangi bütçeyle hareket ettiğini anlaması sağlanacaktır.

#### [NEW] [claude.md](file:///C:/projects/skills/claude.md)
*   Nexus State Anchor'dan (`GEMINI.md`) referans alan, Claude'a özel "Efficiency instructions".
*   Rule 48-49'da belirtilen "Indeks" yapısının kurulması (Büyük dosyalara gitmeden önce link sorma).

---

### 3. Otomasyon ve İzleme
`GEMINI.md` üzerinde planlanan Grafana dashboard'una token takibinin eklenmesi.

#### [MODIFY] [GEMINI.md](file:///C:/projects/skills/GEMINI.md)
*   Sıradaki adımlara "Token & Cost Dashboard (Grafana 3100)" maddesinin detaylandırılması.

## Open Questions
1.  **Skill Kullanımı:** 1244 skill arasından aktif olarak her gün kullandığınız 3-5 ana skill hangileridir? Bunları "Whitelist" yaparak açık bırakabiliriz.
2.  **Server Sync:** Windows tarafında yapacağımız bu değişiklikleri `sync_to_mcp.py` ile mi sunucuya göndermeliyim, yoksa manuel mi yapacaksınız?

## Verification Plan

### Automated Tests
- `/context` komutu ile `.claudeignore` sonrası aktif token sayısının karşılaştırılması.
- `dir` ve `grep` komutları ile ignore edilen klasörlerin Claude tarafından görülmediğinin teyidi.

### Manual Verification
- Claude CLI açılış hızının ve mesaj başı "thinking" süresinin kısalıp kısalmadığının kullanıcı tarafından gözlemlenmesi.
