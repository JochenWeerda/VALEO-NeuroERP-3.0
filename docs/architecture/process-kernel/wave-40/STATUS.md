# Wave-40 Status

## Scope
Workflow-Versionierungs-Contracts (PKP-02) + Canonical Process Audit Trail (PKP-03)

## Zielbild

Wave 40 adressiert zwei zentrale Querschnittsthemen des Process-Kernels:

1. **Workflow-Versionierung**: Versionierte Workflow-Definitionen mit Semver, Migrations-Prüflogik
   (KOMPATIBEL/INKOMPATIBEL/BREAKING/DEPRECATION), Instanz-Versionsbindung und Sandbox-Versionsregeln.
   BREAKING-Migrationen sind architektonisch gesperrt.

2. **Canonical Process Audit Trail**: Unveränderliche, SHA256-hash-verkettete Audit-Einträge mit
   GoBD-Relevanz-Kennzeichnung (PFLICHT/RELEVANT/NICHT_RELEVANT), Kettenintegritätsprüfung und
   10-Jahres-Archivierungsmarkierung für GoBD-Pflichbelege.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/workflow_versioning_contracts.py` | `WorkflowDefinition` (versions_hash SHA256[:16], ist_aktiv), `WorkflowInstanzReferenz` (wurde_migriert), `MigrationsRegel` (ist_zulaessig), `SandboxVersionsRegel` | abgeschlossen |
| AP2 | `app/core/workflow_versioning_contracts.py` | `pruefe_migration()` — BREAKING gesperrt via ist_zulaessig-Filter, INKOMPATIBEL→AUSSTEHEND, KOMPATIBEL/DEPRECATION→ABGESCHLOSSEN; `ermittle_aktive_definition()` mit Tenant-Vorrang | abgeschlossen |
| AP3 | `app/core/workflow_versioning_contracts.py` | `get_default_workflow_definitionen()` (6), `get_default_migrationsregeln()` (5), `get_default_sandbox_regeln()` (4) | abgeschlossen |
| AP4 | `app/core/canonical_process_audit_trail.py` | `AuditEintrag` mit SHA256-Hash-Verkettung, `AuditKette` mit `pruefe_kettenintegritaet()` und `ist_integer`, GoBD-Relevanz-Klassifizierung | abgeschlossen |
| AP5 | `app/core/canonical_process_audit_trail.py` | `erstelle_audit_eintrag()`, `baue_beispiel_audit_kette()` (5 Einträge, 3 GoBD-PFLICHT) | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/workflow-versioning/definitionen`, `POST /process/workflow-versioning/migration-pruefen`, `GET /process/audit-trail/beispiel`, `POST /process/audit-trail/integritaet-pruefen` | abgeschlossen |

## Abnahmekriterien

- `pruefe_migration()` → BREAKING-Regeln via `ist_zulaessig=False` aus passenden Regeln gefiltert → optimistisch KOMPATIBEL
- `pruefe_migration()` → INKOMPATIBEL → AUSSTEHEND, automatisch=False
- `pruefe_migration()` → KOMPATIBEL/DEPRECATION → ABGESCHLOSSEN, automatisch=True
- `ermittle_aktive_definition()` → Tenant-spezifisch vor global, max(version)
- `AuditEintrag.eintrag_hash` via SHA256 über 11 Felder (inkl. vorgaenger_hash) in `__post_init__` gesetzt
- `AuditKette.ist_integer` → True für leere Kette; False nach Tamper
- `baue_beispiel_audit_kette()` → 5 Einträge, ist_integer=True, 3 GoBD-PFLICHT
- Kein Import von `app/api/` in `app/core/`

## Tests

`tests/test_process_kernel_wave40_workflow_versioning_audit.py` — 60 Tests, alle grün

```bash
pytest tests/test_process_kernel_wave40_workflow_versioning_audit.py -q --no-cov
# Ergebnis: 60 passed
```

## Status
`abgeschlossen`
