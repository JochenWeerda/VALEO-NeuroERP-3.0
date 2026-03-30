# NC-A8 - Verification + Policy Wave 2

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt

## Kontext

Nach NC-A6/NC-A7 war der Broker stark, aber die fachliche Korrektheit in Planner und Verification hing noch an vereinfachter Logik: nur der erste Step wurde verifiziert, Policies waren flach und State-Transitions hatten redundante Sonderlogik.

## Umsetzung

- temporale Policy-Bedingungen in `policy_code_engine.py`
- rekursive `PolicyBedingungsGruppe` fuer verschachtelte Regel-Logik
- Policy-Engine-Kopplung in `neuro_verification_engine.py`
- State-Graph-basierte Transition-Pruefung in der Verification
- per-Step-Verification im Planner-/Verification-Pfad

## Verifikation

- `pytest tests/test_neuro_planner.py tests/test_neuro_verification_engine.py tests/test_process_kernel_wave29_policy_query.py -q --no-cov`
- `python -m py_compile app/core/policy_code_engine.py app/services/neuro_verification_engine.py app/agents/neuro_planner.py`

## Offene Folgearbeit

- Tenant-spezifische Policy Overrides tiefer in die Runtime-/Verification-Pfade ziehen
- per-Step-Verification staerker in Broker-Trace und Decision Protocol surfacen
- dynamische Plan-Generierung fuer unbekannte Intents
