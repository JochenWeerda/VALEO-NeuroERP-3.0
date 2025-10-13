***REMOVED*** VALEO-NeuroERP Service-Management

**Version:** 3.0.0  
**Letzte Aktualisierung:** 13. Oktober 2025  

---

***REMOVED******REMOVED*** 📋 Übersicht aller Services

| Service | Port | Typ | Required | Status-Command |
|---------|------|-----|----------|----------------|
| **Frontend** | 3000 | Node | ✅ JA | `http://localhost:3000` |
| **Backend** | 8000 | Python | ✅ JA | `http://localhost:8000/health` |
| **PostgreSQL** | 5432 | Docker | ✅ JA | `docker exec valeo-postgres pg_isready` |
| **Redis** | 6379 | Docker | ⚪ Optional | `docker exec valeo-redis redis-cli ping` |
| **NATS** | 4222 + 8222 | Docker | ⚪ Optional | `curl http://localhost:8222/healthz` |
| **Keycloak** | 8080 | Docker | ⚪ Optional | `curl http://localhost:8080/health/ready` |
| **Prometheus** | 9090 | Docker | ⚪ Optional | `curl http://localhost:9090/-/healthy` |
| **Grafana** | 3001 | Docker | ⚪ Optional | `curl http://localhost:3001/api/health` |
| **Loki** | 3100 | Docker | ⚪ Optional | `curl http://localhost:3100/ready` |

---

***REMOVED******REMOVED*** 🚀 Quick Start (Lokale Entwicklung)

***REMOVED******REMOVED******REMOVED*** Minimal-Setup (nur Testing):
```powershell
***REMOVED*** 1. Service-Manager-Status-Check
python scripts/service_manager.py status

***REMOVED*** 2. Alte Prozesse aufräumen
python scripts/service_manager.py cleanup

***REMOVED*** 3. Minimal-Stack starten (nur required services)
python scripts/service_manager.py start

***REMOVED*** 4. Backend starten (manuell)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

***REMOVED*** 5. Frontend starten (manuell, separates Terminal)
cd packages/frontend-web
pnpm vite

***REMOVED*** 6. Browser öffnen
***REMOVED*** http://localhost:3000
```

---

***REMOVED******REMOVED*** 🔧 Häufige Probleme & Lösungen

***REMOVED******REMOVED******REMOVED*** Problem 1: Port bereits belegt

**Symptom:**
```
Error: listen EADDRINUSE: address already in use :::3000
ERROR: [Errno 48] Address already in use
```

**Lösung:**
```powershell
***REMOVED*** Option A: Automatisches Cleanup
python scripts/service_manager.py cleanup

***REMOVED*** Option B: Manuelles Cleanup
***REMOVED*** Finde Prozess auf Port
netstat -ano | findstr ":3000"
***REMOVED*** Stoppe Prozess
Stop-Process -Id <PID> -Force

***REMOVED*** Option C: Alle Node/Python-Prozesse stoppen
Get-Process python,node -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

***REMOVED******REMOVED******REMOVED*** Problem 2: Backend startet nicht (PostgreSQL-Verbindung)

**Symptom:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
ERROR: Application startup failed. Exiting.
```

**Ursachen:**
1. ❌ PostgreSQL-Container läuft nicht
2. ❌ Falsche Credentials in `app/core/config.py`
3. ❌ Schemas fehlen in der Datenbank
4. ❌ Windows kann nicht zu Docker-PostgreSQL verbinden

**Lösung:**
```powershell
***REMOVED*** 1. Prüfe Container
docker ps | findstr postgres

***REMOVED*** 2. Starte Container falls nötig
docker start valeo-postgres

***REMOVED*** 3. Prüfe Schemas
docker exec valeo-postgres psql -U valeo -d valeo_neuro_erp -c "\dn"

***REMOVED*** 4. Erstelle Schemas falls fehlend
docker exec valeo-postgres psql -U valeo -d valeo_neuro_erp -c "
  CREATE SCHEMA IF NOT EXISTS domain_shared;
  CREATE SCHEMA IF NOT EXISTS domain_crm;
  CREATE SCHEMA IF NOT EXISTS domain_inventory;
  CREATE SCHEMA IF NOT EXISTS domain_erp;
"

***REMOVED*** 5. Prüfe Credentials in app/core/config.py
***REMOVED*** DATABASE_URL muss match en mit Docker-Container:
***REMOVED*** User: valeo
***REMOVED*** Password: valeo_secure_password_2025 (aus .env)
***REMOVED*** Database: valeo_neuro_erp
```

**Wichtig:** Auf Windows kann psycopg2 manchmal nicht zu Docker-PostgreSQL verbinden.  
**Workaround:** Backend akzeptiert DB-Fehler und startet trotzdem (Testing-Modus in `app/core/database.py`)

