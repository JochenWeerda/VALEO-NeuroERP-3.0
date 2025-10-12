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
- FastAPI-Monolith mit gemeinsamem Startpunkt (`main.py`); Serviceabtrennung und Eventbus fehlen weiterhin.[`main.py:10`]
- Dependency-Injection nutzt jetzt konkrete Repository-Implementierungen und Session-Factories; Container wird erfolgreich initialisiert.[`app/core/container_config.py:16` `app/core/container_config.py:58`]
- Persistenz vereinheitlicht: Artikel-, Lager- und Finanz-Endpunkte greifen via SQLAlchemy auf PostgreSQL zu; SQLite-Pfade im API-Layer wurden entfernt.[`app/api/v1/endpoints/articles.py:1` `app/api/v1/endpoints/warehouses.py:1` `app/api/v1/endpoints/chart_of_accounts.py:1`]
- Alembic-Schema muss um neue `policy_rules`-Tabelle ergänzt werden, damit Migrationen den aktuellen Datenstand widerspiegeln.[`app/infrastructure/models/__init__.py:152`]

### 3.2 Module und Domains
- Zahlreiche Domain-Pakete unter `/domains` und `/packages/*-domain`, jedoch ueberwiegend in-memory oder kommentierte Exporte ohne Infrastruktur-Anbindung.[`packages/inventory-domain/src/index.ts:4`]
- API-Schichten nutzen generische Repository-Schnittstellen, aber produktive Services liefern Mock-Daten und umgehen Persistenz (z. B. CustomerService).[`app/core/production_service_implementations.py:30` `app/core/production_service_implementations.py:182`]

### 3.3 KI-Integration
- Policy-Engine persistiert jetzt in PostgreSQL; MCP-Routen liegen konsistent unter `/api/mcp/policy`, SSE-Endpunkte unterstützen sowohl `/api/stream/{channel}` als auch `/api/events`.[`app/api/v1/endpoints/policies.py:21` `app/routers/sse_router.py:1`]
- Frontend-MCP-Client adressiert weiterhin `/api/mcp`; koordinierte Authentifizierung und echte Agenten-Workflows (LangGraph, RAG) fehlen nach wie vor.[`packages/frontend-web/src/lib/mcp.ts:16` `scripts/create_langgraph_integration.py:42`]

### 3.4 Frontend und UX
- Die POS-Artikel-Suche nutzt nun die Live-API (`/api/v1/articles`) inklusive Fehler- und Ladezuständen; viele übrige Seiten bleiben jedoch mit Mock-Daten hinterlegt.[`packages/frontend-web/src/components/pos/ArticleSearch.tsx:1` `packages/frontend-web/src/pages/dashboard/sales-dashboard.tsx:6`]
- Storybook-/Design-Dokumentation existiert weiterhin; automatisierte UI-Tests oder Coverage-Berichte wurden nicht ergänzt.

### 3.5 Qualitaet und Betriebsfaehigkeit
- Tests: Zusätzlich zu den vorhandenen Playwright-Skripten existieren jetzt API-Auth-Checks (Pytest & Playwright); sie erfordern einen laufenden Backend-Server und gültige Tokens.[`tests/test_auth_middleware.py:1` `playwright-tests/auth-api.spec.ts:1`]
- Sicherheit: Lightweight-Bearer-Middleware schützt zentrale Endpunkte; echter OIDC-/RBAC-Fluss und Audit-Telemetrie fehlen weiterhin.[`main.py:24` `app/core/security.py:1`]
- Observability und Deployment: Monitoring-Artefakte unverändert dokumentiert, jedoch keine aktive Integration (Prometheus- bzw. Tracing-Code bleibt ausständig).

## 4. Soll-/Ist-Vergleich

