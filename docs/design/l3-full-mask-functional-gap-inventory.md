---
title: L3-Vollinventur und funktionale Gap-Liste
type: reference
audience: [product, fachbereich, entwickler]
owner: Codex
status: verifiziert
last_reviewed: 2026-08-21
version: 1.2.0
description: Datenschutzkonformer Funktionsabgleich der erreichbaren L3-Masken gegen VALEO NeuroERP 3.0.
---

# L3-Vollinventur und funktionale Gap-Liste

## Ergebnis

Die read-only untersuchte L3-Installation zeigt in den zehn Ribbonbereichen
`Datei`, `Favoriten`, `Allgemein`, `Erfassung`, `Abrechnung`, `Lager`,
`Produktion`, `Auswertungen`, `Schnittstelle` und `Fenster` ein breites
Handels-ERP. Der Abgleich ergibt **keinen neu nachgewiesenen P0-Gap**, aber
**zwei offene P1-, sechs P2- und zwei P3-Gaps**. `L3-GAP-MDE-001`,
`L3-GAP-DOCRET-002`, `L3-GAP-BELEGCHECK-005` und `L3-GAP-PROD-003` wurden
repo-seitig geschlossen. Die groessten verbleibenden
Wechselrisiken liegen nicht in den Kernbelegen, sondern in allgemeiner
Produktion, Inventur-Nebenlaeufen und L3-spezifischen
Ausnahme-Worklists.

Die Kernkette von Kunde/Artikel ueber Angebot, Auftrag, Einkauf, Lieferschein,
Rechnung, offene Posten, Lagerbewegung, Kontrakt, Ernte und Waage ist in VALEO
bereits funktional vertreten. Diese vorhandenen Funktionen werden nicht als
Gap umetikettiert, nur weil Navigation oder Feldanordnung in L3 anders ist.

## Methode und Evidenzgrenzen

- Erfassung am 19.08.2026 in der bereits angemeldeten Remote-Desktop-Sitzung,
  ausschliesslich lesend; keine Speicherung, Buchung, Freigabe oder Loeschung.
