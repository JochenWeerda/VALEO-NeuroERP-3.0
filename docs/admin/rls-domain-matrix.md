---
title: RLS-Domain-Matrix (generiert)
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Generierte Entscheidungsmatrix der noch nicht abgesicherten Mandantentabellen je Domain.
---

# RLS-Domain-Matrix (generiert)

Generiert von `scripts/rls_domain_matrix.py`; nicht von Hand aendern. Entscheidungen und Reihenfolge: `docs/architecture/rls-domaenen-entscheidungsmatrix.md`.

Datenstand gewachsene Datenbank: 2026-10-27. Tabellen: 86.

| Domain | dienst | position | referenzdaten | mandant_nullbar | standardmandant | identitaet |
|---|---|---|---|---|---|---|
| agrar | 1 | 1 | 6 | 6 | 8 |  |
| crm | 7 |  |  |  |  |  |
| dev_mock |  |  |  |  |  | 1 |
| erp | 1 | 1 | 2 | 4 | 2 |  |
| finance | 1 |  |  |  |  |  |
| infrastructure |  | 1 |  |  |  |  |
| inventory | 5 |  | 7 |  |  |  |
| log | 1 | 3 |  |  |  |  |
| logistics |  |  | 2 | 5 |  |  |
| mfg |  |  |  | 3 |  |  |
| ops | 1 | 5 | 1 |  | 3 |  |
| portal |  | 1 |  |  |  |  |
| shared | 1 |  | 1 | 2 | 2 | 1 |

