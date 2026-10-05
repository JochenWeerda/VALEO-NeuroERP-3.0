FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (inkl. postgresql-client für pg_isready)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
# "spacy download" ist mit dem Pin 3.7.2 nicht mehr benutzbar: die Kompatibilitaets-
# tabelle von spacy-models kennt nur den Schluessel "3.7", nicht "3.7.2". spacy bildet
# daraus eine leere Modellversion und laedt ".../download/-en_core_web_sm/-en_core_web_sm.tar.gz"
# -> HTTP 404, der Image-Build bricht ab. Das Modell wird daher direkt und
# versionsfest installiert; das ist ohnehin reproduzierbarer als der Download-Befehl.
RUN pip install --no-cache-dir \
    https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl

# Copy application code
COPY . .

# Entrypoint für automatische Migrationen
COPY docker-entrypoint.sh ./docker-entrypoint.sh
RUN sed -i 's/\r$//' ./docker-entrypoint.sh && chmod +x ./docker-entrypoint.sh

# Expose port
EXPOSE 6200

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import http.client; conn=http.client.HTTPConnection('localhost', 6200, timeout=5); conn.request('GET', '/health'); resp=conn.getresponse(); exit(0 if resp.status==200 else 1)"

# DS-0002: Nicht-Root-Betrieb. Der Benutzer wird erst hier angelegt, damit alle
# vorherigen Schritte (apt, pip, chmod) noch Root-Rechte haben; anschliessend
# gehoert /app dem Dienstbenutzer, damit Schreibpfade weiter funktionieren.
RUN groupadd --system --gid 1000 appuser     && useradd --system --uid 1000 --gid appuser --no-create-home appuser     && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["./docker-entrypoint.sh"]
