# Wave-72 Status

## Scope

Knowledge-backed Onboarding Workspaces — gefuehrte Einarbeitung aus Wissensobjekten und Trainingspfaden.

## Zielbild

Wave 72 verbindet Onboarding-Workspaces mit dem Knowledge Core. Neue Nutzer erhalten rollen- und tenantbezogene Lernpfade, deren Inhalte aus versionierten Wissensobjekten gespeist werden.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/onboarding_workspaces.py` | Workspace-Modell und Bundle-Aufbau | abgeschlossen |
| AP2 | `app/api/v1/endpoints/training.py` | Onboarding-/Trainings-HTTP-Endpunkte | abgeschlossen |
| AP3 | `app/core/knowledge_core_contracts.py` | Kanal- und Objektbezug fuer Onboarding | abgeschlossen |

## Abnahmekriterien

- Onboarding-Workspaces aggregieren Schritte, Quellen und Fortschritt.
- Trainings-Endpunkte liefern tenant-isolierte Workspace-Snapshots.
- Knowledge-Objekte werden in Workspace-Schritte referenziert statt kopiert.

## Tests

`tests/test_process_kernel_wave72_onboarding_workspaces.py` — 4 Tests

- Contract- und API-Tests fuer Workspace-Aufbau und Trainings-Endpunkte
- `python -m pytest tests/test_process_kernel_wave72_onboarding_workspaces.py -q --no-cov`

## Status

`abgeschlossen` - 2026-03-19 - Knowledge-backed Onboarding Workspaces verfuegbar.
