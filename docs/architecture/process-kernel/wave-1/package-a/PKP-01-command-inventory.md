# PKP-01 Command-Inventur

## Zweck
- Inventur der bestehenden Kernprozesspfade für `Kontrakt -> Annahme -> Qualität -> Settlement`
- Basis für `A3` Ziel-Command-Katalog

## Status
- erstellt durch reproduzierbare Code-Inventur
- Quelle: `scripts/process_kernel/build_command_inventory.py`

## Vorläufige Ziel-Commands
- `contract.create`
- `contract.update`
- `contract.allocate`
- `acceptance.register`
- `acceptance.capture`
- `quality.record`
- `settlement.preview`
- `settlement.create`
- `settlement.post`
- `workflow.simulate`
- `policy.evaluate`

## Backend-Inventur

| Methode | Route | Funktion | Ziel-Command | Quelle |
|------|------|------|------|------|
| `GET` | `/` | `list_agrar_contracts` | `candidate.review` | `app/api/v1/endpoints/agrar_contracts.py:117` |
| `GET` | `/{contract_id}` | `get_agrar_contract` | `candidate.review` | `app/api/v1/endpoints/agrar_contracts.py:148` |
| `POST` | `/` | `create_agrar_contract` | `contract.create` | `app/api/v1/endpoints/agrar_contracts.py:156` |
| `PATCH` | `/{contract_id}` | `update_agrar_contract` | `contract.update` | `app/api/v1/endpoints/agrar_contracts.py:195` |
| `POST` | `/{contract_id}/allocations` | `allocate_contract_quantity` | `contract.allocate` | `app/api/v1/endpoints/agrar_contracts.py:225` |
| `GET` | `/{contract_id}/allocations` | `list_contract_allocations` | `contract.allocate` | `app/api/v1/endpoints/agrar_contracts.py:273` |
| `POST` | `/billing-weight/preview` | `preview_billing_weight` | `settlement.preview` | `app/api/v1/endpoints/agrar_settlements.py:366` |
| `POST` | `/drying/compute` | `compute_drying_settlement` | `settlement.create` | `app/api/v1/endpoints/agrar_settlements.py:387` |
| `POST` | `/preview` | `preview_settlement` | `settlement.preview` | `app/api/v1/endpoints/agrar_settlements.py:425` |
| `POST` | `/` | `create_settlement` | `settlement.create` | `app/api/v1/endpoints/agrar_settlements.py:442` |
| `GET` | `/` | `list_settlements` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:572` |
| `GET` | `/{settlement_id}` | `get_settlement` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:592` |
| `POST` | `/{settlement_id}/post-fibu` | `post_settlement_to_fibu` | `settlement.post` | `app/api/v1/endpoints/agrar_settlements.py:605` |
| `POST` | `/{settlement_id}/cancel` | `cancel_settlement` | `settlement.create` | `app/api/v1/endpoints/agrar_settlements.py:674` |
| `GET` | `/drying-rules` | `list_drying_rules` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:781` |
| `GET` | `/drying-rules/{rule_id}` | `get_drying_rule` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:832` |
| `POST` | `/drying-rules` | `create_drying_rule` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:870` |
| `PUT` | `/drying-rules/{rule_id}` | `update_drying_rule` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:913` |
| `DELETE` | `/drying-rules/{rule_id}` | `delete_drying_rule` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1002` |
| `GET` | `/drying-rules/{rule_id}/download` | `download_drying_rule_document` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1020` |
| `GET` | `/drying-rules/{rule_id}/lookup-rows` | `list_drying_lookup_rows` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1080` |
| `POST` | `/drying-rules/lookup-rows` | `create_drying_lookup_row` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1113` |
| `PUT` | `/drying-rules/lookup-rows/{row_id}` | `update_drying_lookup_row` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1165` |
| `DELETE` | `/drying-rules/lookup-rows/{row_id}` | `delete_drying_lookup_row` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1223` |
| `GET` | `/drying-rules/{rule_id}/factor-ranges` | `list_drying_factor_ranges` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1281` |
| `POST` | `/drying-rules/factor-ranges` | `create_drying_factor_range` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1312` |
| `PUT` | `/drying-rules/factor-ranges/{range_id}` | `update_drying_factor_range` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1363` |
| `DELETE` | `/drying-rules/factor-ranges/{range_id}` | `delete_drying_factor_range` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1421` |
| `GET` | `/{settlement_id}/export-pdf` | `export_settlement_pdf` | `candidate.review` | `app/api/v1/endpoints/agrar_settlements.py:1446` |
| `POST` | `/` | `create_harvest_acceptance` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:657` |
| `GET` | `/` | `list_harvest_acceptances` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:788` |
| `GET` | `/last` | `get_last_harvest_acceptance` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:813` |
| `GET` | `/{acceptance_id}` | `get_harvest_acceptance` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:837` |
| `PUT` | `/{acceptance_id}` | `update_harvest_acceptance` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:882` |
| `DELETE` | `/{acceptance_id}` | `delete_harvest_acceptance` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:916` |
| `POST` | `/{acceptance_id}/calculate` | `calculate_harvest_settlement_endpoint` | `settlement.create` | `app/api/v1/endpoints/harvest_acceptance.py:935` |
| `POST` | `/{acceptance_id}/derive-nuts2` | `derive_nuts2_from_postal_code_endpoint` | `candidate.review` | `app/api/v1/endpoints/harvest_acceptance.py:1206` |
| `POST` | `/{acceptance_id}/release` | `release_harvest_acceptance` | `acceptance.capture` | `app/api/v1/endpoints/harvest_acceptance.py:1233` |
| `POST` | `/{acceptance_id}/qualitaetsprotokoll` | `create_qualitaetsprotokoll` | `candidate.review` | `app/api/v1/endpoints/harvest_acceptance.py:1407` |
| `GET` | `/{acceptance_id}/qualitaetsprotokoll` | `get_qualitaetsprotokoll` | `candidate.review` | `app/api/v1/endpoints/harvest_acceptance.py:1501` |
| `POST` | `/{acceptance_id}/frachtkosten` | `calculate_frachtkosten` | `candidate.review` | `app/api/v1/endpoints/harvest_acceptance.py:1533` |
| `GET` | `/{acceptance_id}/frachtkosten` | `get_frachtkosten` | `candidate.review` | `app/api/v1/endpoints/harvest_acceptance.py:1605` |
| `GET` | `/{protocol_id}` | `get_protocol` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:176` |
| `GET` | `/harvest-acceptance/{harvest_acceptance_id}` | `get_protocols_by_harvest_acceptance` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:195` |
| `GET` | `/harvest-acceptance/{harvest_acceptance_id}/latest` | `get_latest_protocol_for_harvest_acceptance` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:211` |
| `PUT` | `/{protocol_id}` | `update_protocol` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:230` |
| `POST` | `/{protocol_id}/finalize` | `finalize_protocol` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:265` |
| `POST` | `/import/csv` | `import_protocol_from_csv` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:286` |
| `POST` | `/import/json` | `import_protocol_from_json` | `quality.record` | `app/api/v1/endpoints/quality_protocols.py:314` |

