FROM python:3.11-slim

WORKDIR /app

***REMOVED*** Install system dependencies (inkl. postgresql-client für pg_isready)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

***REMOVED*** Download spaCy model
RUN python -m spacy download en_core_web_sm

***REMOVED*** Copy application code
COPY . .

***REMOVED*** Entrypoint für automatische Migrationen
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN sed -i 's/\r$//' ./docker-entrypoint.sh && chmod +x ./docker-entrypoint.sh

***REMOVED*** Expose port
EXPOSE 6200

***REMOVED*** Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 6200, timeout=5); conn.request('GET', '/health'); resp=conn.getresponse(); exit(0 if resp.status==200 else 1)"

ENTRYPOINT ["./docker-entrypoint.sh"]