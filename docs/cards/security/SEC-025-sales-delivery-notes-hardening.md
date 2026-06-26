# SEC-025

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_sales_delivery_notes.py, docs/roadmap/status/2026-04-01-security-hardening-phase-1.md

- Bereich: Sales Delivery Notes
- Risiko: freie Query-Tenants und ungescopte ID-Mutationen
- Ergebnis: alle Delivery-Note-Pfade lesen Tenant nur noch aus dem Kontext; Invoice-Statusupdate ist tenant-gescoped
- Tests: `tests/test_security_sales_delivery_notes.py`
