# DMS-Adapter Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/dms/health || exit 1

# Run
EXPOSE 8000
# DS-0002: Nicht-Root-Betrieb. Der Benutzer wird erst hier angelegt, damit alle
# vorherigen Schritte (apt, pip, chmod) noch Root-Rechte haben; anschliessend
# gehoert /app dem Dienstbenutzer, damit Schreibpfade weiter funktionieren.
RUN groupadd --system --gid 1000 appuser     && useradd --system --uid 1000 --gid appuser --no-create-home appuser     && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


