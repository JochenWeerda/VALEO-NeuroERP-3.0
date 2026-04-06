# INT-SG-060 - Superglue Broad Rollout

## Ziel

Agribusiness-, Service- und Analytics-Rollouts ueber denselben Connector-Standard vorbereiten.

## Umgesetzt

- Agribusiness-, Field-Service- und Analytics-Connectoren sind als Connector-Familien im Registry-/Bootstrap-Pfad enthalten.
- Domain-Rollouts und Admin-Surface surfacen die zusaetzlichen Domänen.
- Der Rollout bleibt upstream-first und thin-wrapper-only.

## Verifikation

- `pytest tests/test_superglue_connector_registry.py tests/test_superglue_domain_rollouts.py -q --no-cov`

