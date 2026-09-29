---
title: Anwender-Bedienwege — Touch, Sprache, Agent
type: reference
audience: [design, entwickler, agent, produkt]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-18
version: 1.0.0
description: IST/SOLL der produktiven Bedienung je Rolle — Finger, Stimme, CLI/MCP — ohne SAP-Kopie.
---

# Anwender-Bedienwege (Touch, Sprache, Agent)

Stand 2026-09-17. Gelesen im Browser auf 390×844 (Außendienst-Handy) und
gegen WCAG 2.2, SAP Fiori Mobile 2026 und Dynamics-365-MCP gehalten.
Kein SAP-Lookalike. KIM Object Page bleibt Claude. FSX, Auftrag, Rechnung
unangetastet.

## Was der Anwender braucht

| Rolle | Gerät | Alltag | Erster Weg |
|---|---|---|---|
| Außendienst | Handy / Tablet, oft eine Hand | Kunde finden, Aktivität, Angebot | Start → Handel → Kunden / Suche / Stimme |
| Annahme / Waage | Tablet, Handschuhe, Lärm | Queue, Kennzeichen, Wiegen | Start → Ernte → Warteschlange; große CTAs |
| Disposition | Desktop + gelegentlich Tablet | Bestand, Tour, Ausnahme | Start → Lager; Leitstand nur bei Störung |
| Buchhaltung | Desktop, Tastatur | OP, Beleg, Freigabe | Start → Finanzen; Kürzel bleiben |
| Leitung | Desktop | KPI, Ausnahme | Start-KPIs mit Drilldown, Leitstand |

## Stand der Technik (Recherche 2026)

