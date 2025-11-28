FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (inkl. postgresql-client für pg_isready)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Entrypoint für automatische Migrationen
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN sed -i 's/\r$//' ./docker-entrypoint.sh && chmod +x ./docker-entrypoint.sh

# Expose port
EXPOSE 5700

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 5700, timeout=5); conn.request('GET', '/health'); resp=conn.getresponse(); exit(0 if resp.status==200 else 1)"

# Entrypoint führt Migrationen aus und startet dann den Server
ENTRYPOINT ["./docker-entrypoint.sh"]