| Bereich | Soll (Anspruch) | Ist (aktuell) | Abweichung / Kommentar |
|---------|-----------------|---------------|------------------------|
| Architektur | MSOA/DDD mit BFF, Eventbus, autonome Domains.[`VALEO-NEUROERP-DOMAIN-OVERVIEW.md:13`] | FastAPI-Monolith ohne Serviceabtrennung, Eventbus fehlt.[`main.py:10`] | Hoher Gap: Zielarchitektur nicht umgesetzt. |
| Backend (Domains, Events) | Persistente Domain-Services mit Events, Polyglotte DB.[`valeo_neuro_erp_architekturdiagramm_msoa_agentik.jsx:224`] | Monolith nutzt jetzt konsistente SQLAlchemy-Repos; Event-Layer & Microservice-Trennung fehlen weiterhin.[`app/core/container_config.py:16`] | Fortschritt bei Persistenz, strukturelle Entkopplung offen. |
| Frontend / UI-UX | Multimodal, datengetriebene Workflows, Storybook-led UX.[`UI-UX-MCP-INTEGRATION-ROADMAP.md:16`] | POS-Suche verwendet reale API; übrige UIs überwiegend statisch, keine multimodalen Interaktionen.[`packages/frontend-web/src/components/pos/ArticleSearch.tsx:1`] | Teilfortschritt, Großteil der Vision unbedient. |
| KI-Integration (LangGraph, MCP, RAG) | Agentische Layer als Co-Piloten, Echtzeit-SSE, RAG-Anbindung.[`valeo_neuro_erp_architekturdiagramm_msoa_agentik.jsx:143`] | MCP-/SSE-Routen konsolidiert, Policy-Regeln in Postgres; Agenten- und RAG-Layer weiterhin inaktiv.[`app/services/policy_service.py:1`] | Infrastruktur vorbereitet, Funktionalität fehlt. |
| Datenmodell / API | PostgreSQL + Drizzle/SQLAlchemy, OpenAPI-konforme Services.[`README.md:23`] | Kerndomänen (CRM/Inventory/Finance Policies) bedienen Postgres; Migrationen müssen aktualisiert & getestet werden.[`app/api/v1/endpoints/articles.py:1`] | Basis konsolidiert, Migration/Testabdeckung offen. |
| Prozessintelligenz / Agentik | Policy-/Agenten-Engine mit Auto-Execute und Audit.[`VALEO-NEUROERP-DOMAIN-OVERVIEW.md:132`] | PolicyEngine läuft serverseitig, Audit-/Approval-Flows und Agentenorchestrierung fehlen.[`app/services/policy_service.py:1`] | Fortschritt, aber Governance-Komponenten fehlen. |
| Sicherheit / Datenschutz | OIDC, RBAC/ABAC, Audit Logging auf Events.[`README.md:5`] | Bearer-Auth erzwingt Dev-Token; vollständige OIDC-Integration & Audit-Pipeline stehen aus.[`main.py:24`] | Minimale Absicherung vorhanden, Compliance-Risiko reduziert aber nicht gelöst. |
| Dokumentation / CI/CD | GitHub Actions, Deployment-Guides, laufende Pipelines.[`README.md:5`] | Tests für Auth vorhanden; CI-Konfigurationen weiterhin nicht nachweislich aktiv.[`playwright-tests/auth-api.spec.ts:1`] | Dokumentation + Tests existieren, Automatisierung unklar. |

## 5. Schlussfolgerungen und Empfehlungen

### 5.1 Kritische Luecken
- Architektur bleibt monolithisch ohne Domain-Boundaries und Eventing; Roadmap zur schrittweisen Service-Trennung fehlt.[`main.py:10`]
- Agentische Fähigkeiten (LangGraph, Workflow-Co-Piloten) sind weiterhin nicht implementiert; bestehende Policy-Layer benötigt Approval/Audit-Struktur.[`app/services/policy_service.py:1`]
- Sicherheitsmodell basiert derzeit auf Dev-Token; echte OIDC-/RBAC-Anbindung und revisionssichere Audit-Pipeline fehlen.[`app/core/security.py:1`]
- CI/CD-Vertrauen gering: Tests existieren lokal, aber keine automatisierte Ausführung oder Qualitätsmetriken dokumentiert.[`playwright-tests/auth-api.spec.ts:1`]

### 5.2 Quick Wins
- Migrationen aktualisieren und Testdaten-Seed bereitstellen, damit neue Postgres-Tabellen reproduzierbar sind (inkl. `policy_rules`).
- Weitere Kernseiten (Dashboards, CRM) vom Mock-Modus auf die vorhandenen API-Endpunkte umstellen.
- Dev-Token in `.env` konfigurierbar machen und OIDC-Stubs vorbereiten (Discovery-URL, Tokenprüfung), um Testläufe ohne Hardcodings zu ermöglichen.
- Automatisierte Ausführung der neuen Auth-Tests in CI (z. B. GitHub Actions) etablieren und Ergebnisse dokumentieren.

