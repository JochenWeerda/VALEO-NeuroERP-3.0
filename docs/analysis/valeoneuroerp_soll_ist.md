# VALEO-NeuroERP 3.0 Soll-/Ist-Analyse

## 1. Projektkontext
- Zielsetzung: Aufbau eines NeuroERP, das Prozesse validiert, lernt und Anwender kognitiv entlastet (Benennung VALEO).[README.md:1]
- Analyseumfang: Architektur, Technologie-Stack, UX/UI, KI-Integration und Betriebsfaehigkeit des Repos `VALEO-NeuroERP-3.0` (Branch `develop`).
- Methode: Abgleich dokumentierter Zielbilder mit implementiertem Code und Assets, Ableitung von Abweichungen und Handlungsempfehlungen.

## 2. Soll-Bild (Anspruch)

### 2.1 Zielarchitektur
- Modularisierte MSOA-/DDD-Landschaft mit 19 entkoppelten Domains, BFF-Schicht und asynchronem Event-Bus ueber NATS/Kafka.[`VALEO-NEUROERP-DOMAIN-OVERVIEW.md:13`]
- Polyglotte Persistenz pro Domain, REST/gRPC-APIs, Outbox/Saga-Muster fuer Integrationen.[`valeo_neuro_erp_architekturdiagramm_msoa_agentik.jsx:224`]
- Agentische Ebene (LangGraph/MCP) ueber domainspezifische Services, orchestriert ueber Ereignisse.[`valeo_neuro_erp_architekturdiagramm_msoa_agentik.jsx:143`]

### 2.2 Technologische Leitplanken
- Frontend: React 18, TypeScript, Vite, Storybook, Tailwind als Design-System-Basis.[`README.md:23`]
- Backend: FastAPI, PostgreSQL, Redis, Eventing (Kafka/NATS), Observability (Prometheus/Grafana), OIDC fuer Authentifizierung und Autorisierung.[`README.md:23` `README.md:160`]
- CI/CD: Docker/Kubernetes-Deployments, GitHub Actions, automatisierte Tests und Sicherheitsscans (z. B. SAST/DAST).[`README.md:5`]

### 2.3 UX/UI Vision
- Multimodale Bedienung (Maus, Touch, Sprache), automation-first Workflows, KI-Assistenz (MCP) innerhalb eines konsistenten Design-Systems.[`UI-UX-MCP-INTEGRATION-ROADMAP.md:9`]
- Storybook-basierte Komponentenbibliothek als Single Source of Truth, Accessibility als Baseline.[`UI-UX-MCP-INTEGRATION-ROADMAP.md:16`]

### 2.4 Systemphilosophie und Leitbild
- Selbstvalidierend, auditierbar, erklaerbar, lernfaehig: Entscheidungslogik ueber Policies/Agenten, Audit-Trails und Feedback-Schleifen.[`VALEO-NEUROERP-DOMAIN-OVERVIEW.md:132`]
- Leitbild: "VALEO" = Validate, Analyze, Learn, Engineer/Evolve, Optimize - kontinuierliche Optimierung von Prozessen, UX und Wirtschaftlichkeit.[README.md:1]

**Leitbild des Zielsystems:** Ein entkoppeltes, ereignisgetriebenes NeuroERP, in dem Domains, KI-Agenten und BFFs kooperieren, um geschaeftskritische Entscheidungen autonom vorzubereiten, regulatorisch konform umzusetzen und fuer Menschen nachvollziehbar zu halten.

## 3. Ist-Stand (Repository-Analyse)

### 3.1 Architektur und Backend
- FastAPI-Monolith mit gemeinsamem Startpunkt (`main.py`), keine getrennten Microservices oder Eventbus-Anbindung sichtbar.[`main.py:10`]
- Dependency-Injection-Konfiguration bricht, weil zentrale Repository-Implementierungen nicht importiert werden (`TenantRepositoryImpl` etc.).[`app/core/container_config.py:16` `app/core/container_config.py:58`]
- Persistenz uneinheitlich: Mischung aus SQLAlchemy-Interfaces und direkten SQLite-Dateizugriffen (`valeo_neuro_erp.db`).[`app/api/v1/endpoints/articles.py:6` `app/api/v1/endpoints/articles.py:15`]
- Alembic-Migration definiert andere Schemas als ORM-Modelle (z. B. `tenants` vs. `shared_tenants`), Gefahr divergenter Datenmodelle.[`alembic/versions/001_initial_schema.py:24` `app/infrastructure/models/__init__.py:17`]

