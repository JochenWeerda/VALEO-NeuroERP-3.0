# VALEO NeuroERP 3.0 vs. YouTube-Projektvorstellung
## GAP-Analyse und Verbesserungsprogramm für die weitere VALEO-Entwicklung

**Erstellt:** 2026-06-23
**Repo:** `JochenWeerda/VALEO-NeuroERP-3.0`
**Vergleichsbasis:** GitHub-Status des Repositories, bereitgestelltes YouTube-Transkript und Screenshots zur Projektvorstellung „Der Moment, der die Softwareentwicklung geändert hat!"
**Bewertung:** scharf, aber praxisorientiert – Ziel ist nicht Nachahmung, sondern Übernahme der belastbaren Engineering-Prinzipien.

---

## 1. Executive Summary

VALEO NeuroERP ist gegenüber der YouTube-Anwendung fachlich deutlich anspruchsvoller: Es ist kein persönliches Backoffice-System, sondern ein mehrdomäniges ERP für Agrargenossenschaften und Landhandel mit FIBU, Lager, Waage, Kontraktwesen, Compliance, HRM, POS, DMS, QS, Prozesskernel, Multi-Tenancy, OIDC, Event-Bus und externen Prüf-Gates.

Die YouTube-Vorstellung ist trotzdem extrem wertvoll, weil sie ein klares Muster zeigt:

> KI beschleunigt Enterprise-Entwicklung nicht durch „Vibe Coding", sondern durch einen harten Harness aus Spezifikationen, Architekturregeln, Testregeln, Tooling, Doku-Sync und kleinen beweisbaren Slices.

VALEO hat diesen Gedanken bereits teilweise sehr gut aufgenommen: `AI-assisted Enterprise Development Standard`, `AI-assisted Development Implementation Plan`, Workboard, Slice-YAML, Docs-Code-Sync, AI-Slice-Readiness, Agent-Ops und klare externe Gates sind vorhanden oder bereits umgesetzt.

Die große Lücke liegt nicht mehr im Denken, sondern in der operativen Härte:

1. **Workflow-Orchestrierung** muss sichtbarer, testbarer und replay-fähiger werden.
2. **Semantische E2E-Tests** müssen von Einzel-Slices auf die echten ERP-Prozessketten skaliert werden.
3. **MCP/Agentenfähigkeit** braucht einen produktiven, rollenbasierten Tool-Katalog statt nur technischer Ansätze.
4. **Doku-Code-Sync** darf nicht nur geplant sein, sondern muss regelmäßig als Artefakt sichtbar werden.
5. **Backend-Coverage 64,85 %** ist für ein ERP langfristig zu niedrig; wichtiger als 100 % ist eine harte Coverage für produktkritische Prozessketten.
6. **n8n/Workflow Engine** sollte nicht blind als Kernlogik übernommen werden; in VALEO gehört deterministische Fachlogik in Process Kernel, Services, Events, Policies und Audit-Logs. n8n-ähnliche Automatisierung ist sinnvoll an den Rändern.

---

## 2. Gegenüberstellung der Zielbilder

