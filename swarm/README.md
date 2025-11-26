***REMOVED*** Valero NeuroERP - Swarm Testing & GAP Analysis

Dieses Verzeichnis enthält die Infrastruktur für das Multi-Agent-System zur automatisierten Testing und GAP-Analyse von Valero NeuroERP.

***REMOVED******REMOVED*** Übersicht

Das Swarm-System besteht aus mehreren spezialisierten Agenten, die zusammenarbeiten, um:
1. Das UI automatisch zu explorieren
2. E2E-Tests zu generieren und auszuführen
3. GAP-Analysen gegen ERP-Referenztaxonomien durchzuführen
4. Fehlende Funktionen systematisch zu schließen

***REMOVED******REMOVED*** Schnellstart

***REMOVED******REMOVED******REMOVED*** 1. Umgebungsvariablen setzen

Erstelle eine `.env` Datei im Root-Verzeichnis:

```bash
NEUROERP_URL=http://localhost:3000
NEUROERP_USER=testuser
NEUROERP_PASS=testpass
```

***REMOVED******REMOVED******REMOVED*** 2. Swarm-System starten

```bash
***REMOVED*** Frontend + Tests + UI-Explorer starten
docker compose -f docker-compose.swarm.yml up --build

***REMOVED*** Nur Tests ausführen (Frontend muss bereits laufen)
docker compose -f docker-compose.swarm.yml up neuroerp-tests

***REMOVED*** Nur UI-Explorer starten
docker compose -f docker-compose.swarm.yml up neuroerp-ui-explorer
```

***REMOVED******REMOVED******REMOVED*** 3. Lokale Tests (ohne Docker)

```bash
***REMOVED*** Playwright Tests
npx playwright test --config=playwright.swarm.config.ts

***REMOVED*** UI Explorer (benötigt Python + browser-use)
python swarm/ui_explorer.py
```

***REMOVED******REMOVED*** Ordnerstruktur

```
/swarm
  /missions          ***REMOVED*** Mission-Briefs für Agenten
  /handoffs          ***REMOVED*** Übergabe-Notizen zwischen Rollen
/tests
  /e2e               ***REMOVED*** Playwright E2E-Tests
  /seed              ***REMOVED*** Seed-Tests und Utilities
/evidence
  /screenshots       ***REMOVED*** UI-Explorer Screenshots
  /traces            ***REMOVED*** Playwright Traces/Videos
/specs               ***REMOVED*** Test-Pläne (von Playwright Planner)
/gap
  capability-model.md  ***REMOVED*** ERP-Referenztaxonomie
  matrix.csv          ***REMOVED*** Capability-Matrix
  gaps.md             ***REMOVED*** Priorisierte GAP-Liste
/extensions
  /modules           ***REMOVED*** Custom-Module
  /integrations      ***REMOVED*** Integration-Adapter
```

***REMOVED******REMOVED*** Agent-Rollen

***REMOVED******REMOVED******REMOVED*** UI-Explorer
- **Script**: `swarm/ui_explorer.py`
- **Output**: Screenshots + Handoff-Notizen
- **Nutzt**: browser-use für semantische Browser-Exploration

***REMOVED******REMOVED******REMOVED*** Test-Planner
- **Input**: UI-Explorer Handoffs
- **Output**: Test-Pläne in `/specs/*.md`
- **Nutzt**: Playwright Planner Agent

***REMOVED******REMOVED******REMOVED*** Test-Generator
- **Input**: Test-Pläne
- **Output**: Playwright-Tests in `/tests/e2e/*.spec.ts`
- **Nutzt**: Playwright Generator Agent

***REMOVED******REMOVED******REMOVED*** Test-Healer
- **Input**: Failing Tests
- **Output**: Fixes + Traces
- **Nutzt**: Playwright Healer Agent

***REMOVED******REMOVED******REMOVED*** GAP-Analyst
- **Input**: Screenshots + Evidence
- **Output**: `/gap/matrix.csv` + `/gap/gaps.md`
- **Mappt**: Capabilities auf ERP-Referenztaxonomie

***REMOVED******REMOVED******REMOVED*** Feature-Engineer
- **Input**: GAP-Liste
- **Output**: Code/Config in `/extensions/`
- **Klassifiziert**: Typ A (Config), B (Integration), C (Module), D (UX)

***REMOVED******REMOVED*** Workflow

1. **Swarm-Planner** erstellt Mission in `/swarm/missions/*.md`
2. **UI-Explorer** explorert Module, erstellt Screenshots + Handoff
3. **Test-Planner** erstellt Test-Plan aus Handoff
4. **Test-Generator** generiert Playwright-Tests
5. **Test-Healer** führt Tests aus, repariert Fehler
6. **GAP-Analyst** analysiert Evidence, füllt Matrix
7. **Feature-Engineer** schließt Lücken
8. **Integrator** merged und testet

***REMOVED******REMOVED*** Beispiel-Missions

- `swarm/missions/ui_explore_finance.md` - Finance Module Exploration
- `swarm/missions/ui_explore_procurement.md` - Procurement Module Exploration
- `swarm/missions/ui_explore_sales.md` - Sales Module Exploration

***REMOVED******REMOVED*** Konfiguration

***REMOVED******REMOVED******REMOVED*** Cursor Rules
Die `.cursorrules` Datei im Root definiert die Regeln für alle Agenten.

***REMOVED******REMOVED******REMOVED*** Docker Compose
`docker-compose.swarm.yml` definiert die Services für Frontend, Tests und UI-Explorer.

***REMOVED******REMOVED******REMOVED*** Playwright Config
`playwright.swarm.config.ts` ist die Playwright-Config für Swarm-Tests.

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Frontend nicht erreichbar
- Prüfe Health-Endpoint: `curl http://localhost:3000/health`
- Prüfe Docker-Logs: `docker compose -f docker-compose.swarm.yml logs neuroerp-frontend`

***REMOVED******REMOVED******REMOVED*** Tests schlagen fehl
- Prüfe Traces in `/evidence/traces/`
- Prüfe Screenshots in `/evidence/screenshots/`
- Nutze Test-Healer Agent

***REMOVED******REMOVED******REMOVED*** UI-Explorer funktioniert nicht
- Prüfe Python-Dependencies: `pip install -r swarm/requirements.ui-explorer.txt`
- Prüfe Browser-Use Installation
- Prüfe ENV-Variablen

***REMOVED******REMOVED*** Nächste Schritte

1. Starte erste Mission: `swarm/missions/ui_explore_finance.md`
2. Prüfe Handoff-Notizen in `/swarm/handoffs/`
3. Generiere Tests aus Handoffs
4. Führe GAP-Analyse durch
5. Priorisiere und schließe Lücken

***REMOVED******REMOVED*** Weitere Ressourcen

- [Playwright Agentic Testing](https://playwright.dev/docs/agentic-testing)
- [Browser-Use Documentation](https://github.com/browser-use/browser-use)
- [Cursor Rules Documentation](https://cursor.sh/docs)

