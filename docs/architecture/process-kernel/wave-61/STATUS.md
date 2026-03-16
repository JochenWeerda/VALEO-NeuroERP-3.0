# Wave 61 — Tenant Quota Management + Workflow Pause/Resume Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-16
**Tests:** 166 grün, 0 Fehler, 0 skipped

## Module

### `app/core/process_quota_contracts.py`
- `QuotaTyp` (5 Werte): API_ANFRAGEN, SPEICHER_MB, BENUTZER, DOKUMENTE, WORKFLOW_INSTANZEN
- `QuotaStatus` (4 Werte): NORMAL, WARNUNG, KRITISCH, ERSCHOEPFT
- `QuotaAktionsBei` (3 Werte): WARNUNG, KRITISCH, ERSCHOEPFT
- `QuotaRegel`: Schwellenwert-Berechnung (80%/95%/100%), `berechne_status()`, `verfuegbar()`
- `TenantQuotaVerbrauch`: Tenant-spezifischer Verbrauchsstand
- `QuotaUebersicht`: `status_fuer_typ()`, `kritische_quotas()`
- `get_default_quota_uebersicht()`: Referenz-Tenant mit 5 Quota-Typen

### `app/core/workflow_pause_contracts.py`
- `PauseGrund` (6 Werte): BENUTZER_ANGEFRAGT, EXTERNE_ABHAENGIGKEIT, RESSOURCE_NICHT_VERFUEGBAR, WARTUNG, FEHLER_UNTERSUCHUNG, GENEHMIGUNG_AUSSTEHEND
- `PauseStatus` (3 Werte): AKTIV, FORTGESETZT, ABGEBROCHEN
- `ResumeAusloeser` (4 Werte): MANUELL, AUTOMATISCH, SIGNAL, ADMIN
- `WorkflowPause`: `ist_aktiv()`, `ist_ueberfaellig()`, `pause_dauer_minuten()`
- `PauseVerlauf`: `aktive_pause()`, `gesamt_pause_minuten()`, `ueberfaellige_pausen()`
- `get_default_pause_verlaeufe()`: PV-001 (gemischt), PV-002 (abgebrochen)

## Endpoints (appended to `app/api/v1/endpoints/process_kernel_api.py`)

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET  | `/process/quota/uebersicht` | Quota-Übersicht mit Status pro Typ |
| POST | `/process/quota/pruefe-verbrauch` | Statusberechnung für beliebigen Verbrauchswert |
| GET  | `/process/pause/verlaeufe` | Alle Pause-Verläufe mit Aggregaten |
| POST | `/process/pause/pruefe-ueberfaellig` | Überfällige Pausen für einen Verlauf |

## Referenz-Szenarien

### Quota (TENANT-A, 2026-03-16 10:00)
| Typ | Verbrauch | Limit | % | Status |
|-----|-----------|-------|---|--------|
| API_ANFRAGEN | 7.500 | 10.000 | 75% | NORMAL |
| SPEICHER_MB | 42.000 | 51.200 | 82% | WARNUNG |
| BENUTZER | 48 | 50 | 96% | KRITISCH |
| DOKUMENTE | 100.500 | 100.000 | >100% | ERSCHOEPFT |
| WORKFLOW_INSTANZEN | 500 | 1.000 | 50% | NORMAL |

Kritische Quotas: BENUTZER, DOKUMENTE

### Pause-Verläufe (2026-03-16 10:00)
| Pause | Status | Dauer | Überfällig |
|-------|--------|-------|-----------|
| PA-001 (PV-001) | FORTGESETZT | 60 min | Nein |
| PA-002 (PV-001) | AKTIV (90 min, max=60) | 90 min | **Ja** |
| PA-003 (PV-002) | ABGEBROCHEN | 0 min | Nein |

PV-001 Gesamt-Pause: 150 min | PV-002 Gesamt-Pause: 0 min (ausgeschlossen)

## Regressionsstatus
- Wave 61: 166/166 Tests grün
- Gesamt (ohne test_neuroassist_runtime.py): 4654 passed, 3 pre-existing failures (runtime_operations.py datetime import — Wave 61 unrelated)
