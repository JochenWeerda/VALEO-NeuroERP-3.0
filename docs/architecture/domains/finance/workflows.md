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
