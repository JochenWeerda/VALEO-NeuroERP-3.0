***REMOVED*** Backend-Start-Problem - Debugging-Guide

**Datum:** 13. Oktober 2025  
**Status:** 🔴 KRITISCH - Backend startet nicht trotz erfolgreicher Dependency-Checks  

---

***REMOVED******REMOVED*** 🔍 Problem-Analyse

***REMOVED******REMOVED******REMOVED*** ✅ Was funktioniert:
1. **Alle Python-Dependencies installiert:**
   ```
   fastapi==0.115.14        ✅
   uvicorn==0.24.0          ✅
   sqlalchemy==2.0.41       ✅
   langgraph                ✅
   chromadb                 ✅
   nats-py==2.11.0          ✅
   ```

2. **Alle App-Module importierbar:**
   ```python
   from app.core.config import settings           ✅
   from app.core.database import create_tables    ✅
   from app.api.v1.api import api_router          ✅ (61 routes)
   from main import app                           ✅ (204 routes)
   ```

3. **Keine Import-Fehler:**
   - Diagnose-Skript läuft durch (Exit Code 0)
   - Alle Warnungen sind nicht-kritisch

---

***REMOVED******REMOVED******REMOVED*** ❌ Was NICHT funktioniert:
1. **Backend startet nicht auf Port 8000:**
   ```bash
   curl http://localhost:8000/health
   ***REMOVED*** → Connection Refused
   
   netstat -ano | findstr ":8000"
   ***REMOVED*** → Kein Prozess lauscht auf Port 8000
   ```

2. **UV icorn-Prozess läuft nicht:**
   ```powershell
   Get-Process python
   ***REMOVED*** → PID 6608, 22972 vorhanden
   ***REMOVED*** → Aber keiner lauscht auf Port 8000
   ```

---

***REMOVED******REMOVED*** 🧩 Mögliche Root Causes

***REMOVED******REMOVED******REMOVED*** 1. PostgreSQL-Verbindungsproblem ❗
**Config:**
```python
DATABASE_URL='postgresql://valeo_dev:REDACTED_PASSWORD@localhost:5432/valeo_neuro_erp'
```

**Prüfen:**
```bash
***REMOVED*** Ist PostgreSQL erreichbar?
docker ps | grep postgres
***REMOVED*** → valeo-postgres läuft auf Port 5432

***REMOVED*** Kann man sich verbinden?
psql -h localhost -U valeo_dev -d valeo_neuro_erp
***REMOVED*** → Wenn "password authentication failed" → User/DB fehlt
```

**Vermutung:** `valeo_dev` User existiert nicht in PostgreSQL  
**Expected:** Docker verwendet User `valeo`, nicht `valeo_dev`

---

***REMOVED******REMOVED******REMOVED*** 2. DB-Schema fehlt ❗
**Config erwartet:**
```sql
-- Diese Schemas müssen existieren:
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_erp;
```

**Prüfen:**
```sql
-- In psql:
\dn
-- Sollte zeigen: domain_shared, domain_crm, domain_inventory, domain_erp
```

**Vermutung:** Schemas fehlen, `create_tables()` schlägt beim Startup fehl

---

***REMOVED******REMOVED******REMOVED*** 3. Redis-Verbindungsproblem ⚠️
**Config:**
```python
REDIS_URL='redis://localhost:6379/0'
```

**Prüfen:**
```bash
docker ps | grep redis
***REMOVED*** → valeo-redis läuft

redis-cli -h localhost ping
***REMOVED*** → Sollte "PONG" zurückgeben
```

---

***REMOVED******REMOVED******REMOVED*** 4. Port 8000 bereits belegt ⚠️
**Prüfen:**
```bash
netstat -ano | findstr ":8000"
***REMOVED*** Aktuell: Nichts

Get-NetTCPConnection -LocalPort 8000
***REMOVED*** Alternative Prüfung
```

**Status:** Port ist frei ✅

---

