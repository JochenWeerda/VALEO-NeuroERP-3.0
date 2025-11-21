# Produkt- & Sprintplanung: a.eins-Parität

## Vision & Ziele

- **Kurzfristig**: Compliance- und Infrastruktur-Lücken schließen (InfraStat, Zoll, Workflow-Core, RAG-Basis).
- **Mittelfristig**: Funktionsparität in Fertigung, Service, Beschaffung herstellen.
- **Langfristig**: Differenzierende KI-Erlebnisse und Automatisierungen ausbauen.

## Agenten-Teamstruktur

| Agent | Fokus | Hauptaufgaben | Schnittstellen |
|-------|-------|---------------|----------------|
| **Orchestrator-Agent** | Programm- & Stakeholder-Management | Roadmap-Pflege, Priorisierung, Sprintreviews leiten, KPI-Tracking | C-Level, Product Owners |
| **Workflow-Agent** | Workflow-Engine & Prozessautomatisierung | Umsetzung `backend/workflow/` Kernservices, Policy-as-Code, Eventing | Domain Squads, DevOps |
| **RAG-Agent** | Wissensinfrastruktur & Kontextbereitstellung | Aufbau `services/rag-gateway`, Embedding-Pipeline, IDE-Integration | Developer Experience, Compliance |
| **Compliance-Agent** | Regulatorik & Meldesysteme | InfraStat-Automation, Zollprozesse, Auditvorbereitung | Legal, Finance |
| **Supply-Chain-Agent** | Procure-to-Pay & Lager | Mehrlager, Lieferanten-Scorecards, Qualitätsfeedback | Workflow-Agent, Analytics |
| **Service-Agent** | Service-to-Customer | SLA-Automatisierung, Einsatzplanung, AR-Support | Workflow-Agent, RAG-Agent |
| **Analytics-Agent** | KI & Reporting | Forecasting, KPI-Dashboards, Modell-Monitoring | alle Agenten |

> Jeder Agent umfasst ein cross-funktionales Squad (Dev, QA, Domain SME) und arbeitet teilautonom nach festgelegten Guardrails.

## Programm-Inkremente

1. **PI-1 "Compliance Foundation" (6 Wochen)**
   - Deliverables: InfraStat-MVP, Zoll-Screening, Workflow-Core (Phase 1), RAG-Ingestion-MVP.
   - Agenten: Compliance, Workflow, RAG, Orchestrator.
2. **PI-2 "Operational Parity" (8 Wochen)**
   - Deliverables: Fertigungsleitstand, Supplier Portal, Service SLA-Automation, RAG-IDE-Assistenz.
   - Agenten: Supply-Chain, Service, Workflow, Analytics.
3. **PI-3 "Intelligence Expansion" (8 Wochen)**
   - Deliverables: KI-Forecasts, Predictive Maintenance, Closed-Loop Feedback, Gamifizierte Dashboards.
   - Agenten: Analytics, Service, Supply-Chain, Orchestrator.

## Sprint Cadence (2 Wochen)

| Sprint | Schwerpunkt | Hauptstories | Definition of Done |
|--------|-------------|--------------|--------------------|
| SP-1 | Compliance-Basis | InfraStat-Datenmodell, Workflow-Core Skeleton | Tests, Docs, Monitoring |
| SP-2 | Meldeläufe & Eventing | Automatisierte Meldung, Event-Sagas, RAG-Ingestion CLI | End-to-End-Testlauf |
| SP-3 | Workflow-Policies | Policy-as-Code, Mandantenkonfiguration | Abnahme durch Compliance-Agent |
| SP-4 | RAG-Runtime | RAG-Gateway API, IDE Plugin Alpha | Feedback von Dev-Teams |
| SP-5+ | Domain-Spezifika | Fertigung, Service, Lieferantenportal | KPI-Abdeckung, UAT bestanden |

## Backlog-Struktur

- **Epic E1 – Workflow Core** (`backend/workflow/`)
  - Story W1: Event Schema Standardisierung
  - Story W2: Saga-Orchestrator & Kompensationen
  - Story W3: Policy-as-Code Engine
- **Epic E2 – Compliance Automation** (`services/compliance/`)
  - Story C1: InfraStat ETL & Validierung
  - Story C2: Zolltarif-Service mit Sanktionslisten-Check
  - Story C3: Audit-Trail Dashboard
- **Epic E3 – RAG Enablement** (`services/rag-gateway/`, `tools/rag-sync`)
  - Story R1: Ingestion Pipeline
  - Story R2: Vector Store Integration
  - Story R3: Retrieval API & Access Control
- **Epic E4 – Domain Enhancements**
  - Story D1: Fertigungsleitstand MVP
  - Story D2: Service SLA Automation
  - Story D3: Supplier Scorecards

## Governance & Rituale

- **Weekly Sync**: Agenten führen Fortschrittsberichte (KPIs, Blocker) in `docs/roadmap/status/` fort.
- **PI Planning**: Remote-Workshop mit allen Agenten, Abgleich Abhängigkeiten.
- **Design Authority Board**: Prüft Einhaltung der Design Guidelines und KI-Governance.
- **Retro & Learning Loop**: Jede vierte Woche; Erkenntnisse wandern in `knowledge-base/`.

## Risiken & Mitigation

- **Regulatorische Deadline** → Frühe Abstimmung mit Behörden, Puffer in SP-2.
- **KI-Bias & Explainability** → Testharness, Monitoring, Compliance-Agent sign-off.
- **Ressourcenknappheit** → Cross-Training, Agenten können Stories übernehmen (Swarming).
- **Technische Schulden** → Technischer Budget-Track pro Sprint, Priorisierung über Orchestrator-Agent.

## KPIs

- Time-to-Compliance (InfraStat, Zoll).
- Workflow-Durchsatz & Fehlerrate.
- RAG-Nutzung & Relevanzscore.
- Sprint Predictability (Commit vs. Done).
- Stakeholder-Zufriedenheit (NPS).

