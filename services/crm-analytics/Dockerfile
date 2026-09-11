FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (inkl. postgresql-client für pg_isready)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
ARG CACHEBUST=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Entrypoint für automatische Migrationen
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN sed -i 's/\r$//' ./docker-entrypoint.sh && chmod +x ./docker-entrypoint.sh

# Expose port
EXPOSE 6000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 6000, timeout=5); conn.request('GET', '/health'); resp=conn.getresponse(); exit(0 if resp.status==200 else 1)"

# DS-0002: Nicht-Root-Betrieb. Der Benutzer wird erst hier angelegt, damit alle
# vorherigen Schritte (apt, pip, chmod) noch Root-Rechte haben; anschliessend
# gehoert /app dem Dienstbenutzer, damit Schreibpfade weiter funktionieren.
RUN groupadd --system --gid 1000 appuser     && useradd --system --uid 1000 --gid appuser --no-create-home appuser     && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["./docker-entrypoint.sh"]
