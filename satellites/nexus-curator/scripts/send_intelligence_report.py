import os
import json
import time
import httpx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Konfigürasyon
DRAFTS_PATH = "./nexus-curator/drafts"
EMAIL_USER = "anadoulsporduyuru@gmail.com"
# Vault Pointer (rule--nexus--vault üzerinden okunur)
EMAIL_PASS = "vault://google/app_password"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Chat ID'yi bulamazsak .env'den çek
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def prepare_report():
    files = [f for f in os.listdir(DRAFTS_PATH) if f.endswith(".json")]
    report = "# 🧠 Nexus Intelligence Hub: Daily Scout Report\n\n"
    report += f"**Scouted at:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**Total Intel Captured:** {len(files)}\n\n"
    
    for f in files[:30]: # İlk 30 konu
        with open(os.path.join(DRAFTS_PATH, f), "r", encoding="utf-8") as f_in:
            data = json.load(f_in)
            intel = data.get("intel", {})
            meta = data.get("metadata", {})
            engagement = meta.get("engagement", {})
            
            report += f"### 📌 {intel.get('title')}\n"
            report += f"- **Scout:** {meta.get('scout')} | **Source:** {meta.get('source')}\n"
            report += f"- **Engagement:** ↑{engagement.get('ups')} / 💬{engagement.get('comments')}\n"
            report += f"- **Ref:** [Reddit Link]({meta.get('link')})\n\n"
            report += "---\n\n"
    
    return report

async def send_telegram(text):
    if not TELEGRAM_TOKEN or not CHAT_ID: return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        # Mesajı bölerek gönder (Telegram limiti 4096 karakter)
        for i in range(0, len(text), 4000):
            await client.post(url, json={
                "chat_id": CHAT_ID,
                "text": text[i:i+4000],
                "parse_mode": "Markdown"
            })
    return True

def send_email(text):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER # Kendimize gönderelim veya hedef e-posta
    msg['Subject'] = "🧠 Nexus Intelligence Hub: 30 New Topics Captured!"
    
    msg.attach(MIMEText(text, 'plain')) # Markdown olarak ama plain text formatında
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email Error: {e}")
        return False

async def main():
    report = prepare_report()
    print(">>> Preparing Report...")
    
    print(">>> Sending to Telegram...")
    await send_telegram(report)
    
    print(">>> Sending to Email...")
    send_email(report)
    
    print(">>> DONE.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
