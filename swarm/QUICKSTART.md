# Swarm Quickstart Guide

## Schritt 1: Umgebungsvariablen setzen

### Option A: .env.swarm Datei verwenden (empfohlen)

Die Datei `.env.swarm` ist bereits erstellt mit Standard-Credentials:
- User: `admin`
- Pass: `admin123`

Falls du andere Credentials benötigst, bearbeite `.env.swarm`:

```bash
# .env.swarm bearbeiten
NEUROERP_URL=http://localhost:3000
NEUROERP_USER=admin
NEUROERP_PASS=admin123
```

### Option B: Environment-Variablen direkt setzen

**Windows PowerShell:**
```powershell
$env:NEUROERP_URL="http://localhost:3000"
$env:NEUROERP_USER="admin"
$env:NEUROERP_PASS="admin123"
```

**Linux/Mac:**
```bash
export NEUROERP_URL=http://localhost:3000
export NEUROERP_USER=admin
export NEUROERP_PASS=admin123
```

## Schritt 2: Frontend starten (falls nicht bereits läuft)

### Option A: Bestehendes Frontend nutzen

Wenn das Frontend bereits auf `localhost:3000` läuft, kannst du es direkt nutzen.

**Wichtig:** Stelle sicher, dass der Health-Endpoint funktioniert:
```bash
curl http://localhost:3000/health
# oder
curl http://localhost:3000/health.html
```

### Option B: Neues Frontend für Swarm starten

```bash
# Frontend im Swarm-Netzwerk starten (Port 3001)
docker compose -f docker-compose.swarm.yml up neuroerp-frontend -d

# Warten bis Frontend ready ist
docker compose -f docker-compose.swarm.yml logs -f neuroerp-frontend
# Warte auf: "ready in ..." oder "Local: http://localhost:3000"
```

**Dann URL anpassen:**
```bash
# In .env.swarm oder als ENV-Variable:
NEUROERP_URL=http://localhost:3001
```

## Schritt 3: UI-Explorer ausführen

### Mit Docker (empfohlen)

```bash
# UI-Explorer starten (wartet automatisch auf Frontend)
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer

# Oder im Hintergrund:
docker compose -f docker-compose.swarm.yml up -d neuroerp-ui-explorer
docker compose -f docker-compose.swarm.yml logs -f neuroerp-ui-explorer
```

### Lokal (ohne Docker)

```bash
# Python-Dependencies installieren
pip install -r swarm/requirements.ui-explorer.txt

# UI-Explorer ausführen
python swarm/ui_explorer.py
```

**Output:**
- Screenshots in `/evidence/screenshots/`
- Handoff-Notizen in `/swarm/handoffs/`

## Schritt 4: Tests generieren und ausführen

### Playwright Tests

```bash
# Tests mit Swarm-Config ausführen
npx playwright test --config=playwright.swarm.config.ts

# Oder mit Docker:
docker compose -f docker-compose.swarm.yml up neuroerp-tests
```

**Output:**
- Test-Results in `/evidence/traces/`
- HTML-Reports in `/evidence/traces/html-report/`

### Playwright Agentic Testing (Planner → Generator → Healer)

```bash
# 1. Test-Plan erstellen (aus UI-Explorer Handoff)
# Im Cursor-Chat: "Nutze Playwright planner agent. Erstelle Testplan für /swarm/handoffs/ui-explorer-finance.md"

# 2. Tests generieren
# Im Cursor-Chat: "Nutze generator agent, verwandle /specs/finance.md in Playwright-Tests"

# 3. Tests ausführen und heilen
npx playwright test --config=playwright.swarm.config.ts
# Healer repariert automatisch flaky/failing tests
```

## Schritt 5: GAP-Analyse durchführen

### 1. Evidence sammeln

- Prüfe Screenshots in `/evidence/screenshots/`
- Prüfe Handoff-Notizen in `/swarm/handoffs/`
- Prüfe Test-Traces in `/evidence/traces/`

### 2. Matrix ausfüllen

Öffne `gap/matrix.csv` und fülle für jede Capability:
- **NeuroERP Status**: Yes / Partial / No / ?
- **Evidence Screenshot IDs**: Links zu Screenshots
- **Notes**: Beschreibung
- **Comparable ERP baseline**: SAP-ähnlich / Odoo-ähnlich / Basic

### 3. GAP-Liste erstellen

Öffne `gap/gaps.md` und erstelle priorisierte Liste:
- **GAP-ID**: Eindeutige ID
- **Status**: Missing / Partial / Basic
- **Priorität**: P0 (Kritisch) / P1 (Hoch) / P2 (Mittel) / P3 (Niedrig)
- **Typ**: A (Config) / B (Integration) / C (Module) / D (UX)

### 4. Automatisierte Vor-Befüllung (optional)

Im Cursor-Chat:
```
Nimm Evidence aus /evidence/screenshots und /swarm/handoffs/*. 
Fülle gap/matrix.csv nach Capability-Modell. 
Markiere Unsicherheiten mit ?.
```

## Troubleshooting

### Frontend nicht erreichbar

```bash
# Prüfe ob Frontend läuft
curl http://localhost:3000/health

# Prüfe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-frontend

# Prüfe ob Port belegt ist
netstat -ano | findstr :3000  # Windows
lsof -i :3000  # Linux/Mac
```

### UI-Explorer Fehler

```bash
# Prüfe Python-Dependencies
pip list | grep browser-use

# Prüfe ENV-Variablen
echo $NEUROERP_URL  # Linux/Mac
echo $env:NEUROERP_URL  # Windows PowerShell

# Prüfe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-ui-explorer
```

### Tests schlagen fehl

```bash
# Prüfe Traces
ls evidence/traces/

# Prüfe Screenshots
ls evidence/screenshots/

# Tests mit Debug-Output
npx playwright test --config=playwright.swarm.config.ts --debug
```

## Nächste Schritte nach Quickstart

1. **Weitere Module explorieren**
   - Erstelle neue Missions in `/swarm/missions/`
   - Passe `swarm/ui_explorer.py` an

2. **Test-Suite erweitern**
   - Nutze Playwright Planner/Generator
   - Erstelle weitere Tests in `/tests/e2e/`

3. **GAP-Analyse vertiefen**
   - Fülle `gap/matrix.csv` vollständig aus
   - Priorisiere Lücken in `gap/gaps.md`

4. **Lücken schließen**
   - Feature-Engineer arbeitet GAP-Liste ab
   - Code in `/extensions/` erstellen

## Hilfe

- **Swarm README**: `swarm/README.md`
- **Setup-Status**: `SWARM-SETUP-COMPLETE.md`
- **Cursor Rules**: `.cursorrules`

