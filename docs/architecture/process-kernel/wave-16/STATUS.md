# Wave-16 Status

## Scope
Aggregate Ownership Register — maschinenlesbarer Vertrag für alle Aggregate

## Lieferumfang

| AP | Modul | Beschreibung |
|----|-------|--------------|
| AP1 | `app/core/aggregate_registry.py` | `AggregateDefinition` — Pflichtfelder, schema_version=1 |
| AP2 | `app/core/aggregate_registry.py` | 8 Aggregate-Typen mit korrekten Besitzern (finance/agrar) |
| AP3 | `app/core/aggregate_registry.py` | Command-Katalog-Konsistenz: alle 9 Commands zeigen auf registrierte Aggregate |
| AP4 | `app/core/aggregate_registry.py` | `get_read_model_owner()` — Read-Model → Aggregat-Ownership |
| AP5 | `app/core/aggregate_registry.py` | `get_aggregates_by_domain()` — finance (4) / agrar (4) |
| AP6 | `app/core/aggregate_registry.py` | `validate_command_aggregate_consistency()` + KeyError bei unbekanntem Aggregat |

## Modellierungsregeln — Systemverankerung

Das Register setzt die vier Modellierungsregeln als maschinenlesbare Contracts durch:

1. **Kein Schattenmodell** — `get_aggregate_definition()` wirft `KeyError` für nicht registrierte Typen → erzwingt explizite Eintragung
2. **Klarer fachlicher Besitzer** — `business_domain` pro Aggregat ist stabiler Contract; `get_aggregates_by_domain()` liefert die Ownership-Sicht
3. **Read Models vom Canonical Model** — `read_model_keys` im Register = verbindliche Liste; `get_read_model_owner()` prüft Ownership
4. **Commands an Aggregat anschliessen** — `validate_command_aggregate_consistency()` prüft Command→Aggregat-Passung zur Laufzeit

## Tests
- Datei: `tests/test_process_kernel_wave16_aggregate_registry.py`
- Ergebnis: **31 Tests gruen**
- Gesamtsuite: **886 passed, 5 skipped, 1 xfailed**

## Status
`abgeschlossen`
