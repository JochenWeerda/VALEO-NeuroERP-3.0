# NC-A13 - Tenant Policy Overrides

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt
**Abhaengigkeit:** NC-A8, Gap 014

## Kontext

Nach NC-A8 war die Policy Engine formal mit der Verification gekoppelt, Tenant-Overrides wurden aber in der Runtime nicht durchgaengig ausgewertet. Es gab damit eine sachliche Luecke zwischen Admin-/Tenant-Settings und effektiver Policy-Entscheidung.

## Umsetzung

- Runtime-Normalisierung fuer explizite Override-Payloads, `policy_set_id`-Maps und bestehende regelzentrierte Tenant-Settings
- Regelweise Parameter-Ueberschreibung fuer Schwellenwerte wie `brutto_eur` oder `betrag`
- Plan- und Step-Level-Passthrough in der Verification
- DB-gestuetztes Nachladen vorhandener Tenant-Settings, wenn kein explizites Override im Plan uebergeben wird

## Dateien

- `app/core/policy_code_engine.py`
- `app/services/neuro_verification_engine.py`
- `tests/test_neuro_verification_engine.py`
- `tests/test_process_kernel_wave29_policy_query.py`

## Verifikation

- `pytest tests/test_neuro_verification_engine.py tests/test_process_kernel_wave29_policy_query.py -q --no-cov`
- `python -m py_compile app/core/policy_code_engine.py app/services/neuro_verification_engine.py`
