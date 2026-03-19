# Architecture Delivery Waves 2026-03-11

**Zweck:** Umsetzung der ADR-basierten Architekturarbeit in konkrete Epics, Arbeitspakete und Delivery-Waves
**Quelle:** [ADR Clusters and Epics](../../architecture/adr-clusters-and-epics.md), [Top-50 Gap Backlog Landhandel](2026-03-06-top-50-gap-backlog-landhandel.md)

## Statusabgleich 2026-03-14

Dieses Dokument bleibt die Architektur- und Delivery-Zerlegung der Waves.
Der operative Wahrheitsstand fuer bereits umgesetzte Waves liegt in
`docs/architecture/process-kernel/STATUS.md`.

Standabgleich:

- Waves `1` bis `22` sind im Process-Kernel-Status als abgeschlossen dokumentiert
- besonders relevante neuere Abschluesse:
  - `Wave 20`: Audit-Hash-Kette, GoBD-Vollstaendigkeit, Optimistic Locking
  - `Wave 21`: Preisformel-Engine, Settlement-Journal-Bridge, E2E-Referenz bis Journal
  - `Wave 22`: Command Palette, zentraler Action-Dispatch, Mask-Registry-Surfacing

Hinweis:
- Dieses Dokument ist kein feingranulares Fortschrittsprotokoll je Commit.
- Fuer belastbare Aussagen zu Teststand und Lieferstatus immer die jeweiligen
  `wave-*/STATUS.md`-Dateien gegenpruefen.

## Annahmen zu Owners

Da noch kein verbindliches Delivery-Board mit Teamzuordnung im Repo existiert, arbeitet dieses Dokument mit Rollen-Ownern:

- `Platform Backend`: Backend-Kern, Workflow, Policy, Events, Datenmodelle
- `Frontend Platform`: Designsystem, Patterns, Read-Models im UI, Explainability, Konflikt-UX
- `Domain Leads`: Fachlogik in Agrar, Qualität, Pricing, Settlement, Reklamation
- `Integration & Security`: API, EDI, MCP, IAM, Delegation, Export, Audit
- `Data & Analytics`: Read-Models, Datenprodukte, Reporting, Benchmarking

## 1. Epic-Katalog

| Epic | Owner | Kern-ADRs | Top-50 IDs | Abhängigkeiten | Akzeptanzkriterien |
|------|-------|-----------|------------|----------------|--------------------|
| `Epic 1 Process Kernel Platform` | `Platform Backend` + `Domain Leads` | 003, 004, 005, 009, 010, 020, 022 | 001, 003, 004, 009, 011, 014, 019 | Canonical Domain Model, Workflow-Engine-Basis, Policy-Store, Audit | Kernprozess `Kontrakt -> Annahme -> Qualität -> Settlement` läuft über Commands, versionierte Workflows, erklärbare Policy-Entscheidungen und nachvollziehbare Ausnahmepfade |
| `Epic 2 Read, Event and Data Product Platform` | `Platform Backend` + `Data & Analytics` | 006, 008, 015, 024, 025, 026 | 018, 031, 033, 035, 036, 039, 040, 045, 046, 047 | Eventing-Basis, Query-Contract-Standard, Datenprodukt-Ownership, Importpfade | kritische Cockpits und Reports laufen auf stabilen Query-Contracts, Events, Read-Models und versionierten Datenprodukten; Importpfade sind geprüft und auditierbar |
| `Epic 3 Tenant, Security and Integration Governance` | `Integration & Security` + `Platform Backend` | 007, 013, 014, 019, 021, 023 | 009, 015, 016, 017, 043, 048, 049 | Tenant-/Verbundmodell, IAM, Policy-Override-Logik, Agent-Manifest | Tenant-Vererbung, Delegation, Integrationsklassen und Exportregeln sind modelliert, auditierbar und für externe Agenten sicher begrenzt |
| `Epic 4 Specialized Domain Enablers` | `Domain Leads` + `Frontend Platform` | 011, 012, 016, 017, 018 | 002, 006, 012, 021, 024, 041, 045 | Epic 1 und 2 als Plattformkern, Dokument-/Evidence-Modell, Qualitäts- und Pricing-Modell | Spezialdomänen wie Waage, DMS/OCR, Qualität und Pricing hängen auf gemeinsamen Standards statt auf Sonderpfaden |

## 2. Epic 1 in konkrete Tickets zerlegt

### Ticket PKP-01 Command Catalog Kernprozesse
- Ziel: verbindliche Commands für Kontrakt, Annahme, Qualität, Settlement, Reklamation
- Owner: `Platform Backend`
- Top-50 Bezug: `001`, `004`, `016`
- Akzeptanzkriterien:
  - zentrale Liste produktiver Business-Commands dokumentiert
  - jeder Kernprozessschritt bindet auf Command statt impliziten UI-CRUD
  - Result- und Error-Modelle für kritische Commands definiert

### Ticket PKP-02 Workflow Definition Schema und Versionierung
- Ziel: versionierte Workflow-Definitionen, Instanzreferenz auf Version, Migrationskonzept
- Owner: `Platform Backend`
- Top-50 Bezug: `011`, `012`, `013`, `020`
- Akzeptanzkriterien:
  - Workflow-Definitionen besitzen Version und Herkunft
  - laufende Instanzen referenzieren explizit ihre Definition
  - Sandbox arbeitet gegen konkrete Versionsstände

### Ticket PKP-03 Policy Override und Explainability Kern
- Ziel: global/tenant/rolle/prozess Prioritäten plus nachvollziehbare Begründung
- Owner: `Platform Backend`
- Top-50 Bezug: `014`, `019`
- Akzeptanzkriterien:
  - Prioritätsmodell für Overrides implementiert
  - jede kritische Policy-Entscheidung liefert Regelkette und Begründung
  - Audit protokolliert wirksame Override-Herkunft

### Ticket PKP-04 Cross-Domain Referenzmodell Kontrakt-zu-Settlement
- Ziel: explizite Referenzkette zwischen Kontrakt, Annahme, Charge, Qualität, Settlement
- Owner: `Domain Leads`
- Top-50 Bezug: `001`, `003`, `004`, `010`
- Akzeptanzkriterien:
  - Referenzbeziehungen formal modelliert
  - Read-Models und Audit verwenden dieselben Referenzen
  - keine losen Sonder-IDs für Kernprozesskette

### Ticket PKP-05 Ausnahme-, Reklamations- und Abzugsregeln
- Ziel: Sonderfälle aus UI-/Einzelfalllogik in den Prozesskern überführen
- Owner: `Domain Leads`
- Top-50 Bezug: `003`, `008`, `014`
- Akzeptanzkriterien:
  - Reklamation, Abzug und Ausnahmebehandlung als Regeln modelliert
  - manuelle Overrides sind begründet und auditierbar
  - Simulation deckt Ausnahmefälle ab

