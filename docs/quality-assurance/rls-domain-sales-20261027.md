---
title: QA RLS-DOMAIN-SALES-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: RLS-Domain Sales (Angebote, Aufträge, Lieferscheine, Gutschriften, Positionen, Picklisten) auf valeo_probe abgenommen.
---

# QA RLS-DOMAIN-SALES-20261027

**Basis:** `claude/rls-domain-ki-20261027` (#74, Stand dcd059ddc auf Integrationszweig ed77dded3).
Migration `rls_domain_sales_20261027` folgt auf `rls_domain_ki_20261027`; `alembic heads` zeigt
einen einzigen Head.

**Status:** abgeschlossen. Codex hatte das Prüfstandsfenster freigegeben
(RLS-GESAMTABNAHME-20261027). `valeo_probe` stand vorher und nachher auf
`loading_stop_fk_20261023`, 0 fremde Sitzungen.

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

## Nachweise

```
pytest tests/test_rls_domain_sales.py -rs   -> 17 passed, 0 skipped (valeo_app, zurückgerollt)
Gegenprobe mit alten Einzel-FKs             -> 5 rot
RLS-Gesamtsuite + Größenratsche              -> 303 passed, 0 skipped
77 Sales-/Beleg-/Picklisten-Bestandsmodule (conftest, Prüfstand)
                                             -> 2262 passed; 27 rot wie auf der Basis #74 (0 neu rot)
Inventar/Rollout/Matrix regeneriert, generate_code_inventories.py --check -> OK
```

Die 27 vorbestehenden Fehlschläge liegen in Studio-, Masken- und Architekturverträgen
(`test_kontroll_worklist_parent` 17, `test_meridian_beleg_systemweit` 4, `test_mask_field_contracts` 2,
je 1 in `test_document_control_mask_commands`, `test_generate_architecture_index`,
`test_table_reference_inventory`, `test_uix091_process_chain_contract`). Sie sind mit und ohne
diesen Slice gleich rot.

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze je Tabelle (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein `tenant_id`-Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (8) |
| keine Position unter fremdem Kopf, auch nicht umgehängt | `test_keine_position_unter_fremdem_kopf` (4) |
| Position erbt den Mandanten aus dem Kontext | `test_position_erbt_den_mandanten_vom_kontext` |
| Kopf mit Positionen behält seinen Mandanten | `test_kopf_mit_positionen_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Hintergrund, Pool | `test_kontextwechsel_savepoint_hintergrund_pool` |
| Fachkette Picklisten: Liste nur eigen, fremde Pickliste 404, fremder Auftrag 404, eigener Auftrag → `in_delivery`, fremder Auftrag unberührt | `test_fachkette_pickliste_bucht_nur_eigenen_auftrag` |
| Policy-Formen inkl. `pick_lists` | `test_policy_formen` |

Inventar: 181 zurückgestellt (−9).

## Verbleibend / vor Live-Aktivierung

- **Kundenbezug:** Angebote und Aufträge verweisen per FK auf `domain_crm.customers`
  (Klasse B, zurückgestellt). Ein Verweis auf den Kunden eines fremden Mandanten ist strukturell
  noch möglich; er kommt mit dem Kundenstamm (NOT NULL, Verbund-FK).
- **Belegketten** Angebot → Auftrag → Lieferschein → Rechnung haben keine bzw. einfache FKs
  (z. B. `sales_orders.sales_offer_id`). Das ist ein eigener Folge-Slice.
- **Picklisten-Kinder** (WMS/L3C-Positionen) folgen mit der Domain inventory.
- **Masken:** Angebote, Aufträge, Lieferscheine, Gutschriften, Picklisten mit zwei Mandanten;
  Fachcommands, Freigaben und Buchungsregeln sind unverändert.
