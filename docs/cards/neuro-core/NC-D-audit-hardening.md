# NC-D — Audit Hardening + Decision Protocol

**Lane:** Neuro-Core (Lane D)
**Prioritaet:** P1 (Architektur-kritisch)
**Status:** umgesetzt

## Kontext
Das bestehende Audit-System loggt Mutationen, persistiert sie aber nicht in einem
manipulationssicheren Append-Only-Schema mit Hash-Chain. Fuer GoBD-Konformitaet
und AI-Erklaerbarkeit braucht es ein unveraenderliches Audit-Schema plus ein
Entscheidungs-Protokoll fuer jede Neuro-Core-Aktion.

## Loesung
Append-Only AuditEntry-Tabelle mit SHA-256 Hash-Chain (previous_hash).
AuditMiddleware schreibt alle Mutationen direkt in die DB statt nur ins Log.
NeuroDecisionProtocol erfasst den vollstaendigen Entscheidungspfad jeder AI-Aktion.

## Dateien
- `app/services/audit_hardening.py` — Append-Only Audit + Hash-Chain
- `app/services/neuro_decision_protocol.py` — Decision Protocol Service
- `app/api/v1/endpoints/neuro_audit.py` — REST-API fuer Trail + Decisions
- `docs/workflows/nc-d-audit-hardening.md` — Workflow-Doku

## Abhaengigkeiten
- Bestehende `domain_shared.audit_logs` Tabelle
- Neuro Verification Engine (NC-001) fuer Verification-Ergebnisse
