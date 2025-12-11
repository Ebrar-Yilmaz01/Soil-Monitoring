FROM python:3.11-slim

WORKDIR /app

# System-Abhängigkeiten (optional, hier minimal gehalten)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten
RUN pip install --no-cache-dir paho-mqtt

# Code und Dataset ins Image kopieren
# Passe die Pfade an deine Struktur an:
# Angenommen:
#   - Dockerfile.iot liegt im selben Ordner wie iot_simulation.py
#   - Crop_recommendation.csv liegt eine Ebene darüber (wie im Code: ../Crop_recommendation.csv)
COPY iot_simulation.py /app/iot_simulation.py
COPY ../Crop_recommendation.csv /Crop_recommendation.csv

# CSV_PATH im Container anpassen:
# Entweder:
#   1) Code auf CSV_PATH = "/Crop_recommendation.csv" ändern
#   oder
#   2) Diese ENV setzen und in Python verwenden
ENV CSV_PATH="/Crop_recommendation.csv"
ENV SEND_INTERVAL=30
ENV BROKER="broker.hivemq.com"
ENV PORT=1883
ENV TOPIC="farm/data"

# Startkommando
CMD ["python", "iot_simulation.py"]