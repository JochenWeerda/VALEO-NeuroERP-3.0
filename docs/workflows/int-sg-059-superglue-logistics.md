# INT-SG-059 - Superglue Logistics

## Ziel

Logistics-/Carrier-Rollouts ueber denselben Superglue-Connector-Standard verankern.

## Umgesetzt

- Carrier-Tracking ist als Connector-Familie im Registry-/Bootstrap-Pfad enthalten.
- `warehouses.py` surfact eine Logistics-Rollout-Sicht fuer den Warehouse-Bereich.
- Domain-Rollouts und Admin-Surface kennen Logistics als aktive Connector-Domäne.

## Verifikation

- `pytest tests/test_superglue_domain_rollouts.py tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`

