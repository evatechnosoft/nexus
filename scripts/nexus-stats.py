import os
import json
import glob
from datetime import datetime

# ── Configuration ───────────────────────────────────────────────────────────
NEXUS_TMP_DIR = r"C:\Users\Deacjx\.gemini\tmp\nexus-hub\chats"
MODEL_LIMITS = {
    "gemini-1.5-pro": 2000000,
    "gemini-1.5-flash": 1000000,
    "gemini-3-flash-preview": 1000000,
    "gemini-2.0-flash": 1000000,
}
DEFAULT_LIMIT = 1000000

# ANSI Colors
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[31m"
C_GREEN  = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE   = "\033[34m"
C_CYAN   = "\033[36m"
C_GRAY   = "\033[90m"

def get_latest_session_file():
    files = glob.glob(os.path.join(NEXUS_TMP_DIR, "*.json"))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def format_tokens(n):
    if n >= 1000000:
        return f"{n/1000000:.2f}M"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

def get_color_for_pct(pct):
    if pct >= 80: return C_RED
    if pct >= 50: return C_YELLOW
    return C_GREEN

def render_bar(pct, width=40):
    filled = int(width * pct / 100)
    color = get_color_for_pct(pct)
    bar = color + "█" * filled + C_GRAY + "░" * (width - filled) + C_RESET
    return bar

def main():
    session_file = get_latest_session_file()
    if not session_file:
        print(f"{C_RED}Error: No session files found in {NEXUS_TMP_DIR}{C_RESET}")
        return

    with open(session_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    messages = data.get("messages", [])
    if not messages:
        print(f"{C_YELLOW}No messages found in session.{C_RESET}")
        return

    # Find the last gemini message with token data
    last_tokens = None
    model_name = "unknown"
    user_turns = 0
    
    breakdown = []
    prev_total = 0

    for msg in messages:
        msg_type = msg.get("type")
        if msg_type == "user":
            user_turns += 1
        
        tokens = msg.get("tokens")
        if tokens:
            last_tokens = tokens
            model_name = msg.get("model", model_name)
            
            # Calculate what this turn spent
            current_total = tokens.get("total", 0)
            spent = current_total - prev_total
            if spent > 0:
                # Try to get user prompt text
                prompt = "Unknown"
                # Search backwards for the preceding user message
                idx = messages.index(msg)
                for i in range(idx-1, -1, -1):
                    if messages[i].get("type") == "user":
                        content = messages[i].get("content")
                        if isinstance(content, list) and len(content) > 0:
                            prompt = content[0].get("text", "Text-less")[:30] + "..."
                        break
                breakdown.append((prompt, spent))
            prev_total = current_total

    if not last_tokens:
        print(f"{C_YELLOW}No token data available in the latest messages.{C_RESET}")
        return

    total_tokens = last_tokens.get("total", 0)
    input_tokens = last_tokens.get("input", 0)
    output_tokens = last_tokens.get("output", 0)
    cached_tokens = last_tokens.get("cached", 0)
    
    limit = MODEL_LIMITS.get(model_name, DEFAULT_LIMIT)
    pct = (total_tokens / limit) * 100

    # Print Output
    print(f"\n{C_BOLD}{C_CYAN}── NEXUS CONTEXT STATUS ──{C_RESET}")
    print(f"{C_BOLD}Model:{C_RESET} {model_name} (Limit: {format_tokens(limit)})")
    print(f"{C_BOLD}Turns:{C_RESET} {user_turns}")
    print(f"{C_BOLD}Usage:{C_RESET} {format_tokens(total_tokens)} / {format_tokens(limit)} ({get_color_for_pct(pct)}{pct:.1f}%{C_RESET})")
    
    print(f"\n{render_bar(pct)}")
    
    print(f"\n{C_BOLD}Breakdown (Last 5 turns):{C_RESET}")
    for prompt, spent in breakdown[-5:]:
        print(f"  {C_GRAY}• {C_RESET}{prompt:<35} {C_YELLOW}+{format_tokens(spent):>6}{C_RESET}")

    print(f"\n{C_BOLD}Tokens:{C_RESET} {C_BLUE}In: {format_tokens(input_tokens)}{C_RESET} | {C_GREEN}Out: {format_tokens(output_tokens)}{C_RESET} | {C_CYAN}Cache: {format_tokens(cached_tokens)}{C_RESET}")
    print(f"{C_CYAN}──────────────────────────{C_RESET}\n")

if __name__ == "__main__":
    main()
