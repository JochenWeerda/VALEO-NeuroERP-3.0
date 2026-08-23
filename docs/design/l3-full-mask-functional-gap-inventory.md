---
title: L3-Vollinventur und funktionale Gap-Liste
type: reference
audience: [product, fachbereich, entwickler]
owner: Codex
status: verifiziert
last_reviewed: 2026-08-23
version: 1.4.0
description: Datenschutzkonformer Funktionsabgleich der erreichbaren L3-Masken gegen VALEO NeuroERP 3.0.
---

# L3-Vollinventur und funktionale Gap-Liste

## Ergebnis

Die read-only untersuchte L3-Installation zeigt in den zehn Ribbonbereichen
`Datei`, `Favoriten`, `Allgemein`, `Erfassung`, `Abrechnung`, `Lager`,
`Produktion`, `Auswertungen`, `Schnittstelle` und `Fenster` ein breites
Handels-ERP. Der Abgleich ergibt **keinen P0-Gap**. Die Ribbon-Icon-Erfassung
(19./21.08.2026) schloss P1–P3-Kernluecken repo-seitig. Die Dropdown-Leaf-
Tiefenpruefung (22.08.2026) ergaenzt **14 neue P2/P3-Gaps** fuer Spezialmasken
und Auswertungen — siehe
[`l3-dropdown-leaf-gap-inventory.md`](l3-dropdown-leaf-gap-inventory.md).
`L3-GAP-MDE-001`,
`L3-GAP-DOCRET-002`, `L3-GAP-BELEGCHECK-005`, `L3-GAP-PROD-003`,
`L3-GAP-INV-004` und `L3-GAP-BILLBATCH-006` sind repo-seitig geschlossen.
`L3-ROHWARE-002`, `L3-GAP-QUERY-008`, `L3-GAP-TEAMCAL-009`, `L3-GAP-MAIL-010`,
`L3-GAP-TANK-011`, `L3-GAP-REPORT-012`, `L3-GAP-RECENT-013` und
`L3-GAP-IFACE-014` sind ebenfalls repo-seitig geschlossen. Reale
Standard-/Unimet-Kundenformate, Zielmapping und Produktivpilot bleiben externe
Aktivierungs-Gates, nicht Funktionsluecken des Repositorys.

Die anschliessende Vollabnahme `L3-VISUAL-PARITY-AUDIT-031` hat den gesamten
lokalen Evidenzbestand (1.022 PNGs in acht Capture-Verzeichnissen) erneut
inventarisiert und alle 69 produktiven nativen ScreenDefinitions gegen das
tatsaechlich renderbare Meridian-Vokabular geprueft. Dabei gefundene zentrale
Vertragsdrift bei Floorplans, Context-Rails, Tabellenprofilen, Dichte und
Aktionsrisiken ist geschlossen. Es verbleibt kein weiterer aus den erreichbaren
Screenshots belegbarer repo-seitiger Funktions- oder zentraler GUI-Gap.

Die Kernkette von Kunde/Artikel ueber Angebot, Auftrag, Einkauf, Lieferschein,
Rechnung, offene Posten, Lagerbewegung, Kontrakt, Ernte und Waage ist in VALEO
bereits funktional vertreten. Diese vorhandenen Funktionen werden nicht als
Gap umetikettiert, nur weil Navigation oder Feldanordnung in L3 anders ist.

## Methode und Evidenzgrenzen

- Erfassung am 19.08.2026 in der bereits angemeldeten Remote-Desktop-Sitzung,
  ausschliesslich lesend; keine Speicherung, Buchung, Freigabe oder Loeschung.
