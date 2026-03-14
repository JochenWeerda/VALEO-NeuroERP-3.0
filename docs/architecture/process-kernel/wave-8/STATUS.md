# Wave 8 Status

## Wave
- Name: `Tenant Isolation Haertung, Multi-Kontext-Agent und Reporting-Layer`
- Epics: `Epic 3 Tenant, Security and Integration Governance`, `Epic 2 Read, Event and Data Product Platform`
- Status: `gestartet`
- Startbedingung: Wave 7 abgeschlossen

## Ziel

Die in Wave 7 angelegten Read-Model-Snapshots und Event-Consumer-Wirings werden
durch einen formalen Reporting-Layer abfragbar. Tenant-Isolation-Haertung stellt
sicher, dass Cross-Tenant-Datenzugriffe strukturell ausgeschlossen sind.
Ein Multi-Kontext-Agent-Framework erlaubt KI-Agenten tenantbewusste Command-Ausfuehrung.

## Arbeitspakete

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Reporting-Layer: versionierte Datenprodukte aus Read-Model-Snapshots | umgesetzt |
| AP2 | Tenant-Isolation-Haertung: CrossTenantGuard und IsolationAudit | umgesetzt |
| AP3 | Multi-Kontext-Agent: tenantbewusste Command-Delegation | umgesetzt |
| AP4 | Benchmark-Modul: Betriebskennzahlen-Vergleich zwischen Verbundmitgliedern | umgesetzt |
| AP5 | Archiv und Retention: GoBD-konforme Datenaufbewahrungsregeln | umgesetzt |

## Scope

### AP1: Reporting-Layer

Neue Dateien:
- `app/core/reporting_layer.py`
- `app/api/v1/endpoints/reporting_api.py`

Geliefert:
- `DataProduct` mit tenantbezogenen Snapshot-Referenzen
- `DataProductCatalog` fuer defaultisierte Finance-Datenprodukte
- `ReportDefinition` und `ReportResult`
- `build_default_data_products()` fuer AP-Invoice, Payment-Run und Process-Observation
- `run_report()` fuer Filter und einfache Aggregationen auf Snapshot-Payloads

### AP2: Tenant-Isolation-Haertung

Neue Datei: `app/core/tenant_isolation_guard.py`

Geliefert:
- `CrossTenantAccessAttempt`
- `TenantIsolationGuard`
- `IsolationAuditLog`
- `VerbundSharingPolicy`
- produktive Anbindung an die Reporting-API inklusive `GET /reporting/isolation/check`

### AP3: Multi-Kontext-Agent

Neue Datei: `app/core/multi_context_agent.py`

Geliefert:
- `AgentContext`
- `AgentContextStore`
- `MultiContextAgentManifest`
- `tenantbewusst_dispatch()` mit produktiver Guard-Anbindung
- `app/api/v1/endpoints/agent_context_api.py` mit `POST /agent-context`, `DELETE /{id}`, `POST /{id}/dispatch`

### AP4: Betriebskennzahlen-Benchmark

Neue Datei: `app/core/betriebskennzahlen.py`

Geliefert:
- `BetriebsKennzahl`
- `BenchmarkGruppe`
- `BenchmarkReport.build()`
- `app/api/v1/endpoints/benchmark_api.py`

### AP5: GoBD-Retention

Neue Datei: `app/core/gobd_retention.py`

Geliefert:
- `RetentionKlasse`
- `RetentionRegel`
- `RetentionPruefung`
- `build_default_retention_regeln()`

## Pakete

### Paket A: Reporting + Tenant-Isolation + GoBD-Retention
- Enthaelt: AP1, AP2, AP5
- Artefakt: `package-a/STATUS.md`
- Tests: `tests/test_process_kernel_wave8_reporting.py`, `tests/test_process_kernel_wave8_isolation_retention.py`

### Paket B: Multi-Kontext-Agent + Benchmark
- Enthaelt: AP3, AP4
- Artefakt: `package-b/STATUS.md`
- Tests: `tests/test_process_kernel_wave8_agent.py`

## Exit-Kriterien

- [x] `DataProductCatalog.get_by_tenant()` liefert tenant-isolierte Datenprodukte
- [x] Reporting-API kann Datenprodukte listen und Reports gegen Snapshot-Payloads ausfuehren
- [x] `TenantIsolationGuard.check()` blockiert Cross-Tenant-Zugriffe, erlaubt Verbund-Sharing fuer zulaessige Typen
- [x] `AgentContext` laeuft ab und blockiert nach TTL-Ablauf
- [x] `MultiContextAgentManifest` vereint Wave-5-Manifest und Isolation-Guard
- [x] `BenchmarkReport.build()` anonymisiert Tenant-IDs korrekt
- [x] `build_default_retention_regeln()` deckt GoBD-relevante Dokumenttypen ab
- [ ] Alle >= 42 Wave-8-Tests gruen, Gesamtsuite weiterhin gruen

## Verifikation

```bash
pytest tests/test_process_kernel_wave8_reporting.py -q --no-cov
# Ergebnis: 13 passed

pytest tests/test_process_kernel_wave8_isolation_retention.py -q --no-cov
# Ergebnis: 30 passed

pytest tests/test_process_kernel_wave8_agent.py -q --no-cov
# Ergebnis: 26 passed

pytest tests/test_process_kernel_wave7_read_models.py -q --no-cov
# Ergebnis: 28 passed
```

## Startpunkte

- `app/core/read_model_persistence.py` (Wave 7 AP1) - ReadModelSnapshot als Datenprodukt-Basis
- `app/core/tenant_governance.py` (Wave 2 AP3-AP6) - VerbundMember, AgentManifest
- `app/core/agent_command_manifest.py` (Wave 5 AP5) - bestehende Agent-Manifest-Struktur erweitern
- `app/core/command_dispatcher.py` (Wave 5 AP1) - Dispatcher fuer tenantbewusste Delegation
