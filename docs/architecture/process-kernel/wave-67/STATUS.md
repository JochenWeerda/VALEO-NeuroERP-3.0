# Wave 67 — Process Cache Contracts + Workflow Schema Migration Contracts

## Scope

Wave 67 implementiert zwei reine Domain-Contracts ohne App/API-Abhängigkeiten:

1. **Process Cache Contracts** (`app/core/process_cache_contracts.py`): Typen und Regeln für Prozess-Caching (LRU, TTL, Write-Through, Write-Back), inkl. Cache-Einträge mit TTL-Statusprüfung, tag-basierter Invalidierung und Trefferquoten-Statistik.

2. **Workflow Schema Migration Contracts** (`app/core/workflow_schema_migration_contracts.py`): Typen für Schema-Versionierung, Kompatibilitätsprüfung (VOLLSTAENDIG, RUECKWAERTS, KEINE), Migrations-Schritte mit Rollback-Pfad und Schema-Registry.

## Arbeitspakete

| AP  | Inhalt                                      | Status        |
|-----|---------------------------------------------|---------------|
| AP1 | `process_cache_contracts.py` — Cache-Typen  | abgeschlossen |
| AP2 | `workflow_schema_migration_contracts.py` — Schema-Migrations-Typen | abgeschlossen |
| AP3 | 4 Endpoints in `process_kernel_api.py`      | abgeschlossen |
| AP4 | 192 pytest-Tests                            | abgeschlossen |

## Abnahmekriterien

- `CacheEintrag.status()` liefert VERALTET wenn `(jetzt - erstellt_am).total_seconds() > ttl_sekunden`
- `CacheInvalidierungsRegel.trifft_zu()` prüft Tag-Überschneidung und Schlüssel-Prefix
- `CacheStatistik.trefferquote_pct()` gibt 0.0 bei leerer Statistik zurück
- `FeldAenderung.ist_brechend()` True für ENTFERNT, TYP_GEAENDERT, PFLICHT_GEMACHT
- `SchemaVersion.berechne_kompatibilitaet()` liefert KEINE bei jeder brechenden Änderung
- `SchemaMigration.hat_rueckgaengig_pfad()` prüft nur Pflicht-Schritte
- `SchemaRegistry.aktuellste_version()` bestimmt via semver-Tupel-Vergleich
- Keine `app.api`-Imports in den Core-Modulen

## Tests

```bash
pytest tests/test_process_kernel_wave67_cache_schema_migration.py -q --no-cov
```

**Ergebnis: 192 passed, 0 failed**

## Status: abgeschlossen

Datum: 2026-03-18
