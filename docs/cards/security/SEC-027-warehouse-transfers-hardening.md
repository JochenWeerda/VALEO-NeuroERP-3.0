# SEC-027

- Bereich: Warehouse Transfers
- Risiko: freie Tenant-Queries und ungescopte Transfer-/Correction-ID-Pfade
- Ergebnis: Transfers, Lines, Corrections und Bin-Locations sind jetzt an den Kontext-Tenant gebunden
- Tests: `tests/test_security_warehouse_transfers.py`
