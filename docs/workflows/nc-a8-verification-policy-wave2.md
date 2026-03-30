# NC-A8 - Verification + Policy Wave-2 Integration

## Ziel

Die Verification Engine enger mit der Policy Engine und dem State Graph koppeln, damit nicht mehr nur ein erster Plan-Schritt geprueft wird, sondern der gesamte Plan mit per-Step-Ergebnissen, temporalen Policies und verschachtelten Bedingungen.

## Ablauf

1. `PolicyBedingung` unterstuetzt jetzt auch temporale Bedingungen:
   - `WOCHENTAG`
   - `ZEITRAUM`
   - `UHRZEIT`
2. `PolicyBedingungsGruppe` erlaubt verschachtelte `AND`-/`OR`-Logik fuer komplexere Regeln.
3. `PolicyRegel.matches()` kann entweder klassische Bedingungslisten oder eine rekursive Bedingungsgruppe auswerten.
4. `neuro_verification_engine.verify_plan()` prueft Plan-Level und optional jeden Step einzeln ueber `steps`.
5. `check_policy_conformity()` nutzt die Policy Engine und mappt Policy-Aktionen auf Verification-Violations.
6. `check_state_transition()` nutzt `StateGraphService.validate_transition()` statt lokaler Sonderlogik.
7. `neuro_planner.verify_plan()` reicht jetzt alle Plan-Steps an die Verification Engine durch.

## Betroffene Dateien

- `app/core/policy_code_engine.py`
- `app/services/neuro_verification_engine.py`
- `app/agents/neuro_planner.py`
- `tests/test_neuro_verification_engine.py`
- `tests/test_neuro_planner.py`
- `tests/test_process_kernel_wave29_policy_query.py`

## Ergebnis

- Policies koennen jetzt komplexere fachliche Kontexte ausdruecken, ohne dass neue Sonderlogik in der Verification Engine eingebaut werden muss.
- Verification liefert per-Step-Ergebnisse fuer Broker/Pipeline-Folgeschritte.
- State-Transitions sind mit dem zentralen State Graph abgestimmt statt doppelt modelliert.

## Bekannte Restgrenzen

- Die Policy Engine arbeitet weiterhin primaer mit Default-Sets; echte produktive Tenant-Override-Nutzung in der Verification bleibt ein weiterer Ausbaupunkt.
- Der Planner erzeugt weiterhin statische Templates; die Wave-2-Pruefung verbessert Korrektheit, nicht die Plan-Dynamik.
