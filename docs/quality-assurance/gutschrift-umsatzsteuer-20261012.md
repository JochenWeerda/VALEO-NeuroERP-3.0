# Gutschrift: Umsatzsteuer je Position

Stand: 2026-10-12 · Slice `GUTSCHRIFT-UST-20261012` · offener Punkt aus
[Kein „gebucht" ohne Buchung](buchung-nicht-still-20261012.md)

> **Korrektur vom selben Tag:** Dieser Slice hing die Gutschrift an `vat_codes` – eine Tabelle, die sonst
> niemand liest. Seit [Steuerschlüssel: eine Quelle](steuerschluessel-einheit-20261012.md) kommt der
> Steuerschlüssel aus `domain_erp.tax_keys` des Mandanten (Codes `3`, `2` statt `DE_19`, `DE_7`; Erlöskonto
> in `tax_keys.revenue_account`). Die Buchungslogik unten gilt unverändert.

## Fachliche Entscheidung (Auftraggeber, 12.10.2026)

1. Steuersatz je Position, nicht pauschal je Gutschrift.
2. Netto, Umsatzsteuer und Brutto getrennt führen; der Belegbetrag ist brutto. Kein blindes
   Herausrechnen bei steuerfreien Gutschriften.
3. Erlöskorrektur nur netto; das Erlöskonto wird nicht mit dem Bruttobetrag belastet.
4. Umsatzsteuer separat auf dem passenden Steuerkonto berichtigen.
5. Keine stillschweigende Steuerannahme: Fehlen Steuersatz oder Einordnung, wird die automatische
   Buchung blockiert und zur Prüfung vorgelegt.

Dazu: Steuersätze, Konten und Sonderfälle konfigurierbar; § 24 UStG berücksichtigen;
kaufmännische Rechnungskorrektur und Gutschrift nach § 14 UStG technisch unterscheiden;
bei widersprüchlichen Steuerangaben ablehnen; vorhandene Buchungen nicht überschreiben.

## Ausgangslage

- Der Gesamtbetrag ging ungeteilt gegen 8400; eine Umsatzsteuerberichtigung gab es nicht.
- Die Position trug `tax_rate` mit Vorgabe 19 – in Schema **und** Tabelle.
- `total_amount` war die Summe der Nettozeilen, hieß aber Gesamtbetrag.
- Es gibt eine pflegbare Tabelle der Steuerschlüssel (`vat_codes`: Satz, Steuerkonto, Kennzeichen für
  § 24, Reverse Charge, steuerfrei). Die Gutschrift benutzte sie nicht.

## Umsetzung

| Entscheidung | Umsetzung |
|---|---|
| Satz je Position | Position trägt `tax_code` (Steuerschlüssel aus `vat_codes`). `tax_rate` hat keine Vorgabe mehr. |
| Netto/Steuer/Brutto getrennt | `sales_credit_notes.net_amount`, `tax_amount`; `total_amount` ist brutto. |
| Erlös nur netto | Soll Erlöskonto des Steuerschlüssels = Netto. |
| Steuer separat | Soll Steuerkonto des Steuerschlüssels = Steuer; bei 0 % keine Steuerzeile. |
| Forderung | Haben 1400 = Brutto; der offene Posten der bezogenen Rechnung wird um Brutto gemindert. |
| Keine Annahme | Jeder der folgenden Fälle: 409 „Gutschrift nicht gebucht, bitte prüfen: …", nichts gebucht, Gutschrift bleibt Entwurf. |
| Konfigurierbar | Erlöskonto je Steuerschlüssel: neues Feld `vat_codes.skr03_revenue_account`, pflegbar über die Steuerschlüssel-Wege. |
| § 14 UStG | `sales_credit_notes.correction_type`: `rechnungskorrektur` oder `gutschrift_14_ustg`. Die zweite wird über diesen Weg nicht gebucht. |
| Nicht destruktiv | Migration legt nur Spalten an; Vorbelegung fasst nur leere Felder an; gebucht wird nur neu. |

Zur Prüfung statt gebucht:

- keine Positionen
- Position ohne Steuerschlüssel
- Steuerschlüssel unbekannt, inaktiv oder nicht mehr gültig
- Satz der Position widerspricht dem Steuerschlüssel (beim Anlegen schon 422)
- Steuerschlüssel ohne Erlöskonto, oder mit Satz > 0 ohne Steuerkonto
- Reverse-Charge-Schlüssel
- Belegbetrag ≠ Brutto der Positionen
- ein benötigtes Konto fehlt im Kontenplan
- Gutschrift nach § 14 UStG

Die Steuer wird je Steuerschlüssel auf die Summe der Nettobeträge gerechnet (kaufmännisch
gerundet), nicht je Position.

### Auslegungen (einfachste tragfähige – bitte widersprechen, wenn falsch)

- **Vorbelegt sind nur zwei Erlöskonten:** 19 % → 8400, 7 % → 8300. Alle anderen Schlüssel
  (§ 24 Durchschnittssätze, steuerfrei, innergemeinschaftlich, Export) haben **kein** Erlöskonto.
  Mit ihnen wird nicht automatisch gebucht, bis die Buchhaltung sie einordnet. Das ist Absicht:
  Ein geratenes Erlöskonto für § 24 wäre eine stillschweigende Annahme.
- **Kontenrahmen SKR03.** `vat_codes` kennt auch SKR04-Konten; welcher Rahmen je Mandant gilt, ist
  nirgends hinterlegt. Die übrige Buchungslogik rechnet mit SKR03.
- **Erlösschmälerungskonten** (z. B. 8700 ff.) sind über das Erlöskonto des Steuerschlüssels
  einstellbar – ein eigener Schlüssel je Fall –, aber nicht je Gutschrift wählbar.
- **Alte Entwürfe**, deren `total_amount` die Nettosumme ist, werden beim Buchen abgelehnt
  („Belegbetrag weicht vom Brutto ab") und nicht umgedeutet. In beiden Datenbanken gibt es keine.

## Nachweis

Gegen `valeo_probe` (Migration frisch eingespielt):

`tests/test_gutschrift_umsatzsteuer.py` – 17 bestanden:

- Buchungsbeispiel der Entscheidung: 1.190 brutto, 19 % → 8400 Soll 1.000,00 · 1776 Soll 190,00 ·
  1400 Haben 1.190,00; Netto und Steuer an der Gutschrift gespeichert.
- Offener Posten der Rechnung 1.500 → 310; der zweite Posten des Kunden bleibt 400.
- Gemischt 19 % und 7 %: je Schlüssel eine Erlös- und eine Steuerzeile (150 / 28,50 und 200 / 14,00).
- Steuerfrei: 500 netto = 500 brutto, keine Steuerzeile.
- Anlegen über die Schnittstelle: 2 × 500 mit `DE_19` → netto 1.000, Steuer 190, brutto 1.190.
- Anlegen ohne Steuerangabe: Satz der Position bleibt leer (nicht 19), Buchen wird abgelehnt.
- Anlegen mit Widerspruch (Schlüssel 19 %, Satz 7): 422.
- Neun Fälle „zur Prüfung", jeweils: 409, keine Buchung, Gutschrift bleibt Entwurf.
- Gesperrtes Konto 1400: 409, kein Buchungskopf, offene Posten unberührt.

Nachbarn: `test_buchung_nicht_still` (5), `test_kontosperre_meldung` (8),
`test_security_sales_credit_notes` (3), `test_process_kernel_wave73_…`,
`test_security_vat_return_export` – grün.

## Nicht geprüft

- Die Maske „Gutschrift" (`credit-note-editor.tsx`) im Browser. Sie führt je Position einen
  Steuersatz, keinen Steuerschlüssel, und speichert über den Belegspeicher, nicht über diesen Weg.
- Eine Gutschrift mit § 24-Schlüssel bis zur Buchung (es ist kein Erlöskonto eingeordnet).
- Die Umsatzsteuer-Voranmeldung nach einer gebuchten Gutschrift.

## Offen

- **DATEV-Automatikkonten.** 8400 und 8300 sind in DATEV Automatikkonten. Die Buchung führt die
  Steuer als eigene Zeile; die Zeilen tragen den Steuerschlüssel (`journal_entry_lines.tax_code`).
  Ob die DATEV-Ausgabe daraus eine doppelte Steuer macht, ist **nicht geprüft** – vor dem ersten
  Export mit Gutschriften zu klären.
- **Maske:** Steuerschlüssel je Position auswählen; Anzeige von Netto, Steuer, Brutto; Anzeige des
  Prüfgrunds bei abgelehnter Buchung.
- **§ 24 und übrige Schlüssel einordnen:** Erlöskonten durch die Buchhaltung hinterlegen.
- **Entwicklungsdatenbank:** `vat_codes` ist dort leer. Ohne Steuerschlüssel lässt sich dort keine
  Gutschrift buchen (`POST /finance/vat-codes/seed-defaults` legt die Vorgaben an).
- **Gutschrift nach § 14 UStG** hat hier nur die Kennzeichnung; gebucht wird sie über die
  Abrechnungsgutschrift (Agrar-Abrechnung), deren Umsatzsteuer dieser Slice nicht angefasst hat.
- **Ausgangsrechnung** (`sales_posting_service.py`) bucht weiter mit festem Steuerkonto 1776.
