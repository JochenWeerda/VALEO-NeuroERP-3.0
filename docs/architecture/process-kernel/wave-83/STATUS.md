# Wave 83 — Read-Models für Dashboards (Gap 033)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 30 (alle grün)

## Gap

**Gap 033**: Dashboard-API zu langsam durch Live-Joins auf jede Anfrage
**KPI**: p95 Dashboard-API < 250ms durch vorberechnete Read-Models

## Gelieferte Contracts

### `app/core/dashboard_read_model_contracts.py`

| Klasse / Funktion | Beschreibung |
|---|---|
| `ReadModelFreshness` | FRISCH / VERALTET / LEER / WIRD_GEBAUT |
| `DashboardTyp` | CONTROLLING / AGRAR / FINANCE / LOGISTIK / COMPLIANCE / OPERATIONS |
| `DashboardKpiTile` | Einzelne KPI-Kachel mit Wert, Ampel, Trend |
| `DashboardSnapshot` | Vollständiger vorberechneter Dashboard-Zustand |
| `DashboardReadModelStore` | In-Memory Store — in Produktion Redis-backed |
| `ReadModelBuildJob` | Auftrag zum (Neu-)Aufbau eines Read-Models |
| `DashboardPerformanceContract` | Misst ob p95 < 250ms KPI eingehalten wird |

## Kernlogik

- **Cache-Key**: `"{tenant_id}::{dashboard_typ}"` — Tenant-Isolation garantiert
- **Freshness-Check**: `freshness(max_alter_sekunden=300)` → FRISCH / VERALTET
- **Stale-while-revalidate**: `get_or_stale()` liefert veralteten Snapshot + Freshness-Status
- **Invalidierung**: einzeln per `(tenant_id, typ)` oder alle eines Tenants via `invalidate_tenant()`
- **Performance-KPI**: `kpi_erfuellt = gemessene_p95_ms <= p95_ziel_ms AND stichproben > 0`
- **Produktion**: Store-API ist identisch zu Redis-Backend → kein App-Code-Umbau nötig

## Tests

```
tests/test_process_kernel_wave83_dashboard_read_models.py  — 30 Tests
  TestDashboardKpiTile          (1 Test)
  TestDashboardSnapshot         (7 Tests)
  TestDashboardReadModelStore   (9 Tests)
  TestReadModelBuildJob         (3 Tests)
  TestDashboardPerformanceContract (5 Tests)
  TestIntegrationSzenario       (5 Tests)
```
