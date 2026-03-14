# PKP-04 Cross-Domain-Referenzkette

## Zweck
- explizite Fachreferenz für `Kontrakt -> Annahme -> Charge -> Qualität -> Settlement`

## Status
- erstes Backend-Kernmodell angelegt
- Code-Artefakt: `app/core/process_references.py`

## Kernobjekte
- `ProcessReferenceChain`
- `ProcessReferenceContext`
- `build_process_reference_context(...)`

## Referenzraum
- `contract_id`
- `harvest_acceptance_id`
- `weighing_ticket_id`
- `quality_protocol_id`
- `settlement_id`
- `charge_id`
- `supplier_id`
- `article_id`

## Kerngedanke
- Audit, Workflow und Read-Models sollen auf denselben Referenzraum zeigen
- die Ankerentität wird explizit über `anchor_entity` und `anchor_id` beschrieben

## Nächster Schritt
- bestehende Annahme-/Settlement-/Qualitätsendpunkte schrittweise auf diesen Referenzkontext abbilden
