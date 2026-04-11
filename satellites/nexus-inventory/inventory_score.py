"""
Envanter Skoru — departmana göre en uygun cihazı seçer.

Puanlama (0-100):
  40  → stokta mevcut (base)
  +25 → cihaz türü departman kuralıyla eşleşiyor
  +25 → model adı anahtar kelimeyle eşleşiyor
  +10 → tercih edilen marka

Departman → Kural eşleşmesi:
  Yazılımcı  → yüksek spec laptop (Precision, XPS, Latitude 55xx, ThinkPad X1, EliteBook 8xx)
  Recruiter  → masaüstü veya ofis laptopu (OptiPlex, Latitude 3xx/5xx)
  OS Çalışan → DELL Latitude 3530 (standart saha cihazı)
  Varsayılan → DELL Latitude 3530
"""

from typing import List, Tuple

import models

# ── Kural Tablosu ─────────────────────────────────────────────────────────────

_RULES: dict = {
    "Yazılımcı": {
        "types": {models.DeviceType.laptop},
        "model_kw": [
            "precision",
            "xps",
            "latitude 55",
            "latitude 54",
            "thinkpad x1",
            "thinkpad t",
            "elitebook 8",
            "probook 6",
            "macbook pro",
            "zbook",
        ],
        "brand_pref": [],  # herhangi bir marka
    },
    "Recruiter": {
        "types": {models.DeviceType.desktop, models.DeviceType.laptop},
        "model_kw": [
            "optiplex",
            "latitude 3",
            "latitude 5",
            "elitebook 84",
            "probook 4",
            "pavilion",
        ],
        "brand_pref": ["DELL", "HP"],
    },
    "OS Çalışan": {
        "types": {models.DeviceType.laptop},
        "model_kw": ["3530", "latitude 3530", "latitude 35"],
        "brand_pref": ["DELL"],
    },
}

_DEFAULT_RULE: dict = {
    "types": {models.DeviceType.laptop},
    "model_kw": ["3530", "latitude 3530", "latitude 35"],
    "brand_pref": ["DELL"],
}


# ── Skor Hesaplayıcı ─────────────────────────────────────────────────────────


def score_device(device: models.Device, department_name: str) -> int:
    """Bir cihaz için 0-100 arası envanter skoru döner.
    Stokta yoksa 0 döner."""
    if device.status != models.DeviceStatus.in_stock:
        return 0

    rule = _RULES.get(department_name, _DEFAULT_RULE)
    score = 40  # base: stokta

    # Cihaz türü eşleşmesi
    if device.device_type in {t.value for t in rule["types"]}:
        score += 25

    # Model anahtar kelime eşleşmesi (case-insensitive)
    model_lower = (device.model or "").lower()
    for kw in rule["model_kw"]:
        if kw in model_lower:
            score += 25
            break

    # Marka tercihi
    if device.brand in rule["brand_pref"]:
        score += 10

    return min(score, 100)


def rank_devices(
    devices: List[models.Device],
    department_name: str,
) -> List[Tuple[models.Device, int]]:
    """Cihazları skora göre azalan sırada döner: [(device, score), ...]
    Skoru 0 olan (stokta olmayan) cihazlar listeden çıkarılır."""
    scored = [(d, score_device(d, department_name)) for d in devices]
    return sorted(
        [(d, s) for d, s in scored if s > 0],
        key=lambda x: x[1],
        reverse=True,
    )
