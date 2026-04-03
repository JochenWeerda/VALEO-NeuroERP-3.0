# SEC-025

- Bereich: Sales Delivery Notes
- Risiko: freie Query-Tenants und ungescopte ID-Mutationen
- Ergebnis: alle Delivery-Note-Pfade lesen Tenant nur noch aus dem Kontext; Invoice-Statusupdate ist tenant-gescoped
- Tests: `tests/test_security_sales_delivery_notes.py`
