# Kontosperre: an jedem Buchungsweg ein Satz – und eine Bestandskorrektur, die nie speicherte

Stand: 2026-10-12 · Slice `KONTO-SPERRE-MELDUNG-20261012` · offener Punkt aus
[Kontosperre](konto-sperre-20261012.md)

## Befund 1: Die Sperre las sich nur an einem Weg als Satz

Die Sperre setzt die Datenbank durch (Trigger an `journal_entry_lines`, Kennung `konto_sperre`).
Zwölf Stellen schreiben Buchungszeilen mit rohem SQL. Nur die manuelle Buchung fragte vorher nach
und antwortete mit 409 und einem Satz. Die anderen:

| Weg | bisher |
|---|---|
| Buchungsvorlage anwenden, CSV-Einspielung, OP-Ausgleich | 500 mit rohem Datenbankfehler |
| Tagesabschluss Kasse, Lagergeld, FiBu-Konnektor (buchen, stornieren) | 500 ohne Text |
| Bestandskorrektur, Inventur | Fehler verschluckt, Antwort „gebucht" |

## Befund 2: Die Bestandskorrektur speicherte nie

Beim Prüfen des letzten Falls zeigte sich ein älterer Fehler, der mit der Sperre nichts zu tun hat:
`POST …/bestandskorrektur` antwortete 201 mit Korrektur- und Bewegungsnummer, in der Datenbank stand
danach nichts. Die Vorabfrage der Kontenzuordnung griff auf `articles.article_group` zu; die Spalte
gibt es nicht (weder im Prüfstand noch in der gewachsenen Datenbank). Der Fehler wurde mit `pass`
verschluckt, die Transaktion war danach abgebrochen, das abschließende `commit` verwarf Bewegung,
Bestandsänderung und Buchung. Gemessen: 0 Bewegungen mit `KORR-…` und 0 Buchungen der Art
`stock_correction` in beiden Datenbanken.

## Lieferung

- `app/core/exceptions.py`: `kontosperre_meldung(exc)` erkennt die Sperre an der Kennung des
  Triggers (nicht am Wortlaut). Ein zentraler Behandler übersetzt sie in 409 `KONTO_GESPERRT`; jeder
  andere Integritätsfehler bleibt, was er war.
- Buchungsvorlage, CSV-Einspielung, OP-Ausgleich: 409 mit dem Satz statt 500.
- Bestandskorrektur, Inventur: 409 statt „gebucht". Bestand und Buchung teilen eine Transaktion;
  lehnt die Sperre die Buchung ab, ist auch die Bestandsänderung verworfen – das wird jetzt gesagt.
- Bestandskorrektur: Die Kontenzuordnung fragt `articles.warengruppe` ab und läuft in einem
  Sicherungspunkt. Die Korrektur wird gespeichert.

Auslegung (einfachste tragfähige): `lager_kontenzuordnung.artikelgruppe` wird mit
`articles.warengruppe` verglichen. Die Tabelle ist in beiden Datenbanken leer, eine andere
Zuordnung ist nirgends in Gebrauch.

## Nachweis

`tests/test_kontosperre_meldung.py`, gegen `valeo_probe` und den echten Trigger: 8 bestanden.

- Sperre wird an der Kennung erkannt; Fremdschlüsselfehler und gleichlautender `ValueError` nicht.
- Weg ohne eigene Fehlerbehandlung: 409 `KONTO_GESPERRT`; anderer Integritätsfehler: weiter 500.
- Bestandskorrektur auf gesperrtes Konto: 409, keine Bewegung. Gegenprobe mit dem alten Stand der
  Datei: 201 „gebucht", keine Bewegung.
- Bestandskorrektur auf offenes Konto: 201, eine Bewegung, zwei Buchungszeilen.
- Kontenzuordnung der Warengruppe wird gefunden.
- Ratsche: Kein `try` um ein `INSERT INTO … journal_entry_lines` fängt breit ab, ohne die Sperre zu
  erkennen.

`scripts/check_dead_transactions.py`: keine neue tote Transaktion. Ruff: keine neue Meldung.

## Nicht geprüft

- Buchungsvorlage, CSV-Einspielung, OP-Ausgleich, Inventur, Tagesabschluss, Lagergeld und
  FiBu-Konnektor sind nicht je mit einem gesperrten Konto durchgespielt. Für sie gelten die Ratsche
  und der Test des zentralen Behandlers.
- Die Masken dazu im Browser.
- 30 Fälle in `test_booking_templates_api`, `test_finance_booking_templates_api`,
  `test_inventory_counts`, `test_inventory_operations`, `test_open_items` sind rot (alle 401): Sie
  rufen die Hauptanwendung ohne Anmeldung. Das ist die Anmeldegrenze vom 12.10., nicht dieser Slice.

## Offen

- **Inventur buchen** hat dasselbe Muster wie die Bestandskorrektur vorher: Scheitert die Buchung aus
  einem anderen Grund als der Sperre, wird der Fehler protokolliert, die Transaktion ist tot, und der
  Weg meldet Erfolg. Nicht behoben.
- **Gutschrift buchen** (`sales_credit_notes.py`) schreibt Kontonummern (`1400`, `8400`) in
  `account_id`, wo eine Konto-ID erwartet wird. Das scheitert am Fremdschlüssel und wird verschluckt:
  Die Gutschrift hat einen Buchungskopf ohne Zeilen. Von der Ratsche ausdrücklich ausgenommen.
- Bestandskorrektur setzt `previous_stock` und `new_stock` der Bewegung auf 0.
