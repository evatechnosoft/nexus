## Gemini Added Memories
- Kullanıcının tercih ettiği dil Türkçe'dir.
- Kullanıcının iletişim tercihi kısa, öz ve doğrudan çözümlerdir.
- Kullanıcının rolü BT Müdürü'dür.
- Kullanıcının GitHub kullanıcı adı evatechnosoft'tur.
- Kullanıcı, birincil terminal olarak PowerShell ile Windows 11'de çalışır.
- Kullanıcının proje kısayolları vardır: pc=C:\projects\claude, pcd=C:\projects\claude\Dashboard, pca=C:\projects\claude\arduino-display.
- Kullanıcının ana proje dizini C:\projects\claude'dır.
- Kullanıcının ESP32 ve PlatformIO kullanan bir akıllı pano aracısı projesi var.
- Kullanıcının ESP32, Flutter ve FastAPI arka ucu olan bir akıllı ev aracısı monorepo'su var.
- Kullanıcının bir ux-smart-agent (sweet-home-flutter) Flutter projesi var.
- Kullanıcı, yönetici gerektirmediği için Chocolatey yerine winget'i tercih ediyor.
- Kullanıcı için sık karşılaşılan bir sorun, Flutter'ın kilit dosyasının eski hale gelmesi ve bilgisayarın yeniden başlatılmasını gerektirmesidir.
- Kullanıcı profili özeti: BT Müdürü (GitHub: evatechnosoft), Win11/PowerShell üzerinde çalışıyor. Kısa, doğrudan Türkçe iletişimi tercih ediyor. Ana projeleri C:\projects\claude altında (ESP32, Flutter, PlatformIO, FastAPI) ve kısayolları (pc, pcd, pca) mevcut. Choco yerine winget tercih ediyor. Flutter kilit dosyası sorununa dikkat edilmeli.
- Kullanıcı profili özeti: BT Müdürü (GitHub: evatechnosoft), Win11/PowerShell üzerinde çalışıyor. Kısa, doğrudan Türkçe iletişimi tercih ediyor. Projeler C: ve D: sürücülerinde (ana C:\projects\claude) ESP32, Flutter, vb. kullanılarak kısayollarla (pc, pcd, pca) mevcuttur. `choco` kullanılabilir. Flutter kilit dosyası sorununa dikkat edilmeli.
- For this user, the command for the PlatformIO CLI is 'platformio', not 'pio'. 'pio' is a user-defined alias and should not be used.

<!-- BEGIN ai-sync generated section -->
<!-- DO NOT EDIT. Edit ~/.ai/memory/ and run: ai-sync global-build -->

# Kullanıcı Profili

