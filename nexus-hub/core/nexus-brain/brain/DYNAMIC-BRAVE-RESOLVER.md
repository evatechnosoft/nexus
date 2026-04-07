# Nexus Dynamic Brain Resolver (NMP-02)

> **IT Müdürü Notu:** Bu dosya, sistemin 'Zekâ Çözücü' (Resolver) mantığını tanımlar. Sistem, `@skill:`, `@rule:` veya `@guide:` atıflarını gördüğünde sadece ilgili dosyaları context'e dahil eder.

## 🛠️ Çözücü Hiyerarşisi (Resolution Hierarchy)
1. **İstek:** Kullanıcı `@rule:flutter` veya bir araç (tool) çağırdığında tetiklenir.
2. **Haritalama:** `nexus-skill-map.json` üzerinden dosya yolu bulunur.
3. **Yükleme:** Sadece o dosya `read_file` ile okunur ve 'Hafif Context' (Lean Context) korunur.

## 🔗 Birleşik Ajan Köprüsü (Unified Agent Bridge)
- **Claude:** `main-brain`
- **Gemini:** `state-anchor`
- **GPT:** `instruction-layer`
- **Nexus:** `coordinator`

## 🚀 Örnek Senaryo
Kullanıcı: "Flutter projesine bir buton ekle @rule:flutter-coding-guidelines"
Ajan: 
- `nexus-skill-map.json`'a gider.
- `flutter-coding-guidelines` yolunu bulur.
- Sadece o dosyayı okur.
- Yanıtı verir. (Token tasarrufu: %90+)