- Die Ausgangsinventur wertete 10 Haupt-Ribbonbilder, 37 Dropdown-Zustaende,
  8 Referenzaufnahmen und 53 Einstiegspfade aus. Die Vollabnahme vom 23.08.
  zaehlte darueber hinaus 1.022 lokale PNGs: 373 Vollmasken, 216
  Dropdown-/Leaf-Aufnahmen und 433 fruehere Referenz-/Navigationsbilder. Reine
  Menuezustaende, Fehlklicks, lizenzbedingte Fehler und visuelle Duplikate
  zaehlen weiterhin nicht als eigenstaendige Fachmaske.
- Lokaler Belegbestand:
  `C:\Users\Jochen\Pictures\L3-Capture-2026-08-19`. Er ist absichtlich nicht
  versioniert, weil einzelne Bilder Personen-, Kunden- oder Belegdaten zeigen.
- Eine Funktion gilt nur dann als vorhanden, wenn eine aktuelle VALEO-Seite,
  API oder kanonische Lieferdokumentation gefunden wurde. Archivdateien und
  generierte Handbuecher sind keine alleinige Positiv-Evidenz.
- `teilweise` bedeutet: Kernfaehigkeit vorhanden, aber ein im L3-Bild
  sichtbarer Arbeitsablauf oder eine operatorgeeignete Oberflaeche fehlt.
- Rollen-, Lizenz- und Mandantenvarianten sowie tiefere Untermenues einzelner
  Berichte konnten read-only teilweise nur ueber Menuebezeichnungen erfasst
  werden. Daraus werden keine unbelegten Detailanforderungen abgeleitet.

## Abdeckung nach Arbeitsbereich

