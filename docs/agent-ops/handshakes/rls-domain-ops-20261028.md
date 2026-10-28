---
title: Handshake RLS-DOMAIN-OPS-20261028
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe Claude -> Codex fuer RLS-Domain ops Teil 1 (Schema) und die Datenentscheidung zu Teil 2 (Tabellen ohne Mandant).
---

# Handshake RLS-DOMAIN-OPS-20261028 (Claude Code → Codex)

- Basis `claude/urheber-aus-token-20261028` (#83), Zweig `claude/rls-domain-ops-20261028`.
  Alembic `service_anfragen_20261027 → rls_domain_ops_20261028`, ein Head. Keine Datenaenderung; live kein Abbruchgrund.
- **Live-relevant:** `kon_contract` und `ops_pcn_meldungen` unter getrennten Policies; vier Nummern je Mandant eindeutig
  statt systemweit; Verbund-FKs fuer acht Kind-Eltern-Verweise.
- **Datenentscheidung Teil 2:** 21 `domain_ops`-Tabellen ohne Mandantenspalte, 13 mit Live-Zeilen (Liste im QA-Dokument).
  Bevor eine Spalte kommt, muss jede Zeile einem Mandanten zugeordnet werden. Dazu: 31 EDI-Nachrichten und eine
  Prozessinstanz mit `default`, ein Fahrzeug und 79 Chargen mit `legacy-unassigned`.
- Nicht beruehrt: `reklamationen` (dein Claim), `ops_chargen`, Studio/Masken, Systemrollen, Live.
