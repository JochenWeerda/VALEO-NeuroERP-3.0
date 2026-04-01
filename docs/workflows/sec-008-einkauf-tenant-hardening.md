# SEC-008 - Einkauf Tenant Hardening

## Ziel

Tenant-Isolation, Update-Whitelists und generische Fehlermeldungen fuer den Einkauf-Router nachziehen.

## Umsetzung

- Tenant-Scope in Lieferanten-, Bestellungs-, Rechnungseingangs- und Zahlungslauf-Pfaden
- Mass-Assignment-Whitelists fuer Update-Endpunkte
- keine rohen DB-/Exception-Strings mehr im Response

## Tests

- `tests/test_security_einkauf_router.py`

