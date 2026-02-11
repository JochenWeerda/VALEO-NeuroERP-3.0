# Nächste Schritte - Swarm System

## ✅ Setup abgeschlossen

Alle Komponenten sind konfiguriert und einsatzbereit!

## 🚀 Schritt-für-Schritt Anleitung

### Schritt 1: Umgebungsvariablen ✅

Die Datei `.env.swarm` wurde erstellt mit:
- `NEUROERP_URL=http://localhost:3000`
- `NEUROERP_USER=admin`
- `NEUROERP_PASS=admin123`

**Falls du andere Credentials benötigst**, bearbeite `.env.swarm` oder setze ENV-Variablen:

```powershell
# PowerShell
$env:NEUROERP_URL="http://localhost:3000"
$env:NEUROERP_USER="admin"
$env:NEUROERP_PASS="admin123"
```

### Schritt 2: Frontend prüfen/starten

**Option A: Bestehendes Frontend nutzen (empfohlen)**

Wenn das Frontend bereits auf `localhost:3000` läuft:

```powershell
# Prüfe Health-Endpoint
curl http://localhost:3000/health
# oder
curl http://localhost:3000/health.html
```

**Option B: Neues Frontend für Swarm starten**

```powershell
# Starte Frontend im Swarm-Netzwerk (Port 3001)
docker compose -f docker-compose.swarm.yml up neuroerp-frontend -d

# Warte auf Ready
docker compose -f docker-compose.swarm.yml logs -f neuroerp-frontend
```

**Dann URL anpassen:**
```powershell
$env:NEUROERP_URL="http://localhost:3001"
```

### Schritt 3: Erste Mission starten - UI-Explorer

**Mit Docker (empfohlen):**

```powershell
# UI-Explorer starten (wartet automatisch auf Frontend)
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer

# Oder im Hintergrund:
docker compose -f docker-compose.swarm.yml up -d neuroerp-ui-explorer
docker compose -f docker-compose.swarm.yml logs -f neuroerp-ui-explorer
```

**Lokal (ohne Docker):**

```powershell
# Python-Dependencies installieren
pip install -r swarm/requirements.ui-explorer.txt

# UI-Explorer ausführen
python swarm/ui_explorer.py
```

**Erwartete Outputs:**
- 📸 Screenshots in `evidence/screenshots/finance_flow_*.json`
- 📝 Handoff-Notizen in `swarm/handoffs/ui-explorer-finance-*.md`

### Schritt 4: Tests generieren und ausführen

**Playwright Tests (Seed-Test):**

```powershell
# Tests mit Swarm-Config ausführen
npx playwright test --config=playwright.swarm.config.ts

# Oder mit Docker:
docker compose -f docker-compose.swarm.yml up neuroerp-tests
```

**Playwright Agentic Testing (Planner → Generator → Healer):**

1. **Test-Plan erstellen** (im Cursor-Chat):
   ```
   Nutze Playwright planner agent. 
   Erstelle Testplan für /swarm/handoffs/ui-explorer-finance.md.
   Output nach /specs/finance.md.
   ```

2. **Tests generieren** (im Cursor-Chat):
   ```
   Nutze generator agent, verwandle /specs/finance.md in Playwright-Tests 
   unter /tests/e2e/finance/*.spec.ts. 
   Nutze tests/seed/seed.spec.ts als Beispiel.
   ```

3. **Tests ausführen und heilen**:
   ```powershell
   npx playwright test --config=playwright.swarm.config.ts
   # Healer repariert automatisch flaky/failing tests
   ```

**Erwartete Outputs:**
- 📊 Test-Results in `evidence/traces/results.json`
- 📹 HTML-Reports in `evidence/traces/html-report/`
- 🎬 Videos/Traces bei Fehlern in `evidence/traces/`

### Schritt 5: GAP-Analyse durchführen

**1. Evidence sammeln:**

