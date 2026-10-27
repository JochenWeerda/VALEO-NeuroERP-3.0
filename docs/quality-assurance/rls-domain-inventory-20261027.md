---
title: QA RLS-DOMAIN-INVENTORY-20261027
type: qa
audience: [agent, entwickler]
owner: Claude Code
status: abgeschlossen
last_reviewed: 2026-10-27
version: 1.0.0
description: RLS-Domain inventory (Artikel, Lager, Bestaende, Bewegungen, Inventuren, Ruestlisten, NVE) ohne Silo-/Materialfluss-, Agrar- und Dienst-Tabellen auf valeo_probe abgenommen.
---

# QA RLS-DOMAIN-INVENTORY-20261027

**Basis:** `claude/rls-domain-crm-20261027` (#76, getestet 889a0fa13).
Migration `rls_domain_inventory_20261027` folgt auf `rls_domain_crm_20261027`. `alembic heads` zeigt
einen einzigen Head.

**Status:** abgeschlossen. Prüfstandsfenster nach Freigabe durch Codex (RLS-GESAMTABNAHME-20261027).
`valeo_probe` stand vorher und nachher auf `loading_stop_fk_20261023`, 0 fremde Sitzungen. Die gewachsene
Datenbank wurde nur lesend geprüft.

**Nicht enthalten:**

- Silo- und Materialflusstabellen (`silos`, `silo_cells`, `silo_lots`, `silo_lot_movements`, `silo_systems`,
  `material_flow_nodes`, `material_flow_edges`): Der Codex-Claim MATERIAL-FLOW-SQL zu Transfer- und
  Lot-Link-SQL ist offen. Ihre Verweise auf Lager, Zonen und Plätze bleiben einfache Schlüssel.
- `agrar_contracts` und `weighing_tickets`: Sie gehören zur Domain agrar und hängen an Codex' Allokationen.
- `public.inventory_*`: Tabellen des Inventory-Dienstes, erst nach der Token-Prüfung im Dienst (Option A).

## Analyse inventory

| Tabelle | Befund | Entscheidung |
|---|---|---|
| `articles` (B, live 131 Zeilen, 2 Mandanten) | Schreiber tokengebunden; „Dienst“ war ein Fehltreffer (Worker `compliance_monitor` läuft über `cross_tenant_scope`) | NOT NULL, getrennt; Zentrum der Verbund-FKs |
| `warehouses` (B, live 4) | „Dienst“-Fehltreffer: `services/inventory` schreibt `public.inventory_warehouses`, nicht diese Tabelle | NOT NULL, getrennt |
| `warehouse_zones`, `warehouse_bins`, `bin_stock` (A) | Standardmandant nur in `pos_retoure.py` | getrennt; Zone → Lager, Platz → Lager/Zone/Gang, Bestand → Platz |
| `article_batches`, `article_selections` (A) | **Fachbefund:** `article_extensions.py` nahm `?tenant_id=`, ohne ihn den Standardmandanten; Löschen ohne Mandantenfilter | Token; Verbund-FK zum Artikel/Lager |
| `article_documents` (A, `text`) | Schreiber tokengebunden | getrennt; Verbund-FK zum Artikel |
| `article_suppliers` (C) | **Fachbefund:** `articles.py` filterte nach `ArticleSupplier.tenant_id`, Modell und Tabelle hatten keinen Mandanten; das Lieferantenregister endete immer mit 500 | `tenant_id` vom Artikel, Verbund-FK zum Artikel und zum Geschäftspartner; Register filtert über den mandantengeprüften Artikel |
| `inventory_stock_movements` (A, live 128) | Standardmandant in `pos_retoure.py` (Mandant aus dem Rumpf) | getrennt; Verbund-FK Artikel/Platz/Lager |
| `inventory_counts`(+`_lines`), `inventory_lots`, `inventory_lot_movements` | `mcp_execution_service.py:3155` war ein Fehltreffer (generischer MCP-Leser) | getrennt; Zählposition → Zählung/Artikel/Lager |
| `preparation_lists`(+`_lines`) (A) | **Fachbefund:** Liste über `?tenant_id=` mit Standardmandant; Abruf, Ändern, Verarbeiten, Löschen und Positionen ohne Mandantenfilter | Token, eigener Mandant je Weg; Verbund-FK Position → Liste/Artikel |
| `shipping_units` (A, live 37) | **Fachbefund:** `nve.py` mit `?tenant_id=` und Standardmandant | Token; getrennt |
| `epcis_events`, `nawaro_print_notifications` | `mask_frontend_bridges.py:972` war ein Fehltreffer (Antwortfeld „default“) | getrennt |
| `stock_item`, `stock_movement`, `stock_movements`, `stock_locations` (nur frisch) | ohne Schreiber; `stock_locations` ohne Mandant | NOT NULL, getrennt; Ort erbt den Mandanten vom Lager |
| `drying_rule_factor_ranges`, `drying_rule_lookup_rows` (C) | Mandant nur am Regelsatz (P5) | `tenant_id` vom Regelsatz, Verbund-FK |
| `harvest_acceptance_lines`, `_positions` (C, live 1 und 8) | Mandant nur an der Annahme (P5) | `tenant_id` von der Annahme, Verbund-FK (CASCADE wie bisher) |

**Verbund-FKs aus P5-Tabellen (nur Schlüssel, deren Policies unverändert):** Preisschwellen, Tagespreise,
Preisregeln, Wiegescheinpositionen, Umlagerungen und deren Positionen, Bestandskorrekturen und deren
Positionen, Pickpositionen (Artikel, Platz), LKW-Warteschlange, NaWaRo-Rapsprofile, Lagerplätze,
Lagergänge, Chargenverknüpfungen sowie `harvest_acceptances` (Artikel, Lager, Lagerbewegung,
Spediteur, Zwischenhändler). Die beiden Partnerverweise der Ernteannahme schließen den CRM-Folgebefund.
Dazu kommt `domain_sales.delivery_note_positions.artikel_id`, der Sales-Folgebefund.

ON DELETE bleibt wie bisher. Bei SET NULL leert der Verbund-FK nur die Verweisspalte
(`ON DELETE SET NULL (article_id)`, PG15) und nie den Mandanten.

**Gewachsene DB (lesend):** keine Zeile ohne Mandant oder mit Platzhalter, kein Verweis auf einen
Eltern eines anderen Mandanten, keine Kinder ohne Eltern. Die Migration würde dort nicht abbrechen.

## Fachkorrekturen

- **`article_extensions.py`** (`/articles/batches`, `/articles/selections`): Der Mandant kommt aus dem Token
  statt aus `?tenant_id=` mit dem Standardmandanten als Rückfall. Das Löschen einer Selektion prüft den
  Mandanten; eine fremde Selektion ergibt 404.
- **`preparation_lists.py`** (`/preparation-lists`): Liste, Abruf, Positionen, Ändern, Verarbeiten, Bemerkung
  und Löschen arbeiten nur auf Rüstlisten des Token-Mandanten. Bisher galt `?tenant_id=` mit
  Standardmandant, und die Einzelwege hatten gar keinen Mandantenfilter. Eine fremde Rüstliste ergibt 404.
- **`nve.py`** (`/nve`): Mandant aus dem Token statt aus `?tenant_id=` mit Standardmandant.
- **`pos_retoure.py`** (`POST /pos/retoure`): Der Mandant kommt aus dem Token. Bisher stand er im Rumpf,
  ohne ihn galt der Standardmandant; ein Kassierer konnte damit in einem fremden Mandanten Bestand buchen.
  Die Retoure meldete außerdem „erfolgreich gebucht“, auch wenn die Buchung scheiterte (Fail-soft)
  oder der Artikel unbekannt war (0 Zeilen). Jetzt antwortet der Weg mit 422 bei unbekanntem Artikel und
  mit 500, wenn die Buchung scheitert.
- **`compliance.py`** (`/compliance/bvl-umsaetze`, `/compliance/ustva`): Mandant aus dem Token statt aus
  `?tenant_id=` mit `"default"`. Die BVL-Abfrage nannte die nicht vorhandene Spalte `articles.article_group`,
  schluckte den Fehler und lieferte immer eine leere PSM-Meldung. Jetzt nutzt sie das Stammdatenkennzeichen
  `articles.pflanzenschutzmittel`. Ein Fehler endet mit 500 statt mit einer leeren Meldung.
- **`articles.py`** (`/articles/{id}/suppliers`): Das Register filterte nach `ArticleSupplier.tenant_id`, das Modell
  kennt die Spalte nicht, jeder Abruf endete mit 500. Jetzt filtert es über den bereits mandantengeprüften Artikel;
  die Lieferanten hängen per `(article_id, tenant_id)` daran. Das Modell bleibt ohne `tenant_id`, damit der Code
  auch vor der Migration läuft (eine Modellspalte ließ den Bestellvorschlag auf nicht migrierter DB scheitern).
- Eingefrorene Rückfälle auf `"default"`: −2 (`compliance.py` aus der Baseline).

## Nachweise

```
pytest tests/test_rls_domain_inventory.py -rs  -> 100 passed, 0 skipped (valeo_app, zurueckgerollt)
Gegenprobe mit alten Einzel-FKs                -> 55 rot
Gegenprobe mit alten Endpunkten                -> 10 rot (alle Fach- und Tokenvertraege)
Gegenprobe Lieferantenregister mit altem Code  -> rot (AttributeError ArticleSupplier.tenant_id)
RLS-Gesamtsuite + Fallback-Vertrag             -> 431 passed, 0 skipped
122 Lager-/Artikel-/Einkaufs-/Compliance-Bestandsmodule (conftest, Pruefstand)
                                               -> 2501 passed; 6 rot wie auf der Basis #76 (0 neu rot)
Inventar/Rollout/Matrix/Systemlesen regeneriert, generate_code_inventories.py --check -> OK
```

| Abnahmekriterium | Test |
|---|---|
| Mandantengrenze je Tabelle (eigen ok; fremd und `system` SELECT/INSERT/UPDATE/DELETE gesperrt; kein `tenant_id`-Wechsel; fail-closed) | `test_mandantengrenze_je_tabelle` (27) |
| kein Verweis auf fremden Eltern, auch nicht umgehängt (auch aus P5-Tabellen) | `test_kein_verweis_auf_fremden_eltern` (56) |
| SET NULL leert nur den Verweis, nicht den Mandanten | `test_loeschen_leert_nur_den_verweis` (4) |
| Kind erbt den Mandanten aus dem Kontext | `test_kind_erbt_den_mandanten_vom_kontext` |
| Eltern mit Verweisen behalten ihren Mandanten | `test_eltern_mit_verweisen_behaelt_seinen_mandanten` |
| Kontextwechsel/Savepoint, Hintergrund, Pool | `test_kontextwechsel_savepoint_hintergrund_pool` |
| Fachkette Rüstlisten, NVE, Selektionen, Chargen nur eigen, fremd 404 | `test_fachkette_ruestlisten_nve_selektionen_nur_eigener_mandant` |
| Lieferantenregister funktioniert, fremder Artikel 404 | `test_fachkette_artikellieferanten_nur_eigener_mandant` |
| Retoure bucht im eigenen Mandanten, fremder Artikel 422 | `test_fachkette_pos_retoure_bucht_nur_im_eigenen_mandanten` |
| BVL-Umsätze nur eigener Mandant | `test_fachkette_bvl_umsaetze_nur_eigener_mandant` |
| `?tenant_id=` bzw. Rumpf ersetzen das Token nicht | `test_lagerwege_nehmen_den_mandanten_aus_dem_token` (5), `test_pos_retoure_ignoriert_den_mandanten_im_rumpf` |
| Retoure meldet keinen Schein-Erfolg | `test_pos_retoure_meldet_keinen_schein_erfolg` |
| Policy-Formen | `test_policy_formen` |

Die 6 vorbestehenden Fehlschläge (`test_meridian_beleg_systemweit` 4, `test_quality_protocol_pg_concurrency` 1,
`test_stammdaten_bearbeiten` 1) sind mit und ohne diesen Slice gleich rot. Die 22 übersprungenen Bestandstests
überspringen auch auf der Basis und zählen nicht als Abnahme.

Inventar: 127 zurückgestellt (−27).

**Testhilfe** (`tests/rls_domain_support.py`): `assert_tenant_isolation(values=...)` nimmt feste Spaltenwerte
an, zum Beispiel eine registrierte Belegart (Trigger `pruefe_belegart`). Zufällige eindeutige Ganzzahlen
passen jetzt in den Typ (`numeric(5,2)`).

## Verbleibend / vor Live-Aktivierung

- **Silo/Materialfluss** (7 Tabellen): eigener Slice nach Abschluss von MATERIAL-FLOW-SQL (Codex), danach
  auch die Verbund-FKs von `silo_cells`/`silo_systems`/`material_flow_*` auf Lager, Zonen, Plätze, Gänge.
- **`agrar_contracts`, `weighing_tickets`**: mit der Domain agrar, abgestimmt mit Codex.
- **`inventory_lots`, `inventory_lot_movements`, `epcis_events`** verweisen über `article_id`/`warehouse_id`/`lot_id`
  ohne Fremdschlüssel. Ein neuer FK wäre eine Fachentscheidung (welche Lose, welche Herkunft); nicht in diesem Slice.
- **Stammdaten:** live tragen 8 Artikel der Kategorie „Pflanzenschutz“ das Kennzeichen
  `pflanzenschutzmittel` nicht. Die BVL-Meldung zählt sie erst nach der Pflege.
- **`/compliance/ustva`** meldet „EINGEREICHT“, sobald keine Buchung im Entwurf steht, ohne dass etwas
  übermittelt wurde. Das ist ein eigener Fachbefund für die Domain finance/compliance.
- **`POST /pos/checkout`** meldet „completed“, ohne etwas zu buchen. Das ist ein eigener POS-Befund.
- **`app/seeds/inventory_seed.py`** legt bewusst den Entwicklungsmandanten an (CI und `bootstrap_db.py`).
  Das ist kein Rückfall eines Anfragewegs und bleibt.
- **Masken:** Artikel, Lager, Rüstlisten, NVE, Retoure und PSM-Nachweis mit zwei Mandanten prüfen.
  Die Maskenabnahme liegt bei Codex.
