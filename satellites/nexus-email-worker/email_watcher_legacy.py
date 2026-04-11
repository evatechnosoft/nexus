"""
Exchange Mailbox Watcher
========================
Şirket Exchange kutusunu dinler; işe başlama / işten çıkış e-postalarını
süzer, kişi bilgilerini çıkarır, otomatik talep oluşturur ve onay
bildirimi gönderir.

Bağımlılıklar: exchangelib, apscheduler
Env değişkenleri → .env.example dosyasına bakın.
"""

import os
import re
import uuid
import logging
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Any

from sqlalchemy.orm import Session, joinedload

from database import SessionLocal
import models
from email_parser import parse_email
from inventory_score import rank_devices
import notifier
import ms_oauth

log = logging.getLogger(__name__)

# ── Çevre Değişkenleri ────────────────────────────────────────────────────────

EXCHANGE_SERVER = os.getenv("EXCHANGE_SERVER", "")  # boş → autodiscover
EXCHANGE_EMAIL = os.getenv("EXCHANGE_EMAIL", "")
EXCHANGE_USER = os.getenv("EXCHANGE_USER", "") or EXCHANGE_EMAIL
EXCHANGE_PASSWORD = os.getenv("EXCHANGE_PASSWORD", "")
WATCH_INTERVAL_MIN = int(os.getenv("WATCH_INTERVAL_MIN", "5"))


# Filtre anahtar kelimeleri (virgülle ayrılmış)
def _kw(env_key: str, default: str) -> List[str]:
    return [
        k.strip().lower() for k in os.getenv(env_key, default).split(",") if k.strip()
    ]


_ONBOARD_SUBJ_KW = _kw(
    "WATCH_ONBOARD_SUBJECT_KW",
    "işe başlama,yeni personel,onboarding,hoş geldin,yeni üye,başlıyor",
)
_ONBOARD_BODY_KW = _kw(
    "WATCH_ONBOARD_BODY_KW",
    "işe başlama,yeni işe,işe giriş,işe başlıyor,personel,aday",
)
_OFFBOARD_SUBJ_KW = _kw(
    "WATCH_OFFBOARD_SUBJECT_KW",
    "işten çıkış,ayrılış,offboarding,işten ayrılma,veda",
)
_OFFBOARD_BODY_KW = _kw(
    "WATCH_OFFBOARD_BODY_KW",
    "işten çıkış,ayrılıyor,son iş günü,işten ayrılıyor",
)

# Yalnızca bu gönderenlerden gelen mailler dikkate alınır (boş → herkesten)
_SENDER_WHITELIST: List[str] = [
    s.strip().lower()
    for s in os.getenv("WATCH_SENDER_FILTER", "").split(",")
    if s.strip()
]

# Departman → anahtar kelime eşleşmesi
_DEPT_KW = {
    "Yazılımcı": [
        "yazılım",
        "geliştirici",
        "developer",
        "software",
        "mühendis",
        "engineer",
        "r&d",
        "arge",
    ],
    "Recruiter": [
        "recruiter",
        "ik",
        "insan kaynakları",
        "hr",
        "human resource",
        "işe alım",
        "talent",
    ],
    "OS Çalışan": ["saha", "os çalışan", "field", "operasyon", "koçsistem", "os ekibi"],
}


# ── Yardımcı Fonksiyonlar ─────────────────────────────────────────────────────


