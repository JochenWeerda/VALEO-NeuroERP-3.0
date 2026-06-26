# SEC-029

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_agrar_contracts.py

- Bereich: Agrar Contracts
- Risiko: freie Query-Tenants und ungescopte Contract-/Allocation-ID-Zugriffe
- Ergebnis: alle Contract- und Allocation-Pfade lesen Tenant nur noch aus dem Kontext
- Tests: `tests/test_security_agrar_contracts.py`
