***REMOVED*** 🗺️ VALEO NeuroERP - Gesamtfahrplan (6-9 Monate)

**Version:** 1.0  
**Erstellt:** 2025-10-11  
**Basis:** `docs/analysis/valeoneuroerp_soll_ist.md`  
**Ziel:** Transformation vom Monolithen zum agentischen MSOA-System

---

***REMOVED******REMOVED*** 🎯 VISION & PRINZIPIEN

***REMOVED******REMOVED******REMOVED*** **Ziel-Architektur:**
- ✅ MSOA/DDD mit 19 entkoppelten Domains
- ✅ Event-driven Architecture (NATS/Kafka)
- ✅ Agentische Layer (LangGraph + MCP)
- ✅ Polyglotte Persistenz
- ✅ OIDC/RBAC Security
- ✅ Full Observability (Prometheus/Grafana/Loki)

***REMOVED******REMOVED******REMOVED*** **Leitprinzipien:**
1. **Evolutionär, nicht revolutionär** - Kein Big-Bang, sondern schrittweise Migration
2. **Messbare Inkremente** - Jede Phase liefert produktiven Mehrwert
3. **Abhängigkeiten respektieren** - Service-Kernel vor Microservices
4. **Quality Gates** - Keine Phase ohne Tests & Docs

---

***REMOVED******REMOVED*** 📅 PHASEN-ÜBERSICHT

```
┌──────────────────────────────────────────────────────────────┐
│ Phase 0 │ Phase 1  │ Phase 2   │ Phase 3   │ Phase 4        │
│ 0-2 W   │ 2-6 W    │ 6-10 W    │ 10-16 W   │ 16-24 W        │
├─────────┼──────────┼───────────┼───────────┼────────────────┤
│ Grund-  │ Service- │ Security  │ Events &  │ Skalierung &   │
│ lage    │ Kernel & │ & UX      │ Agentik   │ Compliance     │
│         │ API      │           │           │                │
│ DB ✅   │ Domains  │ OIDC/RBAC │ Event-Bus │ Microservices  │
│ Seeds ✅│ API Real │ Storybook │ LangGraph │ Pen-Test       │
│ CI ✅   │ Metrics  │ E2E Tests │ RAG       │ DSGVO/GxP      │
└─────────┴──────────┴───────────┴───────────┴────────────────┘
         ↑           ↑           ↑           ↑
      2 Wochen   6 Wochen   10 Wochen   16 Wochen   24 Wochen
```

**Gesamt:** 24 Wochen = 6 Monate (Best Case) bis 9 Monate (Realistic)

---

***REMOVED******REMOVED*** 🚀 PHASE 0: GRUNDLAGE (0-2 Wochen)

**Ziel:** Stabile Datenbasis, funktionierende CI, OIDC vorbereitet

***REMOVED******REMOVED******REMOVED*** **Sprint 1 (Woche 1):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **1.1 DB & Migrationen** (3 Tage)
- [ ] Alembic-Migrationen harmonisieren (`tenants` vs `shared_tenants`)
- [ ] Neue Tabellen hinzufügen (`policy_rules`, `tse_transactions`, `suspended_sales`)
- [ ] Migration-Tests (Up/Down) automatisieren
- [ ] PostgreSQL-Schema-Dokumentation generieren

**Deliverable:** ✅ Alle Tabellen migriert, keine Schema-Divergenz

