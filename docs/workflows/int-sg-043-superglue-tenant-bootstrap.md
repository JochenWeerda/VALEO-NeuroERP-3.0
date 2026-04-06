# INT-SG-043 - Superglue Tenant Bootstrap

## Ziel

Tenant-spezifische Superglue-Systems und Tools reproduzierbar aus VALEO provisionieren.

## Umgesetzt

- `superglue_connector_registry.py` liefert deterministische tenant-spezifische Tool-/System-Bindings.
- `superglue_tool_provisioning.py` provisioniert Systems und Tools pro Tenant ueber `/v1/systems` und `/v1/tools`.
- `external_agent_integrations.py` surfact Bootstrap und tenant-spezifische Tool-Summaries.

## Verifikation

- `pytest tests/test_superglue_connector_registry.py tests/test_superglue_tool_provisioning.py -q --no-cov`

