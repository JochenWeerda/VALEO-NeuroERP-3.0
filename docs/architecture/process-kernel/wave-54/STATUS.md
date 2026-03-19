# Wave 54 - Retry Policies + Workflow Checkpoint Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-16
**Tests:** 150 gruen, 0 Fehler

## Scope

Wave 54 liefert Retry-Strategien fuer fehlertolerante Verarbeitung und Checkpoint-Contracts fuer Wiederherstellungspunkte in Workflows.

## Zielbild

Der Kernel stellt Wiederholungslogik und Recovery-Punkte als standardisierte, testbare Domain-Bausteine bereit.

## Lieferumfang

### `app/core/process_retry_contracts.py`

- `RetryStrategie` mit fuenf Strategien
- `RetryStatus` mit fuenf Statuswerten
- `RetryRegel.berechne_verzoegerung()`
- `RetryZustand.kann_nochmal_versuchen()`
- `RetryZustand.naechsten_versuch_planen()`
- `get_default_retry_regeln()` mit fuenf Regeln

### `app/core/workflow_checkpoint_contracts_wave54.py`

- `CheckpointTyp` mit vier Werten
- `CheckpointStatus` mit vier Werten
- `WorkflowCheckpoint.ist_verwendbar()`
- `CheckpointSequenz.aktuellster_checkpoint()`
- `CheckpointSequenz.wiederherstellungs_punkt()`
- `get_default_checkpoint_sequenzen()` mit drei Demo-Sequenzen

### FastAPI-Endpunkte

- `GET /api/v1/process-kernel/retry/regeln`
- `POST /api/v1/process-kernel/retry/berechne-verzoegerung`
- `GET /api/v1/process-kernel/checkpoint/sequenzen`
- `POST /api/v1/process-kernel/checkpoint/wiederherstellungspunkt`

## Abnahmekriterien

- Alle fuenf Retry-Strategien berechnen reproduzierbare Verzoegerungen mit Cap-Verhalten.
- Checkpoints liefern den aktuellsten verwendbaren Stand sowie gueltige Wiederherstellungspunkte.
- Fuenf Retry-Regeln und drei Demo-Sequenzen sind als Default verfuegbar.
- Die vier API-Endpunkte stellen Retry- und Checkpoint-Funktionen bereit.

## Tests

| Bereich | Tests |
|---------|-------|
| RetryStrategie/Status Enums | 13 |
| `berechne_verzoegerung()` | 33 |
| `kann_nochmal_versuchen()` | 9 |
| `naechsten_versuch_planen()` | 13 |
| `get_default_retry_regeln()` | 15 |
| CheckpointTyp/Status Enums | 10 |
| `ist_verwendbar()` | 6 |
| `aktuellster_checkpoint()` | 8 |
| `wiederherstellungs_punkt()` | 10 |
| `get_default_checkpoint_sequenzen()` | 19 |
| Edge Cases + Integration | 14 |
| Gesamt | 150 |

## Status

`abgeschlossen`
Stand: 2026-03-16