**Akzeptanzkriterium:**
```bash
alembic upgrade head  ***REMOVED*** ✅ Funktioniert
alembic downgrade -1  ***REMOVED*** ✅ Rollback OK
pytest tests/migrations/  ***REMOVED*** ✅ Alle grün
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **1.2 Seed-Skripte** (2 Tage)
- [ ] Inventory-Seed (100 Artikel mit EAN, Kategorien)
- [ ] CRM-Seed (50 Kunden, 20 Lieferanten)
- [ ] Finance-Seed (Kontenplan SKR03, Buchungen)
- [ ] Policy-Seed (10 Policies mit Rules)
- [ ] User-Seed (Admin + Test-User mit Rollen)

**Deliverable:** ✅ Reproduzierbare Test-Daten

**Akzeptanzkriterium:**
```bash
python scripts/seed_all.py  ***REMOVED*** ✅ Funktioniert
***REMOVED*** → DB mit 100 Artikeln, 50 Kunden, 10 Policies
```

---

***REMOVED******REMOVED******REMOVED*** **Sprint 2 (Woche 2):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **2.1 CI-Setup** (3 Tage)
- [ ] GitHub Actions: Lint (ESLint + Ruff/Black)
- [ ] GitHub Actions: TypeScript-Check
- [ ] GitHub Actions: Pytest (Backend)
- [ ] GitHub Actions: Migration-Check (`alembic check`)
- [ ] Branch-Protection (develop: min. 1 Approval)

**Deliverable:** ✅ Automatisierte Quality Gates

**Akzeptanzkriterium:**
```yaml
***REMOVED*** .github/workflows/ci.yml
✅ Lint passes
✅ TypeScript passes
✅ Pytest passes
✅ Migrations valid
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **2.2 OIDC-Vorbereitung** (2 Tage)
- [ ] `.env.example` mit OIDC-Variablen
- [ ] Dev-Token nur noch über `.env`
- [ ] Test-OIDC-Provider dokumentieren (Keycloak/Auth0)
- [ ] OIDC-Stubs im Backend (noch nicht aktiv)

**Deliverable:** ✅ OIDC-Ready (aber noch Dev-Token)

**Akzeptanzkriterium:**
```bash
***REMOVED*** .env
OIDC_AUTHORITY=https://...
OIDC_CLIENT_ID=...
***REMOVED*** Backend läuft mit Dev-Token UND mit OIDC-Config
```

---

**Phase 0 Exit-Criteria:**
- ✅ Alle Migrationen funktionieren
- ✅ Seed-Skripte reproduzierbar
- ✅ CI automatisiert (Lint, Tests, Migrations)
- ✅ OIDC vorbereitet (noch nicht aktiv)

---

***REMOVED******REMOVED*** 🔧 PHASE 1: SERVICE-KERNEL & API (2-6 Wochen)

**Ziel:** Domain-Grenzen schärfen, APIs produktiv, Metriken aktiv

***REMOVED******REMOVED******REMOVED*** **Sprint 3 (Woche 3-4):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **3.1 Service-Kernel** (5 Tage)
- [ ] Domain-Module strukturieren (`domains/inventory/`, `domains/crm/`, `domains/finance/`)
- [ ] Application-Layer (Use Cases) einführen
- [ ] Domain-Events definieren (noch ohne Bus)
- [ ] Event-Interface abstrahieren (`IEventPublisher`)

**Struktur:**
```
app/
  domains/
    inventory/
      application/  ***REMOVED*** Use Cases
      domain/       ***REMOVED*** Entities, Value Objects
      infrastructure/  ***REMOVED*** Repositories
      api/          ***REMOVED*** FastAPI Router
    crm/
      application/
      domain/
      infrastructure/
      api/
    finance/
      ...
```

**Deliverable:** ✅ Klare Domain-Boundaries (intern)

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **3.2 API-Vervollständigung** (5 Tage)
- [ ] **CRM-APIs:** `/api/v1/customers`, `/api/v1/leads`, `/api/v1/contacts`
- [ ] **Finance-APIs:** `/api/v1/accounts`, `/api/v1/journal-entries`
- [ ] **Inventory-APIs:** `/api/v1/warehouses`, `/api/v1/stock-movements`
- [ ] Response-Schemas konsolidieren (Pydantic v2)
- [ ] OpenAPI-Docs generieren (`/docs`)

**Deliverable:** ✅ Alle Kern-APIs produktiv (Postgres-backed)

**Akzeptanzkriterium:**
```python
***REMOVED*** Jede Domain hat:
✅ GET /api/v1/{domain} (List)
✅ GET /api/v1/{domain}/{id} (Detail)
✅ POST /api/v1/{domain} (Create)
✅ PUT /api/v1/{domain}/{id} (Update)
✅ DELETE /api/v1/{domain}/{id} (Delete)
```

---

