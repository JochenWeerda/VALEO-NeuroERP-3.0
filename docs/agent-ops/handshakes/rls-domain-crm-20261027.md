---
title: Handshake RLS-DOMAIN-CRM-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain CRM (ohne Dienst-Tabellen) mit Fachkorrekturen am CRM-Router und den DSGVO-Kurzwegen.
---

# Handshake RLS-DOMAIN-CRM-20261027 (Claude Code → Codex)

## Basis und Reihenfolge

- Basis: `claude/rls-domain-sales-20261027` (#75). Der PR zielt auf den Sales-Zweig und wird nach #75 integriert.
- Alembic: `rls_domain_sales_20261027 → rls_domain_crm_20261027`. `alembic heads` zeigt einen einzigen Head.

## Prüfstand

Das Fenster wurde nach deiner Freigabe genutzt: 58 Verhaltenstests ohne Übersprung, Gegenprobe ohne Verbund-FKs 21 rot, RLS-Gesamtsuite 331, Bestand 2788 passed (22 rot wie Basis).
Danach steht `valeo_probe` unverändert auf `loading_stop_fk_20261023`, 0 offene Sitzungen.

## Für dich

1. **Live-relevant:** `app/crm/router.py` hängt über das Root-`main.py` (Produktiv-Image) unter `/api/v1/crm`. Bisher galt dort
   der Kopf `X-Tenant`, ohne ihn `"default"`. Jetzt gilt der Token-Mandant. Wer den Router ohne verifizierten Mandanten
   aufruft, bekommt 401/403.
2. `/crm/gdpr/anonymize` antwortet jetzt mit 409 und verweist auf den Löschantrag. Bisher meldete er „anonymisiert“,
   ohne etwas zu ändern, weil die Zieltabelle `domain_shared.business_partners` nicht existiert.
   `/crm/gdpr/data-export` liest `domain_crm.business_partners` mandantengebunden; bisher endete der Aufruf mit 500.
3. OpenAPI nur für `/api/v1/crm/*` übernommen. Die vorbestehende Drift (`/finance/closing-checklists*`,
   `/agrar/biostimulanzien*`, `/weighing-tickets*`) bleibt bei dir.
4. `tests/rls_domain_support.py`: `seed_row` legt Pflicht-Eltern automatisch an (gleicher Mandant). Werte kommen aus
   CHECK-ANY, eindeutige Ganzzahlen werden zufällig gewählt, Mandanten registriert nur der Eigentümer.
   `_parents=False` gilt für abgewiesene Anlagen. Alle Domain-Tests bestehen damit.
5. Der Vertragstest der Rückfälle erfasst jetzt auch `x_tenant`. Die Baseline sinkt um `app/crm/seed.py`.
6. Folgebefunde (QA-Dokument): Kundenstamm `public.kunden*` ohne Mandant; der Löschantrag erfasst
   `business_partners` nicht; inventory-Verweise auf Partner haben einfache FKs.
7. Nicht berührt: Dienst-Tabellen und `services/*`, deine Lead-Slices (Agrar), Studio/Masken, Systemrollen, Live.
