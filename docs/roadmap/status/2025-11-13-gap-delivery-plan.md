# Delivery-Plan Must-Have Gaps – Stand 13.11.2025

## Ziel
Schrittweise Umsetzung der noch offenen Must-Have-Gaps: **InfraStat**, **Zoll/Exportkontrolle**, **RAG-Gateway**, **QA-Automatisierung**.  
Plan bezieht sich auf Ergebnisse der Gap-Audit-Datei `docs/roadmap/status/2025-11-13-must-have-gap-audit.md`.

---

## 1. InfraStat / Intrastat Automation

### Architektur
- Neuer Microservice `services/compliance/infrastat/` (FastAPI + SQLAlchemy).
- Persistenz: Postgres-Schema `compliance_infrastat` mit Tabellen `declaration_batches`, `declaration_lines`, `validation_errors`, `submission_log`.
- Event-getriebene Vorbefüllung (NATS Subjects `inventory.shipment.posted`, `purchase.receipt.posted`, `finance.invoice.booked`).
- Saga-Orchestrierung via bestehendem Workflow-Service (State-Machine `INTRASTAT_SAGA`).
- Ausleitung: XML/CSV-Export für ELSTER/IDEV (Mock-Endpunkte in QA).

### Umsetzungs-Backlog
1. **Scaffolding & Config**  
   - [x] Verzeichnis anlegen, Settings & Dependency Injection aufsetzen (analog Workflow-Service).  
   - [x] Datenbankmigration (Alembic) erzeugen.
2. **Datenmodell & Ingestion**  
   - [x] ETL-Pipeline: Mapping von Warenwirtschaft (Warennummer, USt-ID, Gewicht, Wert) → `declaration_lines`.  
   - [x] Validierungen (Pflichtfelder, TARIC-Check, Mengeneinheit) inkl. automatischer Statuswechsel `COLLECTING → VALIDATING → READY/ERROR`.
3. **Saga-Integration**  
   - [x] Workflow-Trigger via EventBus (`intrastat.validation.completed`, `intrastat.batch.ready`, `intrastat.validation.failed`).  
   - [ ] Workflow-Definition `intrastat_monthly_cycle` (States: Collecting, Validating, ReadyToSubmit, Submitted, Archived).  
   - [ ] Event Hooks für Fehler-/Retry-Pfade.
4. **Submission Layer**  
   - [x] Export-Adapter (XML nach INSTAT 6.3) + Session-basierter IDEV-Client mit Zertifikats-Support.  
   - [x] Submission-API `/api/v1/batches/{id}/submit` inkl. Logging und Events `submission.started/completed/failed`.  
   - [ ] Automatisierte Übertragung mit echten IDEV-Credentials (Secrets + Alerting).
5. **Tests & Monitoring**  
   - [x] Unit-Tests für Ingestion, Submission, Scheduler, Workflow-Definition (CI-Job `InfraStat Service Tests`).  
   - [ ] Integrationstests mit echtem Postgres + Workflow-Saga.  
   - [ ] Prometheus-Metriken (Anzahl Meldungen, Fehlerquote) inkl. Smoke-Test.  
   - [x] Contract-Tests gegen Workflow-Service.

### Abhängigkeiten
- Zugriff auf Produkt-/Belegdaten (Inventory-, Finance-Domains).  
- Referenzdaten (TARIC, Länder-/Warentabellen) als Seed (`data/reference/intrastat/`).

---

## 2. Zoll & Exportkontrolle

### Architektur
- Neuer Microservice `services/compliance/zoll/` mit FastAPI, Async-Postgres und NATS Event-Bus.
- Module: Screening-Engine (Sanktionslisten), Export-Genehmigungen, Präferenzkalkulation.
- Event-basierte Workflow-Integration (`compliance.zoll.*`).

### Umsetzungs-Backlog
1. **Scaffolding & Config**  
   - [x] Service-Struktur, Settings, DB-Modelle (`ScreeningMatch`, `ExportPermit`, `PreferenceCalculation`).
2. **Geschäftslogik**  
   - [x] Screening-Service (lokale CSV + rudimentäre Fuzzy-Logik, Persistenz).  
   - [x] Genehmigungs-CRUD + Präferenzkalkulation (Originating-Quote).  
   - [ ] Live-Schnittstellen (OFAC/EU Listen, BAFA).  
   - [ ] Workflow-Hooks & Policies (z. B. `export.screening.failed`).
3. **API & Tests**  
   - [x] REST-Endpunkte `/screening`, `/permits`, `/preference`.  
   - [x] Unit-Tests (CI-Job `Zoll Service Tests`).  
   - [ ] Integrationstests / Contract-Tests.
