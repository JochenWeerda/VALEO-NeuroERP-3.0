# Wave 86 — Versionierte Workflow Engine mit Migrationen (Gap 011)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 40 (alle grün)

## Gap

**Gap 011**: Versionierte Workflow Engine mit Migrationen
**KPI**: 0 ungeplante Workflow-Brueche bei Releases

## Gelieferte Contracts

### `app/core/workflow_version_engine_contracts.py`

| Klasse / Funktion | Beschreibung |
|---|---|
| `WorkflowVersion` | Semantic Version (major.minor.patch) mit Vergleichsoperatoren |
| `AenderungsTyp` | PATCH / MINOR / MAJOR |
| `MigrationStrategie` | IN_PLACE / DUAL_RUN / HARD_CUTOVER / ROLLBACK |
| `WorkflowDefinition` | Versionierte Definition mit schema_hash |
| `MigrationsSchritt` | Einzelner Migrationsschritt mit Strategie + Risiko |
| `MigrationsPlan` | Geordneter Plan mit ist_breaking, hoechstes_risiko |
| `WorkflowVersionRegistry` | Zentrales Versions-Register |
| `validate_migrations_sicherheit()` | Blockiert ungeplante Brueche |

## Tests

```
tests/test_process_kernel_wave86_workflow_version_engine.py  -- 40 Tests
```
