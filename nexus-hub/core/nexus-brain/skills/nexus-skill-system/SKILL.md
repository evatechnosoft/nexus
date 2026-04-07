---
name: nexus-skill-system
description: "AgentOps-Nexus projelerinde 'Memory-Skill-MCP' döngüsünü yöneten merkezi zekâ sistemi. Bu skill, projenin 'Unutma, Öğren ve Uygula' yeteneğini (NMP - Nexus Memory Protocol) kontrol eder. Gemini CLI ve Ollama/WebUI arasındaki bağlam (context) transferini sağlar."
---

# Nexus Skill System (NMP)

Bu skill, AgentOps-Nexus projesinin 'Dijital Beyni'dir. 

## 🧠 Nexus Memory Protocol (NMP)

Hafıza üç katmandan oluşur:

1. **Short-Term (ST):** Mevcut oturumdaki (Session) değişkenler ve anlık durumlar.
2. **Project-Memory (PM):** `GEMINI.md` ve `handoff.md` dosyalarında tutulan proje özeti.
3. **Long-Term (LT):** PostgreSQL 'Global Skills' tablosunda tutulan kalıcı yetenekler.

## 🔗 MCP & Ollama Bridge

Sistem, sunucudaki Ollama (LLM) ile Gemini CLI'ı şu yollarla birbirine bağlar:

- **Open WebUI Entegrasyonu:** Sunucudaki `mcp_config.json` üzerinden skill'lerin WebUI'a 'Function' olarak enjekte edilmesi.
- **Local Proxy:** Ollama modellerinin Gemini CLI araçlarını (tools) kullanabilmesi için Python tabanlı köprü.

## 🛠️ Temel Komutlar (Workflows)

- **Memory Sync:** Sunucu ve yerel hafızayı eşitle.
- **Skill Inject:** Yeni bir yeteneği (örneğin: Docker Log Analizi) PostgreSQL'e ve WebUI'a gönder.
- **Context Refresh:** `GEMINI.md` üzerinden 'Mental Refresh' yap.

---
**IT Müdürü:** Gemini CLI (Nexus Brain v1.0)
