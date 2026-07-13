---
title: Datenbank-Migrations-Inventar
type: reference
audience: [entwickler, betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-13
version: 3.0.0
description: Vollständiges Inventar aller Alembic-Migrationsskripte mit Kurzbeschreibung. Beschreibungen sind aus den Datei-Docstrings extrahiert.
---

# Datenbank-Migrations-Inventar

> Automatisch generiert via `python scripts/generate_code_inventories.py`. **Nicht manuell bearbeiten.**

Vollständiges Inventar aller Alembic-Migrationsskripte mit Kurzbeschreibung. Beschreibungen sind aus den Datei-Docstrings extrahiert.

## Migrationsskripte

| Modul | Beschreibung |
|---|---|
| `001_initial_schema` | initial_schema |
| `05c409bd64c6_merge_bank_statements_and_kontrakte_` | merge bank_statements and kontrakte heads |
| `09e3b0da2b08_add_quality_protocols_daily_prices_self_` | add_quality_protocols_daily_prices_self_billing_dispute_nuts2_20260217 |
| `1368e3f15650_align_schema_with_domain__tables` | align schema with domain_* tables |
| `2012a7987e7f_add_finance_tables` | add_finance_tables |
| `31b00be545af_merge_wave106_and_kontrakt_klasse_` | merge_wave106_and_kontrakt_klasse_20260520 |
| `34a9ed912cd7_add_crm_tables_contacts_leads_` | Add CRM tables - contacts, leads, activities, betriebsprofile |
| `42e0e183bd0c_merge_heads_feed_qs_wf_cockpit_repair_` | merge heads: feed_qs_wf_cockpit_repair + pricing_staffelrabatt_artikel_m2m |
| `4601a09c0fc1_add_farmer_declaration_fields_to_psm` | Add farmer declaration fields to PSM |
| `4b6600ac3926_merge_heads` | merge heads |
| `4e8447ad429a_merge_gdpr_base` | — |
| `519e0d90cd66_add_sales_orders_table` | add_sales_orders_table |
| `59b4fa8420f2_add_crm_subservices_seed` | Add CRM sub-service seed tables with demo data. |
| `5ebb49807644_merge_heads` | merge_heads |
| `69a59fde9295_add_sales_offers_table` | Add sales_offers table |
| `6c69769c28cb_merge_all_heads` | merge_all_heads |
| `7f8529f27eb0_add_crm_activities_and_farm_profiles` | add_crm_activities_and_farm_profiles |
| `8f4c2b1d9e7a_merge_current_heads_20260319` | merge current heads for deterministic single-head bootstrap |
| `9efbf36742d6_add_contract_amendments_table` | add_contract_amendments_table |
| `a489a6a4a212_add_l3_target_tables` | add_l3_target_tables |
| `accruals_provisions_table_20260305` | Accruals and Provisions table (FIBU-CLS-03) |
| `add_agrar_domain_models_saatgut_duenger_psm_biostimulanzien` | Add agrar domain models: Saatgut, Duenger, PSM, Biostimulanzien |
| `add_amendment_templates_table_20260303` | add amendment_templates table and seed EHB/EB Nachtrag |
| `add_article_extended_fields_20260219` | Add extended article fields for Einheiten, Kennzeichnung, LH, Analyse, etc. |
| `add_article_fulltext_search_20260222` | Add PostgreSQL fulltext search for articles |
| `add_article_price_thresholds_20260303` | add_article_price_thresholds_20260303 |
| `add_article_search_fields_20260217` | Add missing article search fields for ArtikelSuchDialog. |
| `add_article_search_filter_discount_fields_20260219` | Add article search filter and discount fields. |
| `add_article_suppliers_documents_20260219` | Add article_suppliers and article_documents tables. |
| `add_audit_logs_and_accounting_periods_20260304` | FIBU-COMP-01 / FIBU-GL-05: domain_shared.audit_logs + finance_accounting_periods |
| `add_audit_logs_hash_chain_20260306` | Gap 010: Hash-Kette für domain_shared.audit_logs (Betriebsprüfungsfest) |
| `add_bank_statements_and_lines_20260304` | FIBU-AR-03 / FIBU-BNK-02: bank_statements und bank_statement_lines (Zahlungseingänge, Kontoauszugsimport) |
| `add_business_partners_tenant_id_20260219` | Add tenant_id to business_partners table for multi-tenant isolation. |
| `add_commodity_position_tables_20260304` | add_commodity_position_tables_20260304 |
| `add_config_service_and_jobs_20260218` | add_config_service_and_jobs_20260218 |
| `add_crm_customers_discount_if_missing` | Add discount column to crm_core_customers if present (Rabatt-Vorbelegung) |
| `add_customer_address_generated_columns_20260217` | add_customer_address_generated_columns |
| `add_customer_chefanweisung_20260217` | Add chefanweisung field to customers table. |
| `add_delivery_note_position_fields_20260217` | Add missing delivery note position fields. |
| `add_documents_json_table` | add_documents_json_table |
| `add_gobd_compliance_20260220` | Add GoBD Compliance Tables - Verfahrensdokumentation & Aufbewahrungsfristen |
| `add_harvest_acceptance_vat_modes_20260217` | add_harvest_acceptance_vat_modes_20260217 |
| `add_inventory_entities_stock_movements_and_inventory_counts` | Add inventory entities: stock movements and inventory counts |
| `add_journal_entries_currency_20260303` | journal_entries: Spalte currency ergänzen |
| `add_kontrakte_module_tables_20260303` | add_kontrakte_module_tables_20260303 |
| `add_l3_connect_gap_closure_tables` | Add L3-Connect gap closure tables |
| `add_lkw_annahme_queue_20260306` | add lkw_annahme_queue table (Gap 002) |
| `add_missing_bank_accounts_table_20260304` | — |
| `add_missing_domain_erp_finance_tables_20260304` | — |
| `add_missing_domain_ops_tables_20260304` | add missing domain_ops tables (compliance, enni, qs, zulassungen, sachkunde, saatgut, vvvo, disposition, foerderantraege, labor, marketing, zertifikate) |
| `add_number_ranges_table_20260417` | Add number_ranges table for configurable Debitor/Kreditor account numbering. |
| `add_nutrient_compositions_20260219` | Add nutrient compositions table and article linkage |
| `add_portal_tables_contracts_prepurchases_orders` | Add portal tables: contracts, prepurchases, orders |
| `add_procurement_p0_tables` | add procurement p0 tables |
| `add_schedules_config_json_20260218` | add_schedules_config_json_20260218 |
| `add_system_properties_subledger_20260218` | add_system_properties_subledger_20260218 |
| `add_vat_codes_tables_20260220` | Add VAT codes tables with audit trail |
| `add_weighing_ticket_article_notes_20260219` | add_weighing_ticket_article_notes_20260219 |
| `add_workflow_version_20260307` | Gap 011: workflow_version in workflow_status (versionierte Workflow Engine) |
| `admin_api_keys_20260215` | admin api key management |
| `admin_devices_output_profiles_20260215` | admin devices and output profile settings |
| `admin_mobile_repair_20260626` | ALEMBIC-MERGE-001: Admin-Mobile + Charge-Lineage Repair-Migration. |
| `admin_mobile_routing_connectors_20260215` | admin stations, routing, mobile scan and connectors |
| `admin_report_permissions_20260215` | admin self-service report permissions |
| `agent_proposals_persist_20260626` | OPERATOR-AGENT-002: Tabelle agent_proposals fuer persistente Agent-Proposals. |
| `agrar_contracts_initial_20260213` | add agrar contracts and allocations |
| `agrar_drying_rules_20260217` | add drying rule sets (lookup/factor/normalization) and audit snapshot on agrar_settlements |
| `agrar_drying_rules_audit_contract_dms_20260217` | add audit fields, contract/customer links, DMS ref to drying rule sets |
| `agrar_ernte_planung_20260520` | agrar_ernte_planung — domain_agrar.ernte_planung table for harvest overview |
| `agrar_maschinen_wetter_20260301` | Agrar Maschinenpark — Tabelle agrar_maschinen in domain_agrar |
| `agrar_partie_settlement_20260623` | DOM-AGRAR-004: agrar_partien, agrar_partie_links, agrar_trocknung_abrechnungen, agrar_selbstabrechnung_status_log |
| `agrar_settlement_campaign_reference_20260327` | AgrarSettlement campaign reference |
| `agrar_settlement_row_version_20260324` | AgrarSettlement optimistic locking: row_version |
| `agrar_settlements_initial_20260213` | add agrar settlements and deductions |
| `agrar_silo_lots_initial_20260213` | add agrar silo lots and quality snapshots |
| `agrar_wiegeschein_contract_link_20260213` | link weighing tickets to agrar contracts |
| `agrar_wiegeschein_fields_20260213` | add agrar weighing ticket fields |
| `agri_silo_cells_layout_20260619` | WM-AGRI-SILO-001: silo_cells layout_x/y + updated_at (Hofplan + Transfer) |
| `agri_silo_lot_link_20260619` | WM-AGRI-LOT-LINK: silo_cells.legacy_silo_id → domain_inventory.silos |
| `agri_silo_material_flow_20260612` | Agrar: Siloanlagen, Silozellen, Materialfluss-Knoten/Kanten (domain_inventory). |
| `agribusiness_farmers_table_20260525` | Agribusiness farmers table |
| `articles_image_url_20260322` | Add image_url to articles |
| `articles_master_fields_gap_83_20260215` | Close 8.3 article master-data field gaps. |
| `articles_model_alignment_20260214` | align domain_inventory.articles with Article model |
| `b38680c2f581_add_harvest_acceptance_with_nuts2_` | add_harvest_acceptance_with_nuts2_20260217 |
| `beleg_vordrucke_20260702` | admin: beleg_vordrucke — Druckvorlagen-Editor für Papier/PDF-Ausdrucke |
| `bp_merge_tab23_json_20260330` | Merge heads + domain_crm.business_partners.tab_23 JSONB (Tab-23 Stammdaten) |
| `business_partner_contacts_instructions_20260214` | Add business partner contacts and instructions tables. |
| `business_partner_discount_price_tables_20260214` | Add normalized discount and price agreement tables for business partners. |
| `business_partner_gap_811_normalized_20260214` | Close 8.11 business partner field gaps with normalized CRM tables. |
| `business_partner_item_constraints_20260214` | Add constraints and indexes for business partner discount/price items. |
| `business_partner_tab_23_24_25_20260214` | Add normalized Tab 23/24/25 structures for business partners. |
| `business_partners_customer_master_fields_20260214` | Add extended customer master fields to business_partners. |
| `c137c1d3ba3a_gdpr_requests_table` | — |
| `c4d5e6f7a8b9_add_harvest_acceptance_extensions_20260217` | add_harvest_acceptance_extensions_20260217 |
| `c68442f4d6dd_kontrakt_klasse_variante_enum` | kontrakt_klasse_variante_enum |
| `calendar_items_uix063` | UIX-063: Planungskalender Read-Model und ICS-Token. |
| `comp_artikel_sperren_20260618` | COMP-SPERR-001: Artikel-Sperr-Engine (artikel_sperren) |
| `compliance_pcn_audit_20260623` | DOM-COMPLIANCE-004: compliance_pcn_meldungen, pcn_status_log, vvvo/sachkunde registers, artikel_sperre_audit |
| `con_fixing_matif_20260611` | DOM-CON-004.2 — Fixierungs-Arbeitsraum + MATIF-Marktnotierung. |
| `con_reminder_20260611` | DOM-CON-004.3 — Kontraktmahnung (append-only Mahnungs-Log). |
| `con_settlement_storno_20260611` | DOM-CON-004.4 — Settlement-Übergabe + Storno (Bewegungs-Felder). |
| `config_openitems_tables_20260412` | Create connectors, reporting_units, schedules, and open_items tables in domain_shared |
| `connectors_lohn_quadriga_20260301` | Connectors: Lohn-Import-Läufe und Quadriga/Connector-Konfiguration (domain_erp) |
| `consignment_storage_fee_engine_20260215` | add consignment storage fee run and charge tables |
| `controlling_budget_abschluss_20260623` | DOM-CONTROLLING-004 — controlling_budgets, ist_werte, kst_abschluss. |
| `controlling_module_initial_20260215` | controlling module initial tables |
| `crm360_o2c_delivery_20260608` | Repair canonical sales delivery-note tables for CRM360 O2C. |
| `crm_campaigns_20260524` | CRM: campaign_templates, campaigns, campaign_recipients |
| `crm_capture_inbox_kim_20260609` | crm_capture_inbox — Klärfall-Inbox für nicht zuordenbare Auto-Captures (KIM) |
| `crm_consent_segments_20260305` | CRM: consent, segments and segment_members tables |
| `crm_contacts_ext_kim_s4_20260609` | crm_contacts_ext — Ansprechpartner-Erweiterung (KIM-S4) |
| `crm_customers_business_partner_id_20260404` | domain_crm.customers.business_partner_id — Verknüpfung CRM-Kunde ↔ Business Partner (Stammdaten) |
| `crm_customers_search_index_20260414` | domain_crm.customers — pg_trgm GIN-Indizes fuer schnelle Typeahead-Suche |
| `crm_gifts_kim_s3_20260609` | crm_gifts — Kunden-Präsente (KIM-S3) |
| `crm_kim_perf_indexes_20260612` | CRM/KIM Cockpit-Performance — fehlende Indizes. |
| `crm_merge_20260610` | crm_merge — Kunden-Zusammenführung (DOM-CRM-004.2) |
| `crm_notifications_kim_l3_backend_20260609` | crm_notifications — internes Benachrichtigungs-/Postfach-System fuer KIM (KIM-L3-BACKEND-001) |
| `crm_ownership_log_20260610` | crm_ownership_log — Übergabe-/Zuordnungs-Audit (DOM-CRM-004.3) |
| `crm_phase4_opportunity_links_20260305` | CRM Phase 4: Opportunity links to offer/order, loss_reason |
| `doc_artifact_version_20260611` | DOM-DOC-004.2 — Artefakt-Versionierung + Freigabe-Status. |
| `doc_followup_20260611` | DOM-DOC-004.3 — Bescheid/Rückmeldung + Wiedervorlage am Vorgang. |
| `doc_nachweisraum_lifecycle_20260623` | DOM-DOC-004 — Nachweisraum Dokument-Lifecycle + GoBD-Export Tabellen |
| `docflow_core_20260215` | docflow core tables and command idempotency |
| `docflow_create_idempotency_and_links_unique_20260301` | Docflow: Create-Idempotency-Tabelle + Docflow-Link UNIQUE (GoBD Schritt 3) |
| `docflow_pos_admin_dsfinvk_20260215` | docflow pos admin and dsfinvk export tables |
| `docflow_pos_tse_compliance_20260215` | docflow pos tse compliance table |
| `docflow_print_event_20260301` | Docflow: Druck/Export als Ereignis (printed_at, print_count) — GoBD Schritt 3 |
| `domain_schemas_baseline_20260409` | domain_* PostgreSQL-Schemas: idempotent anlegen (Baseline fuer ORM/create_all) |
| `driver_time_events_20260516` | add driver_time_events table |
| `e7238c2e17a1_merge_inventory_operations_and_` | merge inventory_operations and futtermittel heads |
| `eca81651f8ba_merge_multiple_heads` | Merge multiple heads |
| `einkauf_3wm_invoice_verification_20260613` | Einkauf 3-Wege-Match: domain_einkauf.invoice_verification Alembic migration. |
| `einkauf_bestellungen_dedupe_unique_20260407` | einkauf_bestellungen: Duplikate bereinigen + Unique-Index |
| `einkauf_domain_tables_20260227` | einkauf domain tables — Lieferanten, Kontrakte, Bestellungen, Bestellvorschlaege, ArtikelLagerParameter, LagerKonten, PalettenKonto, PfandKonto, FremdwarenEinlagerung |
| `einkauf_lieferschein_frachtauftrag_20260214` | Add procurement delivery note and freight order tables. |
| `einkauf_ls_opportunities_repair_20260626` | EINKAUF-LS-REPAIR-001: Einkauf-Lieferschein + Opportunities Repair-Migration. |
| `einkauf_missing_tables_20260305` | Einkauf: missing tables for RFQ, delivery advices, order confirmations, article groups, payment runs |
| `einkauf_rechnungseingang_workflow_audit_20260301` | Add workflow audit columns to einkauf_rechnungseingaenge (Prüfen/Freigeben/Verbuchen) |
| `ensure_chart_of_accounts_and_journal_entry_lines_20260303` | chart_of_accounts und journal_entry_lines anlegen (Nachlauf zu journal_entries) |
| `ensure_controlling_tables_20260304` | ensure controlling tables exist |
| `ensure_creditors_table_20260304` | ensure creditors table exists after multi-head merges |
| `ensure_finance_api_tables_20260413` | Ensure finance API tables exist on all upgrade paths |
| `ensure_journal_entries_table_20260303` | domain_erp.journal_entries und journal_entry_lines anlegen (GoBD) |
| `entity_notes_uix062` | UIX-062 entity notes for collab rail. |
| `esg_charge_footprint_uix082` | UIX-082 ESG charge footprint read-model. |
| `exchange_rates_compat_20260413` | Align exchange rate table with API contract |
| `external_mock_sessions_20260623` | EXTERNAL-MOCK-HARNESS-001: Mock-Session-Log fuer Dev/Test. |
| `f49745206879_add_zahlungslauf_kreditoren_table` | add zahlungslauf kreditoren table |
| `fachliche_vertiefung_wave10_20260521` | Fachliche Vertiefung Wave 10: Erlöskennziffern, Warengruppen, Zahlungsbedingungen |
| `fachliche_vertiefung_wave11_20260522` | Fachliche Vertiefung Wave 11: Partiestamm, Forderungsgruppen, Periodische Buchungen |
| `fachliche_vertiefung_wave12_20260522` | Fachliche Vertiefung Wave 12: Zu-/Abschlaggruppen/-klassen, Vertreterprovisionen |
| `fachliche_vertiefung_wave13_20260522` | Fachliche Vertiefung Wave 13: Zahlungsformulare, Zinsgruppen, Leergutarten |
| `fachliche_vertiefung_wave1_20260521` | Fachliche Vertiefung Wave 1: Massebilanz, Zinsabrechnung, Hofliste, Folgeartikel |
| `fachliche_vertiefung_wave2_20260521` | Fachliche Vertiefung Wave 2: Kontraktmengenzeitraum, Zu-Abschlaege, Rezepturgruppen |
| `fachliche_vertiefung_wave3_20260521` | Fachliche Vertiefung Wave 3: Kundenbanken, PIV, Stoffstromanteil, Skonto-Auszifferung |
| `fachliche_vertiefung_wave4_20260521` | Fachliche Vertiefung Wave 4: Rabattgruppen/klassen, Hausbankenstamm, Bestandteile, Frachttabellen |
| `fachliche_vertiefung_wave5_20260521` | Fachliche Vertiefung Wave 5: Vermehrungsvertrag, Vertreterstamm, Geschäftsjahre, Periodische Buchungen |
| `fachliche_vertiefung_wave6_20260521` | Fachliche Vertiefung Wave 6: Mengeneinheitengruppen, Artikelverpackung/Gebinde, Zahlungsmeldungen |
| `fachliche_vertiefung_wave7_20260521` | Fachliche Vertiefung Wave 7: Daueraufträge, Individualpreise, Stücklisten/Rezepturen |
| `fachliche_vertiefung_wave8_20260521` | Fachliche Vertiefung Wave 8: Rohwarengruppen, Rohware-Qualitäten, Zu-/Abschlag-Staffeln |
| `fachliche_vertiefung_wave9_20260521` | Fachliche Vertiefung Wave 9: Betriebsstätten/Filialen, Individuelle Artikelnummern, Versandprofile |
| `faf00a6bfc11_006_missing_tenant_indexes` | 006 missing tenant indexes |
| `fc82677c98b4_add_documents_tables` | add_documents_tables |
| `feed_chain_article_map_20260623` | FEED-CHAIN-004: Einzelfuttermittel → inventory.articles Mapping-Spalte. |
| `feed_chain_quality_lot_20260613` | FEED-CHAIN-003 — quality_lot_profiles + quality_release_decisions (domain_ops). |
| `feed_chain_verbrauch_20260612` | Futtermittel-Produktionsauftrag: Verbrauchs-Snapshot + Charge-Referenz. |
| `feed_produktion_lifecycle_20260623` | DOM-FEED-PROD-004 — Mischfutter Produktionsauftrag, Rezeptur, QS-Log |
| `feed_qs_wf_cockpit_repair_20260626` | FEED-QS-001 + WF-COCKPIT-002: Futtermittel-QS-Tabellen + domain_workflow sicherstellen. |
| `feldbuch_acker_waves_20260713` | Ackerschlagkartei wave fields (AS-W1/W2/W4/W5/W6). |
| `feldbuch_schlag_massnahme_20260226` | Add feldbuch_schlaege and feldbuch_massnahmen to domain_agrar |
| `ff7b1a7899b4_add_customer_inquiries_table` | add_customer_inquiries_table |
| `fibu_connector_asset_ledger_rename_20260301` | FIBU Connector: QUADRIGA → ASSET_LEDGER (geschützter Name entfernt) |
| `fibu_connector_framework_20260301` | FIBU Connector Framework: Profile, Runs, Run-Items (domain_erp) |
| `final_single_head_merge_20260626` | Final single-head merge: alle Repair-Wellen in einen Head zusammenführen. |
| `finance_agrar_sales_repair_20260626` | BULK-REPAIR-001: Finance + Agrar + Sales Batch-Repair-Migration Wave 11. |
| `finance_followup_exports_einkauf_uq_20260406` | finance_followup_exports + optional unique (tenant_id, bestellnummer) |
| `finance_hr_einkauf_repair_20260626` | FINANCE-HR-EINKAUF-REPAIR-001: Finance + HR + Einkauf Batch-Repair Wave 12. |
| `finance_sepa_ratenzahlung_20260623` | DOM-FINANCE-004: finance_sepa_mandate, sepa_batches, ratenzahlungsplaene, ratenzahlungsraten, mahnstufen_audit |
| `flow_spine_instances_20260326` | Flow Spine Instance persistence table |
| `flow_spine_lifecycle_20260417` | Extend flow spine instances with lifecycle state and timeline events |
| `fuhrpark_tables_speditionen_20260225` | Add Fuhrpark sub-tables and Speditionen Frachttarife |
| `fuhrpark_vertiefung_20260616` | Fuhrpark Vertiefung: Statushistorie, Schaeden, Bussgeld |
| `futtermittel_sorten_produktion_20260410` | Futtermittel-Stammdaten, Rezepte, Produktionsaufträge und Sortenregister |
| `gis_geojson_schlag_20260527` | GIS: geometry_geojson column on feldbuch_schlaege for polygon capture. |
| `gobd_archiv_erechnung_20260301` | GoBD: Archiv (document_artifacts) + E-Rechnung XML-Speicher |
| `gobd_aufbewahrungsfristen_20260301` | GoBD: domain_finance.aufbewahrungsfristen (operative Fristentabelle) |
| `gobd_journal_hash_chain_trigger_20260303` | GoBD Hash-Chain: Trigger für journal_entries (sequence_number, hash_prev, hash_current) |
| `grundfutteranalysen_20260419` | Grundfutter-Laboranalysen: LUFA/VDLUFA-Prüfberichts-Schema (GfE-2023) |
| `hr_applications_table_20260702` | hr: applications-Tabelle für Bewerbungs-Pipeline |
| `hr_personal_time_tracking_20260215` | hr personal time tracking tables |
| `hr_planning_tables_20260625` | HR planning tables — employee_time_profiles, calendar_events, payroll_exports, |
| `hr_training_onboarding_module_20260215` | hr training/qualification/onboarding module |
| `hrm_operations_gates_20260513` | HRM operations gates persistence and evidence workflow. |
| `hrm_zeiterfassung_abwesenheit_20260623` | DOM-HRM-004 — HRM Zeiterfassung, Abwesenheit, Arbeitszeitkonto |
| `inv_lot_depth_spec_p1_08` | SPEC-P1-08: Chargen-Tiefenmodell — Herkunft, Sperrgrund, QS-Status, received_at. |
| `inv_lot_trace_20260623` | DOM-INV-004.2/.4: inventory_lots + inventory_lot_movements + storno_ref column |
| `inventory_charge_lineage_20260215` | inventory charge lineage links |
| `inventory_operations_20260409` | Add source_document fields to stock_movements |
| `inventory_stock_movements_consignment_ownership_20260215` | add ownership/consignment fields to inventory_stock_movements |
| `inventory_stock_movements_l3_fields_20260214` | extend inventory_stock_movements with l3 migration fields |
| `job_runner_tables_repair_20260625` | Repair job runner tables for runtime sweep category A. |
| `journal_entries_document_type_20260408` | domain_erp.journal_entries: document_type ergaenzen (GoBD Belegart) |
| `journal_entries_unify_20260301` | Journal: Eine Tabelle für List + Connector (domain_erp.journal_entries) |
| `kontrakt_lifecycle_fixing_20260623` | DOM-CON-004 — Kontrakt Lifecycle, Fixing, Settlement Tabellen |
| `kostenrechnung_stammdaten_20260618` | Kostenrechnung: Kostenstellen-Stammdaten + Kostenarten |
| `kunden_ackerbau_profil_20260604` | Ackerbau-Bedarfsprofil je Betrieb (Fläche → Dünger/PSM/Saatgut). |
| `kunden_bp_bridge_20260601` | Kunden→BusinessPartner Identitäts-Brücke (Phase 1 Stammdaten-Konsolidierung). |
| `kunden_crm360_20260607` | KIM 360°-CRM Satellit: kunden_crm360 (L3-Vertriebsfelder). |
| `kunden_deprecate_legacy_cols_20260602` | Phase 2D Schritt 4: Altspalten in public.kunden deprecaten (nur Metadaten). |
| `kunden_domain_tables_20260602` | Phase 2D Schritt 2: schlanke Domänentabellen für public.kunden (additiv, leer). |
| `kunden_geo_20260604` | Autoritative Geokoordinaten je Kunde (Kartengenauigkeit). |
| `kunden_kaeufer_profil_20260604` | Käufergruppen-Profil je Betrieb (Einkaufsverhalten + realistischer Zielanteil). |
| `kunden_kontakte_20260603` | Kunden-Kontakte für das Kunden-Cockpit (Kontakthistorie + Wiedervorlage). |
| `kunden_lookup_adressen_20260602` | Phase 2D Schritt 3: kunden_lookup liest Adresse aus kunden_adressen. |
| `kunden_lookup_view_20260602` | kunden_lookup View für schnelle Kundenauswahl (Phase 2D, Decomposition). |
| `kunden_milchvieh_profil_20260602` | Milchvieh-Profil je Kunde (Herde/Leistung/Zellzahl) — Agrar-Anreicherung. |
| `kunden_produktgruppen_bezug_20260603` | Ist-Bezug je Betrieb × Produktgruppe (rollierend 12 M) — Durchdringungs-CRM. |
| `lkw_annahme_queue_article_reference_20260328` | LKW-Annahme-Queue article reference |
| `lkw_annahme_queue_klaerung_20260328` | LKW-Annahme-Queue Klaerungsdaten |
| `log_carrier_invoices_20260618` | LOG-FRACHT-001: Spediteur-Rechnungen (carrier_invoices) |
| `log_disposition_20260623` | DOM-LOG-004.2/.3: tour_disposition_checks + epod_settlements |
| `log_frachtbriefe_20260626` | LOG-FRACHTBRIEF-001: Frachtbrief-Tabelle fuer /api/v1/logistik/frachtbriefe. |
| `log_freight_tariff_storno_20260613` | Fracht-Tarif: Storno-Spalten (soft, auditierbar). |
| `log_logistics_core_20260612` | Logistik Kern-Tabellen (domain_logistics) — Alembic statt Runtime-DDL. |
| `log_touren_initial` | Verladung Domain Models Migration |
| `meldewesen_lifecycle_20260623` | DOM-MEL-004 — Meldewesen Lifecycle Tabellen (Intrastat/ELSTER/ATLAS) |
| `merge_agent_job_runner_20260626` | Merge Alembic heads: agent_proposals + job_runner_tables_repair. |
| `merge_crm_capture_pos_fiscal_20260609` | Merge CRM capture inbox and POS fiscal provider branches. |
| `merge_crm_ownership_prod_20260610` | Merge CRM ownership and production-readiness migration branches. |
| `merge_doc_proc_20260612` | Merge DOC- und PROC-Branch zu einem Alembic-Head. |
| `merge_dom004_feed_chain_20260623` | Merge parallel 2026-06-23 branches (DOM-*-004 wave + FEED-CHAIN-004). |
| `merge_driver_time_hrm_gates_20260517` | merge driver_time and hrm_gates heads |
| `merge_einkauf_log_agent_20260626` | Merge Alembic heads: einkauf_ls_opportunities_repair + merge_log_agent. |
| `merge_finance_warehouse_20260626` | Merge Alembic heads: finance_agrar_sales_repair + merge_warehouse_einkauf. |
| `merge_heads_20260522` | Merge: agrar_ernte_planung_20260520 + fachliche_vertiefung_wave13_20260522 |
| `merge_heads_docflow_agrar_einkauf_20260301` | Merge heads: Agrar, Einkauf RE-Workflow, Docflow GoBD Schritt 3 |
| `merge_heads_ops_and_erp_20260304` | merge heads: domain_ops (missing_ops) and domain_erp (finance tables) |
| `merge_l3c_and_procurement_indexes_20260213` | Merge Alembic heads l3c_gap_001 and optimize_procurement_indexes_20260213. |
| `merge_log_agent_20260626` | Merge Alembic heads: log_frachtbriefe + merge_agent_job_runner. |
| `merge_log_agri_heads_20260623` | Merge log_disposition and agri_silo_lot_link heads (DOM-INV-004 pre-step). |
| `merge_sales_orders_and_consignment_20260215` | merge heads sales_orders_items_shipping and consignment_storage_fee_engine |
| `merge_supply_production_readiness_20260610` | Merge supply-chain and production-readiness migration branches. |
| `merge_warehouse_einkauf_20260626` | Merge Alembic heads: warehouse_schema_repair + merge_einkauf_log_agent. |
| `merge_wave104_20260326` | Merge Wave 104 migrations with main head |
| `mobile_event_queue_20260619` | MOB-SYNC-001: Mobile Offline-Sync Event-Queue |
| `neuro_step_audit_einkauf_tenant_20260405` | neuro_step_audit_trace + einkauf_bestellungen.tenant_id |
| `neuroassist_state_graph_confidence_ledger_20260329` | Neuro State Graph + Confidence Ledger tables |
| `normalize_finance_hr_contracts_20260610` | Normalize finance account values and restore HR shift schema. |
| `offene_posten_fields_crud_20260214` | Extend offene_posten with L3 fields for full CRUD. |
| `ops_chargen_add_mhd_20260215` | add mhd to ops_chargen |
| `ops_chargen_qs_fields_20260214` | add qs fields to ops_chargen |
| `ops_domain_initial` | Operations Domain Models Migration |
| `ops_wave106_operations_crud_20260519` | Wave 106: Operations CRUD — Versicherungen, Wartung/Anlagen, Tankstelle/Zapfungen, |
| `ops_wave107_remaining_stubs_20260520` | ops_wave107_remaining_stubs — DB tables for critical in-memory stores |
| `optimize_procurement_indexes_20260213` | Optimize indexes for documents/procurement frequent query paths. |
| `pcn_meldungen_20260326` | PCN-Meldungen Persistenz-Tabelle (Wave 104 Gap-D) |
| `perf_indexes_apply_20260602` | Catch-up: Performance-Indizes auf bereits migrierten DBs anlegen. |
| `perf_indexes_multitenant_20260408` | perf: add missing database indexes for multi-tenant queries |
| `performance_indexes_20260526` | Performance indexes for high-frequency query patterns. |
| `pos_fiscal_providers_20260609` | POS fiscal provider abstraction and evidence tables. |
| `pos_tagesabschluss_lifecycle_20260623` | DOM-POS-004 — POS Tagesabschluss Lifecycle Tabellen |
| `pricing_staffelrabatt_artikel_m2m_20260702` | pricing: staffelrabatte <-> artikel als many-to-many |
| `pricing_staffelrabatte_20260701` | pricing: staffelrabatte Tabelle anlegen |
| `proc_bestellung_wareneingang_20260623` | DOM-PROC-004: proc_bestellung_status_log, proc_wareneingaenge, proc_rechnungspruefungen |
| `proc_ers_credit_20260611` | Procurement ERS credit notes (Gutschriftsverfahren). |
| `proc_follow_up_20260611` | Procurement match follow-up actions (append-only). |
| `proc_rfq_20260611` | RFQ tables for procurement quotation process. |
| `proc_three_way_invoice_20260611` | Ensure finance_erechnungen for procurement three-way match. |
| `prod_fibu_journal_ref_20260618` | PROD-FIBU-001: fibu_journal_ref auf ProduktionsAuftrag |
| `produktgruppen_kaeufer_20260604` | Käuferlogik je Produktgruppe + echte Signal-Herkunft. |
| `rations_feeding_control_20260711` | Persisted feeding-control logs (DLG 01/2025 F1). |
| `rations_integrations_20260712` | Rations integration import journal. |
| `rations_zugang_dsgvo_20260420` | rations_zugang DSGVO access control table |
| `repair_article_dangerous_goods_20260610` | Repair dangerous-goods columns required by the Article runtime model. |
| `repair_business_partner_contract_20260610` | Complete the canonical business-partner runtime contract. |
| `repair_core_schema_drift_20260609` | Repair schema objects missing from databases stamped past older migrations. |
| `repair_customer_contract_20260610` | Complete the canonical CRM customer runtime contract. |
| `repair_runtime_contract_columns_20260610` | Repair runtime columns required by current ORM and domain checks. |
| `repair_runtime_model_alignment_20260610` | Align fresh installations with current CRM and article runtime models. |
| `repair_runtime_schema_20260610` | Bring runtime models that predate Alembic under the migration contract. |
| `runtime_sweep_repair_20260702` | RUNTIME-SWEEP-REPAIR-001: Fresh-DB-Drift schliessen (SPEC-P0-02). |
| `sales_ab_preisabweichung_20260623` | DOM-SALES-004: sales_ab_status_log, lieferschein_close_log, sales_preisabweichungen |
| `sales_angebot_auftrag_tables_20260225` | Add sales_offers, sales_offer_items, sales_orders, sales_order_items to domain_crm |
| `sales_credit_returns_pricing_20260305` | Sales: credit notes, returns, price list items |
| `sales_delivery_notes_branches_audit_20260216` | Add sales delivery notes, branches, and audit attestations tables. |
| `sales_delivery_storno_20260611` | DOM-SALES-004.4 — Lieferungs-Storno (Grund am Lieferschein). |
| `sales_o2c_link_20260610` | sales O2C-Link — Auftrag→Lieferschein-Verknüpfung (DOM-SALES-004.1) |
| `sales_orders_items_shipping_20260215` | Add sales_order_items relation and shipping_method on sales_orders. |
| `seed_anlage1_abzugstabelle_template_20260303` | seed Anlage 1 (Abzugstabelle Qualität) amendment template |
| `seed_default_tenant_20260214` | seed default tenant for foreign-key constrained domain tables |
| `streckengeschaefte_table_merge_20260424` | Streckengeschaefte persistent (public.streckengeschaefte); merge mehrerer Alembic-Heads. |
| `supply_chain_events_20260610` | supply_chain_events — append-only Ketten-Ereignis-Log (DOM-SUPPLY-004.2) |
| `tapi_calls_20260603` | TAPI/Telefonie — eingehende Anrufe für Click-to-Customer-Popup. |
| `user_screen_overlays_uix071` | UIX-071 user screen overlays. |
| `ustva_voranmeldungen_20260527` | UStVA Voranmeldungen Tabelle (§ 18 UStG ELSTER-Übertragung). |
| `warehouse_schema_repair_20260626` | WAREHOUSE-REPAIR-001: domain_inventory.warehouses fehlende Spalten nachziehen. |
| `warehouse_wms_structure_20260517` | WMS warehouse zones, bins, bin_stock, pick_lists and pick_list_lines |
| `wave3_wf_trigger_log_20260618` | wave3: wf_trigger_log + bank_statements + bank_statement_lines + waagen_quittungen |
| `wf_cockpit_persist_20260625` | WF-COCKPIT-PERSIST-001: Persistente Workflow-Cockpit-Tabellen. |
| `whatsapp_bestell_inbox_20260603` | WhatsApp Bestell-Inbox — eingehende Freitext-Bestellungen + AI-Extraktion. |
| `wms_material_flow_stock_link_20260619` | WMS-FLOW-001: silo_cells current_stock_kg + BAB-Umlagen-Tabelle |
| `wms_warehouse_aisles_20260612` | WMS: Lager-Gang (warehouse_aisles) + optionale Zuordnung auf warehouse_bins. |
