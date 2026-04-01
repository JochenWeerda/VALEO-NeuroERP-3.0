# SEC-014 - Externer Vault Adapter und Startup-Fail-Fast

- Status: abgeschlossen
- Scope: `app/services/secrets_vault.py`, `app/core/config.py`, `app/main.py`, `scripts/security/secret_store.py`
- Lieferung: HashiCorp Vault als externer Provider plus Production-Startup-Guard fuer Secret-Quelle und Pflicht-Secrets
- Nachweis: `tests/test_secrets_vault.py`, `tests/test_security_startup_guards.py`