***REMOVED******REMOVED******REMOVED*** **Sprint 4 (Woche 5-6):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **4.1 Observability Base** (4 Tage)
- [ ] Strukturiertes Logging (JSON, Correlation-IDs)
- [ ] Prometheus-Metrics (`/metrics` Endpoint)
- [ ] OpenTelemetry-Hooks (Tracing vorbereitet)
- [ ] Grafana-Dashboard (Basic: Requests, Latency, Errors)

**Deliverable:** ✅ Metrics & Logs produktiv

**Akzeptanzkriterium:**
```bash
curl http://localhost:8000/metrics
***REMOVED*** ✅ Prometheus-Format
***REMOVED*** http_requests_total{method="GET",endpoint="/api/v1/articles"}
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **4.2 Frontend API-Migration** (3 Tage)
- [ ] Dashboards auf Live-APIs umstellen
- [ ] Loading/Error-States konsistent
- [ ] TanStack Query Hooks für alle Domains
- [ ] Mock-Daten entfernen (schrittweise)

**Deliverable:** ✅ 50% der UIs nutzen Live-APIs

---

**Phase 1 Exit-Criteria:**
- ✅ Alle Kern-APIs produktiv (Postgres)
- ✅ Domain-Grenzen intern definiert
- ✅ Metrics aktiv (`/metrics`)
- ✅ 50% Frontend Live-API

---

***REMOVED******REMOVED*** 🔐 PHASE 2: SICHERHEITSLINIE & UX (6-10 Wochen)

**Ziel:** OIDC/RBAC produktiv, Frontend poliert, Tests automatisiert

***REMOVED******REMOVED******REMOVED*** **Sprint 5 (Woche 7-8):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **5.1 OIDC/RBAC Real** (6 Tage)
- [ ] Keycloak/Azure AD Integration
- [ ] JWT-Validation serverseitig
- [ ] RBAC-Middleware (Permission-Check)
- [ ] Role-Mapping (Admin, User, Viewer)
- [ ] Frontend: Auto-Token-Refresh

**Deliverable:** ✅ OIDC Live, Dev-Token deprecated

**Akzeptanzkriterium:**
```python
@router.get("/api/v1/customers")
async def list_customers(
    current_user: User = Depends(get_current_user),  ***REMOVED*** ✅ OIDC
    _: None = Depends(require_role("admin"))         ***REMOVED*** ✅ RBAC
):
    pass
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **5.2 Audit-Logging** (4 Tage)
- [ ] Audit-Service (PostgreSQL-backed)
- [ ] Event-basiertes Logging (Create, Update, Delete)
- [ ] Audit-Log-UI (Admin-Bereich)
- [ ] Retention-Policy (90 Tage Standard)

**Deliverable:** ✅ Revisionssichere Audit-Pipeline

---

***REMOVED******REMOVED******REMOVED*** **Sprint 6 (Woche 9-10):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **6.1 Frontend Productization** (5 Tage)
- [ ] Storybook in CI (Chromatic/GitHub Pages)
- [ ] Design Tokens finalisieren (Farben, Spacing, Typography)
- [ ] Alle UIs auf Live-APIs (100%)
- [ ] Error-Boundaries global
- [ ] Loading-Skeletons konsistent

**Deliverable:** ✅ Frontend produktionsreif

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **6.2 QA-Automatisierung** (5 Tage)
- [ ] E2E-Tests (Playwright): Login, Artikel-Suche, POS-Checkout
- [ ] API-Contract-Tests (Pact/OpenAPI-Validator)
- [ ] Coverage-Ziele (Backend: 80%, Frontend: 70%)
- [ ] Seed-/Fixture-Setup automatisiert

**Deliverable:** ✅ Automatisierte Test-Suite

**Akzeptanzkriterium:**
```bash
pytest --cov=app --cov-report=term  ***REMOVED*** ✅ 80%+
playwright test  ***REMOVED*** ✅ Alle grün
```

---

**Phase 2 Exit-Criteria:**
- ✅ OIDC/RBAC produktiv
- ✅ Audit-Logging aktiv
- ✅ Frontend 100% Live-API
- ✅ E2E-Tests automatisiert
- ✅ Coverage >75%

