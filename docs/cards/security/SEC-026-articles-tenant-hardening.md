# SEC-026

## Status

- **Stand:** abgeschlossen (verifiziert 2026-06-25, Cards-Migration-Audit)
- **Evidenz:** tests/test_security_articles.py

- Bereich: Articles API
- Risiko: Payload-Spoofing und tenant-fremde Artikel-Nebenpfade
- Ergebnis: Kontext-Tenant ist jetzt fuer CRUD, Dokumente, Supplier, Preise, Stock und Image-Enrichment verbindlich
- Tests: `tests/test_security_articles.py`