def _detect_action_type(text: str) -> Optional[str]:
    """'onboarding' | 'offboarding' | None döner."""
    text_lower = text.lower()

    # İşten Çıkış (Hassas)
    for kw in (
        _OFFBOARD_SUBJ_KW
        + _OFFBOARD_BODY_KW
        + ["ayrılış", "istifa", "çıkış işlemi", "ayrılıyor", "veda"]
    ):
        if kw in text_lower:
            return "offboarding"

    # İşe Başlama (Hassas)
    for kw in (
        _ONBOARD_SUBJ_KW
        + _ONBOARD_BODY_KW
        + [
            "yeni ekip",
            "işe başlıyor",
            "personel girişi",
            "kurulum talebi",
            "donanım talebi",
            "yeni çalışan",
            "yeni üye",
        ]
    ):
        if kw in text_lower:
            return "onboarding"

    # Yumuşak Eşleşme (Eğer içinde İsim/E-posta geçiyorsa ve Onboarding emareleri varsa)
    soft_keywords = [
        "isim",
        "soyad",
        "e-posta",
        "laptop",
        "telefon",
        "departman",
        "sicil",
        "kurulum",
    ]
    match_count = sum(1 for kw in soft_keywords if kw in text_lower)
    if match_count >= 2:  # Daha da esnettik (2 yeterli)
        # Belirgin bir 'offboarding' emaresi yoksa onboarding kabul et
        return "onboarding"

    return None


def _detect_department(text: str, db: Session) -> Optional[models.Department]:
    """E-posta metninden departmanı tahmin eder; bulamazsa OS Çalışan döner."""
    text_lower = text.lower()
    for dept_name, keywords in _DEPT_KW.items():
        for kw in keywords:
            if kw in text_lower:
                dept = db.query(models.Department).filter_by(name=dept_name).first()
                if dept:
                    return dept
    # Varsayılan
    return db.query(models.Department).filter_by(name="OS Çalışan").first()


def _preferred_device_type(dept_name: str) -> str:
    """Departmana göre tercih edilen cihaz türünü döner."""
    if dept_name == "Recruiter":
        return models.DeviceType.desktop.value
    return models.DeviceType.laptop.value


def _create_token(
    db: Session,
    request_id: int,
    action: str,
    device_id: Optional[int],
) -> str:
    token = uuid.uuid4().hex
    db.add(
        models.ApprovalToken(
            token=token,
            request_id=request_id,
            action=action,
            suggested_device_id=device_id,
            expires_at=datetime.utcnow() + timedelta(hours=48),
        )
    )
    return token


def _strip_html(html: str) -> str:
    """HTML tag'lerini temizler, tablo hücrelerini pipe (|) ile ayırır."""
    if not html:
        return ""
    import html as html_lib

    # 1. Decode HTML entities (e.g., &nbsp; -> space)
    html = html_lib.unescape(html)

    # 2. Convert table cells to pipes BEFORE stripping tags
    # Handle both </td> and </th> (headers)
    html = re.sub(r"</t[dh]>", " | ", html, flags=re.IGNORECASE)

    # 3. Convert row endings and block elements to newlines
    html = re.sub(r"</(?:tr|p|div|h[1-6])>|<br\s*/?>", "\n", html, flags=re.IGNORECASE)

    # 4. Strip all remaining HTML tags safely
    clean = re.sub(r"<[^>]+>", " ", html)

    # 5. Clean up multiple spaces, standardize pipes, and remove empty lines
    lines = []
    for line in clean.splitlines():
        # Collapse multiple spaces into a single space
        line = re.sub(r"\s+", " ", line).strip()
        # Clean up spacing around pipes
        line = re.sub(r"\s*\|\s*", " | ", line)
        # Strip trailing/leading pipes if they are empty borders
        line = line.strip("| ")
        if line:
            lines.append(line)

    return "\n".join(lines)


# ── Mesaj İşleyici ────────────────────────────────────────────────────────────


def _save_to_queue(msg, db: Session) -> None:
    """Mesajı veritabanındaki kuyruğa kaydeder."""
    message_id = getattr(msg, "message_id", None) or str(
        getattr(msg, "id", uuid.uuid4())
    )

    # Mükerrer kaydı önle
    if db.query(models.EmailQueue).filter_by(message_id=message_id).first():
        return

    # İçerik
    subject = msg.subject or ""
    body_text = ""
    if hasattr(msg, "text_body") and msg.text_body:
        body_text = msg.text_body
    elif hasattr(msg, "body") and msg.body:
        body_text = _strip_html(str(msg.body))

    # Gönderici
    sender_email = ""
    sender_name = ""
    if hasattr(msg, "sender") and msg.sender:
        sender_email = msg.sender.email_address or ""
        sender_name = msg.sender.name or ""

    # Kuyruğa ekle
    item = models.EmailQueue(
        message_id=message_id,
        subject=subject,
        body=body_text,
        sender_email=sender_email.lower(),
        sender_name=sender_name,
        status="pending",
    )
    db.add(item)
    db.commit()
    log.info("Mesaj kuyruğa eklendi: %s", subject)


