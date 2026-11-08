# Steuerschlüssel: eine Quelle, SKR03 für den Testmandanten

Stand: 2026-10-12 · Slice `STEUERSCHLUESSEL-EINHEIT-20261012` · Folge aus
[Gutschrift: Umsatzsteuer je Position](gutschrift-umsatzsteuer-20261012.md)

## Auftrag

„Nutze SKR03 für unseren Testmandanten. Maske an Steuerschlüssel(-Tabelle) ändern, systemweit
vereinheitlichen."

## Befund: zwei Tabellen für dieselbe Sache

| | `domain_erp.tax_keys` | `public.vat_codes` |
|---|---|---|
| Maske | „Steuerschlüssel" (`finance/steuerschluessel.tsx`) | keine |
| Leser | Eingangsrechnung (Vorsteuerkonto), UStVA-Ausgabe (Position je Schlüssel) | niemand |
| Zuschnitt | je Mandant, Code 1–2 Ziffern, Gültigkeit von/bis, UStVA-Position | systemweit, Kürzel `DE_19` |
| Inhalt | leer (beide Datenbanken) | 10 Vorgaben im Prüfstand, leer in der Entwicklungs-DB |

Der Slice `GUTSCHRIFT-UST-20261012` vom selben Tag hatte die Gutschrift an `vat_codes` gehängt – die
Tabelle, die sonst niemand liest. **Das war falsch und ist hier korrigiert.** Ursache: Ich hatte nach
„vat" und „tax_code" gesucht und die deutsch benannte Maske und ihre Tabelle nicht gesehen.

## Lieferung

- **Eine Quelle:** `app/finance/steuerschluessel.py` – `steuergruppen()` liest die Steuerschlüssel des
  Mandanten aus `tax_keys` (aktiv, heute gültig) und liefert je Schlüssel Netto, Steuer, Erlös- und
  Steuerkonto, oder eine `Steuerklaerung`. Die Gutschrift benutzt nur noch diese Stelle.
- **`tax_keys.revenue_account`** (Erlöskonto für Verkaufsbelege) und **`tax_keys.par_24_ustg`**
  (Durchschnittssatz § 24 UStG) – pflegbar über die Steuerschlüssel-Wege (anlegen, ändern, lesen).
- **Rücknahme:** `vat_codes.skr03_revenue_account` und die zugehörigen Änderungen an Modell und Wegen
  sind entfernt. `vat_codes` selbst steht noch (siehe Offen).
- **SKR03 für einen Mandanten:** `richte_skr03_ein()` und
  `scripts/seed_steuerschluessel_skr03.py --tenant … [--apply]` legen an, was fehlt:
  - Kontenrahmen `SKR03` als Mandanteneinstellung (`finance.kontenrahmen`)
  - Steuerschlüssel 2 (USt 7 % → 1771, Erlös 8300), 3 (USt 19 % → 1776, Erlös 8400),
    8 (Vorsteuer 7 % → 1571), 9 (Vorsteuer 19 % → 1576), gültig ab 01.01.2021
  - fehlende Konten im Kontenplan des Mandanten (im gemeinsamen Rahmen fehlen 1571, 1771, 8300)
- **Eingangsrechnung:** Bei gleichem Satz gibt es jetzt einen Umsatzsteuer- und einen
  Vorsteuerschlüssel. Der Auflöser nimmt den mit Vorsteuerkonto. 7 % geht damit auf 1571 statt auf
  den Rückfallwert 1576.
- **Entwicklungsdatenbank:** Der Mandant `00000000-0000-0000-0000-000000000001` („Default Tenant")
  ist als Testmandant mit SKR03 eingerichtet.

### Auslegungen (einfachste tragfähige – bitte widersprechen, wenn falsch)

- **„Unser Testmandant" ist der Default-Mandant** `…0001`.
- **Grundausstattung sind nur die vier Regelfälle.** Steuerfrei, innergemeinschaftlich, Export und
  § 24 legt die Buchhaltung in der Maske an – ein geratenes Konto wäre eine stillschweigende Annahme.
- **Schlüsselnummern 2, 3, 8, 9** folgen der in DATEV üblichen Belegung.
- **Gültig ab 01.01.2021** (nach der befristeten Senkung auf 16 %/5 % im zweiten Halbjahr 2020).

## Nachweis

Gegen `valeo_probe` (Migration `steuerschluessel_einheit_20261012` frisch eingespielt, ein Head):

- `tests/test_gutschrift_umsatzsteuer.py` – 20 bestanden. Die Fälle des Vorgängers laufen jetzt
  über die Schlüssel des Mandanten; neu: SKR03-Einrichtung (vier Schlüssel mit Konten, zweiter Lauf
  legt nichts an, Kontenrahmen = SKR03), Vorsteuerkonto der Eingangsrechnung (19 % → 1576,
  7 % → 1571), Pflege des Erlöskontos über die Steuerschlüssel-Wege.
- Nachbarn: `test_security_sales_credit_notes`, `test_buchung_nicht_still`,
  `test_kontosperre_meldung`, `test_security_vat_return_export`, `test_security_tax_keys`,
  `test_tax_keys_validation`, `test_ap_invoices`, `test_ap_invoices_api` – grün.
  (`test_ap_invoices*` riefen den Produktionsdienst ohne Anmeldung und waren rot; sie nehmen jetzt
  die Test-Anwendung.)

## Nicht geprüft

- Die Maske „Steuerschlüssel" zeigt Erlöskonto und § 24 noch nicht (folgt mit den Masken).
- UStVA und DATEV-Ausgabe mit den neuen Schlüsseln.
- Eine Eingangsrechnung bis zur Buchung mit 7 % (nur der Auflöser ist getestet).

## Offen

- **Masken:** Steuerschlüssel-Auswahl statt Prozent-Freitext – Gutschrift zuerst, dann die übrigen
  Belegmasken (eigener Slice, mit Ratsche über die verbleibenden Stellen).
- **`vat_codes` entfernen?** Tabelle, Wege (`/finance/vat-codes`) und Modell haben keinen Verbraucher.
  Löschen ist eine eigene Entscheidung.
- **Eingangsrechnung** bestimmt das Vorsteuerkonto aus dem höchsten Satz des Belegs, nicht je Position.
- **Ausgangsrechnung** (`sales_posting_service.py`) bucht weiter mit festem Steuerkonto 1776.
- **Steuerkontext der Ursprungsrechnung:** Die Gutschrift nimmt den Steuerschlüssel aus ihren eigenen
  Positionen. Zielbild ist, ihn aus dem ursprünglichen Geschäftsvorfall zu übernehmen.
- **Tax Rules Service / EU-TEDB** (Architekturvorgabe vom 12.10.): `tax_keys` mit Gültigkeitszeitraum
  ist der lokal freigegebene Bestand, aus dem gebucht wird. Abgleich mit TEDB, Vorschlag-und-Freigabe,
  Rechtsnachweis je Regel und die Ableitung aus Artikel, Partner und Geschäftsvorfall sind eingeplant,
  nicht gebaut.
- **DATEV-Automatikkonten** (aus dem Vorgänger): weiterhin ungeprüft.