---

***REMOVED******REMOVED*** 🌐 PHASE 3: EVENTS & AGENTIK (10-16 Wochen)

**Ziel:** Event-Bus aktiv, LangGraph/RAG produktiv, Realtime-UX

***REMOVED******REMOVED******REMOVED*** **Sprint 7 (Woche 11-12):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **7.1 Domain Events** (6 Tage)
- [ ] Outbox-Pattern (PostgreSQL-Tabelle)
- [ ] Event-Publisher-Service
- [ ] Event-Consumer-Framework
- [ ] NATS/Redis-Streams-Anbindung
- [ ] First Event: `ArticleCreated`, `OrderPlaced`

**Deliverable:** ✅ Event-Bus aktiv

**Architektur:**
```python
***REMOVED*** Domain Event
@dataclass
class ArticleCreated:
    aggregate_id: str
    artikel_nr: str
    bezeichnung: str
    timestamp: datetime

***REMOVED*** Publisher
event_bus.publish(ArticleCreated(...))

***REMOVED*** Consumer
@event_bus.subscribe("ArticleCreated")
async def on_article_created(event: ArticleCreated):
    ***REMOVED*** Inventory-Sync, Audit-Log, etc.
    pass
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **7.2 Saga-Pattern** (4 Tage)
- [ ] Orchestration-Saga (z.B. Order → Delivery → Invoice)
- [ ] Compensation-Logic (Rollback)
- [ ] Saga-State-Machine (PostgreSQL)

**Deliverable:** ✅ Erste Saga produktiv (Order-to-Cash)

---

***REMOVED******REMOVED******REMOVED*** **Sprint 8 (Woche 13-14):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **8.1 LangGraph-Integration** (6 Tage)
- [ ] LangGraph-Server (FastAPI-basiert)
- [ ] Workflow: Bestellvorschlag-Agent
- [ ] Memory-Speicher (Redis)
- [ ] Tool-Binding (API-Calls aus Agent)
- [ ] Human-in-the-Loop (Approval-UI)

**Deliverable:** ✅ Erster Workflow-Agent live

**Workflow:**
```python
from langgraph.graph import StateGraph

***REMOVED*** Agent-Workflow: Bestellvorschlag
workflow = StateGraph()
workflow.add_node("analyze_stock", analyze_stock_levels)
workflow.add_node("check_history", check_sales_history)
workflow.add_node("generate_proposal", generate_order_proposal)
workflow.add_node("wait_approval", wait_for_human_approval)
workflow.add_node("create_order", create_purchase_order)

workflow.set_entry_point("analyze_stock")
workflow.add_edge("analyze_stock", "check_history")
workflow.add_edge("check_history", "generate_proposal")
workflow.add_edge("generate_proposal", "wait_approval")
workflow.add_conditional_edges("wait_approval", 
    lambda s: "create_order" if s.approved else END)
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **8.2 RAG-Layer** (4 Tage)
- [ ] Vector-DB (ChromaDB/Qdrant)
- [ ] Embedding-Service (OpenAI/Sentence-Transformers)
- [ ] Document-Indexer (Policies, Artikel, Kunden)
- [ ] Retrieval-API (`/api/rag/search`)

**Deliverable:** ✅ RAG-basierte Suche aktiv

---

***REMOVED******REMOVED******REMOVED*** **Sprint 9 (Woche 15-16):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **9.1 Realtime UX** (5 Tage)
- [ ] WebSocket für CustomerDisplay (POS)
- [ ] SSE für Policy-Updates
- [ ] SSE für Agent-Workflows (Progress)
- [ ] Frontend: useWebSocket Hook
- [ ] Reconnect-Logic

**Deliverable:** ✅ Echtzeit-Updates in 3 UIs

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **9.2 Approval/Audit-Flows** (5 Tage)
- [ ] Policy-Approval-UI (Admin)
- [ ] Agent-Decision-Review
- [ ] Audit-Trail für AI-Decisions
- [ ] Feedback-Loop (Mensch → Agent)

