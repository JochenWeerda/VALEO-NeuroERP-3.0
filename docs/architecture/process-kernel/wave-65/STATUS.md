# Wave 65 - Exception Patterns + Remediation Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-18
**Tests:** 155 bestanden, 0 Fehler

## Scope

Wave 65 liefert Mustererkennung fuer Ausnahmen und Remediation-Contracts fuer strukturierte Gegenmassnahmen.

## Zielbild

Fehlerklassifikation und Remediation-Playbooks sollen als standardisierte Kernel-Contracts fuer Betrieb und Support verfuegbar sein.

## Lieferumfang

### `app/core/process_exception_pattern_contracts.py`

- `AusnahmeMuster`
- `AusnahmeSchwere`
- `MusterErkennungsKonfidenz`
- `AusnahmeSignatur.erkenne_muster()`
- `klassifiziere_ausnahme()`
- `get_default_ausnahme_signaturen()`

### `app/core/workflow_remediation_contracts.py`

- `RemediationsTyp`
- `RemediationsStatus`
- `RemediationsAktion`
- `RemediationsPlaybook.erfolgsrate_pct()`
- `RemediationsPlaybook.automatische_schritte()`
- `RemediationsVorschlag.ist_aktiv()`
- `get_default_playbooks()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/exception/signaturen` | Liste aller Ausnahme-Signaturen |
| POST | `/process/exception/klassifiziere` | Fehler klassifizieren |
| GET | `/process/remediation/playbooks` | Liste aller Remediation-Playbooks |
| POST | `/process/remediation/pruefe-playbook` | Playbook-Details abrufen |

## Abnahmekriterien

- Ausnahme-Signaturen erkennen Muster ueber Schluesselwoerter und Code-Praefixe reproduzierbar.
- Remediation-Playbooks liefern Erfolgsraten, automatische Schritte und aktive Vorschlaege korrekt.
- Default-Signaturen und Default-Playbooks stehen bereit.
- Die vier API-Endpunkte liefern Klassifikation und Remediation-Funktionen.

## Tests

**Anzahl:** 155

## Status

`abgeschlossen`
Stand: 2026-03-18
