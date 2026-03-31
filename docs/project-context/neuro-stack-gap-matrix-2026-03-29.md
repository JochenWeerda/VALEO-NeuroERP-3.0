# Neuro Stack Gap Matrix (2026-03-29)

**Letzte Doku-Synchronisation:** 2026-03-31 (NC-A16 Tool-Contract-Harmonisierung, NC-A13 Tenant-Overrides, NC-A12 Risk-Scoring, Wave-4-Abschluss; SVC-001-P4 Field-Service + ORM uuid7 Kurz-ID-Haertung in Projekt-Doku nachgezogen).

## Quelle

Die folgende Matrix basiert auf dem gelieferten Komponenten-Status und fasst die Luecken in der Neuro-Architektur zusammen.

## Statusmatrix (Ist-Stand)

| Komponente | Status | Details |
|---|---:|---|
| Neuro Tool Broker | 99% | NC-A6 + NC-A7 + NC-A14/A16 abgeschlossen: ToolBinding-Registry (20+ Actions), Tenant-Override-Propagation bis in Tool-Calls, OpenAPI-Execution intern und extern, State-Graph-Persistenz nach Execution, per-Step Audit Trace, Fallback-Handling (4xx->degraded, 5xx->failed), contract-gesteuerte Request-Payload-Modi fuer spezialisierte Tools. Offen: weitere produktive Tool-Adapter und tiefere UI-/Runtime-Nutzung |
| Neuro Intent Engine | 95% | NC-A1/A2 + NC-A9: 11 Intent-Patterns, Capability-Matching, Confidence-Scoring, Risk-Klassen, Parameter-Extraktion, LLM-Fallback fuer unbekannte Intents (injected + service-basiert). 103+ Tests gruen. Offen: Prompt-Pack-Integration, Confidence-Ledger-Feedback |
| Neuro State Graph | 92% | Grundgeruest + API + DB-Modelle + Pipeline-Verdrahtung (Broker/NC-A7) + NC-A11 Snapshot-/Relations-Integrity + NC-A12 Risk-Surfacing ueber Ledger-Summaries. Offen: Persistenz-Tiefe |
| Neuro Context Resolver | 85% | Prozess-/Aggregate-Kontext + Consent-Status + Kanal-Historie in `neuroassist_context` (schema_version 2) |
| Neuro Planner | 95% | NC-A3/A4 + NC-A8 + NC-A10: 9 Plan-Templates, typisierte Schritte, per-Step-Verification, Capability-Runner-Delegation und dynamische Plan-Generierung fuer templatefreie Intents. Offen: tiefere Cross-Entity-Integrity |
| Policy Engine | 95% | NC-A8 + NC-A13: temporale Bedingungen + verschachtelte AND/OR-Gruppen + Policy->Verify-Kopplung + Runtime-Tenant-Overrides fuer Regel-Deaktivierung und Parameter-Schwellen. Offen: breitere Nutzung in Broker/UI-Folgepfaden |
| Verification Engine | 98% | NC-A8 + NC-A11 + NC-A13: per-Step-Verification, Policy-Integration, State-Graph-Transitionen, Snapshot-basierte Cross-Entity-Integrity und produktive Tenant-Override-Auswertung auf Plan-/Step-Level. Offen: tieferes Surfacing ausserhalb des Verification-Pfads |
| Confidence & Risk Engine | 90% | Append-Only Ledger + NC-A12 Composite Risk-Scoring, Latest-Risk-Surfacing und Verteilungsmetriken ueber `/confidence-ledger/summary`. Offen: tieferes produktives Feedback in Intent/Planner |
| Rule & Knowledge Store | 85% | Policy-/Prompt-Pack-Registry; Knowledge Store (`knowledge_store.py`, `/neuro/knowledge`) + Tests; produktive RAG-/Resolver-Anbindung Ausbau |
| Guardrails / PII-DLP | 70% | PII-Detector/Guardrails/Consent als NC-C abgeschlossen, DLP-Ausbau offen |
| Action & Policy Layer | 100% | BusinessCommands + CommandDispatcher produktiv |
| Human Oversight | 95% | Approval-Gates, Prozess-Supervisor, generische Run-API und Case-Management-UI vorhanden; generische Gate-Aktionen ausserhalb Bestellvorschlag fehlen |
| Audit & Trace | 92% | D1-D4 + NC-D5 Hash-Chain-Regression-Tests (`test_audit_hash_chain.py`) |
| Event Bus (NATS) | 97% | Publisher + Consumer + Core-Handler; DLQ/Idempotenz; Flow-Spine-Handler + Observability (`flow_spine_handlers.py`, `observability.py`) plus REST-Surfacing fuer Metrics/Health/Errors (`neuro_event_monitoring.py`) |
| Fast Track | 70% | Fast-Track + Compensation als NC-E abgeschlossen, Bypass-Policy-Ausbau offen |
| Copilot UI | 85% | WebSocket-Streaming, Pipeline-Integration, Copilot-Dock und Supervisor/Oversight-UI vorhanden; tiefere Prozess-Einbettung in Kernmasken offen |
| Multi-Channel | 82% | WhatsApp, E-Mail, Voice, Channel-Ingress, Live-Chat (REST unter `channels.py`); outbound Routing / produktive WS-UI Ausbau |
| LangGraph Integration | 100% | Produktiv - Workflows, Checkpoints, Human-in-the-Loop |