### Ticket PKP-06 Frontend Explainability und Freigabe-Pfade
- Ziel: Policy-/Workflow-Entscheidungen im UI konsistent darstellen
- Owner: `Frontend Platform`
- Top-50 Bezug: `019`, `021`, `028`, `029`
- Akzeptanzkriterien:
  - einheitliche Explainability-Komponenten in Kernmasken
  - Freigabestatus, Blocker und Ausnahmen sind sichtbar
  - keine Prozessmaske ohne erklärbaren Entscheidungszustand

## 2a. Wave-1-Tickets in agentenfähige Einzelaufgaben zerlegt

### PKP-01 Command Catalog Kernprozesse

#### Task PKP-01-A Command-Inventur erstellen
- Ziel: existierende fachliche Aktionen, API-Endpunkte und UI-Aktionen für Kontrakt, Annahme, Qualität, Settlement und Reklamation erfassen
- Empfohlene Reihenfolge: `1`
- Abhängigkeiten: keine
- Output:
  - Liste aktueller Aktionen mit Quelle, Trigger, Zielobjekt, Seiteneinstieg
  - Mapping `bestehender Pfad -> Ziel-Command`
- Definition of Done:
  - alle Kernprozessschritte sind inventarisiert
  - keine offensichtliche Kernaktion bleibt unklassifiziert
  - Dubletten und implizite CRUD-Pfade sind markiert
- Artefakte:
  - Inventar-Matrix im Delivery-Dokument oder ergänzender Statusdatei
  - Referenzliste betroffener Module und Endpunkte

#### Task PKP-01-B Ziel-Command-Katalog spezifizieren
- Ziel: verbindliche Command-Namen, Parameter, Result- und Error-Modelle definieren
- Empfohlene Reihenfolge: `2`
- Abhängigkeiten: `PKP-01-A`
- Output:
  - Command-Katalog für Kernprozess
  - Namenskonvention und fachliche Semantik je Command
- Definition of Done:
  - jeder Kernschritt besitzt einen Ziel-Command
  - Eingaben, Vorbedingungen und Resultate sind dokumentiert
  - idempotenzkritische Commands sind markiert
- Artefakte:
  - Command-Spezifikation
  - erste Command-ID-Namensliste

#### Task PKP-01-C Implementierungs-Roadmap für Command-Migration
- Ziel: Reihenfolge zur Umstellung bestehender Pfade auf Commands definieren
- Empfohlene Reihenfolge: `3`
- Abhängigkeiten: `PKP-01-B`, Input aus `PKP-02-A`, `PKP-03-A`
- Output:
  - Migrationsreihenfolge nach Risiko und Nutzen
  - Liste `sofort umstellen / später ablösen / beibehalten`
- Definition of Done:
  - Migrationsreihenfolge für Kernprozess freigegeben
  - Abhängigkeiten zu Workflow und Policy benannt
  - Frontend- und Backend-Aufgaben getrennt ausgewiesen
- Artefakte:
  - Migrationsplan
  - Task-Liste pro Subsystem

### PKP-02 Workflow Definition Schema und Versionierung

#### Task PKP-02-A Workflow-Definitionsschema festlegen
- Ziel: verbindliches Schema für Workflow-Definition, Version, Herkunft und Tenant-Bezug definieren
- Empfohlene Reihenfolge: `1`
- Abhängigkeiten: keine
- Output:
  - Schemaentwurf
  - Pflichtfelder und Lebenszyklusregeln
- Definition of Done:
  - Version, Herkunft, Status und Tenant-Kontext sind modelliert
  - Mindestanforderungen für neue Definitionen sind festgelegt
  - keine unklare Zuständigkeit zwischen Definition und Instanz
- Artefakte:
  - Workflow-Schema
  - Feldbeschreibung

#### Task PKP-02-B Instanzreferenz und Migrationsmodell beschreiben
- Ziel: Regeln für laufende Instanzen und Workflow-Migrationen definieren
- Empfohlene Reihenfolge: `2`
- Abhängigkeiten: `PKP-02-A`
- Output:
  - Modell `Instanz -> Definitionsversion`
  - Migrationsarten und Einschränkungen
- Definition of Done:
  - laufende Instanzen referenzieren explizit ihre Version
  - zulässige und unzulässige Migrationen sind beschrieben
  - Audit-Anforderungen für Migrationen sind festgelegt
- Artefakte:
  - Migrationsmatrix
  - Zustandsdiagramm oder Prozessbeschreibung

#### Task PKP-02-C Sandbox gegen Versionen ausrichten
- Ziel: Simulation und Sandbox auf konkrete Workflow-Versionen ausrichten
- Empfohlene Reihenfolge: `3`
- Abhängigkeiten: `PKP-02-A`, `PKP-02-B`
- Output:
  - Regeln für Simulationsinput und Versionswahl
  - Liste notwendiger UI-/API-Anpassungen
- Definition of Done:
  - Sandbox ist fachlich an Versionen gekoppelt
  - kein Simulationspfad arbeitet gegen implizite „aktuelle“ Definitionen
  - offene technische Lücken sind benannt
- Artefakte:
  - Sandbox-Spezifikation
  - Implementierungs-Checkliste

### PKP-03 Policy Override und Explainability Kern

#### Task PKP-03-A Override-Prioritätsmodell festlegen
- Ziel: Prioritätsreihenfolge für global, tenant-, rollen- und prozessbezogene Overrides definieren
- Empfohlene Reihenfolge: `1`
- Abhängigkeiten: keine
- Output:
  - Prioritätsmodell
  - Entscheidungslogik bei konkurrierenden Overrides
- Definition of Done:
  - Prioritätsreihenfolge ist eindeutig
  - Konfliktfälle sind beschrieben
  - Sonderregeln sind explizit statt implizit
- Artefakte:
  - Prioritätstabelle
  - Override-Regelkatalog

#### Task PKP-03-B Explainability-Datenmodell definieren
- Ziel: Regelkette, Begründung, Blocker, Freigabehinweise und Quellen strukturiert modellieren
- Empfohlene Reihenfolge: `2`
- Abhängigkeiten: `PKP-03-A`
- Output:
  - Explainability-View-Modell
  - minimale Pflichtdaten pro Entscheidung
- Definition of Done:
  - jede Policy-Entscheidung kann als strukturierte Erklärung gerendert werden
  - UI- und Audit-Bedarf sind beide abgedeckt
  - keine Freitext-Only-Lösung als Kernmodell
- Artefakte:
  - Explainability-Schema
  - Beispiel-Responses

#### Task PKP-03-C Audit-Pfad für wirksame Overrides festlegen
- Ziel: dokumentieren, wie wirksame Override-Herkunft und Ergebnis in Audit protokolliert werden
- Empfohlene Reihenfolge: `3`
- Abhängigkeiten: `PKP-03-A`, `PKP-03-B`
- Output:
  - Audit-Modell für Policy-Entscheidung
  - Liste relevanter Audit-Felder
