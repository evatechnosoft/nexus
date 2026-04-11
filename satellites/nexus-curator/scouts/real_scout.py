import requests
import json
import os

scouts = {
    "Scout-Alpha": "GoogleGeminiAI",
    "Scout-Beta": "ClaudeAI",
    "Scout-Gamma": "OpenAI",
}


def get_real_data():
    headers = {"User-Agent": "Nexus-Real-Scout/1.0"}
    results = []
    for scout, sub in scouts.items():
        url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=3"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            posts = r.json().get("data", {}).get("children", [])
            for post in posts:
                d = post.get("data")
                results.append(
                    {
                        "scout": scout,
                        "action": "FETCHING",
                        "target": f"r/{sub}",
                        "title": d.get("title"),
                        "link": f"https://www.reddit.com{d.get('permalink')}",
                        "time": "Just now",
                    }
                )
        except:
            pass
    return results


# Bu verileri sunucuya activity olarak kaydet (Simüle değil, gerçek dosya listesinden beslenecek)
activities = get_real_data()
with open("real_activities.json", "w", encoding="utf-8") as f:
    json.dump(activities, f)