```powershell
# Prüfe Screenshots
ls evidence/screenshots/

# Prüfe Handoff-Notizen
ls swarm/handoffs/

# Prüfe Test-Traces
ls evidence/traces/
```

**2. Matrix ausfüllen:**

Öffne `gap/matrix.csv` und fülle für jede Capability:
- **NeuroERP Status**: `Yes` / `Partial` / `No` / `?`
- **Evidence Screenshot IDs**: Links zu Screenshots
- **Notes**: Beschreibung der Lücke
- **Comparable ERP baseline**: `SAP-ähnlich` / `Odoo-ähnlich` / `Basic`

**3. GAP-Liste erstellen:**

Öffne `gap/gaps.md` und erstelle priorisierte Liste mit:
- **GAP-ID**: Eindeutige ID (z.B. `FIN-001`)
- **Status**: `Missing` / `Partial` / `Basic`
- **Priorität**: `P0` (Kritisch) / `P1` (Hoch) / `P2` (Mittel) / `P3` (Niedrig)
- **Typ**: `A` (Config) / `B` (Integration) / `C` (Module) / `D` (UX)

**4. Automatisierte Vor-Befüllung (optional):**

Im Cursor-Chat:
```
Nimm Evidence aus /evidence/screenshots und /swarm/handoffs/*. 
Fülle gap/matrix.csv nach Capability-Modell aus gap/capability-model.md. 
Markiere Unsicherheiten mit ?.
```

## 📋 Checkliste

- [ ] `.env.swarm` erstellt/bearbeitet
- [ ] Frontend läuft und Health-Endpoint funktioniert
- [ ] UI-Explorer ausgeführt (Finance Module)
- [ ] Screenshots in `evidence/screenshots/` vorhanden
- [ ] Handoff-Notizen in `swarm/handoffs/` vorhanden
- [ ] Tests generiert und ausgeführt
- [ ] Test-Results in `evidence/traces/` vorhanden
- [ ] `gap/matrix.csv` ausgefüllt
- [ ] `gap/gaps.md` mit priorisierten Lücken erstellt

## 🎯 Beispiel-Workflow

```powershell
# 1. Starte Swarm-System
.\swarm\start-swarm.ps1

# 2. UI-Explorer ausführen (Finance)
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer

# 3. Prüfe Outputs
ls evidence/screenshots/
ls swarm/handoffs/

# 4. Tests generieren (im Cursor-Chat)
# "Nutze Playwright planner agent für /swarm/handoffs/ui-explorer-finance-*.md"

# 5. Tests ausführen
npx playwright test --config=playwright.swarm.config.ts

# 6. GAP-Analyse (im Cursor-Chat)
# "Fülle gap/matrix.csv basierend auf Evidence aus"
```

## 🆘 Troubleshooting

### Frontend nicht erreichbar

```powershell
# Prüfe ob Frontend läuft
curl http://localhost:3000/health

# Prüfe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-frontend

# Prüfe ob Port belegt ist
netstat -ano | findstr :3000
```

### UI-Explorer Fehler

```powershell
# Prüfe Python-Dependencies
pip list | Select-String browser-use

# Prüfe ENV-Variablen
$env:NEUROERP_URL
$env:NEUROERP_USER
$env:NEUROERP_PASS

# Prüfe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-ui-explorer
```

### Tests schlagen fehl

```powershell
# Prüfe Traces
ls evidence/traces/

# Prüfe Screenshots
ls evidence/screenshots/

# Tests mit Debug-Output
npx playwright test --config=playwright.swarm.config.ts --debug
```

## 📚 Weitere Ressourcen

- **Quickstart**: `swarm/QUICKSTART.md`
- **README**: `swarm/README.md`
- **Setup-Status**: `SWARM-SETUP-COMPLETE.md`
- **Start-Script**: `swarm/start-swarm.ps1`

## ✨ Ready to Go!

Das System ist vollständig konfiguriert und einsatzbereit. Starte mit Schritt 1 und arbeite dich durch die Checkliste!


