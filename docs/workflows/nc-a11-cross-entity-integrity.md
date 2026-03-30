# NC-A11 - Cross-Entity Integrity

## Ziel

State-Graph-Beziehungen sollen nicht nur ueber Einzeltransitionen, sondern auch ueber relationale Konsistenz zwischen mehreren Business-Objekten verifiziert werden.

## Ablauf

```mermaid
flowchart TD
    A[Plan oder Step] --> B{state_graph_snapshot vorhanden?}
    B -- Nein --> C[keine Cross-Entity-Pruefung]
    B -- Ja --> D[StateGraphSnapshot validieren]
    D --> E[verify_snapshot_integrity()]
    E --> F{Relationen konsistent?}
    F -- Ja --> G[keine Violations]
    F -- Nein --> H[CROSS_ENTITY_INTEGRITY Violations]
```

## Regeln

- `ERZEUGT`: Quellobjekt darf nicht mehr im `entwurf` stehen; Zielobjekt darf nicht `storniert` sein
- `REFERENZIERT`: terminale Quelle darf kein aktives Ziel referenzieren
- `BLOCKIERT`: offene/in Bearbeitung befindliche Freigaben blockieren fortgeschrittene Zielphasen
- `FOLGT_AUF`: Vorgaenger muss abgeschlossen, archiviert oder storniert sein
- `ENTHAELT`: stornierte Container duerfen keine aktiven Inhalte tragen

## Betroffene Dateien

- `app/core/neuro_state_graph.py`
- `app/core/confidence_ledger.py`
- `app/services/neuro_verification_engine.py`
- `tests/test_neuro_state_graph.py`
- `tests/test_neuro_verification_engine.py`

## Ergebnis

- Snapshot-basierte Cross-Entity-Integrity ist in der Verification Engine angekommen
- Step- und Plan-Level koennen `state_graph_snapshot` direkt verifizieren
- Die angrenzende Ledger-Suite ist mit einer stabilen `latest_confidence()`-Semantik wieder gruen
