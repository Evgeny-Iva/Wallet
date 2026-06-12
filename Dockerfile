FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY entrypoint.sh .
COPY alembic.ini .
COPY migrations ./migrations

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]