## agrar

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_agrar.agrar_duenger` | A | standardmandant | `app/infrastructure/models/agrar_models.py` | `app/api/v1/endpoints/agrar_feldbuch.py`, `app/api/v1/endpoints/agrar_stammdaten_kommandos.py`, `app/api/v1/endpoints/compat.py`, `app/api/v1/endpoints/marketing.py` (+4) | 8 | – | standardmandant 2, token 4 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.agrar_partie_links` | B | mandant_nullbar | – | `app/services/agrar_partie_aggregate_service.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.agrar_psm` | A | standardmandant | `app/infrastructure/models/agrar_models.py` | `app/api/v1/endpoints/agrar_feldbuch.py`, `app/api/v1/endpoints/compliance.py`, `app/api/v1/endpoints/portal_feldbuch.py`, `app/core/screen_definitions.py` (+7) | 20 | – | standardmandant 2, token 5 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.agrar_saatgut` | A | dienst, standardmandant | `app/infrastructure/models/agrar_models.py` | `app/api/v1/endpoints/agrar_feldbuch.py`, `app/api/v1/endpoints/atlas_zollausfuhr.py`, `app/api/v1/endpoints/beleg_vordrucke.py`, `app/api/v1/endpoints/compat.py` (+8) | 21 | – | dienst 2, kopfzeile 1, standardmandant 3, token 7 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_agrar.agrar_sachkunde` | A | standardmandant | `app/infrastructure/models/agrar_models.py` | `app/api/v1/endpoints/compliance.py`, `app/api/v1/endpoints/portal_feldbuch.py`, `app/services/calendar_projection_service.py`, `app/services/pdf_service.py` | 9 | – | standardmandant 2, token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.agrar_selbstabrechnung_status_log` | B | mandant_nullbar | – | `app/services/agrar_selbstabrechnung_lifecycle_service.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.agrar_selbstabrechnungen` | B | mandant_nullbar | – | `app/services/agrar_selbstabrechnung_lifecycle_service.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.agrar_trocknung_abrechnungen` | B | mandant_nullbar | – | `app/services/agrar_trocknung_abrechnung_service.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_feed_products` | A | referenzdaten, mandant_nullbar | – | `app/services/feeding_feed_catalog_service.py` | 2 | – | – | 380 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_feed_reference_values` | A | referenzdaten, mandant_nullbar | – | `app/services/feeding_feed_catalog_service.py` | 2 | – | – | 1157 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_feed_revisions` | A | referenzdaten, mandant_nullbar | – | `app/services/feeding_feed_catalog_service.py` | 0 | – | – | 770 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_groups` | A | referenzdaten, mandant_nullbar | – | `app/services/feeding_business_service.py`, `app/services/feeding_herd_snapshot_service.py`, `app/services/rations_lifecycle_service.py` | 12 | – | token 2 | 1298 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_logs` | A | standardmandant | – | `app/api/v1/endpoints/rations_integrations.py`, `app/api/v1/endpoints/rations_optimization.py` | 0 | – | kopfzeile 1, standardmandant 1, token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_nutrient_definitions` | B | referenzdaten, mandant_nullbar | – | – | 2 | – | – | 19 Z., 0 Mand., 19 null | 19 Zeilen ohne Mandant: Herkunft klaeren (blockiert die Migration) | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_reference_revisions` | B | mandant_nullbar | – | – | 0 | – | – | 22 Z., 0 Mand., 22 null | 22 Zeilen ohne Mandant: Herkunft klaeren (blockiert die Migration) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feeding_unit_definitions` | B | referenzdaten, mandant_nullbar | – | – | 1 | – | – | 8 Z., 0 Mand., 8 null | 8 Zeilen ohne Mandant: Herkunft klaeren (blockiert die Migration) | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.feldbuch_schlaege` | A | standardmandant | `app/infrastructure/models/agrar_models.py` | `app/api/v1/endpoints/agrar_feldbuch.py`, `app/api/v1/endpoints/mask_frontend_bridges.py`, `app/api/v1/endpoints/portal_feldbuch.py`, `modules/agrar/services/feldbuch_service.py` | 6 | – | standardmandant 1, token 5 | 24 Z., 3 Mand., 1 default | 1 Zeilen mit 'default': Herkunft klaeren (blockiert die Migration) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.harvest_acceptances` | B | mandant_nullbar | – | `app/api/v1/endpoints/self_billing.py`, `app/services/mobile_sync_service.py`, `app/services/qs_charge_service.py` | 3 | – | token 2 | 56 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.nutrient_compositions` | A | standardmandant | `app/infrastructure/models/__init__.py` | `app/api/v1/endpoints/nutrient_compositions.py` | 1 | – | nutzlast 1, standardmandant 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.seed_orders` | A | standardmandant | – | `app/api/v1/endpoints/mask_frontend_bridges.py` | 0 | – | standardmandant 1, token 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_agrar.silo_bewegungen` | C | position | `app/domains/operations/models.py` | `app/api/v1/endpoints/silo_operations_api.py` | 1 | – | – | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_agrar.silo_zellen |
| `domain_agrar.waagen_vorlagen` | A | standardmandant | – | `app/api/v1/endpoints/mask_frontend_bridges.py`, `app/api/v1/endpoints/waagen_vorlagen.py` | 0 | – | standardmandant 1, token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |

## crm

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_crm.activities` | B | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/api/v1/endpoints/activities.py`, `app/api/v1/endpoints/compliance_dsgvo.py`, `app/api/v1/endpoints/crm_360.py`, `app/api/v1/endpoints/opportunities.py` (+6) | 12 | – | dienst 2, nutzlast 1, standardmandant 2, token 2 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_crm.crm_opportunities` | A | dienst, standardmandant | `app/domains/crm/models.py` | `app/api/v1/endpoints/leads.py`, `app/api/v1/endpoints/mask_frontend_bridges.py`, `app/api/v1/endpoints/opportunities.py`, `app/core/screen_definitions.py` (+3) | 13 | – | dienst 3, nutzlast 1, standardmandant 2, token 5 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_crm.customers` | B | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/api/v1/endpoints/articles.py`, `app/api/v1/endpoints/compat.py`, `app/api/v1/endpoints/compliance_dsgvo.py`, `app/api/v1/endpoints/contacts.py` (+26) | 70 | `app/workers/compliance_monitor.py` | dienst 14, nutzlast 6, standardmandant 10, token 19 | 6 Z., 2 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_crm.farm_profiles` | B | dienst, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/api/v1/endpoints/farm_profiles.py`, `app/infrastructure/repositories/implementations.py`, `services/crm-core/app/api/v1/endpoints/farm_profiles.py` | 3 | – | dienst 2, nutzlast 1, standardmandant 2 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_crm.leads` | B | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/agents/agent_ops.py`, `app/api/v1/endpoints/compat.py`, `app/api/v1/endpoints/compliance_dsgvo.py`, `app/api/v1/endpoints/customer_extensions.py` (+13) | 32 | – | dienst 8, nutzlast 2, standardmandant 5, token 11 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `public.crm_activities` | A | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/crm/models.py` | `app/api/v1/endpoints/activities.py`, `app/crm/router.py`, `app/crm/seed.py`, `app/infrastructure/repositories/implementations.py` (+2) | 10 | – | dienst 2, nutzlast 1, standardmandant 1, token 1 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `public.crm_leads` | A | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/crm/models.py` | `app/agents/agent_ops.py`, `app/api/v1/endpoints/compat.py`, `app/api/v1/endpoints/compliance_dsgvo.py`, `app/api/v1/endpoints/customer_extensions.py` (+14) | 32 | – | dienst 8, nutzlast 3, standardmandant 5, token 11 | 97 Z., 1 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |

