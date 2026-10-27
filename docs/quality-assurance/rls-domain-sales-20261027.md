---
title: QA RLS-DOMAIN-SALES-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: in-arbeit
last_reviewed: 2026-10-27
version: 0.1.0
description: RLS-Domain Sales (Angebote, Aufträge, Lieferscheine, Gutschriften, Positionen, Picklisten) vorbereitet; Datenbankabnahme steht aus.
---

# QA RLS-DOMAIN-SALES-20261027

**Basis:** `claude/rls-domain-ki-20261027` (#74). Migration `rls_domain_sales_20261027` folgt auf
`rls_domain_ki_20261027`; `alembic heads` zeigt einen einzigen Head.

**Status:** Code vorbereitet. Datenbankabnahme offen, sie braucht ein neues Prüfstandsfenster
von Codex. Inventar, Rollout und Ausnahmen folgen danach.

## Analyse Sales

| Tabelle | Befund | Entscheidung |
|---|---|---|
| `domain_crm.sales_offers`, `sales_orders` (A) | Wege tokengebunden (`sales_offers.py`, `sales_orders.py`, `sales_order_commands.py`, `collective_documents.py`) | getrennt, kein `system` |
| `domain_crm.sales_order_items` (A) | Positionen; live 14, alle unter eigenem Kopf | Verbund-FK zum Auftrag |
| `domain_crm.sales_offer_items` (P5) | live 1, sauber | Verbund-FK zum Angebot (Policies unverändert) |
| `domain_sales.delivery_notes` (A), `sales_credit_notes` (A) | tokengebunden; Matrix-Fundstellen (`articles.py`, `branches.py`, `finance_invoices.py`, `compat.py`) betreffen Artikel, Filialen und Partner | getrennt, kein `system` |
| `domain_sales.delivery_note_positions`, `sales_credit_note_lines` (C) | Mandant nur am Kopf; live 4 bzw. 0 | `tenant_id` vom Kopf, NOT NULL, Default aus dem Kontext, Verbund-FK; der Artikel-FK bleibt einfach (Artikelstamm B, zurückgestellt) |
| `domain_sales.sales_delivery_notes` (B) | Quittierungen, live 0, Schreiber setzt den Mandanten | NOT NULL, getrennt |
| `domain_inventory.pick_lists` | **Fachbefund:** Liste über `?tenant_id=` mit Standardmandant. Acht Schreibwege griffen per ID auf Picklisten jedes Mandanten zu. „Auftrag buchen“ setzte den Status eines beliebigen Auftrags; der Fehlerpfad schluckte die Ausnahme ohne Rollback | alle Wege tokengebunden, verknüpfter Auftrag muss eigener sein (404), Auftragsupdate mit Mandantenfilter, Rollback im Fehlerpfad; Tabelle unter RLS, weil die Analyse sie danach freigab |

Belegketten zwischen den Köpfen (Angebot → Auftrag → Lieferschein → Rechnung) laufen ohne
Fremdschlüssel. Fremde Köpfe sind unter RLS unsichtbar, eine strukturelle Sperre fehlt. Das
ist ein eigener Folge-Slice.

## Offen bis zum Prüfstandsfenster

- `tests/test_rls_domain_sales.py` (17 Fälle) als `valeo_app` auf `valeo_probe`.
- Gegenprobe, Inventar/Rollout/Matrix regenerieren; `rls-exceptions.json` verkleinern
  (−9: 8 Sales-Tabellen + `pick_lists`), Obergrenze senken.
- Bestandstests Sales/Picklisten gegen die Basis vergleichen.
- Maskenabnahme: Angebote, Aufträge, Lieferscheine, Gutschriften, Picklisten mit zwei Mandanten.
