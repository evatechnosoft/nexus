# Nexus Skill Index (NMP-01)

> **IT Müdürü Notu:** Bu dosya, sistemin sahip olduğu yeteneklerin (Skills) hafifletilmiş dizinidir. Tüm yetenekleri prompt'a yüklemek yerine, ihtiyaca göre 'read_skill' aracıyla detaylar okunmalıdır.

## 🛠️ Mevcut Yetenekler (Skills)
1. **nexus-skill-system:** Temel yetenek yönetimi ve MCP köprüsü.
2. **it-inventory-manager:** Envanter kayıt ve puanlama yeteneği.
3. **portable-brain-sync:** GitHub üzerinden hafıza senkronizasyonu.
4. **chatgpt-bridge:** OpenAI Actions için OpenAPI spesifikasyonu üretimi.

## 📜 Kural Setleri (Rules - On-Demand)
- **flutter-guidelines:** Flutter projeleri için SOLID ve Riverpod standartları.
- **zimaos-surgeon:** ZimaOS kilitli dosya sistemine müdahale protokolleri.
- **deployment-ops:** CI/CD ve Docker deployment standartları.

## 🔄 Yükleme Mantığı (Lazy Loading)
Ajan, sadece kullanıcı talebiyle eşleşen yeteneğin `SKILL.md` dosyasını `read_file` ile okur. Detaylar her zaman ilgili klasördedir.