4. **CI/CD**  
   - [x] Eigener Test-Job in `.github/workflows/ci.yml`.  
   - [ ] Container-Build & Helm Values ergänzen.

### Nächste Aufgaben
- Echtzeit-Updates für Sanktionslisten (Scheduler + Provider-APIs).  
- Workflow-Definition `export_clearance` mit Block/Review-Knoten.  
- Präferenzkalkulation an BOM-Service koppeln.

---

## 3. RAG-Gateway

### Architektur
- Service `services/rag-gateway/` (FastAPI oder Node). Empfehlung: FastAPI für Homogenität.
- Schnittstellen:
  - `POST /api/v1/retrieval/query` → orchestriert Vector Store + LLM (via `services/ai`).
  - `POST /api/v1/retrieval/feedback` → Re-Ranking, Bewertung.
  - `POST /api/v1/admin/datasets` → Dataset-Verwaltung, Namespace-Support.
- Storage: Vector DB (Chroma oder Pinecone). Konfiguration via ENV.
- AuthN/AuthZ: OAuth2/JWT, Tenant-Scopes.
- Observability: OpenTelemetry, Prometheus.

### Umsetzungs-Backlog
1. **Gerüst & Konfiguration**  
   - Service-Struktur + Settings (`rag_gateway/config.py`).  
   - Dependency Injection (VectorStoreClient, LLMClient).
2. **Retrieval-Pipeline**  
   - Dokument-Indexierung via `tools/rag-sync` (Webhook oder Polling).  
   - Query-Flow: Embedding → Search → Answer Compose (Streaming optional).
3. **Access Control & Policies**  
   - Mandanten-Namespaces, RBAC (Mapping zu Rollen aus Auth-Service).  
   - Rate-Limiting, Audit-Logging.
4. **Feedback Loop**  
   - Speicherung von Bewertungen, Feeds für Re-Ranking/MLOps.  
   - Reporting (Top Queries, Satisfaction Score).
5. **Tests & CI**  
   - Contract-Tests mit `services/ai`.  
   - Load-Test Baseline (Locust/Playwright API).

### Abhängigkeiten
- `tools/rag-sync` (bestehend) zur Datenbefüllung.  
- AI-Service (`services/ai`) für LLM/Embedding Fallback.

---

## 4. QA-Automatisierung

### Zielbild
- Abdeckung der neuen Compliance- und RAG-Komponenten in CI/CD (`.github/workflows/ci.yml`).
- Kombi aus Unit-, Integration-, Contract- und End-to-End-Tests.

### Maßnahmen
1. **Test-Suites erweitern**
   - `tests/compliance/` um `test_infrastat.py`, `test_customs.py`.  
   - `tests/rag/` für Retrieval und AuthZ.
2. **Synthetic Data & Fixtures**
   - `qa/datasets/compliance/infra_stat_sample.json`.  
   - `qa/datasets/rag/knowledge_base_subset.json`.
3. **CI-Pipeline anpassen**
   - Neue Jobs: `compliance-services`, `rag-gateway`.  
   - Coverage-Upload + Artifact-Publishing (Berichte).
4. **Observability Checks**
   - Smoke-Tests nach Deploy (HTTP Health, Metrics).  
   - Alerting-Config (Prometheus Alertmanager).
5. **Playwright / API Tests**
   - Erweiterung `playwright-tests/` für Compliance-UI (Genehmigungsworkflow, Meldestatus).  
   - API-Szenarien für RAG-Gateway (`qa/api/rag-gateway.test.ts`).

---

## Sequenzierung & Verantwortlichkeiten

| Sprint | Fokus | Deliverables | Hauptteam |
|--------|-------|--------------|-----------|
| SP-1 | InfraStat Foundation | Service-Scaffold, Datenmodell, ETL, Validierung | Compliance-Agent |
| SP-2 | Zoll Engine | Screening + Genehmigungen, Workflow-Integration | Compliance + Workflow |
| SP-3 | Inventory & Finance Service Enablement | Microservice-Adaption, Persistenz, Events | Supply-Chain + Finance |
| SP-4 | RAG-Gateway | API, Vector Store, AuthZ, Monitoring | RAG-Agent |
| SP-5 | QA-Ausbau | CI-Jobs, Synthetic Data, E2E | QA/Analytics |

---

## Offene Punkte
- Entscheidung über Technik-Stack für RAG-Gateway (Python vs. Node).  
- Bereitstellung echter Sanktionslisten/TARIC-Daten (Lizenz/Quelle).  
- Abstimmung mit DevOps bzgl. Infrastruktur (Postgres-Schema, Vector Store Deployment).

_Erstellt von GPT-5 Codex, 13.11.2025_

