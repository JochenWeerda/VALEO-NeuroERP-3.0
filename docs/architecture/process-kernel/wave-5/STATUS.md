# Wave 5 - E2E Agrar-Prozesskette und Command-Layer

**Status:** abgeschlossen
**Datum:** 2026-03-11

## Scope

Wave 5 fuehrt den Business-Command-Catalog, Dispatcher, E2E-Referenzkette, Workflow-Simulation und Agent-Manifest fuer Kernprozesse zusammen.

## Zielbild

Kernprozessschritte sollen formale Commands, Pruefbedingungen und agentensichere Ausfuehrungsregeln erhalten.

## Lieferumfang

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Business-Command-Catalog | abgeschlossen |
| AP2 | E2E-Referenzkette Kontrakt bis FiBu | abgeschlossen |
| AP3 | Rohwarenabrechnung und Qualitaets-Preisbindung | abgeschlossen |
| AP4 | Workflow-Simulation und Sandbox | abgeschlossen |
| AP5 | Agent- und Action-Layer fuer Command-Contracts | abgeschlossen |

## Abnahmekriterien

- Alle Kernprozessschritte haben formale Command-Definitionen mit Preconditions und Rollenpruefung.
- Die E2E-Kette Kontrakt bis FiBu ist lueckenlos modelliert.
- Dispatcher lehnt ungueltige Ausfuehrungen deterministisch ab.
- Agent-Manifest macht erlaubte und gesperrte KI-Kommandos sichtbar.

## Tests

- `pytest tests/test_process_kernel_wave5_commands.py tests/test_process_kernel_wave5_e2e_chain.py -q`
- Ergebnis: 41 Wave-5-Tests bestanden

## Status

`abgeschlossen`
Stand: 2026-03-11
