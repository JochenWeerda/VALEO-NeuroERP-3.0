# Flow Spine Instance Lifecycle Overview

**Status:** in Umsetzung
**Datum:** 2026-04-17
**Scope:** alle 9 Flow-Spine-Prozessraeume

---

## Ziel

Die bestehenden Flow-Spine-Instanzen sollen von einem leichten Navigationsanker zu einem belastbaren, restart-sicheren Prozessfall ausgebaut werden.

Kuenftig muss jede Instanz fuer alle 9 Prozessraeume einheitlich unterstuetzen:

- anlegen
- speichern und verlassen
- spaeter wieder aufnehmen
- Metadaten und Kontext aendern
- pausieren / blockieren
- fachlich abschliessen
- vorzeitig abbrechen
- als gescheitert markieren
- Ursachen, Bemerkungen und Folgeaktionen dokumentieren
- Timeline- und Auditspur fuehren

---

## Ausgangslage

Aktueller technischer Stand:

- `domain_ops.ops_flow_spine_instances` speichert bereits Grunddaten wie `case_number`, `process_key`, `customer_id`, `customer_name`, `node_statuses` und `active_node_id`.
- `GET /api/v1/process/flow-spines/{process_key}/instances` und `GET /api/v1/process/flow-spines/{process_key}?instance_id=...` liefern und laden Instanzen bereits tenant-isoliert.
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/transitions` persistiert Knotenzustaende.

Aktuelle Luecken:

- Reiner UI-Klick auf einen Prozessknoten persistiert keinen fachlichen Schritt.
- Es gibt keinen separaten Lifecycle-Status einer Instanz.
- Resume-Kontext, letzter sinnvoller Wiedereinstieg und Timeline sind nicht explizit modelliert.
- Vorzeitiger Abbruch, Scheitern und Pause sind nicht als belastbarer Vorgangspfad abgebildet.
- Die 9 Flows nutzen denselben Workspace, aber keinen gemeinsamen Instanz-Lifecycle-Vertrag.

---

## Umsetzungsstand

### FLOW-LC-001 geliefert

Der erste technische Basisslice ist umgesetzt:

- `FlowSpineInstance` traegt jetzt Lifecycle-, Resume-, Owner-, Grund- und Abschlussfelder.
- `domain_ops.ops_flow_spine_instance_events` fuehrt eine persistente Timeline- und Auditspur.
- Die API stellt `PATCH`, `save`, `resume`, `hold`, `complete`, `cancel`, `fail` und `timeline` bereit.
- `transition` bleibt fuer Knotenstatus zustaendig, schreibt aber jetzt ebenfalls in die Eventspur und hebt `draft` sauber auf `in_progress`.

Damit ist der gemeinsame Lifecycle-Kern im Backend vorhanden. Die noch offenen Folgeslices betreffen vor allem:

- UI-Actions und Dialoge im gemeinsamen Workspace
- Grundcode-Kataloge pro Flow
- Resume-/Handover-Integration in die Fachmasken
- Rollout ueber alle 9 Flow-Spine-Prozessraeume

### FLOW-LC-003 geliefert

Der gemeinsame Workspace-Rahmen ist jetzt ebenfalls eingezogen:

- `FlowSpineWorkspace` zeigt bei geladener Instanz Lifecycle-Status, Resume-Ziel, Owner-/Aktivitaetskontext und Kurzsummary.
- Generische Workspace-Aktionen fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail` sprechen den Backend-Vertrag direkt an.
- Timeline-Eintraege sind im rechten Panel sichtbar.
- `cancel` und `fail` erzwingen im UI Kategorie und Grundcode; `hold` nutzt denselben generischen Dialog mit optionalem Block-bis-Feld.

Offen bleiben damit vor allem die flow-spezifischen Resume-/Handover-Pfade und die fachlichen Grundcode-Kataloge.

### FLOW-LC-004 geliefert

Der erste Pilotrollout in echte Fachmasken ist jetzt vorhanden:

- `order-to-cash` schreibt beim Speichern den Resume-Punkt auf die konkrete Auftragsmaske und verankert nach der ersten Anlage die Beleg-ID direkt in der URL.
- `procure-to-pay` schreibt nach erfolgreicher Erstanlage den Resume-Punkt auf die echte Bestell-Detailroute statt auf der transienten Create-Seite stehen zu bleiben.
- `inventory-to-settlement` schreibt vor vertieften Dashboard-Spruengen den jeweiligen operativen Zielpfad als Resume-Ziel und traegt den Workflow-Kontext in die Lager-Teilmasken weiter.

