# INT-SG-057 - Superglue Procurement

## Ziel

Den Procurement-/Supplier-Rollout ueber den Superglue-Standardpfad verankern.

## Umgesetzt

- Supplier-Directory ist als Connector-Familie im Registry-/Bootstrap-Pfad enthalten.
- `command_handlers_procurement.py` surfact eine Procurement-Rollout-Sicht.
- Domain-Rollouts kennen Procurement als produktiv vorbereitete Domäne.

## Verifikation

- `pytest tests/test_superglue_connector_registry.py tests/test_superglue_domain_rollouts.py -q --no-cov`

