# SEC-002 - Local Secret Management

**Lane:** Security
**Prioritaet:** P1
**Status:** umgesetzt

## Umsetzung

- optionaler `keyring`-Provider im bestehenden Secrets-Vault
- persistenter Keyring-Metadaten-Index fuer `list`/`rotate`/`delete`
- CLI unter `scripts/security/secret_store.py`
- README-Nutzung fuer lokale Secret-Pflege nachgezogen
