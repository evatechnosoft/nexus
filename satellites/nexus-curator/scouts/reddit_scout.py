import requests
import json
import time
import os

# Test Konuları: Claude, Codex (Coding/LLM), Gemini
scouts = {
    "Scout-Alpha": ["GoogleGeminiAI", "VertexAI", "ArtificialIntelligence"],
    "Scout-Beta": ["ClaudeAI", "Anthropic", "PromptEngineering"],
    "Scout-Gamma": ["ChatGPTCoding", "LangChain", "OpenAI"], 
}

DRAFTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "drafts")

def scout_reddit():
    headers = {"User-Agent": "Nexus-Scout-v1.0 (evatechnosoft)"}
    os.makedirs(DRAFTS_PATH, exist_ok=True)

    for name, subs in scouts.items():
        print(f">>> {name} is scouting high-engagement dev intelligence...")
        for sub in subs:
            # En iyi 5 post (Yüksek etkileşim için t=week ideal)
            url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=5"
            try:
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code != 200: continue
                
                posts = r.json().get("data", {}).get("children", [])

                for post in posts:
                    data = post.get("data", {})
                    # Etkileşim kontrolü (Puan + Yorum sayısı)
                    ups = data.get("ups", 0)
                    comments = data.get("num_comments", 0)
                    
                    # Süzgeç: Geliştirme/Beceri anahtar kelimeleri
                    title = data.get("title", "")
                    content = data.get("selftext", "")
                    
                    raw_data = {
                        "metadata": {
                            "source": f"reddit/r/{sub}",
                            "id": data.get("id"),
                            "scout": name,
                            "engagement": {"ups": ups, "comments": comments},
                            "link": f"https://reddit.com{data.get('permalink')}",
                            "captured_at": time.time()
                        },
                        "intel": {
                            "title": title,
                            "body": content
                        }
                    }

                    file_name = f"{name}_{sub}_{data.get('id')}.json"
                    with open(os.path.join(DRAFTS_PATH, file_name), "w", encoding="utf-8") as f:
                        json.dump(raw_data, f, indent=4, ensure_ascii=False)
                    print(f"  [+] Captured: {title[:60]}... (↑{ups} / 💬{comments})")

            except Exception as e:
                print(f"Error on {sub}: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    scout_reddit()
