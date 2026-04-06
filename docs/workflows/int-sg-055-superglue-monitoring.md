# INT-SG-055 - Superglue Monitoring

## Ziel

Connector-Laufzeiten, Fehler, Replays, Artefakte und Kosten zentral surfacen.

## Umgesetzt

- `superglue_monitoring.py` aggregiert Journal und Quarantaene pro Tenant und Connector.
- Die Monitoring-API liefert Run-Zahlen, Fehlerraten, Artefakte und Kosten.
- Die Admin-Seite zeigt die komprimierte Monitoring-Sicht.

## Verifikation

- `pytest tests/test_superglue_refresh_and_quarantine.py tests/test_process_kernel_wave88_external_agent_integrations.py -q --no-cov`

