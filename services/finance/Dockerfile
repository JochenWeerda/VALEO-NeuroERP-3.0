FROM python:3.11-slim

WORKDIR /app

COPY services/finance/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/finance/app ./app
COPY services/finance/main.py ./main.py

EXPOSE 8003

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8003/health')"

# DS-0002: Nicht-Root-Betrieb. Der Benutzer wird erst hier angelegt, damit alle
# vorherigen Schritte (apt, pip, chmod) noch Root-Rechte haben; anschliessend
# gehoert /app dem Dienstbenutzer, damit Schreibpfade weiter funktionieren.
RUN groupadd --system --gid 1000 appuser     && useradd --system --uid 1000 --gid appuser --no-create-home appuser     && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]

