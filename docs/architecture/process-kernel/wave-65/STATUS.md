# Wave 65: Exception Patterns + Remediation Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-18
**Tests:** 155 bestanden, 0 Fehler

## Module

### `app/core/process_exception_pattern_contracts.py`
- `AusnahmeMuster` (7 Werte): TIMEOUT, DATENFEHLER, BERECHTIGUNGSFEHLER, RESSOURCENENGPASS, GESCHAEFTSREGELVERTOSS, INTEGRATIONSFEHLER, UNBEKANNT
- `AusnahmeSchwere` (4 Werte): KRITISCH, HOCH, MITTEL, NIEDRIG
- `MusterErkennungsKonfidenz` (4 Werte): SICHER (>=90 Punkte), WAHRSCHEINLICH (>=70), MOEGLICH (>=50), UNBEKANNT (<50)
- `AusnahmeSignatur.erkenne_muster()`: Scoring via Schlüsselwörter (+20 je Treffer) und Code-Präfixe (+50)
- `klassifiziere_ausnahme()`: Best-Match-Selektion über alle Signaturen
- `get_default_ausnahme_signaturen()`: 5 vorkonfigurierte Signaturen (AS-001..AS-005)

### `app/core/workflow_remediation_contracts.py`
- `RemediationsTyp` (3): AUTOMATISCH, HALBAUTOMATISCH, MANUELL
- `RemediationsStatus` (6): VORGESCHLAGEN, GENEHMIGT, LAUFEND, ABGESCHLOSSEN, FEHLGESCHLAGEN, ABGELEHNT
- `RemediationsAktion` (7): NEUSTART, ROLLBACK, RETRY, ESKALIEREN, CACHE_LEEREN, VERBINDUNG_RESET, MANUELL_EINGREIFEN
- `RemediationsPlaybook.erfolgsrate_pct()`: 100.0 wenn nie angewendet
- `RemediationsPlaybook.automatische_schritte()`: Nur auto=True, sortiert nach Reihenfolge
- `RemediationsVorschlag.ist_aktiv()`: True bei VORGESCHLAGEN/GENEHMIGT/LAUFEND
- `get_default_playbooks()`: 3 Playbooks (PB-001 Timeout 90%, PB-002 Datenfehler ~90.9%, PB-003 Ressource 100%)

## API-Endpunkte (angehängt an `process_kernel_api.py`)
| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/exception/signaturen` | Liste aller Ausnahme-Signaturen |
| POST | `/process/exception/klassifiziere` | Fehler klassifizieren |
| GET | `/process/remediation/playbooks` | Liste aller Remediation-Playbooks |
| POST | `/process/remediation/pruefe-playbook` | Playbook-Details abrufen |

## Testabdeckung
- 155 Tests in `tests/test_process_kernel_wave65_exception_remediation.py`
- Enum-Tests: 28
- AusnahmeSignatur scoring: 21
- klassifiziere_ausnahme: 11
- Default-Signaturen: 12
- KlassifizierungsErgebnis: 3
- RemediationsSchritt: 5
- RemediationsPlaybook construction: 4
- erfolgsrate_pct: 8
- automatische_schritte: 8
- RemediationsVorschlag: 6
- ist_aktiv: 6
- get_default_playbooks: 23
- FastAPI-Endpunkt-Integration: 10
