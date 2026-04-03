# SEC-031

- Bereich: Sales Orders
- Risiko: freie Query-/Payload-Tenants und ungescopte Folge-Mutationen im Auftragsrouter
- Ergebnis: Tenant kommt nur noch aus dem Kontext; Delete-, Re-Read- und Delivery-Pfade sind tenant-gescoped
- Tests: `tests/test_security_sales_orders.py`, `tests/test_sales_order_numbering.py`
