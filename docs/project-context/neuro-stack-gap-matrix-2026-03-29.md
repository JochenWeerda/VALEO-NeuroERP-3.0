# Neuro Stack Gap Matrix (2026-03-29)

## Quelle

Die folgende Matrix basiert auf dem gelieferten Komponenten-Status und fasst die Luecken in der Neuro-Architektur zusammen.

## Statusmatrix (Ist-Stand)

| Komponente | Status | Details |
|---|---:|---|
| Neuro Intent Engine | 60% | Capability-Routing existiert (`neuroassist.py`), NLU/Confidence-Scoring fehlt |
| Neuro State Graph | 70% | Grundgeruest + API + DB-Modelle umgesetzt (NC-B1), Pipeline-Integration fehlt |
| Neuro Context Resolver | 70% | Prozess-/Aggregate-Kontext vorhanden, Consent-Status + Kanal-Historie fehlt |
| Neuro Planner | 65% | Stage-Contracts + Bestellvorschlag-Workflow produktiv, dynamische Schrittgenerierung fehlt |
| Confidence & Risk Engine | 70% | Append-Only Ledger umgesetzt (NC-B1), weitere Risk-Aggregate fehlen |
| Rule & Knowledge Store | 55% | Knowledge-Versioning vorhanden, A/B-Testing + Rollback fehlt |
| Guardrails / PII-DLP | 70% | PII-Detector/Guardrails/Consent als NC-C abgeschlossen, DLP-Ausbau offen |
| Action & Policy Layer | 100% | BusinessCommands + CommandDispatcher produktiv |
| Human Oversight | 80% | Approval-Gate mit 4 Risikostufen vorhanden, Case-Management-UI fehlt |
| Audit & Trace | 70% | Audit Hardening D1-D3 vorhanden, Hash-Chain/Append-Only-Vertiefung offen |
| Event Bus (NATS) | 60% | Publisher vorhanden, Consumer-Framework (NC-G2) fehlt |
| Fast Track | 70% | Fast-Track + Compensation als NC-E abgeschlossen, Bypass-Policy-Ausbau offen |
| Copilot UI | 50% | Frontend-Chat-Hook da, WebSocket-Streaming teilweise (NC-F), fehlende F5-Integration |
| Multi-Channel | 40% | WhatsApp-Adapter vorhanden, Email/LiveChat fehlt |
| LangGraph Integration | 100% | Produktiv -- Workflows, Checkpoints, Human-in-the-Loop |

## P1-Luecken (sofort schliessen)

1. Audit Hardening -- Hash-Chain + Append-Only-Vertiefung (NC-D4/NC-D5)
2. Guardrails Middleware -- DLP/Prompt-Injection Ausbau (NC-C Folge)
3. Neuro Intent Engine -- NLU/Confidence-Scoring
4. Neuro Planner -- dynamische Schrittgenerierung
5. Event Bus -- NATS Consumer-Framework (NC-G2)

## Produktive Staerken (Ist)

- 6 Agent-Workflows live (Bestellvorschlag, Skonto, Compliance, DQ, Ops, System)
- LangGraph mit Checkpoints + Human-in-the-Loop
- BusinessCommands + Policy-Layer vollstaendig
- Approval-Gate mit Risikostufen

## Annahmen

- Die Prozentwerte sind Einschaetzungen und nicht automatisch aus Tests abgeleitet.
- Status bezieht sich auf funktionale Vollstaendigkeit, nicht auf Skalierung oder Security-Haertung.

## Naechste 3 Schritte (Plan)

1. NC-D4: Audit Hardening Pipeline-Integration abschliessen.
2. NC-G2: NATS Consumer-Framework fuer Event Bus umsetzen.
3. NC-A/Planner: NLU/Confidence-Scoring und dynamische Schrittgenerierung priorisieren.
