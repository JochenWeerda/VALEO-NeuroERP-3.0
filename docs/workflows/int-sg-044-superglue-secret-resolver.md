# INT-SG-044 - Superglue Secret Resolver

## Ziel

Connector- und tenant-spezifische Secrets in den Laufzeitpfad ziehen.

## Umgesetzt

- `build_superglue_secret_keys()` erzeugt connector-scoped Schluessel vor Tenant-/Global-Fallback.
- `resolve_superglue_connector_value()` versorgt Bootstrap und Runtime aus derselben Quelle.
- DMS-, EDI- und CRM-Adapter nutzen jetzt tenant-spezifische Runtime-Credentials.

## Verifikation

- `pytest tests/test_superglue_secret_resolver.py tests/test_superglue_document_adapter.py tests/test_superglue_partner_preview.py tests/test_superglue_customer_profile_adapter.py -q --no-cov`