- 10 Haupt-Ribbonbilder, 37 Dropdown-Zustaende und 8 vorhandene
  Referenzaufnahmen wurden ausgewertet. Zusaetzlich wurden 53 Einstiegspfade
  geprueft. Reine Menuezustaende, lizenzbedingte Fehler und visuelle Duplikate
  zaehlen nicht als eigenstaendige Fachmaske.
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
| Kalender und Teamkalender | projizierter Planungskalender mit Layern, Vorschlaegen, Bestaetigen/Verwerfen und ICS | teilweise | L3-GAP-TEAMCAL-009 |
| Eingebettete E-Mail und letzte Dokumente | Dokumentablage und CRM-Kommunikation vorhanden | teilweise | L3-GAP-MAIL-010, L3-GAP-RECENT-013 |
| Angebote, Auftraege, Disposition, Lieferscheine, Faktura | Verkaufsseiten, Belegkette, unerledigte Positionen und Auftrag-Lieferschein-Abgleich | vorhanden | - |
| Bestellung, Wareneingang, Einkaufslieferschein/-rechnung | Einkaufsseiten, Bestellvorschlag, Rechnungspruefung und Wareneingangsabgleich | vorhanden | - |
| Kontrakte, Strecke, Ernte/Annahme, NaWaRo | Kontrakt-Lifecycle, Disposition, Abrechnung, Ernteannahme und NaWaRo-Funktionen | vorhanden | - |
| Rechnungsein/-ausgang, OP, FIBU-Uebergabe | Finance/AP/AR, offene Posten, e-Rechnung und FIBU-Schnittstellencenter | vorhanden | - |
| Rechnungstapel und Selbstabrechner | Beleg- und Rechnungsgrundlage vorhanden; eigene L3-Worklists nicht nachgewiesen | teilweise | L3-GAP-BILLBATCH-006 |
| Bestand, Vortrag, Korrektur, Lager-zu-Lager | Bestands-, Korrektur-, Bewegungs- und Bewertungsseiten/APIs | vorhanden | - |
| Fremdware/Fremdbestand | Backend-CRUD fuer Fremdwaren-Einlagerung und Third-Party-Stock-Anteile | teilweise | L3-ROHWARE-002 |
| Inventur | Inventur, permanente Inventur, Zaehlen, Abschluss, Differenzliste und Bestandsbewertung | teilweise | L3-GAP-INV-004 |
| Ruest-/Kommissionierliste | FEFO-Kommissionierung und dokumentierter Ruestlisten-Lifecycle | vorhanden | - |
| Produktionsliste, Artikel-Umbuchung, Stapelbuchung, Muehle, Nachbearbeitung | nativer Leitstand als Projektion der Mischfutter-, Bewegungs- und Operationsquellen mit Audit | vorhanden | L3-GAP-PROD-003 geschlossen |
| Abfrage-Center | feste Reports und Dashboards vorhanden | fehlend | L3-GAP-QUERY-008 |
| Beleg-Kontrolle | native Ausnahme-Worklist mit vier Belegarten, Verantwortlichkeit, Audit und Deep-Link | vorhanden | L3-GAP-BELEGCHECK-005 geschlossen |
| Dokumenten-Ruecklauf | native Worklist mit Versand-/Ruecklaufstatus, Vorschau-Metadaten, Schlagworten, Audit und Ursprungsbeleg | vorhanden | L3-GAP-DOCRET-002 geschlossen |
| Kunden-, Lieferanten-, Artikel-, Lager-, Ernte-, Vertreter- und Streckenberichte | zentrale und domaenenspezifische Reports vorhanden | teilweise | L3-GAP-REPORT-012 |
| Fuhrpark | Fahrzeugakte inkl. Technik, Fahrer, Wirtschaft, Termine, km, Reifen, Unfall, Schaden und Wartung | vorhanden | - |
| Waage/Hofliste | Hofliste, Erst-/Zweitwiegung, Wiegescheine, Vorlagen, Gosse und Waagenreferenz | vorhanden | externes Hardware-Gate |
| MDE-Uebernahme/Verarbeitung | nativer Eingangskorb, idempotente Mobile-Sync-Queue, Vorvalidierung, Quarantaene und Retry-Audit | vorhanden | L3-GAP-MDE-001 geschlossen |
| Tankanlage | Zapfungen und Tankbestand vorhanden | teilweise | L3-GAP-TANK-011 |
| Standard-Schnittstelle/Unimet | generisches FIBU-Schnittstellencenter vorhanden; L3-spezifische Adapter nicht nachgewiesen | extern/teilweise | L3-GAP-IFACE-014 |

## Priorisierte funktionale Gaps

### P1 - vor einem breiten L3-Wechsel schliessen

| ID | Gap | Belegter Ist-Stand | Abnahmekriterium |
|---|---|---|---|
| L3-GAP-PROD-003 | Allgemeiner Produktionsleitstand ist nur teilweise vorhanden | Mischfutter-Produktion deckt Auftrag, Rezeptur, Charge und Status ab | Produktionsliste mit Druck, allgemeine Artikel-Umbuchung, Stapelbuchung und Nachbearbeitung als auditierte Lifecycles; L3-Muehlenfall als Referenzjourney — **repo-seitig geschlossen 2026-08-21** (`L3-PRODUCTION-CONTROL-006`; Anlagenpilot extern) |
| L3-GAP-INV-004 | L3-Inventur-Nebenablaeufe fehlen | Grundinventur, PIV, Zaehlen, Abschluss, Differenz und Bewertung sind vorhanden | Zaehllistendruck, kontrollierter Export/Import, Kontrolllauf, vorlaeufige Bewertung und erzeugbare Bestandsvortraege mit Vier-Augen-/Auditregeln |
| L3-GAP-BELEGCHECK-005 | Einheitlicher Beleg-Kontrollarbeitsplatz fehlt | Einzelne Kontrollen existieren fuer Wareneingang, Auftragspositionen und Auftrag/Lieferschein | Gemeinsame Ausnahme-Worklist fuer unerledigte Bestellungen, fehlende Eingangsbelege, gesperrte/nicht fakturierte Lieferscheine; Filter, Verantwortlicher, Faelligkeit, Deep-Link — **repo-seitig geschlossen 2026-08-21** (`L3-BELEGCHECK-WORKLIST-005`; Live-Projektion Folgeausbau) |
| L3-GAP-BILLBATCH-006 | Rechnungstapel/Selbstabrechner sind nicht als kompletter Bedienablauf belegt | Faktura-, AP/AR- und Abrechnungsbausteine existieren | Stapel anlegen/pruefen/freigeben/wiederholen; Selbstabrechner fuer Verkauf und Kunden-Zukauf; Fehlerzeile und Belegnachweis |