Damit ist der Wiedereinstieg fuer drei priorisierte Prozessraeume nicht mehr nur theoretisch ueber den Workspace moeglich, sondern fuehrt in reale Arbeitsmasken.

### FLOW-LC-005 geliefert

Der Rollout fuer die restlichen sechs Prozessraeume ist jetzt ebenfalls eingezogen:

- `harvest-to-settlement` schreibt beim Speichern auf die konkrete Annahme-Route und verankert nach dem ersten Save die Annahme-ID direkt in der URL.
- `contract-to-settlement` schreibt nach Save auf die echte Kontrakt-Detailroute.
- `complaint-to-resolution` und `service-to-customer` sichern vor `neu`- und Detail-Spruengen die jeweiligen Zielpfade als Resume-Ziel.
- `finance-to-close` persistiert beim Oeffnen das Cockpit selbst und vor Detail-Spruengen die konkrete Abschluss-Checkliste.
- `compliance-to-report` persistiert die CO2-Bilanz-Seite selbst als Resume-Ziel.

Damit sind jetzt alle neun Flow-Spine-Prozessraeume mindestens auf einem belastbaren Resume-/Handover-Niveau in reale Arbeitsmasken angebunden.

---

## Betroffene Prozessraeume

Diese Uebersicht gilt fuer:

1. `order-to-cash`
2. `procure-to-pay`
3. `inventory-to-settlement`
4. `harvest-to-settlement`
5. `contract-to-settlement`
6. `complaint-to-resolution`
7. `service-to-customer`
8. `finance-to-close`
9. `compliance-to-report`

---

## Zielbild

Eine `FlowSpineInstance` ist kuenftig das fuehrende Prozessobjekt fuer den jeweiligen End-to-End-Fall.

Sie ist nicht mehr nur:

- Katalogeintrag
- Routing-Parameter
- lose Statussammlung pro Knoten

sondern ein echter Vorgang mit:

- technischem Lifecycle
- fachlichem Status
- Wiedereinstiegspunkt
- Owner / Verantwortlichkeit
- Abbruch- und Fehlergruenden
- Timeline / Auditspur
- Snapshot fuer Header, Listen und Resume

---

## Gemeinsames Statusmodell

### Technischer Lifecycle

Jede Instanz erhaelt einen gemeinsamen `lifecycle_status`:

- `draft`
- `in_progress`
- `on_hold`
- `completed`
- `cancelled`
- `failed`

### Fachstatus

Zusaetzlich behaelt jede Instanz einen flow-spezifischen `business_status`, zum Beispiel:

- `angebot_offen`
- `lieferung_blockiert`
- `rechnung_freigegeben`
- `settlement_in_pruefung`
- `reklamation_in_bearbeitung`

Regel:

- `lifecycle_status` ist der fuehrende technische Vorgangsstatus
- `business_status` beschreibt die fachliche Feingranularitaet
- `node_statuses` bleiben eine UI-nahe Prozessspine-Sicht, aber nicht der alleinige Wahrheitsanker

---

## Erweiterter Instanzvertrag

### Pflichtfelder auf `FlowSpineInstance`

Folgende Felder sollen ergaenzt werden:

- `lifecycle_status`
- `business_status`
- `resume_node_id`
- `resume_route`
- `resume_payload`
- `assigned_owner`
- `last_activity_at`
- `closed_at`
- `closed_by`
- `cancelled_at`
- `cancelled_by`
- `failed_at`
- `failed_by`
- `completion_reason_code`
- `cancellation_reason_code`
- `failure_reason_code`
- `reason_note`
- `blocked_until`
- `version_no`

### Snapshot

`resume_payload` oder `snapshot_payload` soll den kleinsten sinnvollen Wiedereinstieg enthalten:

- zuletzt relevante Fachmaske
- letzte relevante Route mit Parametern
- sichtbarer Header-Kontext
- Kernobjektbezug wie Kunde, Lieferant, Kontrakt, Kampagne oder Charge
- letzter sinnvoller Arbeitszustand

---

## Timeline- und Auditmodell

