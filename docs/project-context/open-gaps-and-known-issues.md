# Open Gaps and Known Issues

## Zweck

Diese Datei sammelt die fuer neue Analysen wichtigsten offenen Restthemen und bekannten Unsicherheiten.

## Aktuell besonders relevant

- einzelne Prozessstarts muessen weiter auf Praxisrealismus gegen Landhandelsablaeufe geprueft werden
- Browser-Use- und CRUD-Pruefungen muessen pro Workflow fortgeschrieben werden
- NATS-Consumer + Core-Handler vorhanden; DLQ/Idempotenz und Flow-Spine-spezifische Handler fehlen noch
- ChromaDB fuer produktive RAG-Nutzung muss mit Prozesswissen befuellt werden
- Voice-Kanal setzt Web Speech API voraus (Chrome/Edge); Firefox und Safari nicht unterstuetzt
- Agentenarchitektur-Diagramm zeigt Luecken bei IAM/Secrets, Memory-Governance, Process-Kernel-Contracts und Observability (siehe `docs/project-context/agent-architecture-gaps-2026-03-28.md`)
- Neuro-Stack-Status und P1-Luecken sind als Matrix dokumentiert (siehe `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md`)
- Knowledge Store fuer Policies/Prompt-Packs fehlt weiterhin (Registry vorhanden, aber kein persistenter Store)

## Zuletzt geschlossene Punkte (Wave 104, 2026-03-27)

- ~~Copilot-/Voice-Pfade sind nicht ueberall gleich tief produktiv~~ → Voice-Kanal Admin-Seite (`pages/admin/voice-channel.tsx`) im Nav verankert (GAP-104-I)
- ~~RAG-/Knowledge-Tiefe ist nicht in jedem Agentenpfad vollstaendig verdrahtet~~ → `POST /agent-action` mit ChromaDB-RAG produktiv (graceful degradation, GAP-104-H)
- ~~Flow Spine Outbox-Events nicht verdrahtet~~ → `FlowSpineInstanceCreated` / `FlowSpineTransitionOccurred` via Outbox (GAP-104-G)

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
