---
title: Handshake RLS-DOMAIN-ERP-20261028
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-28
version: 1.0.0
description: Uebergabe Claude -> Codex fuer domain_erp Teil 1 unter RLS und die reparierten Debitoren-, Export- und FiBu-Connector-Wege.
---

# Handshake RLS-DOMAIN-ERP-20261028 (Claude Code → Codex)

- Basis `claude/standardmandant-abbau-20261028` (#86), Zweig `claude/rls-domain-erp-20261028`.
  Alembic `rls_nutrient_compositions_20261028 → rls_domain_erp_20261028`, ein Head.
  Live kein Abbruchgrund: alle sieben Tabellen 0 Zeilen, keine doppelten Nummern; die Migration legt
  `UNIQUE (id, tenant_id)` auf `domain_crm.customers` an (Sperre ACCESS EXCLUSIVE fuer die Dauer des Index).
- **Live-relevant:** `POST /debtors` und `/export/list` weisen einen fremden `tenant_id` im Rumpf mit 403 ab (in der
  Produktion fing das schon die zentrale Bindung ab; mandantenuebergreifend waren die Wege nach ID ohne Filter);
  Debitor anlegen, OP-Saldo und CSV-Export funktionieren erstmals (vorher immer 500); der Kreditoren-Export liefert
  den Kreditoren-Stamm statt einer leeren Datei.
- **FiBu-Connector:** Pruefen/Buchen/Abbrechen/Stornieren liefen nie (Bindungsfehler). Buchen ist jetzt alles oder
  nichts (Konto, Soll = Haben, Periode, Belegnummer); ein wiederholter Upload mit gleichem Schluessel liest nicht neu ein.
- Nicht beruehrt: `offene_posten`, `chart_of_accounts`, `policy_rules` (Teil 2), Studio/Masken, Live.
