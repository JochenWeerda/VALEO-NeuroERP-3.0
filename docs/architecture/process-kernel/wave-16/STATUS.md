# Wave 16 - Aggregate Ownership Register

**Status:** abgeschlossen
**Datum:** 2026-03-19

## Scope

Wave 16 fuehrt ein maschinenlesbares Ownership-Register fuer Aggregate, Read-Models und Commands ein.

## Zielbild

Ownership und Zuordnung von Aggregaten, Read-Models und Commands sollen ueber ein explizites Register pruefbar werden und Schattenmodelle verhindern.

## Lieferumfang

| AP | Modul | Beschreibung |
|----|-------|--------------|
| AP1 | `app/core/aggregate_registry.py` | `AggregateDefinition` mit Pflichtfeldern und `schema_version=1` |
| AP2 | `app/core/aggregate_registry.py` | Acht Aggregate-Typen mit fachlicher Ownership |
| AP3 | `app/core/aggregate_registry.py` | Konsistenzpruefung fuer Command-Katalog |
| AP4 | `app/core/aggregate_registry.py` | `get_read_model_owner()` |
| AP5 | `app/core/aggregate_registry.py` | `get_aggregates_by_domain()` |
| AP6 | `app/core/aggregate_registry.py` | `validate_command_aggregate_consistency()` |

## Abnahmekriterien

- Aggregate sind mit Pflichtfeldern und Domain-Ownership registriert.
- Alle relevanten Commands verweisen auf registrierte Aggregate.
- Read-Model-Ownership ist ueber das Register ableitbar.
- Inkonsistenzen fuehren zu expliziten Fehlern statt stiller Schattenmodelle.

## Tests

- Datei: `tests/test_process_kernel_wave16_aggregate_registry.py`
- Ergebnis: 31 Tests gruen
- Gesamtsuite: 886 passed, 5 skipped, 1 xfailed

## Status

`abgeschlossen`
Stand: 2026-03-19
