# NC-A10 - Dynamic Plan Generation

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt
**Abhaengigkeit:** NC-A3/A4, NC-A9

## Kontext

Wave 4 verlangt, dass der Planner auch ohne statisches Template belastbare Schrittfolgen erzeugen kann. Bisher liefen solche Faelle fast immer nur ueber `fallback_search`.

## Umsetzung

- `generate_plan()` nutzt bei fehlendem Template jetzt `_generate_dynamic_steps(...)`
- Die Heuristik unterscheidet Navigation, Approval, Capability-Delegation, Analysis, Query, Command und Unknown
- Dynamische Command-Plaene markieren den Ausfuehrungsschritt ab `medium` Risiko als approval-pflichtig
- Pipeline- und Planner-Tests decken Navigation und templatefreie Commands explizit ab

## Dateien

- `app/agents/neuro_planner.py`
- `tests/test_neuro_planner.py`
- `tests/test_neuro_pipeline.py`

## Verifikation

- `pytest tests/test_neuro_planner.py tests/test_neuro_pipeline.py -q --no-cov`
- `python -m py_compile app/agents/neuro_planner.py`
