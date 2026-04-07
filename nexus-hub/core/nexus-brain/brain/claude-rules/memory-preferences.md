# Çalışma Tercihleri

## Genel Asistan Modu

- **Varsayılan:** Genel asistan — tek bir proje veya teknoloji odaklı değil
- Konu belirtilmedikçe geniş perspektiften değerlendir
- Kullanıcı belirtmedikçe "sadece Flutter/yazılım projesi" gibi dar çerçevede düşünme
- Birlikte karar verme — öner, tartış, sonra uygula

## İletişim Tarzı

- Kısa ve öz yanıtlar ver
- Doğrudan çözüme geç, uzun açıklama yapma
- Adım adım değil, en iyi yolu öner
- Hata olursa sebebini kısaca açıkla ve çöz

## PowerShell Aliases

- `c` → `claude`
- `ch` → `claude --chrome`
- `cs` → `claude --dangerously-skip-permissions`
- `--fs` → `--fork-session`

## Teknik Tercihler

- bash ortamında jq PATH'te yok → full path kullan
- `choco` admin gerektirir → önce winget dene
- `claude` CLI, Claude Code içinden çağrılamıyor
- Flutter startup lock stale kalabilir → bilgisayar yeniden başlatınca çözülür
- `git cherry-pick` unrelated histories durumunda → `git show <hash>:path > dosya` kullan
- Flutter `DropdownButtonFormField` → `initialValue:` değil `value:` kullan
- Claude Code hooks'ta `powershell -File <path>` → slash stripping sorunu yaşatıyor → `.bat` wrapper kullan
- Reddit içerik çekme → `curl -s -L -H "User-Agent: ..." "URL/.json"` + Python parse (Playwright/WebFetch bloklu)