**Deliverable:** ✅ Governance für KI-Entscheidungen

---

**Phase 3 Exit-Criteria:**
- ✅ Event-Bus produktiv (min. 3 Event-Typen)
- ✅ LangGraph-Workflow live (min. 1)
- ✅ RAG-Suche funktioniert
- ✅ Realtime-Updates in POS + Dashboard
- ✅ Approval-Flows aktiv

---

***REMOVED******REMOVED*** 🏗️ PHASE 4: SKALIERUNG & COMPLIANCE (16-24 Wochen)

**Ziel:** Microservices, Full Observability, Compliance-Zertifizierung

***REMOVED******REMOVED******REMOVED*** **Sprint 10-11 (Woche 17-20):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **10.1 Microservice-Split** (8 Tage)
- [ ] **Finance-Service** ausgliedern (eigenes Repo)
- [ ] **Inventory-Service** ausgliedern
- [ ] API-Gateway (Kong/NGINX)
- [ ] Service-Mesh (Istio/Linkerd) optional
- [ ] CI/CD pro Service

**Deliverable:** ✅ 2 autonome Microservices

**Architektur:**
```
┌────────────────┐
│  API-Gateway   │
└────────┬───────┘
         │
    ┌────┴────┬──────────┬────────────┐
    │         │          │            │
┌───▼───┐ ┌──▼──┐ ┌─────▼────┐ ┌────▼─────┐
│Finance│ │Inven│ │   CRM    │ │  Policy  │
│Service│ │tory │ │ Service  │ │  Engine  │
└───┬───┘ └──┬──┘ └─────┬────┘ └────┬─────┘
    │        │          │            │
    └────────┴──────────┴────────────┘
              Event-Bus (NATS)
```

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **10.2 Observability Advanced** (6 Tage)
- [ ] Distributed Tracing (Jaeger/Tempo)
- [ ] Grafana Loki (Log-Aggregation)
- [ ] Alerting (Prometheus Alertmanager)
- [ ] SLO-Definition (99.5% Uptime, <200ms Latency)
- [ ] On-Call-Rotation (PagerDuty)

**Deliverable:** ✅ Full Observability Stack

---

***REMOVED******REMOVED******REMOVED*** **Sprint 12 (Woche 21-24):**

***REMOVED******REMOVED******REMOVED******REMOVED*** **12.1 Compliance** (10 Tage)
- [ ] DSGVO-Audit (Datenschutz-Folgenabschätzung)
- [ ] GxP-Compliance (pharmazeutische Kunden)
- [ ] KassenSichV-Zertifizierung (fiskaly Live)
- [ ] SOC 2 Vorbereitung
- [ ] Pen-Test (externer Dienstleister)

**Deliverable:** ✅ Compliance-Zertifizierungen

---

***REMOVED******REMOVED******REMOVED******REMOVED*** **12.2 Security-Härtung** (5 Tage)
- [ ] Secrets Management (Vault/AWS Secrets Manager)
- [ ] WAF (Web Application Firewall)
- [ ] Rate-Limiting (pro User)
- [ ] CSRF-Protection
- [ ] Security-Headers (HSTS, CSP)

**Deliverable:** ✅ Security-Hardening komplett

---

**Phase 4 Exit-Criteria:**
- ✅ 2+ Microservices live
- ✅ Distributed Tracing aktiv
- ✅ Alerting konfiguriert
- ✅ DSGVO-Audit bestanden
- ✅ Pen-Test ohne kritische Findings

---

***REMOVED******REMOVED*** 📊 RESSOURCENBEDARF

***REMOVED******REMOVED******REMOVED*** **Team-Größe (empfohlen):**

| Phase | Backend | Frontend | DevOps | QA | Gesamt |
|-------|---------|----------|--------|-----|--------|
| **Phase 0** | 1 | 0.5 | 0.5 | 0 | 2 FTE |
| **Phase 1** | 2 | 1 | 0.5 | 0.5 | 4 FTE |
| **Phase 2** | 1.5 | 1.5 | 0.5 | 1 | 4.5 FTE |
| **Phase 3** | 2 | 1 | 1 | 1 | 5 FTE |
| **Phase 4** | 1.5 | 0.5 | 1.5 | 1.5 | 5 FTE |

