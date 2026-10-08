# Bestandsbuch und Einkauf: Mandant, Richtung, Storno, Archiv, Lieferschein (Slice BESTANDSBUCH-EINKAUF-20261007)

Stand: 2026-10-07 · Folgeslice zu [Mandant Finanz/CRM/Einkauf](mandant-finanz-crm-einkauf-20261007.md)

## Auftrag

„Alle 5 Befunde beheben“: die fünf benannten Befunde aus dem Vorslice. Dabei sind
weitere Fehler gleicher Art aufgetaucht; sie sind mit behoben und unten eigens
ausgewiesen.

## Befunde und Behebung

| # | Befund | Behebung |
|---|---|---|
| 1 | **Mandant in der Inventar-API.** Alle Wege unter `/inventory/*` (Bewegungen, Berichte, Chargen-Lineage, Lagergeld, Lager) nahmen `tenant_id` aus dem Query und überschrieben damit den Kontext. `get_current_tenant_id` lieferte beim Dev-Token immer den Standardmandanten und ignorierte den Header. Lager anlegen, ändern und stilllegen lief ohne jede Berechtigungsprüfung. | Der Mandant kommt aus dem Header, den die Middleware prüft. Ein JWT-Mandant muss dazu passen (403). Lager schreiben braucht die Lager-Adminrolle. |
| 1a | Dieselbe Lücke unter `/lager/*` (`inventory_operations`): sieben Wege über Query, vier über einen **Query**-Parameter `x_tenant_id`, der wie ein Header aussah. Dazu der Barcode-Scan (`/scan/barcode`), der fremde Artikel samt Bestand fand. | Mandant aus dem Kontext. |
| 2 | **Vorzeichen.** `InventoryService` verlangte für `out` eine negative Menge und schrieb sie so. Die Richtungstabelle rechnet `out` aber als `-quantity`, also hätte jeder Abgang den Bestand **erhöht**. Die Erfassungsmaske schickt positive Mengen und bekam immer „Invalid movement type“. `transfer` kennt keine Richtungstabelle (in jeder Auswertung 0). Artikel und Lager wurden nicht auf den Mandanten geprüft. | `in`/`out` mit positiver Menge (eine negative `out`-Eingabe wird als Betrag gelesen), `adjustment` mit Vorzeichen, `transfer` wird als `umbuchung` gebucht. Vorher-/Nachher-Bestand aus dem Bestandsbuch je Lager, der Artikelbestand läuft um dieselbe Menge mit, kein negativer Lagerbestand. Die Artikelsumme liest die Richtung aus der Tabelle statt aus dem Vorzeichen. |
| 2a | Derselbe Fehler im WMS-Dienst `book_stock_movement`: `pick_out` mit `-5` zählte als Zugang, `transfer_in`/`transfer_out` kennt keine Tabelle, der Artikelbestand lief nicht mit, Lagerplatz und Artikel ohne Mandant. | Bestandsbuch richtungskonform (`umbuchung_ausgang`/`_eingang`). Ein Vorzeichen gegen die Buchungsart wird abgelehnt. Lagerplatz und Artikel im Mandanten, der Artikelbestand läuft mit, `commit=False` für Mehrpositionsbuchungen. |
| 2b | **Lesemodell.** `StockMovement` erbte die Schreibmuster: Eine einzige Altzeile (`wareneingang`, `ownership_type = 'eigen'`) ließ die ganze Bewegungsliste mit 500 scheitern. In der Dev-DB war die Liste **dauerhaft** 500. | Das Lesemodell zeigt, was gebucht ist. Die Muster gelten nur fürs Anlegen. Live: 200, 127 Bewegungen. |
| 3 | **DELETE ohne Bestandskorrektur.** `DELETE /inventory/stock-movements/{id}` löschte die Buchung spurlos (GoBD). Der Storno korrigierte das Bestandsbuch, nicht aber den Artikelbestand. | `DELETE` antwortet mit 409 und nennt den Stornoweg. Der Storno führt den Artikelbestand mit. Die Lagerbewegungsliste (`lagerbewegungen.tsx`) führt statt „Löschen“ in die Detailmaske aus der ScreenDefinition `lager/stock-movement` (Mask Builder, Stornoaktion mit Begründung). |
| 4a | **`register_artifact`** committete selbst und schrieb so die halbe Arbeit des Aufrufers fest. Bei einem Fehler rollte es **dessen** Transaktion zurück, gab `None` zurück und protokollierte nur eine Warnung. Es trug die Belegnummer als `header_id` ein, und der Fremdschlüssel auf `document_headers` ließ **jeden** Eintrag scheitern: Archiviert wurde von Rechnung, Mahnung, FiBu-Übergabe und E-Rechnung nie etwas. | Läuft in der Transaktion des Aufrufers und scheitert laut (`GobdArtifactError`). Der Belegkopf wird angelegt oder gefunden (Muster aus `settlement_document_archive_service`). Der Inhalt liegt in PostgreSQL, geschützt durch `guard_archived_content`, und der Hash wird geprüft. Versionen je Beleg. |
| 4b | Aufrufer: Mahnung „versandt“ committet vor dem Archiv; Rechnung: Lieferscheinbezug nach dem letzten Commit, nie festgeschrieben, Fehler ließ tote Transaktion; E-Rechnung „best-effort“; FiBu-Übergabe exportierte bei DB-Fehler **leer** und archivierte das. | Archiv vor dem Commit; Savepoint + Commit für den Lieferscheinbezug; E-Rechnung ohne Archiveintrag → 503; DB-Fehler beim Export → 503. Dateinamen sagen, was archiviert ist (`…_buchungsdaten.txt`, nicht `.pdf`). |
| 4c | **Bestell-Altbelege** ließen sich weiter ändern, freigeben (`approvedBy = "system"`) und stornieren. Die Statistik zählte nur Altbelege und stand hinter `/{po_id}`, war also **nie erreichbar** (404). Ein toter Anlegeweg lag noch im Code. | Altbelege bleiben lesbar und sind schreibgeschützt (409). Die Statistik läuft über beide Quellen und steht vor `/{po_id}`. Der tote Code ist entfernt (`compat.py` 3589 → 3477 Zeilen, Baseline gesenkt). |
| 5 | **Lieferschein.** Alle 15 Wege mit `Query("system")`. Beim Einbuchen bekam jede Position ihren eigenen Commit (teilgebucht + „erledigt“), ein zweiter Aufruf buchte alles noch einmal, und Artikel wurden ohne Mandant aufgelöst. Jeder weitere Abgleich zählte die Menge erneut auf die Bestellung, und eine Bestellung stand auf „geliefert“, ohne dass Ware im Lager war. | Mandant aus dem Kontext. Einbuchen geht ganz oder gar nicht, in einem Commit, nur einmal (409); Lager, Lagerplatz und Artikel im Mandanten; jede Hinderung wird benannt. Abgleich einmal (Migration `lieferschein_abgleich_20261007`: `abgleich_bestellung_id`, `abgeglichen_am`), erst nach dem Einbuchen, nicht gegen stornierte Bestellungen, `business_today`. |

