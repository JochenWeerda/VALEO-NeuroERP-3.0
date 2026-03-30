# Neuro Stack Gap Matrix (2026-03-29)

## Quelle

Die folgende Matrix basiert auf dem gelieferten Komponenten-Status und fasst die Luecken in der Neuro-Architektur zusammen.

## Statusmatrix (Ist-Stand)

| Komponente | Status | Details |
|---|---:|---|
| Neuro Intent Engine | 85% | NC-A1/A2 umgesetzt: 11 Intent-Patterns, Capability-Matching, Confidence-Scoring, Risk-Klassen, Parameter-Extraktion. 100 Tests gruen. Offen: LLM-basiertes NLU fuer unbekannte Intents |
| Neuro State Graph | 70% | Grundgeruest + API + DB-Modelle umgesetzt (NC-B1), Pipeline-Integration fehlt |
| Neuro Context Resolver | 70% | Prozess-/Aggregate-Kontext vorhanden, Consent-Status + Kanal-Historie fehlt |
| Neuro Planner | 85% | NC-A3/A4: 9 Plan-Templates, typisierte Schritte, Verification-Engine-Integration, Capability-Runner-Delegation. Offen: dynamische Schrittgenerierung fuer unbekannte Intents |
| Confidence & Risk Engine | 75% | Append-Only Ledger umgesetzt (NC-B1), weitere Risk-Aggregate und Cross-Run-Scoring fehlen |
| Rule & Knowledge Store | 70% | Policy-Registry mit A/B + Rollback, Prompt-Pack Registry vorhanden; Knowledge-Store fehlt |
| Guardrails / PII-DLP | 70% | PII-Detector/Guardrails/Consent als NC-C abgeschlossen, DLP-Ausbau offen |
| Action & Policy Layer | 100% | BusinessCommands + CommandDispatcher produktiv |
| Human Oversight | 95% | Approval-Gates, Prozess-Supervisor, generische Run-API und Case-Management-UI vorhanden; generische Gate-Aktionen ausserhalb Bestellvorschlag fehlen |
| Audit & Trace | 85% | Audit Hardening D1-D4 umgesetzt, Pipeline-Audit-Middleware (NC-D4), Hash-Chain + Decision Protocol. Offen: NC-D5 Regression-Tests |
| Event Bus (NATS) | 90% | Publisher + Consumer + Core-Handler vorhanden; DLQ und event_id-Idempotenz vorhanden, Flow-Spine-spezifische Handler/Observability offen |
| Fast Track | 70% | Fast-Track + Compensation als NC-E abgeschlossen, Bypass-Policy-Ausbau offen |
| Copilot UI | 85% | WebSocket-Streaming, Pipeline-Integration, Copilot-Dock und Supervisor/Oversight-UI vorhanden; tiefere Prozess-Einbettung in Kernmasken offen |
| Multi-Channel | 75% | WhatsApp, E-Mail, Voice und Channel-Ingress vorhanden; Live-Chat und outbound Routing fehlen |
| LangGraph Integration | 100% | Produktiv -- Workflows, Checkpoints, Human-in-the-Loop |

## P1-Luecken (sofort schliessen)

1. ~~Audit Hardening -- Hash-Chain + Append-Only-Vertiefung (NC-D4/NC-D5)~~ → D4 umgesetzt, D5 (Regression-Tests) offen
2. Guardrails Middleware -- DLP/Prompt-Injection Ausbau (NC-C Folge)
3. ~~Neuro Intent Engine -- NLU/Confidence-Scoring~~ → NC-A1/A2 umgesetzt mit 11 Intents + Tests
4. ~~Neuro Planner -- dynamische Schrittgenerierung~~ → NC-A3/A4 mit 9 Templates + Capability-Runner-Delegation
5. **NEU:** Pipeline E2E-Integration: Capability-Runner-Aufruf mit echtem NeuroASSIST-Input-Contract

## Produktive Staerken (Ist)

- 6 Agent-Workflows live (Bestellvorschlag, Skonto, Compliance, DQ, Ops, System)
- LangGraph mit Checkpoints + Human-in-the-Loop
- BusinessCommands + Policy-Layer vollstaendig
- Approval-Gate mit Risikostufen

## Annahmen

- Die Prozentwerte sind Einschaetzungen und nicht automatisch aus Tests abgeleitet.
- Status bezieht sich auf funktionale Vollstaendigkeit, nicht auf Skalierung oder Security-Haertung.

## Naechste 3 Schritte (Plan, Stand 2026-03-30)

1. Pipeline E2E: NeuroASSIST-Input-Contracts aus der Intent Engine befuellen und echte Capability-Runs ausloesen.
2. Copilot/Oversight tiefer in Kernmasken surfacen — Pipeline-Ergebnisse in ObjectPage/ListReport einbetten.
3. Live-Chat und outbound Routing als Multi-Channel-Folge ausbauen.
