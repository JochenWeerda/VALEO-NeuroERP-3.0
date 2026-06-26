# SEC-027

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_warehouse_transfers.py, docs/roadmap/status/2026-04-01-security-hardening-phase-1.md

- Bereich: Warehouse Transfers
- Risiko: freie Tenant-Queries und ungescopte Transfer-/Correction-ID-Pfade
- Ergebnis: Transfers, Lines, Corrections und Bin-Locations sind jetzt an den Kontext-Tenant gebunden
- Tests: `tests/test_security_warehouse_transfers.py`
