FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Çevre değişkenleri
ENV APP_PORT=4700
ENV OLLAMA_URL=http://host.docker.internal:11434
ENV NEXUS_HUB_URL=http://192.168.1.186:4500/ops

EXPOSE 4700

CMD ["python", "main.py"]
