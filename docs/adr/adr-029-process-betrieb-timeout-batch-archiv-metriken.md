# ADR-029: Process-Betrieb — Timeout, Batch, Archiv und Metriken

**Status:** Accepted
**Datum:** 2026-03-16
**Cluster:** Process Reliability / Operations & Telemetry

---

## Kontext

Der Process-Kernel benötigte in den Waves 48–50 Querschnittskonzepte für den zuverlässigen
Betrieb von Workflow-Instanzen:

- Fristenüberwachung mit konfigurierbarer Eskalation (SLA-Timeout).
- Massendatenverarbeitung als steuerbarer Batch-Job mit Chunk-Fortschritt.
- GoBD-konforme Archivierung abgeschlossener Workflow-Instanzen.
- Nachvollziehbares KPI-Tracking für Prozessperformanz.

## Entscheidung

1. **Process Timeout Contracts** (`app/core/process_timeout_contracts.py`): Fristenüberwachung
   mit vier Timeout-Typen (RELATIV/ABSOLUT/GESCHAEFTSZEIT/SLA_GEBUNDEN) und konfigurierbarem
   `mahngrenze_pct`. `pruefe_timeout()` liefert AUSSTEHEND/MAHNPHASE/ABGELAUFEN ohne Seiteneffekt.
   MAHNPHASE setzt immer BENACHRICHTIGEN; ABGELAUFEN übernimmt die konfigurierte Aktion der Regel.

2. **Workflow Batch Processing Contracts** (`app/core/workflow_batch_contracts.py`): Batch-Jobs
   mit chunk-basiertem Fortschritt. `erstelle_chunks()` ist deterministisch (1-basiert, letzter
   Chunk ≤ chunk_groesse). `berechne_batch_status()` leitet Status aus Chunk-Zustand ab:
   LAUFEND gewinnt vor allem, danach ABGESCHLOSSEN/TEILWEISE_ERFOLGREICH/FEHLGESCHLAGEN.

3. **Process Archive Contracts** (`app/core/process_archive_contracts.py`): GoBD-konforme
   Archivierung mit vier Aufbewahrungsklassen (A=10J/B=6J/C=3J/D=1J).
   `ist_loeschbar_am(jetzt)`: GESPERRT blockiert Löschung unabhängig vom Datum.
   `archivierungsrate_pct` aggregiert archivierte + gesperrte + gelöschte Einträge.

4. **Workflow Metrics Contracts** (`app/core/workflow_metrics_contracts.py`): KPI-Tracking mit
   `PerformanzBewertung` (AUSGEZEICHNET≥95%/GUT≥80%/AKZEPTABEL≥60%/KRITISCH<60%) und
   `aggregiere_messpunkte()` (MINIMUM/MAXIMUM/DURCHSCHNITT/MEDIAN/SUMME; 0.0 für leer/kein Match).

## Konsequenzen

- Positiv: Betriebskonzepte (Timeout, Batch, Archiv, Metriken) sind als testbare Pure-Python-
  Contracts im `app/core/`-Layer verankert — kein DB-Zugriff in der Kernlogik.
- Positiv: GoBD-Aufbewahrung und GESPERRT-Schutz sind explizit modelliert (nicht nur Kommentar).
- Negativ: Batch-Fortschritt ist derzeit in-memory; für persistente Batch-Jobs braucht es ein
  eigenes Read-Model (→ Folge-Wave).
- Constraint: `app/core/`-Module dürfen weiterhin keine `app/api/`-Importe enthalten.

## Bezug zu anderen ADRs

- ADR-008 (Eventing/Outbox): Timeout-Events können über den Outbox-Pfad ausgelöst werden.
- ADR-012 (Dokument-/Audit-Evidence-Modell): Archivierungsklassen greifen das GoBD-Modell aus ADR-012 auf.
- ADR-015 (Analytics-/Benchmark-Datenproduktmodell): Workflow-Metriken liefern den Input für Benchmarks.
- ADR-016 (IoT-/Telemetrie-Modell): Messpunkte (`MetrikMesspunkt`) folgen dem Telemetrie-Datenmuster.

## Implementierung

- Wave 48: `process_timeout_contracts.py` + `workflow_batch_contracts.py` (147 Tests)
- Wave 49: `workflow_lock_contracts.py` (115 Tests, Lock-Konkurrenzkontrolle)
- Wave 50: `process_archive_contracts.py` + `workflow_metrics_contracts.py` (129 Tests)