## Frontend-Inventur

| Methode | API-Pfad | Ziel-Command | Quelle |
|------|------|------|------|
| `GET` | `/api/v1/agrar/settlements` | `candidate.review` | `packages/frontend-web/src/pages/annahme/abrechnung.tsx:228` |
| `POST` | `/api/v1/agrar/settlements/billing-weight/preview` | `settlement.preview` | `packages/frontend-web/src/pages/annahme/abrechnung.tsx:242` |
| `POST` | `/api/v1/agrar/settlements/drying/compute` | `settlement.create` | `packages/frontend-web/src/pages/annahme/abrechnung.tsx:254` |
| `POST` | `/api/v1/agrar/settlements/preview` | `settlement.preview` | `packages/frontend-web/src/pages/annahme/abrechnung.tsx:269` |
| `POST` | `/api/v1/agrar/settlements` | `settlement.create` | `packages/frontend-web/src/pages/annahme/abrechnung.tsx:288` |
| `POST` | `/api/v1/agrar/quality-protocols` | `quality.record` | `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx:95` |
| `POST` | `/api/v1/annahme/upload` | `acceptance.register` | `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx:49` |
| `POST` | `/annahme/warteschlange` | `acceptance.register` | `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx:126` |
| `GET` | `/api/v1/admin/process-variants` | `workflow.simulate` | `packages/frontend-web/src/pages/workflow/workflow-sandbox.tsx:65` |
| `GET` | `/api/v1/admin/erntefenster-campaigns` | `workflow.simulate` | `packages/frontend-web/src/pages/workflow/workflow-sandbox.tsx:77` |
| `POST` | `/api/v1/admin/workflow-sandbox/preview` | `settlement.preview` | `packages/frontend-web/src/pages/workflow/workflow-sandbox.tsx:84` |

## Vorläufiges Mapping bestehender Pfade -> Ziel-Command

| Bereich | Bestehender Pfad | Ziel-Command | Hinweis |
|------|------|------|------|
| `backend` | `/` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{contract_id}` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/` | `contract.create` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{contract_id}` | `contract.update` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{contract_id}/allocations` | `contract.allocate` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/billing-weight/preview` | `settlement.preview` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying/compute` | `settlement.create` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/preview` | `settlement.preview` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/` | `settlement.create` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{settlement_id}` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{settlement_id}/post-fibu` | `settlement.post` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{settlement_id}/cancel` | `settlement.create` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/{rule_id}` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/{rule_id}/download` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/{rule_id}/lookup-rows` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/lookup-rows` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/lookup-rows/{row_id}` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/{rule_id}/factor-ranges` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/factor-ranges` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/drying-rules/factor-ranges/{range_id}` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{settlement_id}/export-pdf` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/` | `acceptance.capture` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/last` | `acceptance.capture` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{acceptance_id}` | `acceptance.capture` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{acceptance_id}/calculate` | `settlement.create` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{acceptance_id}/derive-nuts2` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{acceptance_id}/release` | `acceptance.capture` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{acceptance_id}/qualitaetsprotokoll` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{acceptance_id}/frachtkosten` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{protocol_id}` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/harvest-acceptance/{harvest_acceptance_id}` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/harvest-acceptance/{harvest_acceptance_id}/latest` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/{protocol_id}/finalize` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/import/csv` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `backend` | `/import/json` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/agrar/settlements` | `candidate.review` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/agrar/settlements/billing-weight/preview` | `settlement.preview` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/agrar/settlements/drying/compute` | `settlement.create` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/agrar/settlements/preview` | `settlement.preview` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/agrar/settlements` | `settlement.create` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/agrar/quality-protocols` | `quality.record` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/annahme/upload` | `acceptance.register` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/annahme/warteschlange` | `acceptance.register` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/admin/process-variants` | `workflow.simulate` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/admin/erntefenster-campaigns` | `workflow.simulate` | vorläufige Heuristik, fachlich prüfen |
| `frontend` | `/api/v1/admin/workflow-sandbox/preview` | `settlement.preview` | vorläufige Heuristik, fachlich prüfen |

## Offene Punkte
- `candidate.review`-Einträge fachlich auf echte Commands konsolidieren
- UI-CRUD-Pfade gegen explizite Command-Semantik prüfen
- fehlende Reklamationspfade im nächsten Schritt ergänzen
