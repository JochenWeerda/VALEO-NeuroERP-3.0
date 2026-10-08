# Folgefunde aus den Restbefunden behoben (Slice FOLGEFUNDE-RESTBEFUNDE-20261008)

Stand: 2026-10-08 · Folgeslice zu [Restbefunde Bestandsbuch](restbefunde-bestandsbuch-20261008.md)

## Auftrag

„Gefundenes gleich mit beheben“: die drei dort benannten Folgefunde und was dabei auftauchte.

## Befunde und Behebung

| # | Befund | Behebung |
|---|---|---|
| 1 | `GET /dunning/rules` lieferte bei **jedem** Datenbankfehler drei erfundene Mahnstufen (5/10/15 EUR Gebühr, Ids "1"–"3"). Der Mahnlauf nutzt diese Funktion. Er hätte damit echte Mahnungen mit Gebühren erzeugt, die kein Mandant festgelegt hat. Ein Test schrieb das fest. | Bei einem Datenbankfehler gibt es Rollback und 503. Der Mahnlauf bricht ab, ohne zu committen. |
| 1a | `GET /dunning` meldete bei einem Datenbankfehler eine leere Liste („keine Mahnungen“). | Ebenfalls 503. |
| 2 | Der Inventar-Seed suchte Lager über `warehouse_code` allein und **hängte sie dem seedenden Mandanten um**. Feste Seed-IDs (`seed-warehouse-…`, Artikel-ID) ließen den zweiten Mandanten auf den Primärschlüssel laufen. | Suche und Update laufen im Mandanten. Ist die feste ID belegt, wird je Mandant eine ID abgeleitet (`uuid5`). Das gilt für Lager und Artikel. |
| 2a | `warehouse_code` war systemweit eindeutig (`warehouses_warehouse_code_key`). | Migration `lagercode_mandant_20261008`: `UNIQUE NULLS NOT DISTINCT (tenant_id, warehouse_code)`, Abbruch bei Dubletten. Angewandt auf Prüfstand und Dev-DB. |
| 2b | Zweiter Lager-Router `/api/v1/warehouses`: Lesen, Ändern und Stilllegen liefen über die ID allein. Das Anlegen nahm den Mandanten aus dem Payload, die Liste und der Superglue-Rollout aus dem Query. Es gab keine Rollenprüfung. | Der Mandant kommt aus dem Kontext. Schreiben braucht die Lager-Adminrolle, wie bei `/inventory/warehouses`. |
| 2c | `POST /api/v1/inventory/warehouses` scheiterte **immer**: `tenant_id` wurde doppelt an das Modell übergeben (Payload-Pflichtfeld plus Kontext). | `WarehouseCreate.tenant_id` ist jetzt optional und wird ignoriert; das Modell bekommt nur den Kontextmandanten. |
| 3 | `journal_entries.entry_number` systemweit eindeutig. | **War bereits behoben:** Codex hat das am 05.10.2026 mit `journal_number_tenant_20261005` / `uq_journal_tenant_number` erledigt, auf Prüfstand und Dev-DB vorhanden. Meine Notiz war veraltet. |

## Nachweis

- `tests/test_lager_mandant_seed.py` (8 Tests): Lagercode je Mandant, der Seed hängt nichts um, eine belegte Seed-ID führt nicht auf den Primärschlüssel, ein fremdes Lager ist unsichtbar und unveränderlich, die Liste wählt den Mandanten nicht per Query, beide Router legen im Header-Mandanten an.
- `tests/test_dunning_api.py`: Ein Datenbankfehler erfindet keine Regeln, der Mahnlauf mahnt nicht damit, und ein Datenbankfehler erscheint nicht als leere Liste.
- Angepasst: `tests/test_warehouses_api.py`, die bisher Mandant aus Query bzw. Payload festschrieben.

Regression über 30 Testdateien zu Lager, Seed und Mahnwesen plus die Verträge der Vorslices: 603 grün. Der einzige rote Test, `uat/test_uat_api_contracts::test_gelangensbestaetigung_valid_create`, scheitert an einem Datenrest im Prüfstand (feste `LS-UAT-001` aus einem früheren Lauf) und hat mit diesem Slice nichts zu tun. Doc-Generatoren, Tabellenkatalog, Single Head und Improvement-Pipelines sind im HEAD-Worktree grün. Live antworten beide Lagerlisten und das Mahnwesen mit 200.

## Weitere Befunde (benannt, nicht Teil)

- Der UAT-Vertrag zur Gelangensbestätigung verwendet eine feste Lieferschein-Nr. und ist deshalb nicht wiederholbar.
