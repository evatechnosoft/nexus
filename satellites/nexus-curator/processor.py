import os
import json
import httpx
import logging
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")

DRAFTS_PATH = "./drafts"
PROCESSED_PATH = "./processed"

SYSTEM_PROMPT = """Sen Nexus Intelligence Hub'ın Baş Analizcisisin. 
Görevin, ham JSON verilerini analiz edip Nexus (MCP) için yapılandırılmış Markdown (.md) dosyaları üretmektir.

Her çıktı mutlaka bir 'Frontmatter' (Metadata bloğu) ile başlamalıdır:
---
title: [BAŞLIK]
category: [SKILL/RULE/GUIDE]
scout: [SCOUT ADI]
engagement_score: [UPs + Comments]
source: [URL]
tags: [tag1, tag2]
nexus_pointer: [İlgili olabilecek diğer Nexus dosyaları için anahtar kelimeler]
---

İçerik Yapısı:
# [BAŞLIK]

## 🎯 Executive Summary
[Bu bilginin neden önemli olduğuna dair kısa, öz analiz.]

## 🛠 Technical Specifications / Implementation
[Eğer bir SKILL ise adım adım talimatlar ve kod örnekleri. Eğer RULE ise kesin kurallar. Eğer GUIDE ise derinlemesine teknik bilgi.]

## 🔗 Nexus Integration Strategy
[Bu bilginin Nexus MCP'ye nasıl ekleneceği. Örneğin: 'nexus-skill-system/scripts/ altına yeni bir fonksiyon ekle' veya 'shared/rules/ altına yeni bir madde ekle'.]

## 📌 References & Pointers
- See also: [İlgili anahtar kelimeler]
- Original Discussion: [URL]
"""

async def process_draft(filename):
    raw_path = os.path.join(DRAFTS_PATH, filename)
    if not os.path.exists(raw_path): return None

    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get('metadata', {})
    intel = data.get('intel', {})
    score = metadata.get('engagement', {}).get('ups', 0) + metadata.get('engagement', {}).get('comments', 0)

    prompt = f"""Aşağıdaki ham veriyi analiz et ve Nexus formatında (Frontmatter dahil) bir dosya üret. 
    Özellikle bu bilginin bir SKILL mi, RULE mu yoksa GUIDE mı olduğuna zekice karar ver.
    
    SCOUT: {metadata.get('scout')}
    SOURCE: {metadata.get('source')}
    ENGAGEMENT SCORE: {score}
    
    CONTENT TITLE: {intel.get('title')}
    CONTENT BODY: {intel.get('body')}
    """

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": SYSTEM_PROMPT,
                    "stream": False
                },
                timeout=180.0
            )
            
            if response.status_code == 200:
                result = response.json().get("response")
                processed_filename = filename.replace(".json", ".md")
                os.makedirs(PROCESSED_PATH, exist_ok=True)
                
                with open(os.path.join(PROCESSED_PATH, processed_filename), "w", encoding="utf-8") as f:
                    f.write(result)
                
                return processed_filename
        except Exception as e:
            logging.error(f"Ollama processing error: {e}")
            return None
