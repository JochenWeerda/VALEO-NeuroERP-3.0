# NC-A12 - Risk Scoring

## Ziel

Das Confidence Ledger soll neben Rohwerten auch ein konservatives Aggregate-Risk-Scoring liefern, das ueber Runs und State-Graph-Kontexte hinweg direkt im Summary-Endpoint surfacbar ist.

## Ablauf

```mermaid
flowchart TD
    A[Confidence Ledger Entries] --> B[risk_score()]
    B --> C[Confidence-Komponente]
    B --> D[Risk-Level-Gewichtung]
    B --> E[Recency-Faktor]
    C --> F[Composite Score 0-100]
    D --> F
    E --> F
    F --> G[risk_summary()]
    G --> H[/confidence-ledger/summary]
```

## Umsetzung

- `risk_score()` kombiniert Confidence-Abfall, diskrete `RiskLevel`-Schwere und leichte Recency-Gewichtung zu einem konservativen 0-100-Score
- `risk_summary()` liefert jetzt zusaetzlich `risk_score`, `latest_confidence`, `latest_risk` und `risk_distribution`
- Das REST-Surfacing bleibt rueckwaertskompatibel: bestehende Felder bleiben erhalten, neue Felder sind additive Erweiterungen

## Betroffene Dateien

- `app/core/confidence_ledger.py`
- `app/api/v1/endpoints/neuro_state_graph_api.py`
- `tests/test_neuro_state_graph.py`

## Ergebnis

- Aggregate Risk-Scoring ist im Ledger zentral verfuegbar
- API-Clients bekommen Cross-Run-/Case-Summaries ohne eigene Nachaggregation
- Wave 4 schliesst damit die offene Risk-Scoring-Luecke; offen bleibt nur tiefere produktive Tenant-Override-Nutzung
