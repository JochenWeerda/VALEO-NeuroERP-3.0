# Wave-32 Status

## Scope
Dashboard Read-Model Snapshots (Gap 033) + Query-Fallback-Contracts (Gap 032)

## Zielbild

Wave 32 schliesst zwei P0-Luecken:
Gap 033 (Read-Models fuer Dashboards statt teurer Live-Joins — p95 Dashboard API <250ms)
und Gap 032 (500er bei controlling/kpis/timeseries eliminieren — Error Rate <0.5%).

Die Dashboard-Snapshot-Registry definiert typisierte Snapshots fuer alle
Kern-Cockpits (Finance-KPIs, Settlement-Cockpit, Wareneingang, AP-Invoice-Cockpit)
mit Staleness-Erkennung und Rebuild-Trigger.
Die Query-Fallback-Contracts legen fest, wie das System bei Query-Fehlern
reagiert (Cache / Safe-Default / Error-Response) — ohne 500er zu propagieren.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/dashboard_snapshots.py` | `SnapshotTyp`, `DashboardSnapshot`, `SnapshotRegistry`; Staleness-Erkennung; `get_default_dashboard_snapshots()` — 6 Cockpit-Snapshots | abgeschlossen |
| AP2 | `app/core/dashboard_snapshots.py` | `validate_snapshot()`, `build_snapshot_from_fields()`, `SnapshotRebuildRequest` | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/dashboards/snapshots[?typ=]` + `POST /process/dashboards/rebuild` | abgeschlossen |
| AP4 | `app/core/query_fallback_contracts.py` | `QueryFallbackTyp`, `QueryFallbackRegel`, `QueryFallbackResult`; `evaluate_fallback(fehler, kontext)` | abgeschlossen |
| AP5 | `app/core/query_fallback_contracts.py` | `get_default_fallback_rules()` — Default-Regeln fuer Finance, Agrar, Compliance, Workflow | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/query-fallbacks[?domain=]` + `POST /process/query-fallbacks/evaluate` | abgeschlossen |

## Abnahmekriterien

- `DashboardSnapshot` traegt Typ, Zeitstempel, Staleness-Flag und typisierte Felder
- Staleness: konfigurierbare `max_alter_sekunden`, Vergleich gegen `letzte_aktualisierung`
- `validate_snapshot()` prueft Pflichtfelder und Staleness
- `evaluate_fallback()` liefert CACHE / SAFE_DEFAULT / ERROR_RESPONSE deterministisch
- Default-Fallback-Regeln decken Finance/Agrar/Compliance/Workflow ab
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave32_snapshots_fallback.py` — 47 Tests, alle gruen

```bash
pytest tests/test_process_kernel_wave32_snapshots_fallback.py -q --no-cov
# Ergebnis: 47 passed
```

## Status
`abgeschlossen`
Stand: 2026-03-19
