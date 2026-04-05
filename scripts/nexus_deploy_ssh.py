import paramiko
import os

hostname = "192.168.1.186"
username = "dean"
password = "Eralp123!"

nexus_monitor_code = """import os, time, requests, influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

INFLUXDB_URL = 'http://192.168.1.186:8086'
INFLUXDB_TOKEN = 'ha-influx-premium-token-2024-v2'
INFLUXDB_ORG = 'evatechnosoft'
INFLUXDB_BUCKET = 'homeassistant'
OLLAMA_HOST = 'http://192.168.1.186:4602'

client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def get_stats():
    try:
        res = requests.get(f'{OLLAMA_HOST}/api/ps')
        return res.json().get('models', []) if res.status_code == 200 else []
    except: return []

while True:
    models = get_stats()
    for m in models:
        p = influxdb_client.Point('nexus_intelligence').tag('model', m.get('name')).field('is_active', 1.0).field('vram_usage', float(m.get('size', 0)))
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)
    time.sleep(5)
"""

docker_compose_code = """services:
  nexus-brain:
    build: .
    container_name: nexus-brain
    ports:
      - "8900:8900"
    volumes:
      - ./data:/app/data
    environment:
      - CHROMA_DATA_DIR=/app/data/chroma
      - OLLAMA_HOST=http://192.168.1.186:4602
      - EMBED_MODEL=nomic-embed-text
      - LLM_MODEL=llama3.2
    restart: unless-stopped

  nexus-monitor:
    image: python:3.11-slim
    container_name: nexus-monitor
    volumes:
      - .:/app
    working_dir: /app
    environment:
      - INFLUXDB_URL=http://192.168.1.186:8086
      - INFLUXDB_TOKEN=ha-influx-premium-token-2024-v2
      - INFLUXDB_ORG=evatechnosoft
      - INFLUXDB_BUCKET=homeassistant
      - OLLAMA_HOST=http://192.168.1.186:4602
    command: /bin/sh -c "pip install requests influxdb-client && python nexus_monitor.py"
    restart: unless-stopped
    depends_on:
      - nexus-brain
"""

def deploy():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password)
        print("Connected to DeanOS successfully.")

        # 1. Nexus Monitor Dosyasını Oluştur
        cmd1 = f"cat << 'EOF' > /DATA/AppData/nexus-brain/nexus_monitor.py\n{nexus_monitor_code}\nEOF"
        ssh.exec_command(cmd1)
        print("Nexus Monitor file created.")

        # 2. Docker Compose Dosyasını Güncelle
        cmd2 = f"cat << 'EOF' > /DATA/AppData/nexus-brain/docker-compose.yml\n{docker_compose_code}\nEOF"
        ssh.exec_command(cmd2)
        print("Docker Compose file updated.")

        # 3. Docker Compose Up
        final_cmd = "export DOCKER_CONFIG=/DATA/AppData/docker-config; cd /DATA/AppData/nexus-brain/; docker compose up -d"
        stdin, stdout, stderr = ssh.exec_command(final_cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        print("Deployment finished.")

        ssh.close()
    except Exception as e:
        print(f"Deployment Error: {e}")

if __name__ == "__main__":
    deploy()