| Dimension | YouTube-Projekt | VALEO NeuroERP 3.0 | Bewertung |
|---|---|---|---|
| Fachlicher Scope | Persönliches Backoffice, Homepage, CustomerUI, Rechnung, Beleg, Termine, Zertifikate | 12+ ERP-Domänen für Landhandel/Agrar: Agrar, Sales, Procurement, Inventory, FIBU, CRM, Logistik, Compliance, HRM, POS, Futtermittel | VALEO ist fachlich deutlich breiter und risikoreicher |
| Architektur | 3 UIs → API Gateway → Microservices → je DB; Workflow Engine; externe Services; MCP; Local AI | React/Vite, FastAPI, PostgreSQL/Redis, OIDC, NATS JetStream + Outbox, ChromaDB/RAG, Agent-Ops, Superglue, Docker/Helm/K8s-Pfade | VALEO ist stärker ERP-/Compliance-orientiert; YouTube ist klarer visualisiert |
| KI-Entwicklung | Harness, Specs, Tests, Tools, Voice Driven Development | AI-assisted Enterprise Standard, Slice-Harness, Workboard, Docs-Code-Sync, AI-Slice-Readiness | VALEO hat den Ansatz bereits übernommen; Härtung und Alltagspflicht sind entscheidend |
| Teststrategie | API-Tests + Workflow-Tests + WireMock; ca. 85 % Coverage im Beispiel | Backend 64,85 %, 18/18 kritische Ratchet-Pfade grün; viele Domain-Tests, Playwright-/UAT-Skripte | VALEO braucht mehr semantische Prozessketten-Tests und höhere Ratchets für kritische Pfade |
| DevOps | 2 Dev-Machines, Gitea, Build Runner, Test-/Prod-Env auf NAS | GitHub, CI/Security-Gates, SBOM, immutable Images, Helm atomic rollout, Staging/Prod Releasepfad | VALEO ist produktionsnäher; lokale Agenten-/Harness-Workbench könnte noch besser werden |
| Doku | Nightly Dokumentation, Entwicklerhandbuch, Doku synchron zum Code | Doku-Struktur stark, Docs-Code-Sync geplant/umgesetzt; Open Gaps und Workboard vorhanden | Doku-Sync muss als laufender Drift-Report sichtbar werden |
| Workflow | n8n zentrale Workflow Engine | Process Kernel, NATS/Outbox, WF-Trigger-Log, Workflows/Runbooks | VALEO sollte n8n nicht als Kern übernehmen, aber ein Workflow-Cockpit / Prozess-Leitstand fehlt |
| Lokale KI | Local AI + MCP + Hermes-Agent | Voice-Kanal, RAG/Wissensbase, Superglue, MCP-Dateien/Server vorhanden | Zielbild: rollenbasierter ERP-Agent mit Least Privilege, Tool-Verträgen und Audit |

---

## 3. Was VALEO NICHT unkritisch übernehmen sollte

### 3.1 Keine pauschale 93x-Produktivitätsplanung

Der im Video genannte Geschwindigkeitsfaktor ist als Erfahrungsbericht interessant, aber für VALEO keine Planungsgrundlage. VALEO muss nach Evidenz planen:

- Welche Prozesskette ist fachlich geschlossen?
- Welche Tests belegen sie?
- Welche externen Gates sind offen?
- Welche Datenmigration ist abgesichert?
- Welche Risiken bleiben?

**Empfehlung:** Produktivität nicht in „x-mal schneller" messen, sondern in `Cycle Time je beweisbarem Slice`, `Defect Escape Rate`, `Doku-Drift`, `Test-Fail-Rate`, `Coverage kritischer Pfade`, `externe Gate-Blocker`.

### 3.2 Kein n8n als unkontrollierter ERP-Kern

n8n ist hervorragend für Automatisierung, Benachrichtigungen und Integrations-Orchestrierung. Für VALEO-Kernprozesse wie FIBU, Waage, POS/TSE, Payroll, QS-Freigabe, Kontrakt-Settlement oder GoBD-Nachweisraum wäre eine unkontrollierte Workflow-Engine gefährlich.

**Regel für VALEO:**

- Deterministische Fachlogik bleibt in Services, Process Kernel, Policies und auditierten Events.
- n8n/Superglue/Workflow-Tools dürfen Randprozesse orchestrieren.
- Jede irreversible Aktion braucht Tenant, Berechtigung, Idempotenz, Audit, Rollback-/Kompensationspfad und Human Approval, wenn rechtlich relevant.

### 3.3 Keine Microservice-Explosion nur wegen Architektur-Optik

Das YouTube-Bild zeigt viele Microservices mit eigener Datenbank. Für VALEO ist das nicht automatisch besser. VALEO braucht Domänengrenzen, aber nicht zwingend physisch getrennte Deployments pro Domain.

**Empfehlung:** Erst modulare, saubere Domain-Services und stabile Contracts. Physische Microservices nur dort, wo Skalierung, Teamgrenze, Ausfallisolierung oder Compliance es wirklich erzwingen.

### 3.4 Kein Agent mit zu breitem Produktionszugriff

Der YouTube-Ansatz mit Agentenzugriff auf Test-/Prod-Logs ist nützlich. Für VALEO darf daraus kein Agent mit freiem Produktionszugriff werden.

**VALEO-Regel:** Agenten erhalten nur rollenbasierte, auditierte, zeitlich begrenzte Tools. Produktive Schreibaktionen brauchen Freigabe oder sehr enge Guardrails.

---

## 4. GAP-Analyse

### 4.1 Architektur- und Prozess-GAPs

