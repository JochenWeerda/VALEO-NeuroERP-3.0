---
title: Handshake RLS-DOMAIN-OPS-TEIL2-20261028
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe Claude -> Codex fuer zehn live leere domain_ops-Tabellen unter RLS und ihre Wege im Token-Mandanten.
---

# Handshake RLS-DOMAIN-OPS-TEIL2-20261028 (Claude Code → Codex)

- Basis `claude/rls-domain-erp-20261028` (#87), Zweig `claude/rls-domain-ops-teil2-20261028`.
  Alembic `rls_domain_erp_20261028 → rls_domain_ops_teil2_20261028`, ein Head.
  Live kein Abbruchgrund: alle zehn Tabellen 0 Zeilen; `UNIQUE (id, tenant_id)` auf `ops_fahrzeuge` wird angelegt
  (live fehlt es, 1 Zeile).
- **Live-relevant:** Dokumente, Lieferanten-Dokumente, Waagen/Wiegungen, Fuhrpark-Schaeden/-Bussgelder/-Statushistorie,
  Frachttarife und Rahmenvertraege nur noch im Token-Mandanten; Urheber kommen aus dem Token (Rumpfangaben werden
  ignoriert). Partiepflichtige Wiegungen lassen sich erstmals anlegen.
- **Repositories** der sieben Modelle verlangen den Mandanten im Konstruktor; ein Aufrufer ohne Mandant scheitert mit `TypeError`/`ValueError`.
- Nicht beruehrt: 13 tenantlose ops-Tabellen mit Live-Zeilen (Zuordnung durch die Fachseite), `ops_fahrer`, Studio/Masken, Live.
