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

## Noch mit Prozentsatz (Teil 2 ff.)

| Maske | Stand heute |
|---|---|
| `sales/invoice-editor` | schickt `tax_rate` je Position |
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
| DocFlow | Buchung fest 8400/1776 |
