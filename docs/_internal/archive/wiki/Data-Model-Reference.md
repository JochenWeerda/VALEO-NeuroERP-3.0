# Datenmodell-Referenz

## Uebersicht

129 Tabellen ueber 7 aktive Domain-Schemas. Alle PKs sind UUID v7 (String(36)).

---

## domain_shared

Mandantenuebergreifende Stammdaten.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| Tenant | tenants | id | name, slug, is_active |
| Branch | branches | id | tenant_id (FK), branch_number, name, address (JSONB) |
| User | users | id | tenant_id (FK), email, role, full_name |
| PolicyRule | policy_rules | id | tenant_id (FK), resource, action, effect |
| AuditLog | audit_logs | id | tenant_id (FK), user_id, action, entity_type, entity_id, changes (JSONB) |
| WebhookRegistration | webhook_registrations | id | tenant_id (FK), url, events, secret |
| InternalMessage | internal_messages | id | tenant_id (FK), sender_id, recipient_id, subject, body |
| MasterDataEntry | master_data_entries | id | tenant_id (FK), category, code, label |
| SystemProperty | system_properties | id | tenant_id (FK), key, value (JSONB), description |
| Dispatcher | dispatchers | id | tenant_id (FK), name, code |

---

## domain_crm

CRM mit 360-Grad-Geschaeftspartner-Sicht.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| Customer | customers | id | tenant_id, customer_number, name, email |
| Lead | leads | id | tenant_id, company_name, contact_name, status |
| Contact | contacts | id | tenant_id, first_name, last_name, email, phone |
| Activity | activities | id | tenant_id, activity_type, subject, due_date |
| FarmProfile | farm_profiles | id | tenant_id, farm_name, total_area_ha |
| **BusinessPartner** | **business_partners** | **partner_id** | tenant_id, partner_number, name1/name2, **38 NOT NULL boolean Felder** |
| BusinessPartnerContact | bp_contacts | id | partner_id (FK→partner_id) |
| BusinessPartnerAddress | bp_addresses | id | partner_id (FK→partner_id) |
| BusinessPartnerDiscountItem | bp_discount_items | id | partner_id (FK→partner_id) |
| BusinessPartnerPriceAgreement | bp_price_agreements | id | partner_id (FK→partner_id) |
| BusinessPartnerInstruction | bp_instructions | id | partner_id (FK→partner_id) |
| BusinessPartnerBillingConfig | bp_billing_configs | id | partner_id (FK→partner_id) |
| BusinessPartnerCpdAccount | bp_cpd_accounts | id | partner_id (FK→partner_id) |
| BusinessPartnerPricingRule | bp_pricing_rules | id | partner_id (FK→partner_id) |
| BusinessPartnerInterestSetting | bp_interest_settings | id | partner_id (FK→partner_id) |
| BusinessPartnerDispatchMedium | bp_dispatch_media | id | partner_id (FK→partner_id) |
| BusinessPartnerCooperativeMembership | bp_cooperative_memberships | id | partner_id (FK→partner_id) |
| BusinessPartnerEmailDistribution | bp_email_distributions | id | partner_id (FK→partner_id) |
| BusinessPartnerCommunity | bp_communities | id | partner_id (FK→partner_id) |
| BusinessPartnerCommunityMember | bp_community_members | id | community_id (FK) |
| BusinessPartnerProfile | bp_profiles | id | partner_id (FK→partner_id) |
| BusinessPartnerInterfaceProfile | bp_interface_profiles | id | partner_id (FK→partner_id) |
| SupplierTaxProfile | supplier_tax_profiles | id | partner_id (FK→partner_id) |

> **ACHTUNG:** BusinessPartner PK ist `partner_id`, NICHT `id`. Alle FKs muessen auf `business_partners.partner_id` verweisen.

---

## domain_inventory

