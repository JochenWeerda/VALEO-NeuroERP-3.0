# HRM Payroll Deepening

## Ergebnis

Der Payroll-Bereich wird als Vorlauf-, Pruef-, FIBU-/KORE- und Uebergabeschicht vertieft. VALEO erzeugt keine Scheingenauigkeit fuer gesetzliche Lohnabrechnung.

Umgesetzt im Slice `HRM-PAYROLL-DEEP-001`:

- versionierter Payroll-Parametervertrag `DE-PAYROLL-2026-PREVIEW-1`
- explizites API-Response-Modell fuer `/api/v1/personal/lohn/berechnung`
- Arbeitnehmer- und Arbeitgeberanteile fuer KV/RV/ALV/PV
- Netto, Arbeitgeber-Gesamtkosten und externe Gate-Liste im Ergebnis
- Monats-Closeout-Preview mit DATEV-ASCII-artigen Vorlaufzeilen
- FIBU-Buchungssaetze fuer Bruttolohn, Arbeitgeberanteile, Steuer-/SV-Verbindlichkeiten und Auszahlung
- Korrekte Abgrenzung: BMF-PAP, DATEV-Zielformat und Steuerberater-Cutover bleiben externe Gates

## Nicht-Ziele

- keine amtliche Lohnsteuerberechnung als zertifiziertes Ergebnis
- keine ELStAM-/DEUEV-/SV-Meldeportal-Anbindung
- keine Herstellerzertifizierung fuer DATEV LODAS, Lohn und Gehalt, Sage, Lexware, Agenda, ADDISON, Simba oder SBS/WK

## Anschluss an Exportprofile

Der Slice `INT-ACCOUNTING-EXPORT-PROFILES-001` stellt die kanzleisoftware-neutrale Exportschicht bereit. Payroll-Closeouts liefern dafuer kanonische Buchungs- und Vorlaufdaten; die Profilschicht rendert daraus DATEV-kompatible oder CSV-/ASCII-Uebergaben.
