# Wave 61 - Tenant Quota Management + Workflow Pause/Resume Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 166 gruen, 0 Fehler, 0 skipped

## Scope

Wave 61 fuehrt Tenant-Quotas fuer Ressourcengrenzen und Pause/Resume-Contracts fuer gesteuerte Workflow-Unterbrechungen ein.

## Zielbild

Mandantenlimits und Pausensteuerung sollen als standardisierte, auswertbare Kernel-Contracts zur Verfuegung stehen.

## Lieferumfang

### `app/core/process_quota_contracts.py`

- `QuotaTyp`
- `QuotaStatus`
- `QuotaAktionsBei`
- `QuotaRegel`
- `TenantQuotaVerbrauch`
- `QuotaUebersicht`
- `get_default_quota_uebersicht()`

### `app/core/workflow_pause_contracts.py`

- `PauseGrund`
- `PauseStatus`
- `ResumeAusloeser`
- `WorkflowPause`
- `PauseVerlauf`
- `get_default_pause_verlaeufe()`

### FastAPI-Endpunkte

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/process/quota/uebersicht` | Quota-Uebersicht mit Status pro Typ |
| POST | `/process/quota/pruefe-verbrauch` | Statusberechnung fuer beliebigen Verbrauchswert |
| GET | `/process/pause/verlaeufe` | Alle Pause-Verlaeufe mit Aggregaten |
| POST | `/process/pause/pruefe-ueberfaellig` | Ueberfaellige Pausen fuer einen Verlauf |

## Abnahmekriterien

- Quota-Status werden fuer Schwellwerte 80, 95 und 100 Prozent korrekt berechnet.
- Pause-Verlaeufe liefern aktive, ueberfaellige und aggregierte Pausenzeiten.
- Eine Default-Quota-Uebersicht und Default-Pause-Verlaeufe sind verfuegbar.
- Die vier API-Endpunkte liefern Quota- und Pause-Funktionen.

## Tests

**Anzahl:** 166

## Status

`abgeschlossen`
Stand: 2026-03-16
