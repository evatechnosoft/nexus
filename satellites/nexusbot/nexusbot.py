import os
import asyncio
import logging
import httpx
import time
import re
from datetime import datetime
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger("nexusbot")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HUB_URL = os.getenv("HUB_URL", "http://192.168.1.186:8900")
OLLAMA_URL = "http://192.168.1.186:4602/api/generate"
ALERT_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID")

if not TOKEN:
    log.error("TELEGRAM_BOT_TOKEN bulunamadı.")
    exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}"
START_TIME = time.time()

def get_help_menu():
    menu = "<b>🛰 NexusBot v2.3 - Intelligence Terminal</b>\n"
    menu += "───────────────────\n"
    menu += "🏥 /health - Sistem sağlığı ve özet\n"
    menu += "📂 /index - Hafıza dosyaları listesi\n"
    menu += "🤖 /ask [soru] - Akıllı AI sorgusu (RAG)\n"
    menu += "🌐 /fetch [konu] - Web'de araştır ve öğren\n"
    menu += "📊 /status - Teknik metrikler\n"
    menu += "❓ /help - Yardım menüsü\n"
    menu += "───────────────────\n"
    return menu

async def send_msg(chat_id, text, reply_markup=None):
    if not chat_id: return
    if len(text) > 4000: text = text[:4000] + "\n\n<i>...kesildi.</i>"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: payload["reply_markup"] = reply_markup
    async with httpx.AsyncClient() as client:
        try: await client.post(f"{API_URL}/sendMessage", json=payload)
        except Exception as e: log.error(f"Hata: {e}")

async def get_health_report():
    uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - START_TIME))
    async with httpx.AsyncClient() as client:
        try:
            hub_status = "🟢 <b>ONLINE</b>"
            try:
                r = await client.get(f"{HUB_URL}/health", timeout=5)
                if r.status_code != 200: hub_status = "🔴 <b>ERROR</b>"
            except: hub_status = "🔴 <b>OFFLINE</b>"
            r_idx = await client.get(f"{HUB_URL}/api/memory/index", timeout=5)
            files = r_idx.json().get("files", []) if r_idx.status_code == 200 else []
            msg = "<b>🏥 Nexus Health</b>\n───────────────────\n"
            msg += f"🖥 Hub: {hub_status}\n"
            msg += f"🤖 Bot: <code>{uptime}</code>\n"
            msg += f"📂 Memory: <code>{len(files)} files</code>\n"
            return msg
        except Exception as e: return f"❌ Error: {e}"

async def get_index_report():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{HUB_URL}/api/memory/index", timeout=5)
            if r.status_code == 200:
                files = r.json().get("files", [])
                if not files: return "📭 Hub belleği boş."
                msg = "<b>📂 Nexus Memory Index</b>\n───────────────────\n"
                important = []
                for f in files:
                    key = f.get("key", "")
                    important.append(key)
                msg += "<b>🌟 Files:</b>\n" + "\n".join([f"• <code>{k}</code>" for k in sorted(important)[:20]])
                msg += f"\n\n<i>Total: {len(files)} files.</i>"
                return msg
            return "❌ Hub Index ulaşılamadı."
        except Exception as e: return f"❌ Index Error: {e}"

async def fetch_web(chat_id, query):
    await send_msg(chat_id, f"🌐 <b>İşlem Sıraya Alındı:</b> <code>{query}</code>")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{HUB_URL}/api/fetch/update", json={"categories": ["general"], "query": query}, timeout=10)
            if r.status_code == 200:
                job_id = r.json().get("job_id")
                await send_msg(chat_id, f"⏳ <b>İş Başlatıldı:</b> <code>{job_id}</code>\n<i>Bittiğinde sana haber vereceğim.</i>")
                asyncio.create_task(poll_fetch_status(chat_id, job_id))
            else: await send_msg(chat_id, f"❌ <b>Hata:</b> Hub {r.status_code} döndürdü.")
        except Exception as e: await send_msg(chat_id, f"❌ <b>Bağlantı Hatası:</b> {e}")

async def poll_fetch_status(chat_id, job_id):
    async with httpx.AsyncClient() as client:
        for _ in range(30):
            await asyncio.sleep(10)
            try:
                r = await client.get(f"{HUB_URL}/api/fetch/status/{job_id}", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("status") == "completed":
                        added = data.get("skills_added", 0)
                        await send_msg(chat_id, f"✅ <b>İşlem Tamamlandı!</b>\n✨ <b>{added}</b> yeni bilgi Hub belleğine işlendi.")
                        return
                    elif data.get("status") == "failed":
                        await send_msg(chat_id, f"❌ <b>İşlem Başarısız:</b> {job_id}")
                        return
            except: pass
        await send_msg(chat_id, f"⚠️ <b>Zaman Aşımı:</b> {job_id} arka planda devam ediyor.")

async def ai_query(chat_id, prompt):
    await send_msg(chat_id, "🤖 <b>Nexus AI</b> (Memory + Llama) derliyor...")
    async with httpx.AsyncClient() as client:
        try:
            context = ""
            has_memory = False
            try:
                r_search = await client.get(f"{HUB_URL}/api/skills/search", params={"q": prompt}, timeout=10)
                if r_search.status_code == 200:
                    results = r_search.json().get("results", [])
                    if results:
                        has_memory = True
                        context = "\n\n--- HAFIZA KAYITLARI ---\n" + "\n".join([f"Dosya: {res.get('key')}\nİçerik: {res.get('content')[:500]}\n" for res in results[:2]])
            except: pass
            
            if not has_memory:
                system = "Sen Nexus Hub asistanısın. Bu konu hakkında Hub hafızasında (RAG) hiçbir kayıt bulunamadı. Lütfen kullanıcıya bu konunun hafızada olmadığını belirt ve sadece genel bilginle çok kısa bir tahmin yap."
            else:
                system = "Sen Nexus Hub asistanısın. Aşağıdaki hafıza kayıtlarına kesinlikle sadık kalarak cevap ver. Hafıza dışına çıkma."
                
            payload = {"model": "llama3.2:latest", "prompt": f"{system}\n{context}\n\nSoru: {prompt}\nCevap:", "stream": False}
            r = await client.post(OLLAMA_URL, json=payload, timeout=120)
            if r.status_code == 200: await send_msg(chat_id, f"🤖 <b>Nexus AI:</b>\n\n{r.json().get('response', '...')}")
            else: await send_msg(chat_id, "❌ <b>AI Offline</b>")
        except Exception as e: await send_msg(chat_id, f"❌ <b>Hata:</b> {e}")

async def handle_update(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        if text in ["/start", "/help"]: await send_msg(chat_id, get_help_menu())
        elif text == "/health": await send_msg(chat_id, await get_health_report())
        elif text == "/index": await send_msg(chat_id, await get_index_report())
        elif text.startswith("/ask"):
            p = text.replace("/ask", "").strip()
            if p: await ai_query(chat_id, p)
        elif text.startswith("/fetch"):
            q = text.replace("/fetch", "").strip()
            if q: await fetch_web(chat_id, q)

async def main():
    log.info("NexusBot v2.3 başlatılıyor...")
    offset = 0
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Bot açıldığında bekleyen mesajları temizle veya en sonuncudan başla
                r = await client.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 30}, timeout=40)
                if r.status_code == 200:
                    updates = r.json().get("result", [])
                    for update in updates:
                        # Mesajları paralel işle, ana döngüyü bloklama
                        asyncio.create_task(handle_update(update))
                        offset = update["update_id"] + 1
            except Exception as e:
                log.error(f"Polling hatası: {e}")
                await asyncio.sleep(5)
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(main())
