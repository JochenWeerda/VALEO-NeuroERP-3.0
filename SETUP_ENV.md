# Environment Setup

## Datenbank: PostgreSQL (erforderlich)

VALEO-NeuroERP nutzt ausschließlich **PostgreSQL**. SQLite wird nicht unterstützt.

### Umgebungsvariable setzen

Erstellen Sie eine `.env` Datei im Projektverzeichnis:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/valeo_neuro_erp
```

### PostgreSQL via Docker

```powershell
# Docker-Compose starten
docker-compose up -d postgres

# Environment Variable setzen (oder in .env)
$env:DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/valeo_neuro_erp"

# Migrationen ausführen
python scripts/run_migrations.py

# Server starten
python main.py
```

### Migrationen

```powershell
python scripts/run_migrations.py
```

## Server neu starten

```powershell
python main.py
```

