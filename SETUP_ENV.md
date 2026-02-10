***REMOVED*** Environment Setup

***REMOVED******REMOVED*** Datenbank: PostgreSQL (erforderlich)

VALEO-NeuroERP nutzt ausschließlich **PostgreSQL**. SQLite wird nicht unterstützt.

***REMOVED******REMOVED******REMOVED*** Umgebungsvariable setzen

Erstellen Sie eine `.env` Datei im Projektverzeichnis:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/valeo_neuro_erp
```

***REMOVED******REMOVED******REMOVED*** PostgreSQL via Docker

```powershell
***REMOVED*** Docker-Compose starten
docker-compose up -d postgres

***REMOVED*** Environment Variable setzen (oder in .env)
$env:DATABASE_URL = "postgresql://USER:PASSWORD@localhost:5432/valeo_neuro_erp"

***REMOVED*** Migrationen ausführen
python scripts/run_migrations.py

***REMOVED*** Server starten
python main.py
```

***REMOVED******REMOVED******REMOVED*** Migrationen

```powershell
python scripts/run_migrations.py
```

***REMOVED******REMOVED*** Server neu starten

```powershell
python main.py
```