- **GitHub:** evatechnosoft / evatechnosoft@gmail.com
- **Rol:** IT Müdürü, yazılım şirketi
- **Ekip:** Yazılım ekibi + dış kaynak (contractor) çalışanlar + recruiterlar
- **Şirket ürünü:** layersup.com — İK/işe alım uygulaması
- **Sorumluluklar:** layersup.com DevOps, CI/CD pipeline yönetimi, Azure servisleri, genel IT altyapısı
- **Yazılım ilgisi:** Yazılımı seviyor — aralarda kolaylaştırıcı küçük araçlar yapmak istiyor
- **Uzmanlık:** Tek bir alanda değil — her konuda genel bilgisi var, araştırır ve geliştirir
- **Hobiler:** EvAnotes (Flutter aile uygulaması — aktif Sprint-2), ESP32/Arduino projeleri
- **Hedef:** Claude genel asistan — iş, DevOps, Azure, araştırma, küçük yazılım projeleri, her konu
- **Çalışma tarzı:** Birlikte karar vererek ilerler, tek taraflı değil
- **Dil:** Türkçe iletişim tercih eder
- Geliştirme süreçlerinde 'Intent (Niyet)', 'Action (Eylem)', 'Validation (Doğrulama)' ve 'Wait (Bekleme)' aşamalarını içeren yapılandırılmış raporlama formatını tercih ediyorum. Ayrıca projelerde 'fiziksel envanter' ile 'dijital varlık/agent ops' dashboard'larının ayrıştırılmasını ve projelerin 'bozmadan, temizlenerek (junk-free)' yeni repolara taşınmasını standart olarak uyguluyorum.
- Git ve Deployment Stratejisi: Geliştirmeler 'feature/', 'bug/', 'fix/' dallarında (branch) yapılır. Tüm geliştirmeler önce 'dev' branch'inde toplanır. Onay sonrası 'test' branch'ine aktarılır ve test ortamında doğrulanır. Kullanıcı 'tamam' diyene kadar bu döngü devam eder. Son aşamada üretim (prod) ortamına/branch'ine gönderilir.
- AgentOps-Nexus (eski it-inventory) uygulaması yerel geliştirme ve test ortamlarında varsayılan olarak 4550 portunu kullanır. Üretim (prod) ortamında PostgreSQL kullanılır.
- Planlama ve geliştirme süreçlerinde ilerlemeyi net takip edebilmek için mutlaka kontrol kutucukları (checkbox: - [x] / - [ ]) kullanılmalı, tamamlanan adımlar işaretlenerek raporlanmalıdır.
- Mimari Yaklaşım: Uygulamalar 'Nexus' (Merkezi Bağlantı) vizyonuna uygun olarak 'Fiziksel Envanter' ve 'Dijital Varlık/Agent Ops' olarak iki ayrı dashboard ile kurgulanır. Veri tabanı olarak yerelde SQLite, üretimde PostgreSQL 15 kullanılır.
- DevOps ve Mimari Standartları: Dosya isimlendirmelerinde ortam belirteci her zaman önde olmalıdır (örn: prod-docker-compose.yml, prod.env). Kod yapısı SOLID prensiplerine ve Dependency Injection (DI) mantığına uygun mikro-mimaride yazılmalıdır (Veritabanı bağımsızlığı esastır). Arayüzler kesinlikle mobil ve masaüstü için duyarlı (responsive) olmalıdır. Sunucu (CasaOS/ZimaOS) işlemleri 192.168.1.186 IP'si üzerinden 'dean' kullanıcısıyla yapılır. 4500-4600 port aralığı AgentOps-Nexus sistemine rezerve edilmiştir.
- Transfer Stratejisi: Üretim (Prod) ve Test ortamları için GitHub tabanlı CI/CD akışı kullanılır. Geliştirme (Dev) ortamında yerel ve sunucu senkronizasyonu için SCP tercih edilir. Sunucu tarafında Secret (Key Vault) yönetimi için Coolify, konteyner yönetimi için Portainer kullanılır. Veri depolama (Blob) yapısı bu araçların sağladığı volume yönetim sistemine entegre edilir.
- ZimaOS/ZimaCube İşletim Sistemi Standartları: Root dosya sistemi (/) salt-okunurdur. Docker işlemleri için 'DOCKER_CONFIG' değişkeni mutlaka yazılabilir bir alana (örn: '/var/lib/docker/.docker' veya '/DATA/AppData/docker-config') yönlendirilmelidir. Kalıcı veriler her zaman '/DATA/AppData/' altında barındırılmalıdır. CLI üzerinden tam yetki için ZimaOS arayüzünden 'Developer Mode' aktif edilmelidir.
- SSH ve Yetki Standardı: 'ssh dean' ile yapılan tüm sunucu müdahalelerinde varsayılan olarak 'sudo' yetkisi kullanılır. Veritabanı port çakışmalarını önlemek için 'nexus-db' gibi alt servislerin portları host makinesine açılmaz (No host port mapping), sadece Docker iç ağında (Private Network) çalıştırılır.
- ZimaOS/ZimaCube Uzak Geliştirme Standartı: VS Code SSH bağlantılarında 'Permission Denied' hatalarını önlemek için settings.json içinde 'remote.SSH.serverInstallPath' değeri mutlaka '/DATA' (yazılabilir alan) olarak ayarlanmalıdır. Root dizini (/) %100 dolduğunda sistem otomatik olarak salt-okunur (read-only) moda geçer; bu durumda 'df -h /' ile kontrol edilip temizlik yapılmalıdır.
- Context Tazeleme & Sıkıştırma Protokolü: Uzun oturumlarda 'halüsinasyon' ve odak kaybını önlemek için IT Müdürü (Agent), her 10-15 turn'de bir veya kritik faz değişimlerinde mevcut durumu 'GEMINI.md' dosyasına kompakt bir şekilde (Current State, Next Steps, Critical Constraints) özetlemeli ve kullanıcıya 'Context Tazeleme Zamanı' hatırlatması yapmalıdır. Bu, 'Tek Komutla Durum Kontrolü' sağlar.
- ZimaOS/CasaOS Port Senkronizasyonu: CasaOS arayüzündeki Web UI kısayollarını (modül yükleniyor hatası) düzeltmek için '/DATA/.casaos/apps/' altındaki YAML dosyalarında bulunan 'port_map' değerleri Python tabanlı bir script ile güncellenmelidir. 'sed' veya 'cat' komutları Bash tırnak işareti yorumlamaları nedeniyle bu kilitli dosyalarda başarısız olabilir. Python 'replace' metodu en güvenli cerrahi yöntemdir.

