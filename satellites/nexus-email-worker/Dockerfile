FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıkları (lxml vb. için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Çevre değişkenleri
ENV WATCH_INTERVAL_MIN=5
ENV LOG_LEVEL=INFO
ENV NEXUS_HUB_URL=http://192.168.1.186:4500

CMD ["python", "main.py"]
