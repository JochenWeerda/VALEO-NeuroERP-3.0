# NC-B1 -- State Graph + Confidence Ledger

**Lane:** Neuro-Core  
**Prioritaet:** P1 (Architektur-kritisch)  
**Status:** umgesetzt  

## Kontext
Neuro-Core benoetigt einen einheitlichen Business-State-Graph, um
Zustandsuebergaenge fuer Bestellung/Rechnung/Lager/Kunde nachvollziehbar
und pruefbar zu halten. Parallel muss jede Risiko- oder Konfidenzentscheidung
append-only im Ledger stehen, damit Audit und Explainability belastbar sind.

## Loesung
State Graph mit Nodes, Edges und Transitions (append-only). Confidence Ledger
mit Hash-Chain zur Integritaetspruefung. REST-API mit DB-Persistenz.

## Dateien
- `app/core/neuro_state_graph.py` -- Modelle und Transition-Validierung
- `app/core/confidence_ledger.py` -- Ledger-Logik und Hash-Chain
- `app/infrastructure/models/neuro_state_models.py` -- SQLAlchemy-Modelle
- `app/api/v1/endpoints/neuro_state_graph_api.py` -- REST-Endpunkte
- `alembic/versions/neuroassist_state_graph_confidence_ledger_20260329.py` -- Migration
- `tests/test_neuro_state_graph.py` -- Unit- und API-Tests
- `docs/workflows/nc-b1-state-graph-confidence-ledger.md` -- Workflow-Doku

## Abhaengigkeiten
- Process-Kernel Contracts (Transition-Guards)
- Approval- und Audit-Layer (Evidence-Refs)
