# Wave 59 - Consent Management + Workflow Trigger Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 142 gruen, 0 Fehler

## Scope

Wave 59 liefert Consent-Management fuer DSGVO-nahe Einwilligungen und Trigger-Contracts fuer regelbasierte Workflow-Aktivierung.

## Zielbild

Einwilligungen und Workflow-Trigger sollen als standardisierte, auswertbare Contracts fuer Datenschutz- und Aktivierungslogik bereitstehen.

## Lieferumfang

### Module

| Modul | Pfad | Beschreibung |
|-------|------|--------------|
| `process_consent_contracts` | `app/core/process_consent_contracts.py` | Consent Management und Datenverarbeitungsprotokolle |
| `workflow_trigger_contracts` | `app/core/workflow_trigger_contracts.py` | Workflow-Trigger-Bedingungen und Aktivierungsregeln |

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process/consent/register` | Default-Einwilligungsregister mit Aktivstatus |
| POST | `/api/v1/process/consent/pruefe` | Prueft gueltige Einwilligung fuer ein Subjekt |
| GET | `/api/v1/process/trigger/regeln` | Alle Workflow-Trigger-Regeln |
| POST | `/api/v1/process/trigger/pruefe-bedingungen` | Prueft Trigger-Bedingungen gegen Kontext |

## Abnahmekriterien

- Einwilligungen koennen Aktivstatus und Ablauf korrekt bestimmen.
- Trigger-Bedingungen werden fuer alle Operatoren robust gegen Kontextdaten geprueft.
- Default-Register und Default-Trigger sind verfuegbar.
- Die vier API-Endpunkte liefern Consent- und Trigger-Funktionen.

## Tests

| Bereich | Tests |
|---------|-------|
| Consent Enums und Statuslogik | 48 |
| Trigger-Bedingungen und Triggerlogik | 47 |
| Default-Datenpruefung | 24 |
| FastAPI-Endpunkte | 23 |
| Gesamt | 142 |

## Status

`abgeschlossen`
Stand: 2026-03-16