**Total:** 4-5 FTE über 6 Monate

---

***REMOVED******REMOVED******REMOVED*** **Budget-Kalkulation:**

| Kategorie | Kosten/Monat | 6 Monate | 9 Monate |
|-----------|--------------|----------|----------|
| **Personal** (4 FTE × 8k€) | 32.000 € | 192.000 € | 288.000 € |
| **Infrastruktur** (Cloud) | 2.000 € | 12.000 € | 18.000 € |
| **Tools** (Licenses) | 1.000 € | 6.000 € | 9.000 € |
| **Externe** (Pen-Test, Audit) | - | 10.000 € | 15.000 € |
| **GESAMT** | **35.000 €** | **220.000 €** | **330.000 €** |

---

***REMOVED******REMOVED*** ⚠️ RISIKO-ANALYSE

***REMOVED******REMOVED******REMOVED*** **High-Risk:**

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **Microservice-Migration** zu früh | Mittel | Hoch | Service-Kernel zuerst (Phase 1) |
| **Event-Bus** Komplexität | Hoch | Mittel | Start mit internem Bus, später NATS |
| **LangGraph** unreif | Mittel | Mittel | Pilot in isoliertem Workflow |
| **Team-Fluktuation** | Niedrig | Hoch | Dokumentation & Pair-Programming |

***REMOVED******REMOVED******REMOVED*** **Medium-Risk:**

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| **OIDC-Provider** Ausfall | Niedrig | Mittel | Fallback auf Dev-Token |
| **PostgreSQL** Performance | Mittel | Mittel | Indexing & Query-Optimierung |
| **Frontend-Komplexität** | Mittel | Niedrig | Storybook & Design-System |

---

***REMOVED******REMOVED*** 📋 DELIVERABLES PRO PHASE

***REMOVED******REMOVED******REMOVED*** **Phase 0:**
- ✅ Alembic-Migrationen harmonisiert
- ✅ Seed-Skripte automatisiert
- ✅ CI-Pipeline aktiv (Lint, Tests, Migrations)
- ✅ OIDC vorbereitet

***REMOVED******REMOVED******REMOVED*** **Phase 1:**
- ✅ Domain-Module strukturiert
- ✅ Alle Kern-APIs produktiv (Postgres)
- ✅ Prometheus-Metrics aktiv
- ✅ 50% Frontend Live-API

***REMOVED******REMOVED******REMOVED*** **Phase 2:**
- ✅ OIDC/RBAC produktiv
- ✅ Audit-Logging revisionssicher
- ✅ Frontend 100% Live-API
- ✅ E2E-Tests automatisiert
- ✅ Storybook in CI

***REMOVED******REMOVED******REMOVED*** **Phase 3:**
- ✅ Event-Bus produktiv (min. 3 Events)
- ✅ LangGraph-Workflow live (min. 1)
- ✅ RAG-Suche aktiv
- ✅ Realtime-Updates (WebSocket/SSE)
- ✅ Approval/Audit-Flows

***REMOVED******REMOVED******REMOVED*** **Phase 4:**
- ✅ 2+ Microservices ausgegliedert
- ✅ Distributed Tracing
- ✅ Alerting konfiguriert
- ✅ DSGVO/GxP-Audit bestanden
- ✅ Pen-Test ohne kritische Findings

---

***REMOVED******REMOVED*** 🎯 MEILENSTEINE & GATES

***REMOVED******REMOVED******REMOVED*** **M0 (Woche 2):** Foundation Ready
- ✅ DB stabil, CI aktiv, OIDC vorbereitet
- **Gate:** Alle Migrationen funktionieren

***REMOVED******REMOVED******REMOVED*** **M1 (Woche 6):** API Complete
- ✅ Alle Kern-APIs produktiv, Metrics aktiv
- **Gate:** OpenAPI-Docs vollständig, 50% Frontend Live

***REMOVED******REMOVED******REMOVED*** **M2 (Woche 10):** Security & UX
- ✅ OIDC live, Frontend poliert, Tests automatisiert
- **Gate:** E2E-Tests grün, Coverage >75%

