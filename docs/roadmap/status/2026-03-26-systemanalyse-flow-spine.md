# Systemanalyse Flow Spine 2026-03-26

**Zweck:** Abgleich zwischen aktuellem Implementierungsstand des Flow-Spine-Stacks und der angestrebten Zielarchitektur von VALEO NeuroERP 3.0.

## Ziel

Diese Analyse verdichtet den Stand nach den juengsten Flow-Spine-, Runtime- und UI-Haertungen auf `develop` bzw. `main`.
Sie dient als korrigierte Management-Sicht fuer Architektur, Produktreife und verbleibende technische Restthemen.

## Statusabgleich

- Codebasis: `develop` / `main` Stand `2026-03-26`
- Relevante Commits:
  - `2a8be12e` `perf: Flow-Spine load time - backend JSON cache + HTTP headers + frontend staleTime`
  - `1a35c3ad` `fix: merge useMemo hooks to prevent HMR hook-count mismatch in AppRouteRuntime`
  - `10e5c740` `fix: stabilize wildcard route loader to prevent Suspense spinner on re-render`
  - `76b916f6` `Clarify dashboard labels and localize starters`
- Hauptquellen:
  - [STATUS.md](/c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
  - [2026-03-20-gap-matrix-bereinigt.md](/c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/roadmap/status/2026-03-20-gap-matrix-bereinigt.md)
  - [flow_spines.py](/c:/Users/Jochen/VALEO-NeuroERP-3.0/app/api/v1/endpoints/flow_spines.py)
  - [flow_spine_registry.py](/c:/Users/Jochen/VALEO-NeuroERP-3.0/app/core/flow_spine_registry.py)
  - [FlowSpineWorkspace.tsx](/c:/Users/Jochen/VALEO-NeuroERP-3.0/packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx)

## Korrigierter Implementierungsstand

| Schicht | Zielbild | Ist-Stand |
|---|---|---|
| VALEO UI | Klassische ERP-Masken | `React 18`, `TypeScript`, `Vite`, Mask-Builder und DS-Pattern produktiv |
| Flow Spine UI | Prozesszentrierte Arbeitsraeume | 9 repo-native Prozessraeume mit gemeinsamem Backend-Katalog und Workspace-Contract |
| Copilot UI | Agent-Hinweise, Kontext, Aktionen | Agent-Panel, Action-Layer und KI-Usability vorhanden; Voice weiter nur partiell |
| API Gateway | Gateway / Middleware | `FastAPI`, Auth, CORS, Prometheus, Audit-Middleware vorhanden |
| Agent Orchestrator | Prozess- und Tool-Steuerung | Flow-Spine-Registry plus Agent-Actions produktiv vorhanden |
| Tool Layer | Function Calling / externe Agenten | OpenAPI-/MCP-Contracts und Flow-Spine-Actions vorhanden |
| Memory Layer | persistente Prozessfaelle | Flow-Spine-Instanzen sind **persistiert in Postgres** ueber `ops_flow_spine_instances`; kein In-Memory-Store mehr |
| Kurzzeit-Cache | Performance-Layer | HTTP-Cache-Header plus JSON-Cache im Flow-Spine-Katalog; Redis weiterhin nur optional / infra-seitig |
| Event Bus | asynchrone Orchestrierung | `NATS JetStream` / Outbox-Pattern vorhanden |
| Vector / RAG | Wissenskontext fuer Agenten | Knowledge-/RAG-Infrastruktur vorhanden, aber noch nicht durchgaengig in jeden Agentenpfad integriert |
| ERP-Domaenen | Sales, Einkauf, Lager, Finanzen, CRM, DMS | Produktiv und breit vorhanden |
| Datenbank | produktive Persistenz | `PostgreSQL`, Multi-Schema, Alembic, SQLAlchemy 2.0 |
| Externe Dienste | OCR, Wetter, Kommunikation, EDI | vorhanden |

## Flow-Spine-spezifischer Stand

- `GET /api/v1/process/flow-spines/catalog` und `GET /api/v1/process/flow-spines/{process_key}` liefern den gemeinsamen Prozesskatalog und die Workspaces.
- `POST /api/v1/process/flow-spines/{process_key}/instances` erzeugt persistente Prozessfaelle mit `workflow_case`-Nummer.
- Die Instanzen liegen in `domain_ops.ops_flow_spine_instances` und bleiben ueber Neustarts erhalten.
- Das Frontend arbeitet mit React Query, `staleTime`, lokalisiertem Katalog und einer gemeinsamen Workspace-Komponente.
- Die frueheren HMR-/Suspense-Probleme im Route-Loader sind behoben.
- Dashboard-Starter und Domain-Badges sind sprachabhaengig gelabelt und fachlich verstaendlicher gezogen.

## Prozessrealismus und Nummernkreise

- Flow-Spine startet nicht mehr mit fachlichen Endbelegnummern im Browser.
- Stattdessen entsteht zuerst ein `workflow_case`, danach erfolgt der Wechsel in die jeweilige Standard- oder Kernmaske.
- `Order-to-Cash`:
  - Auftragsnummer wird erst beim Speichern im Backend vergeben.
  - Mengen, Preise, Positionen und Konditionen werden in der Auftragsmaske gepflegt.
- `Procure-to-Pay`:
  - Bestellnummer wird nicht mehr im Browser generiert.
  - Lieferant, Positionen, Mengen, Preise, Incoterms und Termine werden in der Bestellmaske gepflegt.
- `Contract-to-Settlement`:
  - Kontraktnummer bleibt fuer Workflow-Neuanlagen backendseitig nummernkreisfaehig.
- Weitere Prozessraeume uebergeben Handover-Kontext (`workflowCase`, `entryMode`, `subject`, Partnerkontext) in die jeweilige Zielmaske.

## Verifikation

- Flow-Spine-API:
  - `python -m pytest tests/test_flow_spines_api.py tests/test_sales_order_numbering.py -q`
  - Ergebnis: `17 passed`
- Frontend:
  - `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
  - gruen

## Korrigierte Bewertung gegen die fruehere Analyse

- Aussage `In-Memory Instance Store`:
  - **veraltet / falsch fuer den aktuellen Stand**
  - aktuell DB-persistiert in `ops_flow_spine_instances`
- Aussage `useFlowSpineInstances Typ-Mismatch`:
  - fuer den aktuellen Code **nicht mehr zutreffend**
  - der Hook entpackt das Backend-Envelope bereits korrekt ueber `res.data.instances`
- Aussage `POST /api/v1/compliance/pcn-meldungen fehlt`:
  - nicht Teil des juengsten Flow-Spine-Fixes
  - bleibt als separates Restthema ausserhalb dieser Flow-Spine-Analyse zulaessig

## Verbleibende technische Restthemen

- Voice-/Copilot-Kanal bleibt nicht vollstaendig als durchgehender ERP-Prozessraum umgesetzt.
- RAG-/Vector-Kontext ist vorhanden, aber noch nicht gleichmaessig in alle Agenten-/Tool-Pfade eingebunden.
- Einige Prozessraeume landen nach dem Handover bewusst erst in Arbeitslisten statt direkt in abgespeckten Intake-Masken, vor allem:
  - `Complaint-to-Resolution`
  - `Service-to-Customer`
- Diese Punkte sind Produktverfeinerung, keine Blocker fuer die aktuelle Flow-Spine-Architektur.

## Fazit

Der Flow-Spine-Stack ist architektonisch deutlich naeher an der Zielarchitektur als in der frueheren Analyse beschrieben.
Der wesentliche Sprung ist erfolgt:

- persistente Prozessinstanzen
- gemeinsamer Backend-Vertrag
- lokalisierte und fachlich verstaendliche UI
- prozessrealistischer Handover in echte Fachmasken

Der naechste sinnvolle Ausbau liegt nicht mehr im Kern-Stack, sondern in der weiteren Verfeinerung einzelner Prozessstarts und im tieferen Copilot-/RAG-Ausbau.
