FROM python:3.12-slim
WORKDIR /app
COPY cloud_ingest.py requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "cloud_ingest.py"]