***REMOVED******REMOVED******REMOVED*** **M3 (Woche 16):** Events & AI
- ✅ Event-Bus produktiv, LangGraph live, RAG aktiv
- **Gate:** Min. 1 Agent-Workflow produktiv

***REMOVED******REMOVED******REMOVED*** **M4 (Woche 24):** Production-Ready
- ✅ Microservices live, Compliance zertifiziert
- **Gate:** Pen-Test bestanden, DSGVO-Audit OK

---

***REMOVED******REMOVED*** 🔗 ABHÄNGIGKEITEN

```
Phase 0 (DB/Seeds/CI)
   ↓
Phase 1 (Service-Kernel + API)
   ↓
Phase 2 (OIDC/RBAC + UX)
   ↓
Phase 3 (Events + Agentik)
   ↓
Phase 4 (Microservices + Compliance)
```

**Kritische Pfade:**
- **DB-Migrationen** müssen vor API-Entwicklung funktionieren
- **Service-Kernel** muss vor Event-Bus existieren
- **OIDC/RBAC** muss vor Agentik (wegen Approval) aktiv sein
- **Events** müssen vor Microservice-Split funktionieren

---

***REMOVED******REMOVED*** 📊 SUCCESS-METRIKEN

***REMOVED******REMOVED******REMOVED*** **Phase 0:**
- ✅ Migrationen: 0 Fehler
- ✅ Seeds: <5 Min Laufzeit
- ✅ CI: <10 Min Build-Zeit

***REMOVED******REMOVED******REMOVED*** **Phase 1:**
- ✅ API-Coverage: 100% Kern-Domains
- ✅ API-Latency: <200ms (P95)
- ✅ Frontend Live: 50%

***REMOVED******REMOVED******REMOVED*** **Phase 2:**
- ✅ Auth-Success-Rate: 99.9%
- ✅ E2E-Tests: 100% grün
- ✅ Frontend Live: 100%

***REMOVED******REMOVED******REMOVED*** **Phase 3:**
- ✅ Event-Throughput: >1000/sec
- ✅ Agent-Accuracy: >90%
- ✅ RAG-Latency: <500ms

***REMOVED******REMOVED******REMOVED*** **Phase 4:**
- ✅ Service-Uptime: 99.5%
- ✅ Incident-Response: <15 Min
- ✅ Compliance: Alle Audits bestanden

---

***REMOVED******REMOVED*** 🛠️ TECH-STACK PRO PHASE

***REMOVED******REMOVED******REMOVED*** **Phase 0-1:**
- FastAPI (Monolith)
- PostgreSQL (SQLAlchemy)
- Alembic (Migrationen)
- GitHub Actions (CI)

***REMOVED******REMOVED******REMOVED*** **Phase 2:**
- Keycloak/Azure AD (OIDC)
- Playwright (E2E)
- Storybook (UI)
- Chromatic (Visual Tests)

***REMOVED******REMOVED******REMOVED*** **Phase 3:**
- NATS/Redis Streams (Event-Bus)
- LangGraph (Workflows)
- ChromaDB/Qdrant (Vector-DB)
- OpenAI (Embeddings)

***REMOVED******REMOVED******REMOVED*** **Phase 4:**
- Kubernetes (Orchestrierung)
- Istio/Linkerd (Service-Mesh)
- Jaeger/Tempo (Tracing)
- Vault (Secrets)

---

***REMOVED******REMOVED*** 📅 TIMELINE-VISUALISIERUNG

```
Monat 1  │ Phase 0 ████████│ Phase 1 ████░░░░░░░░░░│
Monat 2  │                 │ Phase 1 ████████████████│
Monat 3  │ Phase 2 ████████████████│
Monat 4  │ Phase 2 ████░░░░│ Phase 3 ████████░░░░░░░│
Monat 5  │                 │ Phase 3 ████████████████│
Monat 6  │ Phase 4 ████████████████│
Monat 7  │ Phase 4 ████████████████│ (Buffer)
Monat 8  │ Phase 4 ████████│ (Buffer)
Monat 9  │ Finalisierung ████│ Go-Live Vorbereitung ████│

Legende:
████ = Aktive Entwicklung
░░░░ = Planung/Vorbereitung
```

