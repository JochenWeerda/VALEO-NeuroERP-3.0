# PostgreSQL-Konnektivitätsprobleme in Docker Desktop

## Zusammenfassung der analysierten Probleme

Dieses Dokument dokumentiert die identifizierten technischen Ursachen für die PostgreSQL-Konnektivitätsprobleme im VALEO-NeuroERP-System und bietet Lösungen sowie Präventivmaßnahmen.

---

## 1. Identifizierte Fehlerursachen

### 1.1 Netzwerk-Isolation (KRITISCH)

**Problem:** PostgreSQL-Container und Backend-Container befinden sich in verschiedenen Docker-Netzwerken.

| Container | Netzwerk | IP-Bereich |
|-----------|----------|------------|
| `valeo-neuro-erp-postgres` | `bridge` (Standard) | 172.17.0.0/16 |
| `valeo-neuro-erp-backend` | `valeo-neuro-erp_valeo-network` | 172.20.0.0/16 |

**Auswirkung:** Der Backend-Container kann den Host-Namen `postgres` nicht auflösen, da dieser nur im `valeo-network` definiert ist, aber nicht im `bridge`-Netzwerk.

**Fehlermeldung im Log:**
```
could not translate host name "postgres": Name or service not known
```

### 1.2 Fehlende PostgreSQL-Rolle "valeo_user"

**Problem:** Verbindungsversuche mit nicht existierenden Benutzern.

**Fehlermeldungen im PostgreSQL-Log:**
```
FATAL:  role "valeo_user" does not exist
FATAL:  role "postgres" does not exist
```

**Tatsächlich existierende Rolle:**
```
 Role name | Attributes
-----------|------------
 valeo_dev | Superuser, Create role, Create DB, Replication, Bypass RLS
```

### 1.3 Inkonsistente Standard-Datenbankverbindungen

**Problem:** Mehrere unterschiedliche Standardverbindungsstrings im Code.

| Datei | Standard-DATABASE_URL |
|-------|----------------------|
| `app/core/database_pg.py` | `postgresql://postgres:postgres@localhost:5432/valeo` |
| `app/core/config.py` | `postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp` |
| `docker-compose.yml` | `postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp` |

**Probleme:**
- Falscher Benutzer: `postgres` statt `valeo_dev`
- Falsches Passwort: `postgres` statt `valeo_dev_2024`
- Falsche Datenbank: `valeo` statt `valeo_neuro_erp`
- Falscher Host: `localhost`/`127.0.0.1` statt `postgres` (Docker Service Name)

### 1.4 Fehlende Konfigurationsdateien

**Problem:** docker-compose.yml referenziert nicht existierende Dateien.

```yaml
volumes:
  - ./scripts/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
  - ./scripts/postgres.conf:/etc/postgresql/postgresql.conf:ro
```

Diese Dateien existieren nicht:
- `./scripts/init.sql`
- `./scripts/postgres.conf`

### 1.5 Fehlende Datenbankschemata

**Problem:** Anwendungen erwarten Schemas, die nicht existieren.

**Fehlermeldung:**
```
ERROR:  schema "domain_inventory" does not exist
ERROR:  column "article_name" does not exist
```

---

## 2. Lösungen

### 2.1 Netzwerk-Problem beheben

**Sofortmaßnahme (manuell):**
```bash
# PostgreSQL zum valeonetzwerk hinzufügen
docker network connect valeo-neuro-erp_valeo-network valeo-neuro-erp-postgres
```

**Langfristige Lösung (docker-compose.yml):**
Stellen Sie sicher, dass alle Services im gleichen Netzwerk definiert sind:

```yaml
services:
  postgres:
    networks:
      - valeo-network  # NICHT vergessen!

  backend:
    networks:
      - valeo-network
```

### 2.2 Datenbank-Benutzer und Connection Strings korrigieren

**Option A: Bestehenden Benutzer verwenden (empfohlen)**

Verwenden Sie `valeo_dev` in allen Konfigurationen:

```python
# app/core/database_pg.py - Korrigiert
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp"
)
```

**Option B: Fehlende Benutzer erstellen**

```sql
-- Erstellt fehlende Rollen (nur für Entwicklung)
CREATE ROLE valeo_user WITH LOGIN PASSWORD 'valeo_user_2024';
CREATE ROLE postgres WITH LOGIN PASSWORD 'postgres' SUPERUSER;
```

### 2.3 Konfigurationsdateien erstellen

**scripts/postgres.conf:**
```properties
# Minimal-Konfiguration für Entwicklung
max_connections = 100
shared_buffers = 128MB
dynamic_shared_memory_type = posix
listen_addresses = '*'
port = 5432
```

**scripts/init.sql:**
```sql
-- Initiales Setup (falls benötigt)
-- WICHTIG: POSTGRES_USER und POSTGRES_DB werden bereits durch 
-- docker-compose Umgebungsvariablen erstellt
```

### 2.4 Erforderliche Schemas erstellen

