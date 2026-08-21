---
title: L3-Delta-Inventur 2026-08-21
type: reference
audience: [product, fachbereich, entwickler]
owner: Cursor Agent
status: verifiziert
last_reviewed: 2026-08-21
version: 1.0.0
description: Live-Delta der L3-/zvoove-Ribbonmasken gegen die Vollinventur vom 19.08.2026 und VALEO NeuroERP.
---

# L3-Delta-Inventur 2026-08-21

## Ergebnis

Live-Erfassung der angemeldeten Remote-Desktop-Sitzung (`10.200.1.3`, L3/zvoove
**Version 26.07.01 - FB**). Die zehn Ribbonbereiche sind unverändert. Es gibt
**keinen neuen P0-Gap** und **keinen neuen Ribbon-Hauptbereich**. Die Gap-Liste
aus [`l3-full-mask-functional-gap-inventory.md`](l3-full-mask-functional-gap-inventory.md)
bleibt bestätigt; `L3-GAP-MDE-001` ist inzwischen repo-seitig geschlossen
(`L3-MDE-INBOX-003`). Nach Abschluss von Dokumentenruecklauf und Belegkontrolle
sind nach dem Rechnungstapel alle P1-Gaps repo-seitig geschlossen. Neu sind nur Feindetails aus
dem DATEI-Hauptmodul-Menü und schärfere Ribbon-Listen.

## Methode

- Read-only: Ribbon-Tabs per RDP-Fensterklick, Screenshots lokal unter
  `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-delta` (nicht in Git).
- Keine Speicherung, Buchung, Freigabe oder Löschung in L3.
- Abgleich gegen die Inventur vom 19.08.2026 und aktuelle VALEO-Routen/APIs.
- Echtdaten (Kunden, Belege) werden hier nicht zitiert.

## Ribbon-Bestand 2026-08-21 (live)

| Ribbon | Sichtbare Einstiege | Delta zu 19.08. |
|---|---|---|
| DATEI | Hauptmodule inkl. CRM, Dokumente, Artikel-Stamm, Wiedervorlage, Preis-Tabelle, Aufträge, Bestellungen, Verkauf-/Einkauf-Lieferschein, Lager-Bestand, Nachrichten, Fakturierung, Einkauf-Rechnung, Rechnungsausgangs-/eingangsbuch; Sidebar Schnellsuche/Stammdaten/Einstellungen | Feindetail Hauptmodule + Shortcuts ergänzt |
| FAVORITEN | Kunden-Artikel, Verkauf-Lieferschein, Artikel-Stamm, Artikel-Konto, CRM Dashboard, Abfrage-Center | unverändert |
| ALLGEMEIN | CRM, Ang./Auftr., Einkauf-Verw., Strecken, Kontrakte, Weitere; Kunden, Artikel; Nachrichten, Wiedervorlage, Kalender, Team Kalender, E-Mail, Dokumente, Letzte Dokumente | unverändert |
| ERFASSUNG | Kontrakt; Bestellung/Lieferschein/Rechnung (Einkauf); Ernte (Zukauf); Angebot/Auftrag/Lieferschein/Dokumente (Verkauf); Fuhrpark, Strecke | unverändert |
| ABRECHNUNG | Einkauf/Verkauf (Faktur); Rechnungseingang, Rechnungsausgang, Offene Posten; Abschluss | unverändert |
| LAGER | Bestand; Vortrag, Korrektur, Lager zu Lager; Fremdware, Inventur | unverändert |
| PRODUKTION | Produktionsliste; Rüstliste, Produktion; Mühle, Nachbearbeitung | unverändert |
| AUSWERTUNGEN | Abfrage-Center; Beleg-Kontrolle, Dokumenten-Rücklauf; Kunden, Lieferant, Artikel, Lager, Ernte, Vertreter, Strecke, Weitere; Dashboard | unverändert |
| SCHNITTSTELLE | Waage, MDE, Tankanlage, Standard-Schnittstelle; Rechnungen | unverändert |
| FENSTER | Fensterverwaltung (nicht vertieft) | unverändert |