---

***REMOVED******REMOVED*** ✅ CURRENT STATUS (Stand: 2025-10-11)

***REMOVED******REMOVED******REMOVED*** **Phase 0: Grundlage**
- ✅ **DB-Migrationen:** Basis vorhanden (harmonisieren nötig)
- ✅ **Seeds:** Teilweise vorhanden
- ✅ **CI:** GitHub Actions vorhanden (aktivieren nötig)
- ⚠️ **OIDC:** Nur Stubs

**Fortschritt:** ~40% (2-3 Tage bis fertig)

***REMOVED******REMOVED******REMOVED*** **Phase 1: Service-Kernel**
- ✅ **DI-Container:** Funktioniert
- ✅ **PostgreSQL:** Durchgängig
- ⚠️ **Domain-Module:** Noch nicht strukturiert
- ⚠️ **Metrics:** Noch nicht aktiv

**Fortschritt:** ~30% (6-8 Tage bis fertig)

***REMOVED******REMOVED******REMOVED*** **Phase 2-4:**
- ⚠️ Noch nicht gestartet

---

***REMOVED******REMOVED*** 🎯 QUICK-START: NÄCHSTE 2 WOCHEN

***REMOVED******REMOVED******REMOVED*** **Woche 1 (Phase 0 abschließen):**
- [ ] Alembic-Migrationen harmonisieren (2 Tage)
- [ ] Seed-Skripte vervollständigen (2 Tage)
- [ ] GitHub Actions aktivieren (1 Tag)

***REMOVED******REMOVED******REMOVED*** **Woche 2 (Phase 1 starten):**
- [ ] Domain-Module strukturieren (3 Tage)
- [ ] API-Vervollständigung starten (2 Tage)

**Ziel:** Phase 0 komplett, Phase 1 zu 50%

---

***REMOVED******REMOVED*** 📖 DOKUMENTATIONS-ANFORDERUNGEN

***REMOVED******REMOVED******REMOVED*** **Pro Phase:**
- ✅ Architecture Decision Records (ADRs)
- ✅ API-Dokumentation (OpenAPI)
- ✅ Deployment-Guides
- ✅ Runbooks (Operations)

***REMOVED******REMOVED******REMOVED*** **Pro Sprint:**
- ✅ Sprint-Planning-Protokoll
- ✅ Definition-of-Done
- ✅ Retrospektive
- ✅ Demo (Stakeholder)

---

***REMOVED******REMOVED*** 🚀 GO-LIVE-STRATEGIE

***REMOVED******REMOVED******REMOVED*** **Soft-Launch (Ende Monat 6):**
- ✅ Phase 1-3 komplett
- ✅ Ausgewählte Kunden (Beta)
- ✅ Monitoring 24/7
- ✅ Support-Team bereit

***REMOVED******REMOVED******REMOVED*** **Full-Launch (Ende Monat 9):**
- ✅ Phase 4 komplett
- ✅ Alle Compliance-Zertifizierungen
- ✅ Marketing & Sales ready
- ✅ SLA-Garantien

---

***REMOVED******REMOVED*** 🏆 FINALE ZUSAMMENFASSUNG

**Roadmap:** 6-9 Monate, 5 Phasen, 12 Sprints  
**Budget:** 220k-330k €  
**Team:** 4-5 FTE  
**Risiko:** Mittel (mit Mitigation-Plan)

**Critical Success Factors:**
1. ✅ Service-Kernel vor Microservices
2. ✅ OIDC/RBAC vor Agentik
3. ✅ Event-Bus vor Microservice-Split
4. ✅ Tests vor Go-Live

**Status Heute:** Phase 0 ~40%, Phase 1 ~30%

**Next:** Phase 0 abschließen (2-3 Tage)

---

**Erstellt:** 2025-10-11 21:30 Uhr  
**Version:** 1.0  
**Owner:** VALERO NeuroERP Team  
**Review:** Quarterly
