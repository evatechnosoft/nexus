import requests
import json

URL = "http://192.168.1.186:8900/api/memory/rule--nexus--docker"
HEADERS = {"Content-Type": "application/json"}
CONTENT = """# NEXUS DOCKER & ZIMAOS PROTOCOL

## KRITIK KURALLAR
1. Kullanıcı: dean (SSH Key: ~/.ssh/zimaos_key)
2. Yetki: Tüm sistem ve docker komutları 'sudo' ile çalıştırılmalıdır.
3. Dizin: Root (/) salt-okunurdur. Tüm işlemler '/DATA/AppData/nexus-hub' içinde yapılmalıdır.
4. Config: Her komutun başında şu exportlar bulunmalıdır:
   export DOCKER_CONFIG=/DATA/AppData/docker-config && export NPM_CONFIG_USERCONFIG=/DATA/AppData/npm-config

## DOCKER YÖNETİMİ
- ZimaOS üzerinde 'docker compose' (boşluklu) plugin olarak yoktur. 'docker' ana komutu veya volume mount üzerinden 'restart' tercih edilmelidir.
- Konteyner konfigürasyonları: /DATA/AppData/docker-config"""

data = {"content": CONTENT}
r = requests.put(URL, headers=HEADERS, json=data)
if r.status_code == 200:
    print("Nexus Hub Kuralı (rule--nexus--docker) Başarıyla Güncellendi!")
else:
    print(f"Hata: {r.status_code} - {r.text}")
