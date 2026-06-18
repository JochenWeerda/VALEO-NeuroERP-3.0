# Steuerberater- und Payroll-Exportprofile

## Architekturregel

VALEO erzeugt kanonische Exportdaten, Pruefdaten, FIBU-/KORE-Uebergaben und Payroll-Vorlaufdaten. VALEO behauptet keine Hersteller- oder DATEV-Zertifizierung, solange kein dokumentierter Hersteller-, DATEV- oder Steuerberater-Testimport vorliegt.

Gesetzliche Lohnabrechnung, ELStAM, DEUEV, Beitragsnachweise, Bescheinigungen und amtliche Lohnsteuerberechnung bleiben externe Gates ueber zertifizierte Payroll-Systeme oder Steuerberater.

## DATEV als Goldstandard

DATEV-kompatible Buchungsdaten sind der primaere gemeinsame Nenner fuer deutsche Steuerberaterprozesse. Andere Kanzleisoftwareprofile werden deshalb zuerst auf den kanonischen VALEO-Accounting-Export und dann auf DATEV-kompatible oder CSV-/ASCII-Uebergaben gemappt.

## Kanonisches Modell

`AccountingExportLine` enthaelt mindestens:

- Mandant, Export-Batch, Profil, Wirtschaftsjahr und Periode
- Buchungsdatum, Belegdatum, optional Leistungsdatum
- Belegnummer, Belegart, Sachkonto, Gegenkonto, Soll/Haben
- Netto-/Brutto-/Steuerbetrag, Steuer-/Buchungsschluessel und Waehrung
- Buchungstext, Debitor/Kreditor, KOST1, KOST2, Profit-Center
- Faelligkeit, Zahlungsbedingung, IBAN, Beleglink und Archiv-ID
- Zeilenpruefsumme und optionalen Korrekturbezug

Jeder Export-Batch besitzt Status `draft`, `validated`, `exported`, `accepted_by_tax_advisor`, `rejected` oder `corrected`. Korrekturen erzeugen neue Batch-Versionen und ueberschreiben nie exportierte Daten.

## Profile

| Profil | Strategie | Status |
| --- | --- | --- |
| `datev_accounting_csv` | DATEV-kompatibler Buchungsstapel als Goldstandard | `datev_compatible_contract` |
| `agenda_datev_compatible_csv` | DATEV-kompatibel zuerst, CSV/ASCII-Fallback | `not_certified` |
| `addison_datev_compatible_csv` | DATEV-kompatibel zuerst, ADDISON-Mapping je Kanzlei | `not_certified` |
| `simba_datev_compatible_csv` | DATEV-kompatibel zuerst, Simba-Mapping je Kanzlei | `not_certified` |
| `lexware_datev_csv` | einfacher DATEV-/CSV-Export fuer KMU-/Steuerberateruebergabe | `not_certified` |
| `sage_datev_csv` | Sage 50/100/HR als Unterprofile, DATEV-kompatibel zuerst | `not_certified` |
| `sbs_wolterskluwer_datev_csv` | DATEV-kompatibel zuerst, SBS/WK-Mapping je Kanzlei | `not_certified` |

Alle `not_certified`-Profile setzen `requires_tax_advisor_test_import: true`.

## KOST1/KOST2

Kostenstelle und Kostentraeger bleiben im kanonischen Modell immer getrennt. Fuer Payroll- und KORE-relevante Buchungen muss `cost_center_1` befuellt sein; `cost_center_2` wird fuer Kostentraeger, Kampagnen, Projekte oder Profit-Center-nahe Auswertungen genutzt.

## Payroll-Abgrenzung

Payroll in VALEO bedeutet:

- Arbeitszeiten, Abwesenheiten, Zuschlaege, Kostenstellen und Kostentraeger als Vorlaufdaten
- Lohnbuchungen fuer FIBU/KORE inklusive Bruttolohn, Arbeitgeberanteilen, SV, Lohnsteuer, Verbindlichkeiten und Auszahlungsbetrag
- DATEV-/CSV-/ASCII-Uebergabepaket mit Pruefsummen und Audit-Log

Payroll in VALEO bedeutet nicht:

- zertifizierte amtliche Lohnabrechnung
- ELStAM-/DEUEV-/SV-Meldewesen
- produktive DATEV-LODAS- oder Lohn-und-Gehalt-Zertifizierung ohne Abnahmetest

## Externe Gates

- Steuerberater-Testimport je Profil
- DATEV-/Herstellerdokumentation oder Partnerfreigabe
- fachliche Abnahme von Lohnarten, Sachkonten, Kostenstellen und Kostentraegern
- Periodensperre und Korrekturprozess im Produktivbetrieb