### P2 - hohe Produktivitaets- oder Fachparitaet

| ID | Gap | Belegter Ist-Stand | Abnahmekriterium |
|---|---|---|---|
| L3-ROHWARE-002 | Fremdware besitzt keine nachgewiesene geschlossene Operator-UI | Backend fuer Fremdwaren-Einlagerung und Bestandsanteile vorhanden | Worklist fuer Einlagerung, automatische Umbuchung, Fremdbestand je Lager, erledigte Faelle und Druck; Mandant/Eigentuemer stets sichtbar |
| L3-GAP-QUERY-008 | Anwender-Abfrage-Center fehlt | Vorgegebene Reports/Dashboards vorhanden | Berechtigter Query-Designer ueber freigegebene Read Models, Vorschau, Ausgabe/Druck, Favoriten und signierter Import/Export ohne beliebiges SQL |
| L3-GAP-TEAMCAL-009 | Teamkalender-Paritaet ist nicht belegt | Planungskalender aggregiert Prozesslayer und bietet ICS | Mehrbenutzer-/Teamansicht, Frei/Belegt, fremde und abgelehnte Termine, Rechte- und Datenschutzmodell |
| L3-GAP-MAIL-010 | Integrierter ERP-Mailarbeitsplatz fehlt | Dokumente und Kommunikationsaktivitaeten koennen abgelegt werden | Rollenbasierter Posteingang, Beleg-/Kontaktzuordnung, Anlagenuebernahme, Entwurf/Senden, revisionssichere Aktivitaet; alternativ verbindlicher externer Mail-Deep-Link |
| L3-GAP-TANK-011 | Tankanlagen-Schnittstellenworkflow ist nur teilweise vorhanden | Zapfungen und Tankbestand mit UI/API vorhanden | Adapter-Eingang mit idempotenter Uebernahme, Fehlerkorb, Einzelnachweis und regelbasierter Lieferscheinerzeugung |
| L3-GAP-REPORT-012 | Exakte L3-Berichtskatalog-Paritaet ist nicht nachgewiesen | allgemeine Umsatz-, Lager-, Finance-, Einkauf- und Dashboardberichte vorhanden | Fachlich priorisierter Berichtskatalog mit Parameter-/Summenparitaet fuer Vertreter, Kunde/Artikel/-gruppe, Charge, Ernte und Strecke; Export und Beleg-Drilldown |

### P3 - Gewohnheit und Komfort

| ID | Gap | Abnahmekriterium |
|---|---|---|
| L3-GAP-RECENT-013 | Bereichsuebergreifende Liste „Letzte Dokumente“ fehlt | Personenbezogene, berechtigte Historie mit Dokumenttyp, Nummer, Partner, Zeitpunkt und Deep-Link; keine globale Datenpreisgabe |
| L3-GAP-IFACE-014 | L3-spezifische Standard-/Unimet-Adapter fehlen oder sind nicht belegt | Erst nach Kundenentscheidung: Formatvertrag, Mapping, Idempotenz, Fehlerkorb, Reconciliation und Betriebsmonitor je benoetigtem Adapter |

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
