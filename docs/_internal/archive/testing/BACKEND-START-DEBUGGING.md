# Backend-Start-Problem - Debugging-Guide

**Datum:** 13. Oktober 2025  
**Status:** 🔴 KRITISCH - Backend startet nicht trotz erfolgreicher Dependency-Checks  

---

## 🔍 Problem-Analyse

### ✅ Was funktioniert:
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

### ❌ Was NICHT funktioniert:
1. **Backend startet nicht auf Port 8000:**
   ```bash
   curl http://localhost:8000/health
   # → Connection Refused
   
   netstat -ano | findstr ":8000"
   # → Kein Prozess lauscht auf Port 8000
   ```

2. **UV icorn-Prozess läuft nicht:**
   ```powershell
   Get-Process python
   # → PID 6608, 22972 vorhanden
   # → Aber keiner lauscht auf Port 8000
   ```

---

## 🧩 Mögliche Root Causes

### 1. PostgreSQL-Verbindungsproblem ❗
**Config:**
```python
DATABASE_URL='postgresql://valeo_dev:REDACTED_PASSWORD@localhost:5432/valeo_neuro_erp'
```

**Prüfen:**
```bash
# Ist PostgreSQL erreichbar?
docker ps | grep postgres
# → valeo-postgres läuft auf Port 5432

# Kann man sich verbinden?
psql -h localhost -U valeo_dev -d valeo_neuro_erp
# → Wenn "password authentication failed" → User/DB fehlt
```

**Vermutung:** `valeo_dev` User existiert nicht in PostgreSQL  
**Expected:** Docker verwendet User `valeo`, nicht `valeo_dev`

---

### 2. DB-Schema fehlt ❗
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

### 3. Redis-Verbindungsproblem ⚠️
**Config:**
```python
REDIS_URL='redis://localhost:6379/0'
```

**Prüfen:**
```bash
docker ps | grep redis
# → valeo-redis läuft

redis-cli -h localhost ping
# → Sollte "PONG" zurückgeben
```

---

### 4. Port 8000 bereits belegt ⚠️
**Prüfen:**
```bash
netstat -ano | findstr ":8000"
# Aktuell: Nichts

Get-NetTCPConnection -LocalPort 8000
# Alternative Prüfung
```

**Status:** Port ist frei ✅

---

### 5. FastAPI Startup-Fehler im Lifespan ❗
**Mögliche Fehlerquellen in `main.py`:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting VALEO-NeuroERP API server...")
    
    # A. Container-Konfiguration
    configure_container()  # ← Könnte fehlschlagen
    
    # B. DB-Tabellen
    create_tables()        # ← Könnte fehlschlagen (DB-Verbindung)
    
    yield
    
    # Shutdown
    logger.info("Shutting down VALEO-NeuroERP API server...")
```

**Vermutung:** `create_tables()` schlägt fehl weil:
- PostgreSQL-User/Passwort falsch
- DB `valeo_neuro_erp` existiert nicht
- Schemas nicht initialisiert

---

## 🔧 Lösung: Schritt-für-Schritt

### Schritt 1: PostgreSQL korrekt konfigurieren

```bash
# A. Stoppe alle Docker-Container
docker-compose -f docker-compose.production.yml down

# B. Starte nur PostgreSQL
docker run -d \
  --name valeo-postgres-dev \
  -e POSTGRES_USER=valeo_dev \
  -e POSTGRES_PASSWORD=REDACTED_PASSWORD \
  -e POSTGRES_DB=valeo_neuro_erp \
  -p 5432:5432 \
  postgres:15-alpine

# C. Warte auf Start
timeout /t 10

# D. Teste Verbindung
docker exec valeo-postgres-dev psql -U valeo_dev -d valeo_neuro_erp -c "SELECT 1;"
```

---

### Schritt 2: DB-Schemas initialisieren

```bash
# Option A: SQL-Skript ausführen
docker exec -i valeo-postgres-dev psql -U valeo_dev -d valeo_neuro_erp <<EOF
CREATE SCHEMA IF NOT EXISTS domain_shared;
CREATE SCHEMA IF NOT EXISTS domain_crm;
CREATE SCHEMA IF NOT EXISTS domain_inventory;
CREATE SCHEMA IF NOT EXISTS domain_erp;
EOF

