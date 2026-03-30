# NC-A10 - Dynamic Plan Generation

## Ziel

Templatefreie Intents sollen nicht mehr auf einen einzelnen `fallback_search`-Schritt kollabieren, sondern als mehrstufige Plaene nach Kategorie, Capability und Risiko aufgebaut werden.

## Ablauf

```mermaid
flowchart TD
    A[IntentResult] --> B{Template vorhanden?}
    B -- Ja --> C[statisches Template]
    B -- Nein --> D{Kategorie / Capability}
    D -- Navigation --> E[resolve_navigation_target -> open_navigation_target]
    D -- Capability --> F[validate_dynamic_request -> delegate_capability_workflow -> summarize_dynamic_result]
    D -- Analysis --> G[collect_business_context -> run_dynamic_analysis -> summarize_findings]
    D -- Query --> H[collect_business_context -> synthesize_query_answer]
    D -- Command --> I[validate_dynamic_request -> collect_business_context -> execute_dynamic_command]
    D -- Unknown --> J[collect_business_context -> fallback_search]
```

## Betroffene Dateien

- `app/agents/neuro_planner.py`
- `tests/test_neuro_planner.py`
- `tests/test_neuro_pipeline.py`

## Ergebnis

- `generate_plan()` erzeugt fuer templatefreie Intents jetzt heuristische Mehrschritt-Plaene
- Dynamic Steps tragen `_dynamic_plan`, `_intent_category` und `_source_intent` im Parameterblock
- Navigation und andere bekannte, aber untemplated Intents laufen nicht mehr ueber den Ein-Schritt-Fallback
