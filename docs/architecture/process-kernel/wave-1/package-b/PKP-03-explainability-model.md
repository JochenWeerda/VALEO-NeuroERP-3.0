# PKP-03 Explainability-Modell

## Zweck
- Policy-, Freigabe- und Ausnahmeentscheidungen als strukturierte Sicht für UI und Audit modellieren

## Status
- erstes Explainability-Kernmodell angelegt
- Code-Artefakt: `app/core/explainability.py`

## Kernobjekte
- `ExplainabilityView`
- `ExplainabilityDetail`
- `build_policy_explainability_view(...)`

## Kerngedanke
- Explainability basiert auf strukturierten Quellen, nicht auf Freitext
- wirksame Ebene, Grund und Quelle werden explizit transportiert

## Nächster Schritt
- bestehende UI-Decision-Views an das Backend-Kernmodell angleichen