| L3-Arbeitsbereich | In VALEO nachgewiesen | Bewertung | Gap |
|---|---|---:|---|
| CRM, Kunden, Lieferanten, Artikel, Nachrichten, Wiedervorlage | CRM-360, Stammdaten-, Aktivitaets-, Kontakt-, Lead- und Wiedervorlage-Seiten/APIs | vorhanden | - |
| Kalender und Teamkalender | native Teamansicht mit Membership-Pruefung, Frei/Belegt-Redaktion, Vorschlaegen und optionalen Ablehnungen | vorhanden | L3-GAP-TEAMCAL-009 geschlossen |
| Eingebettete E-Mail und letzte Dokumente | nativer Rollen-Mailarbeitsplatz und persoenliche, rollenaktuelle Dokumenthistorie vorhanden | vorhanden | L3-GAP-MAIL-010 und L3-GAP-RECENT-013 geschlossen |
| Angebote, Auftraege, Disposition, Lieferscheine, Faktura | Verkaufsseiten, Belegkette, unerledigte Positionen und Auftrag-Lieferschein-Abgleich | vorhanden | - |
| Bestellung, Wareneingang, Einkaufslieferschein/-rechnung | Einkaufsseiten, Bestellvorschlag, Rechnungspruefung und Wareneingangsabgleich | vorhanden | - |
| Kontrakte, Strecke, Ernte/Annahme, NaWaRo | Kontrakt-Lifecycle, Disposition, Abrechnung, Ernteannahme und NaWaRo-Funktionen | vorhanden | - |
| Rechnungsein/-ausgang, OP, FIBU-Uebergabe | Finance/AP/AR, offene Posten, e-Rechnung und FIBU-Schnittstellencenter | vorhanden | - |
| Rechnungstapel und Selbstabrechner | native Vier-Augen-Worklist ueber Faktura-, AP/AR- und Self-Billing-Quellbelegen mit Fehler-Retry | vorhanden | L3-GAP-BILLBATCH-006 geschlossen |
| Bestand, Vortrag, Korrektur, Lager-zu-Lager | Bestands-, Korrektur-, Bewegungs- und Bewertungsseiten/APIs | vorhanden | - |
| Fremdware/Fremdbestand | native tenant-/eigentuemersichere Worklist ueber Fremdwaren-Einlagerung mit Audit, Umbuchung und Abschluss | vorhanden | L3-ROHWARE-002 geschlossen |
| Inventur | Inventur, PIV, Differenzbuchung plus hashgebundene Nebenlaeufe, Bewertung und Vier-Augen-Bestandsvortrag | vorhanden | L3-GAP-INV-004 geschlossen |
| Ruest-/Kommissionierliste | FEFO-Kommissionierung und dokumentierter Ruestlisten-Lifecycle | vorhanden | - |
| Produktionsliste, Artikel-Umbuchung, Stapelbuchung, Muehle, Nachbearbeitung | nativer Leitstand als Projektion der Mischfutter-, Bewegungs- und Operationsquellen mit Audit | vorhanden | L3-GAP-PROD-003 geschlossen |
| Abfrage-Center | native Allowlist-Worklist ueber freigegebenen Read Models mit Vorschau, Favoriten und signiertem Austausch | vorhanden | L3-GAP-QUERY-008 geschlossen |
| Beleg-Kontrolle | native Ausnahme-Worklist mit vier Belegarten, Verantwortlichkeit, Audit und Deep-Link | vorhanden | L3-GAP-BELEGCHECK-005 geschlossen |
| Dokumenten-Ruecklauf | native Worklist mit Versand-/Ruecklaufstatus, Vorschau-Metadaten, Schlagworten, Audit und Ursprungsbeleg | vorhanden | L3-GAP-DOCRET-002 geschlossen |
| Kunden-, Lieferanten-, Artikel-, Lager-, Ernte-, Vertreter- und Streckenberichte | fester, tenantgebundener Berichtskatalog mit Summen, CSV und Beleg-Drilldown | vorhanden | L3-GAP-REPORT-012 geschlossen |
| Fuhrpark | Fahrzeugakte inkl. Technik, Fahrer, Wirtschaft, Termine, km, Reifen, Unfall, Schaden und Wartung | vorhanden | - |
| Waage/Hofliste | Hofliste, Erst-/Zweitwiegung, Wiegescheine, Vorlagen, Gosse und Waagenreferenz | vorhanden | externes Hardware-Gate |
| MDE-Uebernahme/Verarbeitung | nativer Eingangskorb, idempotente Mobile-Sync-Queue, Vorvalidierung, Quarantaene und Retry-Audit | vorhanden | L3-GAP-MDE-001 geschlossen |
| Tankanlage | idempotenter Adaptereingang, Fehlerkorb, Zapfungsuebernahme und regelbasierter Sales-Outbox-Handover | vorhanden | L3-GAP-TANK-011 geschlossen |
| Standard-Schnittstelle/Unimet | versionierte Profile, idempotenter Eingang, Quarantaene, Dry-run-Staging, Reconciliation und Monitor vorhanden | repo-seitig vorhanden; Aktivierung extern | L3-GAP-IFACE-014 geschlossen |

## Priorisierte funktionale Gaps

### P1 - vor einem breiten L3-Wechsel schliessen