- Definition of Done:
  - Herkunft, Entscheidung, Kontext und Auswirkung sind auditierbar
  - Verbindung zu Workflow-/Freigabepfaden ist beschrieben
  - keine kritische Policy-Entscheidung ohne Audit-Konzept
- Artefakte:
  - Audit-Feldkatalog
  - Verknüpfung Policy -> Audit -> UI

### PKP-04 Cross-Domain Referenzmodell Kontrakt-zu-Settlement

#### Task PKP-04-A Referenzkette fachlich modellieren
- Ziel: Referenzraum zwischen Kontrakt, Annahme, Charge, Qualität und Settlement formal definieren
- Empfohlene Reihenfolge: `1`
- Abhängigkeiten: keine
- Output:
  - fachliches Referenzmodell
  - Kardinalitäten und Pflichtbezüge
- Definition of Done:
  - alle Kernobjekte der Kette sind verbunden
  - Pflicht- und optionale Referenzen sind geklärt
  - kein kritischer Prozessschritt bleibt referenziell isoliert
- Artefakte:
  - Referenzdiagramm
  - Objektbeziehungsbeschreibung

#### Task PKP-04-B Schattenreferenzen und Sonder-IDs finden
- Ziel: bestehende lose IDs, implizite Bezüge und Sondertabellen im Kernprozess identifizieren
- Empfohlene Reihenfolge: `2`
- Abhängigkeiten: `PKP-04-A`
- Output:
  - Liste problematischer Referenzpfade
  - Einstufung `ersetzen / überführen / tolerieren`
- Definition of Done:
  - Schattenreferenzen im Kernprozess sind dokumentiert
  - Migrationskandidaten sind priorisiert
  - Read-Model- und Audit-Folgen sind benannt
- Artefakte:
  - Referenz-Schuldenliste
  - Migrationspriorisierung

#### Task PKP-04-C Read-Model- und Audit-Nutzung ausrichten
- Ziel: sicherstellen, dass Read-Models und Audit dieselben Cross-Domain-Referenzen verwenden
- Empfohlene Reihenfolge: `3`
- Abhängigkeiten: `PKP-04-A`, `PKP-04-B`, Input aus `PKP-03-C`
- Output:
  - Liste betroffener Cockpits, Reports und Auditpfade
  - Soll-Modell je Pfad
- Definition of Done:
  - Kerncockpits referenzieren denselben Fachraum
  - Audit-Kette folgt denselben Referenzen
  - Abweichungen sind explizit markiert
- Artefakte:
  - Mapping Read-Model/Audit -> Referenzmodell
  - Gap-Liste

### PKP-05 Ausnahme-, Reklamations- und Abzugsregeln

#### Task PKP-05-A Ausnahmearten katalogisieren
- Ziel: Reklamationen, Abzüge, Qualitätsausnahmen und manuelle Sonderfälle sammeln und klassifizieren
- Empfohlene Reihenfolge: `1`
- Abhängigkeiten: keine
- Output:
  - Ausnahmekatalog
  - Klassifikation nach Auslöser, Wirkung und Freigabepflicht
- Definition of Done:
  - häufige Ausnahmefälle des Kernprozesses sind erfasst
  - fachliche Auslöser und Auswirkungen sind dokumentiert
  - manuelle Sonderpfade sind sichtbar gemacht
- Artefakte:
  - Ausnahmekatalog
  - Klassifikationsmatrix

#### Task PKP-05-B Regelmodell und Entscheidungslogik festlegen
- Ziel: definieren, welche Ausnahmefälle regelbasiert, policy-basiert oder manuell freigabepflichtig sind
- Empfohlene Reihenfolge: `2`
- Abhängigkeiten: `PKP-05-A`, Input aus `PKP-03-A`, `PKP-04-A`
- Output:
  - Entscheidungsmodell für Ausnahmen
  - Verknüpfung zu Policy, Workflow und Qualität
- Definition of Done:
  - jede Ausnahmeart hat einen vorgesehenen Entscheidungsweg
  - Regeln, Freigaben und manuelle Overrides sind klar getrennt
  - Explainability-Anforderungen sind berücksichtigt
- Artefakte:
  - Entscheidungsbaum
  - Regelzuordnung je Ausnahmeart

#### Task PKP-05-C Simulations- und Audit-Pfade definieren
- Ziel: Ausnahmebehandlung in Simulation und Audit integrieren
- Empfohlene Reihenfolge: `3`
- Abhängigkeiten: `PKP-05-B`, `PKP-02-C`, `PKP-03-C`
- Output:
  - Simulationsfälle für Reklamation und Abzug
  - Audit-Anforderungen für Sonderbehandlung
- Definition of Done:
  - Ausnahmefälle sind simulierbar
  - manuelle Overrides sind auditierbar
  - keine Sonderbehandlung ohne Nachweis- und Prüfpfad
- Artefakte:
  - Simulationsfallliste
  - Audit-Checkliste

### PKP-06 Frontend Explainability und Freigabe-Pfade

#### Task PKP-06-A Kernmasken priorisieren
- Ziel: festlegen, welche Prozessmasken zuerst Explainability- und Freigabe-UI erhalten
- Empfohlene Reihenfolge: `1`
- Abhängigkeiten: keine
- Output:
  - priorisierte Maskenliste
  - Zielabdeckung für Wave 1
- Definition of Done:
  - Kernmasken für Kontrakt, Annahme, Qualität, Settlement sind priorisiert
  - Reihenfolge folgt Prozesskritikalität
  - UI-Aufwand je Maske ist grob geschätzt
- Artefakte:
  - Priorisierungsliste
  - Seiten-/Masken-Matrix

#### Task PKP-06-B Gemeinsame Explainability-Komponenten definieren
- Ziel: Standardkomponenten für Entscheidung, Begründung, Freigabestatus, Blocker und Ausnahmehinweis festlegen
- Empfohlene Reihenfolge: `2`
- Abhängigkeiten: `PKP-03-B`, `PKP-06-A`
- Output:
  - Komponentenliste
  - Design- und Zustandsmodell
- Definition of Done:
  - gemeinsamer Komponentenrahmen ist definiert
  - Zustände `freigegeben / blockiert / Freigabe nötig / Ausnahme` sind abgedeckt
  - UI bindet auf strukturiertes Explainability-Modell statt Freitext
- Artefakte:
  - Komponenten-Spezifikation
  - Zustandsmodell

#### Task PKP-06-C Integrationsplan für Kernmasken erstellen
- Ziel: beschreiben, wie Explainability- und Freigabe-UI konkret in die priorisierten Kernmasken eingezogen wird
- Empfohlene Reihenfolge: `3`
- Abhängigkeiten: `PKP-06-A`, `PKP-06-B`, Input aus `PKP-03-C`, `PKP-02-C`
- Output:
  - Integrationsreihenfolge
  - Abhängigkeiten zu API, Policy und Workflow
