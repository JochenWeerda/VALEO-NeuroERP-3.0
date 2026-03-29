# Neuro Stack Gap Matrix (2026-03-29)

## Quelle

Die folgende Matrix basiert auf dem gelieferten Komponenten-Status und fasst die Luecken in der Neuro-Architektur zusammen.

## Statusmatrix (Ist-Stand)

| Komponente | Status | Details |
|---|---:|---|
| Neuro Intent Engine | 60% | Capability-Routing existiert (`neuroassist.py`), NLU/Confidence-Scoring fehlt |
| Neuro State Graph | 0% | Fehlt komplett -- kein unified State Graph fuer Bestellung/Rechnung/Kunde/Lager |
| Neuro Context Resolver | 70% | Prozess-/Aggregate-Kontext vorhanden, Consent-Status + Kanal-Historie fehlt |
| Neuro Planner | 65% | Stage-Contracts + Bestellvorschlag-Workflow produktiv, dynamische Schrittgenerierung fehlt |
| Confidence & Risk Engine | 40% | 4-Stufen-Risikomatrix vorhanden, Append-Only Ledger fehlt |
| Rule & Knowledge Store | 55% | Knowledge-Versioning vorhanden, A/B-Testing + Rollback fehlt |
| Guardrails / PII-DLP | 25% | Kritische Luecke -- kein PII-Masking, kein DLP, kein Prompt-Injection-Schutz |
| Action & Policy Layer | 100% | BusinessCommands + CommandDispatcher produktiv |
| Human Oversight | 80% | Approval-Gate mit 4 Risikostufen vorhanden, Case-Management-UI fehlt |
| Audit & Trace | 65% | Middleware + Evidence-Refs vorhanden, Hash-Chain + Append-Only fehlt |
| Event Bus (NATS) | 50% | Publisher vorhanden, Consumer-Framework fehlt |
| Fast Track | 0% | Fehlt -- kein deterministischer Bypass-Pfad |
| Copilot UI | 40% | Frontend-Chat-Hook vorhanden, WebSocket-Streaming fehlt |
| Multi-Channel | 35% | WhatsApp-Adapter vorhanden, Email/LiveChat fehlt |
| LangGraph Integration | 100% | Produktiv -- Workflows, Checkpoints, Human-in-the-Loop |

## P1-Luecken (sofort schliessen)

1. Neuro State Graph -- Unified Business State Tracking
2. Confidence Ledger -- Append-Only mit Hash-Chain
3. Guardrails Middleware -- PII/DLP/Prompt-Injection
4. Fast Track -- Deterministischer Bypass fuer Standard-CRUD
5. Audit Hardening -- Neuro-Entscheidungs-Protokoll

## Produktive Staerken (Ist)

- 6 Agent-Workflows live (Bestellvorschlag, Skonto, Compliance, DQ, Ops, System)
- LangGraph mit Checkpoints + Human-in-the-Loop
- BusinessCommands + Policy-Layer vollstaendig
- Approval-Gate mit Risikostufen

## Annahmen

- Die Prozentwerte sind Einschaetzungen und nicht automatisch aus Tests abgeleitet.
- Status bezieht sich auf funktionale Vollstaendigkeit, nicht auf Skalierung oder Security-Haertung.
