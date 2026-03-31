# SEC-002 - Local Secret Management

## Ziel

Lokale Entwicklung und Betriebsvorbereitung sollen Secrets zentral pflegen koennen, ohne wieder harte Werte ins Repo oder in `.env`-Defaults zurueckzuschreiben.

## Umsetzung

- `app/services/secrets_vault.py` unterstuetzt jetzt zusaetzlich `keyring` als optionalen Provider
- ein Keyring-Metadaten-Index erlaubt `list`, `rotate` und `delete` auch ueber Prozessgrenzen hinweg
- `scripts/security/secret_store.py` stellt `set`, `get`, `list`, `delete` und `health` als lokales CLI bereit
- `scripts/security/README.md` dokumentiert den praktischen Ablauf fuer lokale Pflege

## Ergebnis

- auf Entwickler-Maschinen koennen Secrets zentral im OS-Keyring gepflegt werden
- ohne `keyring` bleibt der bestehende `memory`-/`env`-Fallback erhalten
- der offene Restpunkt verschiebt sich auf echte externe Produktions-Vault-Anbindung statt lokaler Pflege
