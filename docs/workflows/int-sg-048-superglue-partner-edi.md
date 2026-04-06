# INT-SG-048 - Superglue Partner EDI

## Ziel

Den bisherigen Preview-Pfad auf tenant-gebundene Partner-EDI-Bindings ziehen.

## Umgesetzt

- `edi_adapter.py` nutzt jetzt tenant-spezifische Tool-IDs und Runtime-Credentials.
- Partner-Mapping-Preview laeuft ueber denselben normalisierten Run-Pfad wie die anderen Connectoren.
- Die Admin-/Ops-Surface kennt den Connector ueber Lifecycle- und Tenant-Tool-Summaries.

## Verifikation

- `pytest tests/test_superglue_partner_preview.py tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`