### 5.3 Strategische Massnahmen
- Architektur-Refactor: Domain-Grenzen intern schärfen (Service-Kernel, Event-Publishing) und Fahrplan Richtung echte Microservices definieren.
- KI/Agentik: LangGraph-/RAG-Layer reaktivieren, Policy-Entscheidungen mit Approval-/Audit-Strömen und Realtime-Feedback verschmelzen.
- Daten & Tests: Alembic-Migrationen harmonisieren, Integrationstests für Kern-APIs (CRM, Inventory, Finance) etablieren, Observability (Prometheus/Tracing) anbinden.
- UX-Initiative: Design-System produktiv (Storybook in CI), multimodale Eingaben prototypisch umsetzen, reale Workflows (z. B. POS, Dashboard) mit KPI-Daten versorgen.
- Security & Compliance: Vollständige OIDC/RBAC-Implementierung, Audit-Logging je Domain und Datenschutzkontrollen produktiv schalten.

### 5.4 Priorisierte Roadmap
- Phase 1 (0-4 Wochen): Migrationen & Seed-Skripte aktualisieren, weitere UI-Flows an APIs anbinden, CI-Pipeline um auth/tests erweitern, OIDC-Konfiguration vorbereiten.
- Phase 2 (1-3 Monate): Domain-Events & internes Messaging etablieren, Observability (Metrics/Tracing) integrieren, Storybook + Design Tokens in CI verankern, erste Agenten-Workflows pilotieren.
- Phase 3 (3-6 Monate): LangGraph/RAG produktiv, Approval-/Audit-Flows ausbauen, priorisierte Domains (Finance, Inventory) modularisieren, Compliance-/Security-Zertifizierungen vorbereiten.

---

**Refactoring-Idee (optional):** Ein Service-Kernel innerhalb des Monolithen etabliert klare Domain-Interfaces, abstrahiert Events via internes Publish/Subscribe und schafft damit einen evolutionaeren Pfad zur echten MSOA ohne Big-Bang-Migration.

## 6. Fortschritts-Notizen (Stand aktueller Implementierung)

- **Persistenz vereinheitlicht:** Artikel-, Lager- und Finanz-Endpunkte arbeiten vollständig über SQLAlchemy/PostgreSQL; die neue `policy_rules`-Tabelle sorgt für konsistente KI-Regeln.[`app/api/v1/endpoints/articles.py:1` `app/infrastructure/models/__init__.py:152`]
- **MCP/SSE konsolidiert:** Einheitliche Pfade (`/api/mcp/policy`, `/api/stream/{channel}`, `/api/events`) stellen Frontend- und Backend-Parität sicher; PolicyStore nutzt gemeinsame Service-Logik.[`app/api/v1/endpoints/policies.py:21` `app/routers/sse_router.py:1` `app/policy/store.py:1`]
- **Auth-Baseline aktiv:** Middleware erfordert Bearer-Token (Dev-Token fallback), zusätzliche Tests prüfen Schutzmechanismen.[`main.py:24` `app/core/security.py:1` `tests/test_auth_middleware.py:1`]
- **Frontend-Anbindung gestartet:** POS-Suche konsumiert Live-Daten; weitere Seiten müssen noch von Mock-Ständen gelöst werden.[`packages/frontend-web/src/components/pos/ArticleSearch.tsx:1`]
- **Tests erweitert:** Neben bestehenden Contract-Checks existieren nun API-Auth-Prüfungen für Pytest und Playwright (skippbar via `API_URL`).[`tests/test_auth_middleware.py:1` `playwright-tests/auth-api.spec.ts:1`]

> **Hinweis:** Für zukünftige Releases sollten Migrationen (`alembic/versions`) angepasst, Seed-Skripte bereitgestellt und CI-Pipelines so erweitert werden, dass die neuen Tests automatisiert laufen (inkl. Bereitstellung des Dev-Tokens).

### 6.1 Next Steps (Technische Sofortmaßnahmen)
- FastAPI-Backend einmal starten, damit `create_tables()` die neue `policy_rules`-Tabelle erzeugt, bevor Seed-Skripte laufen.
- `API_DEV_TOKEN` bzw. `VITE_API_DEV_TOKEN` setzen (Standard: `dev-token`) oder echten OIDC-Flow integrieren, um 401-Antworten zu vermeiden.
- Seed-Daten für Artikel pflegen, damit die POS-Suche unmittelbar Ergebnisse ausliefert.
- Für Playwright-API-Checks `API_URL` (und optional `API_DEV_TOKEN`) exportieren, sobald die Tests automatisiert ausgeführt werden sollen.