### 3.2 Module und Domains
- Zahlreiche Domain-Pakete unter `/domains` und `/packages/*-domain`, jedoch ueberwiegend in-memory oder kommentierte Exporte ohne Infrastruktur-Anbindung.[`packages/inventory-domain/src/index.ts:4`]
- API-Schichten nutzen generische Repository-Schnittstellen, aber produktive Services liefern Mock-Daten und umgehen Persistenz (z. B. CustomerService).[`app/core/production_service_implementations.py:30` `app/core/production_service_implementations.py:182`]

### 3.3 KI-Integration
- MCP/LangGraph lediglich als Skript- und Dokumentationsartefakte vorhanden; keine produktive Backend-Anbindung oder RAG/Memory-Bindings nachweisbar.[`scripts/create_langgraph_integration.py:42`]
- Frontend-MCP-Client ruft `/api/mcp/...` auf, waehrend Backend-Router unter `/mcp/policy` registriert ist - Requests laufen ins Leere.[`packages/frontend-web/src/lib/mcp.ts:16` `app/api/v1/api.py:85` `app/api/v1/endpoints/policies.py:21`]
- SSE-Client erwartet `/api/events?stream=mcp`, Backend bietet `/api/stream/{channel}` - Echtzeitpfad inkonsistent.[`packages/frontend-web/src/lib/sse-client.ts:62` `app/routers/sse_router.py:9`]

### 3.4 Frontend und UX
- Umfangreiche Page-Struktur, aber ueberwiegend Hardcoded-Daten (Dashboards, POS-Suche) und fehlende API-Kopplung.[`packages/frontend-web/src/pages/dashboard/sales-dashboard.tsx:6` `packages/frontend-web/src/components/pos/ArticleSearch.tsx:23`]
- Storybook, Design Tokens, Accessibility-Roadmap dokumentiert, jedoch keine belegten automatisierten Tests oder Coverage im Repo.

### 3.5 Qualitaet und Betriebsfaehigkeit
- Tests: Vereinzelte Playwright-Contracttests greifen auf OpenAPI-Endpoints zu, setzen funktionierendes Backend voraus - derzeit nicht erfuellbar.[`contract-tests/openapi-validator.spec.ts:6`]
- Sicherheit: OIDC-Konfiguration existiert nur als Client-Shell, keine Policy-Enforcement oder Tokenvalidierung serverseitig.[`app/core/config.py:44` `app/core/production_service_implementations.py:135`]
- Observability und Deployment: Docker/K8s-Artefakte und Monitoring-Skripte vorhanden, aber keine Integration in laufenden Code (keine Prometheus-Instrumentierung in Services).

## 4. Soll-/Ist-Vergleich

| Bereich | Soll (Anspruch) | Ist (aktuell) | Abweichung / Kommentar |
|---------|-----------------|---------------|------------------------|
| Architektur | MSOA/DDD mit BFF, Eventbus, autonome Domains.[`VALEO-NEUROERP-DOMAIN-OVERVIEW.md:13`] | FastAPI-Monolith ohne Serviceabtrennung, Eventbus fehlt.[`main.py:10`] | Hoher Gap: Zielarchitektur nicht umgesetzt. |
| Backend (Domains, Events) | Persistente Domain-Services mit Events, Polyglotte DB.[`valeo_neuro_erp_architekturdiagramm_msoa_agentik.jsx:224`] | Mischung aus Platzhalter-Services, SQLite-Zugriff, divergente Schemata.[`app/api/v1/endpoints/articles.py:15`] | Kritische Inkonsistenz zwischen Claim und Implementierung. |
| Frontend / UI-UX | Multimodal, datengetriebene Workflows, Storybook-led UX.[`UI-UX-MCP-INTEGRATION-ROADMAP.md:16`] | Statische Mock-Dashboards, keine Storybook-Artefakte im Build, keine Sprach/Touch-Interaktionen.[`packages/frontend-web/src/components/pos/ArticleSearch.tsx:23`] | UX-Vision nur dokumentiert. |
| KI-Integration (LangGraph, MCP, RAG) | Agentische Layer als Co-Piloten, Echtzeit-SSE, RAG-Anbindung.[`valeo_neuro_erp_architekturdiagramm_msoa_agentik.jsx:143`] | Scripts und Clients ohne lauffaehigen Server-Endpunkt; Pfade inkonsistent.[`packages/frontend-web/src/lib/mcp.ts:16`] | KI-Funktionalitaet faktisch nicht verfuegbar. |
| Datenmodell / API | PostgreSQL + Drizzle/SQLAlchemy, OpenAPI-konforme Services.[`README.md:23`] | Mischung aus SQLite-File, unvollstaendigen Repos, OpenAPI-Tests scheitern an Luecken.[`app/core/container_config.py:58`] | Datenhaltung nicht konform zum Zielbild. |
| Prozessintelligenz / Agentik | Policy-/Agenten-Engine mit Auto-Execute und Audit.[`VALEO-NEUROERP-DOMAIN-OVERVIEW.md:132`] | Policy Engine existiert lokal (SQLite), aber ohne Governance/Audit-Flows oder MCP-Einbindung.[`app/services/policy_service.py:24`] | Ansaetze vorhanden, jedoch isoliert. |
| Sicherheit / Datenschutz | OIDC, RBAC/ABAC, Audit Logging auf Events.[`README.md:5`] | Auth-Service nur clientseitig, Backend-Endpunkte ohne Token-Pruefung, Audit-Services Platzhalter.[`app/core/production_service_implementations.py:135`] | Compliance-Risiko: Security nur dokumentiert. |
| Dokumentation / CI/CD | GitHub Actions, Deployment-Guides, laufende Pipelines.[`README.md:5`] | Umfangreiche Dokumente vorhanden, aber keine Evidenz fuer funktionsfaehige Pipelines im Code (Tests nicht konfigurierbar).[`contract-tests/openapi-validator.spec.ts:6`] | Dokumentation ueberholt Implementierung. |

