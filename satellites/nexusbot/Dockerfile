FROM python:3.11-slim

WORKDIR /app

# Bağımlılıkları kur
RUN pip install --no-cache-dir httpx python-dotenv

# Bot kodunu ve .env dosyasını kopyala
# Not: docker-compose üzerinden mount edileceği için burası boş kalabilir 
# veya direkt kopyalanabilir. Güvenli olması için kopyalıyoruz.
COPY .env .env
COPY satellites/nexusbot/nexusbot.py satellites/nexusbot/nexusbot.py

# Çalıştırma komutu
CMD ["python", "satellites/nexusbot/nexusbot.py"]
