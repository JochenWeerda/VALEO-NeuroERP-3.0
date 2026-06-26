# SEC-031

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_sales_orders.py

- Bereich: Sales Orders
- Risiko: freie Query-/Payload-Tenants und ungescopte Folge-Mutationen im Auftragsrouter
- Ergebnis: Tenant kommt nur noch aus dem Kontext; Delete-, Re-Read- und Delivery-Pfade sind tenant-gescoped
- Tests: `tests/test_security_sales_orders.py`, `tests/test_sales_order_numbering.py`
