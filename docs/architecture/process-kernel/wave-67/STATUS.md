# Wave 67 - Process Cache Contracts + Workflow Schema Migration Contracts

**Status:** abgeschlossen
**Datum:** 2026-03-18
**Tests:** 192 passed, 0 failed

## Scope

Wave 67 implementiert zwei reine Domain-Contracts ohne App- oder API-Abhaengigkeiten: Process Cache Contracts und Workflow Schema Migration Contracts.

## Zielbild

Caching und Schema-Migrationen sollen als reine Domain-Contracts ohne App-Abhaengigkeiten im Kernel verfuegbar sein.

## Lieferumfang

| AP | Inhalt | Status |
|----|--------|--------|
| AP1 | `process_cache_contracts.py` mit Cache-Typen, TTL-Status, Invalidierung und Statistik | abgeschlossen |
| AP2 | `workflow_schema_migration_contracts.py` mit Versions-, Kompatibilitaets- und Registry-Logik | abgeschlossen |
| AP3 | Vier Endpunkte in `process_kernel_api.py` | abgeschlossen |
| AP4 | 192 Pytest-Tests | abgeschlossen |

## Abnahmekriterien

- `CacheEintrag.status()` liefert `VERALTET`, wenn die TTL ueberschritten ist.
- `CacheInvalidierungsRegel.trifft_zu()` prueft Tag-Ueberschneidung und Schluessel-Prefix.
- `CacheStatistik.trefferquote_pct()` gibt `0.0` bei leerer Statistik zurueck.
- `FeldAenderung.ist_brechend()` ist fuer Entfernen, Typaenderung und Pflichtsetzung wahr.
- `SchemaVersion.berechne_kompatibilitaet()` liefert `KEINE` bei jeder brechenden Aenderung.
- `SchemaMigration.hat_rueckgaengig_pfad()` prueft nur Pflicht-Schritte.
- `SchemaRegistry.aktuellste_version()` bestimmt korrekt die neueste Semver-Version.
- Keine `app.api`-Imports in den Core-Modulen.

## Tests

**Datei:** `tests/test_process_kernel_wave67_cache_schema_migration.py`
**Anzahl:** 192

## Status

`abgeschlossen`
Stand: 2026-03-18
