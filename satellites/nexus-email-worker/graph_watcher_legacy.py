# graph_watcher.py
import os
import logging
from O365 import Account
from database import SessionLocal
import models
import email_watcher

log = logging.getLogger(__name__)


def get_graph_account():
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    if not all([client_id, tenant_id, client_secret]):
        log.error("Microsoft Graph için gerekli AZURE_ ayarları eksik.")
        return None

    credentials = (client_id, client_secret)
    account = Account(credentials, auth_flow_type="credentials", tenant_id=tenant_id)

    try:
        if account.authenticate():
            return account
    except Exception as e:
        log.error("Graph API kimlik doğrulama hatası: %s", e)
    return None


def check_new_emails_graph():
    account = get_graph_account()
    if not account:
        return

    update_scan_time()

    target_email = os.getenv("EXCHANGE_EMAIL", "support@findtalent.net")
    log.info("Graph API ile %s posta kutusu taranıyor...", target_email)

    try:
        mailbox = account.mailbox(resource=target_email)
        # Sadece okunmamış mesajları al
        messages = list(mailbox.get_messages(limit=50, query="isRead eq false"))
        log.info("Yeni bulunan mail sayısı: %d", len(messages))

        db = SessionLocal()
        try:
            for msg in messages:
                log.info("Yeni mail kuyruğa alınıyor: %s", msg.subject)

                class MockMsg:
                    def __init__(self, o365_msg):
                        self.subject = o365_msg.subject
                        self.text_body = o365_msg.body_preview or ""
                        if hasattr(o365_msg, "body"):
                            self.text_body = email_watcher._strip_html(o365_msg.body)
                        self.message_id = o365_msg.object_id
                        self.sender = type(
                            "obj",
                            (object,),
                            {
                                "email_address": o365_msg.sender.address,
                                "name": o365_msg.sender.name,
                            },
                        )

                try:
                    mock = MockMsg(msg)
                    email_watcher._save_to_queue(mock, db)
                    # Okundu olarak işaretle
                    msg.mark_as_read()
                except Exception as ex:
                    log.error("Mesaj kuyruğa alınırken hata: %s", ex)

            # Kuyruğa alma bittikten sonra işlemeyi başlat
            email_watcher.process_queue()

        finally:
            db.close()

    except Exception as e:
        log.error("Graph API tarama hatası: %s", e)


_last_scan_time = None


def get_last_scan_time():
    return _last_scan_time


def update_scan_time():
    global _last_scan_time
    from datetime import datetime

    _last_scan_time = datetime.now()