- **WCAG 2.2 AA** verlangt 24×24 CSS-Pixel (SC 2.5.8). VALEO hält intern
  **44 px** (`--touch-target`, SC 2.5.5 AAA / iOS HIG). Das bleibt die
  operative Schwelle für Waage und Außendienst. Industrie-Waagen (resistive
  8"-Kiosks, Handschuhe) zielen eher auf 25–40 mm — VALEO 44 CSS-px ist die
  Web-Untergrenze, nicht die Handschuh-Obergrenze.
- **SAP Fiori** Mobile Mode 2026 und Joule Work (Voice, Early Access / GA
  H2 2026): Sprache ist ein Erstklass-Kanal, kein Desktop-Zusatz.
- **Dynamics 365 MCP** und Frihet (viele MCP-Tools): ein Agent steuert
  *dieselben* fachlichen Aktionen wie die UI, mit derselben Berechtigung —
  nicht das DOM.

## IST — was heute geht

### Touch

- Launchpad-Kacheln, Space-Reiter, Prozessraum, Schnellaktionen: 44 px
  (HOME-IA Sprint 1+2).
- Annahme-Warteschlange: Kopf-CTAs und Suche bereits `min-h-touch`;
  Zeilen-Aktionen nachgezogen.
- Kundenliste (`/verkauf/kunden-liste`): Werkzeugleiste und Kundenzelle
  nachgezogen; Name in `text-primary`, nicht Rohblau.
- **Vorher kaputt auf 390 px:** Top-Leiste quetschte Hamburger und Aufgaben
  auf 16 px Breite, Logo 32 px, Suche hieß „Suche... (Ctrl+K)“.
- Breadcrumb-Home war 14 px; jetzt 44×44, Label „Zur Startseite“.
- Kundenliste: Suche und Tabelle vor den KPI-Karten; Werkzeugleiste 44 px.
- Ernte-Annahme: Felder und Speichern waren 32 px; jetzt `min-h-touch`,
  Register 44 px, eine Spalte auf dem Handy, Lookup mit Namen.
- Aktivitäten: Suche vor den KPI-Karten; Zeile `text-primary`, 44 px;
  „Heute / Diese Woche / Überfällig“ filtern wirklich.
- Bestand: Drilldowns 44 px, Statusfarben über Tokens statt Roh-Orange.
- Offene Posten: Suche/Export/Bearbeiten 44 px; Rechnungslink nicht Rohblau.
- Waage-Liste: Suche und Liste zuerst (vorher y≈5800), Hofliste als CTA,
  Standort öffnet den Hof. Leitstand-Panels nur am Desktop.
- Hofliste: Arbeit zuerst, keine F-Tasten-Beschriftung auf Touch, 44 px.
- Prozessleitstand: 44-px-Aktualisieren/Filter/Detail/Replay, Statusfarben
  über Tokens, Filterwert `all` nicht mehr als API-Status.

### Sprache

- Feature-Flag `voiceControl` ist an (`public/flags.json`).
- Command Palette: Omnibox-Diktat (`VoiceBar`), Mikro 44 px, auf Touch ohne
  Alt+V und ohne Push-to-talk-Maus (sonst endet ein Tipp sofort).
- Maskenfelder: `VoiceBar` / Whisper-Host im Dashboard-Layout.
- **Vorher:** Mikrofon in der Top-Leiste `hidden sm:inline-flex` — auf dem
  Handy unsichtbar, also genau dort weg, wo Außendienst es braucht.
- Kein Hands-free-Dialog wie Joule Work; Polish/Ollama ist Best-Effort.

### Agent / CLI / MCP

Registry `MCP-ERP-TOOLS-001`: **18 Tools**, fast nur Lesen.
Schreiben mit Risiko: `crm.contact.log`, `sales.invoice.propose` (Human
Approval). Es gibt **kein** form-level MCP (kein „Feld X in Maske Y setzen“
wie Dynamics). Ein LLM-Agent kann also:

| Kann | Kann nicht |
|---|---|
| Kunden suchen, 360-Kurzlage, Waagenscheine listen, Auftrag-Status, Bestand, OP, DMS-Suche | Eine Maske feldweise ausfüllen |
| Rechnung *vorschlagen* (Freigabe Mensch) | Wiegen, Queue-Eintrag anlegen, SEPA auslösen |
| REST `/api/v1/...` mit Token + `X-Tenant-ID` | Die UI als Benutzer klicken (außer Browser-MCP des Entwicklers) |
| Agent-Handbuch + Tool-Referenz lesen | 157 generische ERP-Tools à la Frihet |

CLI-Einstieg für Menschen: Command Palette und `pnpm`/`pytest`-Scripts.
`scripts/mcp_server.py` ist ein Prompt-Relay, **kein** ERP-Operator.
DOM-Hook `data-mcp-action` an Suche und Sprache hilft Browser-Agenten,
ersetzt aber keine Fach-Tools.

## SOLL (Leitplanke, nicht alles in diesem Slice)

1. Jede produktive Erstaktion per Finger erreichbar, Ziel ≥ 44 px, kein
   Hover-only (WCAG 2.5.7).
2. Sprache auf jedem Gerät sichtbar, sobald `voiceControl` an ist.
3. Tastatur-Kürzel nur, wo eine Tastatur das primäre Gerät ist.
4. Agent: bestehende 18 Tools ehrlich lassen; neue Tools nur mit Scope,
   Audit und Human-Approval analog Invoice-Propose. Kein DOM-Steuern als
   Produktvertrag.

## In diesem Slice geschlossen

- Top-Leiste: 44 px, Suche ohne Ctrl+K, Mikrofon immer, Aufgaben im
  Benutzermenü auf Touch, Tastenkürzel-Panel und Hover-Modus auf schmalen
  Viewports aus.
- `useTouchDevice`: schmale Breite zählt, nicht nur `(pointer: coarse)`.
- Annahme-Warteschlange: Zeilen-CTAs `min-h-touch`.
- Kundenliste Verkauf: Touch-Werkzeugleiste, tappable Name.
- Ernte-Annahme-Erfassung: 32-px-Felder und Speichern auf 44 px, Lookups benannt.
- Aktivitäten, Bestandsübersicht, Offene Posten: Arbeit zuerst bzw. 44-px-CTAs.
- Waage-Liste und Hofliste: Arbeit vor DS-Leitstand; Touch ohne F-Kürzel-Copy.
- Prozessleitstand: Touch-Ziele und Statusfilter; interne Keys bleiben sichtbar
  (das ist die Leitungs-Sicht).
- ListReport: Import/Export/Neu, Suche und Zeilenaktionen `min-h-touch` / 44 px.
- Bestellungen-Liste: Arbeit zuerst, DS-Theater nur Desktop.
- Lieferschein-Erfassung Verkauf: Felder/Lookups/Speichern 44 px, Register 44 px,
  keine F11-Copy auf Touch, Waage statt Desktop-Connect-Text.
- Einkauf-Lieferschein (`/einkauf/lieferschein-erfassung`): als Wareneingang,
  44-px-Felder, Lookups (LS suchen/vorher/nächster, Niederlassung, Zwischenhändler)
  wirklich verdrahtet, eine Spalte auf dem Handy, Speichern 44 px, kein F11-Kürzel
  auf Touch, Header über `bg-primary` statt Rohgrün.
- Bestellung anlegen: Wizard-Schrittchips und `NativeSelect` auf `min-h-touch`
  (gilt für alle Wizard-Masken). Ask-VALEO-FAB auf Touch ausgeblendet, weil er
  „Weiter“ verdeckte; Ask VALEO bleibt in der Top-Leiste.
- Angebot (`/sales/angebot-erstellen`): 44-px-Felder, Suche/Vor/Zurück laden
  den Beleg (nicht nur die Kopfnummer), ein Tipp statt Doppelklick, DS-Theater
  nur Desktop, Speichern 44 px. MCP hat kein Angebots-Tool.
- Kundenstamm (`/verkauf/kunden-stamm`, `/verkauf/kunde/neu`): Register
  `variant="register"` 44 px, Operator-Reiter ohne „Tab 23/24/25“, Header
  wrappt Speichern/Zurück, Zeilen-Löschen pro Datensatz pending, Selects und
  Checkboxen 44 px. MCP: `crm.customer.search` / `summary360` / `crm.contact.log`
  — kein PATCH des Stamms.
- Copilot-FAB auf Touch ausgeblendet (deckte Formularfelder); Außendienst öffnet
  Copilot über das Benutzermenü (`open-copilot-dock`). Ask VALEO bleibt in der
  Top-Leiste (Desktop) bzw. Command Palette.
- Angebotsliste (`/sales/angebote-liste`): Arbeit zuerst (Suche, Status, Neu,
  Tabelle). Rollenfokus/DS-Theater nur Desktop. Nummernlink `text-primary` 44 px,
  Filterleiste wrappt, `AdvancedFilters`-Trigger 44 px (gilt für alle Listen mit
  dem Baustein). MCP hat kein Angebots-Listen-Tool.
- Wiegungen (`/waage/wiegungen`): Anlegen/Zuordnen/Suche vor Rollenfokus und
  KPI-Karten. Schließen 44 px, Status „offen/geschlossen“, kein F-Kürzel auf
  Touch. MCP listet Wiegescheine, legt keine an.
- Wiegeschein-Detail (`/waage/wiegeschein/:id`): Ticket und Gewichte zuerst,
  ARIA-Register 44 px statt Eigenbau-Reiter, DS-Theater und Tastaturleiste nur
  Desktop. Kontrakt zuordnen 44 px, bei Verbucht deaktiviert. MCP listet, holt
  und ordnet einzelne Tickets nicht zu.
- Annahme-Abrechnung (`/annahme/abrechnung`): Lieferdaten und Speichern zuerst,
  Korrekturen (Freigeben, Gutschrift, Belastung) 44 px und ein Tipp statt
  Doppelklick, Status „Entwurf/verbucht“, Tastaturleiste nur Desktop.
  MCP hat kein Settlement-Tool.
- Einkauf-Angebotsliste (`/einkauf/angebote-liste`): ListReport zuerst, DS-Theater
  nur Desktop, Angebotsnummer 44 px `text-primary`. MCP hat kein EK-Angebots-Tool.
- Buchungsvorlagen (`/finance/buchungsvorlagen`): Anwenden/Löschen/Filter 44 px,
  deutsche Kategorien, Löschen mit Nachfrage, „Neue Vorlage“ sagt ehrlich, dass
  Anlegen noch über die API geht. MCP hat kein Vorlagen-Tool.
- LKW-Registrierung (`/annahme/lkw-registrierung`): Wizard (Kennzeichen, Scan,
  Foto-Tipp statt nur Drag) zuerst, DS-Theater und F-Kürzel nur Desktop,
  Scan-Dialog 44 px, Statusfarben über Tokens. MCP legt keine Queue an.
- Qualitätsprüfung (`/annahme/qualitaets-check`): Wizard zuerst, Zur Abrechnung
  44 px, JSON-Prozessdump nur Desktop. MCP schreibt kein QS-Protokoll.
- Einlagerung / Auslagerung (`/lager/einlagerung`, `/lager/auslagerung`): Wizard
  zuerst, Fallkopf und Agent-Panel nur Desktop, Statusfarben über Tokens.
  MCP liest Bestand (`lager.bestand.get`), bucht keine Ein-/Auslagerung.
- LKW-Beladung (`/verladung/lkw-beladung`): Kennzeichen-Wizard zuerst, Theater
  nur Desktop. MCP hat kein Verlade-Schreibtool.
- Disposition (`/disposition/liste`): Tabelle und Bestellvorschläge-CTA zuerst,
  KPI-Karten nur Desktop. MCP hat kein Dispo-Tool.
- Verladungen (`/verladung/liste`, `/logistik/verladungen`): Suche und Tabelle
  zuerst, Neue Beladung 44 px, KPI-Karten nur Desktop. MCP hat kein Verlade-Tool.
- Inventur (`/lager/inventur`): Tabelle und Abschließen zuerst, 44-px-Auswahl
  und Storno je Zeile, Fallkopf nur Desktop. MCP liest `lager.inventur.status`,
  schließt keine Position und storniert nicht.
- Kontrakt-Übersicht (`/kontrakte`): Neu und Filter zuerst, Öffnen per Tipp
  (kein Doppelklick), Pager 44 px. MCP holt einen Kontrakt (`agrar.contract.get`),
  listet und legt keine an.
- Reklamationen (`/qualitaet/reklamationen`): Suche und Tabelle zuerst, Nummer
  44 px `text-primary`, Fallkopf nur Desktop. MCP hat kein Reklamations-Tool.
- Kontrakt-Detail (`/kontrakte/neu`, `/kontrakte/:id`): Operator-h1 statt
  Formularname, Speichern 44 px, Register 44 px, DS-Theater nur Desktop.
  MCP holt einen Kontrakt, speichert und storniert nicht.
- Rohware-Annahme (`/annahme/rohware`): Wizard zuerst (Lieferant, Ware,
  Qualität). MCP legt keine Annahme an.
- Reklamation-Detail (`/qualitaet/reklamation/:id`): Identität und Statuswechsel
  zuerst, Register 44 px. MCP hat kein Reklamations-Tool.
- Positionsmonitor (`/kontrakte/positionen`): Filter und Artikeltabelle zuerst,
  44-px-Checkboxen, Tipp statt Doppelklick. KPI-Theater nur Desktop.
  CIH/Sitagri-Mobile: Positionen und Alarme zuerst, nicht die KPI-Wand.
- Kontrakt-Alarme (`/kontrakte/alarme`): h1 und Zur Kontraktliste zuerst;
  Öffnen 44 px. MCP hat kein Alarm-Tool.
- Labor-Liste (`/qualitaet/labor-liste`): Suche und Tabelle zuerst, Auftrag
  44 px `text-primary`. MCP hat kein Labor-Tool.
- Lieferanten (`/einkauf/lieferanten-liste`): Suche vor KPI, Name 44 px.
- Rückverfolgbarkeit (`/lager/rueckverfolgbarkeit`): Wiegeschein-Picker 44 px,
  Stufen W/A/L/R ohne Hover-only. MCP kann Lot *lesen* (`wms.lot.trace`),
  sperrt und storniert die Kette nicht.
- Labor-Auftrag (`/qualitaet/labor-auftrag`): Wizard-Felder, Analysen und
  Laborwahl 44 px, Pending-Guard.
- GS1-Scanner (`/lager/gs1-scanner`): ARIA-Tabs statt Eigenbau-Reiter,
  44-px-Parsen/Kopieren. MCP hat kein GS1-Tool.
- Silo-Terminal (`/lager/silo-mobil`): Lot-Link und Transfer 48 px, QS-Status
  mit Label (nicht nur Farbe). MCP liest Zellen (`wms.cell.status`), bucht
  keine Transfers.
- Mengenzeiträume (`/kontrakte/mengenzeitraeume`): Laden/Anlegen/Löschen 44 px.
  MCP hat kein Staffel-Tool.
- Ernte-Liste (`/agrar/ernte/liste`): Suche vor KPI, Schlag 44 px.
- Aussaat-Liste (`/agrar/aussaat/liste`): Suche filtert, Export wirkt, Schlag 44 px.
- PSM-Liste (`/agrar/psm/liste`): Mittel 44 px `text-primary`.
- Schlagkartei (`/agrar/feldbuch/schlagkartei`): Schlagliste zuerst (MeinAcker-
  Mobil: Plot tippen), Theater/KPI nur Desktop, Name 44 px, Stilllegen
  beschriftet. MCP hat kein Schlag-Tool.
- Bodenproben (`/agrar/bodenproben`): Suche vor KPI, Schlag 44 px.
  MCP hat kein Bodenproben-Tool.
- Sortenregister (`/agrar/saatgut/sortenregister`): Suche und Sorte 44 px.
  MCP hat kein Saatgut-Tool.
- Saatgut-Liste (`/agrar/saatgut-liste`): ListReport zuerst, Anzeigen/Bearbeiten
  44 px mit Label. MCP hat kein Saatgut-Tool.
- Lagerplätze (`/lager/lagerplaetze`): WMS-Struktur zuerst, NativeSelect 44 px,
  Fach bearbeiten 44 px, Sperr-Checkbox 44 px. MCP liest Silozellen
  (`wms.cell.status`), patcht keine Fächer.
- Maßnahmen (`/agrar/feldbuch/massnahmen`): Liste und Spritztagebuch zuerst
  (FieldLog: tippen was gemacht wurde), Theater nur Desktop, Schlag 44 px,
  Löschen pro Datensatz. MCP hat kein Maßnahmen-Tool.
- Kulturpflanzen (`/agrar/kulturpflanzen`): Suche vor KPI, Kultur 44 px.
- Dünger (`/agrar/duenger-liste`): Filter zuerst, Name 44 px, Anzeigen/Bearbeiten
  beschriftet. MCP hat kein Dünger-Tool.
- Kunden-Schlagkartei (`/agrar/kunden-schlagkartei`): Lohnspritz/Mahl+Misch
  44 px, KPI nur Desktop. MCP legt keine Lohndienste an.
- PSM-Sachkunde (`/agrar/psm/sachkunde-register`): Ablauf-Warnung bleibt,
  Nachweise 44 px, KPI nur Desktop. MCP hat kein Sachkunde-Tool.
- PSM-Auflagen (`/agrar/psm/auflagen-manager`): Suche zuerst, Erledigt
  beschriftet. MCP hat kein Auflagen-Tool.
- Biostimulanzien (`/agrar/biostimulanzien-liste`): Anzeigen/Bearbeiten 44 px.
- Artikel (`/artikel`): Bezeichnung 44 px, Export wirkt, KPI nur Desktop.
- Lagerbewegungen (`/lager/lagerbewegungen`): Suche zuerst, Zugang/Abgang
  auf Deutsch, Bearbeiten/Löschen beschriftet. MCP hat kein Buchungs-Schreibtool.
- Düngemittel-Stamm (`/agrar/duenger/liste`): Name 44 px, Löschen pro Id.
- Chargen (`/charge/liste`): Chargen-ID 44 px, Export wirkt.
- Einzelfutter / Mischfutter: Suche filtert wirklich, Name 44 px.
- Zertifikate, Versicherungen, Projekte, Förderanträge, Schäden: 44 px,
  KPI/Theater nur Desktop. MCP hat keine Betriebs-Schreibtools.
- Schlag anlegen (`/agrar/feldbuch/schlag/neu`): Zurück beschriftet 44 px.
- Wetter (`/agrar/wetter/prognose`): Aktualisieren/Übernehmen 44 px.
- Wasserschutz (`/agrar/psm/wasserschutz`): Adresssuche 44 px.
- Düngermischungen (`/agrar/duenger/mischungen`): Nach oben/unten beschriftet.
- Zinsabrechnung, Vermehrungsverträge, Rohwarengruppen, Massebilanz:
  Buchen/Stornieren/Löschen/Festschreiben beschriftet 44 px.
- Service-Anfragen (`/service/anfragen`): Tickets und Suche zuerst,
  Theater nur Desktop, Neue Anfrage 44 px.
- Wareneingang (`/einkauf/wareneingang`): Buchungsformular zuerst,
  Theater nur Desktop, Abbrechen/Speichern 44 px.
- Klärung gesperrt (`/annahme/klaerung-gesperrt`): Queue und Entscheidung
  zuerst, Speichern 44 px. MCP hat kein Klärungs-Schreibtool.
- Retouren (`/einkauf/retouren`): Wareneingang wählen und buchen zuerst.
- Service-Rückmeldung: beschriftetes Zurück, NativeSelect Ergebnis.
- Feldservice: h1, Liste/Suche zuerst, Zeilenaktionen 44 px.
- Opportunities: ListReport zuerst.
- QS-Checkliste: offene Punkte und Tabelle zuerst; toter „Audit starten“
  führt auf QS-Ausnahmen.
- HRM-Betriebsfreigaben (`/personal/hrm-operations-gates`): Prüfliste zuerst,
  kein SAP-Blau, PDF über Browserdruck, Katalog-Stopper für neue Prüfpunkte.
- QM-Dokumente (`/document`): Upload und Suche zuerst, Scan/Löschen 44 px.
- Mischfutter-Produktion (`/produktion/mischfutter`): Wizard zuerst.
- Meldewesen-Konsole: Export/Import und Tabs zuerst, Theater nur Desktop.
- Monitoring-Regeln: Formulare zuerst, Loeschen 44 px mit Guard.
- Ablage (`/dokumente/ablage`): Export umgeht den Global-Intercept, Folgezeile
  nur Desktop. Download bleibt ein lokaler Metadaten-Text.
- KIM, Auftrag, Rechnung und Lieferschein: Schaltflächen 44 px, Struktur bleibt
  Claude. Register-Tabs zentral `min-h-touch`.
- ELSTER (`/fibu/elster-online`): Schritte zuerst, Theater nur Desktop.
  Sprache findet `elster-online`.
- Bankabgleich (`/finance/bank-abgleich`): ObjectPage zuerst, Theater nur
  Desktop. Sprache findet `bankabgleich`.

## Offen (ehrlich)

| Lücke | Rolle | Prio |
|---|---|---|
| Listen bleiben Tabellen; auf Handy horizontal scrollen statt Kartenstapel | Außendienst, Waage, Buchhaltung | geschlossen DataTable/ListReport/FastTable; KIM/FSX offen |
| Worklist list-detail blendet die FastTable-Liste auf 390 px aus (`display: none`) | Buchhaltung | geschlossen 2026-09-18: Liste zuerst, Detail nach Auswahl |
| Sprache steuert keine Waage-Schritte und keine Queue-Aktionen | Annahme | P2 |
| MCP deckt keine Masken-Mutation, kein „lege Annahme an“, kein Lieferschein speichern | Agent | P1 |
| KIM Object Page (Sprint 3) | Innendienst | Claude |
| Rollenfilter auf der Startseite | alle | HOME-IA Risiko |
| Einkauf-Lieferschein und weitere dichte Belegmasken | Einkauf / Vertrieb | geschlossen bis Listen-UIX; FSX/Auftrag/Rechnung Claude |
| Copilot-Dock bleibt nach Navigation offen (Schliessen 44 px) | alle Touch | geschlossen 2026-09-18 (schliesst bei pathname) |
| FSX, Auftrag, Rechnung, crm_360, KIM Object Page | Innendienst | Struktur bleibt Claude; size=sm am 2026-09-27 auf 44 px |

## Gelesene Seiten

1. `/` Start — Chrome, Launchpad
2. `/annahme/warteschlange` — Waage-Queue
3. `/verkauf/kunden-liste` — Außendienst
4. `/agrar/ernte-annahme-erfassung` — Waage-Erfassung
5. `/crm/aktivitaeten` — Außendienst-Tagebuch
6. `/lager/bestandsuebersicht` — Disposition
7. `/fibu/offene-posten` — Buchhaltung (Desktop-first bleibt zulässig, Touch nachgezogen)

8. `/waage/liste` — Waagenstamm (Annahme)
9. `/waage/hofliste` — offene Wiegescheine
10. `/workflow/leitstand` — Leitung
11. `/einkauf/bestellungen-liste` — Einkauf, Arbeit zuerst
12. `/sales/lieferungen-liste` — Versand-Belege (Auftrag-/Rechnungs-Editor unangetastet)
13. `/verkauf/lieferschein-erfassung` — Verkauf-Erfassung, Touch 44 px
14. `/einkauf/lieferschein-erfassung` — Wareneingang, Lookups + 44 px
15. `/einkauf/bestellung-anlegen` — Wizard-Schritte und NativeSelect 44 px
16. `/sales/angebot-erstellen` — Außendienst-Angebot, Touch 44 px
17. `/verkauf/kunde/neu` — Kundenstamm Außendienst, Register 44 px
18. `/sales/angebote-liste` — Außendienst-Angebote, Arbeit zuerst
19. `/waage/wiegungen` — Annahme/Waage, Anlegen zuerst
20. `/waage/wiegeschein/:id` — Wiegeschein-Detail, Gewichte zuerst
21. `/annahme/abrechnung` — Selbstabrechner, Arbeit zuerst, 44-px-Korrekturen
22. `/einkauf/angebote-liste` — Einkauf-Angebote, ListReport zuerst
23. `/finance/buchungsvorlagen` — Buchhaltung, Anwenden/Löschen 44 px
24. `/annahme/lkw-registrierung` — Waage-Check-in, Wizard zuerst
25. `/annahme/qualitaets-check` — QS-Wizard zuerst, Zur Abrechnung 44 px
26. `/lager/einlagerung` — Disposition Put-away, Wizard zuerst
27. `/lager/auslagerung` — Disposition Pick, Wizard zuerst
28. `/verladung/lkw-beladung` — Waage/Disposition Beladung
29. `/disposition/liste` — Dispo-Tabelle zuerst
30. `/verladung/liste` — Verladung-Arbeit zuerst
31. `/lager/inventur` — Zählung zuerst, kein KPI-Theater
32. `/kontrakte` — Kontrakte öffnen per Tipp, Pager 44 px
33. `/qualitaet/reklamationen` — QS-Beschwerden, Arbeit zuerst
34. `/kontrakte/neu` — Kontrakt-Detail, Speichern und Register 44 px
35. `/annahme/rohware` — Waage-Rohware, Wizard zuerst
36. `/qualitaet/reklamation/:id` — Reklamation-Akte, Status zuerst
37. `/kontrakte/positionen` — Exposure-Liste zuerst, 44-px-Filter
38. `/kontrakte/alarme` — Alarme öffnen, kein KPI-Theater
39. `/qualitaet/labor-liste` — Labor-Aufträge suchen und öffnen
40. `/einkauf/lieferanten-liste` — Einkauf-Lieferanten, Arbeit zuerst
41. `/lager/rueckverfolgbarkeit` — Wiegeschein-Kette, Picker zuerst
42. `/qualitaet/labor-auftrag` — Labor-Wizard 44 px
43. `/lager/gs1-scanner` — Scanner/SSCC/Label, ARIA-Tabs 44 px
44. `/lager/silo-mobil` — Hallenterminal, Lot-Link zuerst
45. `/kontrakte/mengenzeitraeume` — Staffeln laden und anlegen
46. `/agrar/ernte/liste` — Ernte-Übersicht, Arbeit zuerst
47. `/agrar/aussaat` — Aussaat-Planung, Suche filtert
48. `/agrar/psm` — PSM-Stamm, Mittel 44 px
49. `/agrar/feldbuch/schlagkartei` — Schlagliste zuerst, 44 px
50. `/agrar/bodenproben` — Proben suchen und öffnen
51. `/agrar/saatgut/sortenregister` — Sorten 44 px
52. `/agrar/saatgut-liste` — Saatgut-Stamm, Arbeit zuerst
53. `/lager/lagerplaetze` — WMS-Struktur zuerst, Fach 44 px
54. `/agrar/feldbuch/massnahmen` — Einsätze suchen und öffnen
55. `/agrar/kulturpflanzen` — Kulturen 44 px
56. `/agrar/duenger-liste` — Dünger-Stamm, Arbeit zuerst
57. `/agrar/kunden-schlagkartei` — Lohnspritz zuerst, KPI nur Desktop
58. `/agrar/psm/sachkunde-register` — Nachweise suchen, Ablaufwarnung
59. `/agrar/psm/auflagen-manager` — Auflagen abarbeiten
60. `/agrar/biostimulanzien-liste` — Produkte 44 px
61. `/artikel` — Artikelstamm, Export wirkt
62. `/lager/lagerbewegungen` — Buchungen suchen, deutsche Typen
63. `/agrar/duenger/liste` — Düngemittel-Stamm, Löschen pro Id
64. `/charge/liste` — Chargen 44 px
65. `/futter/einzel/liste` — Einzelfutter, Suche filtert
66. `/futter/misch/liste` — Mischfutter, Suche filtert
67. `/zertifikate` — Zertifikate, Ablaufwarnung
68. `/versicherungen` — Policen 44 px
69. `/projekte` — Projekte 44 px
70. `/foerderung` — Förderanträge, Export wirkt
71. `/schaeden` — Schäden 44 px
72. `/agrar/feldbuch/schlag/neu` — Schlag anlegen, Zurück 44 px
73. `/agrar/wetter/prognose` — Standort und Aktualisieren 44 px
74. `/agrar/psm/wasserschutz` — Adresssuche 44 px
75. `/agrar/duenger/mischungen` — Komponenten beschriftet
76. `/agrar/zinsabrechnung` — Buchen/Stornieren beschriftet
77. `/agrar/vermehrungsvertraege` — Stornieren beschriftet
78. `/agrar/rohwarengruppen` — Löschen beschriftet
79. `/lager/massebilanz` — Festschreiben beschriftet
80. `/crm/kontakte-liste` — Kontakte 44 px, KPI nur Desktop
81. `/crm/betriebsprofile-liste` — Betriebe 44 px
82. `/crm/leads` — Zu Kunde pro Id
83. `/fibu/kontenplan` — Theater nur Desktop, Konto 44 px
84. `/banken/konten` — Export wirkt, Bank 44 px
85. `/transporte/fahrer` — Fahrer suchen und oeffnen
86. `/compliance/sachkunde-register` — Compliance-Nachweise
87. `/benachrichtigungen` — Als gelesen lokal, kein Write-API
88. `/fuhrpark/fahrzeuge` — Kennzeichen 44 px, Theater nur Desktop
89. `/einkauf/warengruppen` — Bearbeiten/Deaktivieren beschriftet
90. `/verkauf/kunden-liste` — mailto `text-primary`
91. `/fibu/debitoren` — Rechnungslink 44 px, DATEV wirkt
92. `/marketing/kampagnen` — Kampagnen 44 px, Export wirkt
93. `/personal/schulungen` — Nur PSM / Nur ablaufende filtern
94. `/fibu/verbindlichkeiten` — NativeSelect, Rechnung 44 px
95. `/portal` — Bestell-/Anfrage-CTAs 44 px; Portal-Chrome 34 px bleibt P2
96. `/logistik/frachtbriefe` — Suche filtert, Theater nur Desktop
97. `/logistik/tourenplanung` — Dispo-Arbeitsraum, 44-px-Aktionen
98. `/logistik/tour-fracht-arbeitsraum` — Arbeit zuerst auf Touch
99. `/finance/mahnwesen` — ObjectPage zuerst auf Touch
100. `/service/anfragen` — Tickets zuerst, Theater nur Desktop
101. `/einkauf/wareneingang` — Buchung zuerst, 44-px-Aktionen
102. `/annahme/klaerung-gesperrt` — Queue und Entscheidung zuerst
103. `/einkauf/retouren` — Wareneingang und Retoure zuerst
104. `/service/rueckmeldung` — Formular zuerst, Zurück beschriftet
105. `/agribusiness/field-service-tasks` — Einsätze 44 px, h1
106. `/crm/opportunities` — Pipeline-Liste zuerst
107. `/compliance/qs-checkliste` — Offene Punkte und Tabelle zuerst
108. `/finance/zahlungslauf-kreditoren` — ObjectPage zuerst auf Touch
109. `/finance/ustva` — ObjectPage zuerst auf Touch
110. `/finance/abschluss` — ObjectPage zuerst auf Touch
111. `/einkauf/rechnungseingaenge-liste` — Liste zuerst
112. `/qualitaet/ausnahmen` — Ausnahme erfassen zuerst, 44 px
113. `/einkauf/gutschriften-belastungen` — Formular zuerst
114. `/einkauf/lieferanten-stamm` — Stammregister zuerst
115. `/dashboard/sales` — KPIs zuerst, Theater nur Desktop
116. `/dashboard/einkauf` — KPIs zuerst, Theater nur Desktop
117. `/einkauf/edi-portal` — Meldungen zuerst, 44 px Bestaetigen
118. `/einkauf/lieferantenbewertung` — Scores beschriftet, Guard
119. `/einkauf/service-entry-sheets` — Leistungsnachweis zuerst
120. `/admin/benutzer` — Suche und Liste zuerst
121. `/admin/rollen` — Rollenliste zuerst
122. `/admin/monitoring/alerts` — Alerts zuerst
123. `/system/live-monitor` — Ereignisse zuerst
124. `/strecke/speditionen-fracht-preise` — Tarife 44 px
125. `/fuhrpark/ausgehende-belege-dokumente` — Formular 44 px
126. `/versand/frachtdokumente` — ehrlicher Druck-Stopper
127. `/produktion/produktions-dokumente-drucken` — 44-px-Druck, Replica nur Desktop
128. `/personal/hrm-operations-gates` — Prüfliste zuerst, kein SAP-Blau, PDF druckt
129. `/document` — Upload/Suche zuerst, Scan/Löschen 44 px
130. `/produktion/mischfutter` — Wizard zuerst, 44-px-Lifecycle
131. `/compliance/meldewesen-konsole` — Export und Tabs zuerst
132. `/admin/monitoring/regeln` — Regeln/Kanäle/Jobs zuerst, Loeschen 44 px
133. `/annahme/qr` — Zur Warteschlange 44 px
134. `/weighing` — Wiegescheine deutsch, Abschließen 44 px
135. `/inventory` — Bestand deutsch, Korrigieren/Einlagern 44 px
136. `/contracts` — Tabelle zuerst, Theater nur Desktop
137. `/agrar/kontrakt-engagement` — Mahnen 44 px, per Zeile pending
138. `/agrar/kontrakt-erfuellung` — Suche/Aktualisieren 44 px, Balken Tokens
139. `/agrar/kontrakt-fixierung` — Fixieren 44 px, kein Sky-Blau
140. `/agrar/kontrakt-settlement` — Abrechnen/Storno beschriftet 44 px
141. `/agrar/ernte/neu` — Zur Ernteliste statt Icon-Zurück
142. `/agribusiness/field-service-tasks/neu` — natives Select, 44-px-Speichern
143. `/agribusiness/field-service-tasks/:id/edit` — natives Select, 44-px-Speichern
144. `/agrar/psm/beratung` — Tokens statt Rohblau, Analyse 44 px
145. `/agrar/psm/wasserschutz` — Ergebnis Tokens, Prüfung 44 px
146. `/crm/aktivitaet-detail` — Zurück/Entfernen beschriftet 44 px
147. `/crm/kontakt-detail` — Zurück/Speichern 44 px
148. `/crm/wiedervorlagen` — Erledigen 44 px, überfällig Tokens
149. `/agrar/saatgut-stamm` — Zurück/Speichern 44 px
150. `/agrar/duenger-stamm` — Zurück/Speichern 44 px
151. `/agribusiness/farmers` — Zeilenaktionen 44 px
152. `/agrar/erntefenster-konfig` — Sandbox/Backfill 44 px, per Kampagne pending
153. `/agrar/maschinenauslastung` — Liste zuerst am Touch, Tokens
154. `/crm/kunden-stamm` — Kontakt-/Consent-Aktionen 44 px
155. `/crm/dubletten` — Zusammenführen 44 px
156. `/crm/klaerfall-inbox` — Zuordnen/Verwerfen 44 px
157. `/crm/bestell-inbox` — Tokens, Bestätigen 44 px, per Karte pending
158. `/crm/vertreterstamm` — Bearbeiten/Deaktivieren beschriftet 44 px
159. `/crm/vertreterprovisionen` — Entfernen/Deaktivieren beschriftet 44 px
160. `/crm/kunden-zuordnung` — Zuordnen/Aktualisieren 44 px
161. `/crm/betriebsprofil-detail` — Speichern/Entfernen 44 px
162. `/crm/lead-generierung` — Vorschau/Übernehmen 44 px
163. `/crm/potential-analyse` — KPIs nur Desktop, Kundenliste verdrahtet
164. `/crm/bedarfsdeckung-cockpit` — Tokens, Angebot/KI 44 px, keyed Reklass
165. `/crm/durchdringungs-pipeline` — natives Select, Angebot 44 px
166. `/finance/mahnlauf` — Aktualisieren/Mahnlauf 44 px
167. `/lager/kommissionierung` — Bestätigen 44 px, keyed pending
168. `/mobile/scanner` — Scan/Buchen 44 px, Buchen ehrlich, Details verdrahtet
169. `/einkauf/bestellvorschlag-lager` — kein SAP-Grau, Suchen ehrlich, Theater nur Desktop
170. `/einkauf/bestellvorschlag-rohware` — Tokens, 44 px, Suche ehrlich
171. `/einkauf/bestellvorschlag-verkauf` — Tokens, 44 px, Suche ehrlich
172. `/finance/op-kreditoren` — Liste zuerst am Touch, Ausgleich/Bearbeiten/Löschen beschriftet
173. `/finance/offene-posten` — Aging nur Desktop, Aktualisieren 44 px
174. `/finance/zahlungseingang` — Ausziffern 44 px
175. `/finance/payment-matching` — Theater nur Desktop, Match 44 px
176. `/finance/periods` — Sperren/Wiedereröffnen 44 px, keyed pending
177. `/lager/silo-uebersicht` — Transfer 44 px, Status-Tokens statt Rohfarben
178. `/fibu/zahlungseingaenge` — Theater nur Desktop, Match 44 px
179. `/finance/periodenabschluss` — Öffnen/Abschließen 44 px, Status-Tokens
180. `/lager/qs-leitstand` — Freigeben/Sperren 44 px
181. `/finance/ap/invoices` — Ansehen/Freigabe/Buchen 44 px
182. `/einkauf/frachtauftraege-eingang` — kein SAP-Grau, Suchen ehrlich, 44 px
183. `/fibu/buchhaltungsuebersicht` — Theater nur Desktop, Ribbon 44 px, Hilfe ehrlich
184. `/einkauf/anfrage-erfassung` — kein SAP-Grün, Suche beschriftet, 44 px
185. `/lager/materialfluss` — Speichern/Sync 44 px
186. `/artikel/stamm` — beschriftete Aktionen, tote Uploads toasten
187. `/personal/zeiterfassung` — KPIs nur Desktop, 44 px, Tokens
188. `/einkauf/lieferant/:id` — Theater nur Desktop, Löschen beschriftet 44 px
189. `/pos/terminal` — Einstellungen/Leeren/Rabatt beschriftet 44 px, keine Rohfarben
190. `/fibu/monatswerte` — Theater nur Desktop, Ribbon 44 px, Druck ehrlich
191. `/agrar/ernte-annahme-erfassung` — Lookups beschriftet Suchen
192. `/lager/materialfluss-visualisierung` — Anlegen/Löschen 44 px, Status-Tokens
193. `/portal/feldbuch` — KPIs nur Desktop, Zeilen Bearbeiten/Löschen beschriftet
194. `/einkauf/wareneingangsabgleich` — Aktualisieren/Gutschrift 44 px
195. `/pos/retoure` — kein SAP-Rot, Menge/Entfernen 44 px
196. `/annahme/warteschlange` — Zeilen-CTAs ohne size=sm
197. `/logistik/tour-fracht-arbeitsraum` — Storno/Probe 44 px, Theater nur Desktop
198. `/pos/uebernahme-kasse` — OK/Abbrechen 44 px
199. `/disposition/coverage-monitor` — Deckungsmonitor deutsch, 44 px, Status-Tokens, Shortcuts nur Desktop
200. `/disposition/position-matrix` — Warenpositionsmatrix, Theater nur Desktop, 44 px
201. `/finance/nebenbuch-abstimmung` — Arbeit zuerst, Details beschriftet, Flow-Schlüssel nicht sichtbar
202. `/personal/stundenzettel/:id` — Tour hinzufügen/Löschen 44 px beschriftet
203. `/management/executive-dashboard` — Leitungs-Dashboard deutsch, Aktualisieren beschriftet, Export ehrlich
204. `/lager/permanente-inventur` — Zählen keyed pending, Abschließen 44 px
205. `/fibu/kostenstellenrechnung` — Löschen beschriftet 44 px
206. `/portal` — Alle/Herunterladen beschriftet 44 px
207. `/fibu/elster-online` — ELSTER-XML und UStVA-Links 44 px
208. `/fibu/schnittstelle-fibu` — Vorschau/Übertragung 44 px
209. `/fibu/anlagen-suite` — Validieren/Buchen 44 px
210. `/nawaro/raps-profil` — Zertifikat/Bilanz/Löschen beschriftet 44 px
211. `/finance/datev-export` — Stapel-Typ und Export 44 px
212. `/finance/bank-stamm` — Bearbeiten beschriftet 44 px
213. `/fibu/guv` — Aktualisieren beschriftet, Status-Tokens
214. `/fibu/bilanz` — Aktualisieren/Export 44 px
215. `/finance/chart-of-accounts` — Bearbeiten/Deaktivieren beschriftet
216. `/finance/wechselkurse` — Löschen beschriftet 44 px
217. `/fibu/sachkonto/:id` — Aktualisieren beschriftet 44 px
218. `/fibu/bwa` — Periode 44 px, Aktualisieren beschriftet
219. `/fibu/buchungsjournal` — Storno 44 px
220. `/fibu/periodische-buchungen` — Sperren/Löschen beschriftet 44 px
221. `/fibu/erloeskennziffern` — Bearbeiten/Löschen beschriftet
222. `/fibu/erloeskontenzuordnung` — Bearbeiten beschriftet
223. `/fibu/abschluss-cockpit` — Checklisten-Details 44 px
224. `/fibu/abschluss-checklist-detail` — Erledigen 44 px, kein Instanz-UUID
225. `/fibu/forderungsgruppen` — Bearbeiten/Löschen beschriftet
226. `/fibu/lohn-connector` — Validieren/Buchen/Löschen 44 px
227. `/fibu/atlas` — Zurück zum Schnittstellen-Center 44 px
228. `/portal/bestellungen` — Details/Download beschriftet 44 px
229. `/portal/rechnungen` — Details/Download beschriftet
230. `/portal/vertraege` — Details/Download beschriftet
231. `/portal/anfragen` — Details beschriftet
232. `/portal/shop` — Kategorie und Warenkorb 44 px
233. `/portal/empfehlungen` — CTA 44 px, keine Rohgrau-Titel
234. `/portal/preisspiegel` — Aktualisieren 44 px
235. `/portal/naehrstoffbilanzen` — Download 44 px
236. `/nawaro/anbauflaechen` — Neu/Zeile 44 px
237. `/nawaro/vertraege` — Neu/Zeile 44 px
238. `/nawaro/mitteilung-drucken` — Neu 44 px
239. `/einkauf/zahlungsbedingungen` — Bearbeiten/Löschen beschriftet 44 px
240. `/einkauf/lieferantenbewertung` — Score 44 px
241. `/einkauf/lieferschein-frachtauftrag` — Anlegen/Aktualisieren 44 px
242. `/einkauf/reports` — Export 44 px
243. `/einkauf/rfq-bids` — Ansehen/Zuschlag 44 px
244. `/einkauf/lieferanten-dokumente` — Löschen 44 px
245. `/einkauf/gutschriften-belastungen` — Ausgleichen/Entfernen 44 px
246. `/einkauf/rechnung-abgleich` — Abweichungen 44 px
247. `/einkauf/rechnung-eingang-erfassung` — Toolbar und Suchen 44 px
248. `/stammdaten/hausbanken` — Bearbeiten/Löschen beschriftet
249. `/stammdaten/betriebsstaetten` — Bearbeiten/Löschen beschriftet
250. `/stammdaten/mengeneinheiten` — Löschen beschriftet
251. `/lager/partiestamm` — Löschen beschriftet
252. `/logistik/frachttabellen` — Position 44 px
253. `/benachrichtigungen` — Als gelesen 44 px ohne size=sm
254. `/controlling/kpi-verwaltung` — Bearbeiten/Löschen beschriftet 44 px
255. `/controlling/massnahmen` — Bearbeiten/Löschen beschriftet
256. `/controlling/dashboard-verwaltung` — Bearbeiten/Löschen beschriftet
257. `/controlling/widget-verwaltung` — Bearbeiten/Löschen beschriftet
258. `/controlling/timeseries-erfassung` — Löschen beschriftet
259. `/controlling/benchmark-cockpit` — Analytics/Agent Ops 44 px
260. `/admin/control-center` — Filter Deutsch, Erledigen/Erneut versuchen 44 px
261. `/admin/integrationen-quarantaene` — Erneut versuchen/Erledigen 44 px
262. `/admin/compliance-dashboard` — Details 44 px
263. `/admin/qualitaets-cockpit` — Gates/Aktualisieren 44 px
264. `/admin/externe-gates` — Aktualisieren 44 px
265. `/admin-suite` — Bereich öffnen 44 px
266. `/compliance/intrastat` — CSV 44 px
267. `/compliance/datenpannen` — Bearbeiten/Melden 44 px
268. `/compliance/verarbeitungsverzeichnis` — Export/Neu 44 px
269. `/workflow/regeln` — Bearbeiten/Aktivieren 44 px
270. `/preise/rabattgruppen` — Löschen beschriftet
271. `/preise/individualpreise` — Löschen beschriftet
272. `/konditionen` — Löschen beschriftet
273. `/docflow/artefakt-freigabe` — Freigeben 44 px
274. `/fuhrpark/fahrzeug-vertiefung` — Abschließen/Bezahlt 44 px
275. `/` Start-Dashboard — Kachel Öffnen 44 px
276. `/dokumente/ablage` — Download 44 px
277. `/wissen/wissensbasis` — Version/Neu 44 px
278. `/admin/agenten-integration` — Freigeben und Zeilen 44 px
279. `/admin/vordruck-editor` — Elementtypen Deutsch, Löschen 44 px
280. `/portal/whatsapp-simulator` — Senden 44 px (kein size=sm mehr)
281. `/prospecting` LeadExplorer — Auto-Download 44 px, kein `h-6`
282. Mask-Builder ObjectPage — Wiederherstellen/Verwerfen 44 px
283. FastTable-Pager — Zurück/Weiter 44 px, `>=` unbeschädigt
284. AdvancedFilters-Chips — Entfernen 44 px
285. FlowSpine-Agentaktionen — Übernehmen 44 px
286. `/fibu-suite` — Ribbon und Darstellung 44 px, Karten statt Cards, Dunkel statt Dark
287. Benachrichtigungen „Alle lesen“ 44 px
288. AskVALEO / AskValeo Schnellaktionen 44 px
289. CallWidget Annehmen/Auflegen 44 px, Halten/Weiterleiten beschriftet
290. IntentBar-Aktionen mit sichtbarem Label, kein `hidden sm:inline`
291. Dublettenwarnung Auswählen 44 px
292. Wiege-Freigabe im Feature-Modul 44 px
293. DataTable/ListReport — auf Touch Kartenstapel statt Horizontal-Scroll
294. Sprache „öffne Warteschlange / zeige Wiegungen“ navigiert; Wiegen per Voice-Gate nicht
295. FastTable/VirtualDataTable — auf Touch Kartenstapel, Filter 44 px; `__actions` bleibt Aktion, nicht Feld
296. Worklist list-detail — auf 390 px Liste zuerst, Vorschau erst nach Zeilenauswahl
297. Sprache „öffne Rechnungen“ → `/verkauf/rechnungen` (Worklist, nicht Invoice-Editor)
298. Copilot-Dock geschlossen: `hidden` + `inert`, nicht nur `translate-x`
299. LookupField — Treffer 44 px, Auswahl schreibt den Wert in die Maske
300. `/dokumente/ablage` — Suche/Tabelle zuerst, Download/Export wirken, Hochladen ehrlich ohne API
301. DataTable — `actions`/`__actions` auf Touch in der Karten-Aktionsleiste
302. `/einkauf/bestellung-anlegen` — Vorschlag Uebernehmen 44 px (kein size=sm)
303. Eingabemaske Methode 1: ScreenDefinition → RenderPlan → ObjectPage, kein CDS/OData/Fiori-Tools; valueHelp=`lookup` braucht `screen_definitions.py` (Claude)
304. useTouchDevice folgt matchMedia/Resize — Karten und Theater-Hide ohne Extra-Tipp
305. `/fibu/kreditoren` — Suche/Tabelle zuerst, Rechnung 44 px, Skonto-Callout Tokens
306. `/fibu/zahlungsvorschlaege` — Auswahl und Zahlungslauf 44 px, Theater nur Desktop
307. `/einkauf/anlieferavis-liste` — ListReport zuerst, CSV-Export, Import ehrlich
308. `/fibu/zahlungslaeufe` — Wizard zuerst, 44-px-Auswahl, Theater nur Desktop
309. `/fibu/op-verwaltung` — Debitoren/Kreditoren oeffnen 44 px, Theater nur Desktop
310. `/einkauf/auftragsbestaetigungen` — ListReport zuerst, CSV-Export, Theater nur Desktop
311. Wizard `onFinish` wird awaited; Footer 44 px, kein Doppel-Abschliessen
312. ListReport-Export `data-global-button-handler="ignore"` — Seiten-Export statt Global-Intercept
313. `/einkauf/anfragen` — ListReport zuerst, CSV-Export, Theater nur Desktop
314. `/fibu/offene-posten` — Suche/Mahnlauf zuerst, Rechnungszeile zur Worklist, Theater nur Desktop
315. `/fibu/buchungsjournal` — Suche zuerst, DATEV 44 px, Theater nur Desktop
316. `/fibu/hauptbuch` — Suche zuerst, DATEV zur Buchungsuebergabe, Theater nur Desktop
317. `/fibu/schnittstelle-fibu` — Filter/Uebergabe zuerst, Theater nur Desktop
318. `/finance/buchungsimport` — Schritte zuerst, 44-px-Import, Theater nur Desktop
319. KIM Object Page — Aktionsleiste, Kundenfilter, Alphabet und Register 44 px, Zeilenaktionen beschriftet
320. Auftrag (`OrderEditorLegacyPage`) — Kopf-Lookups und Positionsaktionen 44 px, Suche im Auswahldialog 44 px
321. Rechnung (`/sales/invoice-editor`) — Druck, Export, XRechnung, ZUGFeRD ohne size=sm
322. Lieferschein (`delivery-editor`) — Lookup-Schaltflächen 44 px mit Namen
323. `/fibu/bwa` — Periode und Schema zuerst, Theater nur Desktop
324. `/fibu/bilanz` — Stichtag/CSV zuerst, Theater nur Desktop
325. `/fibu/guv` — Periode und Positionen zuerst, Theater nur Desktop
326. `/finance/lastschriften-debitoren` — ObjectPage zuerst, 44-px-Positionen, Theater nur Desktop
327. `/fibu/elster-online` — Schritte zuerst, Periode und XML 44 px, Theater nur Desktop
328. `/finance/bank-abgleich` — ObjectPage zuerst, Theater nur Desktop

Agent-Ist je Seite: Wiegeschein *listen* (`agrar.weighing_ticket.list`), OP *listen*
(`fibu.open_items.list`), Bestand *lesen* (`lager.bestand.get`), Kontakt *loggen*
(`crm.contact.log`), Bestellungen *listen* (`einkauf.bestellung.list`),
Kunde *suchen* (`crm.customer.search` / `crm.customer.summary360`),
Kontrakt *lesen* (`agrar.contract.get`), Inventur *status* (`lager.inventur.status`),
Lot *lesen* (`wms.lot.trace`), Silozelle *lesen* (`wms.cell.status`).
Annahme speichern, Wiegung anlegen, Aktivität anlegen, Bestellung anlegen,
Angebot anlegen/listen, Kundenstamm speichern, Lieferschein speichern,
Abrechnung anlegen/freigeben/buchen, LKW einreihen, QS-Protokoll speichern,
Ein-/Auslagerung buchen, Beladung buchen, Inventur abschließen/stornieren,
Kontrakte listen/anlegen/speichern, Reklamation anlegen/statuswechseln,
Labor-Auftrag anlegen, Lieferanten exportieren, Kette sperren/stornieren,
Silo-Transfer buchen, Mengenzeiträume anlegen, Schlag stilllegen,
Bodenprobe anlegen, Sorte speichern, Lagerfach sperren, Maßnahme löschen,
Dünger anlegen, Lohndienst anlegen, Sachkunde speichern, Auflage erledigen,
Biostimulanz speichern, Artikel exportieren/anlegen, Lagerbewegung buchen,
Charge anlegen, Futter speichern, Zertifikat anlegen, Police speichern,
Projekt anlegen, Förderantrag anlegen, Schaden melden, Schlag anlegen
und Leitstand-Replay gehen über MCP nicht. Bankkonto, Fuhrpark, Warengruppe,
Debitor-Mahnung, Benachrichtigung-gelesen, Kampagne, Schulung,
Verbindlichkeit-Export, Frachtbrief anlegen, Tour anlegen und Mahnlauf
starten haben ebenfalls kein MCP-Write. Kreditoren-DATEV, Zahlungsvorschlaege-Lauf
und Anlieferavis-Export/Senden gehen über MCP nicht. Zahlungslauf erstellen,
OP-Clearing und Auftragsbestaetigungs-Export/Pruefen gehen über MCP nicht.
Anfragen-Export/Freigabe, FIBU-OP-Mahnlauf und Journal-Storno gehen über MCP nicht. Service-Anfrage anlegen, Wareneingang
buchen, Klaerung speichern, Retoure anlegen, Service-Rueckmeldung POST,
Feldservice anlegen/loeschen und Opportunity-Import gehen ueber MCP nicht.
QS-Audit starten gibt es nicht als eigenen Vorgang; die Checkliste verweist
auf QS-Ausnahmen. EDI bestaetigen, Leistungsnachweis freigeben, Score
aendern, Benutzer exportieren, Frachttarif speichern, Fuhrpark-Beleg
speichern und Dokumentdruck gehen ueber MCP nicht. HRM-Gates, Meldewesen-Jobs,
Mischfutter-Auftraege, QM-Scan/Loeschen und Monitoring-Regeln haben ebenfalls
kein MCP-Write. `wms.lot.trace` liest ein Lot,
`wms.cell.status` liest eine Zelle, bucht keine Buchung und patcht kein Fach.
Kontrakt *lesen* (`agrar.contract.get`) gilt; Mahnen, Fixieren, Abrechnen und
Storno gehen über MCP nicht. Field-Service anlegen/speichern, Ernte anlegen
und PSM-Analyse/Wasserschutz-Prüfung haben ebenfalls kein MCP-Write.
Wiedervorlage erledigen, Landwirt löschen, Erntefenster-Backfill,
Maschinen-Aktualisieren, Dubletten-Merge, Klärfall-Zuordnung und
Bestell-Inbox-Bestätigung gehen über MCP nicht.
Kunden-Zuordnung, Lead-Übernahme, Bedarfsdeckung-Reklass, Mahnlauf starten,
Kommissionierung bestätigen, Scanner buchen, Bestellvorschlag-Bestellung
anlegen, Kreditoren-Ausgleich und Zahlungseingang-Auszifferung gehen über
MCP nicht. Scanner-Kamera ist nicht angebunden; leerer Scan und Buchen
sind ehrliche Stopper. Payment-Matching, Perioden sperren/öffnen und
Silo-Transfer gehen über MCP nicht. FIBU-Zahlungseingang-Match,
Periodenabschluss und QS-Leitstand-Freigabe/Sperre gehen über MCP nicht.
Frachtauftrag anlegen, Anfrage speichern/senden, FIBU-Ribbon-Hilfe,
Artikel-Dokument-Upload und Materialfluss-Silo-Patch gehen über MCP nicht.
Zeiterfassung korrigieren/einreichen/Payroll, Lieferanten speichern/sperren,
POS-Verkauf abschließen, Monatswerte-Export, Ernte-Annahme speichern/freigeben
und Materialfluss-Knoten anlegen/löschen gehen über MCP nicht.
Portal-Feldbuch anlegen/löschen, Wareneingang-Gutschrift, POS-Retoure buchen,
Warteschlangen-Klärung und Fracht-Storno gehen über MCP nicht.
Deckungsmonitor-Override, Positionsmatrix-Refresh, Nebenbuch-Abstimmen,
Stundenzettel speichern, Leitungs-Export, Inventur-Zählmenge, Kostenstelle
löschen, Portal-Dokument-Download, ELSTER-XML, Bankabgleich importieren/buchen, FIBU-Übertragung, Anlagen
buchen/stornieren und Raps-Profil speichern/löschen gehen über MCP nicht.
DATEV-Stapel, Bankkonto bearbeiten, GuV/Bilanz-Export, Kontenplan deaktivieren
und Wechselkurs löschen gehen über MCP nicht.
BWA-Aktualisieren, Journal-Storno, periodische Buchung sperren, EKZ löschen,
Abschluss-Checkliste erledigen, Lohn-Import buchen/löschen, Portal-Download
und NaWaRo-Speichern gehen über MCP nicht. WhatsApp-Simulator im Portal
ist auf 44 px nachgezogen; Schreiben über MCP gibt es dort nicht.
Zahlungsbedingungen, Rechnungseingang speichern/buchen, Gutschrift ausgleichen,
RFQ-Zuschlag, Hausbank/Betriebsstätte löschen und Partie deaktivieren gehen
über MCP nicht.
Vordruck speichern, Ablage-Download/Export/Hochladen, Wissen anlegen und Agenten-Freigeben
gehen über MCP nicht. Ablage-Download ist ein lokaler Metadaten-Text, kein DMS-Binary. Anruf annehmen/auflegen und FIBU-Ribbon-Navigation
gehen über MCP nicht.

Evidenz: Browser 390×844 auf `http://localhost:3001/`, Code, Vitest,
[`mcp-tools.md`](../schnittstellen/mcp-tools.md).
