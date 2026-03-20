# Wave 82 — Controlling 500er eliminieren (Gap 032)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 33 (alle grün)

## Gap

**Gap 032**: Error Rate >1% bei `/controlling/kpis` und `/controlling/timeseries`
**KPI**: Error Rate < 0,5% bei Controlling-Endpoints

## Gelieferte Contracts

### `app/core/controlling_safe_read_contracts.py`

| Klasse / Funktion | Beschreibung |
|---|---|
| `AmpelStatus` | GRUEN / GELB / ROT / UNBEKANNT |
| `KpiVerfuegbarkeit` | VERFUEGBAR / LEER / SCHEMA_FEHLT / PARSE_FEHLER |
| `KpiSafeValue.from_raw()` | Sichere Konvertierung aus DB-Rohdaten ohne Exception-Risiko |
| `TimeseriesSafeEntry` | Einzelner Zeitreihenwert — immer typisiert |
| `TimeseriesSafeResult` | Timeseries-Ergebnis — immer valide, nie 500 |
| `ControllingReadSafetyResult` | Sicherheitsprüfung für Controlling-Datensatz |
| `evaluate_controlling_safety()` | Prüft kritische Fehler (kpi_code fehlt, Wert unparsebar) |
| `safe_kpi_response()` | Wrapper um DB-Abfragen — niemals Exception |
| `safe_timeseries_response()` | Überspringt fehlerhafte Zeilen statt 500 |
| `safe_kpi_list_response()` | Liste sicher konvertieren |

## Kernlogik

- **Ampel-Kalkulation**: `wert/zielwert ≥ 95%` → GRUEN, `≥ 80%` → GELB, sonst ROT
- **Null-Koercion**: Alternative Feldnamen (`current_value` / `wert` / `value`, `target_value` / `zielwert` / `target`)
- **Row-Skip**: Fehlerhafte Timeseries-Zeilen werden übersprungen, kein 500
- **Exception-Wrapper**: `safe_kpi_response()` fängt alle Exceptions, liefert `PARSE_FEHLER`-Objekt

## Tests

```
tests/test_process_kernel_wave82_controlling_safe_reads.py  — 33 Tests
  TestKpiSafeValueFromRaw          (12 Tests)
  TestSafeKpiResponse              (4 Tests)
  TestSafeTimeseriesResponse       (6 Tests)
  TestEvaluateControllingSafety    (5 Tests)
  TestSafeKpiListResponse          (3 Tests)
  TestIntegrationSzenario          (3 Tests)
```