## 5. Schlussfolgerungen und Empfehlungen

### 5.1 Kritische Luecken
- Fehlende Serviceabtrennung und defekte DI-Konfiguration verhindern produktive Backend-Funktion.[`app/core/container_config.py:16`]
- Datenpersistenz uneinheitlich; SQLite-Bypass widerspricht Multi-Tenant/Postgres-Ziel.[`app/api/v1/endpoints/articles.py:15`]
- MCP-/LangGraph-Versprechen ohne funktionsfaehige Schnittstellen, damit kein KI-Mehrwert.[`packages/frontend-web/src/lib/mcp.ts:16`]
- Sicherheits- und Compliance-Anforderungen nicht erfuellt (kein serverseitiger OIDC-Abgleich, keine Audit-Pipeline).[`app/core/production_service_implementations.py:135`]

### 5.2 Quick Wins
- Reparatur der DI-Registrierungen, Import der Repository-Implementierungen und Konfiguration eines konsistenten PostgreSQL-Zugriffs.
- Vereinheitlichung der API-Pfade (`/api/mcp` und `/mcp/policy`) und Einfuehrung eines Gateways fuer MCP-Actions.
- Einfuehrung realistischer Seed-Daten und API-Adapter im Frontend, um Mock-Dashboards schrittweise an echte Endpunkte zu koppeln.
- Aktivierung von Auth-Middleware in FastAPI (z. B. OAuth2/JWT-Pruefung) auf kritischen Routen.

### 5.3 Strategische Massnahmen
- Architektur-Refactor: Priorisierte Domains in klar abgegrenzte Module trennen (zunaechst innerhalb des Monolithen), Events ueber Message-Bus einfuehren.
- Aufbau eines gemeinsamen Policy-/Agent-Backends, das PolicyStore, RAG-Speicher und LangGraph orchestriert; Definition einheitlicher Contracts.
- Implementierung eines konsistenten Data-Access-Layers (SQLAlchemy + Alembic) mit Migrationen, Tests und Eliminierung aller SQLite-Pfade.
- UX-Initiative: Storybook in CI etablieren, Design Tokens verankern, User Flows mit echten Daten aufbauen, Vorbereitung fuer Touch/Voice-Eingaenge.
- Security und Compliance: Zentraler AuthZ-Layer, Audit Logging pro Domain, DSGVO/GxP-Kontrollen operationalisieren.

### 5.4 Priorisierte Roadmap
- Phase 1 (0-4 Wochen): Backend-DI fixen, Postgres-Anbindung finalisieren, REST-Endpunkte (CRM, Inventory, Policy) lauffaehig machen, Frontend auf echte APIs umstellen, Auth-Guards aktivieren.
- Phase 2 (1-3 Monate): Events und Domain-Boundaries schaerfen, MCP-Gateway mit Policy Engine verbinden, Storybook und UX-Guidelines produktiv, Observability-Stack einbinden, erste automatisierte Tests.
- Phase 3 (3-6 Monate): LangGraph/RAG-Integration produktiv, Agenten-Orchestrierung mit Feedback-Schleifen, Microservice-Ausgliederung (z. B. Finance, Inventory), Compliance- und Security-Haertung.

---

**Refactoring-Idee (optional):** Ein Service-Kernel innerhalb des Monolithen etabliert klare Domain-Interfaces, abstrahiert Events via internes Publish/Subscribe und schafft damit einen evolutionaeren Pfad zur echten MSOA ohne Big-Bang-Migration.