- Definition of Done:
  - jede priorisierte Maske hat einen Integrationspfad
  - Backend- und Frontend-Abhängigkeiten sind benannt
  - kein Kernpfad bleibt ohne Zieltermin oder Integrationsansatz
- Artefakte:
  - Integrationsplan
  - Abhängigkeitsliste pro Maske

## 2b. Agentenpakete für Wave 1

### Paket A: Command und Workflow-Grundlagen

Enthaltene Tasks:
- `PKP-01-A`
- `PKP-01-B`
- `PKP-01-C`
- `PKP-02-A`
- `PKP-02-B`
- `PKP-02-C`

Ziel:
- Command- und Workflow-Grundlagen für den Kernprozess definieren

Primäre Outputs:
- Command-Inventur
- Ziel-Command-Katalog
- Workflow-Schema
- Migrationsmodell
- Sandbox-Versionsregeln

### Paket B: Policy, Referenzen und Ausnahmen

Enthaltene Tasks:
- `PKP-03-A`
- `PKP-03-B`
- `PKP-03-C`
- `PKP-04-A`
- `PKP-04-B`
- `PKP-04-C`
- `PKP-05-A`
- `PKP-05-B`
- `PKP-05-C`

Ziel:
- Override-, Explainability-, Referenz- und Ausnahmekern fachlich beschreiben

Primäre Outputs:
- Prioritätsmodell
- Explainability-Schema
- Audit-Feldkatalog
- Referenzmodell
- Ausnahmekatalog und Entscheidungsbaum

### Paket C: Frontend-Explainability und Integrationsvorbereitung

Enthaltene Tasks:
- `PKP-06-A`
- `PKP-06-B`
- `PKP-06-C`

Ziel:
- priorisierte Kernmasken und gemeinsamer UI-Rahmen für Explainability und Freigabe

Primäre Outputs:
- priorisierte Maskenliste
- Komponenten-Spezifikation
- Integrationsplan pro Kernmaske

## 2c. Zuweisungsliste Codex / Codex / Codex

| Paket | Agent 1 | Agent 2 | Agent 3 | Reihenfolge | Kritische Eingänge |
|------|---------|---------|---------|-------------|--------------------|
| Paket A `Command und Workflow-Grundlagen` | `Codex` | `Codex` | `Codex` | zuerst starten | keine |
| Paket B `Policy, Referenzen und Ausnahmen` | `Codex` | `Codex` | `Codex` | parallel zu Paket A starten, Abschluss nach ersten Outputs aus `PKP-02-A` und `PKP-01-B` | Command-Katalog, Workflow-Schema |
| Paket C `Frontend-Explainability und Integrationsvorbereitung` | `Codex` | `Codex` | `Codex` | nach `PKP-03-B` und priorisiertem Maskenfokus starten | Explainability-Modell, priorisierte Kernmasken |

Empfohlene operative Reihenfolge:
1. Paket A sofort beginnen
2. Paket B parallel anlaufen lassen, aber `PKP-03-B`, `PKP-04-C`, `PKP-05-C` erst nach den markierten Eingängen schließen
3. Paket C nach Vorliegen von Explainability-Modell und Maskenpriorisierung schließen

## 2d. Sofort startbare Arbeitsaufträge

### Paket A: Command und Workflow-Grundlagen

| Auftrag | Quelle | Reihenfolge | Ziel | Primärartefakt |
|------|-------|-----------|------|----------------|
| `A1` | `PKP-01-A` | `1` | Command-Inventur für Kernprozess aus bestehendem Codebestand aufbauen | `../../architecture/process-kernel/wave-1/package-a/PKP-01-command-inventory.md` |
| `A2` | `PKP-02-A` | `2` | Workflow-Definitionsschema für versionierte Prozessdefinitionen festziehen | `../../architecture/process-kernel/wave-1/package-a/PKP-02-workflow-definition-schema.md` |
| `A3` | `PKP-01-B` | `3` | Ziel-Command-Katalog auf Basis von `A1` und `A2` spezifizieren | `../../architecture/process-kernel/wave-1/package-a/PKP-01-target-command-catalog.md` |
| `A4` | `PKP-02-B` | `4` | Instanzreferenz- und Migrationsmodell beschreiben | `../../architecture/process-kernel/wave-1/package-a/PKP-02-instance-and-migration-model.md` |

### Paket B: Policy, Referenzen und Ausnahmen

| Auftrag | Quelle | Reihenfolge | Ziel | Primärartefakt |
|------|-------|-----------|------|----------------|
| `B1` | `PKP-03-A` | `1` | Override-Prioritätsmodell für global, tenant, Rolle, Prozess festlegen | `../../architecture/process-kernel/wave-1/package-b/PKP-03-override-priority-model.md` |
| `B2` | `PKP-04-A` | `2` | Cross-Domain-Referenzkette Kontrakt -> Annahme -> Charge -> Qualität -> Settlement modellieren | `../../architecture/process-kernel/wave-1/package-b/PKP-04-reference-chain-model.md` |
| `B3` | `PKP-05-A` | `3` | Ausnahmekatalog für Reklamation, Abzug, Sonderfreigabe und Qualitätsabweichung aufbauen | `../../architecture/process-kernel/wave-1/package-b/PKP-05-exception-catalog.md` |
| `B4` | `PKP-03-B` | `4` | Explainability-Datenmodell an Policy- und Ausnahmepfade anbinden | `../../architecture/process-kernel/wave-1/package-b/PKP-03-explainability-model.md` |

### Paket C: Frontend-Explainability und Integrationsvorbereitung

| Auftrag | Quelle | Reihenfolge | Ziel | Primärartefakt |
|------|-------|-----------|------|----------------|
| `C1` | `PKP-06-A` | `1` | Kernmasken für Explainability/Freigabe priorisieren | `../../architecture/process-kernel/wave-1/package-c/PKP-06-core-mask-priority.md` |
| `C2` | `PKP-06-B` | `2` | gemeinsame Explainability-Komponenten und Zustände definieren | `../../architecture/process-kernel/wave-1/package-c/PKP-06-explainability-components.md` |
| `C3` | `PKP-06-C` | `3` | Integrationsreihenfolge für priorisierte Kernmasken beschreiben | `../../architecture/process-kernel/wave-1/package-c/PKP-06-integration-plan.md` |

## 2e. Minimaler Artefaktpfad

- Paket A Status: `../../architecture/process-kernel/wave-1/package-a/STATUS.md`
- Paket B Status: `../../architecture/process-kernel/wave-1/package-b/STATUS.md`
- Paket C Status: `../../architecture/process-kernel/wave-1/package-c/STATUS.md`
- Reproduzierbare Inventur: `../../../scripts/process_kernel/build_command_inventory.py`

## 3. Feste Zuordnung der Epics zu Top-50-Backlog-IDs

