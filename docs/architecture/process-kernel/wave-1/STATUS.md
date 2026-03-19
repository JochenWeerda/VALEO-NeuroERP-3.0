# Wave 1 - Command und Workflow-Grundlagen

**Status:** abgeschlossen
**Datum:** 2026-03-11

## Scope

Wave 1 liefert die fachlichen und technischen Grundlagen fuer Command-Katalog, Workflow-Versionierung, Explainability und zentrale Referenzpfade im Process Kernel.

## Zielbild

Die ersten Kernpfade sollen formalisiert, testbar und an nachfolgende Waves uebergebbar sein, ohne implizite UI-Zustaende oder Schattenmodelle.

## Lieferumfang

- Paket A: Command- und Workflow-Grundlagen
- Paket B: Policy, Referenzen und Ausnahmen
- Paket C: Frontend-Explainability und Integrationsvorbereitung
- Snapshot- oder Read-Contracts fuer priorisierte Kernmasken und Kerncockpits
- Getrennte Read-Contracts fuer `finance/kasse` ohne zweiten Schreibpfad neben POS

## Abnahmekriterien

- Command-Katalog und Workflow-Versionierung sind in den Kernpfaden verankert.
- Policy-Prioritaeten, Explainability und Cross-Domain-Referenzen sind produktiv angebunden.
- Priorisierte Kernmasken und Cockpits laufen auf expliziten Snapshot- oder Read-Contracts.
- Keine blockierende offene Wave-1-Luecke in den Paketen A bis C.

## Tests

- `pytest tests/test_process_kernel_wave1_contracts.py tests/test_app_bootstrap_imports.py -q`
- Ergebnis: 32 Tests bestanden
- `pnpm --filter @valero-neuroerp/frontend-web run type-check`
- Ergebnis: erfolgreich

## Status

`abgeschlossen`
Stand: 2026-03-11
