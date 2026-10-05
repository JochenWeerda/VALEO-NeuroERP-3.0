# Swarm Quickstart Guide

## Schritt 1: Umgebungsvariablen setzen

### Option A: .env.swarm Datei verwenden (empfohlen)

Die Datei `.env.swarm` ist bereits erstellt mit Standard-Credentials:
- User: `admin`
- Pass: `admin123`

Falls du andere Credentials benÃ¶tigst, bearbeite `.env.swarm`:

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

## Schritt 2: Frontend starten (falls nicht bereits lÃ¤uft)

### Option A: Bestehendes Frontend nutzen

Wenn das Frontend bereits auf `localhost:3000` lÃ¤uft, kannst du es direkt nutzen.

**Wichtig:** Stelle sicher, dass der Health-Endpoint funktioniert:
```bash
curl http://localhost:3000/health
# oder
curl http://localhost:3000/health.html
```

### Option B: Neues Frontend fÃ¼r Swarm starten

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

## Schritt 3: UI-Explorer ausfÃ¼hren

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

# UI-Explorer ausfÃ¼hren
python swarm/ui_explorer.py
```

**Output:**
- Screenshots in `/evidence/screenshots/`
- Handoff-Notizen in `/swarm/handoffs/`

## Schritt 4: Tests generieren und ausfÃ¼hren

### Playwright Tests

```bash
# Tests mit Swarm-Config ausfÃ¼hren
npx playwright test --config=playwright.swarm.config.ts

# Oder mit Docker:
docker compose -f docker-compose.swarm.yml up neuroerp-tests
```

**Output:**
- Test-Results in `/evidence/traces/`
- HTML-Reports in `/evidence/traces/html-report/`

### Playwright Agentic Testing (Planner â†’ Generator â†’ Healer)

```bash
# 1. Test-Plan erstellen (aus UI-Explorer Handoff)
# Im Cursor-Chat: "Nutze Playwright planner agent. Erstelle Testplan fÃ¼r /swarm/handoffs/ui-explorer-finance.md"

# 2. Tests generieren
# Im Cursor-Chat: "Nutze generator agent, verwandle /specs/finance.md in Playwright-Tests"

# 3. Tests ausfÃ¼hren und heilen
npx playwright test --config=playwright.swarm.config.ts
# Healer repariert automatisch flaky/failing tests
```

## Schritt 5: GAP-Analyse durchfÃ¼hren

### 1. Evidence sammeln

- PrÃ¼fe Screenshots in `/evidence/screenshots/`
- PrÃ¼fe Handoff-Notizen in `/swarm/handoffs/`
- PrÃ¼fe Test-Traces in `/evidence/traces/`

### 2. Matrix ausfÃ¼llen

Ã–ffne `gap/matrix.csv` und fÃ¼lle fÃ¼r jede Capability:
- **NeuroERP Status**: Yes / Partial / No / ?
- **Evidence Screenshot IDs**: Links zu Screenshots
- **Notes**: Beschreibung
- **Comparable ERP baseline**: SAP-Ã¤hnlich / Community ERP-Ã¤hnlich / Basic

### 3. GAP-Liste erstellen

Ã–ffne `gap/gaps.md` und erstelle priorisierte Liste:
- **GAP-ID**: Eindeutige ID
- **Status**: Missing / Partial / Basic
- **PrioritÃ¤t**: P0 (Kritisch) / P1 (Hoch) / P2 (Mittel) / P3 (Niedrig)
- **Typ**: A (Config) / B (Integration) / C (Module) / D (UX)

### 4. Automatisierte Vor-BefÃ¼llung (optional)

Im Cursor-Chat:
```
Nimm Evidence aus /evidence/screenshots und /swarm/handoffs/*.
FÃ¼lle gap/matrix.csv nach Capability-Modell.
Markiere Unsicherheiten mit ?.
```

## Troubleshooting

### Frontend nicht erreichbar

```bash
# PrÃ¼fe ob Frontend lÃ¤uft
curl http://localhost:3000/health

# PrÃ¼fe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-frontend

# PrÃ¼fe ob Port belegt ist
netstat -ano | findstr :3000  # Windows
lsof -i :3000  # Linux/Mac
```

### UI-Explorer Fehler

```bash
# PrÃ¼fe Python-Dependencies
pip list | grep browser-use

# PrÃ¼fe ENV-Variablen
echo $NEUROERP_URL  # Linux/Mac
echo $env:NEUROERP_URL  # Windows PowerShell

# PrÃ¼fe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-ui-explorer
```

### Tests schlagen fehl

```bash
# PrÃ¼fe Traces
ls evidence/traces/

# PrÃ¼fe Screenshots
ls evidence/screenshots/

# Tests mit Debug-Output
npx playwright test --config=playwright.swarm.config.ts --debug
```

## NÃ¤chste Schritte nach Quickstart

1. **Weitere Module explorieren**
   - Erstelle neue Missions in `/swarm/missions/`
   - Passe `swarm/ui_explorer.py` an

2. **Test-Suite erweitern**
   - Nutze Playwright Planner/Generator
   - Erstelle weitere Tests in `/tests/e2e/`

3. **GAP-Analyse vertiefen**
   - FÃ¼lle `gap/matrix.csv` vollstÃ¤ndig aus
   - Priorisiere LÃ¼cken in `gap/gaps.md`

4. **LÃ¼cken schlieÃŸen**
   - Feature-Engineer arbeitet GAP-Liste ab
   - Code in `/extensions/` erstellen

## Hilfe

- **Swarm README**: `swarm/README.md`
- **Setup-Status**: `SWARM-SETUP-COMPLETE.md`
- **Cursor Rules**: `.cursorrules`