### Epic 1 Process Kernel Platform
- `001`, `003`, `004`, `008`, `009`, `010`, `011`, `012`, `013`, `014`, `019`, `020`

### Epic 2 Read, Event and Data Product Platform
- `018`, `031`, `033`, `034`, `035`, `036`, `037`, `038`, `039`, `040`, `045`, `046`, `047`, `050`

### Epic 3 Tenant, Security and Integration Governance
- `009`, `015`, `016`, `017`, `038`, `043`, `048`, `049`, `050`

### Epic 4 Specialized Domain Enablers
- `002`, `005`, `006`, `007`, `012`, `021`, `024`, `041`, `042`, `044`, `045`

Hinweis:
- einzelne IDs tauchen bewusst in mehreren Epics auf, wenn Plattform- und Facharbeit gleichzeitig nötig sind
- Delivery-Steuerung erfolgt trotzdem über einen primären Epic-Owner pro Arbeitspaket

## 4. Delivery-Waves

### Wave 1: Process Kernel Foundation

Zeitrahmen:
- 4 bis 6 Wochen

Primäre Epics:
- `Epic 1 Process Kernel Platform`
- Startarbeiten aus `Epic 2`

Arbeitspakete:
1. `PKP-01` Command Catalog Kernprozesse
2. `PKP-02` Workflow Definition Schema und Versionierung
3. `PKP-03` Policy Override und Explainability Kern
4. `PKP-04` Cross-Domain Referenzmodell Kontrakt-zu-Settlement
5. Query-Contract-Härtung für Kernprozess-Cockpits

Top-50 Fokus:
- `001`, `003`, `004`, `009`, `011`, `013`, `014`, `019`, `031`

Wave-Exit:
- Kernprozessschritte laufen über definierte Commands
- Workflow-Versionierung und Policy-Prioritäten sind im Kern eingeführt
- kritische Query-Pfade liefern stabile Verträge

Umgesetzter Stand per 2026-03-11:
- `policy-manager` arbeitet auf produktiver Backend-Explainability statt auf Roh-Decision-Daten
- `workflow-sandbox` erzwingt versionierte Workflow-Metadaten im Preview-Contract
- `annahme/qualitaets-check` und `annahme/abrechnung` nutzen gemeinsame Referenzkette und Explainability
- `finance/ap/invoices` ist auf gemeinsamen AP-Approval-Workflow, Explainability, Override-Resolution und Audit-Fassade gezogen
- Legacy-AP-Freigabe-Endpunkte delegieren in denselben Workflow statt Status direkt zu setzen
- Wave-1-Contracts sind über Bootstrap- und Kernel-Tests abgesichert (24 Tests)

### Wave 2: Data, Event and Governance Build-out

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 1

Primäre Epics:
- `Epic 2 Read, Event and Data Product Platform`
- `Epic 3 Tenant, Security and Integration Governance`

Arbeitspakete:
1. Outbox-/Event-Namenskonvention und erste produktive Event-Pfade
2. Read-Models für Cockpits, KPI- und Prozessbeobachtung
3. Tenant-/Verbundmodell konkretisieren
4. Rollen- und Berechtigungsvererbung definieren
5. Agenten- und Delegationssicherheitsmodell ausarbeiten
6. Export- und Datenresidenzregeln für kritische Pfade modellieren

Top-50 Fokus:
- `015`, `016`, `017`, `018`, `033`, `035`, `039`, `043`, `048`, `049`

Wave-Exit:
- erste produktive Event-Konsumenten und Read-Models laufen stabil
- Agenten- und Integrationsgrenzen sind technisch und fachlich definiert
- Tenant- und Governance-Regeln sind nicht mehr implizit

Umgesetzter Stand per 2026-03-11:
- AP1: Event-Namenskonvention `{tenant_id}.{domain}.{aggregate}.{verb}` (ADR-027), Outbox-Writes in AP-Approval, Ernte-Annahme, Qualitaetsprotokoll, Direct-Debit
- AP2: Read-Model-Endpoints `/finance/read-models/ap-invoice-cockpit|payment-run-cockpit|process-observation` mit stabilen schema_version-Contracts
- AP3: `TenantStructure`/`VerbundMember`-Modell mit Vererbungsregeln, `GET /tenant/structure`
- AP4: `RoleInheritanceChain` mit Scopes global/verbund/tenant/process, `GET /tenant/role-inheritance`
- AP5: `AgentManifest`/`DelegationPolicy` — EXECUTE_PAYMENT fuer KI-Agenten gesperrt, `GET /tenant/agent-manifests`
- AP6: `ExportGovernancePolicy` mit GoBD-Pflichtregeln (10 Jahre Buchungsbelege, DSGVO Kundenstamm), `GET /tenant/data-residency`
- Wave-2-Contracts abgesichert: 37 Wave-2-Tests (13 Events + 5 Read-Models + 19 Governance)

### Wave 3: Specialized Domain Enablement

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 2

Primäre Epics:
- `Epic 4 Specialized Domain Enablers`
- Restarbeiten aus `Epic 2`

Arbeitspakete:
1. UI-Maskenklassifizierung A/B/C für Kernseiten
2. Dokument-/Audit-Evidence-Modell in DMS/OCR/Freigaben einziehen
3. IoT-/Telemetriepfade Waage/Silo/Lager anschließen
4. Pricing-/Marktdatenquellen klassifizieren
5. Qualitäts-/Labordatenmodell an Charge, Preis und Freigabe anbinden
6. Import-/Staging-/Prüfpipelines für CSV, EDI, OCR standardisieren

Top-50 Fokus:
- `002`, `005`, `006`, `007`, `012`, `021`, `024`, `041`, `045`, `046`, `047`

Wave-Exit:
- Spezialdomänen hängen auf gemeinsamen Plattformstandards
- Dokument-, Qualitäts-, Pricing- und Telemetriepfade sind nicht mehr isoliert
- Import- und Prüfpipelines sind kontrolliert und auditierbar

Umgesetzter Stand per 2026-03-11:
- AP1: `MaskRegistry` — 18 Masken klassifiziert (A/B/C), alle Klasse-A mit Explainability-REQUIRED und Wave-1-Contract
- AP2: `AuditEvidenceEntry`/`EvidenceReference` — GoBD-Belegpflicht mit Paperless-ngx/OCR-Anbindung
- AP3: `DeviceManifest`/`TelemetryReading` — Waage, Silo, Lager, Feuchte, Temperatur
- AP4: `PricingGovernancePolicy` — MATIF/XONTRO/spot_daily/fixed_contract/manual_override klassifiziert
- AP5: `LotQualityProfile`/`compute_price_deduction` — Charge-Qualitaet an Preis und Freigabe gebunden
- AP6: `ImportPipelineJob`/`ImportPipelineConfig` — CSV/EDI/OCR/XML-UBL Pipeline-Standard
- Wave-3-Contracts abgesichert: 30 Tests (14 AP1-AP2 + 16 AP3-AP6)
- Gesamtergebnis aller 3 Waves: **99 Tests gruen**

