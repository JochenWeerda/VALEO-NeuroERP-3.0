---
title: Handshake STANDARDMANDANT-ABBAU-20261028
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe Claude -> Codex fuer den Abbau der Standardmandant-Rueckfaelle ueber Konfiguration und feste UUID sowie die Kanal-Freigaben mit gepruefter Rolle.
---

# Handshake STANDARDMANDANT-ABBAU-20261028 (Claude Code → Codex)

- Basis `claude/rls-domain-logistics-20261028` (#85), Zweig `claude/standardmandant-abbau-20261028`.
  Alembic `rls_domain_logistics_20261028 → crm_leads_spalten_20261028 → rls_nutrient_compositions_20261028`, ein Head.
  Live kein Abbruchgrund (Leads-Spalten vorhanden, Naehrstoffe 0 Zeilen).
- **Live-relevant:** CRM-Kunden/-Leads, Duenger, Saatgut, Naehrstoffe, CRM-Berichte, Kundenerweiterungen und
  Kanal-Wege nehmen den Mandanten aus dem Token (`?tenant_id=` und Metadaten werden nicht mehr gelesen); 33 Dienste
  verweigern ohne Mandant. Kunden-Antworten tragen den gespeicherten Mandanten (auch `valeo`) statt des Standardmandanten.
- **Freigaben:** `POST /channels/{kanal}/process-actions/{id}/decision` — Entscheider aus dem Token, `approver_role` muss eine
  gepruefte Rolle sein. Freigaben ueber den Slack-/Teams-Eingang 403, bis eine Nutzerzuordnung existiert.
- **Studio (dein Bereich):** `list_sources` meldet erst 741, dann 848 Quellen; die CLI-Migrationsplanung bricht deshalb
  reihenfolgeabhaengig ab (QA, Offen).
- Nicht beruehrt: `reklamation_api.py` (dein Claim; nur ein Vergleich, als erlaubt verzeichnet), Studio/Masken, Live.
