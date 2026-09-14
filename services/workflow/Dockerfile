FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Alle Quellpfade sind auf den Wurzelkontext bezogen, weil packages/auth-shared
# ausserhalb des Dienstverzeichnisses liegt. Dieser Dienst steht in keiner
# Compose-Datei, deshalb hier der Bauaufruf:
#   docker build -f services/workflow/Dockerfile .
COPY services/workflow/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# auth_shared ist keine Bequemlichkeit, sondern Voraussetzung: main.py bricht
# ohne dieses Paket bewusst ab (SILENT-FAILURE-20260914). Ohne die Installation
# verweigert der Dienst den Start, statt ohne Authentifizierung zu laufen.
COPY packages/auth-shared /opt/auth-shared
RUN pip install --no-cache-dir /opt/auth-shared

COPY services/workflow/app/ ./app/
COPY services/workflow/main.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 5100

# DS-0002: Nicht-Root-Betrieb. Der Benutzer wird erst hier angelegt, damit alle
# vorherigen Schritte (apt, pip, chmod) noch Root-Rechte haben; anschliessend
# gehoert /app dem Dienstbenutzer, damit Schreibpfade weiter funktionieren.
RUN groupadd --system --gid 1000 appuser     && useradd --system --uid 1000 --gid appuser --no-create-home appuser     && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5100", "--reload"]


