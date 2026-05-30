# Wave-70 Status

## Scope

Knowledge Context Injection — kontextuelle Wissenspakete fuer Mensch und Agent auf Basis des Knowledge Core (Wave 69).

## Zielbild

Wave 70 uebersetzt abrufbares Wissen in kanalspezifische Context Packs. Agenten- und Prozesspfade koennen damit rollen-, domain- und query-basiert angereichert werden, ohne Wissensobjekte erneut zu duplizieren.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/knowledge_core_contracts.py` | `build_context_pack`, `KnowledgeChannel` | abgeschlossen |
| AP2 | `app/api/v1/endpoints/agent_context_api.py` | Agent-Context-HTTP-Endpunkte | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | Context-Pack-Surfacing im Process Kernel | abgeschlossen |

## Abnahmekriterien

- Context Packs enthalten Quellen, Zusammenfassung und kanalspezifische Metadaten.
- Rollen- und Domain-Filter schraenken den Wissensumfang nachvollziehbar ein.
- Agent-Context-API und Process-Kernel-Endpunkte liefern konsistente Pack-Struktur.
- Kein Import von `app/api/` in `app/core/`.

## Tests

`tests/test_process_kernel_wave70_context_injection.py` — 8 Tests

- Contract-Tests fuer Context Packs und API-Surfacing
- `python -m pytest tests/test_process_kernel_wave70_context_injection.py -q --no-cov`

## Status

`abgeschlossen` - 2026-03-18 - Knowledge Context Injection fuer Agenten und Prozesspfade verfuegbar.
