# INT-SG-046 - Superglue Result Normalization

## Ziel

Upstream-Run-Resultate in einen stabilen VALEO-Envelope ueberfuehren.

## Umgesetzt

- `normalize_superglue_run_result()` entkoppelt Adapter und Execution-Service vom variierenden Upstream-Nesting.
- `SuperglueExecutionService` schreibt normalisierte Run-Metadaten in Journal und Audit-Payload.
- Die Fachadapter nutzen denselben Normalisierungspfad fuer read-/simulate-Ergebnisse.

## Verifikation

- `pytest tests/test_superglue_document_adapter.py tests/test_superglue_partner_preview.py tests/test_superglue_customer_profile_adapter.py -q --no-cov`

