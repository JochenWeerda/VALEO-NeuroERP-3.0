---
title: API-Endpoint-Inventar
type: reference
audience: [entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-10
version: 3.0.0
description: Vollständiges Inventar aller FastAPI-Endpoint-Module mit Kurzbeschreibung. Beschreibungen sind aus den Modul-Docstrings extrahiert.
---

# API-Endpoint-Inventar

> Automatisch generiert via `python scripts/generate_code_inventories.py`. **Nicht manuell bearbeiten.**

Vollständiges Inventar aller FastAPI-Endpoint-Module mit Kurzbeschreibung. Beschreibungen sind aus den Modul-Docstrings extrahiert.

## Endpoint-Module

| Modul | Beschreibung |
|---|---|
| `accounting_periods` | Accounting Period Management API |
| `accounts` | Finance Account management endpoints |
| `accruals_provisions` | Accruals and Provisions API |
| `activities` | CRM activity endpoints proxied via crm-core. |
| `admin_core` | Core admin endpoints used by the settings/admin frontend. |
| `admin_devices` | Admin device mapping and output/form settings. |
| `admin_dms` | Admin DMS Endpoints |
| `admin_mobile` | Admin endpoints for stations, routing, scan profiles, mobile devices and connectors. |
| `admin_monitoring` | Admin monitoring endpoints. |
| `admin_pos` | Admin POS/TSE settings and DSFinV-K exports. |
| `admin_reporting` | Admin CRUD for self-service report permissions. |
| `admin_suite` | Read-only Admin Suite production-readiness aggregation. |
| `agent_context_api` | — |
| `agent_tool_contracts` | External agent tool contracts. |
| `agents` | AI Agents API |
| `agrar_contracts` | Agrar contract endpoints — thin handlers, all logic in AgrarContractService. |
| `agrar_drying_rules` | Agrar Drying Rule Sets, Lookup Rows, and Factor Ranges — CRUD endpoints. |
| `agrar_feldbuch` | Agrar Feldbuch — ERP-interne Endpoints (Landhandel-Mitarbeiter) |
| `agrar_maschinen` | Agrar Maschinen — CRUD für Maschinenpark (Landhandel + Lohnunternehmer) |
| `agrar_p0` | — |
| `agrar_settlements` | Agrar self-billing settlements with deduction and posting workflow (AGRAR-SET-01). |
| `agrar_varieties` | Agrar Sorten/Varieties API fuer Ernte-Annahme. |
| `agrar_wetter` | Agrar Wetter — Wetter-Proxy für BrightSky (DWD) + Open-Meteo (ICON-D2) |
| `agri_lot_link_booking` | WM-AGRI-LOT-LINK-001 endpoint: Annahme/Waage-Lot in Silozelle buchen. |
| `agri_plc_stub` | WM-AGRI-PLC-005 — PLC/OPC-UA Stub-Endpoint. |
| `agri_qs_workflow` | WM-AGRI-QS-003 endpoints fuer Silo-Lot-QS-Workflow. |
| `agri_silo_material_flow` | WM-AGRI-SILO-001 — Agrar-Siloanlagen und Materialfluss (additiv zu /lager/wms). |
| `agribusiness` | Agribusiness Farmers Endpoint |
| `ai_data_classification` | P2.3 — KI-Datenklassen API. |
| `ai_engineering_metrics` | P2.2 — AI-Engineering-Metriken API. |
| `analytics` | Analytics API v1 |
| `annahme` | Annahme — Eingangs-Warteschlange (Ernte-Annahme / Wareneingang) |
| `ap_approval_workflow` | AP Approval Workflow API |
| `ap_invoices` | Accounts Payable (AP) Invoices API |
| `article_extensions` | Article extension endpoints (l3c-artikel extras) |
| `articles` | Inventory Articles management endpoints. |
| `artikel_bestandteile` | Artikel-Bestandteile — Qualitätsmerkmale und Inhaltsstoffe. |
| `artikel_mengeneinheiten` | Mengeneinheiten und Mengeneinheitengruppen — Artikelstamm. |
| `artikel_stamm_ext` | Artikelstamm-Erweiterungen: Folgeartikel, Inventurgruppen, Wiegungsgruppen. |
| `artikel_stoffstrom` | Artikelstoffstrom — THG/CO2-Bewertung und Nachhaltigkeitsattribute je Artikel. |
| `artikel_verpackung` | Artikelverpackung [AVP] — Gebinde-Stammdaten (1-3 Stufen). |
| `asset_accounting` | Anlagenbuchhaltung (Asset Accounting) — thin-router pattern with sqlalchemy.text() |
| `asset_ledger_connector` | VALEO Suite Anlagen (Asset Ledger) – Connector API. |
| `atlas_zollausfuhr` | ATLAS Zollausfuhr — German customs export declaration (ECS Phase 2). |
| `audit` | Audit Logging API |
| `audit_evidence` | Audit Evidence API — Wave 3 AP2 |
| `auto_matching` | Automatic Matching API |
| `background_jobs` | Queue-backed background job API for heavy process operations. |
| `bank_accounts` | Bankkontenstamm API |
| `bank_import` | INT-BANK-001: Bank-API / SEPA-Import (MT940 + CAMT.053). |
| `bank_reconciliation` | Bank Reconciliation API |
| `bank_statement_import` | Bank Statement Import API |
| `banken` | Bank Accounts API - Bankkonto Management (SQLAlchemy) |
| `batch` | OData-style $batch endpoint for bundling multiple read requests. |
| `bedarfsdeckung` | Bedarfsdeckungs-Cockpit (Durchdringungs-CRM) — Lücke je Betrieb × Produktgruppe. |
| `beleg_vordrucke` | Belegformular-Vordruck-Editor (Admin) — Druckvorlagen für Papier/PDF-Ausdrucke. |
| `benchmark_api` | — |
| `benchmark_cockpit` | — |
| `betriebsstaetten` | Betriebsstätten/Filialen — Filialsystem-Stammdaten. |
| `blockchain_runtime` | — |
| `booking_templates` | Booking Templates API |
| `branches` | Branches (Niederlassungen) CRUD endpoints. |
| `budget_planning` | Budgetierung / Forecast — thin-router pattern with sqlalchemy.text() |
| `bulk_journal_import` | Bulk Journal Entry Import API |
| `business_partners` | Business partner master data endpoints. |
| `case_management_api` | Case Management REST API — NC-08. |
| `cases` | CRM Service Cases API endpoints proxied through crm-service. |
| `central_contracts` | Zentrale Kontrakte-Engine — thin-router, sqlalchemy.text(). |
| `channel_work_surfaces` | — |
| `channels` | Channel Endpoints — NC-H1/H2/H4: WhatsApp Webhook, Email Ingress, Channel Router. |
| `charges` | Charges API - Lot/Batch Management (SQLAlchemy) |
| `chart_of_accounts` | Chart of Accounts management endpoints |
| `closing_checklists` | Closing Checklists API |
| `collab_notes` | Collab Rail notes API (UIX-062). |
| `collective_documents` | Sammellieferschein / Sammelrechnung — thin-router, sqlalchemy.text(). |
| `command_catalog` | Command Catalog API — Wave 5 Paket A. |
| `commodity_positions` | Commodity Position Matrix API: Matrix, Drilldown, KPI, Coverage Monitor, Refresh. |
| `compat` | Compatibility endpoints for frontend path alignment and missing modules. |
| `compliance` | Compliance API - DB-backed endpoints. |
| `compliance_dsgvo` | DSGVO Löschkonzept — Erasure request management (Art. 17 DSGVO). |
| `compliance_whistleblower` | — |
| `compliance_whistleblower_lksg` | Whistleblower and LkSG operating contracts for compliance. |
| `config_service` | Config Service API. |
| `contacts` | CRM Contact management endpoints proxied via crm-core |
| `contract_engagement` | Kontrakt-Engagement & Kontraktmahnung (DOM-CON-004.3). |
| `contract_fixing` | Kontrakt-Fixierung & MATIF-Bewertung (DOM-CON-004.2). |
| `contract_fulfillment` | Kontrakt-Erfüllungsstand (DOM-CON-004) — read-only. |
| `contract_pricing_api` | — |
| `contract_settlement` | Kontrakt-Settlement-Übergabe & Storno (DOM-CON-004.4). |
| `controlling` | Controlling module CRUD endpoints. |
| `controlling_actions` | DOM-CONTROLLING-004 — Budget-Lifecycle, Abweichungsanalyse, KST-Abschluss. |
| `copilot_ws` | Copilot WebSocket Streaming — NC-F3/F5 |
| `credit_debit_memos` | Credit Memos and Debit Memos API |
| `credit_management` | Kreditlimit-Verwaltung und Kreditstatus-Prüfung — thin-router, sqlalchemy.text(). |
| `creditors` | Creditor (Kreditoren) master data management endpoints. |
| `crm_360` | CRM 360°-Kundensicht — aggregiert echte ERP-Daten aus mehreren Domänen. |
| `crm_account_hierarchy` | CRM Account-Hierarchien — Parent/Child-Beziehungen zwischen Business-Partnern. |
| `crm_auto_capture` | KIM-AUTOCAPTURE — automatische Kontakt-Erfassung (Telefon/E-Mail/WhatsApp). |
| `crm_call_transcript` | KIM Telefon-Transkript-Connector — Anrufe automatisch als Kontakt erfassen. |
| `crm_campaigns` | — |
| `crm_capture_inbox` | KIM Klärfall-Inbox — nicht zuordenbare Auto-Captures sichten und zuordnen. |
| `crm_contacts_ext` | KIM-S4 — Ansprechpartner-Erweiterung: Werbe-Präferenzen + Pseudonymisierung. |
| `crm_duplicates` | Kunden-Dubletten (DOM-CRM-004) — Erkennung wahrscheinlicher Doppelanlagen. |
| `crm_gifts` | KIM-S3 — Kunden-Präsente-Endpoints (eigener Router, prefix /crm/kim). |
| `crm_kim` | KIM — „Kunde im Mittelpunkt": 360°-CRM-Cockpit-Backend. |
| `crm_kontakte` | Kunden-Kontakte (Kontakthistorie + Wiedervorlage) — Kunden-Cockpit. |
| `crm_kunden_map` | CRM-Kundenkarte — alle Kunden als GeoJSON (Karte + Hover-Kennzahlen). |
| `crm_lead_gen` | CRM Lead-Generierung — region-universale Lead-Kandidaten (GAP/LKV). |
| `crm_mail_capture` | KIM E-Mail-Connector — ein-/ausgehende Mails als Kontakt erfassen. |
| `crm_ownership` | Kunden-Ownership (DOM-CRM-004.3) — Zuordnung/Übergabe Außendienst/Innendienst. |
| `crm_partner_suche` | Einheitliche Partner-Suche über Kunden, Lieferanten und Leads (Multi-Rolle). |
| `crm_reports` | CRM Reports and Analytics endpoints. |
| `crm_segments` | CRM Kundensegmente — CRUD-Stub |
| `customer_extensions` | Customer extension endpoints (l3c-kunde extras) |
| `customers` | CRM Customer endpoints backed by the crm-core service. |
| `daily_prices` | Daily Price API endpoints. |
| `data_quality` | Datenqualitäts-API (Gap 040): Validierung von Dubletten, Pflichtfeldern und Referenzen. |
| `dauerauftraege` | Daueraufträge [DAU] — Wiederkehrende Aufträge/Rechnungen. |
| `debtors` | Debtor (Debitoren) master data management endpoints |
| `direct_debits` | Direct debit endpoints used by finance UI masks. |
| `disposition` | Disposition API - DB-backed endpoints. |
| `dms_images` | DMS image endpoints (l3c-dms extension) |
| `dms_inbox` | DMS Inbox Endpoints |
| `doc_nachweisraum_actions` | DOM-DOC-004 — Nachweisraum: Dokument-Upload, Freigabe, Wiedervorlage, GoBD-Export. |
| `docflow` | Canonical Docflow command endpoints (DOCFLOW-P0-01..03). |
| `docflow_artifact` | Artefakt-Upload, Versionierung & Freigabe (DOM-DOC-004.2). |
| `docflow_evidence` | Dokument-Nachweisraum (DOM-DOC-004) — GoBD-Artefakt-/Vorgangs-Sicht (read-only). |
| `docflow_followup` | Bescheid/Rückmeldung & Wiedervorlage am Vorgang (DOM-DOC-004.3). |
| `docflow_gobd` | GoBD-Exportpaket & DMS-/Paperless-Liveprobe (DOM-DOC-004.4). |
| `dokumente` | Dokumente API - Dokumentenverwaltung (SQLAlchemy Version) |
| `dunning` | Dunning System API |
| `e2e_chain` | — |
| `ebilanz_elster` | eBilanz / ELSTER export and ERiC submission endpoint. |
| `edi_api` | — |
| `einkauf_bestellvorschlag` | Einkauf â€” Bestell-Vorschlag Endpoints |
| `einkauf_kpis` | Einkauf — KPIs |
| `einkauf_lieferschein` | Einkauf Lieferschein + Frachtauftrag CRUD endpoints. |
| `erechnung_import` | E-Rechnung Import — ZUGFeRD / XRechnung stub. |
| `erloeskennziffern` | Erlöskennziffern [EKZS/EKZZ] — WaWi→FIBU Kontozuordnung. |
| `ernte_kampagne_api` | — |
| `ernte_planung` | Ernte-Planungsübersicht — CRUD für Ernteplanung (Schlag, Kultur, Menge, Status). |
| `ers_settlement` | Einkauf — ERS (Evaluated Receipt Settlement) |
| `esg_footprint` | UIX-082 ESG charge footprint API. |
| `etiketten` | Etiketten (Label Printing) API |
| `exchange_rates` | Exchange Rates API |
| `export_service` | Central Export Mikroservice |
| `external_agent_integrations` | — |
| `external_gates` | Externes Gate-Dashboard — Produktiv-API für den Integrationsstatus externer Systeme. |
| `external_mock_harness` | EXTERNAL-MOCK-HARNESS-001 — Dev-Only API fuer simulierte externe Systeme. |
| `farm_profiles` | CRM Farm Profile endpoints proxied through crm-core. |
| `feed_produktion_actions` | DOM-FEED-PROD-004 — Mischfutter Produktion: Rezeptur, Auftrag, QS-Freigabe. |
| `fibu_connectors` | FIBU Connectors API – einheitliches Framework für PAYROLL und VALEO Suite Anlagen (ASSET_LEDGER). |
| `fibu_geschaeftsjahre` | Geschäftsjahre, FiBu-Perioden und Periodische Buchungen. |
| `fibu_stammdaten` | FIBU Stammdaten: Zahlungsformulare [FIZAF], Zinsgruppen, Leergut-Artikelklassen. |
| `fibu_zahlungsmeldungen` | Zahlungsmeldungen [KASSZAME] — Eingehende Zahlungsanzeigen. |
| `finance_actions` | Finance action endpoints – Start/run actions for bank reconciliation, posting, cash, direct debit, closing. |
| `finance_clearing` | Zahlungseingang / OP-Auszifferung (DOM-FIN-004.3). |
| `finance_datev` | DATEV-Export (DOM-FIN-004.5). |
| `finance_dunning` | Mahnlauf & Mahnstufen-Eskalation (DOM-FIN-004.2). |
| `finance_followup` | Finance Follow-up API — Wave 4 AP5 |
| `finance_invoices` | Finance Invoices API Endpoints |
| `finance_op` | Offene-Posten-Cockpit / OP-Aging (DOM-FIN-004) — read-only. |
| `finance_period` | Periodenabschluss & Storno-Konsistenz (DOM-FIN-004.4). |
| `finance_read_models` | Finance Read-Models — Wave 2 AP2 |
| `financial_reports` | Financial Reports API |
| `flow_spines` | — |
| `foerderung` | Foerderung API - DB-backed endpoints. |
| `forderungsgruppen` | Forderungsgruppen [FORG] — Kundensegmentierung für Bestandskontenzuordnung. |
| `fuhrpark` | Fuhrpark API Endpoints - zvoove style master data mask. |
| `futter_stamm` | Futtermittel-Stammdaten & Rezepte API |
| `futtermittel_qs` | FEED-QS-001 — Futtermittel QS: HACCP-Plaene, VLOG-Meldungen, QS-Leitfaden. |
| `futtermittel_rezepte` | Futtermittel Rezepturverwaltung |
| `futtermittel_rohwaren` | Futtermittel Rohwaren-Stamm mit NÃ¤hrstoffprofil |
| `gap` | GAP Pipeline API Endpoints. |
| `gdpr` | GDPR API Endpoints |
| `gdpr_art30_ropa` | DSGVO Art. 30 — Verzeichnis von Verarbeitungstätigkeiten (Records of Processing Activities, RoPA). |
| `gdpr_art33_breach` | DSGVO Art. 33 — Datenpannen-Meldeprozess (Personal Data Breach Notification). |
| `gdpr_requests` | GDPR Data-Subject Requests API |
| `gelangensbestaetigung` | Gelangensbestätigung API — §17a UStDV |
| `genossenschaft` | Genossenschaft API — Aktionärs- und Gesellschafterverwaltung |
| `geo` | Geo-Endpoints für den Außendienst-Kartenviewer. |
| `gobd_archiv` | GoBD: Archiv (document_artifacts), E-Rechnung XML, Audit-Package Export (Z1/Z2/Z3). |
| `grundfutter_analysen` | Grundfutter-Analysen API |
| `gs1_barcode` | GS1 Barcode Parse Service |
| `gs1_parser` | GS1 barcode parser endpoint (l3c-gs1) |
| `harvest_acceptance` | Harvest Acceptance (Ernte-Annahme) API endpoints. |
| `hausbankenstamm` | Hausbankenstamm — Eigene Bankverbindungen des Mandanten. |
| `hofliste` | Hofliste — Fahrzeugvormeldungen und Status am Waagenterminal. |
| `hrm_abwesenheit` | HRM-ABWESENHEIT-ANTRAG-001 — Abwesenheitsantrag API. |
| `hrm_lifecycle_actions` | DOM-HRM-004 — HRM Lifecycle: Zeiterfassung, Abwesenheit, Arbeitszeitkonto. |
| `iban_lookup` | IBAN Lookup Service |
| `idempotency_monitoring` | — |
| `import_pipeline` | Import Pipeline Endpoints — Wave 3 AP6 |
| `individualpreise` | Individualpreise [PRI/PRIE] — Kunden-/Lieferanten-spezifische Preise. |
| `individuelle_artikelnummern` | Individuelle Artikelnummern [INDIVART] — Kunden-/Lieferanten-spezifische Artikelnummern. |
| `intrastat` | Intrastat API — EU-Handelsstatistik |
| `inventory_counts` | Inventory counts endpoints (l3c-inventur) |
| `inventory_operations` | Inventory Operations — Bestandskorrektur, Schwund, MHD-Abschreibung |
| `inventur_piv` | Permanente Inventur (PIV) — Rollierender Bestandsabschluss. |
| `iot_telemetry` | IoT / Telemetrie Endpoints — Wave 3 AP3 |
| `job_runner` | Job Runner API. |
| `journal_entries` | Finance Journal Entry management endpoints |
| `kaeufergruppe` | Käufergruppen-Klassifikation — lesen, vorschlagen, bestätigen, überschreiben. |
| `kasse_tagesabschluss` | Kasse – Tagesabschluss: Aktueller Tag + Buchung |
| `ki_usability` | KI-Usability API. |
| `knowledge_api` | Knowledge Core API — Wave 69 |
| `kontrakt_actions` | DOM-CON-004 — Kontrakt Lifecycle, Fixing, Settlement. |
| `kontrakt_hedging` | Kontrakt-Hedging und MATIF-Preisbindung. |
| `kontrakt_klassen` | Kontrakt-Klassen und Kontraktvarianten (Agrar-Spezialsoftware Feature). |
| `kontrakt_mengenzeitraum` | Kontraktmengenzeitraum — Ratierliche Lieferpläne für Rohwarenkontrakte. |
| `kontrakte` | Kontrakte endpoints — contract CRUD, movements, amendments, dispositionen. |
| `kostenrechnung` | Kostenrechnung: Kostenstellen, Kostenarten, Kostenstellen-Buchungen. |
| `kundenbanken` | Kundenbanken — IBAN/BIC-Bankverbindungen pro Kunde. |
| `labor` | Labor API - DB-backed endpoints. |
| `leads` | CRM Lead endpoints proxied through crm-core. |
| `liquidity` | Liquidity Planning API -- Liquiditaetsplanung |
| `liquidity_planning` | Liquiditätsplanung — 13-Wochen-Rolling-Forecast, thin-router pattern |
| `logistics_freight` | Logistik – Frachtkostenberechnung (Feature 2) |
| `logistics_tours` | Logistik – Tourenplanung-Engine (Feature 1 + Track & Trace / ePOD Feature 3) |
| `logistik_frachtbriefe` | LOG-FRACHTBRIEF-001 — GET/POST /api/v1/logistik/frachtbriefe. |
| `logistik_frachttabellen` | Frachttabellen — Frachtkosten-Stammdaten und Zuordnungen. |
| `lohn_connector` | Lohn-Connector API – Lohn-Import-Läufe (LEXWARE / externe Lohnbuchhaltung). |
| `marketing` | Marketing API - DB-backed endpoints. |
| `mask_actions` | SPEC-P1-04 / UIX-053+: Mask Action CommandEndpoints mit ActionRuntime. |
| `mask_registry` | Mask Registry API — Wave 3 AP1 |
| `mask_rollout_summaries` | Central screen-summary routes for batch mask rollouts (Waves 42–51). |
| `mask_screen_definition` | Mask ScreenDefinition API — native generator payloads. |
| `massebilanz` | Massebilanz — Periodische Mengenbilanzierung für Rohwarenbewegungen. |
| `master_data` | Master-data / Stammdaten endpoints (l3c-stammdaten) |
| `mcp_tool_registry` | MCP-ERP-TOOLS-001 — API fuer den ERP-Tool-Katalog. |
| `meldewesen_lifecycle_actions` | DOM-MEL-004 — Meldewesen Lifecycle: Intrastat, ELSTER, ATLAS. |
| `messages` | Internal messaging endpoints (l3c-nachricht) |
| `milchvieh_crosssell` | Cross-Sell-Auswertung Milchvieh (Hygiene-Bedarf + Kraftfutter-Potenzial). |
| `mobile_sync` | MOB-SYNC-001: Mobile Offline-Sync Endpoints. |
| `modules` | Runtime module visibility endpoints. |
| `nawaro` | NaWaRo CRUD endpoints for print notifications, contracts, and cultivation areas. |
| `nawaro_raps` | NaWaRo Raps profile API: usage split, sustainability certificates, coproduct balances. |
| `neuro_audit` | Audit Hardening + Decision Protocol — REST API (NC-D). |
| `neuro_compensation` | Compensation Engine — REST API (NC-006). |
| `neuro_consent` | Consent Engine — REST API (NC-004). |
| `neuro_event_monitoring` | Neuro Event Bus Monitoring Surfacing - NC-G8. |
| `neuro_event_policy` | Event Schema Registry + Policy Registry -- REST API (NC-G). |
| `neuro_fast_track` | Fast Track — REST API (NC-E). |
| `neuro_guardrails` | Guardrails + PII — REST API (NC-C). |
| `neuro_interactions` | Interaction State Manager — REST API (NC-002). |
| `neuro_knowledge` | Knowledge Store REST API — NC-06. |
| `neuro_pipeline` | Neuro-Core Pipeline — REST API (NC-A). |
| `neuro_prompt_packs` | Prompt Pack Registry -- REST API (NC-G5). |
| `neuro_simulation` | Neuro Simulation Engine — REST API (NC-005). |
| `neuro_state_graph_api` | Neuro State Graph + Confidence Ledger REST API -- Lane B |
| `neuro_verification` | Neuro Verification Engine — REST API (NC-001). |
| `neuro_voice` | Voice Adapter Layer — REST API (NC-003). |
| `number_ranges` | Admin API for configurable number ranges (Debitor/Kreditor accounts, partner numbers). |
| `nutrient_compositions` | Nutrient Composition (Düngemittel-Zusammensetzung) management endpoints. |
| `nve` | NVE / SSCC shipping-unit endpoints (l3c-nve) |
| `o2c_chain` | Order-to-Cash-Kette (DOM-SALES-004) — Angebot→Auftrag→Lieferschein→Rechnung (read-only). |
| `o2c_uat_scaffold` | O2C/P2P UAT scaffold — end-to-end process chain test data and scenario runner. |
| `op_skonto_auszifferung` | OP Skonto-Auszifferung — Offene Posten mit Skontoaufteilung ausgleichen. |
| `open_items` | Open Items (OP) management endpoints |
| `operational_governance` | Operational Governance API — Wave 4 AP4 |
| `operator_agent` | OPERATOR-AGENT-001 — API fuer den ERP-Operator-Agent (Proposal + LOW-Risiko-Execute). |
| `opportunities` | CRM Sales Opportunities API endpoints proxied through crm-sales. |
| `partiestamm` | Partiestamm [PAR] & Partiegruppen [PGR] — Lot-/Charge-Verwaltung. |
| `payment_matching` | Payment Matching API |
| `payment_runs` | Payment Runs / SEPA API |
| `periodische_buchungen` | Periodische Buchungen [WZA] — Wiederkehrende FIBU-Buchungen. |
| `personal` | Personal endpoints for employee list, time entries and timesheets. |
| `pick_lists` | Pick-list endpoints (l3c-pickliste) |
| `planung_kalender` | UIX-063 planning calendar API. |
| `policies` | Policy Manager API Endpoints |
| `portal_feldbuch` | Portal Feldbuch — Endpoints für den Landwirt im Kundenportal |
| `portal_innendienst` | — |
| `portal_intelligence` | — |
| `portal_interessent` | — |
| `portal_lohndienst` | — |
| `portal_preisspiegel` | — |
| `portal_shop` | Kundenportal Shop API Endpunkte |
| `pos_dsfinvk` | Compatibility endpoints for provider-backed DSFinV-K exports. |
| `pos_fiscalization` | — |
| `pos_payments` | — |
| `pos_payments_promotions` | POS payment split and promotions preview endpoints. |
| `pos_retoure` | POS Retoure (Return) Endpoint |
| `pos_tagesabschluss_actions` | DOM-POS-004 — POS Tagesabschluss: Z-Bon, TSE-Simulation, DSFinV-K. |
| `position_overrides` | Commodity Position Override API (Freigabe anfordern / genehmigen / ablehnen). |
| `position_rules` | Commodity Position Rules API (No-Speculation Guard Regeln). |
| `preis_rabattgruppen` | Rabattgruppen und Rabattklassen — Stammdaten für die Rabattpflege. |
| `preparation_lists` | Preparation list endpoints (l3c-lager Rüstlisten) |
| `price_calculation` | Preis-Kalkulations-Engine (dynamisch). |
| `price_hedge_api` | — |
| `price_lists` | Price List management endpoints. |
| `pricing` | Pricing calculation endpoints with hierarchical cascade logic. |
| `pricing_governance` | Pricing Governance Endpoints — Wave 3 AP4 |
| `process_kernel_api` | Process Kernel API â€” Wave 11 |
| `process_map` | P2.1 — Workflow-Prozesskarte API. |
| `process_mining_api` | — |
| `process_mining_observation` | — |
| `process_sla` | Process SLA API — Wave 4 AP3 |
| `procurement_match` | Beschaffungs-Abgleich / 3-Wege-Match (DOM-PROC-004). |
| `produktion_mischfutter` | Produktion – Mischfutter: Verfuegbarkeit, Rezepte & Produktionsauftraege |
| `produktion_rezepturgruppen` | Rezepturgruppen und Produktions-Schnellerfassung für Mischfutter. |
| `projection_consumer` | Projektions-Consumer API — Wave 4 AP2 |
| `projekte` | Projekte — vollständiges CRUD inkl. Aufgaben. |
| `prospecting` | Prospecting API Endpoints |
| `purchase_invoice_verification` | Einkauf — 3-Wege-Match (Purchase Order / Goods Receipt / Invoice Receipt) |
| `quadriga_connector` | Quadriga-Connector API – Konfiguration und Sync für Quadriga-Anbindung. |
| `quality_evidence` | INTEGRATION-EVIDENCE-BOARD-001 — GET /admin/quality-evidence/ aggregiert Qualitätsnachweise. |
| `quality_lot_binding` | Quality Lot Binding Endpoints — FEED-CHAIN-003. |
| `quality_protocols` | Quality Protocol API endpoints. |
| `rag` | RAG API Endpoints |
| `rations_optimization` | Rationsoptimierung API  (GfE 2023 / DLG-Futterwerttabellen Stand Juli 2025) |
| `rations_zugang` | Rationsoptimierung – DSGVO-Zugangsverwaltung |
| `read_model_snapshots` | — |
| `reklamation_api` | — |
| `report_print` | Report and print endpoints for traceability, weighing PDFs and labels. |
| `reporting_api` | — |
| `reports_export` | Reports Export — generischer Berichts-Download-Endpunkt |
| `rfq` | Einkauf — RFQ (Request for Quotation) — Anfrageprozess |
| `rohware_sammelabrechnung` | Rohware-Sammelabrechnung — gebündelte Abrechnung mehrerer Belege (Agrar-Spezialsoftware Feature). |
| `rohware_schema` | — |
| `rohwarengruppen` | Rohwarengruppen [RWG] — Stammdaten für Rohwarenabrechnung. |
| `ruestliste` | Rüstliste (Kommissioniervorbereitung) |
| `runtime_operations` | Runtime Operations API — Wave 4 AP6 |
| `saatzucht` | Saatzucht-Modul — certified seed / seed breeding management stub. |
| `sales_blanket_orders` | Rahmenaufträge / Abrufe (Blanket Orders) — thin-router, sqlalchemy.text(). |
| `sales_credit` | Kreditlimit-Prüfung & Billing-Status im O2C-Kontext (DOM-SALES-004.3) — read-only. |
| `sales_credit_notes` | Sales Credit Notes (Gutschriften) and Returns (Retouren) endpoints. |
| `sales_delivery_notes` | Sales Delivery Notes (Lieferscheine) CRUD endpoints. |
| `sales_invoice_einvoice` | Slice-006: XRechnung/ZUGFeRD Export Endpoints für SalesInvoice. |
| `sales_match` | Auftrag-↔-Lieferschein-Positions-Match (DOM-SALES-004.2) — read-only. |
| `sales_offers` | Domain sales offers (Angebote) CRUD endpoints. |
| `sales_orders` | Domain sales orders CRUD endpoints. |
| `sales_reports` | Sales Reports and Dashboards endpoints. |
| `sales_shipping_ext` | Sales shipping extension endpoints (l3c-verkaufslieferschein extras) |
| `sales_storno` | Lieferungs-Storno & Gutschrift-Übersicht (DOM-SALES-004.4). |
| `sanctions_compliance` | Sanctions Compliance API — Verbotsliste / Sanktionsprüfung |
| `scan` | Mobile-Scan / Barcode-Dispatch API. |
| `schaeden` | Schaeden (Damage Reports) API |
| `security_monitoring` | Security monitoring surfacing for violation and block events. |
| `self_billing` | Self-Billing API endpoints. |
| `service_anfragen` | Service-Anfragen API — CRUD for service requests, feedback, and case closure. |
| `silo` | Silo capacity and virtual lot endpoints (AGRAR-SILO-01). |
| `silo_cells_readmodel` | UIX-081 Twin-Panel Read-Model fuer Silozellen. |
| `silo_operations_api` | — |
| `silo_target_cell` | WM-SILO-RULE-ENGINE-001 — Zielzellen-Vorschlag API. |
| `sla_escalation_api` | SLA-Eskalation API — Wave 12 |
| `stmd_duplikat` | STMD-DUP-001: Cross-Domain-Dublettenprüfung für Stammdaten. |
| `strecke` | Strecke – Streckengeschaefte CRUD |
| `strecke_speditionen` | Strecke – Speditionen / Frachttarife nach PLZ |
| `stuecklisten` | Stücklisten / Rezepturen [ARTSTLI] — Artikelkomponenten-Stammdaten. |
| `subsidiary_ledger_reconciliation` | Subsidiary Ledger Reconciliation API |
| `supplier_portal` | — |
| `supply_chain` | Supply-Chain-Traceability (DOM-SUPPLY-004). |
| `supply_chain_blockchain` | — |
| `sustainability` | Sustainability API endpoints. |
| `system_metrics` | System Metrics API for AI Agents |
| `tankstelle` | Tankstelle — Zapfungen und Tankbestand, vollständiges CRUD. |
| `tapi` | TAPI/Telefonie — eingehende Anrufe + Kunden-Auflösung für Click-to-Customer. |
| `tax_keys` | Tax Keys API |
| `tenant_governance` | Tenant Governance API — Wave 2 AP3-AP6 |
| `tenant_limits` | Tenant-isolated cache and rate-limit API. |
| `tenants` | Tenant API endpoints |
| `terminology` | Terminology API for the Landhandel bilingual terminology registry. |
| `tours` | Tours API - Verladung/Tour Management |
| `training` | — |
| `transporte` | Transporte — Fahrerverwaltung, vollständiges CRUD. |
| `users` | User API endpoints |
| `ux_overlays` | User-scoped ScreenDefinition overlays (UIX-071). |
| `ux_telemetry` | UX-Telemetrie — Omnibox-Intent-Signale (UIX-060). |
| `vat_codes` | VAT Tax Codes Admin API |
| `vat_return_export` | VAT Return Export API |
| `verladung` | Verladung — vollständiges CRUD. |
| `vermehrungsvertrag` | Vermehrungsvertrag [SAATV] — Saatgut-Anbauverträge mit Vermehrern. |
| `versandprofile` | Versandprofilstamm + Lieferavise — Belegversand-Konfiguration und Lieferavisierungen. |
| `versicherungen` | Versicherungen — vollständiges CRUD. |
| `vertraege` | Verträge API - Rahmenverträge (SQLAlchemy) |
| `vertreterprovisionen` | Vertreterprovisionsgruppen und -staffeln — Provisionsabrechnung Außendienst. |
| `vertreterstamm` | Vertreterstamm — Außendienstmitarbeiter und Vertretergruppen. |
| `waage` | — |
| `waage_mobile` | WGE-MOB-001: Mobile-Sync für Waagenbelege. |
| `waagen_vorlagen` | Waagenvorlagen / Wiederholfall-Anlieferungen (Agrar-Spezialsoftware Feature). |
| `warehouse_transfers` | Warehouse transfer & stock correction endpoints (l3c-lager) |
| `warehouse_wms` | — |
| `warehouses` | Warehouse management endpoints |
| `warengruppen` | Warengruppen 3-stufig — Hauptwarengruppe / Oberwarengruppe / Warengruppe. |
| `wartung` | Wartung / Anlagenverwaltung — vollständiges CRUD. |
| `webhook_system` | Outbound Webhook Registration |
| `webhooks` | Webhook management endpoints (l3c-webhook) |
| `webshop_integration` | B2B webshop integration endpoints. |
| `websocket` | WebSocket Endpoints |
| `weighing_tickets` | Weighing tickets endpoints (l3c-wiegeschein) |
| `wf_cockpit_persist` | WF-COCKPIT-PERSIST-001 — DB-backed Cockpit API (Dead-Letter + Detail). |
| `wf_trigger` | WF-TRIGGER-001: Status-Trigger → Folgeaktion-API. |
| `whatsapp_intake` | WhatsApp Bestell-Inbox — eingehende Freitext-Bestellungen erfassen & bestätigen. |
| `whatsapp_notify` | WA-NOTIFY-001 — Ausgehende WhatsApp Push-Benachrichtigungen |
| `whatsapp_webhook` | WA-AGENT-001/WA-NOTIFY-001 — WhatsApp Webhook + Dev-Simulator Endpoints |
| `workflow_cockpit` | Workflow cockpit API. |
| `workflow_runtime` | Workflow Runtime API — Wave 4 AP1 |
| `workflow_simulation` | — |
| `workflow_template_marketplace` | — |
| `xrechnung` | INT-XRECHNUNG-001: XRechnung / ZUGFeRD E-Rechnung Export. |
| `zahlungsbedingungen` | Zahlungsbedingungen [ZABD] — Zahlungsziel, Skonto, Zahlungsart. |
| `zertifikate` | Zertifikate API - DB-backed endpoints. |
| `zertifikate_api` | — |
| `zinsabrechnung` | Zinsabrechnung — Zinsen auf Rohware-Einlagerungskontrakte. |
| `zu_abschlaggruppen` | Zu-/Abschlaggruppen [ZAGR] und Zu-/Abschlagklassen [ZAKL] — Konditionsstammdaten. |