### Wave 4: Operational Hardening and Runtime Closure

Zeitrahmen:
- 2 bis 4 Wochen nach Wave 3

Primaere Epics:
- `Epic 2 Read, Event and Data Product Platform`
- `Epic 3 Tenant, Security and Integration Governance`
- `Epic 4 Specialized Domain Enablers`

Arbeitspakete:
1. persistente Workflow-Instanzen und robuste Event-Laufzeit
2. Read-Models auf Consumer/Projektionen und Rebuild-Pfade umstellen
3. SLA/Timeout/Eskalationsbeobachtung produktiv schliessen
4. operative Governance fuer Delegation, Export und Evidence verankern
5. verbleibende Finance-Folgesichten nur ueber explizite Backend-Contracts schliessen
6. Runtime-Metriken, Replay- und Rebuild-Standards fuer den Process Kernel etablieren

Wave-Exit:
- Event-, Workflow- und Projektionspfade sind persistent, replaybar und operativ beobachtbar
- verbleibende UI-Folgesichten nutzen nur noch explizite Contracts
- bekannte Runtime-Provisorien im Outbox-/Event-Loop-Umfeld sind beseitigt

Umgesetzter Stand per 2026-03-11:
- `finance_read_models.py` nutzt fuer Finance-Contracts explizite Projektionsbuilder plus `POST /api/v1/finance/read-models/_rebuild`
- `GET /api/v1/finance/read-models/_status` und `GET /api/v1/runtime/health|components` zeigen Runtime-Status und Cache-/Rebuild-Metriken
- Projektions-Metadaten werden best effort in `domain_shared.process_projection_registry` gespiegelt; damit ist die Runtime-Sicht nicht mehr rein in-memory
- erste Projektions-Snapshots werden best effort in `domain_shared.process_projection_snapshots` persistiert; Status und Runtime zeigen damit nicht nur Registry-, sondern auch Snapshot-Fortschritt
- Consumer-Fortschritt und Replay-Cursor werden best effort in `domain_shared.process_projection_cursors` persistiert; Rebuild und Replay haben damit einen gemeinsamen Wiederanlaufanker
- fuer `process-observation` wird dieser Cursor bereits an die letzte echte Workflow-Replay-Event-ID aus `workflow_audit` gebunden statt nur an einen Rebuild-Zeitpunkt
- fuer `ap-invoice-cockpit` wird der Cursor best effort an die letzte echte AP-Invoice-Outbox-Event-ID aus `outbox_events.id` gebunden
- fuer `payment-run-cockpit` und die Cash-Closing-Projektionen werden Cursor jetzt ebenfalls an echte Outbox-Events (`payment_run.*`, `cash_closing.posted`) gebunden
- Runtime und Status zeigen Cursor-Fortschritt nicht mehr nur global, sondern auch pro Projektion mit Quelle, Status und letztem verarbeitetem Event
- der AP-Invoice-Post-Pfad und Payment-Run-Ruecklaeufer schreiben jetzt ebenfalls echte Outbox-Events (`APInvoicePosted`, `payment_run.returned`) und verbreitern damit die laufende Cursor-Abdeckung

### Wave 5: E2E Agrar-Prozesskette und Command-Layer

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 4

Startbedingung:
- Wave 4 abgeschlossen

Primaere Epics:
- `Epic 1 Process Kernel Platform`
- `Epic 2 Read, Event and Data Product Platform`

Arbeitspakete:
1. Business-Command-Catalog fuer alle Kernprozessschritte implementieren
2. E2E-Referenzkette Kontrakt → Annahme → Qualitaet → Settlement → FiBu lueckenlos schliessen
3. Rohwarenabrechnung und Qualitaets-Preisbindung produktionsreif machen
4. Workflow-Simulation und Sandbox auf produktive Szenarien ausrichten
5. Agent-/Action-Layer: Command-Contracts ueber MCP/OpenAPI verfuegbar machen

Top-50 Fokus:
- `001`, `003`, `004`, `008`, `010`, `011`, `019`, `020`

Wave-Exit:
- alle Kernprozessschritte gehen ueber Commands statt UI-CRUD
- E2E-Kette ist lueckenlos referenziert, im Read-Model sichtbar und testbar
- Rohwarenabrechnung ist produktionsreif mit automatischem GoBD-Beleg
- Agent-Command-Manifest ist ueber API abrufbar; kritische Commands erfordern Human-Confirmation

Vorbereiteter Stand per 2026-03-11:
- E2E-Chain-Report zeigt: 6/6 Referenzen bereits vorhanden (Wave-1-Basis)
- Wave-5-STATUS.md mit vollstaendigem AP-Scope vorbereitet
- Pakete A und B mit Abnahmekriterien und Abhaengigkeiten definiert
- Gap-Skript verfuegbar: `scripts/process_kernel/build_e2e_chain_report.py`

### Wave 6: Agrar-P0 Closure und Supplier-Erweiterung

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 5 AP1 und AP2

Startbedingung:
- Wave 5 AP1 (Command-Layer) und AP2 (E2E-Referenzkette) abgeschlossen

Primaere Epics:
- `Epic 4 Specialized Domain Enablers`
- `Epic 1 Process Kernel Platform`

Arbeitspakete:
1. Mandantenfaehige Schlagkartei mit FLIK-ID und GeoJSON-Export (Agrar-P0)
2. DueV-konforme Duenge-/Stoffstrombilanz mit Grenzwert-Compliance-Check (Agrar-P0)
3. Vollstaendiges PSM-Spritztagebuch mit Sachkunde, Wasserauflage und GoBD-Finalisierung (Agrar-P0)
4. Supplier Portal: Lieferanten-Self-Service fuer Kontrakte, Lieferungen, Abrechnungen
5. Erweiterte Kontrakt- und Preislogik: Teilmengen, Qualitaetsstaffeln, Differenzkontrakte
6. Silo- und Lagerprozess auf Branchenniveau mit IoT-Anbindung

Top-50 Fokus:
- `002`, `005`, `006`, `007`, `021`, `024`, `041`, `042`, `044`

Wave-Exit:
- Agrar-P0-Gap-Report zeigt 12/12 Pruefpunkte erfuellt
- Schlagkartei ist GIS-faehig und mandantenisoliert
- Duengebilanz und PSM-Tagebuch sind gesetzeskonform und auditierbar
- Supplier Portal gibt Lieferanten kontrollierten Self-Service-Zugang
- Teilmengenkontrakte und Qualitaetsstaffeln sind in Settlement-Logik integriert
- Siloinhalt-Verwaltung ist IoT-verbunden und GoBD-konform