## Sistem Bilgisi

- **OS:** Windows 11 Pro
- **Terminal:** PowerShell (birincil), Git Bash (ikincil)
- **Paket yöneticisi:** winget tercih et, npm, choco (admin gerekli)
- **jq full path:** `C:\Users\Deacjx\AppData\Local\Microsoft\WinGet\Links\jq.exe`
- **PowerShell profili:** `C:\Users\Deacjx\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`

## Kurulu Araçlar

- Claude Code, DX plugin (dx@ykdojo), cc-safe
- Gemini CLI, Playwright MCP, filesystem MCP, github MCP, fetch MCP
- gh CLI (evatechnosoft authenticate edilmiş), git, npm, winget

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

<!-- Generated by ai-sync global-build. DO NOT EDIT. Edit ~/.ai/memory/ instead. -->

# Projeler & Dizin Kısaltmaları

## Dizin Kısaltmaları

| Kısaltma | Dizin | Açıklama |
|---|---|---|
| `pc` | `C:\projects\claude` | Projeler ana dizini |
| `pcd` | `C:\projects\claude\Dashboard` | ESP32 Dashboard (PlatformIO) |
| `pca` | `C:\projects\claude\arduino-display` | ESP32 Arduino Display (PlatformIO) |
| `eva` | `C:\projects\EvAnotes` | EvAnotes projesi |

Kullanıcı bu kısaltmaları yazdığında o dizine geç ve içeriğini göster.

## EvAnotes

**GitHub:** https://github.com/evatechnosoft/EvAnotes (private)
**Stack:** Flutter (iOS+Android) + Node.js + Express + PostgreSQL
**Mimari:** Offline-first (SQLite + sync), Riverpod, GoRouter, WebSocket+polling
**Entegrasyon:** Google OAuth, Calendar, Drive | 2FA: SMS/email
**Design Spec:** `C:\projects\claude+antigravity\docs\superpowers\specs\2026-03-17-family-task-management-design.md`

**Git:** `main`(prod) → `test`(QA) → `dev`(aktif)
**Feature branches:** `feature/uiux-screens`, `feature/frontend-flutter`, `feature/backend-api`, `feature/test-suite`, `feature/feedback-analytics`

**6 Paralel Rol:** PM, UI/UX, Frontend, Backend, Test, Analytics
**TDD:** Test-Driven Development uygulanıyor

**Kod Kılavuzları** — EvAnotes'ta kod yazarken önce bunları oku:
- `software-architecture-guidelines.md` → SOLID, Repository/Service/Notifier katmanları, DB/API swap
- `flutter-coding-guidelines.md` → Riverpod 3.x `Notifier<T>`/`NotifierProvider<N,T>`, auth persistence, test pattern
- Konum: `~/.claude/projects/C--projects-github-EvAnotes/memory/`

## Dashboard (ESP32)

- `C:\projects\claude\Dashboard` — ESP32, PlatformIO
- Komutlar: `pio run`, `pio run --target upload`, `pio device monitor`

## Arduino Display (ESP32)

- `C:\projects\claude\arduino-display` — ILI9341 TFT 320x240, 4 ekran
- Komutlar: `pio run`, `pio run --target upload`, `pio device monitor`
- GitHub: https://github.com/evatechnosoft/smart-dashboard-agent (private)

