"""
Email metni → kişisel bilgi çıkarıcı.

Desteklenen formatlar:
  1. Etiketli (Anahtar: Değer):
     İsim: Ali Veli
     E-posta: ali@firma.com
  2. Tablo / Satır (Başlık -> Veri):
     Ad Soyad | E-posta | Telefon
     Ali Veli | ali@... | 0532...
"""

import re
from typing import Optional, List, Dict

# ── Regex Kalıpları ──────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

_PHONE_RE = re.compile(
    r"(?:\+90[\s\-]?)?(?:0)?(?:5\d{2})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
    r"|(?:\+90[\s\-]?)?\d{10,11}"
)

# Harici tutulacak gönderen etiketleri
_EXCLUDE_LABELS = ["gönderen", "kimden", "from", "sender", "hi", "merhaba", "sayın"]

# Etiket → alan eşleştirmesi  (Türkçe & İngilizce)
_LABEL_PATTERNS = {
    "name": re.compile(
        r"(?:\bad[\s\-]*soyad[ı]?\b|\bisim\b|\btam[\s\-]*ad[ı]?\b|\bfull[\s\-]*name\b|\bname\b)\s*[:\-]?\s*([A-ZÇĞİÖŞÜa-zçğıöşü]{2,}(?:\s+[A-ZÇĞİÖŞÜa-zçğıöşü]{2,}){0,3})(?!\s*[:@])",
        re.IGNORECASE,
    ),
    "email": re.compile(
        r"(?:\be[\s\-]*posta\b|\be[\s\-]*mail\b|\bmail\b|\bemail\b)\s*[:\-]?\s*([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
        re.IGNORECASE,
    ),
    "phone": re.compile(
        r"(?:\btelefon\b|\btel\b|\bgsm\b|\bcep\b|\bphone\b|\bmobile\b)\s*[:\-]?\s*(\+?[0-9\s\-]{10,20})",
        re.IGNORECASE,
    ),
    "address": re.compile(
        r"(?:adres|address|teslimat[\s\-]*adresi)\s*[:\-]?\s*(.+)",
        re.IGNORECASE,
    ),
}

# Cihaz türü ipucu
_DEVICE_HINTS = {
    "Telefon": re.compile(r"\b(telefon|phone|gsm|mobile|cep)\b", re.IGNORECASE),
    "Laptop": re.compile(
        r"\b(laptop|dizüstü|notebook|bilgisayar|computer)\b", re.IGNORECASE
    ),
    "Tablet": re.compile(r"\b(tablet|ipad)\b", re.IGNORECASE),
}

_NEED_YES_RE = re.compile(
    r"(telefon|laptop|tablet)[^\n]*\b(evet|var|yes|gerekli)\b", re.IGNORECASE
)
_NEED_LABEL_RE = re.compile(r"(?:ihtiyaç|need|cihaz)\s*[:\-]\s*(.+)", re.IGNORECASE)


def parse_email(raw_text: str) -> List[dict]:
    """
    Ham email metnini parse ederek kişisel bilgileri ve cihaz türünü çıkarır.
    Satır bazlı (tablo) formatları da destekler ve birden fazla kişi bulabilir.
    """
    results: List[dict] = []
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]

    # 1. Tablo / Satır Formatı Tespiti
    header_idx = -1
    for i, line in enumerate(lines):
        line_lower = line.lower()
        matches = 0
        if any(k in line_lower for k in ["ad soyad", "isim", "name"]):
            matches += 1
        if any(k in line_lower for k in ["mail", "posta"]):
            matches += 1
        if any(k in line_lower for k in ["tel", "gsm", "telefon", "phone"]):
            matches += 1

        if matches >= 2:
            header_idx = i
            break

    if header_idx != -1:
        header_line = lines[header_idx]
        # En iyi ayırıcıyı bul
        found_delim = None
        for d in ["|", "\t", ";"]:
            if d in header_line:
                found_delim = d
                break

        header_parts = []
        if found_delim:
            header_parts = [p.strip() for p in header_line.split(found_delim)]
        else:
            # Çoklu boşluklara bak
            header_parts = [
                p.strip() for p in re.split(r"\s{2,}", header_line) if p.strip()
            ]

        # Veri satırlarını işle (header_idx+1'den sonuna kadar veya boş satıra kadar)
        for j in range(header_idx + 1, len(lines)):
            data_line = lines[j]
            data_parts = []
            if found_delim:
                data_parts = [p.strip() for p in data_line.split(found_delim)]
            else:
                data_parts = [
                    p.strip() for p in re.split(r"\s{2,}", data_line) if p.strip()
                ]

            # Eğer veri satırı header ile benzer sayıda parça içermiyorsa veya bariz başka bir başlıksa dur
            if len(data_parts) < 2 and len(header_parts) > 1:
                continue
            if any(k in data_line.lower() for k in ["konu:", "gönderen:", "tarih:"]):
                break

            row_result = {
                "name": None,
                "email": None,
                "phone": None,
                "address": None,
                "department": None,
                "device_type": None,
                "confidence": "table",
            }

            max_idx = min(len(header_parts), len(data_parts))
            for k in range(max_idx):
                h = header_parts[k]
                d = data_parts[k]
                h_low = h.lower()

                if any(kw in h_low for kw in ["ad soyad", "tam ad", "isim", "name"]):
                    row_result["name"] = d
                elif any(kw in h_low for hack in ["mail", "posta"] for kw in [hack]):
                    row_result["email"] = d
                elif any(kw in h_low for kw in ["tel", "gsm", "telefon", "phone"]):
                    row_result["phone"] = d
                elif any(kw in h_low for kw in ["adres", "address"]):
                    row_result["address"] = d
                elif any(
                    kw in h_low for kw in ["departman", "bölüm", "birim", "dept", "job"]
                ):
                    row_result["department"] = d

            if row_result["name"] or row_result["email"]:
                results.append(row_result)

    # 2. Eğer tablo bulunamazsa veya eksikse Etiket bazlı (Label) fallback
    if not results:
        label_result = {
            "name": None,
            "email": None,
            "phone": None,
            "address": None,
            "department": None,
            "device_type": None,
            "confidence": "label",
        }
        for line in lines:
            line_lower = line.lower()
            is_sender_line = any(line_lower.startswith(ex) for ex in _EXCLUDE_LABELS)

            for field, pattern in _LABEL_PATTERNS.items():
                if label_result.get(field):
                    continue
                if field == "name" and is_sender_line:
                    continue

                m = pattern.search(line)
                if m:
                    label_result[field] = m.group(1).strip()

        if label_result["name"] or label_result["email"]:
            results.append(label_result)

    # 3. Fallbacks & Cleaning (Tüm sonuçlar için)
    for res in results:
        # Email Temizliği
        if res["email"]:
            m2 = _EMAIL_RE.search(res["email"])
            if m2:
                res["email"] = m2.group(0)
        else:
            # Fallback regex email search
            m_fail = _EMAIL_RE.search(raw_text)
            if m_fail:
                res["email"] = m_fail.group(0)

        # Phone Regex Fallback
        if not res["phone"]:
            m_ph = _PHONE_RE.search(raw_text)
            if m_ph:
                res["phone"] = re.sub(r"[\s\-]", "", m_ph.group(0))

        # Cihaz Türü Tespiti
        for dtype, hint_re in _DEVICE_HINTS.items():
            if hint_re.search(raw_text):
                res["device_type"] = dtype
                break

    return results
