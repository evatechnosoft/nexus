import os
import asyncio
import logging
import imaplib
import email
from email.header import decode_header
import httpx
from bs4 import BeautifulSoup
from parser import parse_email
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger("nexus-email-worker")
HUB_URL = os.getenv("NEXUS_HUB_URL", "http://192.168.1.186:4500")

# Email Ayarları
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com") # Varsayılan Gmail

def clean_html(html_content):
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "lxml")
    for s in soup(["script", "style"]): s.extract()
    return soup.get_text(separator="\n").strip()

async def submit_to_nexus_hub(parsed_data, source="email_worker"):
    """Ayıklanan veriyi ana Hub'a gönderir."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{HUB_URL}/api/requests/create-from-satellite"
            payload = {
                "requester_name": parsed_data.get("name"),
                "requester_email": parsed_data.get("email"),
                "requester_phone": parsed_data.get("phone"),
                "requester_address": parsed_data.get("address"),
                "department_name": parsed_data.get("department"),
                "device_type": parsed_data.get("device_type"),
                "source": source,
                "raw_metadata": parsed_data.get("metadata", {})
            }
            log.info(f"Submitting to Hub: {url}")
            response = await client.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            log.error(f"Hub Submission Failed: {e}")
            return False

async def check_and_process_emails():
    """IMAP üzerinden (Gmail, Outlook vb.) mailleri kontrol eder."""
    if not EMAIL_USER or not EMAIL_PASS:
        log.warning("Email credentials missing in .env. Skipping check.")
        return

    try:
        # IMAP Bağlantısı
        mail = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Okunmamış mailleri ara
        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK": return

        for msg_id in messages[0].split():
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes): subject = subject.decode(encoding or "utf-8")
                    
                    sender = msg.get("From")
                    log.info(f"New Email: {subject} from {sender}")

                    # İçeriği çek
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    # Temizle ve Parse Et
                    clean_text = clean_html(body)
                    parsed_results = parse_email(clean_text)

                    for result in parsed_results:
                        # Metadata ekle
                        result["metadata"] = {
                            "subject": subject,
                            "sender": sender,
                            "received_at": msg.get("Date")
                        }
                        # Hub'a Gönder
                        success = await submit_to_nexus_hub(result)
                        if success:
                            log.info(f"Request created for {result.get('name')}")

        mail.logout()
    except Exception as e:
        log.error(f"IMAP Error: {e}")

if __name__ == "__main__":
    # Test için direkt çalıştırılabilir
    asyncio.run(check_and_process_emails())