## Smart Home Agent

- `C:\projects\claude\smart-home-agent` — Monorepo
- GitHub: https://github.com/evatechnosoft/smart-home-agent (private)
- Stack: ESP32-agent, ESP32-display, Flutter, FastAPI, SQLite
- Bağlam kaybında: `PROJECT-SUMMARY.md` oku

## Referans Dosyalar

- Hafıza: `~/.claude/MEMORY.md` (legacy, yerini rules/ aldı)
- Hatalar: `~/.claude/ERRORS.md`
- Onaylı komutlar: `~/.claude/ALLOWED_COMMANDS.md`
- claude-brain: https://github.com/evatechnosoft/claude-brain (private)

<!-- Generated by ai-sync global-build. DO NOT EDIT. Edit ~/.ai/memory/ instead. -->

# Claude Code Best Practices

Kaynak: shanraisshan/claude-code-best-practice (19.2k ⭐) + codex-cli-best-practice

---

## Planlama

- **Her zaman plan mode'dan başla** — implement etmeden önce planı onayla
- İkinci bir Claude oturumunda planı staff engineer gözüyle review et
- Kapsamlı PRD yerine **prototip ağırlıklı** çalış (20-30 versiyon ucuz)
- Minimal spec yaz, Claude'un AskUserQuestion ile sorgulasına izin ver
- Her aşamada unit + otomasyon + integration test planla
- Cross-model review: Planı Claude Code ile yaz, başka model ile review et

## CLAUDE.md Kuralları

- **200 satırdan az** tut (ideal ~60) — Claude büyük dosyaları atlıyor
- `<important if="...">` etiketiyle kritik kuralları işaretle
- Büyük talimatlar → `.claude/rules/` klasörüne böl
- Monorepo: hiyerarşik CLAUDE.md kullan (her pakette ayrı)
- `@path` ile modüler import yap
- Herhangi biri "claude, run tests" deyince çalışmalı — ilk deneme

## Agent / Subagent Patterns

- **Role-based değil feature-specific** agent yaz (genel değil, domain spesifik)
- Her agent: custom tools, permissions, model, memory, persistent identity
- İzole bağlamda çalıştır — mevcut context'i kirletme
- 2.17.8 frontmatter: `effort`, `maxTurns`, `disallowedTools` kullan
- Paralel agent team: git worktree ile birden fazla agent aynı anda
- Ralph Wiggum Loop: uzun otonom görevler için iteratif döngü

## Agent Frontmatter (2.17.8+)

```yaml
---
name: my-agent
description: "Ne yapar"
model: sonnet          # veya haiku, opus, inherit
effort: high           # low / medium / high — thinking depth
maxTurns: 15           # max turn sayısı
disallowedTools:       # yasak araçlar
  - Bash
  - Write
---
```

## Komutlar & Skill'ler

- Komutlar: basit, yeniden kullanılabilir prompt şablonları
- Skill'ler: auto-discoverable, preloadable bilgi paketleri
- Hierarşi: **Command → Agent → Skill**

## Memory & Context

- Birden fazla CLAUDE.md + `.claude/rules/` ile organize et
- Yarım migrate edilmiş framework bırakma — model karışır
- `.claude/settings.json` ile hiyerarşik config
- Geçmiş oturumlar: `claude-self-reflect` MCP ile ara
- Bağlam kaybolursa: `PROJECT_HANDOFF.md` / `context-prep` skill

## Prompting Teknikleri

- Direkt söyle: "grill me", "prove this works"
- Vasat çözüm için: "scrap this, implement the elegant solution"
- Hata alınca: sadece hata metnini yapıştır + "fix"
- Detayları micromanage etme — Claude'un kararına bırak
- "Babysite etme" — net spec ver, çalışmasına izin ver

## Workflow Teknikleri (Codex'ten Claude'a uyarlandı)

- **Fork & Resume**: Alternatif dene, çalışan session'ı kaybetme
- **Git worktree**: Paralel development branch'leri
- **Incremental commit**: Her task tamamlanınca commit et, bekletme
- **Headless/CI**: `claude --print` ile CI/CD pipeline entegrasyonu
- **Approval policy**: `on-request` ile başla, sonra gevşet
- **Sandbox + approval**: Güvenlik/verimlilik dengesi