## Nachweis

Neue Verträge gegen `valeo_probe`, alle mit dem echten Dev-Token-Weg:

| Datei | Tests |
|---|---|
| `tests/test_bestandsbuch_mandant_richtung.py` | 15 |
| `tests/test_lieferschein_einbuchen_abgleich.py` | 14 |
| `tests/test_gobd_artefakt_bestell_altbeleg.py` | 12 |

Archivtests laufen in einer äußeren Transaktion, weil archivierter Inhalt nicht gelöscht werden kann. Angepasst wurden Tests, die das Alte festschrieben: Query-Mandant (`test_api_gap_lager_pricing_scan`), Teilbuchung (`test_eink_we_001`), Typ `inbound` ohne Richtung (`test_warehouse_wms_fefo`, `test_lager_bwert_001`) und Archiv nach dem Commit (`test_dunning_api`). Dazu kam ein neuer Test „ohne Archiveintrag kein Versand“.

Die Bereichssuiten liefen mit 671 grünen Tests, 0 roten und 6 übersprungenen. Vitest `lagerbewegungen-uix` ist grün. Alle Ratschen sind grün; `check_business_time_usage` und die Godfile-Baseline wurden gesenkt. Die Doc-Generatoren und der Tabellenkatalog wurden in einem HEAD-Worktree erzeugt, damit fremde WIP draußen bleibt.

Am gewachsenen Bestand (Dev-DB, Backend neu gestartet) liefert die Liste 200 statt 500, `DELETE` liefert 409 und ein fremder Query-Mandant liefert 404.

Schon auf HEAD rot sind zwei Gates, die nicht zu diesem Slice gehören: `check_openapi_docs --threshold 0` und `check_response_models --threshold 20`.

## Weitere Befunde (benannt, nicht Teil)

* Artikelnummern sind systemweit eindeutig (`articles_article_number_key`), nicht je Mandant.
* `dunning.py`: sechs Wege mit `Query("system")`.
* Rechnung anlegen: Der Dokumentspeicher committet vor der Buchung. Scheitert die Buchung, steht die Rechnung ohne Buchung da.
* `_list_docs` greift auf einen In-Memory-Speicher zurück, wenn der DB-Speicher leer ist.
* `/purchase-orders/{id}/communications` schreibt in den Dokumentspeicher.
* Bestehende Bestell-Altbelege: einer im gewachsenen Bestand. Ob er als Bestellung neu erfasst werden soll, ist eine fachliche Entscheidung.
