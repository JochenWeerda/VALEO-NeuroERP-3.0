---
title: Native Masken- und Antwortvertraege - Reparatur 2026-10-07
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-10-07
---

# Native Masken- und Antwortvertraege

Ausgehend von den roten Laeufen auf `00de664df` und `3e7142c48` wurden
bestaetigte Vertragswidersprueche behoben; keine Sicherheits-/Coverage-Schwellen
oder Baselines angehoben. Dateibesitz in drei sofort committeten Claims im
Workboard: Masken-/Antwortvertraege, abgeleitete Titel, Zahlungsfreigabe-Mapping.

## Korrekturen

- Fahrzeug-Loeschen verwendet `high` mit unveraenderter Bestaetigung, zentral in
  Python-Definition und TypeScript-Fallback. `destructive` gehoert nicht zum
  gueltigen Renderer-Vokabular; der widersprechende alte Fahrzeugtest folgt nun
  demselben kanonischen Vertrag.
- Die Spalteninventur respektiert explizites `single`, wie der dokumentierte
  Compiler. Ohne explizite Erklaerung bleibt eine Tabellen-Worklist `listDetail`.
  Transaktion/Cockpit/Wizard bleiben `single`; erlaubtes Vokabular unveraendert.
- Der Bewerbungs-Vertrag prueft vorhandene Einwilligungs-/Loeschaktionen statt
  eine feste Reihenfolge. Die Sperre gesperrter Datensaetze bleibt geprueft;
  der Loeschweg wird genau einmal im kanonischen Bewerbungsrouter erwartet.
- Der alte Schulungen-Source-Test prueft native Definition, Compiler, Renderer,
  echte Tabellenzeilen und Standspalte statt entfernte lokale Filtervariablen.
  Dies ist ein Delegationsvertrag, kein neuer Browsernachweis der Filterfunktion.
- Tabellenueberschriften, die den Seitenkopf wiederholen, entfallen zentral in
  FastTabRenderer und DerivedColumnLayout. ColumnLayoutRenderer zeigt die
  Ansichtenleiste erst bei mehreren Spalten. DOM-Gegenprobe vor Fix: H1,
  ueberfluessiger Ein-Spalten-Button und Tabellen-H3 mit demselben Titel. Nach Fix
  exakt eine sichtbare Benennung; zehn bestehende Frameworkvertraege pruefen auch
  Auswahl, Zuruecknavigation, schmale Anzeige und Mehrspaltenverhalten.
- Das Praesente-Register hat einen echten typisierten GET-Vertrag vor dem
  generischen Tab-Pfad. Vorhandene Daten-/Tenantauflösung und Pagination bleiben
  zentral; neue DTOs deklarieren genau die existierenden SQL-Spalten. Auch der
  bisherige `filterPlan`-Alias bleibt erreichbar. Keine neue Fachmutation.
- Der Feldchecker erkennt eine eindeutige benannte typisierte Liste wie
  `EinwilligungStandOut.vorgaenge`. Mehrere moegliche Listen und untypisierte
  Zeilen bleiben nicht pruefbar; ein untypisiertes `items` wird nicht durch eine
  andere Liste kaschiert. Keine Anhebung der Null-Ratsche.
- Der bereits in `af2b90fac` eingefuehrte Dienst `payment_run_freigabe` ist exakt
  Finance zugeordnet. Fremder Dienst und Mandantenreparatur bleiben unveraendert.

## Abnahme und Integration

813 Python-Masken-/Governance-/Router-/Feldvertraege bestanden, null Skip,
Exit 0 in 52,72 s; 23 Architekturvertraege bestanden (0,42 s). 38 Frontendtests
der beiden vormals roten Module bestanden (3,37 s); TypeScript `--noEmit` Exit 0.
Ein erwarteter Console-Fehler stammt aus dem Vertrag, der ungueltige Spalten
absichtlich abweist; kein fehlgeschlagener Frontendtest.

Gepruefte Quellen sind committed Backend/Frontend mit ausschliesslich eigenen
Hunks im vorhandenen `artifacts/ci-committed-source`. Ein Namespace-Fallback auf
den gemeinsamen Baum wurde vor der finalen Python-Abnahme ausgeschaltet und
Modulpfade geprueft. Die drei Renderer werden indexseitig integriert; ihre
fremden Arbeitsbaumfassungen bleiben erhalten.

OpenAPI folgt dem bereits committeten ehrlichen Aktionsrueckbau: sieben
vorgetaeuschte Action-Pfade aus `af2b90fac` entfallen, genau ein expliziter
Praesente-Pfad kommt hinzu, 3097 Pfade. Keine entfernten Stubs zur Befriedigung
alter Tests wieder eingebaut. Inventare, Architekturindex und Agent-Handbuch
werden aus demselben Quellstand erzeugt. Architektur vollstaendig:
935/935 Frontend-Routen, 274/274 Services, 454/454 Endpoint-Module.

Arbeitsbaum-Beruehrung: Der Architekturindex wurde einmal versehentlich am
geteilten Baum regeneriert (935 Routen/259 Services/448 Endpoints). Diese
Fassung bleibt uncommittet; geliefert wird nur der isolierte vollstaendige
Index. Kein pauschaler Restore oder Rueckbau fremder laufender Quellen.

## Weiter offen

Neue Gesamt-CI-Abnahme erforderlich. Auf `3e7142c48`: PostgreSQL, kritische E2E,
Docs und Service Security erfolgreich; OpenAPI, Smoke, Security und Gesamt-CI
rot, Quality abgebrochen. Smoke scheitert weiterhin am KIM-Kundenakte-Deep-Link.

Der aktualisierte Backendlauf hat elf Fehler bei 16055 bestandenen Tests; sechs
betreffen die hier geschlossenen Masken-/Feld-/Routervertraege. Fuenf
SPEC-P1-04-Fehler betreffen inzwischen bewusst gesperrte/entfernte Fachaktionen
und veraltete direkte Handlerannahmen. Die Command-Inventur bleibt blockierend,
bis echte Fachwege samt Berechtigungen, Daten, Audit und Atomaritaet bestehen.
Die vier Mandant-Finanz/CRM/Einkaufsbefunde sind fremd aktiv geclaimt.

Security, 41 Routerkonflikte, Journal-/Futter-/Waageintegration und Bewerber-
Selbstzugang/Akteurszuordnung bleiben im Gesamtziel. Keine DB-Verbindung,
neue DB/Container, Migration, Reset oder Dockerbereinigung in diesem Slice.
