---
title: Handshake RLS-DOMAIN-SALES-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain Sales einschließlich Picklisten.
---

# Handshake RLS-DOMAIN-SALES-20261027 (Claude Code → Codex)

Reihenfolge: Integrationszweig ed77dded3 → #74 KI (dcd059ddc) → #75 Sales. Alembic:
`rls_verified_agrar_20261027 → rls_domain_ki_20261027 → rls_domain_sales_20261027`, ein Head.

Prüfstandsfenster nach deiner Freigabe genutzt:
- 17 Verhaltenstests ohne Übersprung;
- RLS-Gesamtsuite 303;
- 77 Bestandsmodule ohne neuen Fehlschlag. 27 sind vorbestehend rot in Studio-, Masken- und
  Architekturverträgen, Liste im QA-Bericht.

`valeo_probe` ist danach unverändert und hat keine offene Sitzung.

Für dich:
1. `pick_lists.py` war auf allen Schreibwegen mandantenoffen, und „Auftrag buchen“ setzte fremde
   Aufträge auf `in_delivery`. Jetzt ist es tokengebunden mit Rollback im Fehlerpfad, die
   Tabelle steht unter RLS. Die Picklisten-Maske bitte mit zwei Mandanten abnehmen.
2. Folgebefunde (QA): Kundenbezug auf `domain_crm.customers` (Klasse B), Belegketten ohne
   Verbund-FK, Picklisten-Kinder.
3. OpenAPI nur für `/pick-lists/` nachgezogen.
