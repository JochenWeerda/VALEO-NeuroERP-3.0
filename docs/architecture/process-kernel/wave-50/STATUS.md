# Wave-50 Status

## Scope
Process Archive Contracts + Workflow Metrics Contracts

## Zielbild

Wave 50 ergänzt den Process-Kernel um GoBD-konforme Archivierung und KPI-Tracking:

1. **Process Archive Contracts**: GoBD-konforme Archivierung von Workflow-Instanzen mit
   4 Aufbewahrungsklassen (KLASSE_A=10J/KLASSE_B=6J/KLASSE_C=3J/KLASSE_D=1J) und
   4 Archivierungsgründen (ABGESCHLOSSEN/GOBD_PFLICHT/MANUELL/INAKTIVITAET).
   `ArchivEintrag.loeschen_ab`: archiviert_am + N Jahre (Jahres-Arithmetik).
   `ist_loeschbar_am(jetzt)`: False wenn status==GESPERRT, unabhängig vom Datum.
   `ArchivStatistik.archivierungsrate_pct`: (archiviert+gesperrt+geloescht)/gesamt×100.
   5 Standardeinträge: AE-001 (GESPERRT/KLASSE_A 10J), AE-002 (ARCHIVIERT/KLASSE_B 6J),
   AE-003 (ARCHIVIERT/KLASSE_C 3J), AE-004 (GELOESCHT/KLASSE_D 1J), AE-005 (AKTIV/KLASSE_B).

2. **Workflow Metrics Contracts**: KPI-Tracking für Workflow-Performance mit 5 Metriktypen
   (DURCHLAUFZEIT/SLA_EINHALTUNG/FEHLERRATE/DURCHSATZ/WARTEZEIT) und 5 Aggregationsmodi
   (MINIMUM/MAXIMUM/DURCHSCHNITT/MEDIAN/SUMME).
   `WorkflowKpiSummary.performanz_bewertung`: AUSGEZEICHNET≥95%/GUT≥80%/AKZEPTABEL≥60%/KRITISCH<60%.
   `aggregiere_messpunkte()`: 0.0 für leere/keine-passenden Messpunkte; MEDIAN korrekt für
   gerade und ungerade Anzahl.
   4 Standard-KPIs: kontrakt_freigabe (95%/AUSGEZEICHNET), settlement (82%/GUT),
   ap_rechnungseingang (58%/KRITISCH), qualitaets_freigabe (88%/GUT).

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/process_archive_contracts.py` | `ArchivEintrag` (loeschen_ab, ist_loeschbar_am), `ArchivStatistik` (archivierungsrate_pct), AUFBEWAHRUNGSFRISTEN | abgeschlossen |
| AP2 | `app/core/process_archive_contracts.py` | `berechne_archiv_statistik()`, `get_default_archiv_eintraege()` (5) | abgeschlossen |
| AP3 | `app/core/workflow_metrics_contracts.py` | `MetrikMesspunkt`, `WorkflowKpiSummary` (fehlerrate_pct, erfolgsrate_pct, performanz_bewertung) | abgeschlossen |
| AP4 | `app/core/workflow_metrics_contracts.py` | `aggregiere_messpunkte()` (5 Modi inkl. Median), `get_default_kpi_summaries()` (4) | abgeschlossen |
| AP5 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/archiv/eintraege`, `POST /process/archiv/statistik` | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/metrics/kpi-summaries`, `POST /process/metrics/aggregiere` | abgeschlossen |

## Abnahmekriterien

- `ist_loeschbar_am()`: GESPERRT → immer False, unabhängig vom Datum
- `AUFBEWAHRUNGSFRISTEN[KLASSE_A]` == 10, KLASSE_B == 6, KLASSE_C == 3, KLASSE_D == 1
- `performanz_bewertung`: Grenzwert 95% → AUSGEZEICHNET; 94.9% → GUT; 60% → AKZEPTABEL; 59.9% → KRITISCH
- `aggregiere_messpunkte()`: leere Liste → 0.0; falscher workflow_typ → 0.0
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave50_archive_metrics.py` — 129 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave50_archive_metrics.py -q --no-cov
# Ergebnis: 129 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
