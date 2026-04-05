
import urllib.request
import json
import time

def fetch_subreddit_top(subreddit, limit=10):
    url = f"https://www.reddit.com/r/{subreddit}/top/.json?t=month&limit={limit}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            posts = []
            for child in data['data']['children']:
                post = child['data']
                posts.append({
                    "subreddit": subreddit,
                    "title": post['title'],
                    "content": post.get('selftext', ''),
                    "url": f"https://www.reddit.com{post['permalink']}"
                })
            return posts
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []

if __name__ == "__main__":
    subreddits = ["ClaudeAI", "GeminiAI", "LocalLLM", "PromptEngineering"]
    all_content = []
    for sub in subreddits:
        print(f"Fetching r/{sub}...")
        posts = fetch_subreddit_top(sub)
        all_content.extend(posts)
        time.sleep(1) # Be nice
    
    with open("c:/projects/skills/reddit_raw_data.json", "w", encoding="utf-8") as f:
        json.dump(all_content, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_content)} posts to reddit_raw_data.json")