| ID | Gap | Belegter Ist-Stand | Abnahmekriterium |
|---|---|---|---|
| L3-GAP-PROD-003 | Allgemeiner Produktionsleitstand ist nur teilweise vorhanden | Mischfutter-Produktion deckt Auftrag, Rezeptur, Charge und Status ab | Produktionsliste mit Druck, allgemeine Artikel-Umbuchung, Stapelbuchung und Nachbearbeitung als auditierte Lifecycles; L3-Muehlenfall als Referenzjourney — **repo-seitig geschlossen 2026-08-21** (`L3-PRODUCTION-CONTROL-006`; Anlagenpilot extern) |
| L3-GAP-INV-004 | L3-Inventur-Nebenablaeufe fehlen | Grundinventur, PIV, Zaehlen, Abschluss, Differenz und Bewertung sind vorhanden | Zaehllistendruck, kontrollierter Export/Import, Kontrolllauf, vorlaeufige Bewertung und erzeugbare Bestandsvortraege mit Vier-Augen-/Auditregeln — **repo-seitig geschlossen 2026-08-21** (`L3-INVENTORY-AUX-007`) |
| L3-GAP-BELEGCHECK-005 | Einheitlicher Beleg-Kontrollarbeitsplatz fehlt | Einzelne Kontrollen existieren fuer Wareneingang, Auftragspositionen und Auftrag/Lieferschein | Gemeinsame Ausnahme-Worklist fuer unerledigte Bestellungen, fehlende Eingangsbelege, gesperrte/nicht fakturierte Lieferscheine; Filter, Verantwortlicher, Faelligkeit, Deep-Link — **repo-seitig geschlossen 2026-08-21** (`L3-BELEGCHECK-WORKLIST-005`; Live-Projektion `L3-BELEGCHECK-PROJECTION-016`) |
| L3-GAP-BILLBATCH-006 | Rechnungstapel/Selbstabrechner sind nicht als kompletter Bedienablauf belegt | Faktura-, AP/AR- und Abrechnungsbausteine existieren | Stapel anlegen/pruefen/freigeben/wiederholen; Selbstabrechner fuer Verkauf und Kunden-Zukauf; Fehlerzeile und Belegnachweis — **repo-seitig geschlossen 2026-08-21** (`L3-BILLING-BATCH-008`) |

### P2 - hohe Produktivitaets- oder Fachparitaet

| ID | Gap | Belegter Ist-Stand | Abnahmekriterium |
|---|---|---|---|
| L3-ROHWARE-002 | Fremdware besitzt keine nachgewiesene geschlossene Operator-UI | Backend fuer Fremdwaren-Einlagerung und Bestandsanteile vorhanden | Worklist fuer Einlagerung, automatische Umbuchung, Fremdbestand je Lager, erledigte Faelle und Druck; Mandant/Eigentuemer stets sichtbar — **repo-seitig geschlossen 2026-08-21** (`L3-ROHWARE-OPERATOR-009`; Lager-/Druckpilot extern) |
| L3-GAP-QUERY-008 | Anwender-Abfrage-Center fehlt | Vorgegebene Reports/Dashboards vorhanden | Berechtigter Query-Designer ueber freigegebene Read Models, Vorschau, Ausgabe/Druck, Favoriten und signierter Import/Export ohne beliebiges SQL — **repo-seitig geschlossen 2026-08-21** (`L3-QUERY-CENTER-010`) |
| L3-GAP-TEAMCAL-009 | Teamkalender-Paritaet ist nicht belegt | Planungskalender aggregiert Prozesslayer und bietet ICS | Mehrbenutzer-/Teamansicht, Frei/Belegt, fremde und abgelehnte Termine, Rechte- und Datenschutzmodell — **repo-seitig geschlossen 2026-08-21** (`L3-TEAM-CALENDAR-011`; IAM-/Datenschutzpilot extern) |
| L3-GAP-MAIL-010 | Integrierter ERP-Mailarbeitsplatz fehlt | Dokumente und Kommunikationsaktivitaeten koennen abgelegt werden | Rollenbasierter Posteingang, Beleg-/Kontaktzuordnung, Anlagenuebernahme, Entwurf/Senden, revisionssichere Aktivitaet; alternativ verbindlicher externer Mail-Deep-Link — **repo-seitig geschlossen 2026-08-21** (`L3-MAIL-WORKSPACE-012`; Provider/Virenscan extern) |
| L3-GAP-TANK-011 | Tankanlagen-Schnittstellenworkflow ist nur teilweise vorhanden | Zapfungen und Tankbestand mit UI/API vorhanden | Adapter-Eingang mit idempotenter Uebernahme, Fehlerkorb, Einzelnachweis und regelbasierter Lieferscheinerzeugung — **repo-seitig geschlossen 2026-08-21** (`L3-TANK-ADAPTER-013`; Anlagen-/Sales-Consumer-Pilot extern) |
| L3-GAP-REPORT-012 | Exakte L3-Berichtskatalog-Paritaet ist nicht nachgewiesen | allgemeine Umsatz-, Lager-, Finance-, Einkauf- und Dashboardberichte vorhanden | Fachlich priorisierter Berichtskatalog mit Parameter-/Summenparitaet fuer Vertreter, Kunde/Artikel/-gruppe, Charge, Ernte und Strecke; Export und Beleg-Drilldown — **repo-seitig geschlossen 2026-08-21** (`L3-REPORT-CATALOG-014`; Echtdaten-Summen-UAT extern) |

