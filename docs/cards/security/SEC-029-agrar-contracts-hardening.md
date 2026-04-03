# SEC-029

- Bereich: Agrar Contracts
- Risiko: freie Query-Tenants und ungescopte Contract-/Allocation-ID-Zugriffe
- Ergebnis: alle Contract- und Allocation-Pfade lesen Tenant nur noch aus dem Kontext
- Tests: `tests/test_security_agrar_contracts.py`