| GAP | Aktueller Eindruck VALEO | Warum kritisch | Verbesserung |
|---|---|---|---|
| Workflow-Cockpit fehlt als zentrale Sicht | Process Kernel, WF-Trigger und Event-Bus vorhanden, aber nicht so klar sichtbar wie n8n-Overview | Operatoren brauchen Sicht auf laufende Prozesse, Fehler, Replay, Dead Letter, externe Blocker | `VALEO-WF-COCKPIT-001`: Prozessleitstand mit Trigger-Log, Event-Kette, Status, Replay, Blocker, externem Gate |
| MCP-Toolkatalog noch nicht als Produktvertrag sichtbar genug | MCP-Dateien und Server existieren, aber kein klarer ERP-Agent-Katalog mit Rechten/Tests | Ohne Tool-Vertrag wird Agentenfähigkeit unscharf | `MCP-ERP-TOOLS-001`: Tool Registry je Domain, Scopes, Input/Output-Schema, Idempotenz, Testfälle |
| KI-Agent „Hermes"-Äquivalent fehlt als klares Zielbild | Agent-Ops/Voice/RAG vorhanden | VALEO braucht später echten Operator-/Backoffice-Agenten, nicht nur Entwickler-Agenten | `VALEO-OPERATOR-AGENT-001`: Aufgaben wie Rechnungsvorschlag, Wiedervorlage, Mahnung, Angebot, Lieferkettenabfrage |
| Externe Integrationen brauchen mehr Mock-/Contract-Schicht | Live-Credentials und externe Systeme bleiben Gates | Tests dürfen nicht von Office/DATEV/DMS/TSE/ELSTER live abhängen | WireMock-/Mockserver-Konzept für DATEV, DMS, TSE, ELSTER, Banken, Mail, L3 |
| Semantische UI-Klicktests noch nicht konsequent repo-weit | Playwright und UAT vorhanden, aber nicht als durchgängige semantische Action-Matrix für alle Kernflüsse | 404-freie Navigation reicht nicht; Buttons müssen fachlich das Richtige tun | CRM360, O2C, P2P, WMS, FIBU, POS/TSE, QS mit Action-Matrix absichern |
| Doku-Code-Sync braucht Betriebsevidenz | Plan/Standard vorhanden | Ohne regelmäßige Artefakte entsteht wieder Doku-Drift | Nightly Drift Report mit CI-Artefakt und Schwellwerten |
| Coverage repo-weit zu niedrig für ERP-Langfristbetrieb | 64,85 %, kritische Pfade grün | Akzeptabel für Alpha, aber zu wenig für produktionsnahes ERP | Ratchet schrittweise: kritische Pfade 85–95 %, Gesamt 70 → 75 → 80 % |
| Branch-/Release-Disziplin muss hart bleiben | main/develop derzeit identisch geprüft; Releasepfad dokumentiert | Viele Agenten erhöhen Risiko paralleler Konflikte | Branch Protection, Pflicht-Reviewer, Slice-Dateibesitz und keine fremden WIP-Bündel |

---

## 5. Was konkret aus der YouTube-Vorstellung übernommen werden sollte

### 5.1 Harness-first als eiserne Regel

**Übernehmen:** Erst Harness, dann Code.

Jeder größere VALEO-Slice muss vor Umsetzung enthalten:

- fachlicher Vertrag
- Architekturvertrag
- Datenvertrag
- Testvertrag
- Security-Vertrag
- Betriebsvertrag
- Dokumentationsvertrag
- externe Gates

Das ist in VALEO bereits konzeptionell vorhanden. Jetzt muss es operativ erzwungen werden.

**Konsequenz:** Kein Agenten-Slice darf „in Arbeit" gehen, wenn Slice-YAML, Dateibesitz, Akzeptanzkriterien und Teststrategie fehlen.

---

### 5.2 Spec-/Test-driven Development statt Prompt-driven Coding

**Übernehmen:** Die KI soll nicht aus einem groben Wunsch Code erzeugen, sondern aus Anforderungen und Akzeptanzkriterien zuerst Tests und Verträge ableiten.

**VALEO-Regel:**

1. User Story / Prozessziel
2. Akzeptanzkriterien
3. Daten-/Tenant-/Audit-Vertrag
4. Testfälle
5. Erst danach Implementierung
6. Danach Doku-Sync und Gaps aktualisieren

---

### 5.3 Workflow-Tests mit Mock externer Systeme

