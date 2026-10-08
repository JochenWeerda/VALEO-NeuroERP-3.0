# Restbefunde aus dem Bestandsbuch-Slice geschlossen (Slice RESTBEFUNDE-BESTANDSBUCH-20261008)

Stand: 2026-10-08 · Folgeslice zu [Bestandsbuch und Einkauf](bestandsbuch-einkauf-20261007.md)

## Auftrag

Die vier dort benannten Restbefunde schließen.

## Befunde und Behebung

| # | Befund | Behebung |
|---|---|---|
| 1 | **Mahnwesen:** sechs Wege in `dunning.py` lasen den Mandanten aus `Query("system")`. Mahnlauf und Mahnverarbeitung nahmen ihn aus dem Request-Rumpf, mit `"system"` als Vorgabe. | Der Mandant kommt aus dem Kontext. Die Rumpffelder sind entfernt, Query und Rumpf wählen keinen Mandanten mehr. |
| 2 | **Rechnungsanlage:** Der Dokumentspeicher committete die Rechnung vor der Buchung. Scheiterte die Buchung oder der Archiveintrag, stand die Rechnung ohne Buchung und ohne offenen Posten da. | Beleg, Buchung, offener Posten, Archiv und Lieferscheinbezug laufen in einem Commit. `SalesPostingService(commit=False)` flusht nur, `save_document(commit=False)`. Jeder Fehlerzweig rollt zurück. Ändern und Buchen eines Entwurfs folgt demselben Muster. |
| 3 | **Artikelnummern:** `article_number` war seit `001_initial_schema` systemweit eindeutig, ein zweiter Mandant konnte eine vergebene Nummer nie anlegen. Der gewachsenen Dev-DB fehlte die Eindeutigkeit ganz. | Migration `artikelnummer_mandant_20261008`: `UNIQUE NULLS NOT DISTINCT (tenant_id, article_number)`. Bei Dubletten je Mandant bricht sie ab, statt Daten umzuschreiben. Sie ist auf Prüfstand und Dev-DB angewandt. |
| 3a | **Lesestellen ohne Mandant:** Der Inventar-Seed suchte Artikel nur über die Nummer und **hängte sie dem seedenden Mandanten um**. Die Ist-Aggregation und der WhatsApp-Abgleich lasen Artikel aller Mandanten. Die Artikel-Auflöser in `compat`/`annahme` hatten bei eigenem und mandantenlosem Artikel gleicher Nummer keine Vorrangregel. | Alle Lesestellen sind auf den Mandanten begrenzt. Bei gleicher Nummer gewinnt der eigene Artikel. Alle übrigen Lookups (Artikelanlage, Barcode, POS-Retoure, Lieferschein, Preisfindung, Bestellvorschlag) filterten bereits nach Mandant; das wurde einzeln geprüft. |
| 4 | **`_list_docs`:** Lieferte die Datenbank für einen Mandanten nichts, fiel die Funktion auf den Prozessspeicher zurück. Der war flüchtig und mit Daten aus beliebigen Requests gefüllt. | Sie liest nur noch aus dem Datenbank-Dokumentspeicher, leer heißt leer. `compat.py` hat 3474 Zeilen, die Godfile-Baseline ist gesenkt. |

## Nachweis

Neue Verträge laufen gegen `valeo_probe`, Archiv- und Artikeldaten in einer äußeren Transaktion:

- `tests/test_rechnung_ein_commit.py` (4 Tests): Scheitert die Buchung oder das Archiv, bleibt keine Rechnung zurück. Die Buchung committet nicht selbst, ein Entwurf wird gespeichert.
- `tests/test_artikelnummer_mandant_dokumentspeicher.py` (5 Tests): gleiche Nummer in zwei Mandanten, eindeutig im Mandanten, der eigene Artikel wird gefunden, der Seed hängt nichts um, kein Rückfall in den Prozessspeicher.
- `tests/test_dunning_api.py::TestMandantAusDemKontext` (3 Tests).
- `tests/test_lieferschein_einbuchen_abgleich.py` nutzt jetzt dieselbe Nummer in beiden Mandanten.

Angepasst habe ich Tests, die das Alte festschrieben: der Mandant im Rumpf beim Mahnwesen und der Posting-Dienst mit eigenem Commit.

Regression über alle 68 Testdateien, die die geänderten Stellen berühren, plus die neuen: 1090 grün, 0 rot. Doc-Generatoren, Tabellenkatalog, Single Head und die Improvement-Pipelines sind im HEAD-Worktree grün. Live auf dem gewachsenen Bestand antworten Mahnregeln, Mahnungen, Bestellliste, Bestellstatistik und Artikel mit 200.

## Weitere Befunde (benannt, nicht Teil)

- `test_dunning_api::test_fallback_default_rules_on_db_error` schreibt fest, dass `GET /dunning/rules` bei einem Datenbankfehler **erfundene Standardregeln** liefert.
- Der Inventar-Seed sucht Lager weiterhin nur über `warehouse_code` und setzt `tenant_id` um. Das ist dasselbe Muster wie bei den Artikeln, für Lager aber nicht geprüft.
- `journal_entries.entry_number` ist weiterhin systemweit eindeutig (Finanz-Owner).
