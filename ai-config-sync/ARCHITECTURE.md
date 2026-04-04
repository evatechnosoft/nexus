# AI Config Sync — Universal Skill & Instruction Portability Layer

## Problem Statement

Her AI coding aracı kendi config formatını dayatıyor. Bir Flutter projesi için yazdığın responsive-ux skill'i sadece Claude.ai'da çalışıyor. Gemini CLI aynı bilgiyi GEMINI.md formatında istiyor. Yarın Copilot'a geçsen `.github/copilot-instructions.md` lazım. Sonuç: **aynı bilgi N kere yazılıyor, N kere güncelleniyor, N kere drift ediyor.**

## Çözüm: Single Source of Truth → Multi-Target Transpilation

```
┌─────────────────────────────────────────────────────────────┐
│                    CANONICAL SOURCE                         │
│              .ai/config/  (Git-tracked)                     │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│  │ skills/  │  │ guides/  │  │contracts/│  │  memory/    │  │
│  │          │  │          │  │          │  │             │  │
│  │ flutter- │  │ code-    │  │ api-     │  │ preferences │  │
│  │ arch.md  │  │ style.md │  │ design.md│  │ .md         │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │
│                                                             │
│  manifest.yaml  ←  Tek kaynak: neyin nereye gideceği        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    ai-sync build
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
   │  CLAUDE.md   │ │  GEMINI.md  │ │  AGENTS.md   │
   │  .claude/    │ │  .gemini/   │ │  (cross-tool)│
   │  rules/      │ │  GEMINI.md  │ │              │
   └─────────────┘ └─────────────┘ └──────────────┘
   Claude Code      Gemini CLI       Cursor/Copilot
```

## Canonical Directory Structure

```
your-project/
├── .ai/                          # ← TEK KAYNAK
│   ├── manifest.yaml             # Dağıtım haritası
│   ├── skills/                   # Tekrar kullanılabilir beceriler
│   │   ├── flutter-architect/
│   │   │   ├── skill.md          # Skill tanımı
│   │   │   └── reference.md      # Ek döküman
│   │   └── api-design/
│   │       └── skill.md
│   ├── guides/                   # Coding standartları
│   │   ├── code-style.md
│   │   ├── testing.md
│   │   └── security.md
│   ├── contracts/                # API sözleşmeleri, mimari kararlar
│   │   ├── architecture-decisions.md
│   │   └── api-contracts.md
│   ├── memory/                   # Kişisel tercihler, proje bağlamı
│   │   ├── project-context.md
│   │   └── preferences.md
│   └── templates/                # Hedef format şablonları (opsiyonel override)
│       ├── claude.hbs
│       └── gemini.hbs
│
├── CLAUDE.md                     # ← GENERATED (git: .gitattributes → generated)
├── .claude/rules/                # ← GENERATED
├── GEMINI.md                     # ← GENERATED
├── AGENTS.md                     # ← GENERATED
└── .ai-sync.lock                 # Son build hash'leri
```

## manifest.yaml Şeması

```yaml
version: "1.0"
project:
  name: "my-flutter-app"
  description: "E-commerce Flutter app with Firebase backend"

targets:
  claude:
    enabled: true
    output:
      root: "CLAUDE.md"                    # Ana dosya
      rules_dir: ".claude/rules/"          # Path-scoped rules
    strategy: "merged"                     # merged | split | minimal
    max_lines: 200                         # Claude önerisi: 200 satır/dosya

  gemini:
    enabled: true
    output:
      root: "GEMINI.md"
      global: "~/.gemini/GEMINI.md"        # Opsiyonel global sync
    strategy: "merged"
    imports: true                          # @file.md import syntax kullan

  agents:
    enabled: false                         # Cursor/Copilot için
    output:
      root: "AGENTS.md"

# Neyin nereye gideceği
distribution:
  # Her skill/guide hangi hedefe dağıtılacak
  - source: "skills/*"
    targets: [claude, gemini]
    scope: "project"                       # project | global | conditional

  - source: "guides/code-style.md"
    targets: [claude, gemini]
    scope: "project"
    claude_rule_path: "code-style"         # .claude/rules/code-style.md olarak

  - source: "guides/testing.md"
    targets: [claude, gemini]
    scope: "project"
    claude_rule_paths: "src/test/**"       # Path-scoped rule

  - source: "guides/security.md"
    targets: [claude, gemini]
    scope: "project"

  - source: "contracts/*"
    targets: [claude, gemini]
    scope: "project"

  - source: "memory/preferences.md"
    targets: [claude, gemini]
    scope: "global"                        # ~/.claude/ ve ~/.gemini/ ye gider

  - source: "memory/project-context.md"
    targets: [claude, gemini]
    scope: "project"

# Format-specific transformations
transforms:
  claude:
    # Claude YAML frontmatter paths kullanıyor
    path_scoped_rules: true
    frontmatter_format: "yaml"
    import_syntax: "@path"                 # CLAUDE.md @./file.md

  gemini:
    # Gemini @file.md import syntax kullanıyor
    import_syntax: "@path"
    concatenation: true                    # Tüm içeriği birleştir
```

## Format Farkları: Detaylı Uyumluluk Matrisi