## Gap-Status (Delta)

| ID | Priorität | Live 21.08. | Bewertung |
|---|---|---|---|
| L3-GAP-MDE-001 | P1 | SCHNITTSTELLE → MDE sichtbar | repo-seitig geschlossen (`L3-MDE-INBOX-003`); L3-Menü bleibt Referenz, Geräte-Pilot extern |
| L3-GAP-DOCRET-002 | P1 | AUSWERTUNGEN → Dokumenten-Rücklauf | repo-seitig geschlossen (`L3-DOCRET-INBOX-004`) |
| L3-GAP-PROD-003 | P1 | PRODUKTION → Liste/Mühle/Nachbearbeitung | repo-seitig geschlossen (`L3-PRODUCTION-CONTROL-006`) |
| L3-GAP-INV-004 | P1 | LAGER → Inventur (+ Vortrag/Korrektur) | repo-seitig geschlossen (`L3-INVENTORY-AUX-007`) |
| L3-GAP-BELEGCHECK-005 | P1 | AUSWERTUNGEN → Beleg-Kontrolle | repo-seitig geschlossen (`L3-BELEGCHECK-WORKLIST-005`) |
| L3-GAP-BILLBATCH-006 | P1 | ABRECHNUNG Faktur/Abschluss | repo-seitig geschlossen (`L3-BILLING-BATCH-008`) |
| L3-ROHWARE-002 | P2 | LAGER → Fremdware | weiter offen (Operator-UI) |
| L3-GAP-QUERY-008 | P2 | Favoriten/Auswertungen → Abfrage-Center | weiter offen |
| L3-GAP-TEAMCAL-009 | P2 | ALLGEMEIN → Team Kalender | weiter teilweise |
| L3-GAP-MAIL-010 | P2 | ALLGEMEIN → E-Mail | weiter offen |
| L3-GAP-TANK-011 | P2 | SCHNITTSTELLE → Tankanlage | weiter teilweise |
| L3-GAP-REPORT-012 | P2 | Auswertungsgruppen Kunden…Strecke | weiter teilweise |
| L3-GAP-RECENT-013 | P3 | Letzte Dokumente | weiter offen |
| L3-GAP-IFACE-014 | P3 | Standard-Schnittstelle | repo-seitiger Adapterrahmen geschlossen (`L3-LEGACY-INTERFACES-017`); reale Formate/Aktivierung extern |

### Kein neuer Gap (nur Feindetail)

| L3-Einstieg | Hinweis |
|---|---|
| DATEI → Anzeige Preis-Tabelle (F4) | In VALEO Preis-/Kalkulationsbausteine vorhanden; kein neuer P1 |
| DATEI → Rechnungsausgangs-/eingangsbuch | In VALEO AP/AR und Belegübersichten vorhanden; Parität bei Buchansicht ggf. P2-Komfort, nicht neu priorisiert |
| FAVORITEN → Artikel-Konto | Artikelbewegungs-/Kontosichten in Lager/Verkauf teilweise vorhanden |

## Empfohlene Reihenfolge (unverändert)

1. MDE (`L3-MDE-INBOX-003`)
2. Produktion / Inventur-Nebenläufe
3. Rechnungstapel / Fremdware
4. Teamkalender, Mail, Tank, Reports, Abfrage-Center

## Evidenz

- Lokale Captures: `C:\Users\Jochen\Pictures\L3-Capture-2026-08-21-delta` (~139 PNGs)
- Referenzinventur: [`l3-full-mask-functional-gap-inventory.md`](l3-full-mask-functional-gap-inventory.md)
- Workboard: `L3-FULL-MASK-GAP-002` abgeschlossen; nächster Slice `L3-MDE-INBOX-003`
