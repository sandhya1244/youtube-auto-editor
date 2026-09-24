FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY apps/worker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/worker/worker.py ./worker.py
COPY apps/api/app ./app

CMD ["celery", "-A", "worker", "worker", "--loglevel=INFO", "--concurrency=1"]