## Hook Patterns

- Olay bazlı otomasyon: PreToolUse, PostToolUse, Stop, StopFailure
- Ses bildirimi: SessionStart, Stop, UserPromptSubmit
- Tehlikeli komut bloğu: PreToolUse/Bash matcher
- Token takip: UserPromptSubmit hook
- Session özeti: Stop / SessionEnd hook

## Debugging

- Hata + "fix" yeterli — uzun açıklama yapma
- Screenshot + MCP Playwright ile görsel bağlam ver
- Farklı model: QA için Opus, hızlı implementasyon için Haiku
- Background task ile detaylı log topla

## Kısaltmalar / Araçlar

| Araç | Kullanım |
|---|---|
| `sequential-thinking` MCP | Karmaşık çok adımlı reasoning |
| `claude-self-reflect` MCP | Geçmiş oturum arama |
| `dollhouse` MCP | Persona/skill/template yönetimi |
| `/context-prep` | Görev öncesi bağlam hazırlama |
| `/deep-research` | Iteratif web araştırması |
| `/incident-commander` | Prod olayı yönetimi |
| `/cicd-orchestrator` | Pipeline yönetimi |

<!-- Generated by ai-sync global-build. DO NOT EDIT. Edit ~/.ai/memory/ instead. -->

# MCP Güvenlik Notları

## Genel Kurallar

MCP eklemeden önce şu sorularını sor:

1. **Kaynak:** Resmi `@modelcontextprotocol/server-*` paketi mi, yoksa üçüncü taraf mı?
2. **Hardcoded IP/URL:** `mcp.json` veya config'de harici IP adresi var mı?
3. **API Key:** Ortam değişkeni mi yoksa config'e gömülü mü?
4. **npm audit:** Bağımlılıklarda güvenlik açığı var mı?
5. **Son commit:** Repo aktif mi, abandonware mi?

---

## Kırmızı Bayraklar — EKLEME

| Durum | Neden Tehlikeli |
|---|---|
| `"url": "http://34.x.x.x:XXXXX/sse"` gibi hardcoded IP | Sunucu kayıtlı, istekleri logluyor olabilir, kapanabilir |
| `"url": "http://..."` (HTTPS değil) | Man-in-the-middle riski |
| NPM'de yayınlanmamış, sadece GitHub repo | Doğrulama yok, zararlı kod eklenebilir |
| README olmayan, tek commit'li repo | Suspect / honeypot olabilir |
| API key config dosyasına gömülü | Key sızıntısı riski |

---

## Güvenli Kurulum Şablonları

### Resmi MCP (env key ile)
```bash
claude mcp add brave-search --scope user \
  -e BRAVE_API_KEY=YOUR_KEY \
  -- npx -y @modelcontextprotocol/server-brave-search
```

