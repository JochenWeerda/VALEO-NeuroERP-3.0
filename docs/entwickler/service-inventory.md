---
title: Service-Inventar
type: reference
audience: [entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-10
version: 3.0.0
description: Vollständiges Inventar aller Backend-Service-Module mit Kurzbeschreibung. Beschreibungen sind aus den Modul-Docstrings extrahiert.
---

# Service-Inventar

> Automatisch generiert via `python scripts/generate_code_inventories.py`. **Nicht manuell bearbeiten.**

Vollständiges Inventar aller Backend-Service-Module mit Kurzbeschreibung. Beschreibungen sind aus den Modul-Docstrings extrahiert.

## Service-Module

| Modul | Beschreibung |
|---|---|
| `accounting_export_profiles` | Canonical tax-advisor export profiles. |
| `action_execution_mutations` | Nachgelagerte Schreibpfade fuer ActionExecutionService (Wave-17/18). |
| `admin_core_service` | Service layer for the core admin domain. |
| `agrar_contract_service` | Service layer for Agrar contract management and allocation logic. |
| `agrar_drying_rule_service` | Service layer for Agrar Drying Rule Sets, Lookup Rows, and Factor Ranges. |
| `agrar_partie_aggregate_service` | DOM-AGRAR-004.2 — Partie-Aggregations-Service (Ernteannahmen → Partie). |
| `agrar_selbstabrechnung_lifecycle_service` | DOM-AGRAR-004.4 — Selbstabrechnung-Lifecycle-Service (Status-Maschine + Storno). |
| `agrar_settlement_service` | Service layer for Agrar self-billing settlements (AGRAR-SET-01). |
| `agrar_trocknung_abrechnung_service` | DOM-AGRAR-004.3 — Trocknungsabrechnung-Service. |
| `agri_lot_link_booking_service` | WM-AGRI-LOT-LINK-001: Waage/WE-Lot in Materialfluss-Silozelle buchen. |
| `agri_material_flow_trace_integration` | WM-AGRI-CHAIN-002 — Materialfluss ↔ Lieferketten-Log + Outbox. |
| `agri_qs_workflow_service` | WM-AGRI-QS-003: QS-Workflow fuer Silo-Lots mit Audit-Rueckkopplung. |
| `agri_silo_lot_link_service` | WM-AGRI-LOT-LINK — Sync silo_lots (DOM-SUPPLY) ↔ silo_cells (Materialfluss-Graph). |
| `agri_silo_material_flow_service` | Agrar-Siloanlagen und Materialfluss (Knoten/Kanten) — WM-AGRI-SILO-001. |
| `agribusiness_service` | Service layer for compat agribusiness/setup/management domain routes. |
| `ai_data_classification_service` | P2.3 — Lokale KI-Datenklassen fuer VALEO NeuroERP. |
| `ai_engineering_metrics_service` | P2.2 — Produktivitaetsmetriken fuer AI-Engineering in VALEO. |
| `annahme_service` | Service layer for compat Annahme (goods intake) and LKW queue routes. |
| `ap_invoice_kernel_posting` | Kernel PostAPInvoice: gleiche Fachlogik wie POST /ap/invoices/{id}/post, aber ohne |
| `archive_service` | Archive Service |
| `article_image_enrichment` | Article Image Enrichment Service |
| `articles_service` | Helper functions for the Articles domain. |
| `atlas_customs_service` | ATLAS Zollausfuhr Service — Implementierung nach Zollkodex der Union (UZK). |
| `audit_hardening` | Audit Hardening Service — NC-D1/D2 |
| `bedarfsdeckung_service` | Bedarfsdeckungs-Cockpit (Durchdringungs-CRM) — „Die Lücke ist das Vertriebsobjekt". |
| `business_partner_service` | Service layer for BusinessPartner aggregate management. |
| `calendar_projection_service` | UIX-063 planning calendar projections. |
| `case_management` | Case Management Service — NC-08 |
| `closing_checklists_service` | Schemas and helpers for the Closing Checklists domain (FIBU-CLS-01). |
| `command_handlers_finance` | Domain-Mutationen fuer Process-Kernel-Commands (Finance / AP). |
| `command_handlers_procurement` | Domain-Mutationen fuer Process-Kernel-Commands (Einkauf). |
| `compat_helpers` | Shared helpers for compat service classes. |
| `compensation_engine` | Compensation Engine — NC-006 |
| `competitor_monitor` | Competitor Price & Image Monitoring Service |
| `compliance_pcn_lifecycle_service` | DOM-COMPLIANCE-004.2 — PCN-Meldung Lifecycle Service (Status-Maschine). |
| `compliance_service` | Helpers and PDF builder for the Compliance domain. |
| `compliance_sperre_audit_service` | DOM-COMPLIANCE-004.4 — Artikel-Sperre Audit-Trail Service (append-only). |
| `compliance_vvvo_sachkunde_service` | DOM-COMPLIANCE-004.3 — VVVO-Prüfung + Sachkunde-Ablauf-Monitoring. |
| `connector_config` | Per-Tenant-Konfiguration der Auto-Capture-Connectoren (STT + IMAP). |
| `consent_engine` | Consent Engine — NC-004 |
| `contract_engagement_service` | Kontrakt-Engagement & Kontraktmahnung (DOM-CON-004.3). |
| `contract_fixing_service` | Kontrakt-Fixierung & MATIF-Bewertung (DOM-CON-004.2). |
| `contract_fulfillment_service` | Kontrakt-Erfüllungsstand (DOM-CON-004). |
| `contract_settlement_service` | Kontrakt-Settlement-Übergabe & Storno (DOM-CON-004.4). |
| `controlling_abweichung_service` | DOM-CONTROLLING-004.3 — Plan/Ist-Abweichungsanalyse Service. |
| `controlling_budget_lifecycle_service` | DOM-CONTROLLING-004.2 — Budget Lifecycle Service (Statusmaschine). |
| `controlling_kostenstellen_abschluss_service` | DOM-CONTROLLING-004.4 — Kostenstellen-Abschluss Service. |
| `controlling_service` | Service layer for Controlling module (KPIs, Dashboards, Widgets, Timeseries, Actions). |
| `crm_auto_capture_service` | Automatische Kontakt-Erfassung (KIM-AUTOCAPTURE). |
| `crm_capture_inbox_service` | Klärfall-Inbox für nicht zuordenbare Auto-Captures (KIM). |
| `crm_compat_service` | Service layer for compat CRM domain routes. |
| `crm_contact_ext_service` | Ansprechpartner-Erweiterung (KIM-S4): Werbe-/Marketingpräferenzen + Pseudonymisierung. |
| `crm_duplicate_service` | Kunden-Dubletten-Erkennung (DOM-CRM-004). |
| `crm_gift_service` | Kunden-Präsente (KIM-S3) — kundenbezogene Geschenke-PR mit Jahr-/AP-Filter. |
| `crm_kontakt_service` | Kunden-Kontakte (Kontakthistorie + Wiedervorlage) für das Kunden-Cockpit. |
| `crm_kunden_map_service` | CRM-Kundenkarte — alle Kunden (public.kunden) als GeoJSON-POIs. |
| `crm_lead_gen_service` | CRM Lead-Generierung — region-universale Lead-Kandidaten aus offenen Quellen. |
| `crm_merge_service` | Kunden-Zusammenführung (DOM-CRM-004.2). |
| `crm_notification_service` | CRM-Benachrichtigungen — internes In-App-Postfach + externe Fachberater-Mail. |
| `crm_ownership_service` | Kunden-Ownership (DOM-CRM-004.3) — Zuordnung & Übergabe. |
| `customer_sales_eligibility` | CRM-Kunde ↔ Business-Partner: Sperr- und Lieferfähigkeit für Verkaufsbelege. |
| `customer_service` | Service layer for CRM Customer management (crm-core + monolith bridge). |
| `doc_nachweisraum_lifecycle_service` | DOM-DOC-004.2 — Dokumenten-Nachweisraum Lifecycle (Upload/Freigabe/GoBD). |
| `docflow_artifact_service` | Artefakt-Upload, Versionierung & Freigabe (DOM-DOC-004.2). |
| `docflow_evidence_service` | Dokument-Nachweisraum (DOM-DOC-004) — GoBD-Artefakt-/Vorgangs-Sicht. |
| `docflow_followup_service` | Bescheid/Rückmeldung & Wiedervorlage am Vorgang (DOM-DOC-004.3). |
| `docflow_gobd_service` | GoBD-Exportpaket & DMS-/Paperless-Liveprobe (DOM-DOC-004.4). |
| `docflow_service` | Service layer for the canonical Docflow command pipeline (DOCFLOW-P0-01..03). |
| `einkauf_compat_service` | Service layer for compat einkauf domain routes. |
| `einvoice_generator` | E-Rechnung XRechnung/ZUGFeRD Generator (EN 16931). |
| `eric_submission_service` | ELSTER ERiC Submission Service für eBilanz-Übertragung. |
| `esg_footprint_service` | ESG-CO2e-Fussabdruck je Charge (UIX-082) — auditierbarer Berechnungskern. |
| `event_schema_registry` | Event Schema Registry — NC-G1 |
| `external_mock_harness_service` | EXTERNAL-MOCK-HARNESS-001 — Simulierte Responses fuer externe Systeme. |
| `fast_track` | Fast Track Classifier + Router — NC-E1/E2 |
| `feed_inventory_link_service` | FEED-CHAIN-004: Einzelfuttermittel ↔ domain_inventory.articles + Bewegungsbelege. |
| `feed_production_chain_service` | Produktion→Charge-Durchstich Mischfutter (FEED-CHAIN-001) — durchgängig. |
| `feed_produktion_lifecycle_service` | DOM-FEED-PROD-004.2 — Mischfutter Produktions-Lifecycle (Rezeptur→Charge→Freigabe). |
| `feed_rezeptur_service` | DOM-FEED-PROD-004.3 — Rezeptur-Verwaltung (Freigabe + Versionierung). |
| `finance_clearing_service` | Zahlungseingang / OP-Auszifferung (DOM-FIN-004.3). |
| `finance_closing_service` | FIN-ABSCHLUSS-STUBS-001 — GoBD-taugliche Periodenabschluss-Fachlogik. |
| `finance_datev_service` | DATEV-Export (DOM-FIN-004.5). |
| `finance_dunning_service` | Mahnlauf & Mahnstufen-Eskalation (DOM-FIN-004.2). |
| `finance_mahnstufe_service` | DOM-FINANCE-004.4 — Mahnstufen-Eskalation-Trail Service (append-only). |
| `finance_op_service` | Offene-Posten-Cockpit / OP-Aging (DOM-FIN-004). |
| `finance_period_service` | Periodenabschluss & Storno-Konsistenz (DOM-FIN-004.4). |
| `finance_ratenzahlung_service` | DOM-FINANCE-004.3 — Ratenzahlungsplan-Lifecycle Service. |
| `finance_read_model_service` | Service layer for Finance Read-Models (cockpit KPI projections). |
| `finance_sepa_service` | DOM-FINANCE-004.2 — SEPA-Zahlungsträger Service (Mandate + Batch-Export). |
| `finance_transaction_service` | Service layer for finance journal entry and posting operations. |
| `fints_connector` | FinTS/HBCI Bank-API Connector (§ 25a KWG, PSD2). |
| `gap_analytics` | GAP-Analytik: Trend-/Wachstumsabschätzung aus mehreren Jahrgängen. |
| `gap_pipeline` | GAP (Gemeinsame Agrarpolitik) ETL-Engine. |
| `gap_pipeline_service` | Service layer for the GAP (Gemeinsame Agrarpolitik) ETL pipeline endpoints. |
| `gap_progress` | In-process job- and progress-tracking for the GAP ETL pipeline. |
| `geo_pipeline` | Geo-Pipeline – Betriebsadressen → Koordinaten für den Außendienst-Viewer. |
| `guardrails` | Guardrails Service — NC-C3 |
| `harvest_acceptance_service` | Service layer for Harvest Acceptance (Ernte-Annahme) CRUD operations. |
| `hrm_abwesenheit_service` | — |
| `hrm_zeiterfassung_service` | DOM-HRM-004.2 — HRM Zeiterfassung Lifecycle (Einstempeln/Ausstempeln/Korrektur). |
| `integration_bootstrap` | — |
| `interaction_state_manager` | Interaction State Manager — NC-002 |
| `inventory_compat_service` | Service layer for compat inventory (lager) and futter domain routes. |
| `inventory_correction_service` | DOM-INV-004.4 — Bestandskorrektur-Storno-Service. |
| `inventory_count_close_service` | DOM-INV-004.3 — Inventur-Differenzbeleg-Service. |
| `inventory_lot_trace_service` | DOM-INV-004.2 — Chargen-/MHD-Traceability Service (FEFO). |
| `ist_aggregation_service` | Echte Ist-Belegaggregation für das Bedarfsdeckungs-Cockpit. |
| `kaeufer_klassifikator` | Austauschbare Käufergruppen-Klassifikatoren (regelbasiert / KI). |
| `kaeufer_signal_service` | Aggregiert echte Verhaltenssignale je Betrieb (und je Produktgruppe) aus den |
| `kaeufergruppe` | Käufergruppen-Modell + realistisch gewinnbare Bedarfslücke (Durchdringungs-CRM). |
| `knowledge_store` | Knowledge Store — NC-06 |
| `kontrakt_fixing_service` | DOM-CON-004.3 — Kontrakt Preis-Fixing Service (MATIF/Kassamarkt). |
| `kontrakt_lifecycle_service` | DOM-CON-004.2 — Kontrakt-Lifecycle Service (Statusmaschine + Fixing + Settlement). |
| `kontrakt_movement_sync` | Automatic Kontrakt-Movement synchronization. |
| `kontrakt_position_service` | Rohwaren-Positionsmonitor: Long/Short-Berechnung pro Artikel. |
| `kontrakt_settlement_service` | DOM-CON-004.4 — Kontrakt Settlement Service (Abrechnung + Storno). |
| `kontrakte_adapters` | — |
| `kontrakte_service` | — |
| `kunden_backfill` | Phase 2D Schritt 3: Backfill public.kunden -> Domänensatelliten. |
| `kunden_geocode_service` | Befüllt public.kunden_geo mit präzisen Koordinaten je Kunde. |
| `kunden_merge` | Kunden/Business-Partner-Merge — Dry-Run / Reconciliation (Phase 2A). |
| `lieferschein_pdf` | Lieferschein PDF Generator |
| `lkv_pipeline` | LKV-Pipeline – Download der LKV-Weser-Ems-Jahresberichte (Milchleistungsprüfung). |
| `llm_gateway` | Anbieterunabhängiges LLM-Gateway. |
| `logistics_disposition_service` | DOM-LOG-004.2 — Tour-Dispositions-Service (Kapazität + Zeitfenster). |
| `logistics_epod_service` | DOM-LOG-004.3 — ePOD-Lifecycle-Service (Ablieferungsbeleg → Settlement). |
| `lohn_service` | Payroll calculation and closeout contracts. |
| `mail_ingest_service` | Server-seitiger IMAP-Mail-Ingest (per Tenant konfiguriert). |
| `mask_action_runtime_service` | SPEC-P1-04 — gemeinsame ActionRuntime für Mask-CommandEndpoints. |
| `mask_rollout_summary_service` | Data service for batch mask rollout screen-summary endpoints (Waves 42–51). |
| `mcp_tool_registry_service` | MCP-ERP-TOOLS-001 — Rollenbasierter ERP-Tool-Katalog fuer Agent-Zugriff. |
| `meldewesen_lifecycle_service` | DOM-MEL-004.2 — Meldewesen Lifecycle (Intrastat/ELSTER/ATLAS — extern gegated). |
| `milchvieh_crosssell_service` | Cross-Sell-Auswertung Milchvieh: Hygiene-Bedarf + Kraftfutter-Potenzial. |
| `mobile_sync_service` | MOB-SYNC-001: Mobile Offline-Sync Service. |
| `nats_event_handlers` | NC-G3 -- Core NATS event handlers. |
| `neuro_decision_protocol` | Neuro Decision Protocol — NC-D3 |
| `neuro_simulation_engine` | Neuro Simulation Engine — NC-005 |
| `neuro_tool_broker` | Neuro Tool Broker - NC-A6 / NC-A7 |
| `neuro_tool_execution` | Neuro Tool Execution Service - NC-A7 |
| `neuro_verification_engine` | Neuro Verification Engine — NC-001 / Wave 2 |
| `notification_service` | Notification Service |
| `number_range_service` | Configurable number range service for Debitor/Kreditor accounts and partner numbers. |
| `numbering_service` | Numbering Service |
| `numbering_service_pg` | Numbering Service (PostgreSQL) |
| `o2c_chain_service` | Order-to-Cash-Kette (DOM-SALES-004) — Angebot → Auftrag → Lieferschein → Rechnung. |
| `operator_agent_service` | OPERATOR-AGENT-001 — ERP-Operator-Agent: Proposal + kontrollierte LOW-Schreibaktionen. |
| `pdf_service` | PDF Service |
| `pdf_template_service` | PDF Template Service |
| `personal_service` | Service layer for HR/Personal domain queries (Mitarbeiter, Zeiterfassung, Abwesenheiten). |
| `pii_detector` | PII Detector + Masker — NC-C1/C2 |
| `policy_registry` | Policy Registry — NC-G4 |
| `policy_service` | Policy Service - Policy-Framework für Alert-Actions |
| `portal_compat_service` | Service layer for compat portal domain routes (supplier/customer portal). |
| `portal_intelligence_service` | — |
| `portal_interessent_service` | — |
| `portal_lohndienst_service` | — |
| `portal_preisspiegel_service` | — |
| `pos_accounting_service` | — |
| `pos_compat_service` | Service layer for compat POS domain routes. |
| `pos_fiscal_document_service` | — |
| `pos_tagesabschluss_service` | DOM-POS-004.2 — POS Tagesabschluss Lifecycle (Z-Bon, TSE-Signatur, DSFinV-K-Export). |
| `position_guard_service` | No-Speculation Guard Service for Commodity Positions. |
| `position_service` | Commodity Position Calculation Service. |
| `position_snapshot_service` | Commodity Position Snapshot Service (optional cache for matrix performance). |
| `proc_bestellung_lifecycle_service` | DOM-PROC-004.2 — Bestellung Lifecycle Service (Statusmaschine). |
| `proc_rechnungspruefung_service` | DOM-PROC-004.4 — Rechnungsprüfung + ERS (Evaluated Receipt Settlement) Service. |
| `proc_wareneingang_service` | DOM-PROC-004.3 — Wareneingangs-Buchung + QS Service. |
| `process_map_service` | P2.1 — Workflow-Designer / Prozesskarte fuer VALEO ERP-Prozessketten. |
| `procurement_match_service` | Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004). |
| `procurement_service` | Service layer for Einkauf/Procurement domain. |
| `prompt_pack_registry` | Prompt Pack Registry -- NC-G5 |
| `purchase_order_service` | Service layer for purchase-order compat routes. |
| `qs_charge_service` | QS-CHARGE-001: Qualitätsprotokoll → Preisabschlag-Kalkulation. |
| `report_print_service` | Report and print contracts for traceability, weighing tickets and labels. |
| `rfq_service` | RFQ-Service (Anfrage → Angebot → Zuschlag → Bestellung). |
| `sales_ab_lifecycle_service` | DOM-SALES-004.2 — Auftragsbestätigung Lifecycle Service (Statusmaschine). |
| `sales_credit_service` | Kreditlimit-Prüfung & Rechnungs-/Billing-Status im O2C-Kontext (DOM-SALES-004.3). |
| `sales_lieferschein_close_service` | DOM-SALES-004.3 — Lieferschein-Closing-Flow Service. |
| `sales_match_service` | Auftrag-↔-Lieferschein-Positions-Match (DOM-SALES-004.2). |
| `sales_posting_service` | Service for creating FIBU journal entries along the Auftrag → Lieferschein → Rechnung chain. |
| `sales_preisabweichung_service` | DOM-SALES-004.4 — Preisabweichungs-Prüfung + Eskalation/Freigabe Service. |
| `sales_storno_service` | Lieferungs-Storno & Gutschrift-Übersicht (DOM-SALES-004.4) — durchgängig. |
| `scheduler_service` | Scheduler Service |
| `secrets_vault` | Secrets Vault Service — NC-15 |
| `security_observability` | Central observability for security-relevant block and violation events. |
| `semantic_e2e_chain_service` | SEMANTIC-E2E-MATRIX-001 — Semantische Prozessketten-Validierung. |
| `settlement_approval_service` | Approval workflow service for Agrar settlements (AGRAR-SET-FREIGABE). |
| `settlement_drying_service` | Drying calculation service for Agrar settlements (AGRAR-SET-TROCKNUNG). |
| `settlement_pdf_service` | PDF generation and GoBD archiving for Agrar settlement self-billing documents. |
| `silo_rule_engine_service` | WM-SILO-RULE-ENGINE-001 — Automatische Zielzellen-Vorschlaege fuer Einlagerung. |
| `stt_client` | Speech-to-Text-Client (anbieterunabhängig, OpenAI-kompatibel). |
| `studio_validation` | SD-Studio Draft-Validierung (UIX-090) — harte Sicherheitsregeln. |
| `supply_chain_event_service` | Append-only Ketten-Ereignis-Log + kanonischer Übergabestatus (DOM-SUPPLY-004.2). |
| `supply_chain_lot_service` | Lager-Lot-Folgeaktionen mit Abweichungsgrund (DOM-SUPPLY-004.3). |
| `supply_chain_trace_service` | Supply-Chain-Traceability (DOM-SUPPLY-004) — durchgängige, prüfbare Kette. |
| `sync_scheduler` | Advanced Sync Scheduler Service |
| `tse_fiskaly_service` | Compatibility facade for the canonical fiscalization provider layer. |
| `vies_service` | VIES Service |
| `voice_adapter` | Voice Adapter Layer — NC-003 |
| `warehouse_service` | — |
| `webshop_integration_service` | Service layer for B2B webshop order imports. |
| `wf_cockpit_nats_projector` | WF-COCKPIT-PERSIST-001 — NATS-JetStream-Projector fuer Workflow-Cockpit. |
| `wf_cockpit_persist_service` | WF-COCKPIT-PERSIST-001 — DB-backed Workflow-Cockpit-Service. |
| `wf_trigger_service` | WF-TRIGGER-001: Status-Trigger → Folgeaktion-Automationen. |
| `whatsapp_agent_service` | WA-AGENT-001 — WhatsApp Bestellagent |
| `whatsapp_intake_service` | WhatsApp Bestell-Inbox: Freitext-Bestellungen → strukturierter Beleg-Entwurf. |
| `whatsapp_notify_service` | WA-NOTIFY-001 — Ausgehende WhatsApp-Benachrichtigungen |
| `workflow_cockpit_service` | Workflow cockpit service for operational process visibility. |
| `workflow_guards` | Workflow Guards |
| `workflow_service` | Workflow Service (Gap 011: versionierte Definitionen). |