def _process_email_item(item: models.EmailQueue, db: Session) -> bool:
    """Kuyruktaki tek bir e-postayı işleyip talebe dönüştürür."""
    try:
        subject = item.subject or ""
        body_text = item.body or ""
        sender_email = (item.sender_email or "").lower()
        sender_name = item.sender_name or ""

        full_text_lower = (subject + " " + body_text).lower()

        # Gönderici filtresi
        if _SENDER_WHITELIST and sender_email not in _SENDER_WHITELIST:
            log.info("Kuyruk öğesi gönderen filtresine takıldı: %s", sender_email)
            item.status = "ignored"
            item.error_message = "Whitelist dışı gönderici."
            db.commit()
            return False

        # İşe başlama / işten çıkış tespiti
        action_type = _detect_action_type(full_text_lower)

        # Eğer aksiyon tipi bulunamadıysa ama içerik okunabiliyorsa (Soft Match)
        # parse_email sonucuna göre devam et
        parsed_data = parse_email(f"Konu: {subject}\n{body_text}")

        if not action_type:
            # En azından bir isim veya mail bulunduysa 'onboarding' olarak kabul et
            has_data = (
                any(p.get("name") or p.get("email") for p in parsed_data)
                if parsed_data
                else False
            )

            if has_data:
                action_type = "onboarding"
                log.info(
                    "Soft Match: Aksiyon anahtar kelimesi yok ama veriler bulundu. Onboarding olarak işleniyor."
                )
            else:
                log.info("Kuyruk öğesi süzgece takılmadı: %s", subject)
                item.status = "ignored"
                item.error_message = "Onboarding/Offboarding anahtar kelimesi bulunamadı ve içerik anlaşılamadı."
                db.commit()
                return False

        # Parser'ı tekrar çağırmaya gerek yok, zaten yukarıda çağırdık (Soft Match için)
        # Ama eğer action_type bulunduysa ve henüz parse edilmediyse (yukarıdaki akışa göre hep edilecek)
        data = parsed_data

        if not data and action_type == "onboarding":
            log.warning("İsim bulunamadı, öğe askıya alınıyor: %s", subject)
            item.status = "failed"
            item.error_message = (
                f"E-posta içeriğinden isim çıkarılamadı (Sistem: {action_type})"
            )
            db.commit()
            return False

        for parsed in data:
            name = parsed.get("name") or sender_name or "Bilinmeyen"
            email = parsed.get("email") or sender_email
            phone = parsed.get("phone") or ""
            address = parsed.get("address") or ""
            extracted_dept_name = parsed.get("department")

            if not email:
                continue

            # Departman
            dept = None
            if extracted_dept_name:
                dept = (
                    db.query(models.Department)
                    .filter(models.Department.name.ilike(f"%{extracted_dept_name}%"))
                    .first()
                )
            if not dept:
                dept = _detect_department(body_text, db)
            if not dept:
                continue

            device_type = parsed.get("device_type") or _preferred_device_type(dept.name)

            # Personel bul/oluştur
            person = db.query(models.Person).filter_by(email=email.lower()).first()
            if not person:
                person = models.Person(
                    name=name,
                    email=email.lower(),
                    phone=phone or None,
                    address=address or None,
                )
                db.add(person)
                db.flush()
                person.person_code = f"KSI-{person.id:04d}"
            else:
                if phone:
                    person.phone = phone
                if address:
                    person.address = address

            # Talep oluştur
            prefix = (
                "🤖 [Otomatik·İşe Başlama]"
                if action_type == "onboarding"
                else "🚪 [Otomatik·İşten Çıkış]"
            )
            req = models.Request(
                person_id=person.id,
                requester_name=name,
                requester_email=email.lower(),
                requester_phone=phone or None,
                requester_address=address or None,
                department_id=dept.id,
                device_type=device_type,
                status=models.RequestStatus.pending_approval,
                notes=f"{prefix} Konu: {subject[:200]}",
            )
            db.add(req)
            db.flush()

            # Envanter & Tokenlar (Birden fazla cihaz seçeneği için)
            available = (
                db.query(models.Device)
                .filter_by(status=models.DeviceStatus.in_stock, device_type=device_type)
                .all()
            )
            ranked = rank_devices(available, dept.name)

            # Her cihaz için bir onay tokeni oluştur (İlk 5 cihaz için)
            ranked_with_tokens = []
            for d, s in ranked[:5]:
                t = _create_token(db, req.id, "approve", d.id)
                ranked_with_tokens.append((d, s, t))

            reject_token = _create_token(db, req.id, "reject", None)

            # Kuyruk bağla
            item.request_id = req.id
            item.status = "processed"

            # Bildirim (Zenginleştirilmiş liste ile)
            notifier.notify(
                req, dept.name, reject_token, ranked_with_tokens, action_type
            )
            log.info(
                "Talep oluşturuldu #%d (%s) — %s (Seçenekler gönderildi)",
                req.id,
                action_type,
                name,
            )

        db.commit()
        return True

    except Exception as exc:
        db.rollback()
        log.error("Kuyruk öğesi işleme hatası: %s", exc)
        item.status = "failed"
        item.error_message = str(exc)
        item.retry_count += 1
        db.commit()

        # İlk hatada bilgi ver
        if item.retry_count == 1:
            notifier.send_error_notification(item, str(exc))

        return False


