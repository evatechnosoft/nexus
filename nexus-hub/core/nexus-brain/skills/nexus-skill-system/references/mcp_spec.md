# Nexus MCP Standard (NMCP)

Bu belge, AgentOps-Nexus projesindeki skill'lerin Open WebUI ve Gemini CLI arasında nasıl paylaşılacağını (Model Context Protocol) tanımlar.

## 📡 MCP Bağlantı Noktaları

- **Provider:** Nexus Brain API (FastAPI)
- **Client 1:** Gemini CLI (Local)
- **Client 2:** Open WebUI (Server-side)

## 🛠️ Tool Definition Schema

Her Nexus Tool (Skill), şu standartta bir JSON şemasına sahip olmalıdır:

```json
{
  "name": "read_nexus_memory",
  "description": "Nexus PM (Project Memory) verilerini oku.",
  "parameters": {
    "type": "object",
    "properties": {
      "category": { "type": "string", "enum": ["ST", "PM", "LT"] }
    }
  }
}
```

## 🔄 Entegrasyon Akışı

1. **Skill Creation:** Yerelde yeni bir skill yazılır.
2. **PostgreSQL Push:** Skill, sunucudaki Global Skills tablosuna atılır.
3. **WebUI Hook:** Open WebUI, Nexus API üzerinden bu skill'i bir 'Function' olarak içeri çeker.

---
**IT Müdürü:** Gemini CLI (MCP Architect)
