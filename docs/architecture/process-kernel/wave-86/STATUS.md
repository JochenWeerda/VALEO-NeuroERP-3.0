# Wave 86 — Versionierte Workflow Engine (Gap 011)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**Tests:** 36 grün, 0 Fehler

## Gap

**Gap 011:** Semantic Versioning für Workflow-Definitionen
**KPI:** Alle MAJOR-Breaking-Changes durch genehmigte Versionen abgesichert; HARD_CUTOVER niemals mit aktiven Instanzen

## Implementierung

### Contracts (`app/core/workflow_version_engine_contracts.py`)

| Klasse / Funktion | Beschreibung |
|---|---|
| `AenderungsTyp` | Enum: PATCH, MINOR, MAJOR (SemVer-Analogie) |
| `MigrationsStrategie` | Enum: SOFT_UPGRADE, HARD_CUTOVER, PARALLEL_RUN, DRAIN |
| `WorkflowStatus` | Enum: ENTWURF, REVIEW, FREIGEGEBEN, VERALTET, ARCHIVIERT |
| `RisikoStufe` | Enum: NIEDRIG, MITTEL, HOCH, KRITISCH |
| `WorkflowVersion` | Semantische Versionsnummer mit `aenderungs_typ()` |
| `WorkflowVersionDefinition` | Vollständige Versionsdefinition inkl. Status + Genehmigung |
| `WorkflowMigrationsplan` | Migrationsplan von Version A nach Version B |
| `validate_migrations_sicherheit()` | Blockiert: MAJOR ohne Genehmigung, HARD_CUTOVER mit Instanzen |
| `WorkflowVersionsHistorie` | Historieliste mit aktuelle_version, anzahl_major_releases |

### Sicherheitsregeln (Gap 011)

**Blockierend (erlaubt=False):**
1. `MAJOR`-Änderung ohne `genehmigungs_pflicht=True`
2. `HARD_CUTOVER` mit `aktive_instanzen > 0`

**Warnend (nicht blockierend):**
- `PARALLEL_RUN` mit `KRITISCHEM` Risiko

**Hinweise:**
- Irreversible Migration mit Risiko HOCH oder KRITISCH → Backup empfohlen

## Tests (`tests/test_process_kernel_wave86_workflow_version_engine.py`)

| Testklasse | Tests | Inhalt |
|---|---|---|
| `TestWorkflowVersion` | 9 | SemVer, Negativprüfung, aenderungs_typ, ist_neuer_als |
| `TestValidateMigrationsSicherheitErlaubt` | 5 | PATCH/MINOR ok, MAJOR mit Genehmigung, HARD_CUTOVER ohne Instanzen |
| `TestValidateMigrationsSicherheitBlockiert` | 3 | MAJOR ohne Genehmigung, HARD_CUTOVER mit Instanzen, beide |
| `TestValidateMigrationsSicherheitHinweise` | 5 | Irreversibel-HOCH, PARALLEL_RUN-KRITISCH, Warnungen |
| `TestWorkflowVersionsHistorie` | 6 | aktuelle_version, anzahl_major_releases, get_version |
| `TestWorkflowMigrationsplan` | 2 | aenderungstyp, as_dict |

**Gesamt: 36 Tests**
