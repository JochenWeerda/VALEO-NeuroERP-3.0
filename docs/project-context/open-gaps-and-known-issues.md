# Open Gaps and Known Issues

## Zweck

Diese Datei sammelt die fuer neue Analysen wichtigsten offenen Restthemen und bekannten Unsicherheiten.

## Aktuell besonders relevant

- einzelne Prozessstarts muessen weiter auf Praxisrealismus gegen Landhandelsablaeufe geprueft werden
- Browser-Use- und CRUD-Pruefungen muessen pro Workflow fortgeschrieben werden
- Security-Triage 2026-03-31: `SEC-001` ist abgearbeitet (harte Repo-Secrets und kritische Credential-Defaults entfernt), `SEC-002` liefert lokale zentrale Secret-Pflege ueber Vault + optionales OS-Keyring + CLI, `SEC-003` haertet Metrics und Copilot-WebSocket gegen unauthentifizierten Zugriff und Tenant-Spoofing, `SEC-004` zieht Supplier-Portal-Queries auf tenant-gebundene parametrisierte Statements, `SEC-005` schliesst die generischen Realtime-WebSockets fuer POS/Workflow/Policy, `SEC-006` zieht Accounting-Periods auf kontextgebundene Tenant-Isolation, `SEC-007` haertet den Creditor-Router gegen Payload-/Query-/ID-basierte Cross-Tenant-Zugriffe und die nachgezogenen Slices `SEC-008` bis `SEC-013` schliessen Tenant-Isolation/Mass-Assignment im Einkauf, SQL-Identifier-Whitelists fuer Admin Mobile, XML-Injection im VIES-Client, Information Disclosure im Documents-Router, SSRF bei Webhooks und XSS in browserbasierten Print-Pfaden. Offen bleiben die weiteren schweren Backend-Funde aus SAST sowie die echte externe Produktions-Vault-Anbindung. Roadmap und Folge-Slices: `docs/roadmap/status/2026-04-01-security-hardening-phase-1.md`
- NATS-Consumer + Core-Handler: DLQ, Idempotenz, zusaetzlich Flow-Spine-Handler und Event-Observability (`flow_spine_handlers.py`, `observability.py`) sind umgesetzt; produktives Surfacing im Betrieb/Monitoring steht jetzt ueber `neuro_event_monitoring.py` bereit. Offen bleibt vor allem die Anbindung an externe Dashboards/Alerting
- Der zentrale Neuro Tool Broker ist umgesetzt (NC-A6/NC-A7 inkl. interner OpenAPI-Execution); NC-A14/NC-A16 ziehen Tenant-Override-Propagation, externe HTTP-Execution und contract-gesteuerte Request-Payloads nach. Offen bleiben primaer weitere produktive Tool-Adapter und breitere UI-/Runtime-Nutzung
- Verification und Policy Engine sind in Wave 2 (NC-A8) gekoppelt; Wave 3 ist mit NC-A9 (LLM-Fallback) und NC-D5 (Hash-Chain-Tests) umgesetzt; Wave 4 ist mit NC-A10 (dynamische Plan-Generierung), NC-A11 (Cross-Entity-Integrity), NC-A12 (Risk-Scoring) und NC-A13 (Tenant-Overrides) abgeschlossen. Offen bleiben nun vor allem tiefere Broker-/UI-Folgepfade und produktive Monitoring-/RAG-Ausbaustufen. Details in `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md`
- ChromaDB fuer produktive RAG-Nutzung muss mit Prozesswissen befuellt werden
- Voice-Kanal setzt Web Speech API voraus (Chrome/Edge); Firefox und Safari nicht unterstuetzt
- Agentenarchitektur-Diagramm zeigt weiterhin Restluecken bei produktiver Vault-Anbindung, Memory-Governance, Process-Kernel-Contracts und tieferer Observability (siehe `docs/project-context/agent-architecture-gaps-2026-03-28.md`)
- Neuro-Stack-Status und P1-Luecken sind als Matrix dokumentiert (siehe `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md`)
- Knowledge Store (`knowledge_store.py`, `/neuro/knowledge`) ist umgesetzt; offen bleiben breitere produktive Nutzung in RAG-/Resolver-Pfaden und ggf. dedizierte Migrationen je nach Deploy-Strategie
- Multi-Channel: WhatsApp, E-Mail, Voice, Live-Chat (Backend-REST), Channel-Ingress; offen bleiben outbound Routing und vollstaendige Live-Chat-WebSocket-Anbindung im Produkt-UI

## Zuletzt geschlossene Punkte (Wave 104, 2026-03-27)

- ~~Copilot-/Voice-Pfade sind nicht ueberall gleich tief produktiv~~ -> Voice-Kanal Admin-Seite (`pages/admin/voice-channel.tsx`) im Nav verankert (GAP-104-I)
- ~~RAG-/Knowledge-Tiefe ist nicht in jedem Agentenpfad vollstaendig verdrahtet~~ -> `POST /agent-action` mit ChromaDB-RAG produktiv (graceful degradation, GAP-104-H)
- ~~Flow Spine Outbox-Events nicht verdrahtet~~ -> `FlowSpineInstanceCreated` / `FlowSpineTransitionOccurred` via Outbox (GAP-104-G)

## Zuletzt geschlossene Punkte (2026-03-31)

- ~~SVC-001-P4 Field-Service: `fetch()` statt apiClient~~ — `field-service-tasks.tsx` nutzt `apiClient` + TanStack Query; Backend-Endpunkte unter `/api/v1/agribusiness/field-service-tasks` in `app/api/v1/endpoints/compat.py` (CRM-Mapping, Demo-Fallback).
- ~~Kurz-IDs aus `uuid7()[:8]` bei schnellen Mehrfach-Inserts~~ — Präfix-IDs verwenden `uuid7_short_suffix()` / `default_prefixed_id()` / `prefixed_id()` in `app/core/uuid7.py` (Zeit-Präfix der v7-String-Darstellung war in derselben Millisekunde nicht eindeutig).

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen:

- Doku
- Implementierung
- Fachlogik
- Benutzerfuehrung

auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
- `docs/roadmap/status/*.md`
