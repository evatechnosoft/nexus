import asyncio
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

from notifier import send_notification

async def main():
    print("--- Telegram Test Mesajı Gönderiliyor ---")
    print(f"Token: {os.getenv('TELEGRAM_BOT_TOKEN')}")
    print(f"Chat ID: {os.getenv('TELEGRAM_CHAT_ID')}")
    
    subject = "Nexus Zekâ Testi"
    message = "Merhaba! AgentOps-Nexus sisteminden Telegram bildirimi başarıyla çalışıyor. 🚀\n\n- Asenkron yapı: ✅\n- Yeni Notifier: ✅"
    
    success = await send_notification(subject, message)
    if success:
        print("✅ Mesaj başarıyla gönderildi!")
    else:
        print("❌ Mesaj gönderilirken hata oluştu. Logları kontrol edin.")

if __name__ == "__main__":
    asyncio.run(main())
