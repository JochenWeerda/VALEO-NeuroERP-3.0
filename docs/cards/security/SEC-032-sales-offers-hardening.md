# SEC-032

- Bereich: Sales Offers
- Risiko: freie Query-/Payload-Tenants und ungescopte Convert-/Update-/Delete-Pfade im Angebotsrouter
- Ergebnis: Tenant kommt nur noch aus dem Kontext; Item-Reset, Soft-Delete, Convert und Re-Reads sind tenant-gescoped
- Tests: `tests/test_security_sales_offers.py`
