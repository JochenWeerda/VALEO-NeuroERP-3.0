---
title: L3 Dropdown-Leaf Gap-Inventur
type: reference
audience: [product, fachbereich, entwickler]
owner: Codex
status: repo-seitig-geschlossen
last_reviewed: 2026-08-22
version: 2.0.0
description: Live-Abgleich der L3-Dropdown-Untermenues gegen VALEO NeuroERP 3.0.
---

# L3 Dropdown-Leaf Gap-Inventur

## Ergebnis

Die erreichbaren Ribbon-Tabs, Dropdowns, Flyouts und Leaf-Masken wurden in der
aktiven RDP-Sitzung read-only geoeffnet. Alle dabei bestaetigten repo-seitigen
Funktionsgaps sind in `L3-DEEP-MASK-PARITY-020` geschlossen. Produktive
Summenabnahme, externe DMS-Verbindung und rollenbedingt nicht sichtbare L3-Leafs
bleiben Betriebs-/UAT-Gates, keine fehlenden Implementierungen.

Screenshots verbleiben wegen moeglicher Echtdaten ausschliesslich lokal unter
`C:\Users\Jochen\Pictures\L3-Capture-2026-08-22-dropdown-correct`.

## Methode und Evidenzgrenze

- Live-RDP am 22.08.2026; Ribbon-Y und Dropdown-Koordinaten wurden neu kalibriert.
- Jede Funktion wurde gegen Route, ScreenDefinition, API/Service und Tests geprueft.
- Fehlklick-, Leer- und Modal-Duplikatbilder gelten nicht als Funktionsbeleg.
- Nicht sichtbare lizenz- oder rollenabhaengige Menues werden nicht als vorhanden behauptet.

## Geschlossene Gaps

| Gap | L3-Funktion | VALEO-Umsetzung | Status |
|---|---|---|---|
| L3-GAP-CHARGEN-EDIT-019 | Chargen-Nummern bearbeiten | `produktion/chargen-bearbeiten`, tenant-sicheres Repository, Lief.-Charge/Anerkennungs-Nr., Auswahl-Freigabe mit Qualitaetsgate und Audit | geschlossen |
| L3-GAP-ARTKONTO-020 | Artikel-Konto / Druck | feste Berichte `article-account` und `article-account-print`, gleicher Run-/CSV-/Drilldown-Vertrag | geschlossen |
| L3-GAP-BONUS-021 | Bonus an Kunden/Artikelgruppen | `auswertungen/bonus-berechnung`, unveraenderbare Periodenlaeufe, Korrekturlauf und auditierter CSV-Export | geschlossen |
| L3-GAP-DUENG-MENGEN-022 | Duengemittelmengen | `auswertungen/duengemittelmengen`, kanonische N/P2O5/K2O-Feldbuchwerte, Tenant-/Jahr-/Kunden-/Schlagfilter | geschlossen |
| L3-GAP-EB-LS-023 | EB Lieferschein-Kontrolle | gespeicherte Worklist `abrechnung/eb-lieferschein-kontrolle` ueber zentraler Belegkontrolle | geschlossen |
| L3-GAP-AUDIT-HIST-024 | Aenderungshistorie | `auswertungen/aenderungshistorie` ueber tenantgebundener Audit-Trail-API | geschlossen |
| L3-GAP-DMS-FULLTEXT-025 | DMS-Volltextsuche | `auswertungen/dms-volltext`, lokale tenant-sichere Suche, Filter, Quellobjekt und extern gegatete Vorschau | geschlossen |
| L3-GAP-CHARGEN-AUSW-026 | Chargenregister/Bewertung/Verwendung | drei feste Report-Spezifikationen mit identischen Summen, CSV und Drilldown | geschlossen |
| L3-GAP-ART-AUSW-027 | Artikel-Spezialauswertungen | Chefauswertung, Verrechnungspreis, EK-Aenderungen, Aktionen, Bewegungen, Dispo, Suche/Biete, Getreide, MVO, Tagesjournal | geschlossen |
| L3-GAP-KUND-AUSW-028 | Kunden-Spezialauswertungen | Auftrag-Disposition, Angebot/Auftrag, Kunden-Artikel, Bescheinigungen und Praesente | geschlossen |
| L3-GAP-TERROR-SPLIT-029 | Terrorschutz Personal/Kunden | zwei native Scopes mit getrenntem, tenantgebundenem Pruefprotokoll | geschlossen |
| L3-GAP-BELEGCHECK-SUB-030 | Auftrags-/Lieferschein-Kontrolle | native gespeicherte Sichten ueber derselben zentralen Ausnahme-/Audit-Funktion | geschlossen |

## Weitere live bestaetigte Leafs

- Kasse: Kassen-Statistik und Kassen-Gutscheine sind vorhandenen POS-/TSE-Sichten zugeordnet.
- Fracht: Kunden-Frachten ist durch Frachtauftraege und Logistik-Auswertungen abgedeckt.
- Genossenschaften: Geschaeftsguthaben und Warenrueckverguetung bleiben im vorhandenen Genossenschafts-/Abrechnungsbereich.
- Nachhaltige Biomasse/Massenbilanz und IBAN-Pruefliste nutzen bestehende Compliance-/Finance-Funktionen; die EB-Kontrolle ist der L3-vertraute Einstieg.
- Die festen Berichtsspezifikationen decken 30 L3-Berichte ab; freie SQL-Ausfuehrung bleibt ausgeschlossen.

## Abnahme

- ScreenDefinition -> RenderPlan -> `useUniversalMaskRuntime` -> `UniversalMaskRenderer`
- Generator-Readiness fuer alle neuen Masken
- tenantgebundene APIs, Auditgrund fuer Freigabe/Korrektur/Export
- serverseitige Pagination und Virtualisierung fuer grosse Listen
- Backend-, Frontend-, Routing-, Architektur- und Doku-Gates laut Slice-Handoff