**Übernehmen:** Das Prinzip aus der Testing-Folie: Workflow-Tests dürfen externe Systeme simulieren.

Für VALEO besonders wichtig:

- DATEV/Kanzlei-Export
- DMS/Paperless
- TSE/DSFinV-K
- ELSTER/ERiC
- Bank/MT940/CAMT
- E-Mail/Teams/Outlook
- L3-/zvoove-Import
- Waage-/Druckerhardware

**Ziel:** Jeder externe Gate bekommt einen repo-seitigen Simulator/Mock, aber ohne externe Zertifizierung zu behaupten.

---

### 5.4 Nightly Documentation Sync

**Übernehmen:** Doku-Drift wird zum Fehler.

VALEO sollte nicht automatisch Doku überschreiben, aber jede Nacht einen Drift-Report erzeugen:

- neue Routen ohne API-/QA-Doku
- neue Migrationen ohne Runbook/Gaps
- neue Domain-Services ohne Fachprozessbeleg
- UI-Seiten ohne Action-Matrix
- Tests ohne Traceability

---

### 5.5 Voice Driven Development vorsichtig übernehmen

Voice Driven Development ist für VALEO wertvoll, aber nicht als „freie Erzählung → Code". Es sollte als Anforderungs- und Review-Werkzeug genutzt werden.

**Sinnvolle Nutzung:**

- Prozess mit Fachanwender durchsprechen
- daraus Akzeptanzkriterien ableiten
- Edge Cases sammeln
- Rückfragen generieren
- Fachsprache in Domain-Modell überführen

**Nicht sinnvoll:** Sprache direkt in Code ohne Test- und Architekturvertrag.

---

## 6. Priorisierte Verbesserungsliste

### P0 — Sofort umsetzen

#### P0.1 `VALEO-WF-COCKPIT-001`: Prozess- und Workflow-Leitstand

**Ziel:** Sichtbarkeit über Prozesse, Events, Trigger, externe Gates und Fehler.

**Funktionen:**

- Prozessinstanzen mit Status: `pending`, `running`, `blocked_external_gate`, `failed`, `completed`, `compensated`
- Event-Kette je Prozess
- Dead-Letter-/Retry-Sicht
- Replay nur mit Berechtigung
- Externe Gate-Markierung
- Verbindung zu Audit-Log und Doku

**Warum P0:** Ohne Prozesssicht bleibt Event-/Workflowfähigkeit technisch stark, aber operativ unsichtbar.

---

#### P0.2 `SEMANTIC-E2E-MATRIX-001`: Action-Matrix für kritische UI-Flows

**Ziel:** Nicht nur Klickbarkeit testen, sondern fachlich richtige Aktionen.

**Startflows:**

1. CRM360: Kunde → Angebot → Auftrag → Lieferschein → Rechnung → Zahlung
2. WMS/Silo: Annahme → Waage → Lot → Silozelle → QS → Trace
3. P2P: RFQ → Bestellung → Wareneingang → 3-Wege-Match → ERS/Rechnung
4. FIBU: OP → Zahlung → Auszifferung → Mahnung → DATEV-Export
5. POS/TSE: Bon → Zahlung → Tagesabschluss → DSFinV-K → FIBU
6. QS/Reklamation: Labor → Sperre/Freigabe → Retoure/Gutschrift → CAPA

**Prüfkriterien je Button/Aktion:**

- Zielroute
- Zielmaske
- Entity-Kontext
- CRUD-Typ
- Rechteprüfung
- Back-Verhalten
- Fehlerfreiheit Console/Network
- fachliche Plausibilität

---

#### P0.3 `MCP-ERP-TOOLS-001`: Produktiver ERP-MCP-Toolkatalog

**Ziel:** Agenten können VALEO nicht nur lesen, sondern kontrolliert handeln.

**Tool-Gruppen:**

- CRM: Kunde suchen, 360-Zusammenfassung, Kontaktprotokoll, Angebotsvorschlag
- Sales/O2C: Auftrag prüfen, Lieferscheinstatus, Rechnungsvorschlag
- FIBU: OP-Liste, Mahnstatus, DATEV-Exportstatus, Zahlungsvorschlag
- WMS/QS: Lot verfolgen, Sperrstatus, Silozelle, QS-Freigabe
- DMS: Dokument suchen, Nachweisraum-Paket, GoBD-Export
- Compliance: externe Gate-Status, Sperren, Audit-Belege

