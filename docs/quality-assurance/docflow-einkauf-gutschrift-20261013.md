# DocFlow: Einkaufsbelege, Buchung der Eingangsrechnung und der Gutschriften über Finance

Stand: 2026-10-13 · Slice `DOCFLOW-EINKAUF-GUTSCHRIFT-20261013` · Phase 0.4 und 0.5 aus
[Bestandsprüfung Screen Framework](../design/screen-framework-fiori-gap-analyse.md) ·
Folge aus [Teilmengen und Statushistorie](docflow-teilmengen-statushistorie-20261013.md)

## Auftrag

Entscheidung des Auftraggebers vom 13.10.2026: DocFlow führt die Belege; der Einkauf verantwortet die
Eingangsrechnung fachlich, die Finanzbuchhaltung bucht. Der alte Einkaufsweg wird nicht repariert.

## Vorher

- DocFlow kannte nur Verkaufs- und Kassenbelege.
- `post` setzte bei jeder Belegart den Status „gebucht"; eine Buchung entstand nur für die
  Ausgangsrechnung. Eine Gutschrift (`sales_credit_memo`) galt als gebucht, ohne Journal und ohne
  Minderung des offenen Postens.
- `reverse` setzte bei allem außer der Ausgangsrechnung nur den Status.
- Ein Auftrag ließ sich direkt berechnen und zusätzlich über seine Lieferscheine.

## Jetzt

### Einkaufsbelegarten (0.4)

| Belegart | Nummernkreis | Folgebelege |
|---|---|---|
| `purchase_order` Bestellung | POR | Wareneingang, Eingangsrechnung |
| `goods_receipt` Wareneingang | GRN | Eingangsrechnung |
| `purchase_invoice` Eingangsrechnung | PIV | Einkaufsgutschrift |
| `purchase_credit_memo` Einkaufsgutschrift | PCM | — |

- Teilmengen, Restmengen, Belegbezug je Position, Statushistorie und Protokoll gelten wie im Verkauf.
- **Steuerrichtung nach Belegart:** Einkaufsbelege nehmen Vorsteuerschlüssel, Verkaufsbelege
  Umsatzsteuerschlüssel. Ein Schlüssel der falschen Richtung wird schon beim Speichern abgelehnt.
- **Aufwandskonto je Position** (`document_items.expense_account`, Migration `docflow_einkauf_20261013`,
  ein Head); leer = das des Steuerschlüssels. Umwandeln nimmt es mit.
- **Eingangsrechnung buchen:** Finance (`finance_eingangsrechnung_buchung`) bucht Aufwand netto und
  Vorsteuer im Soll je Steuerschlüssel und Aufwandskonto, Kreditor brutto im Haben, und legt den
  offenen Posten an. Beispiel sechs Tonnen zu 100 € mit 19 %: 3400 Soll 600,00 · 1576 Soll 114,00 ·
  1600 Haben 714,00.
- **Beleg und Buchung stimmen auf den Cent** — gebucht wird die Steuer der Positionen des Belegs.
- **Ohne eindeutige Angabe keine Buchung:** fehlender Steuerschlüssel, fehlendes Aufwandskonto oder
  fehlender Lieferant → 409 bzw. 400, der Beleg bleibt offen.
- **Storno der Eingangsrechnung:** Gegenbuchung über Finance, offener Posten storniert, Status
  „storniert" — in einem Commit.

### Gutschriften (0.5)

Neu: `app/services/finance_belegbuchung.py`.

- **Verkaufsgutschrift** (`sales_credit_memo`): Erlös netto und Umsatzsteuer je Steuerschlüssel im
  Soll, Forderungen brutto im Haben; der offene Posten der Bezugsrechnung wird um den Bruttobetrag
  gemindert. Beispiel zwei von zehn Einheiten zu 100 € mit 19 %: 8400 Soll 200,00 · 1776 Soll 38,00 ·
  1400 Haben 238,00; offener Posten 1.190,00 → 952,00.
- **Einkaufsgutschrift** (`purchase_credit_memo`): Kreditor brutto im Soll, Aufwand netto und
  Vorsteuer im Haben; der offene Posten der Eingangsrechnung wird gemindert.
- Die Bezugsrechnung ergibt sich aus der Belegkette (Umwandeln Rechnung → Gutschrift). Eine
  Gutschrift ohne Bezug bucht, mindert aber keinen Posten.
