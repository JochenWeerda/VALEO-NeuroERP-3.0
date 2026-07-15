---
title: "Fütterungsberatung — UI/UX-Fachkonzept"
type: reference
audience: [produkt, ux, frontend, fachlich, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
sources:
  - docs/specs/feeding/07-maskenkatalog.md
  - docs/design/frontend-design-skill-audit.md
  - docs/architecture/uix/universal-mask-runtime-status.md
---

# 10 — UI/UX-Fachkonzept

## 1. Leitentscheidung: Spezialmaske neu denken

Die Kernfrage lautet nicht „Wie bilden wir eine Agrar-Spezialsoftware nach?“,
sondern „Welche Entscheidung muss diese Rolle jetzt sicher treffen?“. Eine dichte
Spezialmaske ist nur dort sinnvoll, wo Experten wiederholt viele abhängige Werte
vergleichen. Sie ist ungeeignet als globale Produktstruktur.

VALEO verwendet deshalb drei aufgabengerechte Interaktionsmodi:

| Modus | Einsatz | Charakter |
|---|---|---|
| Entscheiden | Cockpit, Review, Beratung | Priorität, Evidenz, nächste Aktion |
| Bearbeiten | Ration, Analyse, Stammdaten | präzise, tabellarisch, validiert |
| Ausführen | Stall, Mischen, mobile Aufgabe | linear, große Ziele, offlinefähig |

Diese Modi teilen Tokens, Renderer, Commands und Navigation, unterscheiden aber
Informationsdichte und Fokus. Damit bleibt das System konsistent, ohne jedem Nutzer
dieselbe universelle Megamaske aufzuzwingen.

## 2. UX-Ziele

| ID | Ziel | Messgröße |
|---|---|---|
| FEED-UX-001 | Handlungsbedarf in unter 10 Sekunden erkennen | First Meaningful Decision |
| FEED-UX-002 | Neue Standardration ohne Handbuch erstellen | Erfolgsquote Usability-Test ≥ 90 % |
| FEED-UX-003 | Finding bis zur Ursache nachvollziehen | ≤ 2 Kontextwechsel |
| FEED-UX-004 | Keine stille Daten-/Einheitenunsicherheit | 100 % unsichere Werte markiert |
| FEED-UX-005 | Freigabeentscheidung reproduzierbar | Evidenz-/Diff-Vollständigkeit |
| FEED-UX-006 | Stallaufgabe auch offline abschließen | Sync-Erfolg und Konfliktrate |
| FEED-UX-007 | Experten effizient halten | Tastaturflow und Zeit pro Rationsänderung |
| FEED-UX-008 | Anfänger nicht überfordern | progressive Offenlegung, Fehlerrate |

## 3. Mentales Modell

Das zentrale Objekt ist nicht das Futtermittel und nicht die Maske, sondern die
Entscheidungskette:

```text
Betrieb → Herde → Gruppe → Bedarf
       + Material → Analyse → Preis/Verfügbarkeit
       = Rationsversion → Bewertung → Freigabe
       → Plan → Ausführung → Soll/Ist → Beratung → nächste Version
```

Der aktuelle Scope ist dauerhaft sichtbar. Jede Kennzahl zeigt, auf welchen
Zeitpunkt, welche Gruppe, Version und Quelle sie sich bezieht.

## 4. Meridian-Fundament

ScreenDefinition ist die einzige Maskenquelle. Floorplan, Dichte, Context Rail und
Tabellenprofil werden zentral kompiliert. Lokale Seiten dürfen Tokens kombinieren,
aber keinen zweiten AppShell-, Formular-, Tabellen-, Dialog- oder Action-Stack
einführen.

| Tokenklasse | Verwendung |
|---|---|
| Farbe | semantische Zustände; keine rein dekorative Fachcodierung |
| Typografie | klare Hierarchie, tabellarische Zahlen mit stabiler Ausrichtung |
| Raum | Dichteprofile `comfortable`, `compact`, `operational` |
| Radius/Schatten | sparsam; Struktur durch Layout statt Card-in-Card |
| Motion | Zustandskontinuität, maximal zurückhaltend, Reduced Motion |
| Icon | bestehende Bibliothek; Bedeutung immer mit Label/Tooltip |

## 5. Navigation

### 5.1 Ebenen

1. globale Produktshell: Portal, Domain, Suche, Profil;
2. Feeding-Navigation: Überblick, Daten, Rationen, Stall, Controlling, Beratung;
3. fachlicher Scope: Betrieb, Herde, Gruppe;
4. Objektpfad: Worklist → Objekt/Version → Unteransicht;
5. Context Rail: Evidenz, Workflow, Aufgaben, Audit.

Breadcrumbs bilden Objektbeziehung, nicht Browserhistorie. „Zurück“ erhält Filter,
Sortierung, Scrollposition und gewählten Scope.

### 5.2 Globale Suche

Suche findet Betriebe, Gruppen, Materialien, Analysen, Rationen und Fälle nur im
autorisierten Scope. Treffer zeigen Typ, Betrieb, Status und wichtigsten Kontext;
gleiche Namen bleiben unterscheidbar. Keine Rohpayload- oder Tiergesundheitssuche
ohne expliziten Scope.

## 6. Informationsdichte

| Profil | Nutzer | Verhalten |
|---|---|---|
| comfortable | gelegentlicher Farmer | größere Zeilen, Kernspalten, mehr Erklärung |
| compact | Advisor/Analyst | mehr Spalten, Tastaturfokus, gespeicherte Sichten |
| operational | Stalloperator | große Aktionen, linearer Schritt, wenig Navigation |

Dichte ist Rollenpräferenz, kein separates Produkt. Kritische Hinweise und
Touchziele werden durch „compact“ nicht unlesbar klein.

## 7. Rationseditor als Workbench

Der Editor folgt fünf Fragen:

1. Für wen wird gerechnet?
2. Welche Datenstände fließen ein?
3. Welche Mengen/Constraints werden gesetzt?
4. Welche Wirkung und Risiken entstehen?
5. Was ist der nächste kontrollierte Zustand?

Positionen belegen den größten Bereich; Bewertung bleibt sichtbar. Ein Finding
fokussiert die betroffene Position und erklärt Grenzwert, Regelversion und Abhilfe.
Optimierung öffnet keinen magischen Ein-Klick-Dialog, sondern zeigt Ziel,
Constraints, ausgeschlossene Inputs und Candidate-Differenzen.

### 7.1 Eingabeverhalten

- Dezimaltrennzeichen werden lokal akzeptiert, kanonisch gespeichert.
- Einheit steht am Feld und ist nicht Teil frei eingegebenen Textes.
- Tab/Shift-Tab folgt visueller Tabellenreihenfolge.
- Enter bestätigt Zelle, fügt aber nicht versehentlich eine neue Version an.
- Bulk Paste wird vor Übernahme als tabellarischer Diff validiert.
- Undo/Redo wirkt auf Arbeitsentwurf, nicht auf freigegebene Versionen.
- Autosave zeigt Zeitpunkt und Status; fachlicher Versionssave bleibt explizit.

### 7.2 Bewertung

Bewertung ist hierarchisch:

```text
Gesamtstatus
├── Versorgung
├── Struktur/Pansengesundheit
├── Mineralien
├── Kosten/Verfügbarkeit
└── Nachhaltigkeit/Datenqualität
```

Der Gesamtstatus verschweigt keine blockierende Unterdimension. Ampelfarbe wird
durch Text, Symbol und Anzahl ergänzt. Fachlich konkurrierende Ziele erscheinen als
Trade-off, nicht als eindimensionaler Score.

## 8. Warnungsdesign

| Stufe | Platzierung | Nutzerreaktion |
|---|---|---|
| info | inline/rail | optional prüfen |
| warning | inline plus Summary | prüfen/begründen |
| critical | persistent, Aktion hervorgehoben | Fachentscheidung erforderlich |
| blocking | Fokus + verlinkte Summary | Ursache beheben; Command gesperrt |

Eine Warnung beantwortet: Was ist passiert? Was ist betroffen? Wie sicher ist die
Aussage? Welche Quelle/Grenze gilt? Was kann ich tun? Wiederholte identische
Warnungen werden gruppiert, aber Blocker nicht versteckt.

## 9. Datenqualität und Provenienz

Jeder berechnungsrelevante Wert besitzt Herkunftsklasse:

- gemessen;
- vom Labor/Provider gemeldet;
- manuell bestätigt;
- abgeleitet;
- geschätzt;
- Default;
- veraltet/unbekannt.

Die UI zeigt nicht überall technische Metadaten, aber stellt sie über Wertdetails
und Context Rail erreichbar bereit. Schätzungen sind visuell anders als Messwerte.
„Zuletzt synchronisiert“ ist pro Quelle, nicht pauschal für die ganze Seite.

## 10. Dialoge und irreversible Aktionen

Bestätigung ist nur für Risiko, nicht für Routine. Der ActionRuntime-Ablauf:

1. validieren;
2. Dry-run mit Auswirkungen;
3. proposed changes menschenlesbar anzeigen;
4. gegebenenfalls Grund/Freigabe erfassen;
5. ausführen;
6. Ergebnis, Audit und nächste Aktion rückmelden.

Freigabe, Aktivierung, Export, Grant und Storno zeigen konkretes Objekt, Version,
Betrieb, Zeitpunkt und Nebenwirkung. Generische „Sind Sie sicher?“-Dialoge sind
nicht ausreichend.

## 11. Tabellen und Visualisierungen

Tabellen unterstützen stabile Sortierung, Filterchips, Spaltenprofile, angeheftete
Schlüsselspalten, Summen mit Einheit und Zeilenaktionen ohne Hover-Zwang.

Charts werden nur genutzt, wenn Trend, Verteilung oder Vergleich leichter erkennbar
wird. Jeder Chart besitzt:

- sprechenden Titel und Zeitraum;
- Einheit und Baseline/Ziel;
- Datenabdeckung und Schätzstatus;
- zugängliche Textzusammenfassung/Tabelle;
- Drilldown zur Observation;
- keine abgeschnittene Achse, die Unterschiede irreführend vergrößert.

## 12. Responsive und Offline

Komplexe Bearbeitung bleibt Desktop/Tablet. Mobil priorisiert Tagesliste,
Mischschritt, Aufgabe, Freigabe-Review und Signal. Offlinefähige Commands werden
lokal mit Command-ID, erwarteter Version und Zeit gespeichert. Die UI unterscheidet
„lokal gespeichert“, „zur Synchronisation vorgemerkt“, „synchronisiert“ und
„Konflikt“.

Konflikte werden nicht automatisch last-write-wins gelöst. Der Nutzer sieht
Serverstand, lokalen Auftrag und sichere Optionen.

## 13. KI-Interaktion

Agentenvorschläge erscheinen dort, wo ihre Evidenz sichtbar ist. Ein Vorschlag
enthält:

- Ziel und kurze Begründung;
- betroffene Objekte/Felder;
- Quellen und Datenstand;
- Konfidenz/Unsicherheit;
- erwartete Wirkung und Risiken;
- „als Entwurf übernehmen“, „verwerfen“ oder „prüfen“.

Agententext darf keine fachliche Warnung verdecken. Nutzer können jederzeit zur
deterministischen Regel-/Berechnungsansicht wechseln. Übernommene Vorschläge werden
als menschlich bestätigte Commands auditiert.

## 14. Accessibility

- WCAG 2.2 AA als Releasegate.
- Logische Landmarken und Überschriften; Skiplinks.
- vollständige Tastaturbedienung und sichtbarer Fokus.
- Fokus bleibt nach dynamischer Validierung stabil.
- Fehlerzusammenfassung verlinkt Felder.
- Status nie nur über Farbe; Kontrast und Reduced Motion.
- Tabellen-/Chartalternativen für Screenreader.
- Touchziele mindestens 44 × 44 CSS-Pixel in operational/mobile.
- Fachabkürzungen beim ersten Auftreten erklärt und im Glossar erreichbar.

## 15. UX-Research-Programm

| Phase | Teilnehmer | Aufgabe | Erfolgskriterium |
|---|---|---|---|
| Konzept | 5 Advisor, 5 Farmer | Informationsarchitektur/Card Sort | ≥ 80 % Kernobjekte korrekt |
| Prototype | 6 je Rolle | Ration/Analyse/Freigabe | ≥ 90 % ohne Moderation |
| Stallpilot | 8 Operator | Batch offline ausführen | keine sicherheitskritische Fehlbedienung |
| Controlling | 6 Advisor | Abweichung zur Ursache | median ≤ 2 Minuten |
| Accessibility | Tastatur/SR-Nutzer | Kernflows | keine kritischen Barrieren |
| Pilotbetrieb | reale Rollen | 4 Wochen Telemetrie/Interviews | definierte KPI-Verbesserung |

Researchdaten werden datensparsam erhoben. Keine Sessionaufzeichnung mit Tier-
Gesundheitsdaten ohne Einwilligung und Redaktionskonzept.

## 16. UX-Metriken

- Task Success und Time-on-Task je Kernworkflow;
- Validierungsfehler pro Feld und Wiederholung;
- Abbruch-/Rücksprungrate;
- Zeit bis Ursache bei Finding;
- Quote verworfener/übernommener Agentenvorschläge;
- Freigabe-Durchlaufzeit ohne Wartezeitverwechslung;
- Offline-Konflikt-/Syncfehlerrate;
- Warnungsbestätigungen ohne Evidenzöffnung als mögliches Alarmmüdigkeitssignal;
- A11y-Verstöße und Tastaturerfolg.

Metriken optimieren nicht blind auf Klickzahl. Ein zusätzlicher Evidenzschritt kann
bei Freigaben bessere UX und Sicherheit sein.

## 17. Nicht akzeptiert

- eine universelle Vollbildmaske für alle Rollen;
- Dashboardkarten ohne klare Aktion oder Drilldown;
- nur farbcodierte Ampeln;
- versteckte Einheiten, Quellen oder Datenstände;
- KI-Chat als Ersatz für deterministische Fachfunktionen;
- Desktopeditor auf Mobil nur verkleinern;
- lokales CSS/Komponentenfork für Feeding;
- fremde Screens, Texte, Icons oder visuelle Signaturen kopieren.

## 18. Abnahme

1. Kernflows bestehen rollenbezogene Usability-Tests.
2. Jede Maske besteht Meridian-, A11y-, Responsive- und State-Gates.
3. Kritische Commands zeigen konkrete Auswirkungen und Auditgrund.
4. Datenqualität/Provenienz ist bis zur Quelle nachvollziehbar.
5. Expertendichte und Einsteigerführung nutzen dieselbe Architektur.
6. Offlinezustände und Konflikte sind testbar und verständlich.
7. UX-Metriken sind datensparsam und besitzen Baseline/Ziel.