---

***REMOVED******REMOVED******REMOVED*** Problem 3: Frontend zeigt keine Daten (CORS-Fehler)

**Symptom:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Lösung:**
```python
***REMOVED*** In app/core/config.py:
BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
    "http://localhost:3000",  ***REMOVED*** ← Frontend-Port muss hier sein!
    "http://localhost:5173",
]
```

**Nach Änderung:** Uvicorn lädt automatisch neu (--reload)

---

***REMOVED******REMOVED******REMOVED*** Problem 4: Docker-Container "unhealthy"

**Symptom:**
```
valeo-keycloak: Up 5 minutes (unhealthy)
valeo-nats: Up 2 minutes (unhealthy)
```

**Lösung:**
```bash
***REMOVED*** A. Container-Logs prüfen
docker logs valeo-keycloak --tail=50

***REMOVED*** B. Healthcheck-Konfiguration prüfen
docker inspect valeo-keycloak --format='{{json .State.Health}}'

***REMOVED*** C. Container neu starten
docker restart valeo-keycloak

***REMOVED*** D. Falls Healthcheck fehlerhaft: Fix in docker-compose.production.yml
```

**Bekannte Fixes:**
- **NATS:** Braucht `--http_port=8222` für Healthcheck
- **Keycloak:** Braucht 90-120s Start-Zeit, `start_period: 120s`

---

***REMOVED******REMOVED*** 📚 Service-Manager Commands

```bash
***REMOVED*** Status aller Services anzeigen
python scripts/service_manager.py status

***REMOVED*** Alle Ports aufräumen (alte Prozesse stoppen)
python scripts/service_manager.py cleanup

***REMOVED*** Minimal-Stack für Testing starten
python scripts/service_manager.py start

***REMOVED*** Health-Checks durchführen
python scripts/service_manager.py health

***REMOVED*** Alle Services stoppen
python scripts/service_manager.py stop-all
```

---

***REMOVED******REMOVED*** 🔄 Typischer Workflow

***REMOVED******REMOVED******REMOVED*** Morgens / Neustart:

```powershell
***REMOVED*** 1. System-Status prüfen
python scripts/startup_check.py

***REMOVED*** 2. Alte Services aufräumen
python scripts/service_manager.py cleanup

***REMOVED*** 3. Docker-Services starten
docker-compose -f docker-compose.production.yml up -d postgres redis nats

***REMOVED*** 4. Backend starten
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

***REMOVED*** 5. Frontend starten (separates Terminal)
cd packages/frontend-web && pnpm vite
```

***REMOVED******REMOVED******REMOVED*** Abends / Herunterfahren:

```powershell
***REMOVED*** Option A: Alles stoppen (inkl. Docker)
python scripts/service_manager.py stop-all

***REMOVED*** Option B: Nur lokale Prozesse stoppen (Docker läuft weiter)
Get-Process python,node -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

***REMOVED******REMOVED*** 🎯 Service-Dependencies

```mermaid
graph TD
    A[PostgreSQL] --> B[Backend]
    C[Redis] -.-> B
    D[NATS] -.-> B
    B --> E[Frontend]
    F[Keycloak] -.-> B
```

**Legende:**
- Durchgezogene Linie: Hard Dependency (muss laufen)
- Gestrichelte Linie: Soft Dependency (optional)

---

***REMOVED******REMOVED*** ⚙️ Konfigurationsdateien

| Datei | Zweck |
|-------|-------|
| `config/services.yml` | Zentrale Service-Definitionen |
| `.env` | Environment-Variablen für Docker |
| `app/core/config.py` | Backend-Konfiguration (Ports, DB-URL, CORS) |
| `docker-compose.production.yml` | Docker-Stack-Definition |
| `package.json` (Frontend) | Frontend-Scripts und Port-Konfiguration |

---

***REMOVED******REMOVED*** 🐛 Debugging-Checkliste

Bei Problemen der Reihe nach prüfen:

- [ ] **1. Ports frei?** `python scripts/service_manager.py status`
- [ ] **2. Docker läuft?** `docker ps`
- [ ] **3. PostgreSQL erreichbar?** `docker exec valeo-postgres psql -U valeo -d valeo_neuro_erp -c "SELECT 1;"`
- [ ] **4. Schemas existieren?** `docker exec valeo-postgres psql -U valeo -d valeo_neuro_erp -c "\dn"`
- [ ] **5. Backend-Health-Check?** `curl http://localhost:8000/health`
- [ ] **6. Frontend-Health-Check?** `curl http://localhost:3000`
- [ ] **7. CORS korrekt?** Prüfe Browser-Console für CORS-Errors
- [ ] **8. Logs prüfen:** Backend-Terminal, Frontend-Terminal, Docker-Logs

