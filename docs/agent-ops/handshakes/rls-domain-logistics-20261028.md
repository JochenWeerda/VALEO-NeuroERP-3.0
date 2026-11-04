---
title: Handshake RLS-DOMAIN-LOGISTICS-20261028
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe Claude -> Codex fuer RLS-Domain logistics mit Mandant aus dem Token in Touren-, Fracht-, ePOD- und Dispositionswegen.
---

# Handshake RLS-DOMAIN-LOGISTICS-20261028 (Claude Code → Codex)

- Basis `claude/rls-domain-ops-20261028` (#84), Zweig `claude/rls-domain-logistics-20261028`.
  Alembic `rls_domain_ops_20261028 → rls_domain_logistics_20261028`, ein Head. Live kein Abbruchgrund.
- **Live-relevant:** Alle Logistikwege nehmen den Mandanten aus dem Token; `X-Tenant-ID` wird nicht mehr gelesen. Fremde
  Touren, Stopps und Tarife sind 404 (vorher teils sichtbar, teils 403). `/logistik/tracking/{id}` ist nicht oeffentlich
  und nimmt kein `share_token` mehr an.
- **Spediteur-Rechnung:** meldet `entwurf` (Buchungsentwurf) statt `gebucht`; doppelte Nummer 409. Fachlich gehoert sie
  auf den Eingangsrechnungsweg (QA, Offen).
- 15 Bestandstests auf das neue Verhalten umgestellt (Liste im QA-Dokument).
- Nicht beruehrt: `domain_log.*` (LOADING-ATOMIC-ACTOR), Studio/Masken, Systemrollen, Live.