def process_queue() -> None:
    """Kuyruktaki bekleyen e-postaları işler."""
    db = SessionLocal()
    try:
        # pending veya az sayıda başarısız denemesi olanları çek
        pending_items = (
            db.query(models.EmailQueue)
            .filter(
                (models.EmailQueue.status == "pending")
                | (
                    (models.EmailQueue.status == "failed")
                    & (models.EmailQueue.retry_count < 3)
                )
            )
            .order_by(models.EmailQueue.received_at.asc())
            .all()
        )

        if not pending_items:
            return

        log.info("Kuyruk işleniyor: %d öğe bulundu.", len(pending_items))
        for item in pending_items:
            _process_email_item(item, db)

    except Exception as exc:
        log.error("Kuyruk genel işleme hatası: %s", exc)
    finally:
        db.close()


# ── Exchange Bağlantısı ───────────────────────────────────────────────────────


def _get_account():
    """exchangelib Account nesnesi döner."""
    print(f">>> Exchange bağlantısı başlatılıyor: {EXCHANGE_EMAIL}", flush=True)
    try:
        from exchangelib import (
            Configuration,
            OAuth2Credentials,
            Identity,
            Account,
            IMPERSONATION,
            Credentials,
        )

        token = ms_oauth.get_ms_token()
        if token:
            print(">>> Modern Auth (OAuth2) kullanılıyor...", flush=True)
            creds = OAuth2Credentials(
                client_id=os.getenv("AZURE_CLIENT_ID"),
                client_secret=os.getenv("AZURE_CLIENT_SECRET"),
                tenant_id=os.getenv("AZURE_TENANT_ID"),
                access_token={"access_token": token},
                identity=Identity(primary_smtp_address=EXCHANGE_EMAIL),
            )
        else:
            print(">>> Basic Auth (Kullanıcı/Şifre) kullanılıyor...", flush=True)
            creds = Credentials(username=EXCHANGE_USER, password=EXCHANGE_PASSWORD)

        if EXCHANGE_SERVER:
            print(f">>> Sunucu: {EXCHANGE_SERVER}", flush=True)
            config = Configuration(server=EXCHANGE_SERVER, credentials=creds)
            return Account(
                primary_smtp_address=EXCHANGE_EMAIL,
                config=config,
                autodiscover=False,
                access_type=IMPERSONATION,
            )
        else:
            print(">>> Autodiscover...", flush=True)
            return Account(
                primary_smtp_address=EXCHANGE_EMAIL,
                credentials=creds,
                autodiscover=True,
                access_type=IMPERSONATION,
            )
    except Exception as exc:
        log.error("Exchange bağlantı hatası: %s", exc)
        return None


