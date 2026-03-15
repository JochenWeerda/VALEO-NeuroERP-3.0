# Wave-26 Status

## Scope
Trocknungsabrechnung Audit-Contract (Gap 003) + Workflow-Migrations-Guard (Gap 011)

## Zielbild

Wave 26 schliesst zwei verbliebene P0-Luecken:
Gap 003 (Trocknungs- und Abzugsregeln 100% reproduzierbar, GoBD-konform)
und Gap 011 (Versionierte Workflow Engine, 0 ungeplante Workflow-Brueche bei Releases).

Der Trocknungsabrechnung-Audit-Contract macht jede Berechnung deterministisch
nachvollziehbar (SHA-256, schema_version=1) und ergaenzt die bestehende
drying_rule_engine aus modules/agrar/services/ um einen reinen Core-Layer.
Der Workflow-Migrations-Guard prueft Breaking Changes in Workflow-Definitionen
vor jedem Release-Uebergang.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/trocknungs_abrechnung.py` | `TrocknungsInput`, `TrocknungsPosition`, `TrocknungsErgebnis`; `compute_trocknungs_abrechnung()` deterministisch; SHA-256 Audit-Hash; `schema_version=1` | abgeschlossen |
| AP2 | `app/core/workflow_migrations_guard.py` | `WorkflowDefinitionSnapshot`, `MigrationRisikoKlasse`, `validate_workflow_migration()` → `MigrationCompatibilityResult`; SAFE/WARNUNG/BREAKING | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/trocknungs-abrechnung/preview/{id}` + `GET /regelsets` | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | `POST /process/workflow-migration/check` — Migrations-Kompatibilitaetspruefung | abgeschlossen |
| AP5 | `app/core/trocknungs_abrechnung.py` | `validate_trocknungs_ergebnis()` — 5 Plausibilitaetscodes (Feuchte, Abzug, Netto, Extremwert) | abgeschlossen |
| AP6 | `app/core/trocknungs_abrechnung.py` | `get_default_trocknungsregeln()` — 5 Branchenrichtwerte (WW/SG/RA/KM/ZR) nach DLG/UFOP | abgeschlossen |

## Abnahmekriterien

- `compute_trocknungs_abrechnung()` ist deterministisch: gleicher Input → gleicher SHA-256
- `TrocknungsErgebnis` traegt `schema_version=1` und `audit_hash`
- `validate_workflow_migration()` erkennt: entfernte Pflichtschritte, veraenderte Terminalzustaende, fehlende Rollenzuweisung
- Migrations-Guard klassifiziert in SAFE / WARNUNG / BREAKING
- Alle 5 Default-Trocknungsregeln (WW/SG/RA/KM/ZR) sind serialisierbar
- Keine Schichtverletzungen: `app/core/` importiert kein `modules/agrar/`

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave26_trocknungs_migration.py` | 37 | AP1/AP5/AP6: compute_trocknungs_abrechnung() (11 Tests, inkl. Determinismus + Max-Clamp); validate_trocknungs_ergebnis() (5 Tests); Default-Regelsets (5 Tests); AP2: validate_workflow_migration() (10 Tests, SAFE/WARNUNG/BREAKING); AP3/AP4: API-Endpoints (6 Tests) |

**Gesamt Wave 26: 37 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 003 | Trocknungs-/Abzugsregeln 100% reproduzierbar | `trocknungs_abrechnung.py`: `compute_trocknungs_abrechnung()` mit SHA-256 Audit-Hash, deterministisch; `validate_trocknungs_ergebnis()`; 5 DLG/UFOP-Richtwert-Regelsets (WW/SG/RA/KM/ZR) |
| Gap 011 | Versionierte Workflow Engine, 0 ungeplante Brueche | `workflow_migrations_guard.py`: `validate_workflow_migration()` klassifiziert SAFE/WARNUNG/BREAKING; erkennt entfernte Pflichtschritte, Terminalzustand-Aenderungen, Schema-Downgrade, Reihenfolge-Umkehr |

## Status
`abgeschlossen` — 2026-03-15
