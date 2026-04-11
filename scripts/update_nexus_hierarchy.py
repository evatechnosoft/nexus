import requests
import json

BASE_URL = "http://192.168.1.186:8900/api/memory/"
HEADERS = {"Content-Type": "application/json"}

# 1. rule--nexus--pip
PIP_CONTENT = """---
rule_type: environment_config
context: python_pip
---
# PYTHON PIP PROTOCOL (ZIMAOS)
- User: dean (sudo required)
- Config: export PIP_CONFIG_FILE=/DATA/AppData/pip-config/pip.conf
- Cache: export PIP_CACHE_DIR=/DATA/AppData/pip-cache
- Base: export PYTHONUSERBASE=/DATA/AppData/python-userbase
- Note: Always use --user or the defined paths to avoid read-only filesystem errors."""

# 2. rule--nexus--npm
NPM_CONTENT = """---
rule_type: environment_config
context: node_npm
---
# NPM PROTOCOL (ZIMAOS)
- User: dean (sudo required)
- Config: export NPM_CONFIG_USERCONFIG=/DATA/AppData/npm-config
- Prefix: export NPM_CONFIG_PREFIX=/DATA/AppData/npm-global
- Note: Node modules must live in /DATA/AppData to persist and stay writable."""

# 3. rule--nexus--master (The Pointer)
MASTER_CONTENT = """---
extends:
  - rule--nexus--docker
  - rule--nexus--pip
  - rule--nexus--npm
user: dean
privilege: sudo
base_path: /DATA/AppData/nexus-hub
---
# NEXUS MASTER PROTOCOL (ZIMAOS)
Bu kural, ZimaOS (192.168.1.186) üzerindeki tüm operasyonlar için ana rehberdir. 
Tüm alt kurallar (Docker, Pip, NPM) bu protokole tabidir.
ROOT (/) dizinine yazma. Sadece /DATA/AppData kullan."""

rules = {
    "rule--nexus--pip": PIP_CONTENT,
    "rule--nexus--npm": NPM_CONTENT,
    "rule--nexus--master": MASTER_CONTENT
}

for name, content in rules.items():
    r = requests.put(BASE_URL + name, headers=HEADERS, json={"content": content})
    if r.status_code == 200:
        print(f"✅ {name} başarıyla güncellendi.")
    else:
        print(f"❌ {name} hata: {r.status_code}")
