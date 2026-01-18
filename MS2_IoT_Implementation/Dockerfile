FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir paho-mqtt

COPY iot_simulation.py /app/iot_simulation.py
COPY Crop_recommendation.csv /app/Crop_recommendation.csv

ENV CSV_PATH="/app/Crop_recommendation.csv"
ENV SEND_INTERVAL=5
ENV BROKER="broker.hivemq.com"
ENV PORT=1883
ENV TOPIC="farm/data"

CMD ["python", "iot_simulation.py"]
