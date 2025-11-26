# Valero NeuroERP - Swarm Testing & GAP Analysis

Dieses Verzeichnis enthält die Infrastruktur für das Multi-Agent-System zur automatisierten Testing und GAP-Analyse von Valero NeuroERP.

## Übersicht

Das Swarm-System besteht aus mehreren spezialisierten Agenten, die zusammenarbeiten, um:
1. Das UI automatisch zu explorieren
2. E2E-Tests zu generieren und auszuführen
3. GAP-Analysen gegen ERP-Referenztaxonomien durchzuführen
4. Fehlende Funktionen systematisch zu schließen

## Schnellstart

### 1. Umgebungsvariablen setzen

Erstelle eine `.env` Datei im Root-Verzeichnis:

```bash
NEUROERP_URL=http://localhost:3000
NEUROERP_USER=testuser
NEUROERP_PASS=testpass
```

### 2. Swarm-System starten

```bash
# Frontend + Tests + UI-Explorer starten
docker compose -f docker-compose.swarm.yml up --build

# Nur Tests ausführen (Frontend muss bereits laufen)
docker compose -f docker-compose.swarm.yml up neuroerp-tests

# Nur UI-Explorer starten
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer
```

### 3. Lokale Tests (ohne Docker)

```bash
# Playwright Tests
npx playwright test --config=playwright.swarm.config.ts

# UI Explorer (benötigt Python + browser-use)
python swarm/ui_explorer.py
```

## Ordnerstruktur

```
/swarm
  /missions          # Mission-Briefs für Agenten
  /handoffs          # Übergabe-Notizen zwischen Rollen
/tests
  /e2e               # Playwright E2E-Tests
  /seed              # Seed-Tests und Utilities
/evidence
  /screenshots       # UI-Explorer Screenshots
  /traces            # Playwright Traces/Videos
/specs               # Test-Pläne (von Playwright Planner)
/gap
  capability-model.md  # ERP-Referenztaxonomie
  matrix.csv          # Capability-Matrix
  gaps.md             # Priorisierte GAP-Liste
/extensions
  /modules           # Custom-Module
  /integrations      # Integration-Adapter
```

## Agent-Rollen

### UI-Explorer
- **Script**: `swarm/ui_explorer.py`
- **Output**: Screenshots + Handoff-Notizen
- **Nutzt**: browser-use für semantische Browser-Exploration

### Test-Planner
- **Input**: UI-Explorer Handoffs
- **Output**: Test-Pläne in `/specs/*.md`
- **Nutzt**: Playwright Planner Agent

### Test-Generator
- **Input**: Test-Pläne
- **Output**: Playwright-Tests in `/tests/e2e/*.spec.ts`
- **Nutzt**: Playwright Generator Agent

### Test-Healer
- **Input**: Failing Tests
- **Output**: Fixes + Traces
- **Nutzt**: Playwright Healer Agent

### GAP-Analyst
- **Input**: Screenshots + Evidence
- **Output**: `/gap/matrix.csv` + `/gap/gaps.md`
- **Mappt**: Capabilities auf ERP-Referenztaxonomie

### Feature-Engineer
- **Input**: GAP-Liste
- **Output**: Code/Config in `/extensions/`
- **Klassifiziert**: Typ A (Config), B (Integration), C (Module), D (UX)

## Workflow

1. **Swarm-Planner** erstellt Mission in `/swarm/missions/*.md`
2. **UI-Explorer** explorert Module, erstellt Screenshots + Handoff
3. **Test-Planner** erstellt Test-Plan aus Handoff
4. **Test-Generator** generiert Playwright-Tests
5. **Test-Healer** führt Tests aus, repariert Fehler
6. **GAP-Analyst** analysiert Evidence, füllt Matrix
7. **Feature-Engineer** schließt Lücken
8. **Integrator** merged und testet

## Beispiel-Missions

- `swarm/missions/ui_explore_finance.md` - Finance Module Exploration
- `swarm/missions/ui_explore_procurement.md` - Procurement Module Exploration
- `swarm/missions/ui_explore_sales.md` - Sales Module Exploration

## Konfiguration

### Cursor Rules
Die `.cursorrules` Datei im Root definiert die Regeln für alle Agenten.

### Docker Compose
`docker-compose.swarm.yml` definiert die Services für Frontend, Tests und UI-Explorer.

### Playwright Config
`playwright.swarm.config.ts` ist die Playwright-Config für Swarm-Tests.

## Troubleshooting

### Frontend nicht erreichbar
- Prüfe Health-Endpoint: `curl http://localhost:3000/health`
- Prüfe Docker-Logs: `docker compose -f docker-compose.swarm.yml logs neuroerp-frontend`

### Tests schlagen fehl
- Prüfe Traces in `/evidence/traces/`
- Prüfe Screenshots in `/evidence/screenshots/`
- Nutze Test-Healer Agent

### UI-Explorer funktioniert nicht
- Prüfe Python-Dependencies: `pip install -r swarm/requirements.ui-explorer.txt`
- Prüfe Browser-Use Installation
- Prüfe ENV-Variablen

## Nächste Schritte

1. Starte erste Mission: `swarm/missions/ui_explore_finance.md`
2. Prüfe Handoff-Notizen in `/swarm/handoffs/`
3. Generiere Tests aus Handoffs
4. Führe GAP-Analyse durch
5. Priorisiere und schließe Lücken

## Weitere Ressourcen

- [Playwright Agentic Testing](https://playwright.dev/docs/agentic-testing)
- [Browser-Use Documentation](https://github.com/browser-use/browser-use)
- [Cursor Rules Documentation](https://cursor.sh/docs)

