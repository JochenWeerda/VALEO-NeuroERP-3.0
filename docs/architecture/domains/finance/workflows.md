---
title: Finance — Workflows
type: explanation
audience: [entwickler, fachlich]
owner: domain/finance
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Finance — Workflows

Rechnungstapel: kanonische Belegreferenzen sammeln -> Datenqualitaet pruefen ->
durch abweichenden Benutzer freigeben -> idempotent ausfuehren -> Fehlerzeilen
mit Quellbeleg und Nachweis klaeren -> begruendet wiederholen.

- [fin-001 Finance to Reporting](../../../workflows/fin-001-finance-to-reporting.md)
- O2C → FiBu: [seq-o2c-fibu.md](../../views/sequences/seq-o2c-fibu.md)
- Abschluss / Closing: Process Kernel FiBu-Slices
- UStVA / ELSTER: Frontend `meldewesen`, Open Gaps FIBU-006
- POS/TSE: [pos-fiscalization-providers.md](../../pos-fiscalization-providers.md)

Bonus: freigegebenen festen Bericht und Periode waehlen -> Basiszeilen
berechnen -> unveraenderlichen Lauf speichern -> optional Korrekturlauf mit
Bezug/Grund -> auditierter CSV-Export. Ursprungslauf bleibt unveraendert.

## Bank- und Zahlungsabgleich

Tenant aus X-Tenant-ID -> echten Auszug und Bankzeile lesen -> eindeutige
Belegreferenz, Waehrung und Zahlungsrichtung pruefen -> OP-Rest exakt reduzieren
-> Bankzeile persistent zuordnen -> bei OP-Rest null eigenen Beleg als bezahlt
markieren -> hashverketteten Nachweis schreiben -> gemeinsam committen.

Import-Automatik, manuelle Zuordnung und Batch-Automatik nutzen denselben
Vertrag. Mehrdeutigkeit und Ueberzahlung bleiben unzugeordnet; Teilzahlungen
lassen den OP und die Rechnung offen. Batch maximal 100 Zeilen; wiederholte
Zuordnung derselben Bankzeile ist idempotent. Keine neue GL-Buchung durch
blossen Abgleich. Nachweis:
[Matching-Abnahme](../../../quality-assurance/bank-payment-matching-integrity-20261001.md).

Dateiimport -> aktives eigenes Konto mit gueltiger IBAN und gleicher Waehrung
pruefen -> fuer CAMT/MT940 Datei-IBAN vergleichen -> Dateiidentitaet aus
Tenant/Konto/Format/Originalbytes sperren -> einmal atomar speichern oder
vorhandenen Auszug mit aktuellem Zuordnungsstatus liefern. Beide CSV-Routen
teilen die Identitaet. Replay fuehrt keinen erneuten Abgleich durch, auch
nicht bei geaendertem auto_match; expliziten Batchabgleich verwenden.
Historische UUID-Importe und gleiche Buchungen in anderen Datei-Bytes bleiben
separate Fachgaps. CSV-Salden sind synthetische Summen, keine Banknachweise.
[Kontobindung und Replay-Abnahme](../../../quality-assurance/bank-import-account-replay-20261001.md).

MT940 verarbeitet jede :61:-Zeile auch ohne :86:-Beschreibung und vergleicht
Anfangssaldo plus Zeilen exakt mit dem angegebenen Schlusssaldo. Ein Auszug
mit IBAN, passenden Waehrungen und gueltigen Daten; Widersprueche verhindern
alle Writes. RC/RD bis zum Rueckbuchungsvertrag explizit abgelehnt.
Weitere Bankprofile und CAMT-Details bleiben separate Abnahmen.
[MT940-Profil und Parser-Abnahme](../../../quality-assurance/bank-mt940-parser-integrity-20261001.md).

CAMT.053.001.02 liest gezielt OPBD und CLBD, gleicht gebuchte Zahlungen exakt
gegen den Bank-Endsaldo ab und behaelt explizite Buchungs-/Valutadaten sowie
alle Referenztexte und Gegenkonten. Nur BOOK-Einzelzahlungen ohne Reversal;
Sammelbuchungen, FX und Retouren ohne Fachvertrag werden abgelehnt. Auch
leere Auszuege pruefen die Kontowaehrung. Weitere Profile bleiben separat.
[CAMT-Profil und Parser-Abnahme](../../../quality-assurance/bank-camt-parser-integrity-20261001.md).

## Zweiter Bankweg entfernt

INT-BANK-001 entfaellt; aktiver Speicher bleibt allein domain_erp. Nach
expliziter Entwicklungsfreigabe entfernt bank_legacy_retirement_20261001
beide alten domain_finance-Tabellen mitsamt Entwicklungsdaten. Kein Archiv,
keine zweite Zahlung, kein OP-Umschreiben. Die Migration verwendet kein
CASCADE und bricht bei unerwarteten Abhaengigkeiten ab.
[Retirement-Nachweis](../../../quality-assurance/bank-legacy-retirement-20261001.md).