### Resmi MCP (key gerektirmeyen)
```bash
claude mcp add sequential-thinking --scope user \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## Kurulu Güvenli MCP'ler (User Scope)

| MCP | Kaynak | Durum |
|---|---|---|
| playwright | `@playwright/mcp` | ✅ Resmi |
| github | `@modelcontextprotocol/server-github` | ✅ Resmi |
| fetch | `@modelcontextprotocol/server-fetch` | ✅ Resmi (✗ bağlantı sorunu) |
| filesystem | `@modelcontextprotocol/server-filesystem` | ✅ Resmi |
| claude-self-reflect | local script | ✅ Local |
| excalidraw | `mcp-excalidraw-server` | ⚠️ 3rd party (✗ bağlantı sorunu) |

---

## Referans Kaynaklar

| Kaynak | URL | Not |
|---|---|---|
| Awesome Context Engineering | https://github.com/Meirtz/Awesome-Context-Engineering | Context Engineering survey — memory sistemleri, MCP/A2A/AG-UI protokolleri, RAG araçları. mem0/Graphiti olgunlaşınca tekrar değerlendir. |
| arXiv 2507.13334 | https://arxiv.org/abs/2507.13334 | "Context Engineering for Large Language Models" survey makalesi |

## Reddedilen MCP'ler

| MCP / Repo | Red Sebebi | Tarih |
|---|---|---|
| `bobbercheng/mcp-deep-research` | Hardcoded harici IP (`34.123.61.175`) — tüm istekler yabancı sunucuya gönderilir | 2026-03-19 |

---

## Alternatif: Harici MCP Yerine Yerleşik Araçlar

Çoğu araştırma işi zaten kurulu araçlarla yapılabilir.
Bkz: `~/.claude/commands/deep-research.md`

# Spec-Kit Kullanım Kılavuzu

**Spec-Kit**, spec-driven development için GitHub'dan gelen açık kaynak araçtır. Proje ilkelerinden başlayıp otomatik olarak görevleri oluşturur.

## Nedir?

Geleneksel workflow (kod → test) yerine, **spec-first** yaklaşım kullanır:
- **Spesifikasyon** yazarsın
- **Spec-Kit** görev listesi oluşturur
- **Uygulama** bu görevlere göre yapılır
- Kalite ve hız artar

## Kurulum

### Kalıcı Kurulum (Önerilen)
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

### Tek Kullanım (Test için)
```bash
uvx --from git+https://github.com/github/spec-kit.git specify init <PROJE_ADI>
```

## 6 Adımlık Temel Akışı

### 1. Constitution (İlkeler)
```bash
specify constitution
```
Proje değerleri, amaçları, tasarım felsefeleri tanımla.

### 2. Specify (Spesifikasyon)
```bash
specify specify
```
**Ne** inşa edeceğini tanımla (features, user stories, senaryolar).

### 3. Plan (Teknik Plan)
```bash
specify plan
```
**Nasıl** yapacağını planla (mimari, stack, API tasarımı).

### 4. Tasks (Görevler)
```bash
specify tasks
```
Otomatik olarak yapılacak görevler listesi oluşturulur.

### 5. Implement (Uygulama)
```bash
specify implement
```
Her görevi sırayla tamamla.

## Desteklenen AI Araçları

✅ Claude Code (Recommended)
✅ GitHub Copilot
✅ Cursor, Windsurf
✅ Gemini, Qwen Code, Mistral

## Hızlı Başlangıç

```bash
# Yeni feature için
specify init feature-name
cd feature-name

# Akışı başlat
specify constitution  # İlkeleri tanımla
specify specify       # Speci yazıl
specify plan          # Teknik plan yap
specify tasks         # Task listesi al
specify implement     # Görevleri yap
```

## İsteğe Bağlı Komutlar

- `specify clarify` — Belirsiz noktaları açıkla
- `specify analyze` — İş akışını analiz et
- `specify checklist` — Tamamlanma durumunu kontrol et

## Dosya Yapısı

```
.speckit/
├── constitution.md   # Proje ilkeleri
├── specify.md        # Spesifikasyon
├── plan.md          # Teknik plan
├── tasks.md         # Görev listesi
└── output/          # Çıktılar
```

## Gerçek Kullanım Senaryoları

### 1. Yeni Feature Ekleme
```bash
specify init feature-auth-2fa
cd feature-auth-2fa
specify constitution  # SMS/Email ilkeleri
specify specify       # User flow
specify plan          # Backend API, provider seçimi
specify tasks         # Task otomatik oluşur
```

### 2. Refactoring
```bash
specify init refactor-database
specify constitution  # Performans ilkeleri
specify plan          # Yeni schema
specify tasks         # Migration görevleri
```

### 3. API Tasarımı
```bash
specify init api-design
specify specify       # Endpoint spesifikasyonu
specify plan          # Authentication, rate limiting
specify tasks         # Implementation görevleri
```

## Referanslar

- **GitHub:** https://github.com/github/spec-kit
- **Doküman:** https://github.com/github/spec-kit?tab=readme-ov-file

---

**Not:** Spec-Kit isteğe bağlıdır. Gerektiğinde kurup çalıştırabilirsin. Tüm projelerinizde kullanabilirsiniz.

<!-- END ai-sync generated section -->
inizde kullanabilirsiniz.

<!-- END ai-sync generated section -->