### P3 - Gewohnheit und Komfort

| ID | Gap | Abnahmekriterium |
|---|---|---|
| L3-GAP-RECENT-013 | Bereichsuebergreifende Liste „Letzte Dokumente“ fehlt | Personenbezogene, berechtigte Historie mit Dokumenttyp, Nummer, Partner, Zeitpunkt und Deep-Link; keine globale Datenpreisgabe — **repo-seitig geschlossen 2026-08-21** (`L3-RECENT-DOCUMENTS-015`) |
| L3-GAP-IFACE-014 | L3-spezifische Standard-/Unimet-Adapter fehlen oder sind nicht belegt | Erst nach Kundenentscheidung: Formatvertrag, Mapping, Idempotenz, Fehlerkorb, Reconciliation und Betriebsmonitor je benoetigtem Adapter — **repo-seitig geschlossen 2026-08-21** (`L3-LEGACY-INTERFACES-017`); reale Formatmuster, Zielmapping und Produktivaktivierung extern |

### P2/P3 — neu aus Dropdown-Leaf-Inventur (22.08.2026)

| ID | Prioritaet | Gap | Kurz-Ist | Abnahme (Auszug) |
|---|---|---|---|---|
| L3-GAP-CHARGEN-EDIT-019 | P2 | Chargen-Nummern bearbeiten | Operator-Maske, Metadaten, Massenfreigabe und Audit | **geschlossen** |
| L3-GAP-ARTKONTO-020 | P2 | Artikel-Konto / Druck | fester Run-/CSV-/Drilldown-Bericht | **geschlossen** |
| L3-GAP-BONUS-021 | P2 | Bonus-Berechnung | unveraenderliche Laeufe, Korrektur und Export | **geschlossen** |
| L3-GAP-DUENG-MENGEN-022 | P2 | Duengemittelmengen | N/P2O5/K2O-Auswertung | **geschlossen** |
| L3-GAP-EB-LS-023 | P2 | EB Lieferschein-Kontrolle | gespeicherte zentrale Worklist | **geschlossen** |
| L3-GAP-AUDIT-HIST-024 | P2 | Aenderungshistorie | einheitliche Audit-Trail-Maske | **geschlossen** |
| L3-GAP-CHARGEN-AUSW-026 | P2 | Chargen-Lager-Auswertungen | drei feste Paritaetsberichte | **geschlossen** |
| L3-GAP-ART-AUSW-027 | P2 | Artikel-Weitere-Auswertungen | elf feste Spezialberichte | **geschlossen** |
| L3-GAP-DMS-FULLTEXT-025 | P3 | DMS-Volltext Auswertung | tenant-sichere navigierbare Worklist | **geschlossen** |
| L3-GAP-TERROR-SPLIT-029 | P3 | Terrorschutz Personal/Kunden | getrennte Scopes/Protokolle | **geschlossen** |
| L3-GAP-BELEGCHECK-SUB-030 | P3 | Belegkontrolle-Submasken | drei gespeicherte Sichten | **geschlossen** |
| L3-GAP-KUND-AUSW-028 | P3 | Kunden-Weitere-Auswertungen | fuenf feste Spezialberichte | **geschlossen** |

Details, Leaf-Katalog und Evidenzgrenzen:
[`l3-dropdown-leaf-gap-inventory.md`](l3-dropdown-leaf-gap-inventory.md).

