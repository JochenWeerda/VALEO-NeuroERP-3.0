# Wave-48 Status

## Scope
Process Timeout Contracts + Workflow Batch Processing Contracts

## Zielbild

Wave 48 ergänzt den Process-Kernel um Fristenüberwachung und Massendatenverarbeitung:

1. **Process Timeout Contracts**: Timeout-Management für Workflow-Schritte mit 4 Typen
   (RELATIV/ABSOLUT/GESCHAEFTSZEIT/SLA_GEBUNDEN), Mahnphasen-Schwellwert (`mahngrenze_pct`)
   und konfigurierbarer Timeout-Aktion (ESKALIEREN/ABBRECHEN/BENACHRICHTIGEN/AUTOMATISCH_FORTFAHREN).
   `pruefe_timeout()`: jetzt≥deadline→ABGELAUFEN+regel.aktion, jetzt≥mahnzeitpunkt→MAHNPHASE+BENACHRICHTIGEN,
   sonst→AUSSTEHEND. `verbrauchte_minuten` und `auslastung_pct` werden mitgegeben.
   5 Standardregeln: TR-001 (kontrakt_freigabe 4h/75%/ESKALIEREN), TR-002 (settlement 8h/80%/ESKALIEREN),
   TR-003 (ap_rechnungseingang 2d/90%/BENACHRICHTIGEN), TR-004 (qualitaets_freigabe 1h/AUTOMATISCH_FORTFAHREN),
   TR-005 (* 24h/ABBRECHEN Fallback).

2. **Workflow Batch Processing Contracts**: Batch-Job-Definitionen, Chunk-Erzeugung und
   Fortschrittserfassung für Massenoperationen (IMPORT/EXPORT/VERARBEITUNG/ABRECHNUNG/ARCHIVIERUNG).
   `erstelle_chunks()`: 1-basiert, letzter Chunk ≤ chunk_groesse; leer bei ungültigen Werten.
   `berechne_batch_status()`: LAUFEND gewinnt vor allem; alle abgeschlossen → ABGESCHLOSSEN/TEILWEISE/FEHLGESCHLAGEN.
   `BatchJob.fortschritt_pct`: abgeschlossene_chunks / gesamt_chunks × 100.
   4 Standardjobs: BJ-001 (ABGESCHLOSSEN, 6 Chunks), BJ-002 (TEILWEISE_ERFOLGREICH, gemischte Chunks),
   BJ-003 (LAUFEND, 10 Chunks), BJ-004 (AUSSTEHEND, 0 Chunks).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_timeout_contracts.py` | `TimeoutRegel` (berechne_deadline, berechne_mahnzeitpunkt), `TimeoutPruefung` (ist_abgelaufen, ist_in_mahnphase) | abgeschlossen |
| AP2 | `app/core/process_timeout_contracts.py` | `pruefe_timeout()` (AUSSTEHEND/MAHNPHASE/ABGELAUFEN-Logik), `get_default_timeout_regeln()` (5) | abgeschlossen |
| AP3 | `app/core/workflow_batch_contracts.py` | `BatchChunk` (ist_abgeschlossen, ist_erfolgreich), `BatchJob` (fortschritt_pct, fehlerrate_pct, verarbeitete_datensaetze) | abgeschlossen |
| AP4 | `app/core/workflow_batch_contracts.py` | `berechne_batch_status()`, `erstelle_chunks()`, `get_default_batch_jobs()` (4) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/timeouts/regeln`, `POST /process/timeouts/pruefe` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/batch/jobs`, `POST /process/batch/erstelle-chunks` | abgeschlossen |

## Abnahmekriterien

- `pruefe_timeout()`: ABGELAUFEN übernimmt aktion aus Regel; MAHNPHASE setzt immer BENACHRICHTIGEN
- `pruefe_timeout()`: `verbleibende_minuten` ist negativ wenn Deadline überschritten
- `erstelle_chunks(0, 250)` → leere Liste
- `erstelle_chunks(300, 250)` → 2 Chunks: [250, 50]
- `berechne_batch_status()`: LAUFEND gewinnt auch wenn andere Chunks abgeschlossen sind
- `BatchJob.fortschritt_pct`: 0.0 wenn keine Chunks
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave48_timeout_batch.py` — 147 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave48_timeout_batch.py -q --no-cov
# Ergebnis: 147 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
