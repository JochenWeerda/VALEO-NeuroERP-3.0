# Wave 62 - Process Templates + Workflow Deadline Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-18
**Tests:** 132 passed, 0 failed, 0 skipped

## Scope

Wave 62 liefert Prozessvorlagen fuer standardisierte Instanziierung und Deadline-Contracts fuer Fristen, Eskalation und SLA-Ueberwachung.

## Zielbild

Vorlagen und Deadlines sollen als wiederverwendbare Kernel-Contracts fuer operative Prozesssteuerung verfuegbar sein.

## Lieferumfang

### `app/core/process_template_contracts.py`

- `TemplateTyp`
- `TemplateStatus`
- `InstanzierungsStatus`
- `ProzessSchrittTemplate`
- `ProzessTemplate`
- `InstanzierungsErgebnis`
- `instanziere_template()`
- `get_default_templates()`

### `app/core/workflow_deadline_contracts.py`

- `DeadlineTyp`
- `DeadlineStatus`
- `EskalationsStufe`
- `WorkflowDeadline`
- `DeadlineMonitor`
- `get_default_deadline_monitor()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process/template/vorlagen` | Alle Prozess-Templates inklusive Verwendbarkeit |
| POST | `/api/v1/process/template/instanziere` | Instanziert Template mit Parametervalidierung |
| GET | `/api/v1/process/deadline/monitor` | Deadline-Monitor mit SLA-Rate |
| POST | `/api/v1/process/deadline/pruefe-eskalation` | Prueft Eskalationsstufe einer Deadline |

## Abnahmekriterien

- Templates validieren Pflichtparameter und liefern reproduzierbare Instanzierungsergebnisse.
- Deadlines berechnen verbleibende Minuten, Verletzungen und Eskalationsstufen korrekt.
- Default-Templates und ein Default-Deadline-Monitor stehen bereit.
- Die vier API-Endpunkte liefern Template- und Deadline-Funktionen.

## Tests

**Anzahl:** 132

## Status

`abgeschlossen`
Stand: 2026-03-18
