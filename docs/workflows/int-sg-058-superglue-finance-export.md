# INT-SG-058 - Superglue Finance Export

## Ziel

Finance-/Export-Rollouts ueber denselben Superglue-Connector-Standard verankern.

## Umgesetzt

- Finance-Export ist als Connector-Familie im Registry-/Bootstrap-Pfad enthalten.
- `finance_followup.py` und `export_service.py` surfacen den Finance-Rollout.
- Domain-Rollouts und Admin-Surface kennen Finance als aktive Connector-Domäne.

## Verifikation

- `pytest tests/test_superglue_domain_rollouts.py tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`