- **Eine gebuchte Gutschrift wird nicht storniert**, solange ihre Gegenbuchung fehlt — der Aufruf wird
  abgelehnt, statt den Status ohne Buchung zu setzen.

### Keine Doppelberechnung

Ein Auftrag bzw. eine Bestellung wird entweder direkt berechnet oder über die Lieferungen bzw.
Wareneingänge — nicht beides:

- Hat der Auftrag eine aktive Lieferung, lehnt DocFlow die Rechnung aus dem Auftrag ab.
- Ist der Auftrag schon direkt berechnet, lehnt DocFlow die Rechnung aus seiner Lieferung ab.

Stornierte, abgebrochene und gelöschte Folgebelege zählen nicht.

## Auslegungen (meine, nicht entschieden)

- **Entweder direkt oder über die Lieferung.** Die einfachste Regel, die Doppelberechnung
  ausschließt. Sie verbietet den Mischfall „ein Teil geliefert und daraus berechnet, der Rest direkt
  berechnet"; wer das braucht, braucht eine Restmengenrechnung über beide Wege.
- **Kreditorenkonto aus dem Kontenrahmen** (SKR03: 1600), da der Beleg keines trägt.
- **Fälligkeit 30 Tage nach Belegdatum**, weil der DocFlow-Kopf kein Fälligkeitsdatum hat.
- **Eingangsrechnung ohne Wareneingang ist erlaubt** (Rechnung direkt aus der Bestellung oder frei
  erfasst). Ein Abgleich Rechnung gegen Wareneingang und Bestellung (Menge, Preis) ist nicht Teil
  dieses Slices.

## Befunde und Lücken, nicht behoben

- **Storno gebuchter Gutschriften** fehlt (wird abgelehnt).
- **Andere Belegarten:** `post` setzt für Auftrag, Lieferschein, Bestellung und Wareneingang weiterhin
  nur den Status; eine Bestandsbuchung löst DocFlow nicht aus.
- **Rechnungskontrolle** (Betrag des Lieferanten gegen die Summe der Positionen, Drei-Wege-Abgleich).
- **Zwei Gutschriftstrukturen:** Die Gutschrift mit Agentenfreigabe (`/sales/credit-notes`, Maske
  `sales/gutschrift`) besteht daneben weiter; sie auf DocFlow umzuziehen ist ein eigener Slice.
- **Kein Fälligkeitsdatum und keine Zahlungsbedingung am DocFlow-Kopf.**
- **Mandant aus der Anfrage** (Phase 0.1) liegt bei Codex; die Tests binden den Mandanten schon an
  die Anmeldung.

## Nachweis

- `tests/test_docflow_einkauf_gutschrift.py`: 17 bestanden gegen `valeo_probe` — Bestellung → zwei
  Wareneingänge → Eingangsrechnung → Buchung mit offenem Posten; Schlüssel der falschen Richtung in
  drei Belegarten; zwei unklare Eingangsrechnungen bleiben offen; Aufwandskonto der Position teilt
  die Buchung; kein Buchen ohne Lieferant; Cent-Gleichheit; Storno mit Gegenbuchung;
  Verkaufsgutschrift und Einkaufsgutschrift mit Minderung des offenen Postens; Gutschrift ohne
  Schlüssel; gebuchte Gutschrift nicht ohne Gegenbuchung stornierbar; keine Doppelberechnung in
  beiden Richtungen und für Verkauf und Einkauf.
- `tests/test_docflow_teilmengen_statushistorie.py`: 19 bestanden; ein Test ersetzt (er berechnete
  einen Auftrag mit Lieferschein direkt — das ist jetzt ausgeschlossen): Teilrechnungen aus dem
  Lieferschein bis zur gelieferten Menge.
- Gesamtlauf mit den Nachbarn (übrige DocFlow-Tests, Eingangsrechnung, Ausgangsrechnung, Gutschrift,
  Übergabe, Tabellenbesitz) einschließlich der beiden Dateien oben: 193 bestanden, 1 übersprungen.
- `check_pagination`, `check_dead_transactions`, `check_baseline_integrity`,
  `check_domain_table_ownership`: in Ordnung.

**Nicht geprüft:** Es gibt noch keine Maske für die Einkaufsbelegarten; geprüft ist der Serverweg.