Vorbereiteter Stand per 2026-03-11:
- Agrar-P0-Gap-Report zeigt aktuell 0/12 (Wave-6-Scope noch nicht implementiert)
- Wave-6-STATUS.md mit vollstaendigem AP-Scope vorbereitet
- Pakete A (Agrar-P0) und B (Supplier/Lager) mit Abnahmekriterien definiert
- Gap-Skript verfuegbar: `scripts/process_kernel/build_agrar_p0_gap_report.py`

### Wave 8: Reporting, Tenant-Isolation und Agent-Kontexte

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 7

Startbedingung:
- Wave 7 abgeschlossen

Primaere Epics:
- `Epic 2 Read, Event and Data Product Platform`
- `Epic 3 Tenant, Security and Integration Governance`

Arbeitspakete:
1. versionierte Datenprodukte aus Read-Model-Snapshots aufbauen
2. Cross-Tenant-Zugriffe ueber einen formalen Isolation-Guard absichern
3. tenantbewusste Agent-Kontexte und Delegationspfade anbinden
4. Betriebskennzahlen-Benchmarks fuer Verbundkontexte verfuegbar machen
5. GoBD-Retention maschinell pruefbar machen

Wave-Exit:
- Snapshot-basierte Datenprodukte sind ueber Reporting-Contracts nutzbar
- Tenant-Isolation wird in produktiven API-Pfaden erzwungen
- Agent-Kontexte und Benchmark-Pfade nutzen dieselben Governance-Regeln

Umgesetzter Stand per 2026-03-12:
- AP1: `ReadModelSnapshotStore` ist DB-persistiert; `GET /api/v1/reporting/data-products` und `POST /api/v1/reporting/run` arbeiten auf Snapshot-Basis
- AP2: `TenantIsolationGuard` ist produktiv an Reporting- und Agent-Dispatch-Pfade angebunden; `GET /api/v1/reporting/isolation/check` zeigt den Guard-Contract direkt
- AP3: `AgentContext`, `AgentContextStore` und `tenantbewusst_dispatch()` nutzen denselben Guard statt eines separaten Tenant-Vergleichs
- AP4: `BenchmarkReport.build()` und `GET /api/v1/benchmark/katalog` liefern anonymisierte Kennzahlen-Vergleiche
- AP5: `RetentionPruefung` und `build_default_retention_regeln()` decken die GoBD-Retention vertraglich ab
- Wave-8-Contracts abgesichert: **69 Tests gruen** (`13 reporting + 30 isolation/retention + 26 agent`)

### Wave 9: EDI/API-Integration, Ernte-Kampagnen und Frontend-Prozessbindung

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 8

Startbedingung:
- Wave 8 abgeschlossen

Primaere Epics:
- `Epic 3 Tenant, Security and Integration Governance`
- `Epic 4 Specialized Domain Enablers`

Arbeitspakete:
1. EDI-Integrations-Klassen fuer ORDERS/INVOIC und SEPA XML modellieren
2. Ernte-Kampagnen mit Schlagzielen und Zustandsmaschine formalisieren
3. API-Gateway-Manifest fuer externe Partner mit Scopes und Limits absichern
4. Frontend-Masken auf Process-Kernel-Commands statt CRUD binden
5. Zertifikate und Qualitaetsnachweise als Kernmodell verfuegbar machen

Wave-Exit:
- EDI-, API-Partner- und Zertifikatsvertraege sind formal modelliert und testbar
- Ernte-Kampagnen und Frontend-Bindings sind als Prozesskern-Bausteine verfuegbar
- Wave 9 liefert keine neuen Schattenpfade ausserhalb des Command-/Governance-Rahmens

Umgesetzter Stand per 2026-03-12:
- AP1: `EdiNachricht`, `EdiPartner`, `parse_edi_nachricht()` und `POST /api/v1/edi/nachrichten` sind ueber Contracts abgesichert
- AP2: `ErnteKampagne`, `SchlagErnteziel`, Zustandsuebergaenge und `POST /api/v1/ernte-kampagnen` inkl. Start/Abschluss-Endpoints sind umgesetzt
- AP3: `ApiGatewayRegistry.pruefe_api_zugriff()` prueft Partner, Scopes und Zugriffsbeschraenkungen vertraglich
- AP4: `MaskenBindingRegistry` und `build_default_bindings()` bilden den Frontend-zu-Command-Rahmen ab
- AP5: `Zertifikat`, `ZertifikatStore`, `tage_bis_ablauf()` und `POST /api/v1/zertifikate` sind abgesichert
- Test-Kompatibilitaet: `app/main.py` stellt eine leichte `api_router`-Test-App fuer Wave-9-API-Contracts bereit
- Wave-9-Contracts abgesichert: **50 Tests gruen** (`28 integration + 22 domain`)

### Wave 10: Process Mining, Observability und Analytics-Verknuepfung

Zeitrahmen:
- 4 bis 6 Wochen nach Wave 9

Startbedingung:
- Wave 9 abgeschlossen

Primaere Epics:
- `Epic 2 Read, Event and Data Product Platform`
- `Epic 3 Tenant, Security and Integration Governance`

Arbeitspakete:
1. Process-Mining-Sicht aus Cursor-, Replay- und Runtime-Zustaenden aufbauen
2. Observability-Signale mit Runtime-Komponenten und Telemetrie verbinden
3. Reporting- und Benchmark-Produkte an diese Mining-Sicht anschliessen

Wave-Exit:
- Cursor- und Replay-Fortschritt ist nicht nur operativ, sondern analytisch auswertbar
- Bottlenecks und degradierte Runtime-Komponenten sind ueber stabile Contracts abfragbar
- spaetere Analytics-Pfade bauen auf derselben Mining-Sicht statt auf Schattenmetriken

Umgesetzter Stand per 2026-03-12:
- AP1: `ProcessMiningTrace`, `ProcessMiningBottleneck`, `ProcessMiningReport` und `build_process_mining_report()` liefern eine erste Mining-Sicht auf Projektionen und Runtime-Komponenten
- AP2: `ProcessObservabilitySignal` bindet `iot_telemetry`-Device- und Reading-Signale an dieselbe Mining-Sicht an; `offline`, `error`, `calibrating` und schlechte Reading-Qualitaet werden als Bottlenecks gespiegelt
- AP3: `POST /api/v1/reporting/process-mining/report` und `GET /api/v1/benchmark/process-mining/{verbund_id}` haengen Reporting und Benchmarking an dieselbe Mining-Sicht
- API: `GET /api/v1/process-mining/finance/report`, `GET /api/v1/process-mining/finance/bottlenecks`, `POST /api/v1/reporting/process-mining/report` und `GET /api/v1/benchmark/process-mining/{verbund_id}` sind als Wave-10-Contracts vorhanden
- Wave-10-Closure abgesichert: **11 Tests gruen** (`tests/test_process_kernel_wave10_process_mining.py`)

### Wave 17: Action Execution Layer und Agent Contracts

Zeitrahmen:
- nach Wave 16

Startbedingung:
- Wave 16 abgeschlossen