**Pflicht:** Jedes Tool braucht Schema, Scope, Idempotenz, Audit, Test, Risiko-Klasse.

---

#### P0.4 `COVERAGE-RATCHET-ERP-CORE-001`

**Ziel:** Coverage nicht kosmetisch erhöhen, sondern produktkritische Prozessketten absichern.

**Vorschlag:**

- Gesamt-Coverage kurzfristig: 64,85 % → 70 %
- Kritische Prozessketten: 85–95 %
- Neue Services: Mindest-Ratchet je Risiko
- Keine neue kritische Domain ohne Testvertrag

---

### P1 — Nächste Ausbaustufe

#### P1.1 `EXTERNAL-MOCK-HARNESS-001`

Mock-/Contract-Schicht für:

- DATEV / Kanzlei-Export
- DMS/Paperless
- TSE/DSFinV-K
- ERiC/ELSTER
- Bankdateien
- Mail/Teams/Outlook
- Waage/Drucker

Ergebnis: Tests werden reproduzierbar, externe Gates bleiben ehrlich getrennt.

---

#### P1.2 `AI-DOC-DRIFT-DASHBOARD-001`

Der Nightly-Drift-Report sollte nicht nur als CI-Artefakt existieren, sondern auch als Dashboard:

- neue APIs ohne Doku
- Migrationen ohne Runbook
- UI-Seiten ohne Action-Matrix
- offene externe Gates
- veraltete Gap-Einträge
- Slice-Abschluss ohne Verifikation

---

#### P1.3 `OPERATOR-AGENT-001`

Ein produktiver Agent darf nicht direkt „alles können". Start mit Assistenzmodus:

- liest Kontext
- schlägt Handlung vor
- erzeugt Entwurf
- verlangt Human Approval
- schreibt nach Freigabe
- protokolliert alles

Erste Use Cases:

- Mahnvorschlag
- Angebotsnachfassung
- offene UAT-/Gate-Liste
- Rechnungsvorschlag aus Lieferschein
- QS-Sperrliste
- DMS-Nachweisraum-Paket

---

#### P1.4 `DEV-HARNESS-CLI-001`

Ein einheitlicher Agenten-Workflow als CLI:

```bash
valeo-slice claim <SLICE-ID>
valeo-slice plan <SLICE-ID>
valeo-slice test-first <SLICE-ID>
valeo-slice implement <SLICE-ID>
valeo-slice verify <SLICE-ID>
valeo-slice docs-sync <SLICE-ID>
valeo-slice close <SLICE-ID>
```

Ziel: Agentenarbeit wird wiederholbar und prüfbar, nicht chatabhängig.

---

### P2 — Mittelfristig

#### P2.1 Workflow Designer / Prozesskarte

Nicht zwingend n8n, aber eine visuelle Prozesskarte:

- ERP-Prozessketten
- Events
- Policies
- externe Gates
- Verantwortlichkeiten
- SLA/Blocker

#### P2.2 Produktivitätsmetriken für AI-Engineering

Messen:

- Slice Cycle Time
- Rework-Quote
- Test-Fail-Ursachen
- Doku-Drift
- externe Gate-Blocker
- Agentenfehler nach Ursache
- Review-Aufwand

#### P2.3 Lokale KI-Datenklassen

Definieren:

- darf externes Modell sehen
- nur EU/API
- nur lokal
- niemals Modellkontext
- synthetisch/anonymisiert erlaubt

---

## 7. 30/60/90-Tage-Plan

### Erste 30 Tage

1. Semantic Action Matrix für CRM360 und WMS/Silo starten.
2. MCP-Toolkatalog als `docs/architecture/mcp-erp-tool-registry.md` anlegen.
3. Workflow-Cockpit-Konzept mit Datenmodell und API-Vertrag schreiben.
4. Coverage-Ratchet für 5 produktkritische Prozessketten anheben.
5. Nightly Doku-Drift-Report als CI-Artefakt prüfen und sichtbar machen.

### 31–60 Tage

1. Workflow-Cockpit MVP implementieren.
2. External Mock Harness für DMS, DATEV, TSE und Bank starten.
3. Operator-Agent im Read-only/Proposal-Modus.
4. Dev-Harness-CLI für Slice-Claim, Verify und Close.
5. Playwright semantisch für CRM360, O2C, WMS/Silo und FIBU.

### 61–90 Tage

