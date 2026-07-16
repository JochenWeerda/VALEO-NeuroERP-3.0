---
title: "Fütterungsberatung — Maskenkatalog"
type: reference
audience: [produkt, fachlich, ux, frontend, backend, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
sources:
  - docs/architecture/uix/universal-mask-runtime-status.md
  - docs/specs/feeding/06-api.md
  - docs/specs/feeding/lastenheft-fuetterungsberatung.md
  - docs/design/frontend-design-skill-audit.md
---

# 07 — Maskenkatalog

## 1. Produktentscheidung

Die vorhandene „Agrar-Spezialmaske“ ist nicht das Zielmodell. Fütterungsberatung
ist ein zusammenhängender Entscheidungsprozess aus Datenqualität, Entwurf,
Bewertung, Freigabe, Ausführung und Lernen. Die UI wird deshalb aufgaben- und
zustandsorientiert aufgebaut und nicht als Sammlung maximal dichter Formulare.

Fremde Produktoberflächen dienen nur dem Funktionsabgleich. Layout, Interaktion,
Benennung, visuelle Hierarchie und Komponenten entstehen eigenständig im Meridian-
System. Eine Spezialseite darf keine zweite UI-Architektur einführen.

## 2. Verbindliche Laufzeitkette

```text
ScreenDefinition
  → RenderPlan / Schema Compiler
  → useUniversalMaskRuntime
  → UniversalMaskRenderer
  → Renderer Library + ActionRuntime + WorkflowRuntime
```

| ID | UI-Regel |
|---|---|
| FEED-UI-001 | Jede produktive Maske besitzt eine native `ScreenDefinition`; kein manuell duplizierter Seitenrahmen. |
| FEED-UI-002 | `layout.floorplan`, `density`, `contextRail` und `tableProfile` sind Meridian-Metadaten, keine lokale CSS-Entscheidung. |
| FEED-UI-003 | Mutationen laufen über deklarierte Actions und CommandEndpoints mit validate → dry-run → propose → execute. |
| FEED-UI-004 | Workflowstatus, Blocking Reasons und erlaubte Übergänge stammen aus dem Vertrag. |
| FEED-UI-005 | Fachliche Warnungen erklären Auswirkung, Evidenz und Abhilfe; Farbe allein transportiert keine Bedeutung. |
| FEED-UI-006 | Die primäre Aktion ist pro Zustand eindeutig; gefährliche Aktionen stehen nie direkt neben ihr. |
| FEED-UI-007 | Tabellen behalten Spalten-, Filter- und Dichtepräferenzen pro Rolle, nicht pro Einzelroute. |
| FEED-UI-008 | Mobile Stallmasken optimieren Einhandbedienung, große Ziele und Offlinefähigkeit; Desktopeditoren optimieren Vergleich und Präzision. |
| FEED-UI-009 | KI-Ausgaben sind Vorschläge mit Quellen, Konfidenz und Übernahmeaktion; keine simulierte Gewissheit. |
| FEED-UI-010 | Leere, ladende, eingeschränkte, fehlerhafte und konfliktbehaftete Zustände sind Teil jeder Definition. |

## 3. Informationsarchitektur

```text
Fütterung
├── Überblick
├── Betriebe & Herden
├── Futtermittel
│   ├── Stammdaten
│   ├── Analysen
│   └── Preise & Verfügbarkeit
├── Rationen
│   ├── Worklist
│   ├── Editor
│   ├── Variantenvergleich
│   └── Freigaben
├── Planung & Stall
│   ├── Kalender
│   ├── Mischanweisungen
│   └── Ausführung
├── Controlling
│   ├── Soll/Ist
│   ├── Leistung & Gesundheit
│   └── Kosten & Nachhaltigkeit
├── Beratung
└── Integrationen
```

Der globale Betrieb-/Herden-/Gruppenkontext bleibt beim Wechsel zwischen Masken
erhalten. Ein sichtbarer Scope-Chip verhindert Bearbeitung im falschen Betrieb.

## 4. Gemeinsame Zustände

| Zustand | Darstellung | Erlaubte Aktion |
|---|---|---|
| loading | Skeleton in echter Layoutgeometrie | abbrechen/navigieren |
| empty | fachlicher Leerzustand mit nächstem Schritt | anlegen/importieren |
| ready | Daten und Aktualitätszeitpunkt | rollenabhängig |
| dirty | persistente Änderungsleiste | speichern/verwerfen |
| validating | Felder bleiben lesbar, Validierung läuft | nicht doppelt senden |
| blocked | Blocking-Reason-Rail, betroffene Felder verlinkt | Ursache beheben |
| conflict | Server-/Clientvergleich | neu laden oder kontrolliert übernehmen |
| offline | lokaler Status und Syncwarteschlange | offlinefähige Commands |
| degraded | Datenquelle veraltet/teilweise | mit Hinweis weiter oder sperren |
| forbidden | kein Existenzdetail fremder Objekte | zum erlaubten Scope |
| error | Korrelation, Retry und sichere Rückkehr | wiederholen |

## 5. Maskenübersicht

| ID | Maske | Floorplan | Primäre Rolle | Release |
|---|---|---|---|---|
| FEED-MASK-001 | Fütterungs-Cockpit | cockpit | farmer/advisor | A |
| FEED-MASK-002 | Betriebs- und Herdenstruktur | master-detail | admin/advisor | A |
| FEED-MASK-003 | Fütterungsgruppe | object-page | advisor | A |
| FEED-MASK-004 | Futtermittel-Worklist | list-report | advisor/farmer | A |
| FEED-MASK-005 | Futtermittel-Detail | object-page | advisor | A |
| FEED-MASK-006 | Analyse-Worklist und Import | list-report | analyst/advisor | A |
| FEED-MASK-007 | Analyse-Prüfung | object-page | analyst/approver | A |
| FEED-MASK-008 | Rations-Worklist | list-report | advisor/farmer | A |
| FEED-MASK-009 | Rationseditor | split-workbench | advisor | A |
| FEED-MASK-010 | Variantenvergleich | comparison | advisor/farmer | A |
| FEED-MASK-011 | Freigabe-Cockpit | workflow-cockpit | approver | A |
| FEED-MASK-012 | Fütterungskalender | planning-board | farmer/operator | B |
| FEED-MASK-013 | Mischanweisung | execution | operator | B |
| FEED-MASK-014 | Mobile Fütterungsausführung | mobile-execution | operator | B |
| FEED-MASK-015 | Soll-Ist-Cockpit | analytical-cockpit | advisor/farmer | B |
| FEED-MASK-016 | Leistung/Gesundheit | analytical-cockpit | advisor/vet | C |
| FEED-MASK-017 | Kosten/Nachhaltigkeit | analytical-cockpit | farmer/controller | C |
| FEED-MASK-018 | Beratungsfall | object-page | advisor/farmer | A |
| FEED-MASK-019 | Integrations-Cockpit | operations-cockpit | admin | B |
| FEED-MASK-020 | Connector-Setup | wizard | admin | B |
| FEED-MASK-021 | Reportcenter | list-report | advisor/farmer | B |
| FEED-MASK-022 | Regelwerks-/Einheiteninfo | reference | advisor/analyst | A |

## 6. Detailkatalog

### FEED-MASK-001 — Fütterungs-Cockpit

| Aspekt | Vertrag |
|---|---|
| Zweck | Tagesrelevante Entscheidungen bündeln: Datenlücken, Freigaben, Fütterung, Abweichungen. |
| Rollen | Farmer eigener Betrieb; Advisor per Grant; Approver; Operator mit Ausführungssicht. |
| Eingaben | Scope, Zeitraum, Tiergruppe, Kennzahlenprofil; keine Stammdatenpflege im Cockpit. |
| Validierung | Zeitraum max. 366 Tage; Scope autorisiert; Aktualität je Datenquelle sichtbar. |
| Aktionen | `Neue Ration`, `Analyse importieren`, `Freigaben prüfen`, `Heute füttern`. |
| Workflow | Aufmerksamkeit → Ursache öffnen → Entscheidung/Aufgabe → Wirksamkeit verfolgen. |
| Rechte | Karten und Kennzahlen werden serverseitig nach Scope gefiltert. |
| Navigation | Jede Karte öffnet eine vorgefilterte Worklist oder das konkrete Objekt. |
| Zustände | leerer Pilotbetrieb, veraltete Daten, blockierende Analyse, offene Freigabe, normal. |
| Context Rail | Datenaktualität, kritische Findings, offene Aufgaben, letzte Änderungen. |

```text
┌ Betrieb / Herde / Gruppe ───────── Zeitraum ── Aktualität ┐
│ 3 Entscheidungen heute │ 1 Freigabe │ 2 Datenlücken      │
├─────────────────────────────────────┬─────────────────────┤
│ Rationen & Abweichungen             │ Kontext / Aufgaben  │
│ Trend, Priorität, Ursache, CTA       │ Evidenz, Fälligkeit │
├─────────────────────────────────────┴─────────────────────┤
│ Tagesplan und letzte Ausführungen                          │
└────────────────────────────────────────────────────────────┘
```

### FEED-MASK-002 — Betriebs- und Herdenstruktur

| Aspekt | Vertrag |
|---|---|
| Zweck | Betrieb, Standorte, Herden, Gruppen und Zugriffe in einem Strukturbaum verwalten. |
| Rollen | Admin, Betriebsverantwortlicher; Advisor lesend bzw. `advise`. |
| Eingaben | Name, Partnerreferenz, Land, Zeitzone; Standort; Herde; Produktionsrichtung. |
| Validierung | Tenant-/Betriebsgleichheit, Zeitzone, eindeutige externe Referenzen, keine Zyklen. |
| Aktionen | aktivieren, Standort/Herde/Gruppe anlegen, verschieben, archivieren, Grant verwalten. |
| Workflow | draft → active → suspended/archived; Partneraktivierung zeigt Herkunft. |
| Rechte | Grantverwaltung ausschließlich Admin; Advisor sieht nur zugewiesene Knoten. |
| Navigation | Baum links, Objektseite Mitte, Rechte/Audit rechts. |
| Zustände | unvollständige Struktur, aktiver Betrieb, externer Link gebrochen, archiviert. |
| Context Rail | Herkunft, Datenverbindungen, Grants, Audit. |

### FEED-MASK-003 — Fütterungsgruppe

| Aspekt | Vertrag |
|---|---|
| Zweck | Leistungs- und Bedarfsprofil einer operativen Tiergruppe pflegen. |
| Rollen | Farmer, Advisor; Provider-Sync als kontrollierte Quelle. |
| Eingaben | Tierart/-klasse, Anzahl, Masse, DIM, Laktation, Milchziel, System, Standort. |
| Validierung | nichtnegative Werte, plausible Klassenbereiche, Herdzuordnung, Stichtag. |
| Aktionen | speichern, Profil versionieren, aktive Ration öffnen, Gruppenzugang prüfen. |
| Workflow | Profilentwurf → validiert → gültig; neue Daten erzeugen neue Profilversion. |
| Rechte | Advisor `advise`; externe Tier-Level-Daten nur bei Consent. |
| Navigation | aus Strukturbaum, Rationseditor, Controlling; zurück mit erhaltenem Scope. |
| Zustände | keine Tiere, Syncabweichung, fehlende Leistungsdaten, vollständig. |
| Context Rail | aktive Ration, letzte Provideraktualität, Datenqualitätsfindings. |

**Lieferstand FEED-CORE-016:** native ScreenDefinition `agrar/feeding-group`
mit ObjectPage-Floorplan, Audit-Rail, Stammdaten-/Leistungs-/Historien-Tabs und
optimistischem Revisionsdialog. Die Rations-Worklist zeigt eine grant-gefilterte
Tiergruppentabelle und öffnet die ObjectPage per stabiler Deep-Link-Route.

### FEED-MASK-004/005 — Futtermittel-Worklist und Detail

| Aspekt | Worklist | Detail |
|---|---|---|
| Zweck | Materialien nach Handlungsbedarf finden | Stamm, Analyse, Preis und Verfügbarkeit zusammenführen |
| Rollen | Farmer, Advisor, Analyst, Einkauf lesend | Advisor/Farmer; Analyst für Analysebezug |
| Eingaben | Suche, Kategorie, Readiness, Standort | Code, Name, Kategorie, Basis, Dichte, Artikel-/Lieferantlink |
| Validierung | nur erlaubte Filter/Sortierung | eindeutiger Code, Einheiten, Tenant-/Businessreferenzen |
| Aktionen | anlegen, exportieren, Sammelprüfung | speichern, archivieren, Preis/Analyse ergänzen |
| Workflow | auswählen → Detail/Readiness | draft → active → archived |
| Rechte | Preise rollenabhängig maskiert | Änderungen `advise`; Bestandsbuchung extern |
| Navigation | Zeile öffnet Detail, Analyse oder Readiness | Tabs Überblick, Analysen, Preise, Verwendung, Audit |
| Zustände | leer, Filter ohne Treffer, stale, teilweise | ohne Analyse, Preis fehlt, gesperrt, aktiv |
| Rail | Filterchips, gespeicherte Sichten | Readiness, letzte Änderung, verwendende Rationen |

### FEED-MASK-006/007 — Analyse-Worklist, Import und Prüfung

| Aspekt | Vertrag |
|---|---|
| Zweck | Labor-/Dateiimporte in einen nachvollziehbaren freigegebenen Analysevertrag überführen. |
| Rollen | Analyst, Advisor, Approver; Farmer lesend. |
| Eingaben | Datei/Labor, Probe, Material, Datumswerte, Mapping, Werte, Methode, Einheit. |
| Validierung | Dateityp/-größe, Virusscan, Materialmapping, Einheit, Wertebereich, Pflichtwerte, Duplikathash. |
| Aktionen | hochladen, Mapping bestätigen, validieren, zurückweisen, freigeben, ersetzen. |
| Workflow | uploaded → mapped → draft → validated → released/superseded/rejected. |
| Rechte | Import `advise`; Release getrennte Freigabeberechtigung; Originaldownload geloggt. |
| Navigation | Jobliste → Mappingfehler → Analyseprüfung → betroffenes Material/Rationen. |
| Zustände | Upload läuft, Quarantäne, Mapping offen, Warnungen, blockiert, freigegeben. |
| Context Rail | Dokumentvorschau, Provenienz, Regel-Findings, Vorgängerversion. |

```text
┌ Probe / Material / Labor ─────────────── Status: validiert ┐
├ Nährstoffwerte ───────────────────┬ Original & Provenienz ┤
│ Wert | Einheit | Bereich | Befund │ Dokumentvorschau      │
│ ...                               │ Mapping / Methoden     │
├───────────────────────────────────┴────────────────────────┤
│ [Zurückweisen]                    [Analyse freigeben]      │
└────────────────────────────────────────────────────────────┘
```

### FEED-MASK-008 — Rations-Worklist

| Aspekt | Vertrag |
|---|---|
| Zweck | Rationen nach Gruppe, Status, Wirksamkeit und Handlungsbedarf steuern. |
| Rollen | Farmer, Advisor, Approver, Operator lesend aktive Versionen. |
| Eingaben | Suche, Betrieb/Herde/Gruppe, Status, Startdatum, Finding-Severity. |
| Validierung | Whitelist-Sortierung/-Filter; Scope serverseitig. |
| Aktionen | neue Ration, aus Version kopieren, vergleichen, Freigabe öffnen. |
| Workflow | Entwurf → Review → Freigabe → Planung/Aktivierung → Archiv. |
| Rechte | CTA passt sich Rolle und Grant an; keine ausgegrauten Datenleaks. |
| Navigation | Zeile öffnet Editor/Lesesicht; Statuschip öffnet Timeline. |
| Zustände | keine Rationen, nur archiviert, blockiert, Freigabe offen, aktiv. |
| Context Rail | gespeicherte Sicht, offene Blocker, zuletzt bearbeitet. |

### FEED-MASK-009 — Rationseditor

| Aspekt | Vertrag |
|---|---|
| Zweck | Ration präzise erstellen und Wirkung während der Bearbeitung verstehen. |
| Rollen | Advisor, Farmer; Approver im Review schreibgeschützt. |
| Eingaben | Gruppe/Bedarfsprofil, Material, Analyse, Frisch-/Trockenmasse, Min/Max, Zielmodell. |
| Validierung | Einheiten, positive Mengen, Analyse-Readiness, Verfügbarkeit, Summen, fachliche Regelchecks. |
| Aktionen | Entwurf speichern, Position, optimieren, Variante, bewerten, Review einreichen. |
| Workflow | dirty → validiert → bewertet → in_review; Versionierung statt Überschreiben. |
| Rechte | Advisor `advise`; Optimierung darf nur Candidate vorschlagen; Review sperrt Editor. |
| Navigation | Worklist/Gruppe hinein; Vergleich, Analyse und Finding ohne Kontextverlust öffnen. |
| Zustände | neu, dirty, offline nicht editierbar, Konflikt, blockiert, Review, freigegeben. |
| Context Rail | Kennzahlen, Findings, Kosten, Struktur, Quellenqualität; Dimensionen umschaltbar. |

```text
┌ Gruppe / Bedarfsprofil ─ Version ─ Status ───── [Review] ┐
├ Rationspositionen (flexibel) ──────┬ Bewertung (sticky) ┤
│ Material │ Analyse │ FM │ TM │ €   │ Energie  ✓         │
│ ...                                │ Protein  !         │
│ [+ Position]                       │ Struktur !!        │
├ Zielsetzung / Constraints ─────────┤ Kosten / Umwelt    │
│ [Variante] [Optimieren]            │ Evidenz & Abhilfe  │
└────────────────────────────────────┴─────────────────────┘
```

Die permanente Bewertung ersetzt modale Warnungsfluten. Findings fokussieren die
betroffene Position. Der Editor zeigt progressive Tiefe: Kernspalten zuerst,
Expertenparameter in einer kontrollierten Detailansicht.

### FEED-MASK-010 — Variantenvergleich

| Aspekt | Vertrag |
|---|---|
| Zweck | Zwei bis fünf Versionen anhand gemeinsamer fachlicher Dimensionen entscheiden. |
| Rollen | Farmer, Advisor, Approver. |
| Eingaben | Basis/Varianten, Kennzahlenprofil, Gewichtung nur als Ansicht. |
| Validierung | gleiche Gruppe/Basis; fehlende Werte als unbekannt, nicht nullwertig günstig. |
| Aktionen | Variante als Entwurf übernehmen, Bewertung öffnen, PDF, Entscheidung dokumentieren. |
| Workflow | auswählen → Unterschiede verstehen → Entscheidung begründen → neue Version. |
| Rechte | Preis-/Nachhaltigkeitsdimension rollenabhängig; Übernahme `advise`. |
| Navigation | vom Editor/Worklist; zurück zur exakt gleichen Auswahl. |
| Zustände | unvollständige Bewertung, veraltete Preise, nicht vergleichbare Basis, bereit. |
| Context Rail | Differenztreiber, Trade-offs, KI-Erklärung mit Evidenz. |

### FEED-MASK-011 — Freigabe-Cockpit

| Aspekt | Vertrag |
|---|---|
| Zweck | Fachliche Freigaben effizient und nachweisbar bearbeiten. |
| Rollen | Approver; Advisor als Einreicher; Admin Audit. |
| Eingaben | Entscheidung, Grund, Auflagen, optionales Startdatum. |
| Validierung | Vier-Augen-Policy, keine Blocker, aktuelle Bewertung/Analyse, Separation of Duties. |
| Aktionen | öffnen, Rückfrage, zurückweisen, unter Auflage/final freigeben. |
| Workflow | in_review → approved oder draft; Folgeplanung separat. |
| Rechte | ausschließlich `approve`; Einreicher darf bei SoD nicht selbst freigeben. |
| Navigation | Queue → Reviewpaket → Diff/Evidenz → nächste Queueposition. |
| Zustände | neue Aufgabe, Daten nach Einreichung geändert, Blocker, freigabefähig. |
| Context Rail | Diff zur Basis, Findings, Analyse-/Preisstand, Audit. |

### FEED-MASK-012 — Fütterungskalender

| Aspekt | Vertrag |
|---|---|
| Zweck | Freigegebene Rationen zeitlich Gruppen, Schichten und Mischchargen zuordnen. |
| Rollen | Farmer, Operator, Advisor lesend. |
| Eingaben | Version, Gruppe, Zeitraum, Schicht, Tierzahl, Batch-/Geräteprofil. |
| Validierung | keine unerlaubte Überlappung, Version freigegeben, Gerät/Material bereit. |
| Aktionen | planen, kopieren, verschieben, freigeben, exportieren, stornieren. |
| Workflow | draft → released → exported/executing → completed/cancelled. |
| Rechte | Planung `execute`; Rationsinhalt bleibt unverändert. |
| Navigation | Kalender → Plan → Mischanweisung/Ausführung/Soll-Ist. |
| Zustände | Konflikt, Material fehlt, Export offen, heute, abgeschlossen. |
| Context Rail | Readiness, Gerätestatus, Übergabehinweise. |

### FEED-MASK-013/014 — Mischanweisung und mobile Ausführung

| Aspekt | Vertrag |
|---|---|
| Zweck | Zielmengen sicher in reale Misch- und Fütterungsschritte übersetzen. |
| Rollen | Operator; Farmer im Ausnahmeentscheid. |
| Eingaben | Istmenge, Start/Ende, Charge/Lot, Substitution, Abweichungsgrund, Foto optional. |
| Validierung | klassenspezifische Toleranz, Reihenfolge, Einheit, Lotfreigabe, Doppelausführung. |
| Aktionen | starten, bestätigen, überspringen mit Grund, substituieren, pausieren, abschließen. |
| Workflow | ready → mixing → delivering → completed; exception → review. |
| Rechte | Geräte-/Betriebsscope; Substitution über Schwelle benötigt Bestätigung. |
| Navigation | Tagesliste → Batch → Schritt; nach Abschluss automatisch nächster Batch. |
| Zustände | offline, Waage getrennt, Toleranzwarnung, Blocker, Sync offen, abgeschlossen. |
| Context Rail | Desktop: Batchkontext; mobil: reduzierte Bottom Sheet Details. |

Mobile Mockup:

```text
┌ Stall 2 · Batch 3/6 ───────── 07:42 ┐
│ Maissilage                         │
│ Ziel 1.240 kg      Ist [ 1.218 ] kg│
│ ███████████████████░  -1,8 %       │
│ Lot: MS-2026-14 · QS freigegeben   │
│                                    │
│ [Problem melden]   [Bestätigen]    │
└ Offline: gespeichert · Sync offen ─┘
```

### FEED-MASK-015 — Soll-Ist-Cockpit

| Aspekt | Vertrag |
|---|---|
| Zweck | Abweichungen zwischen Plan, Aufnahme, Kosten und Leistung priorisieren. |
| Rollen | Farmer, Advisor, Controller. |
| Eingaben | Zeitraum, Gruppe, Kennzahlenprofil, Aggregation, Vergleichsbasis. |
| Validierung | Tierzahlgewichtung, Datenabdeckung, Zeitzonen-/Tagesgrenze. |
| Aktionen | Ursache öffnen, Beratungsfall/Aufgabe, Zeitraum vergleichen, Report. |
| Workflow | Signal → Evidenz → Hypothese → Maßnahme → Wirksamkeit. |
| Rechte | Kosten rollenabhängig; Healthdetails nur mit Consent/Scope. |
| Navigation | Trendpunkt → Ausführung/Observation/Rationsversion. |
| Zustände | keine Daten, unvollständige Tierzahl, Provider stale, normal, kritisch. |
| Context Rail | Abdeckung, Quellen, Findings, dokumentierte Maßnahmen. |

### FEED-MASK-016/017 — Leistung, Gesundheit, Kosten, Nachhaltigkeit

| Aspekt | Vertrag |
|---|---|
| Zweck | Wirkung der Fütterung mehrdimensional und ohne Scheinkausalität beurteilen. |
| Rollen | Advisor/Farmer; Vet für Gesundheit; Controller für Kosten. |
| Eingaben | Gruppe, Zeitraum, Laktationssegment, Vergleich, Kennzahlenprofil. |
| Validierung | Mindestabdeckung, gewichtete Aggregation, Schätzwerte markieren. |
| Aktionen | Segmentieren, Evidenz öffnen, Maßnahme/Fall, Report. |
| Workflow | beobachten → korrelieren → fachlich prüfen → handeln → nachmessen. |
| Rechte | personenbezogene Tierdetails minimiert; Kosten-/CO₂-Scope getrennt. |
| Navigation | Kennzahl → Observation → Version/Plan; kein Sackgassen-Dashboard. |
| Zustände | Schätzung, geringe Stichprobe, Datenbruch, normal, kritischer Trend. |
| Context Rail | Datenqualität, Einflussfaktoren, frühere Entscheidungen. |

### FEED-MASK-018 — Beratungsfall

| Aspekt | Vertrag |
|---|---|
| Zweck | Anlass, Evidenz, Entscheidung, Aufgaben und Wirksamkeit als Fallakte verbinden. |
| Rollen | Advisor, Farmer; Vet/Controller per Scope. |
| Eingaben | Anlass, Ziel, Hypothese, Entscheidung, Verantwortlicher, Termin, Ergebnis. |
| Validierung | Betrieb/Gruppe, Verantwortlicher, Fälligkeit; Abschluss braucht Ergebnis. |
| Aktionen | Entscheidung, Aufgabe, Kommentar/Nachtrag, Rationsentwurf, schließen. |
| Workflow | open → investigating → action_planned → monitoring → closed/reopened. |
| Rechte | Teilnehmer/Grant; interne Notizen getrennt von Kundenfreigabe. |
| Navigation | aus Cockpit/Finding; Evidenzlinks öffnen Side Peek statt Kontextverlust. |
| Zustände | neu, wartet auf Daten/Kunde, überfällig, Monitoring, geschlossen. |
| Context Rail | Timeline, Beteiligte, verknüpfte Versionen/Analysen. |

### FEED-MASK-019/020 — Integrations-Cockpit und Connector-Setup

| Aspekt | Vertrag |
|---|---|
| Zweck | Providerverträge sicher konfigurieren und Syncbetrieb transparent steuern. |
| Rollen | Tenantadmin, Integrationsoperator; Advisor Status lesend. |
| Eingaben | Provider, Herd-ID, Basis-URL, Templates, Credential-Referenz, Vertrag, Consent, Cursor. |
| Validierung | URL-Allowlist, Secret nur als Env/Vault-Referenz, Contract/Consent, Dry-run. |
| Aktionen | testen, speichern, aktivieren, Sync, pausieren, Quarantäne retry/dead-letter. |
| Workflow | draft → tested → enabled → live_enabled; degraded/suspended. |
| Rechte | Live-Aktivierung Admin plus Policy; Rohpayload streng begrenzt. |
| Navigation | Übersicht → Verbindung → Runs/Observations/Quarantäne. |
| Zustände | nie getestet, Credentials fehlen, stale, Rate Limit, Fehler, gesund. |
| Context Rail | letzter Cursor, SLA, Fehlerrate, Vertrags-/Consentstand. |

Wizard-Schritte: Provider wählen → Vertrag/Consent → Endpointmapping → Credential-
Test → Mock/Dry-run → Feldmapping → Zeitplan → explizite Live-Freigabe.

### FEED-MASK-021 — Reportcenter

| Aspekt | Vertrag |
|---|---|
| Zweck | Rollenprofilierte, reproduzierbare Beratung-, Stall- und Controllingausgaben. |
| Rollen | Farmer, Advisor, Approver, Operator, Controller. |
| Eingaben | Profil, Scope, Zeitraum, Versionen, Sprache, Ausgabeformat. |
| Validierung | Profilberechtigung, Datenabdeckung, Downloadscope. |
| Aktionen | Vorschau, Job starten, herunterladen, planmäßig erzeugen. |
| Workflow | configured → queued → generated/failed → expired. |
| Rechte | Serverseitige Inhaltsfilter; kurzlebiger Downloadtoken. |
| Navigation | aus Objekt mit vorausgefülltem Scope oder zentral. |
| Zustände | keine Daten, Job läuft, teilweise, bereit, abgelaufen. |
| Context Rail | Eingabechecksumme, Quellenstand, Freigabestatus. |

### FEED-MASK-022 — Regelwerks- und Einheiteninfo

| Aspekt | Vertrag |
|---|---|
| Zweck | Geladene GfE/DLG/NRC-Version, Einheiten und Berechnungsprovenienz erklären. |
| Rollen | alle fachlichen Rollen lesend; Admin kontrolliert Refresh. |
| Eingaben | Regelwerk, Version, Nährstoffdimension, Suche. |
| Validierung | signierte/erlaubte Version; Refresh nie automatisch produktiv aktiv. |
| Aktionen | Details/Änderungen ansehen, Golden-Test-Status, kontrollierten Refresh starten. |
| Workflow | available → validated → active → deprecated/retired. |
| Rechte | Aktivierung getrennte Admin-/Fachfreigabe. |
| Navigation | aus jedem Finding zur konkreten Regelversion. |
| Zustände | aktiv, Update verfügbar, Validierung fehlgeschlagen, veraltet. |
| Context Rail | Quellenreferenz, Prüfsumme, Testnachweis, Gültigkeitsbereich. |

## 7. Responsive Strategie

| Breite | Verhalten |
|---|---|
| ≥ 1440 px | Hauptbereich plus persistente Context Rail; Tabellen mit Expertenprofil. |
| 1024–1439 px | Rail einklappbar; Split-Workbench bleibt zweispaltig. |
| 768–1023 px | Rail als Drawer; Editor wechselt zwischen Positionen und Bewertung. |
| < 768 px | nur freigegebene mobile Aufgaben; komplexer Rationseditor ist Lesesicht. |

Mobile unterstützt Stallausführung, Aufgaben, Freigabe-Review und Kennzahlen. Eine
komplexe Optimierung auf kleinem Display wird nicht durch gequetschte Desktop-UI
simuliert.

## 8. Accessibility

- WCAG 2.2 AA; vollständige Tastaturbedienung auf Desktop.
- Sichtbarer Fokus; Skiplinks zu Hauptbereich und Context Rail.
- Tabellen besitzen Caption, Headerbeziehungen und zugängliche Sortierung.
- Charts haben Datentabelle/Zusammenfassung und unterscheiden Linien zusätzlich
  durch Muster/Form.
- Fehler werden am Feld und in einer verlinkten Zusammenfassung ausgegeben.
- Live-Regionen melden Validierung, Jobstatus und Offline-Sync zurückhaltend.
- Touchziele mindestens 44 × 44 CSS-Pixel in Stallmasken.

## 9. Performance und Telemetrie

ScreenDefinition und RenderPlan sind cachebar. Worklists laden seitenweise;
Editorberechnungen werden entprellt und abbrechbar. Telemetrie misst keine
Nährstoff-/Tierdetails, sondern technische Dauer, Fehlercode, Masken-ID, Aktion,
Status und anonymisierte Größenklasse.

Ziele: Shell < 1,5 s p75 im Pilotnetz, interaktive Worklist < 2,5 s, lokale
Feldeingabe < 100 ms, Bewertungsfeedback < 500 ms bei synchroner Berechnung.

## 10. Abnahme je Maske

1. Native ScreenDefinition besteht Schema-, Layout-, Workflow- und Action-Gates.
2. Rollen-/Granttests prüfen sichtbare Daten und erlaubte Commands.
3. Empty/loading/error/conflict/degraded/blocked sind visuell und per Test belegt.
4. Playwright deckt Happy Path und kritischen Negativpfad ab.
5. Axe/WCAG-Gate sowie Tastatur- und Fokusablauf sind grün.
6. Kein lokaler Sonderrahmen, keine parallele Form-/Tabellen-/Action-Runtime.
7. Screenshot-/Golden-Review prüft Hierarchie, Dichte und Responsive-Stufen.
8. Fachliche Begriffe und IDs stimmen mit DDD, API und Workflowkatalog überein.

## 11. Eigenständigkeits- und Rechteregel

Nicht übernommen werden fremde Screenshots, Texte, Icons, CSS, Navigationsbäume,
Interaktionsdetails oder visuelle Signaturen. Zulässig ist ausschließlich die
abstrakte Erkenntnis, dass ein fachlicher Anwendungsfall benötigt wird. Seine
Lösung folgt VALEO-Tokens, Meridian-Floorplans, eigener Informationsarchitektur
und dokumentierten Nutzerzielen.

## 12. Ausgelieferte Maske FEED-CORE-017

`agrar/feeding-reference-data` ist ein nativer Meridian-ListReport mit zwei
virtuellen Tabellen fuer Naehrstoffe und Einheiten. Er zeigt Code, Bezugsbasis,
Dimension, Wertebereich, Herkunft und Revision statt eine weitere freie
Agrar-Spezialmaske einzufuehren. Route:
`/portal/rationsoptimierung?view=reference-data`. Der Screen ist read-only;
Aenderungen werden erst nach einem eigenen Governance-Workflow freigeschaltet.

## 13. Futtermittel-ObjectPage FEED-CORE-018

`futtermittel/einzelfuttermittel` verwendet keine generischen Masken-Stubs mehr.
Kopf, Naehrstoffwerte, Lieferprodukte/Preise und Revisionen kommen aus dem echten
Feed-Catalog. Die bestehende native Route
`/futtermittel/einzelfuttermittel/{id}` rendert die zentrale Runtime; nur der
begruendete Revisionsdialog ist ein Domain-Overlay. Die Liste navigiert fuer
bestehende Datensaetze auf diese ObjectPage statt in die freie Legacy-Maske.

## 14. Analyse-Worklist und -ObjectPage FEED-CORE-019

`futtermittel/analysen` ist die expertendichte Worklist mit Suche, Status,
Aktivkennzeichen und direkter Navigation. `futtermittel/analyse` ist eine
ObjectPage mit Probe/Freigabe, Original-/Rechenwerten, Plausibilitaetsbefunden
und unveraenderlichem Audit. Beide laufen durch ScreenDefinition -> RenderPlan
-> useUniversalMaskRuntime -> UniversalMaskRenderer. Datei-Vorschau,
Validierung und begruendete Freigabe sind schmale fachliche Overlays; die
produktive Route lautet `/futtermittel/grundfutteranalysen[/{id}]`.

## 15. Rationseditor-Grenzen FEED-EDITOR-024

Die Positionsflaeche des Rationseditors zeigt Menge, Minimum und Maximum in
kompakten numerischen Spalten. Grenzbefunde erscheinen in der permanenten
Bewertungsleiste mit vierstufiger Prioritaet, verursachendem Futtermittel und
konkreter Abhilfe. Ein Klick fokussiert die Mengenposition; Speichern bewahrt
die Grenzen im append-only Versionssnapshot. Die bestehende Split-Workbench
bleibt die zentrale Editor-Journey und fuehrt keine neue Maskenarchitektur ein.

## 16. Betriebsakte FEED-EDITOR-025

`agrar/feeding-business` ist eine native Meridian-ObjectPage unter
`/futtermittel/fuetterungsbetrieb/{id}`. Die Arbeitsuebersicht trennt Datenlage,
Lifecycle und Analysereife; Lazy-Tabs zeigen Tiergruppen, Rationen, Befunde und
unveraenderliche Vorlagen. Tabellenzeilen fuehren in bestehende Detail-Journeys.
Anlegen und Anwenden einer Vorlage sind schmale Overlays; Layout, Tabellen und
Zustandssemantik bleiben in ScreenDefinition, RenderPlan und zentraler Runtime.

## 17. FeedingPlan-ObjectPage und mobile Stallroute FEED-PLAN-027

`agrar/feeding-plan` ist eine native ObjectPage unter
`/futtermittel/fuetterungsplan/{id}`. Kopf und Statusbanner zeigen current,
scheduled oder stale als Text; Tabs enthalten Plan/Gueltigkeit, dosierbare
Mischfolge und Provenienz. Browserdruck blendet die interaktive Runtime aus und
druckt Plan-ID, Quellversion, Gueltigkeit, Druckzeitpunkt und Rundungsdelta.

`/futtermittel/fuetterungsdokumentation-mobil` liest ausschliesslich
`/feeding/plans/current`. Der Offline-Fallback ist an Planversions-ID und
Cachevertrag v2 gebunden. Unbekannte Zielmengen bleiben sichtbar und blockieren
die Ist-Erfassung; geplante/veraltete Versionen werden nicht angeboten.