Artikel, Lager, Wiegescheine, Kontrakte, Ernte-Annahme.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| Article | articles | id | tenant_id, article_number, name, unit, **15+ NOT NULL boolean Felder** |
| ArticleSupplier | article_suppliers | id | article_id (FK), supplier_id |
| ArticleDocument | article_documents | id | article_id (FK) |
| ArticleAlternativeEan | article_alternative_eans | id | article_id (FK) |
| ArticleUnit | article_units | id | article_id (FK) |
| ArticleAnalysis | article_analyses | id | article_id (FK) |
| ArticlePrintSetting | article_print_settings | id | article_id (FK) |
| ArticleBatch | article_batches | id | article_id (FK), batch_number |
| ArticleSelection | article_selections | id | article_id (FK) |
| Warehouse | warehouses | id | tenant_id, warehouse_code, name |
| StockMovement | stock_movements | id | tenant_id, article_id (FK), warehouse_id (FK), quantity |
| InventoryCount | inventory_counts | id | tenant_id, warehouse_id (FK) |
| InventoryCountLine | inventory_count_lines | id | count_id (FK), article_id (FK) |
| WeighingTicket | weighing_tickets | id | tenant_id, ticket_number, vehicle_plate, gross/tare/net_weight |
| WeighingTicketLine | weighing_ticket_lines | id | ticket_id (FK) |
| WeighingMeasurement | weighing_measurements | id | ticket_id (FK) |
| AgrarContract | agrar_contracts | id | tenant_id, contract_number, partner_id (FK→partner_id), article_id (FK) |
| AgrarContractAllocation | agrar_contract_allocations | id | contract_id (FK), ticket_id (FK) |
| HarvestAcceptance | harvest_acceptances | id | tenant_id, acceptance_number, customer_id, article_id, **5 NOT NULL boolean Felder** |
| HarvestAcceptancePosition | harvest_acceptance_positions | id | acceptance_id (FK) |
| HarvestAcceptanceLine | harvest_acceptance_lines | id | acceptance_id (FK) |
| Silo | silos | id | tenant_id, silo_number, warehouse_id (FK) |
| SiloLot | silo_lots | id | silo_id (FK), article_id (FK) |
| SiloLotMovement | silo_lot_movements | id | lot_id (FK) |
| SiloQualitySnapshot | silo_quality_snapshots | id | silo_id (FK) |
| DryingRuleSet | drying_rule_sets | id | tenant_id, name |
| DryingRuleLookupRow | drying_rule_lookup_rows | id | rule_set_id (FK) |
| DryingRuleFactorRange | drying_rule_factor_ranges | id | rule_set_id (FK) |
| AgrarSettlement | agrar_settlements | id | contract_id (FK) |
| AgrarSettlementDeduction | agrar_settlement_deductions | id | settlement_id (FK) |
| PriceAdjustmentRule | price_adjustment_rules | id | tenant_id |
| QualityProtocol | quality_protocols | id | tenant_id |
| DailyPrice | daily_prices | id | tenant_id, article_id (FK) |
| WarehouseTransfer | warehouse_transfers | id | from_warehouse_id (FK), to_warehouse_id (FK) |
| WarehouseTransferLine | warehouse_transfer_lines | id | transfer_id (FK) |
| StockCorrection | stock_corrections | id | warehouse_id (FK) |
| StockCorrectionLine | stock_correction_lines | id | correction_id (FK) |
| BinLocation | bin_locations | id | warehouse_id (FK) |
| PreparationList | preparation_lists | id | tenant_id |
| PreparationListLine | preparation_list_lines | id | list_id (FK) |
| PickList | pick_lists | id | tenant_id |
| PickListLine | pick_list_lines | id | list_id (FK) |
| ShippingUnit | shipping_units | id | tenant_id, sscc |
| NawaroPrintNotification | nawaro_print_notifications | id | tenant_id |
| NawaroContractSheet | nawaro_contract_sheets | id | tenant_id |
| NawaroContractSheetRow | nawaro_contract_sheet_rows | id | sheet_id (FK) |
| NawaroAreaSheet | nawaro_area_sheets | id | tenant_id |
| NawaroAreaSheetRow | nawaro_area_sheet_rows | id | sheet_id (FK) |
| NawaroRapsProfile | nawaro_raps_profiles | id | tenant_id |
| NawaroRapsCertificate | nawaro_raps_certificates | id | profile_id (FK) |
| NawaroRapsBalance | nawaro_raps_balances | id | profile_id (FK) |

---

## domain_agrar

Agrar-Produkte und Fachkunde.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| Saatgut | saatgut | id | tenant_id, sorte, art, kultur, tkm, keimfaehigkeit |
| SaatgutLizenz | saatgut_lizenzen | id | saatgut_id (FK) |
| Duenger | duenger | id | tenant_id, name, n_gehalt, p_gehalt, k_gehalt |
| DuengerMischung | duenger_mischungen | id | tenant_id |
| PSM | psm | id | tenant_id, name, zulassungsnummer, wirkstoff |
| Sachkunde | sachkunde | id | tenant_id, nachweis_nummer |
| Biostimulanz | biostimulanzien | id | tenant_id |
| NutrientComposition | nutrient_compositions | id | tenant_id |

---

## domain_erp

Kontenrahmen und Buchhaltung.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| Account | finance_accounts | id | tenant_id, account_number, account_name, account_type, **category (enum!)** |
| JournalEntry | finance_journal_entries | id | tenant_id, entry_number, entry_date, posting_date, status |
| JournalEntryLine | finance_journal_entry_lines | id | journal_entry_id (FK), account_id (FK), debit, credit |

> **ACHTUNG Account.category:** Muss einer der folgenden English-Enum-Werte sein:
> `current_assets`, `fixed_assets`, `current_liabilities`, `long_term_liabilities`, `equity`, `revenue`, `cost_of_goods_sold`, `operating_expenses`, `other_expenses`, `other_income`

---

## domain_finance

Selbstabrechnungen und Reklamationen.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| SelfBillingInvoice | self_billing_invoices | id | tenant_id, invoice_number, partner_id (FK→partner_id) |
| DisputeRecord | dispute_records | id | invoice_id (FK) |

---

## domain_portal

Kundenportal.

| Modell | Tabelle | PK | Wichtige Felder |
|--------|---------|-----|-----------------|
| CustomerContract | customer_contracts | id | tenant_id |
| CustomerPrePurchase | customer_pre_purchases | id | tenant_id |
| CustomerOrder | customer_orders | id | tenant_id |
| CustomerOrderItem | customer_order_items | id | order_id (FK) |
| CustomerOrderHistory | customer_order_histories | id | order_id (FK) |
