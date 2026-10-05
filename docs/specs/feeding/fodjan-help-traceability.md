---
title: "Fuetterungsberatung — oeffentlicher Funktionsabgleich Fodjan-Hilfe"
type: reference
audience: [produkt, fachlich, entwickler, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Quellengebundene, eigenstaendig formulierte Funktions-Traceability der oeffentlich erreichbaren Fodjan-Hilfe ohne Uebernahme von Texten, Screens oder Produktdesign.
---

# Oeffentlicher Funktionsabgleich Fodjan-Hilfe

## Zweck, Stand und Schutzgrenzen

Dieser Abgleich schliesst den in `implementation-plan.md` offenen Quellenpunkt.
Ausgewertet wurden am 15.07.2026 die oeffentlichen Hilfe-Hubs, deren verlinkte
Artikeltitel sowie erreichbare Detailseiten. Einzelne Detail-URLs lieferten beim
Abruf einen Cache-Fehler; sie sind im Inventar als vom Hub nachgewiesene Themen,
nicht als inhaltlich voll gelesene Detailquelle, gekennzeichnet.

Verbindliche Schutzgrenzen:

- keine Uebernahme von Hilfetexten, Screenshots, Icons, Seitenaufbau oder
  Navigationsmodell;
- nur paraphrasierte Funktions- und Prozessanforderungen;
- fachliche Formeln und Grenzwerte stammen weiterhin aus GfE 2023,
  DLG-Information 01|2025 und VALEO-Golden-Tests, nicht aus Fremdsoftware;
- jede Produktentscheidung bleibt im VALEO-Zielmodell, Meridian-Vertrag und
  `ScreenDefinition -> RenderPlan -> Runtime -> Renderer`-Pfad verankert.

## Ergebnis

Der vorhandene VALEO-Plan deckt den oeffentlich beschriebenen End-to-End-Kreis
Betrieb -> Futter/Analyse -> Ration -> Plan -> Ist-Fuetterung -> Auswertung ->
Folgemassnahme bereits strukturell ab. Der Quellenabgleich aendert nicht die
Architektur, schaerft aber Abnahmekriterien und Reihenfolge mehrerer Slices.

## Funktions-Traceability

| Oeffentlich beschriebenes Arbeitsmotiv | Eigenstaendige VALEO-Anforderung | Requirement-IDs | Umsetzung / Slice | Bewertung |
|---|---|---|---|---|
| Mehrere Nutzer und Zusammenarbeit je Betrieb | Rollen plus ressourcenbezogene Betriebs-/Herdengrants, zeitlich begrenzte Beratung | FEED-RBAC-002/003/004, FEED-COLLAB-002 | FEED-ADVICE-ROLES-013, FEED-CORE-015, FEED-CONS-032 | Architektur passt; Betriebsgrants sind der wichtige Ausbau |
| Berater arbeitet ueber mehrere Betriebe | Betriebsworklist mit Risiko, Faelligkeit und naechster Aktion statt kopiertem Fremd-Cockpit | FEED-BUS-001/003/004, FEED-UI-002 | FEED-CORE-015, FEED-EDITOR-025, FEED-CONS-031/032 | Im Plan enthalten |
| Futtergruppen mit Leistung, Laktation und Fuetterungssystem | Typisierte, historisierte Tiergruppe mit Gueltigkeit und fachlichen Profilen | FEED-HERD-001/002/003 | FEED-CORE-016, spaeter Delta-Verdichtung | Im Plan enthalten |
| Kraftfutterstation/Melkroboter als eigener Fuetterungsweg | Futtertisch und optionale Leistungsfutterwege getrennt planen; Grenzen und Gesamtwirkung gemeinsam bewerten | FEED-HERD-002, FEED-REQ-002, FEED-RAT-004 | FEED-CORE-016/020, FEED-EDITOR-021 | Abnahmekriterium fuer Gruppenprofil und Editor ergaenzt |
| Eigene Futtermittel, Datenbankvorlagen und individuelle Werte | Persistentes Feed/FeedProduct-Modell mit Referenzwert-Herkunft und klarer Kennzeichnung geschaetzter Werte | FEED-MAT-001/003, FEED-LAB-004 | FEED-CORE-017/018/019 | Im Plan enthalten |
| Futteranalyse manuell oder per Labor, danach als neues Futter oder neue Version verwenden | Importvorschau, Material-Mapping, Originalbeleg, Plausibilitaet und bewusste Aktivierung einer Analyseversion | FEED-LAB-001/002/003/004 | FEED-CORE-019, FEED-INT-034 | Abnahmekriterien bestaetigt |
| Bestand, Reichweite, Lieferungen, Inventur und Kontrakte | Bedarf aus Planversion, Bestand, Sicherheitszuschlag, Lieferung, Reservierung und Einkauf getrennt modellieren | FEED-SUP-001/002/003, FEED-MAT-004 | FEED-SUP-028, FEED-INT-035 | VALEO nutzt vorhandenen Einkauf/Lager statt ein Fremdmodell zu kopieren |
| Rationsentwurf in FM/TM mit Min/Max, Skalierung und Mischreihenfolge | Tastaturfaehiger Editor mit Undo/Redo, stabiler Reihenfolge, Einheitenregeln und unveraenderlicher Version | FEED-RAT-001/002/004 | Slices 006/007, FEED-EDITOR-021 | Im Plan enthalten |
| Geplante, aktuelle, gespeicherte und gefuetterte Rationen | Expliziter Lifecycle mit geplantem Start, einer aktiven Version und spaeterem Planabschluss | FEED-RAT-002, FEED-PLAN-001 | Slice 007, FEED-PLAN-026 | VALEO-Lifecycle ist eigenstaendig und strenger auditiert |
| Assistent und Katalog mehrerer Vorschlaege | Solver-Ergebnis reproduzierbar speichern; Alternativen nach Bestand, Preis und Restriktionen; spaeter Pareto/Sensitivitaet | FEED-OPT-005/006, FEED-CMP-002 | FEED-CORE-020, Release-C-Ausbau | Pareto bleibt echter offener Gap |
| Gesundheitsbewertung mit Ueber-/Unterversorgung und Handlungshinweis | Kennzahl, Ist, Ziel, Bedeutung, Ursache, Prioritaet und Empfehlung als strukturierte Evaluation | FEED-EVAL-001/002/003 | FEED-EDITOR-022/024 | Im Plan enthalten; keine fremde Score-Darstellung uebernehmen |
| Freigabe, Kommentar, Beschreibung und Teilen | Serverstatus, Vier-Augen-Option, Auditgrund, Kommentar und adressatengerechte Ausgabe | FEED-COLLAB-001/002/003, FEED-REP-001 | Slice 007, FEED-EDITOR-023, FEED-PLAN-027 | Im Plan enthalten |
| Rezept-, Auswertungs-, Vergleichs- und Uebersichtsdruck | Rollenprofilierte Berichte aus derselben freigegebenen Version, inklusive Betrieb/Freigabe/Gueltigkeit | FEED-REP-001/002, FEED-CMP-001 | FEED-EDITOR-023, FEED-PLAN-027, FEED-CONS-032 | Abnahmekriterium geschaerft |
| Mobile Ist-Fuetterung und Nachtrag | Planversion lesen, geladene Mengen/Restfutter erfassen, offline puffern, Konflikte sichtbar aufloesen | FEED-PLAN-002, FEED-ACT-001/002, FEED-MOB-001 | Slices 007/009, FEED-PLAN-027, FEED-ACT-029 | Im Plan enthalten |
| Mischgenauigkeit pro Komponente und Fuetterung | Soll/Ist in kg FM und Prozent, Filter nach Gruppe/Futter/Zeitraum, Schwelle je Komponentenklasse konfigurierbar | FEED-ACT-002/003/004 | FEED-ACT-029/030 | Neue Abnahme: keine universelle Einzelschwelle |
| Futteraufnahme, Effizienz, Kosten, N, Methan und Milchbezug | Lueckenfreie Herkunft, keine Nullfabrikation, Versionsmarker und Aufgaben aus Abweichungen | FEED-PERF-001/002/003, FEED-ACT-004 | Slices 009/012, FEED-ACT-030 | Kern vorhanden; Aufgaben/IOFC/Versionsmarker offen |
| MLP, Milchguete und AMS | Providerneutrale Importvertraege, Mapping/Quarantaene und Kennzahlenpfad in Tagesreihe | FEED-PERF-004, FEED-INT-001/002/003 | FEED-PERF-033, FEED-INT-034/036 | Livepfade bleiben bis Partnervertrag blockiert |
| Labor- und Mischtechnik-Schnittstellen | Bidirektional, idempotent, mit Vorschau, Fehlerquarantaene, Betriebszuordnung und Audit | FEED-PLAN-003, FEED-INT-001/002/004 | FEED-INT-034/035/036 | Im Plan enthalten |
| Farmbezogene Glocke und Push-Hinweise | Ereignisbasierte, rollen- und nutzerspezifisch konfigurierbare Benachrichtigungen mit Deep Link | FEED-COLLAB-002, FEED-ACT-004 | FEED-CONS-032, FEED-INT-036 | Konkretes Abnahmekriterium ergaenzt |

## Konkretisierte Abnahmekriterien

1. `FEED-CORE-016`: Gruppenprofile koennen Futtertisch und optionale
   Leistungsfutterwege getrennt beschreiben; Gesamtbedarf bleibt nachvollziehbar.
2. `FEED-EDITOR-021`: Mischreihenfolge ist per Tastatur und Zeilenaktion
   bedienbar; Drag-and-drop darf nur progressive Ergaenzung sein.
3. `FEED-EDITOR-022`: Warnungen besitzen Text, Symbol, Prioritaet und Ursache;
   Farbe allein transportiert keine Bedeutung.
4. `FEED-PLAN-027`: Ausgabeprofile basieren auf derselben Planversion und
   unterscheiden Informationsdichte, nicht fachliche Wahrheit.
5. `FEED-ACT-029/030`: Mischabweichungen werden je Komponentenklasse und Betrieb
   konfiguriert; unbekannte Werte bleiben unbekannt.
6. `FEED-INT-034`: Labor-/MLP-/AMS-Daten werden vor Uebernahme gemappt und
   validiert; unklare Datensaetze landen in einer sichtbaren Quarantaene.
7. `FEED-INT-035`: Maschinenexport und Rueckmeldung tragen Planversions- und
   Quellenreferenz und sind idempotent.
8. `FEED-CONS-032/FEED-INT-036`: Benachrichtigungen sind farm-, rollen- und
   nutzerspezifisch abschaltbar und fuehren zur bearbeitbaren Ausnahme.

## Quelleninventar

### Kategorie-Hubs

- [Hilfe-Startseite](https://fodjan.com/de/hilfe/hilfe/)
- [Einfuehrung](https://fodjan.com/de/hilfe/einfuehrung-in-fodjan/)
- [Rationsplanung](https://fodjan.com/de/hilfe/rationsplanung/)
- [Dokumentation](https://fodjan.com/de/hilfe/dokumentation/)
- [Auswertungen](https://fodjan.com/de/hilfe/ueberblick-auswertungen-in-fodjan/)
- [Schnittstellen](https://fodjan.com/de/hilfe/schnittstellen-in-fodjan-ueberblick/)

### Einstieg, Rollen und Zusammenarbeit

Vom Einstiegs-Hub inventarisiert: erste Schritte, Zusammenarbeit, beratener
Landwirt, Fuetterungsworkflow, Offline-Nutzung, Benachrichtigungen,
Beratercockpit, IOFC sowie Freigaben/Kommentare. Inhaltlich vertieft wurden
[Zusammenarbeit](https://fodjan.com/de/hilfe/zusammenarbeiten-in-fodjan/),
[Benachrichtigungen](https://fodjan.com/de/hilfe/benachrichtigungsglocke/) und
[erste Schritte](https://fodjan.com/de/hilfe/erste-schritte-in-fodjan-unsere-tipps/).

### Futterbestand und Analysen

Inventarisierte Themen: Futtermittel erstellen, bearbeiten/ersetzen,
archivieren/loeschen, Mischfutter/Hofmischung, Datenbankvorlagen, Mengen/Preise,
Reichweite/Bestandsreduktion, Analysen, Analyse uebernehmen/ueberschreiben,
Kontrakte, Lieferplanung, Inventur und Handel. Vertiefte Quellen:

- [Futtermittel erstellen](https://fodjan.com/de/hilfe/futtermittel-erstellen/)
- [Futtermodell und Datenbanken](https://fodjan.com/de/hilfe/futtermodell-und-datenbanken-in-fodjan/)
- [Futterdatenbank](https://fodjan.com/de/hilfe/seite-futterdatenbank-in-fodjan-erklaert/)
- [Kontraktmanagement](https://fodjan.com/de/hilfe/kontraktmanagement-uebersicht/)
- [Futtermittelhandel](https://fodjan.com/de/hilfe/futtermittel-kaufen-und-handeln-in-fodjan/)
- [Laborschnittstelle](https://fodjan.com/de/hilfe/laborschnittstelle-einrichten/)

### Futtergruppen, Rationen und Optimierung

Der Rations-Hub listet 31 Fachartikel: Gruppen-CRUD, Laktationsphase, Restfutter,
Kraftfutterstation, Erhaltungs-/Leistungsbedarf, Inhaltsstoff-/Mineral-/
Futtermittelgrenzen, Rationsuebersicht und -planung, CRUD, Mischreihenfolge,
angezeigte Inhaltsstoffe, Export/Druck/Teilen, Kopieren, Gesundheitsbewertung,
Freigaben, Fehlerbehebung, Skalierung, Sonderfaelle, Optimierungsgrundlagen,
Assistent, Vorschlagskatalog und Alternativen. Vertiefte Quellen:

- [Kraftfutterstation](https://fodjan.com/de/hilfe/kraftfutterstation-anlegen/)
- [Erhaltungs- und Leistungsbedarf](https://fodjan.com/de/hilfe/erhaltungs-und-leistungsbedarf-anpassen/)
- [Futtermittelgrenzen](https://fodjan.com/de/hilfe/futtermittelgrenzen-richtig-einstellen/)
- [Rationsuebersicht](https://fodjan.com/de/hilfe/seite-rationsuebersicht-in-fodjan-pro-erklaert/)
- [Rationen planen](https://fodjan.com/de/hilfe/rationen-vorplanen-seite-planung-in-fodjan-pro/)
- [Rationen bearbeiten](https://fodjan.com/de/hilfe/rationen-anlegen-bearbeiten-loeschen/)
- [Gesundheitsbewertung](https://fodjan.com/de/hilfe/futtergesundheit-fgb-auswerten-und-verbessern/)
- [Optimierungsueberblick](https://fodjan.com/de/hilfe/rationsoptimierung-mit-fodjan-ueberblick/)
- [Optimierungsgrundlagen](https://fodjan.com/de/hilfe/grundeinstellungen-fuer-die-rationsoptimierung/)
- [Ausgabe und Teilen](https://fodjan.com/de/hilfe/rationen-exportieren-ausdrucken-und-teilen/)
- [Milch aus Ration](https://fodjan.com/de/hilfe/was-bedeutet-milch-aus-ration/)

### Dokumentation, mobile Ausfuehrung und Auswertungen

Der Dokumentations-Hub listet Milch, Futter, Tierbestand, Mischtechnik,
Maschinenexport, tatsaechlich geladene Mengen, Nachtrag, mobile Fuetterung und
Schuettelbox-Logbuch. Vertiefte Auswertungsquellen:

- [Auswertungsueberblick](https://fodjan.com/de/hilfe/ueberblick-auswertungen-in-fodjan/)
- [Mischgenauigkeit und Verbrauch](https://fodjan.com/de/hilfe/mischgenauigkeit-und-futtermittelverbrauch/)
- [Fuetterungscontrolling](https://fodjan.com/de/hilfe/fuetterungscontrolling/)
- [MLP-Report](https://fodjan.com/de/hilfe/mlp-report/)
- [MLP-Schnittstelle](https://fodjan.com/de/hilfe/mlp-schnittstelle-nutzen/)
- [Melkroboter/AMS](https://fodjan.com/de/hilfe/melkroboter-schnittstelle-und-auswertungen/)

### Schnittstellen

Der Schnittstellen-Hub nennt Labor, Futtermischtechnik, MLP, Milchguete,
Melkroboter/AMS und Mehrbenutzer-Zusammenarbeit. Die oeffentlichen Seiten
belegen Funktionsrichtungen, aber keinen belastbaren technischen API-Vertrag.
Providerpfade, Authentifizierung, SLA und Nutzungsrechte duerfen daher nicht
aus UI-Texten abgeleitet werden; fuer Livebetrieb bleiben Partnervertrag und
Connector-Gates zwingend.

## Nicht aus der Quelle ableitbar

- keine vertraglich belastbaren DDW-, Labor-, Mischwagen-, MLP- oder AMS-API-
  Endpunkte;
- keine Garantie fuer Datenfrequenz, Verfuegbarkeit, Loeschsemantik oder SLA;
- keine fachlich verbindlichen Formeln fuer GfE/DLG-Kennzahlen;
- keine Erlaubnis zur Uebernahme von Produktdesign, Text, Bild oder Markenlogik.