## Kein Gap beziehungsweise bereits abgedeckt

Folgende im L3-Menue sichtbaren Schwerpunkte sind im aktuellen Bestand
ausreichend belegt: Kunden-/Lieferanten-/Artikelstamm, CRM und Wiedervorlage,
Angebot/Auftrag, Bestellvorschlag, Ein- und Verkaufslieferschein,
Rechnungsein/-ausgang, offene Posten, Kontrakte und Disposition,
Streckengeschaeft, Ernteannahme und NaWaRo, Lagerbestand/Korrektur/Umbuchung,
permanente Inventur, Kommissionierung/Ruestliste, Chargenrueckverfolgung,
Fuhrpark, Dashboard, Sanktionspruefung sowie Waage/Hofliste und
Doppelwiegung. Die vorhandene technische Gewohnheitsbruecke fuer dichte
Desktopmasken ist separat in
[`l3-to-meridian-habit-parity.md`](l3-to-meridian-habit-parity.md)
dokumentiert.

## VALEO-Evidenz (Auswahl)

- Fuhrpark: `app/api/v1/endpoints/fuhrpark.py` und
  `packages/frontend-web/src/pages/fuhrpark/fahrzeug-stamm.tsx`
- Inventur: `packages/frontend-web/src/pages/lager/inventur.tsx`,
  `packages/frontend-web/src/pages/lager/permanente-inventur.tsx` und
  `app/api/v1/endpoints/inventur_piv.py`
- Produktion: `packages/frontend-web/src/pages/produktion/mischfutter-produktion.tsx`
  und `packages/frontend-web/src/pages/produktion/rezepturgruppen.tsx`
- Ruestliste/Kommissionierung:
  `packages/frontend-web/src/pages/lager/kommissionierung.tsx`
- Planungskalender: `app/api/v1/endpoints/planung_kalender.py` und
  `packages/frontend-web/src/pages/planung/kalender.tsx`
- Tankstelle: `app/api/v1/endpoints/tankstelle.py` und
  `packages/frontend-web/src/pages/tankstelle/zapfungen.tsx`
- Waage: `packages/frontend-web/src/pages/waage/hofliste.tsx`,
  `wiegungen.tsx` und `wiegeschein-detail.tsx`
- Lieferstand frueherer L3-Slices:
  [`open-gaps-and-known-issues.md`](../project-context/open-gaps-and-known-issues.md)
  Abschnitt „L3 API Migration“.

## Externe Rollout-Gates

Diese Punkte sind keine pauschalen Code-Gaps und muessen getrennt behandelt
werden:

1. reale Waagen-, Tankanlagen-, MDE-, Mail- und Finanzsysteme samt Treibern,
   Zugangsdaten und Herstellervertraegen;
2. kundenspezifische Druckformulare und Berichtssummen;
3. Rollen-/Berechtigungsmatrix fuer sensible Team-, Mail- und Query-Funktionen;
4. Datenmigration und Reconciliation offener Belege, Kontrakte und Bestaende;
5. Pilotabnahme durch erfahrene L3-Anwender an 1366-, 1440- und 1920-Pixel-
   Arbeitsplaetzen.

## Empfohlene Umsetzungsreihenfolge

1. MDE und Dokumentenruecklauf, weil sonst operative Eingangsdaten und
   Nachverfolgung ausserhalb des ERP verbleiben.
2. Produktions-, Inventur- und Belegkontroll-Worklists, weil sie den
   Tagesabschluss und die Bestands-/Belegqualitaet sichern.
3. Rechnungstapel/Selbstabrechner und Fremdware fuer die fachliche
   End-to-End-Paritaet.
4. Teamkalender, Mail, Tankadapter und priorisierte Reports.
5. Abfrage-Center und Komfortfunktionen erst mit freigegebenen Read Models und
   belastbarem Berechtigungskonzept.
