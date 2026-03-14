# Wave 11 — Command-Catalog, Policy-Entscheidungen und Finance-Folgesichten

## Status
- Stand: `2026-03-13`
- Status: `abgeschlossen`
- Tests: `30 gruen` (`tests/test_process_kernel_wave11_commands_policy.py`)

## Ziel
Command-Catalog, Policy-Override-Resolution, Exception-Katalog, Prozessreferenz-Kontext
und Explainability als stabile API-Contracts bereitstellen.

## Arbeitspakete

| AP | Inhalt | Endpunkt | Status |
|----|--------|----------|--------|
| AP1 | Command-Catalog API | `GET /api/v1/process/commands` | abgeschlossen |
| AP2 | Policy-Override-Resolution | `POST /api/v1/process/policy/resolve` | abgeschlossen |
| AP3 | Exception-Katalog | `GET /api/v1/process/exceptions/{process_key}` | abgeschlossen |
| AP4 | Prozessreferenz-Kontext | `POST /api/v1/process/references` | abgeschlossen |
| AP5 | Finance Follow-up Contracts | reine Contract-Tests | abgeschlossen |
| AP6 | Explainability API + Agrar Settlement Ref | `POST /api/v1/process/explainability`, `POST /api/v1/process/references/agrar/settlement` | abgeschlossen |

## Neue Core-Module (untracked → jetzt aktiv genutzt)

- `app/core/process_commands.py` — Command-Katalog (13 Commands)
- `app/core/process_references.py` — ProcessReferenceChain/Context
- `app/core/agrar_process_references.py` — agrar-spezifische Reference Builder
- `app/core/exception_rules.py` — ProcessExceptionCatalog + 3 Settlement-Default-Rules
- `app/core/explainability.py` — ExplainabilityView + build_policy_explainability_view()
- `app/core/policy_decisions.py` — PolicyOverrideLayer, PolicyOverrideResolution, resolve_policy_override_layers()

## Neuer Endpunkt-Router

- `app/api/v1/endpoints/process_kernel_api.py` — Wave-11-Router (prefix `/process`)

## Abnahme-Verifikation

```bash
pytest tests/test_process_kernel_wave11_commands_policy.py -q --no-cov
# Ergebnis: 30 passed
```

## Konfliktregeln (Wave 11)

- `app/core/process_commands.py` und alle anderen neuen Core-Module sind stabil; nur erweitern
- Command-Catalog via `get_process_command_catalog()` exportieren; keine Duplikation in Endpunkten
- Exception-Catalogs in `_EXCEPTION_CATALOGS`-Dict in `process_kernel_api.py` eintragen; neuen Prozess als eigenes `ProcessExceptionCatalog`-Objekt in `exception_rules.py` anlegen
- Agrar-spezifische Reference Builder gehören in `agrar_process_references.py`, nicht in Endpoints
