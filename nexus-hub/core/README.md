# nexus-sync — Universal AI Config Sync

Tek kaynak (`.ai/`), tüm AI araçlara otomatik dağıtım.

## Hızlı Başlangıç

```bash
# 1. Proje kök dizinine kopyala
cp nexus-sync.py /your/project/
cd /your/project

# 2. Başlat
python nexus-sync.py init --project-name "my-app"

# 3. Skills ve guides ekle
python nexus-sync.py add skill flutter-architect
python nexus-sync.py add guide code-style

# 4. İçerikleri düzenle
#    .ai/skills/flutter-architect/skill.md
#    .ai/guides/code-style.md

# 5. Build → CLAUDE.md + GEMINI.md otomatik oluşur
python nexus-sync.py build

# 6. Git hook kur (her commit'te otomatik)
python nexus-sync.py install-hooks
```

## Mevcut Projeyi Tarama

```bash
# Windows — C: ve D: sürücülerini tara
python ai-discovery.py C:\ D:\ --output inventory.json

# Sadece belirli dizin
python ai-discovery.py D:\projects --output inventory.json

# Sadece özet (dosya içerikleri olmadan)
python ai-discovery.py D:\projects --compact
```

## Komutlar

| Komut | Açıklama |
|-------|----------|
| `init` | `.ai/` yapısını oluştur |
| `build` | Canonical → hedef dosyalara transpile |
| `build --target claude` | Sadece Claude hedefini build et |
| `build --dry-run` | Preview, dosya yazma |
| `diff` | Drift kontrolü |
| `status` | Genel durum |
| `validate` | manifest.yaml doğrulama |
| `add skill <isim>` | Yeni skill scaffold |
| `add guide <isim>` | Yeni guide scaffold |
| `import claude` | Mevcut CLAUDE.md'den import |
| `import gemini` | Mevcut GEMINI.md'den import |
| `install-hooks` | Git pre-commit hook kur |

## Gereksinimler

- Python 3.9+
- Harici bağımlılık yok (sadece stdlib)

## Roadmap

1. ✅ **Phase 1:** Statik build-time transpiler (şu an)
2. 🔲 **Phase 2:** MCP Server — AI araçları doğrudan sunucudan skill çeker
3. 🔲 **Phase 3:** Observability — skill performans izleme