## dev_mock

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_dev_mock.mock_sessions` | A | identitaet | – | – | 0 | – | – | 0 Z., 0 Mand. | – | keine Mandanten-Policy: Nachschlagen vor der Mandantenbindung, Zugriff ueber valeo_system |

## erp

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_erp.bank_accounts` | B | mandant_nullbar | – | `app/api/v1/endpoints/bank_accounts.py` | 4 | – | token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.chart_of_accounts` | B | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/api/v1/endpoints/accounts.py`, `app/api/v1/endpoints/banken.py`, `app/api/v1/endpoints/booking_templates.py`, `app/api/v1/endpoints/chart_of_accounts.py` (+11) | 32 | – | dienst 2, kopfzeile 2, nutzlast 3, standardmandant 1, token 12 | 49 Z., 3 Mand., 28 system | 28 'system'-Zeilen: gemeinsame Referenzdaten begruenden oder zuordnen | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_erp.creditors` | B | mandant_nullbar | – | `app/api/v1/endpoints/creditors.py` | 1 | – | nutzlast 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.debitors` | B | mandant_nullbar | – | `app/api/v1/endpoints/debtors.py` | 1 | – | nutzlast 1, token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.dunning_notices` | A | referenzdaten, mandant_nullbar | – | `app/api/v1/endpoints/dunning.py`, `app/services/finance_dunning_service.py` | 2 | – | token 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.fibu_connector_run_items` | C | position | – | `app/core/connectors/workflow.py` | 1 | – | token 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_erp.fibu_connector_runs |
| `domain_erp.gift_cards` | A | standardmandant | – | – | 2 | – | standardmandant 1, token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.offene_posten` | A | referenzdaten, mandant_nullbar, standardmandant | – | `app/api/v1/endpoints/collective_documents.py`, `app/api/v1/endpoints/credit_debit_memos.py`, `app/api/v1/endpoints/dauerauftraege.py`, `app/api/v1/endpoints/dunning.py` (+20) | 21 | `app/services/scheduler_service.py` | kopfzeile 4, nutzlast 3, standardmandant 2, token 22 | 25 Z., 2 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.open_items` | A | standardmandant | – | – | 3 | – | standardmandant 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_erp.policy_rules` | B | mandant_nullbar | `app/infrastructure/models/__init__.py` | `app/services/policy_service.py` | 1 | – | – | – | Datenbefund fehlt (Tabelle nicht in der gewachsenen Datenbank) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |

## finance

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `public.finance_accounting_periods` | A | dienst | – | `app/api/v1/endpoints/accounting_periods.py`, `app/services/finance_period_service.py` | 4 | – | dienst 1, nutzlast 1, token 2 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |

## infrastructure

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `infrastructure.audit_log` | C | position, standardmandant | – | `app/api/v1/endpoints/open_items.py`, `app/domains/inventory/api/storage_fees.py`, `app/services/admin_core_service.py`, `app/services/docflow_service.py` | 0 | – | standardmandant 1, token 1 | – | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_shared.users |

## inventory

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_inventory.agrar_contracts` | A | referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/l3c_models.py` | `app/api/v1/endpoints/agrar_contracts.py`, `app/api/v1/endpoints/nawaro_raps.py`, `app/api/v1/endpoints/weighing_tickets.py`, `app/routers/contracts_router.py` (+3) | 9 | – | standardmandant 1, token 5 | 3 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_inventory.material_flow_edges` | A | referenzdaten, mandant_nullbar | `app/infrastructure/models/wms_models.py` | `app/services/agri_flush_booking.py`, `app/services/agri_silo_material_flow_service.py` | 4 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_inventory.material_flow_nodes` | A | referenzdaten, mandant_nullbar | `app/infrastructure/models/wms_models.py` | `app/services/agri_silo_material_flow_service.py` | 5 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_inventory.silo_cells` | A | referenzdaten, mandant_nullbar | `app/infrastructure/models/wms_models.py` | `app/api/v1/endpoints/agri_plc_stub.py`, `app/services/agri_flush_booking.py`, `app/services/agri_lot_link_booking_service.py`, `app/services/agri_qs_workflow_service.py` (+2) | 7 | – | token 2 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_inventory.silo_lot_movements` | A | referenzdaten, mandant_nullbar | `app/infrastructure/models/l3c_models.py` | `app/api/v1/endpoints/silo.py`, `app/services/agri_qs_workflow_service.py`, `app/services/agri_silo_lot_link_service.py`, `app/services/supply_chain_lot_service.py` | 5 | – | token 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_inventory.silo_lots` | A | referenzdaten, mandant_nullbar | `app/infrastructure/models/l3c_models.py` | `app/api/v1/endpoints/silo.py`, `app/services/agri_qs_workflow_service.py`, `app/services/agri_silo_lot_link_service.py`, `app/services/supply_chain_lot_service.py` | 10 | – | token 1 | 3 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_inventory.silos` | A | dienst, referenzdaten, mandant_nullbar | `app/infrastructure/models/l3c_models.py` | `app/api/v1/endpoints/silo.py`, `app/api/v1/endpoints/silo_operations_api.py`, `app/core/agent_integration_contracts.py`, `app/core/event_consumer_wiring.py` (+5) | 35 | – | dienst 1, token 4 | 4 Z., 1 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_inventory.weighing_tickets` | A | referenzdaten, mandant_nullbar | `app/infrastructure/models/l3c_models.py` | `app/api/v1/endpoints/nawaro_raps.py`, `app/api/v1/endpoints/weighing_tickets.py`, `app/services/agrar_contract_service.py`, `app/services/harvest_acceptance_service.py` (+2) | 13 | – | token 3 | 50 Z., 2 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `public.inventory_goods_receipt_lines` | C | dienst, position, standardmandant | `services/inventory/app/db/models.py` | `services/inventory/app/api/v1/endpoints/goods_receipt.py` | 2 | – | dienst 2, standardmandant 1 | 3 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `public.inventory_goods_receipts` | A | dienst, standardmandant | `services/inventory/app/db/models.py` | `services/inventory/app/api/v1/endpoints/goods_receipt.py` | 3 | – | dienst 2, standardmandant 1 | 2 Z., 1 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `public.inventory_locations` | C | dienst, position, standardmandant | `services/inventory/app/db/models.py` | `app/api/v1/endpoints/betriebsstaetten.py`, `app/api/v1/endpoints/compat.py`, `services/inventory/app/integration/subscribers.py`, `services/inventory/app/services/inventory_service.py` | 12 | – | dienst 6, kopfzeile 1, standardmandant 1, token 1 | 1 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `public.inventory_warehouses` | A | dienst, standardmandant | `services/inventory/app/db/models.py` | `app/api/v1/endpoints/articles.py`, `app/api/v1/endpoints/warehouse_transfers.py`, `app/api/v1/endpoints/warehouses.py`, `app/domains/inventory/api/warehouses.py` (+8) | 12 | – | dienst 6, nutzlast 2, standardmandant 2, token 2 | 1 Z., 1 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |

