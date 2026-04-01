# SEC-009 - Admin Mobile SQL Whitelist

## Ziel

Identifier-Injection in dynamisch zusammengesetzten Admin-Mobile-Queries verhindern.

## Umsetzung

- Allow-Lists fuer Tabellen und ORDER-BY-Klauseln
- unbekannte Sortierung faellt auf `id` zurueck

## Tests

- `tests/test_security_admin_mobile.py`

