# Wave 11 - Command-Catalog, Policy-Entscheidungen und Finance-Folgesichten

**Status:** abgeschlossen
**Datum:** 2026-03-13

## Scope

Wave 11 liefert Command-Catalog, Policy-Override-Resolution, Exception-Katalog, Prozessreferenz-Kontext und Explainability als stabile API-Contracts.

## Zielbild

Commands, Referenzen, Explainability und Policy-Aufloesung sollen ueber gemeinsame Core-Modelle und einen zentralen Process-Kernel-Router verfuegbar sein.

## Lieferumfang

| AP | Inhalt | Endpunkt oder Modul | Status |
|----|--------|---------------------|--------|
| AP1 | Command-Catalog API | `GET /api/v1/process/commands` | abgeschlossen |
| AP2 | Policy-Override-Resolution | `POST /api/v1/process/policy/resolve` | abgeschlossen |
| AP3 | Exception-Katalog | `GET /api/v1/process/exceptions/{process_key}` | abgeschlossen |
| AP4 | Prozessreferenz-Kontext | `POST /api/v1/process/references` | abgeschlossen |
| AP5 | Finance Follow-up Contracts | Core-Contracts | abgeschlossen |
| AP6 | Explainability API und Agrar-Settlement-Referenz | `POST /api/v1/process/explainability` | abgeschlossen |

## Abnahmekriterien

- Command-Catalog ist ueber API lesbar verfuegbar.
- Policy-Overrides koennen deterministisch aufgeloest werden.
- Exception-Catalog und Prozessreferenzen sind als Core-Contracts verfuegbar.
- Explainability-Views sind ueber den Process-Kernel-Router surfacbar.

## Tests

- `pytest tests/test_process_kernel_wave11_commands_policy.py -q --no-cov`
- Ergebnis: 30 passed

## Status

`abgeschlossen`
Stand: 2026-03-13
