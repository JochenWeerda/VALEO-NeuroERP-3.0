# Wave 54 — Retry Policies + Workflow Checkpoint Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-16
**Tests:** 150 grün, 0 Fehler

## Module

### `app/core/process_retry_contracts.py`
- `RetryStrategie` (5 Werte): KEIN_RETRY, FESTER_INTERVALL, LINEARES_BACKOFF, EXPONENTIELLES_BACKOFF, JITTER
- `RetryStatus` (5 Werte): AUSSTEHEND, LAUFEND, ERFOLGREICH, ERSCHOEPFT, AUFGEGEBEN
- `RetryRegel.berechne_verzoegerung(versuch_nummer)` — backoff-Berechnung für alle Strategien mit Cap
- `RetryZustand.kann_nochmal_versuchen(regel)` — Prüfung ob Retry möglich
- `RetryZustand.naechsten_versuch_planen(regel, jetzt)` — immutable Zustandsübergang
- `get_default_retry_regeln()` — 5 vordefinierte Regeln (RR-001..RR-005)

### `app/core/workflow_checkpoint_contracts_wave54.py`
- `CheckpointTyp` (4 Werte): AUTOMATISCH, MANUELL, VOR_KRITISCHEM_SCHRITT, NACH_FEHLER
- `CheckpointStatus` (4 Werte): AKTUELL, VERALTET, WIEDERHERGESTELLT, KORRUPT
- `WorkflowCheckpoint.ist_verwendbar()` — True für AKTUELL und WIEDERHERGESTELLT
- `CheckpointSequenz.aktuellster_checkpoint()` — höchster verwendbarer Schritt
- `CheckpointSequenz.wiederherstellungs_punkt(ab_schritt)` — Recovery-Punkt <= ab_schritt
- `get_default_checkpoint_sequenzen()` — 3 Demo-Sequenzen (Kontrakt, Settlement, leer)

## FastAPI Endpoints (appended to `process_kernel_api.py`)
- `GET /api/v1/process-kernel/retry/regeln` — alle 5 Retry-Regeln
- `POST /api/v1/process-kernel/retry/berechne-verzoegerung` — Verzögerung für Strategie+Versuch
- `GET /api/v1/process-kernel/checkpoint/sequenzen` — Checkpoint-Sequenzen mit aktuellem Schritt
- `POST /api/v1/process-kernel/checkpoint/wiederherstellungspunkt` — Recovery-Checkpoint für Instanz+Schritt

## Testabdeckung (150 Tests)
| Bereich | Tests |
|---------|-------|
| RetryStrategie/Status Enums | 13 |
| berechne_verzoegerung KEIN_RETRY | 5 |
| berechne_verzoegerung FESTER_INTERVALL | 6 |
| berechne_verzoegerung LINEARES_BACKOFF | 7 |
| berechne_verzoegerung EXPONENTIELLES_BACKOFF | 8 |
| berechne_verzoegerung JITTER | 7 |
| kann_nochmal_versuchen | 9 |
| naechsten_versuch_planen | 13 |
| get_default_retry_regeln | 15 |
| CheckpointTyp/Status Enums | 10 |
| ist_verwendbar | 6 |
| aktuellster_checkpoint | 8 |
| wiederherstellungs_punkt | 10 |
| get_default_checkpoint_sequenzen | 19 |
| Edge cases + Integration | 14 |
| **Gesamt** | **150** |
