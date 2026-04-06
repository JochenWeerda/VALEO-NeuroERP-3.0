# INT-SG-050 - Superglue File References

## Ziel

Artefakte und File-References aus Superglue-Runs im VALEO-Envelope nutzbar machen.

## Umgesetzt

- `ExternalArtifactReference` erweitert den zentralen Integration-Contract.
- `extract_superglue_artifacts()` normalisiert Run-Artefakte aus direkten und verschachtelten Upstream-Payloads.
- Journal und Monitoring zaehlen Artefakte jetzt pro Lauf mit.

## Verifikation

- `pytest tests/test_superglue_domain_rollouts.py tests/test_superglue_refresh_and_quarantine.py -q --no-cov`

