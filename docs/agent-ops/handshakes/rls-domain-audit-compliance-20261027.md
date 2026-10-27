---
title: Handshake RLS-DOMAIN-AUDIT-COMPLIANCE-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain audit/compliance.
---

# Handshake RLS-DOMAIN-AUDIT-COMPLIANCE-20261027 (Claude Code → Codex)

## Reihenfolge

`#63 → #64 → #65 pricing → #66 hr → dieser PR`. Die Alembic-Kette ist
`… → rls_domain_hr_20261027 → rls_domain_audit_compliance_20261027`.

## Für Codex

1. **Fachkorrekturen außerhalb reiner Migrationsarbeit:**
   - `compliance_pcn_lifecycle_service.py` liest und ändert nur im eigenen Mandanten.
   - `intrastat.py`: `PUT` liefert 404 statt eines Erfolgs ohne Wirkung.

   Bestehende Verträge sind grün: `test_steuernachweis_mandant_vertrag.py`,
   `test_dom_compliance_004.py` und zwei Intrastat-Tests, zusammen 63 passed.
2. **Neuer FK auf eine P5-Tabelle:** `compliance_pcn_meldungen` bekommt
   `UNIQUE (id, tenant_id)`, der Verlauf hängt per Verbund-FK daran. Die Policies der
   Tabelle sind unberührt.
3. **Nicht geändert, zur Kenntnis:** `sales_delivery_notes.py:54` hat eine ungenutzte
   Konstante `DEFAULT_TENANT` (Domain sales). Das Muster „gehört nicht zu Tenant“ (siehe QA)
   kommt in den Domains agrar, controlling und vvvo.
4. **Testhinweis:** Bestandstests mit `TestClient(app.main)` brauchen den Conftest und
   `DATABASE_URL` auf dem Prüfstand. Ohne `DATABASE_URL` zielt die App auf den
   Docker-Host `postgres`.

## Nicht berührt

P0–P7, dein Arbeitsbaum, `compliance_dsgvo.py`, keine Live-DB, `valeo_probe` ohne
Restzeilen.
