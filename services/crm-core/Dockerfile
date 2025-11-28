FROM python:3.11-slim

WORKDIR /app

# Installiere postgresql-client für pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY app ./app
COPY main.py ./main.py
COPY docker-entrypoint.sh ./docker-entrypoint.sh
# Konvertiere Windows-Zeilenumbrüche zu Unix und mache ausführbar
RUN sed -i 's/\r$//' ./docker-entrypoint.sh && chmod +x ./docker-entrypoint.sh

EXPOSE 5600

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 5600, timeout=5); conn.request('GET', '/health'); resp=conn.getresponse(); exit(0 if resp.status==200 else 1)"

# Entrypoint führt Migrationen aus und startet dann den Server
ENTRYPOINT ["./docker-entrypoint.sh"]