***REMOVED******REMOVED******REMOVED*** 5. FastAPI Startup-Fehler im Lifespan ❗
**Mögliche Fehlerquellen in `main.py`:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    ***REMOVED*** Startup
    logger.info("Starting VALEO-NeuroERP API server...")
    
    ***REMOVED*** A. Container-Konfiguration
    configure_container()  ***REMOVED*** ← Könnte fehlschlagen
    
    ***REMOVED*** B. DB-Tabellen
    create_tables()        ***REMOVED*** ← Könnte fehlschlagen (DB-Verbindung)
    
    yield
    
    ***REMOVED*** Shutdown
    logger.info("Shutting down VALEO-NeuroERP API server...")
```

**Vermutung:** `create_tables()` schlägt fehl weil:
- PostgreSQL-User/Passwort falsch
- DB `valeo_neuro_erp` existiert nicht
- Schemas nicht initialisiert

---

***REMOVED******REMOVED*** 🔧 Lösung: Schritt-für-Schritt

***REMOVED******REMOVED******REMOVED*** Schritt 1: PostgreSQL korrekt konfigurieren

```bash
***REMOVED*** A. Stoppe alle Docker-Container
docker-compose -f docker-compose.production.yml down

***REMOVED*** B. Starte nur PostgreSQL
docker run -d \
  --name valeo-postgres-dev \
  -e POSTGRES_USER=valeo_dev \
  -e POSTGRES_PASSWORD=REDACTED_PASSWORD \
  -e POSTGRES_DB=valeo_neuro_erp \
  -p 5432:5432 \
  postgres:15-alpine

***REMOVED*** C. Warte auf Start
timeout /t 10

***REMOVED*** D. Teste Verbindung
docker exec valeo-postgres-dev psql -U valeo_dev -d valeo_neuro_erp -c "SELECT 1;"
```

---

***REMOVED******REMOVED******REMOVED*** Schritt 2: DB-Schemas initialisieren

```bash
***REMOVED*** Option A: SQL-Skript ausführen
docker exec -i valeo-postgres-dev psql -U valeo_dev -d valeo_neuro_erp <<EOF
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_erp;
EOF

***REMOVED*** Option B: Python-Init-Skript
python scripts/init_db.py
```

---

***REMOVED******REMOVED******REMOVED*** Schritt 3: Backend-Start mit Logging

```bash
***REMOVED*** Starte Backend im Vordergrund (um Fehler zu sehen)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

***REMOVED*** Erwartete Ausgabe:
***REMOVED*** INFO: Started server process [12345]
***REMOVED*** INFO: Waiting for application startup.
***REMOVED*** INFO: Application startup complete.
***REMOVED*** INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

***REMOVED******REMOVED******REMOVED*** Schritt 4: Health-Check

```bash
***REMOVED*** In einem zweiten Terminal:
curl http://localhost:8000/health

***REMOVED*** Erwartete Antwort:
***REMOVED*** {"status": "healthy", "timestamp": "..."}
```

---

***REMOVED******REMOVED*** 📊 Alternativer Ansatz: Lokales Backend ohne Docker

