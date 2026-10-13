# Belege und Stammdaten: Steuerschlüssel statt Prozentsatz

Stand: 2026-10-13 · Slice `STEUERSCHLUESSEL-BELEGE-20261013`, Teil 1 (Grundlage, Artikelstamm,
Ausgangsrechnung) · Folge aus [Maske „Steuerschlüssel"](steuerschluessel-maske-sd-20261013.md)

## Auftrag

„Offenes ändern auf einheitlich Steuerschlüssel" (Auftraggeber, 13.10.2026). Rund vierzehn Masken
fragen einen Prozentsatz ab oder setzen 19 ein. Angegeben wird künftig der Steuerschlüssel aus
`domain_erp.tax_keys`; der Satz ist sein Abbild und kommt vom Server.

## Grundlage — eine Auswahl für alle Masken

- `GET /api/v1/finance/tax-keys/auswahl?richtung=verkauf|einkauf` (`schluessel_auswahl`): die heute
  gültigen, aktiven Schlüssel des Mandanten. Verkaufsbelege bekommen keine reinen
  Vorsteuerschlüssel, Eingangsbelege keine reinen Umsatzsteuerschlüssel; Schlüssel ohne Steuerkonto
  (steuerfrei) gelten für beide.
- `satz_des_schluessels(db, mandant, code, richtung)`: der Satz zum Schlüssel — oder eine
  `Steuerklaerung`, wenn der Schlüssel für die Richtung nicht gilt.
- Frontend: `components/finance/SteuerschluesselSelect.tsx` und
  `lib/api/steuerschluessel-auswahl.ts` (`useSteuerschluesselAuswahl`, `satzVon`, `schluesselText`).
  Das Feld wählt nichts vor, zeigt einen hinterlegten, nicht mehr gültigen Schlüssel weiter an und
  sagt, wenn die Auswahl nicht geladen werden konnte.

## Artikelstamm — die Quelle der Position

- Migration `artikel_steuerschluessel_20261013` (ein Head): `domain_inventory.articles` bekommt
  `steuerschluessel_verkauf` und `steuerschluessel_einkauf`. Ein Artikel braucht zwei Schlüssel, weil
  derselbe Artikel im Verkauf Umsatzsteuer und im Einkauf Vorsteuer auslöst.
- Maske `artikel/stamm`: zwei Auswahlfelder statt „MwSt %". Die Vorgabe 19 ist entfernt.
- `mehrwertsteuer_prozent` bleibt für alle, die den Satz lesen, ist aber nur noch das Abbild des
  Verkaufsschlüssels: Mit Schlüssel setzt der Server den Satz. Ein Schlüssel der falschen Richtung,
  ein ungültiger Schlüssel oder ein abweichend mitgeschickter Satz wird abgelehnt (422).
- **Bestand:** `scripts/artikel_steuerschluessel_zuordnen.py --tenant <id> [--apply]` ordnet
  bestehenden Artikeln mit Satz einen Schlüssel zu, **nur** wenn der Mandant für die Richtung genau
  einen gültigen Schlüssel mit diesem Satz hat. Alles andere bleibt offen und wird genannt.
  Trockenlauf ist der Normalfall. In keiner Datenbank ausgeführt.

## Ausgangsrechnung (`POST`/`PUT /finance/invoices`, Maske `finance/invoice-form`)

Vorher:

- Netto, Steuer und Brutto kamen aus der Anfrage, also aus dem Browser.
- Fehlte die Steuer, rechnete der Server mit `(vatRate or 0.19) / 100` — 0,19 Promille.
- Gebucht wurde jeder Erlös auf 8400 und jede Steuer auf 1776, gleich welcher Satz.
- Die Maske belegte „MwSt %" mit 19 vor.

Jetzt:

- Die Position nennt ihren Steuerschlüssel (`taxCode`). Der Server rechnet Netto, Steuer und Brutto
  aus den Schlüsseln (dieselbe Stelle wie die Gutschrift, `steuergruppen`); Summen der Anfrage
  werden nicht übernommen. `vatRate` der Position wird aus dem Schlüssel gesetzt.
- Gebucht wird **je Steuerschlüssel**: Forderung brutto im Soll, Erlös netto auf das Erlöskonto des
  Schlüssels, Umsatzsteuer auf sein Steuerkonto. Beispiel 1.000 € zu 19 % und 200 € zu 7 %:
  1400 Soll 1.404,00 · 8400 Haben 1.000,00 · 1776 Haben 190,00 · 8300 Haben 200,00 · 1771 Haben 14,00.
- Lässt sich die Steuer nicht eindeutig bestimmen, wird nicht gebucht und nicht gespeichert:
  409 „Rechnung … nicht gebucht, bitte prüfen: Position 2 hat keinen Steuerschlüssel." Das gilt für
  fehlenden Schlüssel, Satz ohne Schlüssel, Satz gegen den Schlüssel, unbekannten Schlüssel, reinen
  Vorsteuerschlüssel und Rechnungen ohne Positionen.
- Ein **Entwurf** wird auch ohne Schlüssel gespeichert. Er trägt den Prüfgrund
  (`steuerPruefgrund`), Netto aus den Positionen, Steuer 0 und Brutto = Netto — kein Brutto, das es
  so nicht gibt. Gebucht wird er erst, wenn jede Position einen Schlüssel hat.
- Eine bereits gebuchte Rechnung wird bei einem Statuswechsel nicht neu gerechnet.
- Maske: Auswahl „Steuerschlüssel" je Position statt „MwSt %"; ohne Schlüssel stehen Steuer und
  Brutto auf „offen".

## Auslegungen (meine, nicht entschieden)

- **Ein Satz ohne Schlüssel genügt nicht.** Wie bei der Gutschrift: Der Satz sagt nicht, auf welches
  Konto. Ich leite aus einem Satz keinen Schlüssel ab, auch nicht, wenn es nur einen passenden gäbe.
  Folge: Aufrufer, die nur `vatRate` schicken, können Rechnungen nur noch als Entwurf speichern.
- **Bestehende Masken werden angepasst, nicht neu gebaut.** Die Masken dieser Reihe sind
  handgebaut (500 bis 3.200 Zeilen). Sie bekommen das gemeinsame Feld an der Stelle des
  Prozentfelds; der Neubau als ScreenDefinition ist je Maske ein eigener Slice.
- **Rechnungen ohne Positionen werden nicht gebucht.** Eine Steuersumme ohne Position hat keinen
  Schlüssel.

## Befunde, nicht behoben

- **DocFlow bucht weiter fest auf 8400/1776.** `docflow_service` ruft denselben Buchungsdienst mit
  Kopfsummen; `document_items` tragen nur `tax_rate`. Der feste Weg bleibt dafür bestehen, bis die
  Positionen Schlüssel tragen.
- **Zwei Regeln, welche Konten ein Mandant bebuchen darf.** Der Buchungsdienst der Rechnung
  (`FinanceTransactionService`) kennt nur Konten des Mandanten; Steuerschlüssel-Maske,
  Kontenvorschläge und Gutschrift lassen auch den gemeinsamen Rahmen (`system`) zu. Ein Schlüssel
  mit einem gemeinsamen Konto bucht in der Gutschrift, scheitert aber in der Rechnung.
- **Buchungszeilen der Rechnung tragen keinen Steuerschlüssel** (`journal_entry_lines.tax_code`
  bleibt leer); die Gutschrift schreibt ihn.

## Nachweis

- `tests/test_steuerschluessel_belege.py`: 10 bestanden gegen `valeo_probe` — Auswahl je Richtung,
  abgelaufene und inaktive Schlüssel, Satz aus dem Schlüssel, Artikel mit Schlüsseln (Satz folgt),
  vier abgelehnte Fälle, Satz gegen hinterlegten Schlüssel, Bestandszuordnung nur eindeutig.
- `tests/test_ausgangsrechnung_steuerschluessel.py`: 11 bestanden — Buchung je Schlüssel mit
  Serversummen und offenem Posten, sechs abgelehnte Fälle ohne Beleg und ohne Buchung, Entwurf mit
  und ohne Schlüssel, Entwurf wird erst mit Schlüsseln gebucht, gebuchte Rechnung bleibt.
- Angepasst: `test_rechnung_ein_commit.py` (zwei Tests ersetzen die Steuerermittlung, weil sie
  Rechnungen ohne Positionen schicken) und `test_crm360_finance_handover.py` (neuer Parameter).
- Nachbarn (Rechnung, Storno, Sammelrechnung, Rollenverträge, Gutschrift, Steuerschlüssel-Maske):
  bestanden. `test_coverage_ratchet_erp_core_001.py` ist in 22 Fällen rot mit 401 — die Datei
  schickt keine Anmeldung; ohne Bezug zu diesem Slice.
- Vitest: Auswahlfeld 5, Ausgangsrechnung 2, Artikel 1. `tsc --noEmit` und ESLint ohne Befund.

**Nicht geprüft:** die Masken im Browser (keine lokale Anmeldung ohne Anbieterkonto).

## Teil 2: Eingangsrechnung (`/finance/ap/invoices`, Kernel `PostAPInvoice`)

Der Weg hinter der ScreenDefinition `finance/ap-invoice`, dem Agentenwerkzeug und dem Kernel.

Vorher (beide Buchungswege gleich):

- **Seitenverkehrt:** Kreditor im Soll, Aufwand und Vorsteuer im Haben.
- **Kontonummern statt Konten:** „3300" und „6000" standen an der Stelle der Konto-ID. Das sind zudem
  Nummern aus SKR04; der Verkauf bucht nach SKR03.
- **Ein Vorsteuerkonto für die ganze Rechnung**, gewählt nach dem höchsten Satz, notfalls 1576.
- **Summen aus dem gespeicherten Beleg**, gerechnet aus dem frei eingegebenen Satz.
- **„Verbucht" ohne Buchung:** Scheiterte das Journal, setzte der REST-Weg die Rechnung trotzdem auf
  `VERBUCHT`.
- **Kein offener Posten:** Die Anlage nannte die Spalte `op_betrag`, die es in keiner der beiden
  Datenbanken gibt; der Fehler wurde verschluckt.

Jetzt (`app/services/finance_eingangsrechnung_buchung.py`, von beiden Wegen benutzt):

- Die Position nennt ihren Steuerschlüssel. Gebucht wird **Aufwand netto und Vorsteuer im Soll je
  Steuerschlüssel, Kreditor brutto im Haben**. Beispiel 1.000 € zu 19 % und 200 € zu 7 %:
  3400 Soll 1.000,00 · 1576 Soll 190,00 · 3300 Soll 200,00 · 1571 Soll 14,00 · 1600 Haben 1.404,00.
- **Aufwandskonto:** das der Rechnung (`expenseAccountId`), sonst das des Steuerschlüssels (neu:
  `tax_keys.expense_account`, Migration `steuerschluessel_aufwandskonto_20261013`). Fehlt beides,
  wird nicht gebucht. Die Vorgabe „6000" ist entfernt.
- **Kreditorenkonto:** das der Rechnung, sonst das Sammelkonto des Kontenrahmens des Mandanten
  (SKR03: 1600, SKR04: 3300). Ohne festgelegten Kontenrahmen wird nicht gebucht.
- Journal, offener Posten und Beleg liegen in einer Transaktion. Lässt sich nicht buchen, antwortet
  der REST-Weg 409 „… nicht gebucht, bitte prüfen: …", und die Rechnung bleibt freigegeben. Der
  Kernel-Weg bucht nicht und protokolliert den Grund.
- Schon beim Anlegen und Ändern rechnet der Server die Summen aus den Schlüsseln; ohne eindeutige
  Angabe bleibt die Vorsteuer offen und der Beleg trägt den Prüfgrund.
- Abgelehnt werden: fehlender Schlüssel, Satz ohne Schlüssel, Satz gegen den Schlüssel, unbekannter
  Schlüssel, Umsatzsteuerschlüssel in einer Eingangsrechnung, Reverse Charge, fehlendes
  Aufwandskonto.

Steuerschlüssel-Maske: neues Feld **Aufwandskonto** (Auswahl aus den Aufwandskonten des Kontenplans,
zum Satz passende zuerst). Die SKR03-Grundausstattung trägt für die Schlüssel 8 und 9 die Konten
3300 und 3400 und legt 1600 an. Sie legt Konten jetzt als eigene Konten des Mandanten an, auch wenn
der gemeinsame Rahmen die Nummer führt — der Buchungsdienst bebucht nur eigene Konten.

### Mitbehoben: Lese-Cache gab Pydantic-Antworten als Text zurück

`cached_read_model` schrieb mit `json.dumps(…, default=str)`. Gibt ein Handler Pydantic-Modelle
zurück, lag deren Textdarstellung im Cache; der nächste gleiche Aufruf bekam eine Liste von
Zeichenketten und endete an der Antwortprüfung mit 500, bis der Eintrag ablief. Bei
`GET /finance/tax-keys` (eine Stunde) hieß das mit laufendem Redis: Der zweite Aufruf der
Schlüsselliste scheiterte. Seit die Liste nach Änderungen geleert wird, fiel es nur noch bei
unverändertem Bestand auf. Korrigiert in `app/core/read_model_cache.py` (`_zu_json`), Test
`test_die_liste_laesst_sich_zweimal_hintereinander_lesen`.

### Altlasten-Prüfung (Hinweis des Auftraggebers, 13.10.2026)

„Viele Masken sind schon umgestellt — vorher prüfen, dass keine Altlast bearbeitet wird." Geprüft
gegen Navigation (`app/navigation/domains`), Routen (`route-aliases.json`) und SD-Registry:

| Maske | Navigation | Serverweg | Einordnung |
|---|---|---|---|
| `artikel/stamm` | ja | `/articles` | lebende Maske; angepasst (Teil 1) |
| `finance/invoice-form` | **nein** | `/finance/invoices` | Nebenweg (Route `finance/invoices/new`, KI-Aktion); in Teil 1 angepasst |
| `sales/invoice-editor` | ja | **DocFlow** `/docflow` | die Rechnungsmaske der Navigation; **noch offen** |
| `einkauf/rechnung-eingang-erfassung` | ja | `/einkauf/rechnungen`, `/einkauf/rechnungseingaenge` | die Eingangsrechnung der Navigation; **noch offen** |
| `finance/ap-invoice-form`, `finance/ap-invoice-native` (SD) | nein | `/finance/ap/invoices` | SD-, Agenten- und Kernelweg; Server in Teil 2 korrigiert |
| `sales/order-editor` | ja | — | neuer Auftrag: Altmaske; bestehender: `sales-order-native` (SD) |

Folge: Die Ausgangsrechnung aus Teil 1 betraf nicht den Hauptweg. Rechnungen aus der Navigation
laufen über DocFlow und buchen weiter fest auf 8400/1776. **Befund am zweiten Eingangsrechnungsweg:**
`POST /einkauf/rechnungseingaenge/{id}/verbuchen` setzt nur den Status auf `VERBUCHT`; ein Journal
entsteht dort nicht.

### Nachweis Teil 2

- `tests/test_eingangsrechnung_steuerschluessel.py`: 13 bestanden gegen `valeo_probe` — Buchung je
  Schlüssel mit richtigen Seiten und offenem Posten, Aufwandskonto der Rechnung vor dem des
  Schlüssels, steuerfrei ohne Vorsteuerzeile, sechs abgelehnte Fälle (Rechnung bleibt freigegeben),
  gescheiterte Buchung ohne halben Zustand, kein Kreditorenkonto ohne Kontenrahmen, Kernel-Weg,
  Gruppen nach Schlüssel und Aufwandskonto.
- `tests/test_steuerschluessel_maske.py`: 33 bestanden (neu: Aufwandskonto, zweimal lesen).
- Angepasst: fünf Tests in `test_ap_invoices.py` und `test_ap_invoices_api.py`, die das Rechnen aus
  dem Satz festschrieben, und die Musterzeile in `test_security_tax_keys.py`.
- Nachbarn (Gutschrift, Ausgangsrechnung, Maskenaktionen, Kommando-Wege): bestanden.
  `test_eingangsrechnung_mandant.py`: 18 Rollentests rot mit 401 — auf unverändertem `main` ebenso.
- Vitest: Steuerschlüssel-Maske 8, Bauplan-Cache 3. `tsc --noEmit` ohne Befund.

## Teil 3: DocFlow-Rechnung — der Verkauf führt den Beleg, Finance bucht

Architekturentscheidung des Auftraggebers vom 13.10.2026: „Warenwirtschaft verantwortet den
Geschäftsvorfall und seine Rechnung. Finance verantwortet seine buchhalterischen Konsequenzen."
Keine zweite Rechnungsverwaltung in der Finanzbuchhaltung; Finance ist Buchungsautorität; Fehler
führen zu einem prüfbaren Buchungsstatus.

Für die Ausgangsrechnung heißt das: Belegführend ist DocFlow (`/api/v1/docflow`, Maske
`sales/invoice-editor` — die Rechnungsmaske der Navigation). Der Weg `/finance/invoices` aus Teil 1
ist der Nebenweg.

Vorher:

- Die Position trug nur `tax_rate`, Vorgabe 0. Die Maske belegte „MwSt %" mit 19 vor.
- `POST /docflow/{id}/post` buchte die Kopfsummen fest auf 8400 und 1776, gleich welcher Satz.
- Die Buchung schrieb sich selbst fest, bevor Buchungsnachweis und Belegstatus geschrieben waren.

Jetzt:

- Migration `docflow_steuerschluessel_20261013` (ein Head): `domain_docflow.document_items.tax_code`.
- Die Position nennt ihren Steuerschlüssel. Der Satz kommt dann vom Server; ein Schlüssel, der für
  Verkaufsbelege nicht gilt, oder ein abweichend mitgeschickter Satz wird schon beim Speichern
  abgelehnt. Ohne Schlüssel gilt weiter der Satz der Anfrage — speicherbar, aber nicht buchbar.
- Umwandeln (Auftrag → Lieferschein → Rechnung) nimmt den Steuerschlüssel der Quellposition mit.
- Buchen: Finance (`steuergruppen`, `SalesPostingService`) bucht Erlös und Umsatzsteuer **je
  Steuerschlüssel** auf dessen Konten. Ohne Schlüssel an jeder Position: 409 „Rechnung … nicht
  gebucht, bitte prüfen: …", der Beleg bleibt freigegeben.
- **Beleg und Buchung stimmen auf den Cent:** Die gebuchte Steuer je Schlüssel ist die Summe der
  Positionssteuern des Belegs, nicht neu gerechnet (drei Positionen zu 0,33 € bei 19 %: Beleg und
  Buchung 0,18 €).
- Buchung, Buchungsnachweis (`document_postings`) und Belegstatus werden gemeinsam festgeschrieben.
- Anlegen, Ändern und Umwandeln benutzen eine Positionsanlage; vorher gab es sie dreimal wortgleich.
- Maske `sales/invoice-editor`: Spalte „Steuerschlüssel" (gemeinsames Auswahlfeld) statt „MwSt %";
  die Vorgabe 19 ist entfernt. Die Maske zeichnet ihre Positionen aus
  `domain-schemas/sales_invoice.schema.json` über `features/forms/FormBuilder` — ein drittes
  Maskengerüst neben Mask Builder und Handbau, nur von dieser Seite benutzt. Der Neubau als
  ScreenDefinition steht aus.

### Nachweis Teil 3

- `tests/test_docflow_steuerschluessel.py`: 11 bestanden gegen `valeo_probe` — Satz aus dem
  Schlüssel, drei beim Speichern abgelehnte Fälle, Ändern, Buchung je Schlüssel, Cent-Gleichheit,
  drei Fälle ohne Schlüssel (gespeichert, nicht gebucht, Status nicht „posted"), Umwandeln.
- Bestehende DocFlow-Tests (zehn Dateien): 66 bestanden.
- Vitest: Positionsraster mit Steuerschlüssel-Spalte 2. `tsc --noEmit`, ESLint ohne Befund.

### Befunde, nicht behoben

- **DocFlow nimmt den Mandanten aus der Anfrage** (`tenant_id` als Query-Parameter, sonst der
  Vorgabemandant), nicht aus der Anmeldung. An Codex (Identität).
- **Positionen aus Lieferscheinen der alten Tabellen** (`_bootstrap_sales_delivery`) kommen mit
  `mwst_prozent` und ohne Schlüssel in DocFlow an; solche Rechnungen lassen sich erst buchen, wenn
  die Positionen einen Schlüssel bekommen.
- **Kasse:** Die Maske `pos/terminal` weist im Bon fest 19 % aus, auch bei 7-%-Artikeln (unverändert).

## Noch mit Prozentsatz (Teil 2 ff.)

| Maske | Stand heute |
|---|---|
| `einkauf/rechnung-eingang-erfassung` | `mwstProzent`, Vorgabe 19; Tabellen-Default 19,00 |
| `einkauf/rechnungseingang` | feste Liste `VAT_19`/`VAT_7`/`VAT_0` |
| `finance/ap-invoice-form` | Eingangsrechnung Finanz |
| `einkauf/gutschriften-belastungen` | `taxRate`, Vorgabe 19 |
| `einkauf/lieferschein-erfassung`, `verkauf/lieferschein-erfassung` | Vorgabe 19; Tabellen-Default 19 |
| `einkauf/bestellung-anlegen`, `einkauf/bestellvorschlaege` | `taxRate: 19` fest |
| `sales/angebot-erstellen`, `sales/OrderEditorLegacyPage` | Vorgabe 19, sonst aus dem Artikel |
| `agrar/zinsabrechnung` | „MwSt-Satz (%)", Vorgabe 19 |
| `pos/terminal` | Bon weist immer 19 % aus (`mwst_zeilen` fest), auch bei 7-%-Artikeln |
| `agrar/ernte-annahme-erfassung` | `vat_rate_percent` aus dem Artikel |