1. Operator-Agent mit kontrollierten Schreibaktionen für risikoarme Use Cases.
2. Prozesskarte für O2C, P2P, WMS, POS, FIBU.
3. Coverage-Ratchet Gesamtziel 70–75 %, kritische Pfade 85–95 %.
4. Externe Gate-Dashboards.
5. Release-Freigabe nur noch mit sichtbarer Prozess-/Doku-/Test-Evidenz.

---

## 8. Konkreter erster Slice-Vorschlag

```yaml
slice_id: VALEO-WF-COCKPIT-001
title: Workflow- und Prozessleitstand für VALEO Process Kernel
priority: P0
owner: Cursor/Codex
status: offen
goal: >
  Einen operativen Workflow-Leitstand schaffen, der Process-Kernel-Trigger,
  Domain-Events, externe Gates, Fehler, Retry, Replay und Audit sichtbar macht.
ai_harness:
  fachlicher_vertrag:
    - Prozessinstanzen müssen je Tenant sichtbar sein.
    - Status blockiert_externes_gate muss getrennt von failed geführt werden.
    - Replay darf nur berechtigten Rollen offenstehen.
  architekturvertrag:
    - Keine unkontrollierte n8n-Kernlogik.
    - Process Kernel, Outbox/NATS und Audit bleiben Source of Truth.
    - UI als Meridian Worklist/ListReport.
  datenvertrag:
    - wf_process_instance
    - wf_process_event
    - wf_process_blocker
    - tenant_id, correlation_id, idempotency_key, audit fields
  testvertrag:
    - Unit Tests für Statusübergänge
    - API Contract Tests
    - Playwright Smoke für Leitstand
    - Fehlerfall: Replay ohne Recht blockiert
  security_vertrag:
    - OIDC/RBAC
    - Tenant Isolation
    - Audit für Replay/Retry
  dokumentationsvertrag:
    - Workflow-Doku
    - Open-Gaps Update
    - UAT-Szenario
external_gates:
  - Keine externe Abnahme erforderlich für MVP
definition_of_done:
  - Tests grün
  - API dokumentiert
  - UI sichtbar
  - Audit/Replay abgesichert
  - Doku-Code-Sync bestanden
```

---

## 9. Scharfe Schlussbewertung

VALEO ist nicht hinter dem YouTube-Projekt zurück. In vielen Punkten ist VALEO bereits professioneller, weil es echte ERP-, Compliance-, Multi-Tenant- und Produktionsfreigabe-Anforderungen ernst nimmt.

Die Gefahr liegt woanders:

VALEO kann durch seine Breite unübersichtlich werden. Das YouTube-Projekt wirkt deshalb stark, weil es sehr klare Ebenen zeigt:

- Architecture
- DevOps
- Testing
- Harness
- Voice/Spec/Test Driven Development

VALEO braucht jetzt genau diese Klarheit als operative Steuerungsebene.

**Kurzform:**

- Nicht mehr nur weitere Funktionen bauen.
- Jetzt Prozesssicht, Agentenverträge, semantische Tests, externe Mock-Gates und Doku-Drift-Härte ausbauen.
- KI nicht als Code-Turbo betrachten, sondern als beschleunigten, beweisbaren Engineering-Betrieb.

---

## 10. Quellen und Repo-Belege

### GitHub-Statusquellen

- `README.md` — Produktstatus, Domänen, Architektur, Reifegrad.
- `docs/project-context/open-gaps-and-known-issues.md` — offene Punkte, Build-Health, externe Gates, Domain-Parity.
- `docs/architecture/process-kernel/STATUS.md` — Process-Kernel, Teststatus, Waves, Production Readiness.
- `docs/agent-ops/active-workboard.md` — laufende/abgeschlossene Slices, AI-Harness-GOV, Agentenkoordination.
- `docs/architecture/ai-assisted-enterprise-development-standard.md` — aus YouTube-Transkript abgeleiteter VALEO-Standard.
- `docs/project-context/ai-assisted-development-implementation-plan-2026-06-23.md` — operative Umsetzung des AI-Harness.
- `docs/operations/production-readiness-runbook.md` — fail-closed Release- und External-Gate-Ansatz.

### YouTube-Vergleichsbasis

- Bereitgestelltes Transkript und Screenshots:
  - Architecture
  - DevOps
  - Testing
  - Phase 5: Voice Driven
  - BackOffice UI
  - n8n Workflow Overview