***REMOVED******REMOVED******REMOVED*** Setup:
```bash
***REMOVED*** 1. SQLite statt PostgreSQL (für lokale Entwicklung)
***REMOVED*** In .env:
DATABASE_URL=sqlite:///./dev.db

***REMOVED*** 2. Redis deaktivieren (optional für Testing)
ENABLE_CACHE=False

***REMOVED*** 3. NATS deaktivieren (optional)
***REMOVED*** Events verwenden In-Memory-Publisher

***REMOVED*** 4. Backend starten
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

***REMOVED******REMOVED******REMOVED*** Vorteile:
- ✅ Kein Docker-Overhead
- ✅ Schnellerer Entwicklungszyklus
- ✅ Einfacheres Debugging
- ✅ Funktioniert sofort

***REMOVED******REMOVED******REMOVED*** Nachteile:
- ⚠️ Nicht production-like
- ⚠️ Keine Event-Bus-Integration
- ⚠️ Keine Redis-Caching

---

***REMOVED******REMOVED*** 🚀 Empfohlene Nächste Schritte

***REMOVED******REMOVED******REMOVED*** Sofort (10 Min):
1. ✅ Python-Dependencies installiert
2. ⏭️ PostgreSQL-User/DB korrekt konfigurieren
3. ⏭️ DB-Schemas initialisieren
4. ⏭️ Backend im Vordergrund starten (Fehler sichtbar machen)

***REMOVED******REMOVED******REMOVED*** Danach (30 Min):
1. ⏭️ Health-Check erfolgreich
2. ⏭️ API-Endpoints testen (curl/Postman)
3. ⏭️ Frontend mit Backend verbinden
4. ⏭️ Erste CRUD-Operationen testen

***REMOVED******REMOVED******REMOVED*** Vollständiges UI/UX-Testing (8-12 Std):
1. ⏭️ 181 Masken durchgehen
2. ⏭️ Pro Maske: 20 Create, 3 Edit, 3 Delete
3. ⏭️ Security-Tests (SQL-Injection, XSS)
4. ⏭️ Workflow-Tests (Belegfluss, Policies)
5. ⏭️ Error-Handling-Tests

---

***REMOVED******REMOVED*** 💡 Debug-Kommandos

***REMOVED******REMOVED******REMOVED*** Backend-Logs live ansehen:
```powershell
***REMOVED*** Finde uvicorn-Prozess
Get-Process python | Where-Object {$_.Path -like "*python*"}

***REMOVED*** Netzwerk-Connections prüfen
netstat -ano | findstr "8000"
Get-NetTCPConnection -State Listen

***REMOVED*** Docker-Container-Logs
docker-compose -f docker-compose.production.yml logs -f valeo-app
```

***REMOVED******REMOVED******REMOVED*** Datenbank-Status prüfen:
```bash
***REMOVED*** PostgreSQL
docker exec valeo-postgres pg_isready -U valeo
docker exec valeo-postgres psql -U valeo -d valeo_neuro_erp -c "\dt domain_shared.*"

***REMOVED*** Redis
docker exec valeo-redis redis-cli ping
docker exec valeo-redis redis-cli INFO server
```

***REMOVED******REMOVED******REMOVED*** Backend-Tests ohne UI:
```bash
***REMOVED*** API direkt testen (wenn Backend läuft)
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/crm/customers
curl -X POST http://localhost:8000/api/v1/crm/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "Test GmbH", "email": "test@example.com"}'
```

---

***REMOVED******REMOVED*** 🎯 Quick Win: Minimal-Backend für Testing

Wenn das komplette Backend-Setup zu lange dauert, kannst du ein **Minimal-Backend** erstellen:

```python
***REMOVED*** minimal_backend.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VALEO-NeuroERP Minimal Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

***REMOVED*** Mock-Daten
MOCK_CUSTOMERS = [
    {"id": 1, "name": "Müller Agrar GmbH", "email": "mueller@example.com"},
    {"id": 2, "name": "Schmidt Landhandel", "email": "schmidt@example.com"},
]

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/crm/customers")
def get_customers():
    return MOCK_CUSTOMERS

@app.post("/api/v1/crm/customers")
def create_customer(data: dict):
    new_id = max([c["id"] for c in MOCK_CUSTOMERS]) + 1
    customer = {"id": new_id, **data}
    MOCK_CUSTOMERS.append(customer)
    return customer

***REMOVED*** Starten mit:
***REMOVED*** uvicorn minimal_backend:app --host 0.0.0.0 --port 8000 --reload
```

**Vorteil:** Läuft sofort, kein DB-Setup nötig  
**Nachteil:** Nur Mock-Daten, keine Persistierung

---

***REMOVED******REMOVED*** 📝 Status-Update

**Diagnose-Ergebnis:** ✅ PASS (alle Imports funktionieren)  
**Backend-Start:** ❌ FAIL (Prozess startet nicht auf Port 8000)  
**Root Cause:** ⏳ UNGEKLÄRT (vermutlich DB-Verbindung oder Lifespan-Fehler)  

**Empfehlung:** Backend manuell im Vordergrund starten um Fehler zu sehen:
```bash
cd C:\Users\Jochen\VALEO-NeuroERP-3.0
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Nächster Schritt:** Fehlermeldu ng analysieren und spezifischen Fix anwenden

