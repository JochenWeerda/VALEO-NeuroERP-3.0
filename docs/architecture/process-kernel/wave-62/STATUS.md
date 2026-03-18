# Wave 62: Process Templates + Workflow Deadline Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-18
**Tests:** 132 passed, 0 failed, 0 skipped

## Neue Module

### `app/core/process_template_contracts.py`
- `TemplateTyp` (STANDARD, SAISONAL, TENANT_SPEZIFISCH, REGULATORISCH)
- `TemplateStatus` (ENTWURF, AKTIV, ARCHIVIERT, VERALTET)
- `InstanzierungsStatus` (ERFOLGREICH, FEHLGESCHLAGEN, VALIDIERUNGSFEHLER)
- `ProzessSchritt_Template` — Einzelner Prozessschritt mit Pflicht-Flag und Zeitschätzung
- `ProzessTemplate` — Template mit `ist_verwendbar()`, `pflicht_schritte()`, `geschaetzte_gesamtdauer_minuten()`
- `InstanzierungsErgebnis` — Ergebnis einer Template-Instanzierung
- `instanziere_template()` — Validierung und Instanzierung mit Parameterprüfung
- `get_default_templates()` — PT-001 (Kontrakt, AKTIV), PT-002 (Settlement, AKTIV), PT-003 (VERALTET)

### `app/core/workflow_deadline_contracts.py`
- `DeadlineTyp` (HART, WEICH, GESETZLICH, SLA)
- `DeadlineStatus` (AUSSTEHEND, ERFUELLT, VERLETZT, ESKALIERT)
- `EskalationsStufe` (STUFE_1 <60min, STUFE_2 60–240min, STUFE_3 240–1440min, KRITISCH ≥1440min)
- `WorkflowDeadline` — mit `verbleibende_minuten()`, `ist_verletzt()`, `berechne_eskalations_stufe()`
- `DeadlineMonitor` — mit `verletzte_deadlines()`, `kritische_deadlines()`, `sla_einhaltungs_rate_pct()`
- `get_default_deadline_monitor()` — DM-001 mit 6 Deadlines (3 verletzt, 1 kritisch)

## Neue Endpoints (`app/api/v1/endpoints/process_kernel_api.py`)

| Method | Path | Beschreibung |
|--------|------|--------------|
| GET | `/api/v1/process/template/vorlagen` | Alle Prozess-Templates inkl. Verwendbarkeit |
| POST | `/api/v1/process/template/instanziere` | Template instanzieren mit Parametervalidierung |
| GET | `/api/v1/process/deadline/monitor` | Deadline-Monitor mit SLA-Rate |
| POST | `/api/v1/process/deadline/pruefe-eskalation` | Einzelne Deadline auf Eskalationsstufe prüfen |

## Testabdeckung (132 Tests)

- Enum-Werte: 6 Tests
- `ProzessSchritt_Template` Defaults/Werte: 2 Tests
- `ProzessTemplate.ist_verwendbar()`: 4 Tests
- `ProzessTemplate.pflicht_schritte()`: 5 Tests
- `ProzessTemplate.geschaetzte_gesamtdauer_minuten()`: 4 Tests
- `instanziere_template()` Logik: 13 Tests
- Default Templates PT-001/PT-002/PT-003: 20 Tests
- `InstanzierungsErgebnis` Dataclass: 2 Tests
- `WorkflowDeadline.verbleibende_minuten()`: 4 Tests
- `WorkflowDeadline.ist_verletzt()`: 6 Tests
- `WorkflowDeadline.berechne_eskalations_stufe()`: 13 Tests
- `DeadlineMonitor.verletzte_deadlines()`: 6 Tests
- `DeadlineMonitor.kritische_deadlines()`: 4 Tests
- `DeadlineMonitor.sla_einhaltungs_rate_pct()`: 8 Tests
- Default Monitor Detail-Checks: 14 Tests
- API Endpoint Smoke Tests: 12 Tests
