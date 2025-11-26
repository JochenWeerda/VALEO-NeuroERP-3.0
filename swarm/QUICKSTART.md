***REMOVED*** Swarm Quickstart Guide

***REMOVED******REMOVED*** Schritt 1: Umgebungsvariablen setzen

***REMOVED******REMOVED******REMOVED*** Option A: .env.swarm Datei verwenden (empfohlen)

Die Datei `.env.swarm` ist bereits erstellt mit Standard-Credentials:
- User: `admin`
- Pass: `admin123`

Falls du andere Credentials benötigst, bearbeite `.env.swarm`:

```bash
***REMOVED*** .env.swarm bearbeiten
NEUROERP_URL=http://localhost:3000
NEUROERP_USER=admin
NEUROERP_PASS=admin123
```

***REMOVED******REMOVED******REMOVED*** Option B: Environment-Variablen direkt setzen

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

***REMOVED******REMOVED*** Schritt 2: Frontend starten (falls nicht bereits läuft)

***REMOVED******REMOVED******REMOVED*** Option A: Bestehendes Frontend nutzen

Wenn das Frontend bereits auf `localhost:3000` läuft, kannst du es direkt nutzen.

**Wichtig:** Stelle sicher, dass der Health-Endpoint funktioniert:
```bash
curl http://localhost:3000/health
***REMOVED*** oder
curl http://localhost:3000/health.html
```

***REMOVED******REMOVED******REMOVED*** Option B: Neues Frontend für Swarm starten

```bash
***REMOVED*** Frontend im Swarm-Netzwerk starten (Port 3001)
docker compose -f docker-compose.swarm.yml up neuroerp-frontend -d

***REMOVED*** Warten bis Frontend ready ist
docker compose -f docker-compose.swarm.yml logs -f neuroerp-frontend
***REMOVED*** Warte auf: "ready in ..." oder "Local: http://localhost:3000"
```

**Dann URL anpassen:**
```bash
***REMOVED*** In .env.swarm oder als ENV-Variable:
NEUROERP_URL=http://localhost:3001
```

***REMOVED******REMOVED*** Schritt 3: UI-Explorer ausführen

***REMOVED******REMOVED******REMOVED*** Mit Docker (empfohlen)

```bash
***REMOVED*** UI-Explorer starten (wartet automatisch auf Frontend)
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer

***REMOVED*** Oder im Hintergrund:
docker compose -f docker-compose.swarm.yml up -d neuroerp-ui-explorer
docker compose -f docker-compose.swarm.yml logs -f neuroerp-ui-explorer
```

***REMOVED******REMOVED******REMOVED*** Lokal (ohne Docker)

```bash
***REMOVED*** Python-Dependencies installieren
pip install -r swarm/requirements.ui-explorer.txt

***REMOVED*** UI-Explorer ausführen
python swarm/ui_explorer.py
```

**Output:**
- Screenshots in `/evidence/screenshots/`
- Handoff-Notizen in `/swarm/handoffs/`

***REMOVED******REMOVED*** Schritt 4: Tests generieren und ausführen

***REMOVED******REMOVED******REMOVED*** Playwright Tests

```bash
***REMOVED*** Tests mit Swarm-Config ausführen
npx playwright test --config=playwright.swarm.config.ts

***REMOVED*** Oder mit Docker:
docker compose -f docker-compose.swarm.yml up neuroerp-tests
```

**Output:**
- Test-Results in `/evidence/traces/`
- HTML-Reports in `/evidence/traces/html-report/`

***REMOVED******REMOVED******REMOVED*** Playwright Agentic Testing (Planner → Generator → Healer)

```bash
***REMOVED*** 1. Test-Plan erstellen (aus UI-Explorer Handoff)
***REMOVED*** Im Cursor-Chat: "Nutze Playwright planner agent. Erstelle Testplan für /swarm/handoffs/ui-explorer-finance.md"

***REMOVED*** 2. Tests generieren
***REMOVED*** Im Cursor-Chat: "Nutze generator agent, verwandle /specs/finance.md in Playwright-Tests"

***REMOVED*** 3. Tests ausführen und heilen
npx playwright test --config=playwright.swarm.config.ts
***REMOVED*** Healer repariert automatisch flaky/failing tests
```

***REMOVED******REMOVED*** Schritt 5: GAP-Analyse durchführen

***REMOVED******REMOVED******REMOVED*** 1. Evidence sammeln

- Prüfe Screenshots in `/evidence/screenshots/`
- Prüfe Handoff-Notizen in `/swarm/handoffs/`
- Prüfe Test-Traces in `/evidence/traces/`

***REMOVED******REMOVED******REMOVED*** 2. Matrix ausfüllen

Öffne `gap/matrix.csv` und fülle für jede Capability:
- **NeuroERP Status**: Yes / Partial / No / ?
- **Evidence Screenshot IDs**: Links zu Screenshots
- **Notes**: Beschreibung
- **Comparable ERP baseline**: SAP-ähnlich / Odoo-ähnlich / Basic

***REMOVED******REMOVED******REMOVED*** 3. GAP-Liste erstellen

Öffne `gap/gaps.md` und erstelle priorisierte Liste:
- **GAP-ID**: Eindeutige ID
- **Status**: Missing / Partial / Basic
- **Priorität**: P0 (Kritisch) / P1 (Hoch) / P2 (Mittel) / P3 (Niedrig)
- **Typ**: A (Config) / B (Integration) / C (Module) / D (UX)

***REMOVED******REMOVED******REMOVED*** 4. Automatisierte Vor-Befüllung (optional)

Im Cursor-Chat:
```
Nimm Evidence aus /evidence/screenshots und /swarm/handoffs/*. 
Fülle gap/matrix.csv nach Capability-Modell. 
Markiere Unsicherheiten mit ?.
```

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Frontend nicht erreichbar

```bash
***REMOVED*** Prüfe ob Frontend läuft
curl http://localhost:3000/health

***REMOVED*** Prüfe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-frontend

***REMOVED*** Prüfe ob Port belegt ist
netstat -ano | findstr :3000  ***REMOVED*** Windows
lsof -i :3000  ***REMOVED*** Linux/Mac
```

***REMOVED******REMOVED******REMOVED*** UI-Explorer Fehler

```bash
***REMOVED*** Prüfe Python-Dependencies
pip list | grep browser-use

***REMOVED*** Prüfe ENV-Variablen
echo $NEUROERP_URL  ***REMOVED*** Linux/Mac
echo $env:NEUROERP_URL  ***REMOVED*** Windows PowerShell

***REMOVED*** Prüfe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-ui-explorer
```

***REMOVED******REMOVED******REMOVED*** Tests schlagen fehl

```bash
***REMOVED*** Prüfe Traces
ls evidence/traces/

***REMOVED*** Prüfe Screenshots
ls evidence/screenshots/

***REMOVED*** Tests mit Debug-Output
npx playwright test --config=playwright.swarm.config.ts --debug
```

***REMOVED******REMOVED*** Nächste Schritte nach Quickstart

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

***REMOVED******REMOVED*** Hilfe

- **Swarm README**: `swarm/README.md`
- **Setup-Status**: `SWARM-SETUP-COMPLETE.md`
- **Cursor Rules**: `.cursorrules`

