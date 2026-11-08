---
title: inventory-Dienst fuehrt public.inventory_* (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# inventory-Dienst fuehrt public.inventory_* (2026-10-26)

Slice `INVENTORY-OWNERSHIP-20261026`, Zweig `claude/inventory-ownership-20261026`, gestapelt
auf `SERVICES-VERSION-TABLE-20261026` (PR #52). Vorstufe:
[services-version-table-20261026.md](services-version-table-20261026.md).

## Entscheidung

Nutzerentscheidung 2026-10-26: Der inventory-Dienst ist Eigentuemer von `public.inventory_*`,
das Backend liest nur (`app/services/procurement_match_service.py`, Wareneingaenge gegen
Bestellungen). Die Backend-eigenen Chargen in `domain_inventory.inventory_lots` sind nicht
betroffen.

## Ausgangslage

`wms_material_flow_stock_link_20260619` legt vier Kompatibilitaetstabellen
(`inventory_warehouses`, `_locations`, `_goods_receipts`, `_goods_receipt_lines`) mit
`TEXT`-IDs an. Live kam `create_all` des Dienstes zuerst (uuid-Form, die Backend-Migration
war ein No-op); auf frischer Datenbank (valeo_probe) entstand die TEXT-Form, und der Dienst
konnte weder migrieren noch `create_all` ausfuehren. Seed (`scripts/seed_demo_procurement.py`)
und Testfixture schreiben bereits die Dienstform (uuid-Strings, `'POSTED'`).

## Aenderung

- Neue Backend-Migration `inventory_service_shape_20261026`: uuid-Form → nichts; leere
  TEXT-Tabellen → durch die Dienstform ersetzt, Leseindizes des Backends wieder angelegt;
  TEXT-Tabellen mit Zeilen → Abbruch mit Tabellennamen. Downgrade No-op.
- `inventory_0001` (Dienst): je Tabelle eine `_create_*`-Funktion; legt nur fehlende Tabellen
  an, vorhandene mit anderem ID-Typ brechen ab; offline (`--sql`) unveraendert alle acht.
- `tests/test_inventory_service_shape.py`: Backend-Kopien der vier `_create_*`-Funktionen
  muessen AST-gleich zur Dienstbasis sein (Mutationsprobe: geaenderte Laenge faellt auf).

## Pruefung (valeo_probe, eine Transaktion je Fall, ROLLBACK)

Prüfstand ohne fremde Sitzungen; Stand `loading_stop_fk_20261023` (im Zweig enthalten, direkte
Vorgaengerin von `governance_ddl_log_20261026`; der Pruefstand liegt nur hinter dem Kopf, unberuehrt). Modell-DDL der Dienstmodelle im Schema `vt_model`.

| Fall | Ergebnis |
| --- | --- |
| leere TEXT-Tabellen, Backend dann Dienst | Backend ersetzt 4, Dienst legt 4 weitere an; alle 8 gegen Modell: 0 Spalten-, 0 Constraint-, 0 Indexabweichungen; beide Leseindizes vorhanden |
| Backend-Migration zweimal | zweiter Lauf No-op |
| TEXT-Tabelle mit Zeile | Abbruch, nennt `inventory_warehouses` |
| Dienst vor Backend-Fix auf TEXT | Abbruch, verweist auf die Backend-Migration |

Danach valeo_probe unveraendert (TEXT-Form, kein `vt_model`). Offline-SQL der Dienstbasis im
Container: 8 Tabellen plus Versionstabelle. Vertragstests: 16 gruen.

## Live

Keine Aenderung. `valeo_neuro_erp` liegt in uuid-Form vor; die Backend-Migration ist dort ein
No-op und wird mit dem naechsten regulaeren Backend-Upgrade gestempelt. inventory steht
unveraendert auf `inventory_0001 (head)`.

Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Ergebnis |
| --- | --- |
| Docs Build / Docs Governance (PR #53) | success |
| Quality Gate 40385231751 | alle Jobs ausser zweien success; Backend bricht wie auf der Basis am Doc-Drift-Gate ab (272 Befunde, lokal gegengeprueft, identisch); Frontend-Unit wie auf der Basis rot (keine Frontend-Aenderung) |
