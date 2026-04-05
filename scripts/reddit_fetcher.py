
import urllib.request
import json
import sys

def fetch_reddit(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    try:
        req_with_json = url if url.endswith('.json') else f"{url.rstrip('/')}/.json"
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            # Usually Reddit API returns a list [post, comments]
            post_data = data[0]['data']['children'][0]['data']
            return {
                "title": post_data['title'],
                "content": post_data['selftext'],
                "upvotes": post_data['ups']
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    urls = [
        "https://www.reddit.com/r/PromptEngineering/comments/1nt7x7v/after_1000_hours_of_prompt_engineering_i_found/.json",
        "https://www.reddit.com/r/OpenAI/comments/18v4n8j/a_different_approach_to_system_prompts/.json"
    ]
    for url in urls:
        print(f"--- Fetching: {url} ---")
        result = fetch_reddit(url)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Title: {result['title']}")
            print(f"Upvotes: {result['upvotes']}")
            print("-" * 20)
            print(result['content'][:3000]) # Get first 3000 chars
            print("\n" + "="*50 + "\n")