Primaere Epics:
- `Epic 1 Process Kernel Platform`
- `Epic 3 Tenant, Security and Integration Governance`

Arbeitspakete:
1. zentralen Execute-Orchestrator auf Basis des bestehenden Command-Katalogs bereitstellen
2. Idempotenz-Store fuer `(tenant_id, idempotency_key)` und Execution-Lookups einfuehren
3. Agent-Beschraenkungen und Aggregate-Ownership im Execute-Pfad erzwingen
4. Process-Kernel-API um Execute- und Snapshot-Contracts erweitern

Wave-Exit:
- Business-Commands sind ueber einen stabilen Execute-Contract statt nur ueber Katalog und Einzel-Dispatch ansprechbar
- Replay und Key-Konflikte sind als Kernel-Contract modelliert
- Agent- und Aggregate-Grenzen werden im Execute-Pfad zentral durchgesetzt

Umgesetzter Stand per 2026-03-13:
- AP1: `ActionExecutionRequest`, `ActionExecutionResult` und `ActionExecutionService.execute()` orchestrieren Dispatch, Agent-Checks und Aggregate-Ownership in `app/core/action_execution.py`
- AP2: `ActionIdempotencyStore` in `app/core/action_idempotency.py` liefert Replay per `execution_id` und `(tenant_id, idempotency_key)`
- AP3: `POST /api/v1/process/actions/execute` behandelt Fresh-, Duplicate- und Conflict-Pfade auf dem bestehenden `/process`-Router
- AP4: `GET /api/v1/process/actions/{execution_id}` und `GET /api/v1/process/actions/idempotency/{tenant_id}/{idempotency_key}` liefern kanonische Action-Snapshots
- Wave-17-Contracts abgesichert: **17 Tests gruen** (`tests/test_process_kernel_wave17_action_execution.py`)

## 5. Execution Board

| Wave | Epic | Owner | Startbedingung | Deliverables | Exit-Kriterium |
|------|------|-------|----------------|--------------|----------------|
| Wave 1 | Process Kernel Platform | `Platform Backend` | Zielbild, ADR-003 bis 010 akzeptiert | Command-Katalog, Workflow-Versionierung, Policy-Prioritäten, Cross-Domain-Referenzen | Prozesskern ist fachlich modelliert und erklärbar |
| Wave 1 | Read, Event and Data Product Platform | `Data & Analytics` | Query-Contract-Standard priorisiert | gehärtete Query-Verträge in Kerncockpits | Kerncockpits laufen ohne implizite Datenzustände |
| Wave 2 | Read, Event and Data Product Platform | `Data & Analytics` | Eventing-Basis definiert | Outbox/Event-Konvention, erste Read-Models, Datenprodukt-Schnitt | Datenfluss-Stack ist produktiv nutzbar |
| Wave 2 | Tenant, Security and Integration Governance | `Integration & Security` | Tenant-/Policy-Basis vorhanden | Verbundmodell, Rollenvererbung, Agenten-Security, Integrationsgrenzen | Tenant- und Agentenregeln sind kontrolliert statt implizit |
| Wave 3 | Specialized Domain Enablers | `Domain Leads` | Plattformkern aus Wave 1 und 2 belastbar | UI-Maskenklassen, Evidence-Modell, Telemetrie, Pricing, Qualität, Importpipelines | Spezialdomänen basieren auf denselben Plattformstandards |

| Wave 4 | Operational Hardening and Runtime Closure | `Platform Backend` + `Data & Analytics` + `Integration & Security` | Waves 1 bis 3 abgeschlossen | persistente Workflow-/Event-Laufzeit, Consumer/Projektionen, SLA-Beobachtung, Runtime-Operations, Contract-konforme Restschliessung | Plattformkern ist operativ belastbar und ohne bekannte Runtime-Provisorien betreibbar |
| Wave 5 | E2E Agrar-Prozesskette und Command-Layer | `Platform Backend` + `Domain Leads` | Wave 4 abgeschlossen | Business-Commands, lueckenlose E2E-Kette, produktionsreife Rohwarenabrechnung, Agent-Contracts | Kernprozess laeuft vollstaendig ueber Commands, E2E-Kette ist lueckenlos und testbar |
| Wave 6 | Agrar-P0 Closure und Supplier-Erweiterung | `Domain Leads` + `Frontend Platform` | Wave 5 AP1+AP2 abgeschlossen | Schlagkartei, Duengebilanz, PSM-Tagebuch, Supplier Portal, erweiterte Kontrakt-/Preislogik, Silo-IoT | Agrar-P0-Pflichten erfuellt, Lieferantenseite produktiv, Branchenprozesse auf Plattformstandard |
| Wave 8 | Reporting, Tenant-Isolation und Agent-Kontexte | `Platform Backend` + `Data & Analytics` + `Integration & Security` | Wave 7 abgeschlossen | Datenprodukte, Reporting, Tenant-Isolation, Agent-Kontexte, Benchmarking, GoBD-Retention | Query- und Agent-Pfade sind tenantgesichert und snapshotbasiert betreibbar |
| Wave 9 | EDI/API-Integration, Ernte-Kampagnen und Frontend-Prozessbindung | `Platform Backend` + `Domain Leads` + `Frontend Platform` | Wave 8 abgeschlossen | EDI-Modelle, API-Partner-Governance, Zertifikate, Ernte-Kampagnen, Frontend-Command-Bindings | externe Integrations- und Ernteprozesse laufen auf denselben Kernel- und Governance-Standards |
| Wave 10 | Process Mining, Observability und Analytics-Verknuepfung | `Platform Backend` + `Data & Analytics` + `Integration & Security` | Wave 9 abgeschlossen | Mining-Report, Bottleneck-Contracts, Observability-Anschluss, Analytics-Verknuepfung | Runtime- und Cursor-Fortschritt ist analytisch nutzbar und ohne Schattenmetriken auswertbar |
| Wave 17 | Action Execution Layer und Agent Contracts | `Platform Backend` + `Integration & Security` | Wave 16 abgeschlossen | Execute-Contract, Idempotenz-Store, Agent-Guards, Action-Snapshots | Commands sind zentral ausfuehrbar, replaybar und ohne zweite Action-API abgesichert |

## 6. Empfohlener Steuerungsmodus

Wöchentlich messen:
- `Delivery`: abgeschlossene Arbeitspakete pro Wave
- `Quality`: Error Rate, Reopen Rate, Konfliktquote, Importfehler
- `Process`: Anteil Kernprozess über Commands/Workflow/Policy
- `Governance`: Anzahl impliziter Sonderpfade, nicht erklärbarer Policy- oder Freigabeentscheidungen

Blocker-Regel:
- kein Wave-Start ohne definierte Startbedingung
- keine Spezialdomäne in Wave 3, wenn Prozesskern und Datenflussstack in Wave 1 und 2 nicht belastbar sind