| Özellik | Claude Code | Gemini CLI | AGENTS.md |
|---------|------------|------------|-----------|
| Ana dosya | `CLAUDE.md` | `GEMINI.md` | `AGENTS.md` |
| Global konum | `~/.claude/CLAUDE.md` | `~/.gemini/GEMINI.md` | Yok |
| Rules dizini | `.claude/rules/*.md` | Alt dizin GEMINI.md | Yok |
| Path scoping | YAML frontmatter `paths:` | Dizin hiyerarşisi | YAML `applyTo:` |
| Import syntax | `@./file.md` | `@./file.md` | `@./file.md` |
| Öncelik | Yakın dosya > uzak | Alfabetik sıra | Concat sırası |
| Max boyut önerisi | ~200 satır/dosya | Sınır yok (pratikte ~500) | ~500 satır |
| Frontmatter | YAML (opsiyonel) | Yok | YAML (opsiyonel) |

## Transpilation Kuralları

### Claude Hedefi
1. `CLAUDE.md` → Skills + guides + contracts + memory birleştirilir
2. Her guide opsiyonel olarak `.claude/rules/` altına path-scoped rule olarak yazılabilir
3. YAML frontmatter ile `paths:` alanı eklenir
4. `@./path` import syntax'ı desteklenir
5. 200 satır limitine dikkat: uzun içerikler `@import` ile referanslanır

### Gemini Hedefi
1. `GEMINI.md` → Skills + guides + contracts + memory birleştirilir
2. `@./file.md` import syntax'ı ile modüler yapı korunabilir
3. Frontmatter kullanılmaz (Gemini bunu parse etmez)
4. Alt dizinlerdeki `GEMINI.md` dosyaları otomatik keşfedilir
5. Gemini ayrıca `AGENTS.md`'yi de okur (GEMINI.md öncelikli)

### Dönüşüm Algoritması
```
for each source file in .ai/:
  1. Parse markdown + opsiyonel YAML frontmatter
  2. Strip canonical-only metadata (version, targets, etc.)
  3. Apply target-specific transforms:
     - Claude: Add YAML frontmatter if path-scoped
     - Gemini: Remove frontmatter, keep pure markdown
  4. Resolve @import paths relative to target location
  5. Concatenate or split based on strategy
  6. Write to target location
  7. Update .ai-sync.lock with content hash
```

## CLI Aracı: `ai-sync`

### Komutlar

```bash
ai-sync init                  # .ai/ yapısını oluştur, manifest.yaml scaffold
ai-sync build                 # Canonical → tüm hedeflere transpile et
ai-sync build --target claude # Sadece Claude hedefini build et
ai-sync build --dry-run       # Neyin değişeceğini göster, yazma
ai-sync diff                  # Canonical vs generated farkları göster
ai-sync validate              # manifest.yaml ve source dosyaları doğrula
ai-sync status                # Son sync durumu, drift tespiti
ai-sync add skill <name>      # Yeni skill scaffold'u oluştur
ai-sync add guide <name>      # Yeni guide scaffold'u oluştur
ai-sync import claude         # Mevcut CLAUDE.md'den canonical'a reverse-import
ai-sync import gemini         # Mevcut GEMINI.md'den canonical'a reverse-import
```

### Git Entegrasyonu

```bash
# .git/hooks/pre-commit (otomatik kurulum: ai-sync install-hooks)
#!/bin/sh
ai-sync build
git add CLAUDE.md GEMINI.md AGENTS.md .claude/rules/ .ai-sync.lock
```

### Drift Detection

```bash
# CI/CD pipeline'da
ai-sync diff --exit-code
# Exit 1 = generated dosyalar canonical'dan farklı → CI fail
```

## Güvenlik Kararları

1. **Secrets asla canonical'da tutulmaz** — `.ai/` git-tracked, secret yok
2. **Generated dosyalar `.gitattributes`'da işaretlenir** — merge conflict azaltır
3. **Lock dosyası** — her generated dosyanın SHA256 hash'i tutulur, tamper detection

## Migration Yolu (Mevcut Dağınık → Organize)

```
Adım 1: ai-sync init
Adım 2: ai-sync import claude    # Mevcut CLAUDE.md varsa parse et
Adım 3: Dağınık skill'leri .ai/skills/ altına taşı
Adım 4: manifest.yaml'ı düzenle
Adım 5: ai-sync build
Adım 6: ai-sync install-hooks    # Git hook kur
Adım 7: git commit -m "chore: unified AI config"
```

## Trade-off Analizi

| Karar | Avantaj | Dezavantaj | Neden bu seçim |
|-------|---------|------------|----------------|
| Canonical olarak plain MD | Her yerde okunur, git-friendly | Metadata için ek dosya lazım | Markdown zaten tüm araçların ortak dili |
| manifest.yaml ayrı dosya | Dağıtım mantığı içerikten ayrı | Bir dosya daha | Separation of concerns |
| Generated dosyalar git'te | CI/CD'de hemen kullanılır | Merge conflict riski | `.gitattributes merge=ours` ile çözülür |
| Lock dosyası | Drift detection, tamper detection | Ekstra complexity | Güvenlik ve tutarlılık için gerekli |
