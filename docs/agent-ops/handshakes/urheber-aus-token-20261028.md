---
title: Handshake URHEBER-AUS-TOKEN-20261028
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe Claude -> Codex fuer fuenf Wege, die den Urheber aus dem Anfragekoerper nahmen, und den geschaerften Identitaetsvertrag.
---

# Handshake URHEBER-AUS-TOKEN-20261028 (Claude Code → Codex)

- Basis `claude/tenant-fallback-abbau-20261027` (#82), Zweig `claude/urheber-aus-token-20261028`. Keine Migration.
- **API-Vertrag:** `AmendmentCreate` ohne `tenantId`/`createdBy`, `PayrollExportCreateIn` ohne `createdBy`; Angaben in
  `business_partner.audit` werden beim Schreiben ignoriert. Ein Nachtrag zu einem Vertrag ausserhalb des Mandanten ist 404.
- **Vertragstest** `tests/test_keine_client_identitaet.py` ist schaerfer (Syntaxbaum statt Zeichenzaehlung, camelCase,
  `audit.*`, `app/routers`). Neue Treffer in fremden Zweigen sind echte Funde.
- Offen: Rahmenvertraege ohne Mandant (Teil von RLS-DOMAIN-OPS).
- Nicht beruehrt: Studio/Masken, Systemrollen, Codex-Claims, Live.
