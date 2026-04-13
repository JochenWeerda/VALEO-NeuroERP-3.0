# NÃ¤chste Schritte - Swarm System

## âœ… Setup abgeschlossen

Alle Komponenten sind konfiguriert und einsatzbereit!

## ðŸš€ Schritt-fÃ¼r-Schritt Anleitung

### Schritt 1: Umgebungsvariablen âœ…

Die Datei `.env.swarm` wurde erstellt mit:
- `NEUROERP_URL=http://localhost:3000`
- `NEUROERP_USER=admin`
- `NEUROERP_PASS=admin123`

**Falls du andere Credentials benÃ¶tigst**, bearbeite `.env.swarm` oder setze ENV-Variablen:

```powershell
# PowerShell
$env:NEUROERP_URL="http://localhost:3000"
$env:NEUROERP_USER="admin"
$env:NEUROERP_PASS="admin123"
```

### Schritt 2: Frontend prÃ¼fen/starten

**Option A: Bestehendes Frontend nutzen (empfohlen)**

Wenn das Frontend bereits auf `localhost:3000` lÃ¤uft:

```powershell
# PrÃ¼fe Health-Endpoint
curl http://localhost:3000/health
# oder
curl http://localhost:3000/health.html
```

**Option B: Neues Frontend fÃ¼r Swarm starten**

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

# UI-Explorer ausfÃ¼hren
python swarm/ui_explorer.py
```

**Erwartete Outputs:**
- ðŸ“¸ Screenshots in `evidence/screenshots/finance_flow_*.json`
- ðŸ“ Handoff-Notizen in `swarm/handoffs/ui-explorer-finance-*.md`

### Schritt 4: Tests generieren und ausfÃ¼hren

**Playwright Tests (Seed-Test):**

```powershell
# Tests mit Swarm-Config ausfÃ¼hren
npx playwright test --config=playwright.swarm.config.ts

# Oder mit Docker:
docker compose -f docker-compose.swarm.yml up neuroerp-tests
```

**Playwright Agentic Testing (Planner â†’ Generator â†’ Healer):**

1. **Test-Plan erstellen** (im Cursor-Chat):
   ```
   Nutze Playwright planner agent.
   Erstelle Testplan fÃ¼r /swarm/handoffs/ui-explorer-finance.md.
   Output nach /specs/finance.md.
   ```

2. **Tests generieren** (im Cursor-Chat):
   ```
   Nutze generator agent, verwandle /specs/finance.md in Playwright-Tests
   unter /tests/e2e/finance/*.spec.ts.
   Nutze tests/seed/seed.spec.ts als Beispiel.
   ```

3. **Tests ausfÃ¼hren und heilen**:
   ```powershell
   npx playwright test --config=playwright.swarm.config.ts
   # Healer repariert automatisch flaky/failing tests
   ```

**Erwartete Outputs:**
- ðŸ“Š Test-Results in `evidence/traces/results.json`
- ðŸ“¹ HTML-Reports in `evidence/traces/html-report/`
- ðŸŽ¬ Videos/Traces bei Fehlern in `evidence/traces/`

### Schritt 5: GAP-Analyse durchfÃ¼hren

**1. Evidence sammeln:**

```powershell
# PrÃ¼fe Screenshots
ls evidence/screenshots/

# PrÃ¼fe Handoff-Notizen
ls swarm/handoffs/

# PrÃ¼fe Test-Traces
ls evidence/traces/
```

**2. Matrix ausfÃ¼llen:**

Ã–ffne `gap/matrix.csv` und fÃ¼lle fÃ¼r jede Capability:
- **NeuroERP Status**: `Yes` / `Partial` / `No` / `?`
- **Evidence Screenshot IDs**: Links zu Screenshots
- **Notes**: Beschreibung der LÃ¼cke
- **Comparable ERP baseline**: `SAP-Ã¤hnlich` / `Community ERP-Ã¤hnlich` / `Basic`

**3. GAP-Liste erstellen:**

Ã–ffne `gap/gaps.md` und erstelle priorisierte Liste mit:
- **GAP-ID**: Eindeutige ID (z.B. `FIN-001`)
- **Status**: `Missing` / `Partial` / `Basic`
- **PrioritÃ¤t**: `P0` (Kritisch) / `P1` (Hoch) / `P2` (Mittel) / `P3` (Niedrig)
- **Typ**: `A` (Config) / `B` (Integration) / `C` (Module) / `D` (UX)

**4. Automatisierte Vor-BefÃ¼llung (optional):**

Im Cursor-Chat:
```
Nimm Evidence aus /evidence/screenshots und /swarm/handoffs/*.
FÃ¼lle gap/matrix.csv nach Capability-Modell aus gap/capability-model.md.
Markiere Unsicherheiten mit ?.
```

## ðŸ“‹ Checkliste

- [ ] `.env.swarm` erstellt/bearbeitet
- [ ] Frontend lÃ¤uft und Health-Endpoint funktioniert
- [ ] UI-Explorer ausgefÃ¼hrt (Finance Module)
- [ ] Screenshots in `evidence/screenshots/` vorhanden
- [ ] Handoff-Notizen in `swarm/handoffs/` vorhanden
- [ ] Tests generiert und ausgefÃ¼hrt
- [ ] Test-Results in `evidence/traces/` vorhanden
- [ ] `gap/matrix.csv` ausgefÃ¼llt
- [ ] `gap/gaps.md` mit priorisierten LÃ¼cken erstellt

## ðŸŽ¯ Beispiel-Workflow

```powershell
# 1. Starte Swarm-System
.\swarm\start-swarm.ps1

# 2. UI-Explorer ausfÃ¼hren (Finance)
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer

# 3. PrÃ¼fe Outputs
ls evidence/screenshots/
ls swarm/handoffs/

# 4. Tests generieren (im Cursor-Chat)
# "Nutze Playwright planner agent fÃ¼r /swarm/handoffs/ui-explorer-finance-*.md"

# 5. Tests ausfÃ¼hren
npx playwright test --config=playwright.swarm.config.ts

# 6. GAP-Analyse (im Cursor-Chat)
# "FÃ¼lle gap/matrix.csv basierend auf Evidence aus"
```

## ðŸ†˜ Troubleshooting

### Frontend nicht erreichbar

```powershell
# PrÃ¼fe ob Frontend lÃ¤uft
curl http://localhost:3000/health

# PrÃ¼fe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-frontend

# PrÃ¼fe ob Port belegt ist
netstat -ano | findstr :3000
```

### UI-Explorer Fehler

```powershell
# PrÃ¼fe Python-Dependencies
pip list | Select-String browser-use

# PrÃ¼fe ENV-Variablen
$env:NEUROERP_URL
$env:NEUROERP_USER
$env:NEUROERP_PASS

# PrÃ¼fe Docker-Logs
docker compose -f docker-compose.swarm.yml logs neuroerp-ui-explorer
```

### Tests schlagen fehl

```powershell
# PrÃ¼fe Traces
ls evidence/traces/

# PrÃ¼fe Screenshots
ls evidence/screenshots/

# Tests mit Debug-Output
npx playwright test --config=playwright.swarm.config.ts --debug
```

## ðŸ“š Weitere Ressourcen

- **Quickstart**: `swarm/QUICKSTART.md`
- **README**: `swarm/README.md`
- **Setup-Status**: `SWARM-SETUP-COMPLETE.md`
- **Start-Script**: `swarm/start-swarm.ps1`

## âœ¨ Ready to Go!

Das System ist vollstÃ¤ndig konfiguriert und einsatzbereit. Starte mit Schritt 1 und arbeite dich durch die Checkliste!



