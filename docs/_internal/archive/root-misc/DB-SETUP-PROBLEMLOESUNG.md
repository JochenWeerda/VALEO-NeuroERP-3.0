# Database Setup - Problemlösung

## Problem 1: Port-Konflikt PostgreSQL

### Symptom
```
psycopg2.OperationalError
```
Verbindung zu Port 5432 funktioniert nicht.

### Ursache
- Lokaler Windows-PostgreSQL-Service belegt Port 5432
- Docker PostgreSQL Container kann nicht auf Port 5432 binden

### Lösung

**Option A: Docker auf anderen Port umbiegen (empfohlen)**

```bash
# 1. Container stoppen und entfernen
docker stop valeo-neuro-erp-postgres
docker rm valeo-neuro-erp-postgres

# 2. Container auf Port 5433 neu starten
docker run -d --name valeo-neuro-erp-postgres \
  -e POSTGRES_USER=valeo_dev \
  -e POSTGRES_PASSWORD=valeo_dev_2024 \
  -e POSTGRES_DB=valeo_neuro_erp \
  -p 5433:5432 \
  -v valeo-pgdata:/var/lib/postgresql/data \
  postgres:15-alpine
```

**Option B: Lokalen PostgreSQL Service stoppen**

```powershell
# Service-Name finden
Get-Service -Name *postgres*

# Service stoppen (als Administrator)
Stop-Service -Name <postgres-service> -Force
```

### Konfiguration aktualisieren

```bash
# .env Datei
DATABASE_URL=postgresql://valeo_dev:valeo_dev_2024@localhost:5433/valeo_neuro_erp

# alembic.ini
sqlalchemy.url = postgresql://valeo_dev:valeo_dev_2024@localhost:5433/valeo_neuro_erp
```

---

## Problem 2: Migration Syntax-Fehler

### Symptom
```
SyntaxError: positional argument follows keyword argument
```

### Ursache
In alembic Migrations-Dateien: positional Argumente nach keyword Argumenten

### Lösung

**Datei: add_article_suppliers_documents_20260219.py**

Falsch:
```python
op.create_table(
    'article_suppliers',
    schema='domain_inventory',  # ← Keyword nach positional
    sa.Column('id', sa.String(), nullable=False),
    ...
)
```

Richtig:
```python
op.create_table(
    'article_suppliers',
    sa.Column('id', sa.String(), nullable=False),
    ...
    schema='domain_inventory'  # ← Keyword am Ende
)
```

**Datei: add_gobd_compliance_20260220.py**

Falsch:
```python
op.execute(f\"\"\"
    INSERT INTO ...
""")
```

Richtig:
```python
op.execute(f"""
    INSERT INTO ...
""")
```

**Datei: ops_domain_initial.py**

Falsch:
```python
DO $ BEGIN
    CREATE TYPE ...
END $;
```

Richtig:
```python
DO $$ BEGIN
    CREATE TYPE ...
END $$;
```

ODER:
```python
DO $body$ BEGIN
    CREATE TYPE ...
END $body$;
```

---

## Problem 3: Fehlende Schemas

### Symptom
```
psycopg2.errors.InvalidSchemaName: schema "domain_ops" does not exist
```

### Lösung
Schema vor Tabellen erstellen:

```python
# Am Anfang der upgrade() Funktion
op.execute('CREATE SCHEMA IF NOT EXISTS domain_ops')
```

---

## Problem 4: Migration Chain Fehler

### Symptom
```
KeyError: 'add_weighing_ticket_article_notes_20260219'
```

### Ursache
Falsche down_revision Referenzen

### Lösung

**Revision ID finden:**
```bash
alembic history
```

**down_revision korrigieren in der Migrationsdatei:**

```python
# Falsch:
down_revision = 'add_weighing_ticket_article_notes_20260219'

# Richtig:
down_revision = 'add_wt_article_notes_20260219'
```

---

## Problem 5: Mehrere Migration Heads

### Symptom
```
Multiple head revisions are present for given argument 'head'
```

### Lösung
```bash
# Heads zusammenführen
alembic merge heads -m "merge_all_heads"

# Oder spezifische Migration anwenden
alembic upgrade add_vat_codes_20260220
```

---

## Schnellstart: VAT Codes manuell erstellen

Falls Alembic nicht funktioniert, können die Tabellen direkt per SQL erstellt werden:

```python
import psycopg2

conn = psycopg2.connect('postgresql://valeo_dev:valeo_dev_2024@localhost:5433/valeo_neuro_erp')
conn.autocommit = True
cur = conn.cursor()

# Schema erstellen
cur.execute('CREATE SCHEMA IF NOT EXISTS domain_finance')

# Tabelle erstellen
cur.execute('''
    CREATE TABLE IF NOT EXISTS domain_finance.vat_codes (
        id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
        code VARCHAR(10) NOT NULL UNIQUE,
        name VARCHAR(200) NOT NULL,
        rate DECIMAL(5, 2) NOT NULL,
        category VARCHAR(50) NOT NULL,
        description TEXT,
        legal_reference VARCHAR(200),
        is_active BOOLEAN DEFAULT TRUE,
        is_default BOOLEAN DEFAULT FALSE,
        tenant_id VARCHAR(36) NOT NULL DEFAULT 'default-tenant',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_by VARCHAR(100),
        updated_at TIMESTAMP WITH TIME ZONE,
        updated_by VARCHAR(100)
    )
''')

print("Tabelle erstellt!")

conn.close()
```

---

## Docker Container Management

```bash
# Container Status prüfen
docker ps -a | findstr postgres

# Logs anzeigen
docker logs valeo-neuro-erp-postgres

# In Container verbinden
docker exec -it valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp

# Container neu starten
docker restart valeo-neuro-erp-postgres

# Daten persistieren (Volume)
docker volume ls | findstr valeo
```