## P1-Luecken (sofort schliessen)

1. ~~Audit Hardening -- Hash-Chain + Append-Only-Vertiefung (NC-D4/NC-D5)~~ -> D4 + D5 (Regression-Tests) umgesetzt
2. Guardrails Middleware -- DLP/Prompt-Injection Ausbau (NC-C Folge)
3. ~~Neuro Intent Engine -- NLU/Confidence-Scoring~~ -> NC-A1/A2 umgesetzt mit 11 Intents + Tests
4. ~~Neuro Planner -- dynamische Schrittgenerierung~~ -> NC-A3/A4 mit 9 Templates + Capability-Runner-Delegation
5. **NEU:** Pipeline E2E-Integration: Capability-Runner-Aufruf mit echtem NeuroASSIST-Input-Contract

## Produktive Staerken (Ist)

- 6 Agent-Workflows live (Bestellvorschlag, Skonto, Compliance, DQ, Ops, System)
- LangGraph mit Checkpoints + Human-in-the-Loop
- BusinessCommands + Policy-Layer vollstaendig
- Approval-Gate mit Risikostufen

## Annahmen

- Die Prozentwerte sind Einschaetzungen und nicht automatisch aus Tests abgeleitet.
- Status bezieht sich auf funktionale Vollstaendigkeit, nicht auf Skalierung oder Security-Haertung.

## Naechste 3 Schritte (Plan, Stand 2026-03-31)

1. ~~NC-A7 - Broker OpenAPI Execution Adapter~~ -> umgesetzt
2. ~~Wave 2 - Verification + Policy Integration~~ -> NC-A8 umgesetzt: Policy Engine in Verification verdrahtet, State-Graph-Transitions unifiziert, per-Step Verification im Planner
3. ~~Wave 3 - Decision Trace Hardening + LLM-Fallback~~ -> NC-A9 (LLM-Fallback) + NC-D5 Hash-Chain-Tests umgesetzt. Wave 4 ist mit NC-A10, NC-A11, NC-A12, NC-A13 und NC-A16 auf Produktreife-Stufe nachgezogen.

## Neuro Core Completion Plan (4 Waves)

| Wave | Ziel | Kern-Tasks | Abhaengigkeit |
|------|------|------------|---------------|
| **1: Foundation** | Tool Broker Execution + Pipeline-Verdrahtung | NC-A7: OpenAPI-Adapter, State-Graph-Persistenz, per-Step Audit | keine |
| **2: Correctness** | Verification + Policy Engine Integration | Policy->Verify, State->Verify, per-Step Verify, nested/temporale Bedingungen | erledigt |
| **3: Completeness** | Decision Trace Hardening + Intent LLM | ~~NC-A9 LLM-Fallback~~ umgesetzt; NC-D5 Hash-Chain Regression-Tests offen | Wave 1 |
| **4: Maturity** | Advanced Features + Stufe 2 Vorbereitung | ~~NC-A10 Dynamische Schrittgenerierung~~ + ~~NC-A11 Cross-Entity-Integrity~~ + ~~NC-A12 Risk-Scoring~~ + ~~NC-A13 Tenant-Overrides~~ + ~~NC-A16 Tool-Contract-Harmonisierung~~ umgesetzt | Waves 2+3 |
