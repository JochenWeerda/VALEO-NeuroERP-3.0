# Wave 8 Paket A Status

## Paket
- Name: `Reporting-Layer, Tenant-Isolation-Haertung und GoBD-Retention`
- Zugeordnete Aufgaben: `AP1`, `AP2`, `AP5`
- Status: `gestartet`

## Ziel
Datenprodukte aus Read-Model-Snapshots werden abfragbar. Tenant-Isolation
wird formal geprueft und protokolliert. GoBD-Aufbewahrungsregeln sind
maschinell auswertbar.

## Gelieferte Artefakte

| Datei | Inhalt | Status |
|-------|--------|--------|
| `app/core/read_model_persistence.py` | `ReadModelSnapshotStore` mit DB-gestuetzter Persistenz und In-Memory-Fallback | umgesetzt |
| `app/infrastructure/models/read_model_snapshots.py` | persistentes Snapshot-ORM-Modell | umgesetzt |
| `app/api/v1/endpoints/read_model_snapshots.py` | Snapshot-API arbeitet ueber DB-Store statt nur In-Memory | umgesetzt |
| `app/core/reporting_layer.py` | `DataProduct`, `DataProductCatalog`, `ReportDefinition`, `ReportResult`, `run_report()` | umgesetzt |
| `app/api/v1/endpoints/reporting_api.py` | `GET /reporting/data-products`, `POST /reporting/run`, `GET /reporting/isolation/check` | umgesetzt |
| `tests/test_process_kernel_wave8_reporting.py` | 13 Tests | umgesetzt |
| `app/core/tenant_isolation_guard.py` | `TenantIsolationGuard`, `CrossTenantAccessAttempt`, `IsolationAuditLog`, `VerbundSharingPolicy` | umgesetzt |
| `tests/test_process_kernel_wave8_isolation_retention.py` | 30 Tests (AP2/AP5) | umgesetzt |
| `app/core/gobd_retention.py` | `RetentionRegel`, `RetentionPruefung`, `build_default_retention_regeln()` | umgesetzt |

## Abnahmekriterien

- [x] Read-Model-Snapshots lassen sich DB-persistiert speichern und wieder abfragen
- [x] Snapshot-API ist nicht mehr auf einen Prozess-lokalen In-Memory-Store beschraenkt
- [x] `DataProductCatalog.get_by_tenant()` liefert nur Produkte des eigenen Tenants
- [x] Reporting-API listet Datenprodukte tenantbezogen und fuehrt einfache Reports ueber Snapshot-Payloads aus
- [x] `TenantIsolationGuard.check()` gibt DENIED fuer fremde Tenants ohne Verbund-Berechtigung
- [x] `IsolationAuditLog` loggt alle DENIED-Zugriffe append-only
- [x] `RetentionPruefung.darf_geloescht_werden()` prueft Aufbewahrungsfrist korrekt
- [x] `build_default_retention_regeln()` enthaelt mindestens 8 Dokumenttypen

## Verifikation

```bash
pytest tests/test_process_kernel_wave8_reporting.py -q --no-cov
# Ergebnis: 13 passed

pytest tests/test_process_kernel_wave8_isolation_retention.py -q --no-cov
# Ergebnis: 30 passed

pytest tests/test_process_kernel_wave7_read_models.py -q --no-cov
# Ergebnis: 28 passed
```

## Abhaengigkeiten
- `app/core/read_model_persistence.py` (Wave 7 AP1)
- `app/core/tenant_governance.py` (Wave 2)
- `app/core/audit_evidence.py` (Wave 3 AP2)