Neben der Instanz wird eine Ereignistabelle benoetigt, zum Beispiel `ops_flow_spine_instance_events`.

Pflichtfelder:

- `event_id`
- `instance_id`
- `event_type`
- `from_lifecycle_status`
- `to_lifecycle_status`
- `from_business_status`
- `to_business_status`
- `node_id`
- `actor_id`
- `reason_category`
- `reason_code`
- `reason_note`
- `payload`
- `created_at`

Typische `event_type`:

- `created`
- `saved`
- `resumed`
- `node_transition`
- `handover`
- `hold_set`
- `hold_released`
- `completed`
- `cancelled`
- `failed`
- `owner_changed`
- `note_added`

Optional zusaetzlich:

- `ops_flow_spine_instance_notes` fuer strukturierte Arbeitsnotizen, Lessons Learned und Abbruchhinweise

---

## API-Zielvertrag

### Bestehende Endpunkte behalten

- `POST /api/v1/process/flow-spines/{process_key}/instances`
- `GET /api/v1/process/flow-spines/{process_key}/instances`
- `GET /api/v1/process/flow-spines/{process_key}/instances/{instance_id}`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/transitions`

### Neue Lifecycle-Endpunkte

- `PATCH /api/v1/process/flow-spines/{process_key}/instances/{instance_id}`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/save`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/resume`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/hold`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/complete`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/cancel`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/fail`
- `GET /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/timeline`
- `POST /api/v1/process/flow-spines/{process_key}/instances/{instance_id}/notes`

### Semantik

- `transitions` aendert Knotenstatus
- `save` schreibt Snapshot, Resume-Ziel und Arbeitsstand
- `resume` liefert den letzten sinnvollen Wiedereinstieg
- `hold` pausiert die Instanz
- `complete` schliesst fachlich sauber ab
- `cancel` beendet bewusst mit Pflichtgrund
- `fail` markiert gescheiterten Vorgang mit Pflichtgrund

---

## Abbruch- und Fehlerkonzept

Abbruch und Scheitern muessen strukturiert erfassbar sein.

### Gemeinsame Kategorien

- `customer`
- `supplier`
- `logistics`
- `quality`
- `finance`
- `compliance`
- `technical`
- `internal`

### Beispielhafte Grundcodes

- `customer_order_cancelled`
- `delivery_deadline_missed`
- `quality_rejected`
- `inventory_shortage`
- `approval_denied`
- `external_system_unavailable`
- `data_incomplete`
- `duplicate_case`

### Pflichtregeln

- `cancelled` nur mit `reason_category` und `reason_code`
- `failed` nur mit `reason_category` und `reason_code`
- Freitext `reason_note` optional, aber stark empfohlen
- `on_hold` mit Grund dringend empfohlen

---

## UI-Muster fuer alle 9 Flows

Jede Flow-Spine-Seite soll denselben Instanzrahmen tragen:

- Fallkopf mit `case_number`, Prozessraum, Lifecycle-Status, Business-Status, Owner
- kompakter Kontextblock fuer Kunde / Partner / Kernobjekt
- Timeline mit letzten Ereignissen
- Resume-Hinweis
- Aktionsleiste mit:
  - `Speichern und verlassen`
  - `Wieder aufnehmen`
  - `Bearbeiten`
  - `Pause setzen`
  - `Abschliessen`
  - `Abbrechen`
  - `Als gescheitert markieren`

### Wichtige UI-Regeln

- Ein visueller Klick auf einen Node-Kreis darf keinen Persistenzschritt ausloesen.
- Nur explizite Benutzeraktionen duerfen den Lifecycle oder den Knotenstatus aendern.
- Abbrechen und Scheitern laufen immer ueber denselben strukturierten Dialog.
- Der Resume-Punkt soll nicht nur dieselbe Flow-Seite, sondern den letzten sinnvollen Arbeitskontext oeffnen.

---

## Regeln fuer Fachmasken

Jede aus dem Flow-Spine gestartete Fachmaske muss optional denselben Instanzkontext tragen:

- `workflowProcess`
- `workflowInstanceId`
- `workflowCase`
- `resumeRoute`
- `resumeNodeId`

Beim Verlassen oder Speichern einer Fachmaske gilt:

- `save` aktualisiert Snapshot und Resume-Kontext
- erfolgreicher Fachschritt kann zusaetzlich einen `node_transition` ausloesen
- reine Navigation ohne fachliche Aktion darf keinen Abschluss vortaeuschen

---

## Architekturregeln

1. Keine neun separaten Lifecycle-Implementierungen.
2. Gemeinsame Contracts in API und Frontend, nur Flow-spezifische Konfiguration differiert.
3. `FlowSpineWorkspace` bleibt generischer Rahmen; Fachlogik sitzt in deklarativer Konfiguration oder in klar getrennten Handlern.
4. Timeline-Events muessen tenant-isoliert, auditierbar und spaeter auswertbar sein.
5. Optimistic Locking oder Versionszaehler sind fuer gleichzeitige Bearbeitung vorzusehen.

---

## Rollout in Wellen

### Welle 1 - Infrastruktur

- `FlowSpineInstance` um Lifecycle-Felder erweitern
- Event-/Timeline-Tabelle einfuehren
- Pydantic-Contracts fuer Save / Resume / Hold / Complete / Cancel / Fail
- API-Endpunkte in `flow_spines.py`
- Backend-Tests fuer neuen Lifecycle

### Welle 2 - Gemeinsamer UI-Rahmen

- generische Lifecycle-Aktionsleiste in `FlowSpineWorkspace.tsx`
- gemeinsamer Cancel-/Fail-/Hold-Dialog
- Timeline-Panel
- Resume-Handling

### Welle 3 - Pilotflows

- `order-to-cash`
- `procure-to-pay`
- `inventory-to-settlement`

### Welle 4 - restliche Prozessraeume

- `harvest-to-settlement`
- `contract-to-settlement`
- `complaint-to-resolution`
- `service-to-customer`
- `finance-to-close`
- `compliance-to-report`

---

## Slice-Vorschlag

### FLOW-LC-001 - Instanzmodell und Event-Timeline

- Ziel: `FlowSpineInstance` um Lifecycle-Felder erweitern und Event-Tabelle einfuehren
- Fokus: SQLAlchemy-Modelle, Alembic, Kern-Contracts

### FLOW-LC-002 - Lifecycle-API-Endpunkte

- Ziel: `save`, `resume`, `hold`, `complete`, `cancel`, `fail`, `timeline`, `notes`
- Fokus: `app/api/v1/endpoints/flow_spines.py`, Tests

### FLOW-LC-003 - Gemeinsamer Workspace-Lifecycle-Rahmen

- Ziel: generische Aktionsleiste, Dialoge, Timeline, Resume-Hinweis
- Fokus: `FlowSpineWorkspace.tsx`, API-Hooks, UI-Tests

### FLOW-LC-004 - Pilotrollout OTC / P2P / Inventory

- Ziel: drei priorisierte Prozessraeume komplett auf den Lifecycle-Vertrag ziehen
- Fokus: Resume, Handover, Fachmasken-Anbindung

### FLOW-LC-005 - Rollout restliche 6 Prozessraeume

- Ziel: die uebrigen sechs Flows auf denselben Lifecycle-Vertrag ziehen
- Fokus: prozessspezifische Reason-Codes, Resume-Ziele, Abschlussregeln

### FLOW-LC-006 - Abbruch- und Fehlerkatalog

- Ziel: gemeinsamer Kategorien-/Codekatalog plus flow-spezifische Auspraegung
- Fokus: Doku, Dialog-Optionen, Validierungsregeln

---

## Abnahmekriterien fuer das Gesamtprogramm

- Jede Instanz kann angelegt, gespeichert, pausiert, wieder aufgenommen, abgeschlossen, abgebrochen und als gescheitert markiert werden.
- `cancelled` und `failed` sind ohne Pflichtgrund nicht moeglich.
- Timeline zeigt alle relevanten Lifecycle-Ereignisse.
- Resume fuehrt in den letzten sinnvollen Arbeitskontext.
- Node-Klick allein aendert keine Persistenz.
- Alle 9 Flow-Spine-Seiten nutzen denselben Lifecycle-Rahmen.

---

## Naechster sinnvoller Schritt

Technisch und fachlich ist `FLOW-LC-001` der erste belastbare Einstieg:

- Instanzmodell erweitern
- Event-Tabelle einfuehren
- vorhandene `transition_instance`-Logik sauber in den breiteren Lifecycle-Vertrag einordnen

Erst danach sollte die UI- und Prozessraum-Rollout-Welle starten.