```sql
-- Schema für Inventory-Service
CREATE SCHEMA IF NOT EXISTS domain_inventory;

-- Rechte für valeo_dev
GRANT ALL ON SCHEMA domain_inventory TO valeo_dev;
```

---

## 3. Diagnoseschritte

### 3.1 Container-Status prüfen

```bash
# Alle VALEO-Container anzeigen
docker ps -a --filter "name=valeo"

# Container-Netzwerke prüfen
docker inspect valeo-neuro-erp-postgres --format "{{json .NetworkSettings.Networks}}"
docker inspect valeo-neuro-erp-backend --format "{{json .NetworkSettings.Networks}}"
```

### 3.2 Netzwerk-Konnektivität testen

```bash
# Von Backend zu PostgreSQL pingen
docker exec valeo-neuro-erp-backend ping -c 3 postgres

# PostgreSQL-Port von extern prüfen
docker exec valeo-neuro-erp-backend nc -zv postgres 5432
```

### 3.3 Datenbank-Verbindung testen

```bash
# Interne Verbindung (aus PostgreSQL-Container)
docker exec valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp -c "SELECT 1"

# Externe Verbindung (von Host)
psql -h localhost -p 5432 -U valeo_dev -d valeo_neuro_erp -c "SELECT 1"
```

### 3.4 PostgreSQL-Logs analysieren

```bash
# Authentifizierungsfehler finden
docker logs valeo-neuro-erp-postgres 2>&1 | grep -i "FATAL\|ERROR"

# Letzte 50 Einträge
docker logs valeo-neuro-erp-postgres --tail 50
```

### 3.5 Rollen und Datenbanken prüfen

```bash
# Verfügbare Rollen
docker exec valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp -c "\du"

# Verfügbare Datenbanken
docker exec valeo-neuro-erp-postgres psql -U valeo_dev -d valeo_neuro_erp -c "\l"
```

---

## 4. Präventivmaßnahmen

### 4.1 Docker Compose Best Practices

1. **Immer explizite Netzwerke definieren:**
   ```yaml
   networks:
     valeo-network:
       driver: bridge
   ```

2. **Service-Namen konsistent verwenden:**
   - Host: `postgres` (nicht `db`, `database` oder `127.0.0.1`)
   - Rolle: `valeo_dev` (nicht `postgres` oder `valeo_user`)
   - Datenbank: `valeo_neuro_erp`

3. **Gesundheitschecks für alle DB-abhängigen Services:**
   ```yaml
   depends_on:
     postgres:
       condition: service_healthy
   ```

### 4.2 Environment-Variablen konsolidieren

Erstellen Sie eine zentrale `.env`-Datei:

```bash
# Database
POSTGRES_USER=valeo_dev
POSTGRES_PASSWORD=valeo_dev_2024
POSTGRES_DB=valeo_neuro_erp

# Application (muss mit POSTGRES_* übereinstimmen)
DATABASE_URL=postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp
```

### 4.3 Monitoring und Alerting

1. **Regelmäßige Konnektivitätsprüfungen:**
   ```bash
   # Health-Check-Skript
   docker exec valeo-neuro-erp-postgres pg_isready -U valeo_dev -d valeo_neuro_erp
   ```

2. **Log-Überwachung für Auth-Fehler:**
   ```bash
   docker logs valeo-neuro-erp-postgres 2>&1 | grep -i "FATAL" | tail -5
   ```

### 4.4 Dokumentation

- Aktualisieren Sie bei Änderungen an der DB-Konfiguration dieses Dokument
- Versionieren Sie Konfigurationsdateien
- Dokumentieren Sie alle nicht-standardmäßigen Einstellungen

---

## 5. Schnellfix-Skript

Führen Sie folgende Befehle aus, um die kritischsten Probleme sofort zu beheben:

```bash
# 1. Netzwerk verbinden
docker network connect valeo-neuro-erp_valeo-network valeo-neuro-erp-postgres

# 2. Container neu starten
docker restart valeo-neuro-erp-postgres valeo-neuro-erp-backend

# 3. Verbindung verifizieren
docker exec valeo-neuro-erp-backend nc -zv postgres 5432

# 4. Datenbank-Verbindung testen
docker exec valeo-neuro-erp-backend python -c "
import psycopg2
conn = psycopg2.connect('postgresql://valeo_dev:valeo_dev_2024@postgres:5432/valeo_neuro_erp')
print('Verbindung erfolgreich!')
conn.close()
"
```

---

## 6. Wartungsaufgaben

### Täglich
- [ ] Container-Status prüfen (`docker ps`)
- [ ] Health-Checks verifizieren

### Wöchentlich
- [ ] Datenbank-Backups testen
- [ ] Log-Dateien auf Fehler analysieren
- [ ] Ungenutzte Images bereinigen

### Monatlich
- [ ] PostgreSQL-Version auf Updates prüfen
- [ ] Performance-Metriken analysieren
- [ ] Dokumentation aktualisieren

---

*Zuletzt aktualisiert: 2026-02-20*
*Erstellt von: VALEO NeuroERP Orchestrator*
