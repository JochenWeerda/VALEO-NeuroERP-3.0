# FIN-LESEWEGE-MANDANT: Lieferantengutschriften und alter Rechnungsweg nur im eigenen Mandanten

Stand: 2026-10-13 · Slice `FIN-LESEWEGE-MANDANT-20261013`

## Befund

Beim Anschluss an die Kontroll-Engine waren mir Wege aufgefallen, die ohne Mandant arbeiten. Die Prüfung ergab
mehr als gemeldet:

| Weg | Zustand bis 13.10.2026 |
|---|---|
| `GET /einkauf/credit-memos`, `/debit-memos` (Liste und Einzelbeleg) | lieferten die Belege **aller Mandanten**, ohne Rollenprüfung |
| `POST /einkauf/credit-memos/{id}/freigabe`, `/debit-memos/{id}/freigabe` | gaben auch **fremde** Belege zur Buchung frei, ohne Rolle; der Freigebende kam aus dem Kopf `X-User-ID` oder aus einem **ungeprüft dekodierten Token** |
| Ersteller, Freigebender und Buchender der Lieferantengutschrift | aus demselben Kopf — jeder konnte unter fremdem Namen handeln |
| `GET /finance/invoices` (Liste) | lieferte die Ausgangsrechnungen **aller Mandanten** |
| `PUT`, `DELETE /finance/invoices/{nr}` | änderten und löschten auch die Rechnung eines **anderen Mandanten** |
| `POST /finance/invoices` | ersetzte unter einer vergebenen Nummer still die Rechnung eines anderen Mandanten (die Nummer ist im Dokumentspeicher systemweit eindeutig); der Beleg trug **keinen Mandanten** |
| `GET /finance/invoices/{nr}` | antwortete immer mit 500 (falsches Antwortmodell) — deshalb an dieser Stelle kein Abfluss |
| `POST /ap/invoices/{nr}/post?posted_by=…` | der Buchende kam aus der Anfrage |

## Was jetzt gilt

- **Lieferantengutschrift und -belastung:** Lesen nur im Mandanten der Anmeldung und nur mit Preisrecht des
  Einkaufs (eine Gutschrift besteht aus Beträgen; das Lager sieht sie nicht). Freigabe zur Buchung nur im eigenen
  Mandanten und mit Buchungsrecht. Ersteller, Freigebender und Buchender sind die angemeldete Person; die
  Auswertung des ungeprüften Tokens ist entfernt.
- **Alter Rechnungsweg:** Die Rechnung trägt ihren Mandanten. Lesen, Ändern und Löschen treffen nur eigene Belege
  (sonst 404). Eine vergebene Nummer wird nicht überschrieben (409). Der Einzelabruf antwortet.
- **Finanzrechnung buchen:** Es bucht, wer angemeldet ist; der Parameter `posted_by` wird angenommen und nicht
  beachtet (die Oberfläche sendet ihn noch).
- **Altbelege ohne Mandant** werden niemandem ausgeliefert. `scripts/belege_mandant_nachtragen.py` ordnet zu, wo
  genau ein Mandant eine Buchung oder einen offenen Posten zu der Nummer hat (ohne `--apply` nur Anzeige);
  mehrdeutige und ungebuchte Belege bleiben offen und werden ausgewiesen.

## Nachweis

- `tests/test_lesewege_mandant.py` (14, gegen die frische Datenbank): Liste und Einzelabruf je Mandant;
  Leserecht; Altbeleg ohne Mandant; Freigabe nur im eigenen Mandanten und mit dem Namen der Anmeldung trotz
  gesetztem `X-User-ID`; Anlegen und Buchen nennen die Anmeldung; Rechnung trägt den Mandanten; fremde Rechnung
  weder änderbar noch löschbar (Beleg danach unverändert); vergebene Nummer überschreibt nicht; Nachtrag nur bei
  eindeutiger Buchung, zweiter Lauf findet nichts.
- `tests/test_freigabe_zweitwege.py`: Buchender der Finanzrechnung ist die Anmeldung, mit und ohne Parameter.
- 899 Tests der Dateien, die diese Wege berühren, grün (Rollenvertrag der Finanz-REST-Wege, Mandantentests der
  Eingangsrechnung, Prozesskern, OpenAPI-Vertrag der Gutschriften).
- **Gewachsene Datenbank** (`valeo_neuro_erp`, nur gelesen): sechs Ausgangsrechnungen ohne Mandant
  (`INV-Q-…`), keine davon gebucht — nicht zuordenbar, seither nicht mehr sichtbar. Nichts geändert.

## Offen

- **Die Ursache sitzt tiefer:** `DocumentRepository.list_documents` und `count_documents`
  (`app/documents/repository.py`) behandeln einen Mandantenfilter als „dieser Mandant **oder kein Mandant**".
  Jeder Weg, der sich auf diesen Filter verlässt, liefert mandantenlose Belege an alle. Das betrifft Belegarten
  anderer Bereiche (Bestellungen, Angebote, Lieferscheine des alten Dokumentspeichers) und ist hier nicht
  geändert — es braucht eine Bestandsaufnahme je Belegart und die Entscheidung, was mit Altbelegen ohne
  Mandant geschieht.
- Die Rechnungsnummer des alten Wegs bleibt systemweit eindeutig; zwei Mandanten können dieselbe Nummer nicht
  führen (der zweite erhält 409 und erfährt damit, dass es die Nummer gibt).
- `ap_memo_booking` (Buchungsvermerk der Lieferantengutschrift) trägt weiter keinen Mandanten und ist keine
  Hauptbuchbuchung — unverändert, bereits gemeldet.
- Die Oberfläche sendet `posted_by` weiter mit; sie kann den Parameter entfallen lassen.
