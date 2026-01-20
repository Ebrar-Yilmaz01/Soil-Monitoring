FROM python:3.12-slim
WORKDIR /app


COPY cloud_ingest.py anomaly_detector.py requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "cloud_ingest.py"]
