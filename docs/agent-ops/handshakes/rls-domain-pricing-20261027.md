---
title: Handshake RLS-DOMAIN-PRICING-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die erste RLS-Domain domain_pricing.
---

# Handshake RLS-DOMAIN-PRICING-20261027 (Claude Code → Codex)

## Reihenfolge

`#63 (P7) → #64 RLS-DOMAIN-MATRIX → dieser PR`. Die Alembic-Kette ist
`rls_system_role_20261026 → rls_domain_pricing_20261027`. Ändert die P3/P5-Korrektur die
Kette, hänge ich `down_revision` um.

## Für Codex

1. **P5-Formtest:** `test_alle_rls_tabellen_tragen_genau_die_mandantenpolicy` ist auf dem
   Prüfstand rot für `domain_pricing.price_lists`/`price_list_items` (getrennte Form). Die
   Datei habe ich nicht geändert. Bitte bei der Korrektur der Altform die getrennte Form
   zulassen oder die Formprüfung `tests/test_rls_policy_shape.py` überlassen.
2. **Live-Aktivierung:** Die Migration nimmt `ACCESS EXCLUSIVE` auf beiden Tabellen (live 0
   Zeilen) und bricht bei Platzhalter-Mandanten ab. Sie setzt `public.rls_current_tenant()`
   aus P3 voraus.
3. **Frontend:** `packages/frontend-web/src/lib/api/konditionen.ts` hängt `?tenant_id=` an.
   Das ist harmlos, der Parameter wird ignoriert, sollte aber bei Gelegenheit weg. Nicht
   geändert, weil die Datei nicht in meinem Besitz ist.

4. **OpenAPI:** `docs/schnittstellen/openapi.json` habe ich nur für `/api/v1/price-lists/`
   und `PriceListCreate` nachgezogen. `generate_openapi.py --check` meldet auf dieser Basis
   zusätzlich Drift in `/api/v1/finance/closing-checklists*`, ein entfallener
   `tenant_id`-Query-Parameter aus 9b4308339. Die Drift ist vorbestehend und liegt im
   Leadbesitz; ich habe sie nicht übernommen.

## Nicht berührt

P0–P7-Dateien, `preisfindung_service.py` (nur lesend geprüft und im Test benutzt), keine
Live-DB, kein Reset, `valeo_probe` unverändert.
