FROM python:3.11-slim

WORKDIR /app

# System dependencies for AI/ML
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY services/ai/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# auth_shared ist keine Bequemlichkeit, sondern Voraussetzung: main.py bricht
# ohne dieses Paket bewusst ab (SILENT-FAILURE-20260914). Frueher fehlte es im
# Image, und der Dienst lief stillschweigend ohne Authentifizierung.
COPY packages/auth-shared /opt/auth-shared
RUN pip install --no-cache-dir /opt/auth-shared

# Application code
COPY services/ai/app/ ./app/
COPY services/ai/main.py ./

# Create data directory for ChromaDB
RUN mkdir -p /app/data/chroma

# Environment
ENV PYTHONUNBUFFERED=1

# Expose ports (REST API + MCP Server)
EXPOSE 5000 5001

# Run
# DS-0002: Nicht-Root-Betrieb. Der Benutzer wird erst hier angelegt, damit alle
# vorherigen Schritte (apt, pip, chmod) noch Root-Rechte haben; anschliessend
# gehoert /app dem Dienstbenutzer, damit Schreibpfade weiter funktionieren.
RUN groupadd --system --gid 1000 appuser     && useradd --system --uid 1000 --gid appuser --no-create-home appuser     && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]