---

***REMOVED******REMOVED*** 📊 Installation vs. Produktiv

Das System erkennt automatisch ob es sich in der **Installation** oder **Produktiv**-Phase befindet:

***REMOVED******REMOVED******REMOVED*** Installation-Phase:
- **Marker:** `.installation_complete` fehlt
- **Verhalten:** 
  - Erstellt fehlende Schemas
  - Erstellt Tabellen beim ersten Backend-Start
  - Führt Seed-Scripts aus

***REMOVED******REMOVED******REMOVED*** Produktiv-Phase:
- **Marker:** `.installation_complete` existiert
- **Verhalten:**
  - **KEINE** Schema-Änderungen
  - **KEINE** Tabellen-Drops
  - **KEINE** Datenbank-Resets
  - Nur Tabellen-Updates via Alembic-Migrationen

***REMOVED******REMOVED******REMOVED*** Marker zurücksetzen (für Neuinstallation):
```powershell
***REMOVED*** ACHTUNG: Löscht Installation-Marker (Datenbank bleibt erhalten!)
Remove-Item .installation_complete -ErrorAction SilentlyContinue

***REMOVED*** Für KOMPLETTE Neuinstallation (inkl. Datenbank-Reset):
docker-compose -f docker-compose.production.yml down -v
Remove-Item .installation_complete -ErrorAction SilentlyContinue
Remove-Item dev_test.db -ErrorAction SilentlyContinue
```

---

***REMOVED******REMOVED*** 🎓 Lessons Learned (aus heutigem Testing)

***REMOVED******REMOVED******REMOVED*** 1. Port-Konflikte vermeiden
**Problem:** Grafana lief auf Port 3000 und blockierte Frontend  
**Fix:** Grafana auf Port 3001 verschoben, Frontend nutzt Standard-Port 3000  
**Learning:** Zentrale Port-Registry in `config/services.yml`

***REMOVED******REMOVED******REMOVED*** 2. Windows + Docker + PostgreSQL
**Problem:** psycopg2 kann nicht zu Docker-PostgreSQL verbinden (trotz korrektem Port-Mapping)  
**Fix:** `create_tables()` fängt Fehler ab und startet Backend trotzdem (Testing-Modus)  
**Learning:** Für lokales Testing: Tabellen im Container direkt erstellen oder SQLite nutzen

***REMOVED******REMOVED******REMOVED*** 3. Background-Prozesse auf Windows
**Problem:** `Start-Process -WindowStyle Hidden` verschluckt Fehlerme ldungen  
**Fix:** Prozesse im Vordergrund starten beim Debugging  
**Learning:** Nur im Production-Deployment Background-Modus nutzen

***REMOVED******REMOVED******REMOVED*** 4. CORS-Origins dynamisch
**Problem:** Frontend wechselt zwischen Port 3000/3001/5173  
**Fix:** Alle möglichen Ports in CORS-Origins aufnehmen  
**Learning:** Frontend-Port sollte fix sein (immer 3000)

***REMOVED******REMOVED******REMOVED*** 5. Service-Dependencies
**Problem:** Backend startet ohne PostgreSQL und crasht  
**Fix:** Startup-Check prüft Dependencies vor dem Start  
**Learning:** Dependency-Graph in `config/services.yml` definiert

---

***REMOVED******REMOVED*** 📝 Maintenance-Commands

***REMOVED******REMOVED******REMOVED*** Regelmäßige Wartung:
```powershell
***REMOVED*** Wöchentlich: Docker-Cleanup
docker system prune -f

***REMOVED*** Monatlich: Image-Updates
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml build --no-cache

***REMOVED*** Bei Problemen: Kompletter Neustart
python scripts/service_manager.py stop-all
docker-compose -f docker-compose.production.yml down
***REMOVED*** Warte 10 Sekunden
python scripts/service_manager.py start
```

---

***REMOVED******REMOVED*** 🆘 Notfall-Kommandos

***REMOVED******REMOVED******REMOVED*** System hängt sich komplett auf:
```powershell
***REMOVED*** 1. Alle Prozesse killen
Get-Process python,node -ErrorAction SilentlyContinue | Stop-Process -Force

***REMOVED*** 2. Alle Docker-Container stoppen
docker stop $(docker ps -aq)

***REMOVED*** 3. Port-Check
netstat -ano | findstr ":3000 :8000 :5432"

***REMOVED*** 4. System neu starten
python scripts/service_manager.py start
```

---

**Ansprechpartner:** DevOps-Team  
**Dokumentation:** `docs/operations/`  
**Tools:** `scripts/service_manager.py`, `scripts/startup_check.py`

