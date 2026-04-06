# INT-SG-052 - Superglue Idempotency

## Ziel

Replay- und Idempotenz-Schutz fuer reale Connector-Writes schliessen.

## Umgesetzt

- Execution-Journal speichert `idempotency_key`, Replay-Herkunft, Kosten und Latenz.
- `find_latest_execution_by_idempotency_key()` ermoeglicht Replay-Erkennung fuer Write-Runs.
- Replays werden im Envelope als solche surfact statt erneut auszufuehren.

## Verifikation

- `pytest tests/test_superglue_execution_guardrails.py tests/test_superglue_refresh_and_quarantine.py -q --no-cov`

