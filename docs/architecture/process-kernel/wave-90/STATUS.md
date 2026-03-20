# Wave 90 - Workflow-Template Marketplace intern

## Scope

Interner Marketplace fuer kuratierte Workflow-Templates, damit neue Prozessvarianten als installierbare Vorlagen statt als Einzelfall-Implementierung ausgerollt werden koennen.

## Zielbild

Tenant-Teams sollen kuratierte Workflow-Vorlagen finden, previewen und in einen kontrollierten Review-/Installationspfad ueberfuehren koennen.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/workflow_template_marketplace.py` | Katalog-, Preview- und Install-Contracts fuer interne Workflow-Templates | abgeschlossen |
| AP2 | `app/api/v1/endpoints/workflow_template_marketplace.py` | API fuer Marketplace-Listing, Detailansicht, Preview und Installation | abgeschlossen |
| AP3 | `tests/test_process_kernel_wave89_workflow_template_marketplace.py` | Contract-Tests fuer Katalog, Preview und Installationspfad | abgeschlossen |

## Abnahmekriterien

- Interner Template-Katalog ist ueber API abrufbar.
- Templates lassen sich tenant-spezifisch previewen.
- Installationspfad liefert kontrollierte Follow-ups und Monitoring-Hooks.

## Tests

- `python -m pytest tests/test_process_kernel_wave89_workflow_template_marketplace.py -q --no-cov`

## Status

`abgeschlossen` - 2026-03-20 - Interner Workflow-Template-Marketplace mit kuratiertem Katalog, Preview- und Installationspfad produktiv verdrahtet.