## log

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_log.log_tour_delivery_notes` | C | position | `app/domains/verladung/models.py` | `app/domains/verladung/repository.py` | 1 | – | nutzlast 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_log.log_touren |
| `domain_log.log_tour_events` | C | position | `app/domains/verladung/models.py` | `app/domains/verladung/repository.py` | 1 | – | nutzlast 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_log.log_touren |
| `domain_log.log_tour_stops` | C | position | `app/domains/verladung/models.py` | `app/domains/verladung/repository.py` | 1 | – | nutzlast 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_log.log_touren |
| `domain_log.log_touren` | A | dienst, referenzdaten, mandant_nullbar | `app/domains/verladung/models.py` | `app/api/v1/endpoints/tours.py`, `app/domains/verladung/repository.py` | 16 | – | dienst 1, kopfzeile 1, nutzlast 1, token 3 | 0 Z., 0 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |

## logistics

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_logistics.carrier_invoices` | A | referenzdaten, mandant_nullbar | – | `app/api/v1/endpoints/logistics_freight.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_logistics.epod_settlements` | B | mandant_nullbar | – | `app/services/logistics_epod_service.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_logistics.freight_tariffs` | B | referenzdaten, mandant_nullbar | – | `app/api/v1/endpoints/logistics_freight.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_logistics.tour_disposition_checks` | B | mandant_nullbar | – | `app/services/logistics_disposition_service.py` | 0 | – | – | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_logistics.tour_events` | B | mandant_nullbar | – | `app/api/v1/endpoints/logistics_tours.py` | 0 | – | kopfzeile 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_logistics.tour_stops` | B | mandant_nullbar | – | `app/api/v1/command_handlers/logistics.py`, `app/api/v1/endpoints/logistics_tours.py`, `app/services/logistics_epod_service.py`, `app/services/mobile_sync_service.py` | 1 | – | kopfzeile 1 | 2 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_logistics.tours` | B | mandant_nullbar | – | `app/api/v1/command_handlers/logistics.py`, `app/api/v1/endpoints/logistics_tours.py` | 0 | – | kopfzeile 1 | 2 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |

## mfg

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_mfg.bill_of_material` | B | mandant_nullbar | – | – | 0 | – | – | – | Datenbefund fehlt (Tabelle nicht in der gewachsenen Datenbank) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_mfg.production_event` | B | mandant_nullbar | – | – | 0 | – | – | – | Datenbefund fehlt (Tabelle nicht in der gewachsenen Datenbank) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_mfg.production_order` | B | mandant_nullbar | – | – | 0 | – | – | – | Datenbefund fehlt (Tabelle nicht in der gewachsenen Datenbank) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |

