import os
import time
import requests
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Environment Variables
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://192.168.1.186:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "ha-influx-premium-token-2024-v2")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "evatechnosoft")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "homeassistant")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.1.186:4602")

# InfluxDB Client
client = influxdb_client.InfluxDBClient(
    url=INFLUXDB_URL,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG
)
write_api = client.write_api(write_options=SYNCHRONOUS)

def get_ollama_stats():
    """Ollama API'sinden anlık durum (tags/ps) bilgisini alır."""
    try:
        # ps endpoint'i çalışan modelleri ve kullanımlarını gösterir
        response = requests.get(f"{OLLAMA_HOST}/api/ps")
        if response.status_code == 200:
            return response.json().get('models', [])
        return []
    except Exception as e:
        print(f"Ollama API Error: {e}")
        return []

def track_metrics():
    """Sürekli döngüde modellerin performansını izler ve InfluxDB'ye yazar."""
    print("Nexus Monitor starting...")
    while True:
        models = get_ollama_stats()
        for model in models:
            model_name = model.get('name')
            # Not: Ollama /api/ps çıktısında anlık 'eval_count' vermez, 
            # ancak bu modelin 'aktif' olduğunu ve bellekte olduğunu doğrular.
            # Gerçek token hızı her cevapta yakalanmalıdır.
            
            p = influxdb_client.Point("nexus_intelligence") \
                .tag("model", model_name) \
                .field("is_active", 1.0) \
                .field("vram_usage", float(model.get('size', 0))) \
                .time(time.time_ns(), influxdb_client.WritePrecision.NS)
            
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=p)
            print(f"Logged: {model_name}")

        time.sleep(5)  # 5 saniyede bir kontrol et

if __name__ == "__main__":
    track_metrics()