# ── IMAP Bağlantısı (Gmail vb.) ────────────────────────────────────────────────


def _get_imap_connection():
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    email_user = os.getenv("GMAIL_EMAIL") or os.getenv("EXCHANGE_EMAIL")
    email_pass = os.getenv("GMAIL_APP_PASSWORD") or os.getenv("EXCHANGE_PASSWORD")

    if not email_user or not email_pass:
        return None
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        return mail
    except Exception as exc:
        log.error("IMAP bağlantı hatası: %s", exc)
        return None


def _process_imap_message(msg_data: bytes, db: Session) -> None:
    msg = email.message_from_bytes(msg_data)
    subject_header = msg["Subject"] or ""
    decoded_parts = decode_header(subject_header)
    subject = ""
    for part, enc in decoded_parts:
        if isinstance(part, bytes):
            subject += part.decode(enc or "utf-8", errors="ignore")
        else:
            subject += part

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="ignore"
                )
                break
    else:
        body = msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="ignore"
        )

    from_header = msg.get("From", "")
    sender_name, sender_email = email.utils.parseaddr(from_header)

    class MockMsg:
        def __init__(self, s, b, m_id, s_name, s_email):
            self.subject = s
            self.text_body = b
            self.message_id = m_id
            self.sender = type(
                "obj", (object,), {"email_address": s_email, "name": s_name}
            )

    m_id = msg.get("Message-ID") or subject or str(uuid.uuid4())
    _save_to_queue(MockMsg(subject, body, m_id, sender_name, sender_email), db)


# ── Zamanlayıcı Görevi ────────────────────────────────────────────────────────


def check_new_emails() -> None:
    provider = os.getenv("EMAIL_PROVIDER", "exchange").lower()
    if provider == "gmail" or provider == "imap":
        _check_imap_emails()
    else:
        _check_exchange_emails()

    # E-postaları çektikten sonra kuyruğu işle
    process_queue()


def _check_imap_emails() -> None:
    global _last_scan_time
    _last_scan_time = datetime.utcnow()
    mail = _get_imap_connection()
    if not mail:
        return
    db = SessionLocal()
    try:
        mail.select("inbox")
        status, messages = mail.search(None, "UNSEEN")
        if status != "OK":
            return
        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            if status == "OK":
                _process_imap_message(data[0][1], db)
                mail.store(num, "+FLAGS", "\\Seen")
    finally:
        mail.logout()
        db.close()


_last_scan_time: Optional[datetime] = None


def get_last_scan_time() -> Optional[datetime]:
    return _last_scan_time


def _check_exchange_emails() -> None:
    global _last_scan_time
    _last_scan_time = datetime.utcnow()
    account = _get_account()
    if not account:
        return
    db = SessionLocal()
    try:
        from exchangelib import UTC, EWSDateTime

        # 'since' filtresini kaldırıyoruz çünkü sistem kapalıyken gelenlerin kaçmasını istemiyoruz
        # Sadece okunmamış (is_read=False) mesajları son gelenlerden başlayarak çekiyoruz.
        messages = account.inbox.filter(is_read=False).order_by("-datetime_received")[
            :100
        ]

        log.info(
            "Exchange (%s) üzerinde yeni okunmamış mesaj taranıyor...", EXCHANGE_EMAIL
        )
        count = 0
        for msg in messages:
            _save_to_queue(msg, db)
            msg.is_read = True
            msg.save(update_fields=["is_read"])
            count += 1

        if count > 0:
            log.info("%d yeni mesaj kuyruğa eklendi.", count)
    except Exception as exc:
        log.error("Exchange tarama hatası: %s", exc)
    finally:
        db.close()