# Option B: Python-Init-Skript
python scripts/init_db.py
```

---

### Schritt 3: Backend-Start mit Logging

```bash
# Starte Backend im Vordergrund (um Fehler zu sehen)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# Erwartete Ausgabe:
# INFO: Started server process [12345]
# INFO: Waiting for application startup.
# INFO: Application startup complete.
# INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

### Schritt 4: Health-Check

```bash
# In einem zweiten Terminal:
curl http://localhost:8000/health

# Erwartete Antwort:
# {"status": "healthy", "timestamp": "..."}
```

---

## 📊 Alternativer Ansatz: Lokales Backend ohne Docker

### Setup:
```bash
# 1. SQLite statt PostgreSQL (für lokale Entwicklung)
# In .env:
DATABASE_URL=sqlite:///./dev.db

# 2. Redis deaktivieren (optional für Testing)
ENABLE_CACHE=False

# 3. NATS deaktivieren (optional)
# Events verwenden In-Memory-Publisher

# 4. Backend starten
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Vorteile:
- ✅ Kein Docker-Overhead
- ✅ Schnellerer Entwicklungszyklus
- ✅ Einfacheres Debugging
- ✅ Funktioniert sofort

### Nachteile:
- ⚠️ Nicht production-like
- ⚠️ Keine Event-Bus-Integration
- ⚠️ Keine Redis-Caching

---

## 🚀 Empfohlene Nächste Schritte

### Sofort (10 Min):
1. ✅ Python-Dependencies installiert
2. ⏭️ PostgreSQL-User/DB korrekt konfigurieren
3. ⏭️ DB-Schemas initialisieren
4. ⏭️ Backend im Vordergrund starten (Fehler sichtbar machen)

### Danach (30 Min):
1. ⏭️ Health-Check erfolgreich
2. ⏭️ API-Endpoints testen (curl/Postman)
3. ⏭️ Frontend mit Backend verbinden
4. ⏭️ Erste CRUD-Operationen testen

### Vollständiges UI/UX-Testing (8-12 Std):
1. ⏭️ 181 Masken durchgehen
2. ⏭️ Pro Maske: 20 Create, 3 Edit, 3 Delete
3. ⏭️ Security-Tests (SQL-Injection, XSS)
4. ⏭️ Workflow-Tests (Belegfluss, Policies)
5. ⏭️ Error-Handling-Tests

---

## 💡 Debug-Kommandos

### Backend-Logs live ansehen:
```powershell
# Finde uvicorn-Prozess
Get-Process python | Where-Object {$_.Path -like "*python*"}

# Netzwerk-Connections prüfen
netstat -ano | findstr "8000"
Get-NetTCPConnection -State Listen

# Docker-Container-Logs
docker-compose -f docker-compose.production.yml logs -f valeo-app
```

### Datenbank-Status prüfen:
```bash
# PostgreSQL
docker exec valeo-postgres pg_isready -U valeo
docker exec valeo-postgres psql -U valeo -d valeo_neuro_erp -c "\dt domain_shared.*"

# Redis
docker exec valeo-redis redis-cli ping
docker exec valeo-redis redis-cli INFO server
```

### Backend-Tests ohne UI:
```bash
# API direkt testen (wenn Backend läuft)
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/crm/customers
curl -X POST http://localhost:8000/api/v1/crm/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "Test GmbH", "email": "test@example.com"}'
```

---

## 🎯 Quick Win: Minimal-Backend für Testing

Wenn das komplette Backend-Setup zu lange dauert, kannst du ein **Minimal-Backend** erstellen:

```python
# minimal_backend.py
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

# Mock-Daten
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

# Starten mit:
# uvicorn minimal_backend:app --host 0.0.0.0 --port 8000 --reload
```

**Vorteil:** Läuft sofort, kein DB-Setup nötig  
**Nachteil:** Nur Mock-Daten, keine Persistierung

---

## 📝 Status-Update

**Diagnose-Ergebnis:** ✅ PASS (alle Imports funktionieren)  
**Backend-Start:** ❌ FAIL (Prozess startet nicht auf Port 8000)  
**Root Cause:** ⏳ UNGEKLÄRT (vermutlich DB-Verbindung oder Lifespan-Fehler)  

**Empfehlung:** Backend manuell im Vordergrund starten um Fehler zu sehen:
```bash
cd C:\Users\Jochen\VALEO-NeuroERP-3.0
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

**Nächster Schritt:** Fehlermeldu ng analysieren und spezifischen Fix anwenden