## ops

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_ops.kon_contract` | A | standardmandant | `app/domains/operations/models.py` | `app/api/v1/endpoints/kontrakte.py`, `app/api/v1/endpoints/stammdaten_bearbeiten.py`, `app/domains/operations/repository.py`, `app/routers/contracts_router.py` (+3) | 11 | – | nutzlast 2, standardmandant 1, token 3 | 4 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_ops.ops_chargen` | A | dienst, referenzdaten, standardmandant | `app/domains/operations/models.py` | `app/api/v1/endpoints/beleg_vordrucke.py`, `app/api/v1/endpoints/charges.py`, `app/api/v1/endpoints/compat.py`, `app/api/v1/endpoints/compliance.py` (+18) | 34 | – | dienst 3, kopfzeile 1, nutzlast 1, standardmandant 3, token 14 | 79 Z., 1 Mand. | – | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `domain_ops.ops_fahrer` | C | position | `app/domains/operations/models.py` | `app/api/v1/endpoints/beleg_vordrucke.py`, `app/api/v1/endpoints/personal.py`, `app/api/v1/endpoints/sales_orders.py`, `app/api/v1/endpoints/transporte.py` (+2) | 10 | – | nutzlast 3, token 4 | 1 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_ops.ops_fahrzeuge |
| `domain_ops.ops_fahrzeug_bussgeld` | C | position | – | `app/api/v1/endpoints/fuhrpark.py` | 0 | – | token 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_ops.ops_fahrzeuge |
| `domain_ops.ops_fahrzeug_schaeden` | C | position | – | `app/api/v1/endpoints/fuhrpark.py` | 0 | – | token 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_ops.ops_fahrzeuge |
| `domain_ops.ops_fahrzeug_status_historie` | C | position | – | `app/api/v1/endpoints/fuhrpark.py` | 0 | – | token 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_ops.ops_fahrzeuge |
| `domain_ops.ops_fahrzeug_touren` | C | position | `app/domains/operations/models.py` | `app/domains/operations/repository.py` | 2 | – | nutzlast 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_ops.ops_fahrzeuge |
| `domain_ops.ops_fahrzeuge` | A | referenzdaten, mandant_nullbar | `app/domains/operations/models.py` | `app/api/v1/command_handlers/fuhrpark.py`, `app/api/v1/endpoints/fuhrpark.py`, `app/api/v1/endpoints/harvest_acceptance.py`, `app/api/v1/endpoints/hofliste.py` (+5) | 13 | – | kopfzeile 1, nutzlast 2, token 3 | 1 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_ops.ops_pcn_meldungen` | A | standardmandant | `app/domains/operations/models.py` | `app/api/v1/endpoints/compliance.py` | 1 | – | standardmandant 1, token 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_ops.reklamationen` | A | standardmandant | `app/domains/operations/models.py` | `app/api/v1/endpoints/reklamation_api.py` | 3 | – | standardmandant 2, token 3 | 15 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |

