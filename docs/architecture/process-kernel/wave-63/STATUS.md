# Wave 63 — Process Validation + Workflow Collaboration Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-18
**Tests:** 150 passed, 0 failed

## Neue Module

### `app/core/process_validation_contracts.py`
Business Rule Validation Engine mit:
- `ValidierungsSchwere`: FEHLER / WARNUNG / HINWEIS
- `RegelTyp`: PFLICHTFELD / WERTEBEREICH / FORMAT / QUERVERWEIS / GESCHAEFTSREGEL
- `ValidierungsStatus`: GUELTIG / UNGUELTIG / WARNUNG
- `ValidierungsRegel.pruefe()`: Regelauswertung pro Datensatz
- `validiere_daten()`: Batch-Auswertung mit Fehlerklassifizierung
- 5 Default-Regeln (VR-001..VR-005) für Lieferant, Menge, Preis, Querverweis, Kommentar

### `app/core/workflow_collaboration_contracts.py`
Multi-User Collaborative Decisions mit:
- `AbstimmungsTyp`: EINFACHE_MEHRHEIT / QUALIFIZIERTE_MEHRHEIT / EINSTIMMIGKEIT / VETO
- `StimmeTyp`: JA / NEIN / ENTHALTEN
- `KollaborationsEntscheidung.berechne_ergebnis()`: Abstimmungslogik nach Typ
- `KollaborationsEntscheidung.ausstehende_stimmer()`: Differenz ausstehender Stimmer
- `KollaborationsEntscheidung.beteiligung_pct()`: Beteiligungsquote
- 3 Default-Entscheidungen (E-001..E-003)

## Neue API-Endpunkte (an `process_kernel_api.py` angehängt)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/api/v1/process/validierung/regeln` | Alle Validierungsregeln |
| POST | `/api/v1/process/validierung/pruefe` | Datensatz gegen Regeln prüfen |
| GET | `/api/v1/process/kollaboration/entscheidungen` | Alle Kollaborationsentscheidungen |
| POST | `/api/v1/process/kollaboration/pruefe-ergebnis` | Einzelentscheidung berechnen |

## Testabdeckung

| Bereich | Tests |
|---------|-------|
| Enum-Smoke | 10 |
| ValidierungsRegel.pruefe() PFLICHTFELD | 9 |
| ValidierungsRegel.pruefe() WERTEBEREICH | 14 |
| ValidierungsRegel.pruefe() QUERVERWEIS | 6 |
| ValidierungsRegel.pruefe() FORMAT/GESCHAEFTSREGEL | 4 |
| validiere_daten() | 10 |
| Default-Regeln VR-001..VR-005 | 14 |
| KollaborationsEntscheidung helpers | 15 |
| berechne_ergebnis() VETO | 6 |
| berechne_ergebnis() EINSTIMMIGKEIT | 5 |
| berechne_ergebnis() EINFACHE_MEHRHEIT | 7 |
| berechne_ergebnis() QUALIFIZIERTE_MEHRHEIT | 6 |
| Default-Entscheidungen E-001..E-003 | 18 |
| Stimme / ValidierungsErgebnis Dataclass | 6 |
| FastAPI Endpoints (4 Endpunkte) | 20 |
| **Gesamt** | **150** |
