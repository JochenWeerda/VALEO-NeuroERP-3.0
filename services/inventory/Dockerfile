FROM python:3.11-slim

WORKDIR /app

# Installiere postgresql-client für pg_isready
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY main.py ./main.py
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic/

# Optional: set PYTHONPATH so Alembic env can import app.*
ENV PYTHONPATH=/app

# Entrypoint runs migrations before starting API
COPY --chown=root:root docker-entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 5400

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 5400, timeout=5); conn.request('GET', '/health'); resp=conn.getresponse(); exit(0 if resp.status==200 else 1)"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5400"]