## portal

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_portal.customer_order_items` | C | position | `app/infrastructure/models/portal_models.py` | `app/api/v1/endpoints/portal_shop.py` | 2 | – | token 1 | 0 Z. | tenant_id aus dem Elternbeleg nachziehen, NOT NULL, Verbund-FK (eltern_id, tenant_id) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant; tenant_id aus domain_portal.customer_orders |

## shared

| Tabelle | Kl. | Ursache | Modell | Schreiber | Leser | Worker | Identitaet | Daten | Bereinigung | Policy |
|---|---|---|---|---|---|---|---|---|---|---|
| `domain_shared.admin_api_keys` | A | identitaet | – | – | 0 | – | – | – | Datenbefund fehlt (Tabelle nicht in der gewachsenen Datenbank) | keine Mandanten-Policy: Nachschlagen vor der Mandantenbindung, Zugriff ueber valeo_system |
| `domain_shared.api_keys` | A | standardmandant, identitaet | – | `app/services/admin_core_service.py` | 0 | – | standardmandant 1 | 0 Z., 0 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_shared.audit_logs` | A | referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/api/v1/endpoints/ap_approval_workflow.py`, `app/api/v1/endpoints/audit.py`, `app/api/v1/endpoints/compat.py`, `app/api/v1/endpoints/gdpr.py` (+9) | 8 | `app/workers/cleanup_worker.py` | standardmandant 1, token 10 | 2 Z., 2 Mand., 1 system | 1 'system'-Zeilen: gemeinsame Referenzdaten begruenden oder zuordnen | getrennt: SELECT eigener Mandant + 'system' lesen (Begruendung je Tabellenfamilie); INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_shared.calendar_ics_tokens` | A | standardmandant, identitaet | – | `app/services/calendar_projection_service.py` | 0 | – | standardmandant 1 | 9 Z., 1 Mand. | – | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_shared.policy_rules` | B | mandant_nullbar | `app/infrastructure/models/__init__.py` | `app/services/policy_service.py` | 1 | – | – | 3 Z., 0 Mand., 3 null | 3 Zeilen ohne Mandant: Herkunft klaeren (blockiert die Migration) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
| `domain_shared.users` | B | dienst, referenzdaten, mandant_nullbar, standardmandant | `app/infrastructure/models/__init__.py` | `app/agents/neuro_intent_engine.py`, `app/agrar/rations/solver/constraint_registry.py`, `app/api/v1/endpoints/feeding_core.py`, `app/api/v1/endpoints/fibu_connectors.py` (+32) | 116 | – | dienst 18, kopfzeile 2, nutzlast 11, standardmandant 6, token 67 | 5 Z., 3 Mand., 2 default, 2 system | 2 Zeilen mit 'default': Herkunft klaeren (blockiert die Migration); 2 'system'-Zeilen: gemeinsame Referenzdaten begruenden oder zuordnen | keine, bis der Dienst tokengebundene Identitaet hat (rls-dienste-identitaet-vorschlag.md) |
| `public.outbox_events` | B | mandant_nullbar | `app/infrastructure/eventbus/outbox.py` | `app/agrar/rations/events.py`, `app/infrastructure/eventbus/outbox.py`, `app/services/ap_invoice_approval_service.py`, `app/services/docflow_service.py` (+4) | 3 | – | nutzlast 1, token 1 | 1407 Z., 4 Mand., 8 default | 8 Zeilen mit 'default': Herkunft klaeren (blockiert die Migration) | getrennt: SELECT eigener Mandant; INSERT/UPDATE/DELETE nur eigener Mandant |
