# SEC-014 - Externer Vault Adapter und Startup-Fail-Fast

## Ziel

Die lokale Secret-Verwaltung fuer den Produktivpfad um einen echten externen Provider erweitern und den App-Start in Produktion an eine gueltige Secret-Konfiguration koppeln.

## Umsetzung

- `app/services/secrets_vault.py`
  - HashiCorp Vault KV-v2 als externer Provider
  - Lesen, Schreiben, Loeschen und Health-Check gegen den konfigurierten Vault
  - `validate_startup_secrets()` fuer Production-Startup-Guards
- `app/core/config.py`
  - Secret-Provider- und HashiCorp-Vault-Konfiguration
  - Flag `REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION`
- `app/main.py`
  - Startup validiert Secret-Konfiguration vor EventBus-/Consumer-Start
- `scripts/security/secret_store.py`
  - surfact aktive Secret-Konfiguration via `config`

## Abnahmekriterien

- Produktion startet nicht mit `API_DEV_TOKEN`
- Produktion startet nicht mit lokalem Secret-Provider, wenn externe Secrets erzwungen sind
- `SECRET_KEY` und `ENCRYPTION_KEY` muessen fuer den Production-Start aufloesbar sein
- HashiCorp Vault kann als Provider gelesen und beschrieben werden

## Tests

- `tests/test_secrets_vault.py`
- `tests/test_security_startup_guards.py`
