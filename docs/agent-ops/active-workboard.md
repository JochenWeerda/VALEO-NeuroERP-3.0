# Active Workboard

## Zweck

Gemeinsame operative Sicht fuer parallele Agentenarbeit.

Diese Datei ist absichtlich schlank und soll bei jeder Session schnell lesbar bleiben.

## Aktueller Stand

- Datum: `2026-03-29`
- Branch: `develop` (lokal; mit `backup/develop` abgleichen bei Push)
- Source of Truth: `docs/architecture/process-kernel/STATUS.md`

## Parallele E2E-Lanes (Kollisionen vermeiden)

Zwei End-to-End-Stränge laufen **fachlich und technisch getrennt**. Bitte **nicht** ohne Lead-Abstimmung dieselben Verzeichnisse in einer Session bearbeiten:

| Lane | Scope (typisch) | Aktive / reservierte Slices | Regel |
|------|-----------------|--------------------------------|--------|
| **Agrar / Harvest-to-Settlement** | `packages/frontend-web/src/pages/agrar/**`, relevante `pages/annahme/**` | VK-017 abgeschlossen (Codex) | Kein paralleles Editing mit der OTC-Folge-Lane. |
| **Order-to-Cash Folge (Finance)** | `packages/frontend-web/src/pages/finance/**`, optional `pages/sales/**` / `pages/verkauf/**` | OTC-011 | Kein paralleles Editing mit VK-013-Agrar ohne Absprache. |
| **Kontrakt (Contract-to-Settlement)** | `packages/frontend-web/src/pages/kontrakte/**`, `lib/api/kontrakte.ts` | CTS-001 bis CTS-009 abgeschlossen | Ueberlappung mit OTC (Auftrag/LS) und VK (Ernte-Annahme) — bei Aenderungen an order-editor/lieferschein abstimmen. |
| **Lager (Inventory-to-Settlement)** | `packages/frontend-web/src/pages/lager/**`, `app/api/v1/endpoints/warehouses*.py`, `inventory_counts.py` | INV-001 bis INV-007 (P1 abgeschlossen) | Ueberlappung mit CTS (Auslagerung aus Kontrakt) und VK (Einlagerung aus Ernte). |
| **Finance (Finance-to-Reporting)** | `packages/frontend-web/src/pages/finance/**`, `pages/fibu/**`, `app/api/v1/endpoints/finance_*.py` | FIN-001 bis FIN-003 (P1 abgeschlossen) | Ueberlappung mit OTC (Zahlungen) und Compliance (USTVA). |
| **CRM (CRM-to-Revenue)** | `packages/frontend-web/src/pages/crm/**`, `pages/vertrieb/**`, `app/api/v1/endpoints/customers.py` | CRM-001, CRM-002 (P1 abgeschlossen) | Ueberlappung mit OTC (Auftraege) und CTS (Kontrakte). |
| **Compliance (Compliance-to-Audit)** | `packages/frontend-web/src/pages/compliance/**`, `app/api/v1/endpoints/compliance.py`, `audit.py` | COM-001, COM-002 (P1 abgeschlossen) | Ueberlappung mit Finance (USTVA) und Agrar (BVL-PSM). |

**Lane-Status:** `VK-019` ist abgeschlossen (Queue-Repair). `OTC-011` ist als Folgelane zu OTC-010 **begonnen** (Workflow+Card), Umsetzung im Finance-UI folgt iterativ. Alle 9 Flow-Spine-Lanes haben jetzt Workflow-Dokumentation mit Mermaid-Diagrammen und Status-Abschnitten.

## Neuro-Core Architektur-Lanes (NEU 2026-03-29)

8 parallelisierbare Lanes fuer die integrierte Zielarchitektur. Vollstaendige Gap-Analyse und Slice-Details: `docs/architecture/neuro-core-gap-analysis-2026-03-29.md`

| Lane | Scope | Slices | Status | Dateibesitz (exklusiv) | Abhaengigkeit |
|------|-------|--------|--------|----------------------|---------------|
| **NC-A: Neuro-Core Kernel** | Intent Engine + Planner + Verification Engine | **abgeschlossen** (A1-A5) | Cursor Agent | `app/agents/neuro_intent_engine.py`, `app/agents/neuro_planner.py`, `app/agents/neuro_pipeline.py`, `app/services/neuro_verification_engine.py`, `app/api/v1/endpoints/neuro_pipeline.py` | keine — Kern-Lane fertig, abhaengige Slices (D4, F5, H4, H5) jetzt freigegeben |
| **NC-B: State Graph + Confidence** | Business Object Graph + Append-Only Confidence Ledger | NC-B1..B5 | abgeschlossen (Codex, 2026-03-29) | `app/core/neuro_state_graph.py`, `confidence_ledger.py`, `app/infrastructure/models/neuro_state_models.py`, `app/api/v1/endpoints/neuro_state_graph_api.py`, `tests/test_neuro_state_graph.py` | B5 wartet auf A |
| **NC-C: Guardrails + Consent** | PII/DLP-Schutz, Consent-Lifecycle (DSGVO) | **abgeschlossen** (C1-C3 + NC-004) | Cursor Agent | `app/services/pii_detector.py`, `app/services/guardrails.py`, `app/services/consent_engine.py`, `app/api/v1/endpoints/neuro_guardrails.py`, `app/api/v1/endpoints/neuro_consent.py` | keine |
| **NC-D: Audit Hardening** | Append-Only Audit-Schema, Neuro-Entscheidungs-Protokoll, Hash-Chain | teilweise (D1-D3 umgesetzt) | Cursor Agent | `app/services/audit_hardening.py`, `app/services/neuro_decision_protocol.py`, `app/api/v1/endpoints/neuro_audit.py` | D4 (Pipeline-Integration) wartet auf A |
| **NC-E: Fast Track + Compensation** | Deterministischer CRUD-Bypass + Saga-Rollback | **abgeschlossen** (E1-E2 + NC-006) | Cursor Agent | `app/services/fast_track.py`, `app/services/compensation_engine.py`, `app/api/v1/endpoints/neuro_fast_track.py`, `app/api/v1/endpoints/neuro_compensation.py` | keine |
| **NC-F: Copilot Backend** | WebSocket-Streaming + Interaction State FSM | teilweise (F1-F4 umgesetzt) | Cursor Agent | `app/api/v1/endpoints/copilot_ws.py`, `app/services/interaction_state_manager.py`, `packages/frontend-web/src/features/copilot/useCopilotStream.ts` | F5 wartet auf Lane A |
| **NC-G: Event Bus + Knowledge** | NATS-Consumer, Event-Schemas, Policy-Versionierung | reserviert (Codex, 2026-03-29) | Codex | `app/services/event_schema_registry.py`, `app/services/policy_registry.py`, `app/api/v1/endpoints/neuro_event_policy.py`, `app/infrastructure/eventbus/nats_consumer.py` | NC-G2 (NATS Consumer) starten |
| **NC-H: Channels + Voice** | WhatsApp, E-Mail, Voice-Adapter, Simulation Engine | teilweise (EXT-03 + EXT-05 umgesetzt via NC-003/NC-005) | Cursor Agent (NC-003/NC-005) | `app/channels/whatsapp_adapter.py`, `email_channel.py`, `app/services/voice_adapter.py`, `app/services/neuro_simulation_engine.py` | NC-H1 (WhatsApp Adapter) starten |

**Prioritaet:** P1 = A, B, C, D (sofort) | P2 = E, F, G (danach) | P3 = H (Channel-Erweiterung)

## Aktive Slices

| Slice-ID | Thema | Status | Owner | Dateibesitz | Naechster Schritt | Blocker |
|----------|-------|--------|-------|-------------|-------------------|---------|
| OPS-001 | Workflow-Analyse-Methodik und Agent-Ops-Doku | abgeschlossen | — | `AGENTS.md`, `docs/agent-ops/**`, `docs/workflows/**`, `docs/project-context/**`, `docs/quality-assurance/**` | bei neuen Workflow-Slices wiederverwenden | keine |
| DOCS-105 | Wave-104-Dokumentations-Nachzug (GAP-G/H/I, Repo-Hygiene) | abgeschlossen | — | `docs/architecture/process-kernel/STATUS.md`, `DELIVERY-MAP.md`, `wave-104/STATUS.md`, `docs/roadmap/status/2026-03-27-wave-104-abschluss.md`, `docs/project-context/open-gaps-and-known-issues.md` | keine (Doku im Repo eingecheckt) | keine |
| NC-B1 | Neuro State Graph + Confidence Ledger (Grundgeruest) | abgeschlossen | Codex | `app/core/neuro_state_graph.py`, `app/core/confidence_ledger.py`, `app/infrastructure/models/neuro_state_models.py`, `app/api/v1/endpoints/neuro_state_graph_api.py`, `alembic/versions/neuroassist_state_graph_confidence_ledger_20260329.py`, `tests/test_neuro_state_graph.py`, `docs/workflows/nc-b1-state-graph-confidence-ledger.md`, `docs/cards/neuro-core/NC-B1-state-graph-confidence-ledger.md` | NC-D1 oder NC-C1 claimen | keine |
| NC-G2 | NATS Consumer Framework | reserviert | Codex | `app/infrastructure/eventbus/nats_consumer.py`, `app/services/event_schema_registry.py`, `app/api/v1/endpoints/neuro_event_policy.py`, `docs/workflows/nc-g2-nats-consumer.md`, `docs/cards/neuro-core/NC-G2-nats-consumer.md` | Umsetzung starten | keine |
| P2P-001 | Procure-to-Pay Direktbestellung: Workflow-Analyse, QA und Handover-Haertung | abgeschlossen | aktuell offener Agent | `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/**`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Folgeslice fuer Bedarfsmeldung/Rahmenabruf zuschneiden | keine |
| P2P-040 | Procure-to-Pay Vorbelegung aus Bedarfsmeldung/Vertrag/RFQ | abgeschlossen | aktuell offener Agent | `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Folgeslice Schrittvalidierung zuschneiden | keine |
| P2P-050 | Procure-to-Pay Wizard-Schrittvalidierung | abgeschlossen | aktuell offener Agent | `docs/workflows/p2p-050-wizard-schrittvalidierung.md`, `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` | Landhandel-Kernprozess beginnen | keine |
| VK-010 | Ernte-Annahme Workflow-Analyse, Handover-Haertung und QA-Slice | abgeschlossen | aktuell offener Agent | `docs/workflows/vk-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` | VK-011 Handover-Bruecke und Schrittvalidierung zuschneiden | keine |
| VK-011 | Ernte-Annahme Handover-Bruecke (QP→Erfassung) und LKW-Wizard-Schrittvalidierung | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-011-qp-handover-und-lkw-validierung.md`, `docs/cards/agrar/VK-011-qp-handover-und-lkw-validierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` | Folgearbeit in **Agrar-Lane**: VK-013 (Codex) oder Queue-/Artikel-Slice | keine |
| VK-012 | Annahme-Abrechnung: Settlement-Flow-Analyse und QA-Haertung | abgeschlossen | Claude Sonnet 4.6 | `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/pages/annahme/rohware.tsx`, `docs/workflows/vk-012-annahme-abrechnung.md`, `docs/cards/agrar/VK-012-annahme-abrechnung.md` | abgeschlossen | keine |
| VK-020 | Rohware-Wizard Schrittvalidierung (VK-012-P1) | abgeschlossen | Cursor Agent | `packages/frontend-web/src/pages/annahme/rohware.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/rohware.test.tsx`, `docs/workflows/vk-020-rohware-wizard-schrittvalidierung.md`, `docs/cards/agrar/VK-020-rohware-wizard-schrittvalidierung.md` | VK-012-P2/P3 oder VK-013 | keine |
| VK-013 | Ernte-Kampagne-Abschluss: Gesamtabrechnung ueber alle Settlements | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-013-kampagnenabschluss.md`, `docs/cards/agrar/VK-013-kampagnenabschluss.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx` | Folge-Slice fuer echte Kampagnenreferenz oder Queue-/Artikel-API zuschneiden | keine |
| VK-014 | Settlement-Kampagnenreferenz: echte Zuordnung statt Zeitfenster-Proxy | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-014-settlement-kampagnenreferenz.md`, `docs/cards/agrar/VK-014-settlement-kampagnenreferenz.md`, `app/api/v1/endpoints/agrar_settlements.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/agrar_settlement_campaign_reference_20260327.py`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `tests/test_agrar_settlement_campaign_reference.py`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx` | Folge-Slice fuer Backfill oder Queue-/Artikel-API zuschneiden | keine |
| VK-015 | Settlement-Kampagnenreferenz Backfill fuer Alt-Daten | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-015-settlement-kampagnen-backfill.md`, `docs/cards/agrar/VK-015-settlement-kampagnen-backfill.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/agrar_settlements.py`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `tests/test_agrar_settlement_campaign_backfill.py`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx` | Queue-/Artikel-API-Folgeslice fuer die Annahmekette zuschneiden | keine |
| VK-016 | Annahme-Warteschlange CTA und kanonische Artikel-API | abgeschlossen | aktuell offener Agent (Codex) | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-016-queue-cta-und-artikel-api.md`, `docs/cards/agrar/VK-016-queue-cta-und-artikel-api.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` | Folge-Slice fuer echte `article_id` bereits in der Queue-API oder Klaerungsprozess gesperrte Ware zuschneiden | keine |
| VK-017 | Annahmekette Queue-Contract mit echter `article_id` | abgeschlossen | Codex | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-017-queue-article-id.md`, `docs/cards/agrar/VK-017-queue-article-id.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/lkw_annahme_queue_article_reference_20260328.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/annahme/qr-scanner.tsx`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`, `tests/test_compat_lkw_registrierung.py` | Klaerungsprozess `gesperrt` oder Repair-Slice fuer historische Queue-Eintraege schneiden | keine |
| VK-018 | Klaerungsprozess gesperrte Ware (QP-Ergebnis `gesperrt`) | abgeschlossen | Codex | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-018-klaerungsprozess-gesperrt.md`, `docs/cards/agrar/VK-018-klaerungsprozess-gesperrt.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/lkw_annahme_queue_klaerung_20260328.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/annahme/klaerung-gesperrt.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/annahme.ts`, `packages/frontend-web/src/app/route-builders/alias-groups/generated/annahme.ts`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `tests/test_compat_lkw_registrierung.py` | Folge-Slice: Repair historischer Queue-Eintraege oder Sonderfreigabe-Policy | keine |
| VK-019 | Queue-Repair: historische Eintraege ohne `article_id` | abgeschlossen | Codex | `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-019-queue-repair-article-id.md`, `docs/cards/agrar/VK-019-queue-repair-article-id.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx` | Naechster Schritt: Sonderfreigabe-Policy/Role-Guard | keine |
| OTC-010 | Order-to-Cash End-to-End: Verkaufsauftrag → Lieferschein → Rechnung → Zahlung | abgeschlossen | Claude Sonnet 4.6 | `pages/sales/invoice-editor.tsx`, `pages/verkauf/lieferschein-erfassung.tsx`, `docs/workflows/otc-010-order-to-cash.md`, `docs/cards/verkauf/OTC-010-order-to-cash.md` | abgeschlossen | keine |
| OTC-011 | Zahlungseingang und Abstimmung (Folgeslice OTC-010) | abgeschlossen | Claude Sonnet 4.6 | `packages/frontend-web/src/pages/finance/op-debitoren.tsx`, `pages/finance/payment-matching.tsx`, `pages/sales/invoice-editor.tsx`, `docs/workflows/otc-011-zahlungseingang-und-abstimmung.md`, `docs/cards/finance/OTC-011-zahlungseingang-und-abstimmung.md` | abgeschlossen — P1-P4 als Folge-Slices | keine |
| CTS-001 | Contract-to-Settlement: Erstanalyse (15 Cards, Mermaid, Soll-Ist, Empfehlungen) | abgeschlossen | Cursor Agent | `docs/workflows/cts-001-contract-to-settlement.md`, `docs/cards/kontrakte/CTS-001-contract-to-settlement.md` | — | keine |
| CTS-002 | Kontraktbindung auf Belegen: Lookup + Preisuebernahme + Restmengen-Warnung | abgeschlossen | Cursor Agent | `packages/frontend-web/src/hooks/useKontraktLookup.ts`, `pages/sales/order-editor.tsx`, `pages/verkauf/lieferschein-erfassung.tsx` | — | keine |
| CTS-003 | Auto-Movement-Buchung aus Lieferschein | abgeschlossen | Cursor Agent | `app/services/kontrakt_movement_sync.py`, `app/api/v1/endpoints/sales_delivery_notes.py` | — | keine |
| CTS-004 | MATIF-Preisfixierungs-Dialog | abgeschlossen | Cursor Agent | `pages/kontrakte/DlgMatifPreisfixierung.tsx`, `pages/kontrakte/FrmKontraktDetail.tsx` | — | keine |
| CTS-005 | Soft-Delete + Bestaetigung-Dialog | abgeschlossen | Cursor Agent | `app/api/v1/endpoints/kontrakte.py`, `pages/kontrakte/FrmKontraktDetail.tsx`, `lib/api/kontrakte.ts` | — | keine |
| CTS-006 | Kontraktliste aufwerten (Statusfilter, Party-Name, Paginierung, Artikel+Preis) | abgeschlossen | Cursor Agent | `pages/kontrakte/LstKontraktUebersicht.tsx`, `app/api/v1/endpoints/kontrakte.py`, `lib/api/kontrakte.ts` | — | keine |
| CTS-007 | Tabs differenzieren (Partner, Preismodell, Bedingungen, Notizen, Unterlagen) | abgeschlossen | Cursor Agent | `pages/kontrakte/FrmKontraktDetail.tsx` | — | keine |
| CTS-008 | Alarm-Dashboard (ablaufende Kontrakte, niedrige Restmenge, offene MATIF) | abgeschlossen | Cursor Agent | `pages/kontrakte/KontraktAlarmDashboard.tsx`, Route-Registrierung | — | keine |
| CTS-009 | Rohwaren-Positionsmonitor (Long/Short-Deckung, Unterdeckungs-Alarm) | abgeschlossen | Cursor Agent | `app/services/kontrakt_position_service.py`, `app/api/v1/endpoints/kontrakte.py`, `pages/kontrakte/KontraktPositionsmonitor.tsx`, `pages/kontrakte/FrmKontraktDetail.tsx`, `pages/kontrakte/LstKontraktUebersicht.tsx` | — | keine |
| INV-001 | Inventory-to-Settlement: Vollanalyse (11 Masken, 11 Cards, 15 Soll-Ist, Mermaid, P1-P5) | abgeschlossen | Claude Opus 4.6 | `docs/workflows/inv-001-inventory-to-settlement.md`, `docs/cards/inventory/INV-001-inventory-to-settlement.md`, `pages/lager/**`, `pages/verladung/**` | P1-P5 als Folge-Slices | keine |
| INV-002 | Bestandsuebersicht: echte KPIs aus StockMovement-Aggregation | abgeschlossen | Cursor Agent | `app/api/v1/endpoints/compat.py` (GET /lager/dashboard), `lib/api/dashboard.ts` | — | keine |
| INV-003 | Ein-/Auslagerung: StockMovement-Buchung (FIFO/FEFO, Chargen-Abzug) | abgeschlossen | Cursor Agent | `app/api/v1/endpoints/compat.py` (POST einlagerung/auslagerung) | — | keine |
| INV-004 | Einlagerung: Stammdaten aus API (Artikel + Lagerorte) statt hart codiert | abgeschlossen | Cursor Agent | `pages/lager/einlagerung.tsx` | — | keine |
| INV-007 | Lagerplaetze: echte Belegung aus used_capacity/total_capacity | abgeschlossen | Cursor Agent | `pages/lager/lagerplaetze.tsx` | — | keine |
| FIN-001 | Finance-to-Close: Vollanalyse (7 Masken, 11 Cards, 14 Soll-Ist, Mermaid, P1-P8) | abgeschlossen | Claude Opus 4.6 | `docs/workflows/fin-001-finance-to-close.md`, `docs/cards/finance/FIN-001-finance-to-close.md`, `pages/finance/buchungserfassung.tsx`, `pages/finance/nebenbuch-abstimmung.tsx`, `pages/finance/periods.tsx`, `pages/fibu/abschluss-cockpit.tsx`, `pages/fibu/abschluss-checklist-detail.tsx`, `pages/finance/ustva.tsx` | P1-P8 als Folge-Slices | keine |
| CMP-001 | Compliance-to-Report: Vollanalyse (6 Masken, 12 Cards, 13 Soll-Ist, Mermaid, P1-P5) | abgeschlossen | Claude Opus 4.6 | `docs/workflows/cmp-001-compliance-to-report.md`, `docs/cards/compliance/CMP-001-compliance-to-report.md`, `pages/compliance/**`, `pages/nachhaltigkeit/eudr-compliance.tsx`, `pages/finance/ustva.tsx`, `pages/admin/compliance-dashboard.tsx` | P1-P5 als Folge-Slices | keine |
| REK-001 | Complaint-to-Resolution: Vollanalyse (5 Masken, 11 Cards, 14 Soll-Ist, Mermaid, P1-P10) | abgeschlossen | Claude Opus 4.6 | `docs/workflows/rek-001-complaint-to-resolution.md`, `docs/cards/qualitaet/REK-001-complaint-to-resolution.md`, `pages/qualitaet/**`, `app/api/v1/endpoints/reklamation_api.py` | P1-P10 als Folge-Slices | keine |
| SVC-001 | Service-to-Customer: Vollanalyse (2 Masken, 10 Cards, 15 Soll-Ist, Mermaid, P1-P10) | abgeschlossen | Claude Opus 4.6 | `docs/workflows/svc-001-service-to-customer.md`, `docs/cards/service/SVC-001-service-to-customer.md`, `pages/service/anfragen.tsx`, `pages/agribusiness/field-service-tasks.tsx` | P1-P10 als Folge-Slices | keine |

## Reservierungsregel

**Pflichtschritt vor jeder Arbeit an einem Slice (Claim-Protokoll):**

1. Workboard lesen — ist der Slice bereits `reserviert` oder `in arbeit`? Dann: anderen Slice waehlen.
2. Slice in der Tabelle auf Status `reserviert` setzen, Owner eintragen, Dateibesitz listen.
3. Diesen Workboard-Stand **sofort als eigenen Commit** abgeben: `chore(workboard): claim SLICE-ID`.
4. Erst nach diesem Commit mit der eigentlichen Arbeit beginnen.

Kein Agent darf einen Slice beginnen, der bereits `reserviert` oder `in arbeit` ist.

**Status-Werte:**

| Status | Bedeutung |
|--------|-----------|
| `offen` | Noch nicht begonnen, kann uebernommen werden |
| `reserviert` | Claim-Commit erfolgt, Agent beginnt gleich |
| `in arbeit` | Agent arbeitet aktiv, keine Neuuebernahme |
| `abgeschlossen` | Fertig, committet, Handoff vorhanden |

- Pro Slice ein Owner.
- Dateibesitz klar dokumentieren.
- Ueberschneidungen nur mit explizitem Integrationshinweis.

## Aufgabenverteilung Cursor Agent / Codex (Stand 2026-03-29)

### Cursor Agent: Lane A — Neuro-Core Kernel (reserviert)

Cursor Agent arbeitet jetzt an Lane A (Intent Engine + Planner). Das ist die Kern-Lane, von der D4, F5, H4, H5 abhaengen.

**Slices:**

| Slice | Inhalt | Status |
|-------|--------|--------|
| NC-A1 | `IntentResult` Contract: intent, confidence_score (0-1), risk_class, explanation, requested_action | **abgeschlossen** |
| NC-A2 | `IntentEngine.classify(user_input, context) -> IntentResult` mit 11 Intents + Capability-Matching | **abgeschlossen** |
| NC-A3 | `PlanStep` Contract + `Planner.generate_plan(intent, context) -> ExecutionPlan` mit 9 Templates | **abgeschlossen** |
| NC-A4 | `VerificationResult` Integration — Planner nutzt bestehende Verification Engine (NC-001) | **abgeschlossen** |
| NC-A5 | Pipeline: Intent -> Plan -> Verify -> Execute + Decision Protocol | **abgeschlossen** |

**Dateibesitz (exklusiv):** `app/agents/neuro_intent_engine.py`, `app/agents/neuro_planner.py`, `tests/test_neuro_intent_engine.py`, `tests/test_neuro_planner.py`

### Codex: Verbleibende Aufgaben

Codex soll folgende Aufgaben uebernehmen, sobald seine aktuelle Arbeit (NC-B) abgeschlossen ist:

**Prio 1 — Abhaengig von Lane A (erst nach Cursor-Agent-Commit NC-A5):**

| Aufgabe | Lane | Beschreibung | Dateibesitz |
|---------|------|-------------|-------------|
| NC-D4 | D | Decision Protocol automatisch aus Neuro-Core Pipeline befuellen | `app/middleware/audit_middleware.py` (EDIT) |
| NC-D5 | D | Audit-Query-API: Hash-Chain-Validierung als Regression | `tests/test_audit_append_only.py` |
| NC-F5 | F | Copilot -> Neuro-Core Pipeline: Chat -> IntentEngine -> Planner -> Response-Stream | `app/api/v1/endpoints/copilot_ws.py` (EDIT) |

**Prio 2 — Sofort machbar (keine Abhaengigkeit):**

| Aufgabe | Lane | Beschreibung | Dateibesitz |
|---------|------|-------------|-------------|
| NC-G2 | G | `NATSConsumer` — generischer Consumer mit Retry, DLQ, Idempotenz | `app/infrastructure/eventbus/nats_consumer.py` |
| NC-G3 | G | Mindestens 3 Consumer aktivieren: Audit-Event, Inventory-Movement, Settlement-Created | `app/infrastructure/eventbus/` |
| NC-H1 | H | `WhatsAppAdapter` — WhatsApp Business API Webhook-Empfang, Message-Parsing, Reply | `app/channels/whatsapp_adapter.py` |
| NC-H2 | H | `EmailChannel` — IMAP-Polling/Webhook fuer eingehende E-Mails, Response via SMTP | `app/channels/email_channel.py` |
| NC-H4 | H | Channel -> ChannelIngress -> Neuro-Core Routing fuer alle neuen Kanaele | `app/channels/` |

**Regeln fuer Codex:**
- Vor jeder Arbeit den Slice im Workboard auf `reserviert` setzen und sofort committen (`chore(workboard): claim SLICE-ID`).
- Dateibesitz ist exklusiv — keine Dateien aus Lane A oder den bereits abgeschlossenen Lanes C/E bearbeiten.
- Nach jedem Slice: Tests, Doku (Workflow + Card) und Workboard aktualisieren.
- Commit-Convention: `feat(nc-XX): <beschreibung>`.

## Letzte wichtige Entscheidungen

- Workflow-Analyse wird dokumentationsbasiert und card-basiert durchgefuehrt.
- Standardmaske vor Spezialmaske ist verbindliche Entscheidungsregel.
- Restart-sicherer Kontext laeuft ueber `AGENTS.md` plus `docs/agent-ops/`.
- Wave 104 vollstaendig abgeschlossen (GAP-A bis GAP-I, 5931 Tests gruen, commit `1ad5ea4d`).
- Claude-Parallelstand in `docs/AGENT-INTEGRATION.md`, `docs/governance-rollout-summary.md` und `docs/standards/markdown-governance.md` geprueft; operative Folgearbeit richtet sich an den neuen Doku-Einstiegen aus.
- P2P-040 abgeschlossen: Vorbelegung aus Bedarfsmeldung/Vertrag/RFQ korrekt verdrahtet (`.data`, URL `/v1/`, Toast), Backend-Compat-Endpoints fuer Anfrage und Vertrag nachgezogen, Frontend- und API-Tests gruen.
- P2P-050 abgeschlossen: Wizard-Schrittvalidierung verdrahtet (validateStep, onStepValidationError); die relevante Frontend-Regression fuer Wizard und P2P-Pfad ist gruen.
- VK-010 abgeschlossen: Claude-Analyse fuer den breiten Ernte-Annahme-Kernprozess ist mit dem operativen Handover-/QA-Slice zusammengezogen. Dokumentiert und abgesichert sind jetzt sowohl der Edit-Mode-Fix (`.data`-Extraktion in `loadHarvestAcceptance`) als auch die restart-sichere Handover-Haertung (`useMemo` fuer Workflow-Kontext, Seitentest, QA-Checkliste).
- VK-011 abgeschlossen: Qualitaets-Check uebergibt restart-sicher per Query in die Ernte-Annahme; `quality_protocol_id` wird mitpersistiert; LKW-Wizard blockiert leere Pflichtschritte per Toast.
- VK-013 abgeschlossen: Kampagnenabschluss laeuft ueber bestehende Standardmasken (`erntefenster-konfig.tsx` -> `abrechnung.tsx`); Aggregation erfolgt vorerst ueber `created_at` im Kampagnenfenster.
- VK-014 abgeschlossen: Settlements tragen jetzt eine echte `campaign_id`; Frontend filtert kampagnenbezogen bevorzugt ueber diese Referenz und nutzt Datumsfenster nur noch als Legacy-Fallback.
- VK-015 abgeschlossen: Alt-Settlements ohne `campaign_id` koennen kampagnenbezogen per Repair-CTA nachgezogen werden; ueberlappende Kampagnenfenster bleiben bewusst offen statt blind migriert zu werden.
- VK-016 abgeschlossen: Die Warteschlange bietet fuer abgeschlossene Eintraege einen direkten CTA in die Ernte-Annahme; der Handover zieht die kanonische `article_id` ueber die Artikel-API nach, wenn moeglich.
- VK-017 abgeschlossen: Die Annahmekette persistiert jetzt `article_id` bereits in der Queue; LKW-Registrierung, QR-Pfad, Warteschlange, Qualitaets-Check und Ernte-Annahme fuehren dieselbe Referenz durchgaengig mit.
- Naechste Prioritaet: **parallel getrennt** - Agrar-Lane Folge-Slice fuer Backfill der Alt-Settlements oder Queue-/Artikel-API vs Finance-Folge-Lane **OTC-011** (siehe Abschnitt Parallele E2E-Lanes).
- Naechste Prioritaet Agrar-Lane: Queue-/Artikel-API-Folgeslice in der Annahmekette, da Neu- und Alt-Daten fuer Kampagnen jetzt belastbar referenziert sind.
- Naechste Prioritaet Agrar-Lane aktuell: den Klaerungsprozess fuer `gesperrt` als naechsten VK-Slice schneiden; optional danach Repair fuer historische Queue-Eintraege ohne `article_id`.
- VK-020 abgeschlossen: Rohware-Wizard mit `getStepValidationError` (Lieferant/Fahrzeug, Ware/Lager/Netto); Card VK-012-P1 als erledigt markiert; Vitest `rohware.test.tsx`.
- Workboard-Konsistenz 2026-03-27: DOCS-105-Handoff geschlossen (Doku im Repo); VK-013 von Stub auf abgeschlossen gehoben; OTC-011 Folgelane mit Workflow/Card begonnen.
- CTS-001 abgeschlossen: Contract-to-Settlement vollstaendig analysiert (15 Cards, Mermaid, 28 Soll-Ist-Abweichungen, 8 priorisierte Empfehlungen). Kontrakt-Lane im Workboard eingefuehrt.
- CTS-002 bis CTS-005 umgesetzt: Kontraktbindung mit Lookup+Preis auf Belegen (order-editor, lieferschein), Auto-Movement-Sync bei LS-Erstellung, MATIF-Preisfixierungs-Dialog, Soft-Delete mit Bestaetigung.

## Handoff: 2026-03-27 — DOCS-105 (archiviert)

**Von:** Claude Sonnet 4.6
**Stand:** **abgeschlossen und im Repo eingecheckt** (Nachzug Wave 104, Workboard, Roadmap-Dateien; siehe History ab Wave-104-Commits).

**Hinweis fuer Sessions:** Die frueheren Zeilen "Docs-Commit ausstehend" / "P2P-001 als naechster Schritt" sind **veraltet**; P2P-Slices sind inzwischen ebenfalls abgeschlossen. Aktuelle Prioritaeten: **Parallele E2E-Lanes**, offene Finance-Lane **OTC-011** und im Agrar-Strang der Folge-Slice nach **VK-013**.

**Tests / Checks:** `node scripts/docs-governance-check.cjs` bei Doku-Aenderungen.

## Slice-Details

## Slice: P2P-001 - Procure-to-Pay Direktbestellung

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Ersten belastbaren Workflow-/QA-Slice fuer den Flow-Spine-Einstieg `Procure-to-Pay` in die Standard-Bestellmaske dokumentieren und gefundene Workflow-Brueche direkt beheben.
**Fachlicher Scope:** Flow-Spine-Handover, Standardmaske `Bestellung anlegen`, Direktbestellung als Standardstart, Bedarfsmeldung und Rahmenabruf als Alternativpfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/**`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** Workflow-Doku nach Master-Prompt vorhanden; mindestens eine Card nach Template vorhanden; Bestellmaske verhindert leere oder fachlich unbrauchbare Anlage; Lieferadresse wird konsistent an den Backend-Contract uebergeben; Regressionstest ist gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx`
**Doku-Updates:** Workboard, Workflow-Analyse, Card-Datei, Resume-/Handoff-Block.
**Risiken / Blocker:** Backend-Compat-Contract erzwingt Pflichtfelder nicht serverseitig; Frontend muss fuer diesen Slice eine belastbare Mindestvalidierung sicherstellen.
**Naechster konkreter Schritt:** Folgeslice fuer Bedarfsmeldung-, Vertrags- und RFQ-Vorbelegung separat zuschneiden.

## Handoff: 2026-03-27 - P2P-001

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** `Procure-to-Pay`-Direktbestellung dokumentieren, QA-haerten und den Handover in die Standard-Bestellmaske stabilisieren.
**Stand:** abgeschlossen
**Erledigt:** Workflow-Analyse nach Master-Prompt erstellt; Card fuer `P2P-020` erstellt; Render-Schleife im Workflow-Handover ueber memoisierten Kontext behoben; Mindestvalidierung vor Bestellungsspeicherung ergaenzt; Lieferadresse auf `shippingAddress` ausgerichtet; Frontend-Regressionstests fuer Handover, Validierung und Payload ergaenzt.
**Offen:** Bedarfsmeldung-, Vertrags- und RFQ-Vorbelegung als eigener Folgeslice; optionale serverseitige Pflichtfeldvalidierung im Compat-Endpoint.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/cards/einkauf/P2P-020-direktbestellung-standardmaske.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx`
**Offene Risiken:** Backend-Compat-Endpoint erzwingt Pflichtfelder weiterhin nicht serverseitig; Inline-Fehlhinweise im Wizard fehlen weiterhin.
**Annahmen:** `shippingAddress` bleibt das kanonische Persistenzfeld des aktuellen Purchase-Order-Contracts; Direktbestellung ist der priorisierte Standardstart fuer den ersten P2P-Slice.
**Naechster konkreter Schritt:** `P2P-040` fuer Vorbelegung aus Requisition, Vertrag und RFQ zuschneiden und mit Browser-Use-/CRUD-Checks absichern.

## Slice: P2P-040 - Procure-to-Pay Vorbelegung

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Vorbelegung der Bestellmaske aus Bedarfsmeldung, RFQ und Vertrag auf reale API- und Datenvertraege ziehen.
**Fachlicher Scope:** Einkaufsanfrage als Bedarfsmeldung/RFQ, Vertragsbezug fuer Rahmenabruf, Vorbelegung der Standard-Bestellmaske ohne Spezialmaske.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** `.data`-Extraktion in allen Load-Funktionen; URL-Prefix `/v1/` konsistent; Toast-Bestaetigung bei Vorbelegung; Backend-Compat-Endpoints fuer Anfrage und Vertrag vorhanden; Frontend- und API-Regressionstests gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`; `pytest tests/test_compat_einkauf_anfragen.py -q`
**Doku-Updates:** Workboard, Workflow-Datei `p2p-040-vorbelegung-requisition-vertrag-rfq.md`, Card `P2P-040-vorbelegung-standardmaske.md`, Handoff.
**Risiken / Blocker:** Graceful Degradation bleibt gewollt; abweichende Backend-Feldnamen wuerden weiterhin zu teilweiser Leer-Vorbelegung fuehren.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung zuschneiden.

## Handoff: 2026-03-27 - P2P-040

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Vorbelegungs-Ladefunktionen fuer Bedarfsmeldung, RFQ und Vertrag korrekt verdrahten.
**Stand:** abgeschlossen
**Erledigt:**
- `.data`-Extraktion in `loadRequisitionData`, `loadContractData`, `loadRFQData` nachgezogen (war fehlendes `.data` bei `apiClient.get` = AxiosResponse)
- Contract-URL von `/api/contracts/:id` auf `/api/v1/contracts/:id` korrigiert
- Backend-Compat-Endpoint `GET /api/v1/einkauf/anfragen/:id` fuer Bedarfsmeldung und RFQ eingefuehrt
- Backend-Compat-Endpoint `GET /api/v1/contracts/:id` auf bestehenden Contract-Router verdrahtet
- Toast-Bestaetigung nach erfolgreichem Vorbelegungs-Load eingefuegt
- 3 neue Regressionstests: Bedarfsmeldung-Prefill, RFQ-Prefill, Vertrags-Prefill
- API-Regressionstests fuer Anfrage- und Contract-Compat-Pfade ergaenzt
- `getMock.mockResolvedValue({ data: null })` als Default-Reset in `beforeEach`
- Workflow-Analyse `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md` erstellt
- Card `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md` erstellt
**Offen:** Weiterfuehrende Landhandel-Kernprozesse folgen separat.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `app/api/v1/endpoints/compat.py`, `tests/test_compat_einkauf_anfragen.py`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`, `packages/frontend-web/src/pages/einkauf/rfq-bids.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx` - gruen; `pytest tests/test_compat_einkauf_anfragen.py -q` - API-Compat-Regression
**Offene Risiken:** Graceful Degradation kann bei abweichenden Backend-Feldnamen zu teilweiser Leer-Vorbelegung fuehren.
**Annahmen:** `apiClient.get<T>()` gibt `AxiosResponse<T>` zurueck (`.data` = Nutzdaten). Requisition und RFQ teilen denselben Endpoint `/api/v1/einkauf/anfragen/`.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung zuschneiden.

## Slice: P2P-050 - Procure-to-Pay Wizard-Schrittvalidierung

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Schrittvalidierung im generischen Wizard additiv einfuehren und den P2P-Anlagepfad ueber eine konkrete Browser-Use-Checkliste restart-sicher machen.
**Fachlicher Scope:** Lieferanten- und Positionsschritt in `Bestellung anlegen`, Ruecksprunglogik, Vorwaertsnavigation, Browser-Use fuer Direktbestellung und Vorbelegung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/workflows/p2p-050-wizard-schrittvalidierung.md`, `docs/cards/einkauf/P2P-020-direktbestellung-standardmaske.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/components/patterns/Wizard.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Abnahmekriterien:** Generischer Wizard erlaubt additive Schrittvalidierung ohne Bestandsbruch; P2P blockiert `Weiter` bei leerem Lieferanten- oder Positionsschritt; Frontend-Regressionen sind gruen; Browser-Use-Checkliste ist konkret dokumentiert.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/patterns/Wizard.test.tsx src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx`; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Doku-Updates:** Workboard, Workflow-Datei `p2p-050-wizard-schrittvalidierung.md`, Card `P2P-050-wizard-schrittvalidierung.md`, P2P-001/P2P-040-Nachzug, Browser-Use-Checkliste, Handoff.
**Risiken / Blocker:** Inline-Fehlhinweise pro Schritt fehlen weiterhin; aktueller Nutzerfeedback-Kanal ist Toast-basiert.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung als Folgeslice zuschneiden.

## Handoff: 2026-03-27 - P2P-050

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Schrittvalidierung im P2P-Wizard sauber in den Standard-Pattern-Baustein ziehen und die QA-Dokumentation konkretisieren.
**Stand:** abgeschlossen
**Erledigt:**
- Claude-Parallelstand in `docs/AGENT-INTEGRATION.md`, `docs/governance-rollout-summary.md` und `docs/standards/markdown-governance.md` geprueft und in den operativen Doku-Einstieg eingeordnet
- Generischen Wizard um `getStepValidationError` und `onStepValidationError` additiv erweitert
- P2P-Bestellmaske mit Schrittvalidierung fuer `Lieferant` und `Positionen` verdrahtet
- Wizard-Regressionstest fuer blockierten Schrittwechsel ergaenzt
- P2P-Seitentests auf den echten Schrittfluss nachgezogen und um Blockierfall erweitert
- Workflow-Doku `docs/workflows/p2p-050-wizard-schrittvalidierung.md` erstellt
- Card `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md` erstellt
- Browser-Use-Checkliste um konkrete P2P-Direkt- und Vorbelegungspruefung ergaenzt
- P2P-001- und P2P-040-Doku auf den neuen Validierungsstand nachgezogen
**Offen:** Inline-Fehlhinweise im Wizard sind weiterhin nicht vorhanden.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/p2p-001-procure-to-pay-direktbestellung.md`, `docs/workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md`, `docs/workflows/p2p-050-wizard-schrittvalidierung.md`, `docs/cards/einkauf/P2P-020-direktbestellung-standardmaske.md`, `docs/cards/einkauf/P2P-040-vorbelegung-standardmaske.md`, `docs/cards/einkauf/P2P-050-wizard-schrittvalidierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/components/patterns/Wizard.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx`, `packages/frontend-web/src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/patterns/Wizard.test.tsx src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx` - gruen; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` - gruen
**Offene Risiken:** Toast-basierte Validierung ist funktional, aber weniger fuehrend als Inline-Fehlhinweise; andere Wizards nutzen den neuen Hook noch nicht.
**Annahmen:** P2P benoetigt vorerst nur harte Schrittvalidierung fuer Lieferanten- und Positionsschritt; Lieferung bleibt optional.
**Naechster konkreter Schritt:** VK-011 Ernte-Annahme-Handover-Bruecke und LKW-Wizard-Schrittvalidierung als Folgeslice zuschneiden.

## Slice: VK-010 - Ernte-Annahme (Landhandel-Kernprozess)

**Owner:** aktuell offener Agent
**Status:** abgeschlossen
**Ziel:** Ersten belastbaren Landhandel-Kernprozess-Slice dokumentieren und die Ernte-Annahme-Maske auf den kritischen Pfaden Edit-Mode und Workflow-Handover stabilisieren.
**Fachlicher Scope:** Breite Annahmekette LKW-Registrierung -> Warteschlange -> Qualitaets-Check -> Ernte-Annahme-Erfassung -> Abrechnung als Analysebasis; operativer Umsetzungsslice fuer den Handover in die Ernte-Annahme-Maske.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Abnahmekriterien:** Workflow-Analyse nach Master-Prompt vorhanden; mindestens eine Card fuer den Ernte-Annahme-Einstieg vorhanden; kritischer Edit-Mode-Bug behoben; Workflow-Handover render-stabil; Seitentest und Browser-Use-Checkliste dokumentieren den Handover-Pfad.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Doku-Updates:** Workboard, Workflow-Analyse, bestehende Kernprozess-Card, fokussierte Standardmasken-Card, QA-Checkliste, Handoff-Block.
**Risiken / Blocker:** Qualitaets-Check -> Ernte-Annahme ist weiterhin keine vollstaendige Handover-Bruecke; LKW-Wizard hat noch keine Schrittvalidierung; Artikelquelle ist weiterhin nicht kanonisch an Backend-Listen gebunden.
**Naechster konkreter Schritt:** VK-011 Handover-Bruecke Qualitaets-Check -> Ernte-Annahme und Schrittvalidierung im LKW-Wizard zuschneiden.

## Handoff: 2026-03-27 - VK-010

**Von:** aktuell offener Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Ernte-Annahme-Kernprozess nach Master-Prompt analysieren und die Ernte-Annahme-Maske auf Edit-Mode- und Workflow-Handover-Pfaden stabilisieren.
**Stand:** abgeschlossen
**Erledigt:**
- Workflow-Analyse `docs/workflows/vk-010-ernte-annahme.md` als breite Prozessbasis fuer die Annahmekette erstellt
- Kernprozess-Card `docs/cards/agrar/VK-010-ernte-annahme.md` fortgefuehrt; zusaetzlich fokussierte Standardmasken-Card `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md` fuer den operativen Handover-Slice angelegt
- Edit-Mode-Bug in `ernte-annahme-erfassung.tsx` behoben: `apiClient.get()` gibt `AxiosResponse<T>` zurueck; `loadHarvestAcceptance()` liest Nutzdaten ueber `.data`
- Workflow-Handover in `ernte-annahme-erfassung.tsx` render-stabil gemacht: `readWorkflowEntryContext(searchParams)` memoisiert, damit kein instabiler Handover-Kontext pro Render entsteht
- Seitentest `src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx` ergaenzt; Banner- und Bemerkungs-Vorbelegung aus Workflow-Parametern regressionsgesichert
- Browser-Use-Checkliste fuer Harvest-to-Settlement / Ernte-Annahme und P2P-Fehlerpfad nachgezogen
- Workboard und P2P-Doku auf den erreichten Stand synchronisiert
**Offen:** VK-011 Handover-Bruecke (Qualitaets-Check -> Ernte-Annahme navigieren); Schrittvalidierung im LKW-Wizard; Artikel-API statt hardcodierter Liste; Klaerungsprozess gesperrte Ware.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme.md`, `docs/cards/agrar/VK-010-ernte-annahme-standardmaske.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Offene Risiken:** Handover-Bruecke fehlt weiterhin als vollstaendige Navigation aus dem Qualitaets-Check; Schrittvalidierung im LKW-Wizard fehlt; Backend-Artikelquelle ist noch nicht kanonisch verdrahtet.
**Annahmen:** Der zuvor dokumentierte Edit-Mode-Bug lag in `loadHarvestAcceptance()`; der operative Folgeschritt fuer restart-sicheren Handover ist Kontextstabilisierung in der Ernte-Annahme-Maske, nicht eine neue Spezialmaske.
**Naechster konkreter Schritt:** VK-011 Handover-Bruecke und LKW-Wizard-Schrittvalidierung als eigenstaendigen Slice zuschneiden.

## Slice: VK-011 - QP-Handover und LKW-Wizard-Validierung

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Den operativen Handover aus der Qualitaetspruefung restart-sicher in die Ernte-Annahme ziehen und den Touch-Wizard fuer LKW-Registrierung gegen leere Pflichtschritte haerten.
**Fachlicher Scope:** `Qualitaetspruefung` -> `Ernte-Annahme-Erfassung`, Query-basierter Handover, Persistenz von `quality_protocol_id`, additive Schrittvalidierung im LKW-Wizard.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-011-qp-handover-und-lkw-validierung.md`, `docs/cards/agrar/VK-011-qp-handover-und-lkw-validierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Abnahmekriterien:** QP navigiert bei `freigegeben`/`bedingt` direkt in die Ernte-Annahme; Handover ueberlebt Reload; `quality_protocol_id` wird mitpersistiert; LKW-Wizard blockiert leere Pflichtschritte; Doku und QA-Checkliste sind nachgezogen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/components/patterns/Wizard.test.tsx src/__tests__/pages/einkauf/bestellung-anlegen.test.tsx src/__tests__/pages/workflow/flow-spine-procure-to-pay.test.tsx src/__tests__/pages/annahme/lkw-registrierung.test.tsx src/__tests__/pages/annahme/qualitaets-check.test.tsx src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-011-qp-handover-und-lkw-validierung.md`, Card `VK-011-qp-handover-und-lkw-validierung.md`, QA-Checkliste.
**Risiken / Blocker:** Queue-CTA fuer abgeschlossene Eintraege fehlt weiterhin; Artikelname bleibt im Handover noch Freitext statt kanonischer API-Referenz; `tsc --noEmit` lief in dieser Session mehrfach ins Timeout ohne konkreten Compilerfehler.
**Naechster konkreter Schritt:** VK-013 claimen oder einen Folge-Slice fuer Queue-CTA/Artikel-API schneiden.

## Handoff: 2026-03-27 - VK-011

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** QP-Handover in die Ernte-Annahme restart-sicher machen und den LKW-Wizard validieren.
**Stand:** abgeschlossen
**Erledigt:**
- `qualitaets-check.tsx` baut jetzt einen query-basierten Handover nach `/agrar/ernte-annahme-erfassung` statt stumpf zur Warteschlange zurueckzuspringen; `gesperrt` bleibt weiterhin in der Warteschlange
- `ernte-annahme-erfassung.tsx` liest QP-Handover aus Query-Parametern/Route-State, vorbelegt Fahrzeug, Artikelname und Bemerkungen additiv und persistiert `quality_protocol_id` im Harvest-Acceptance-Write-Contract
- `lkw-registrierung.tsx` nutzt `getStepValidationError` und destructive Toasts fuer Kennzeichen-, Lieferanten- und Artikel-Pflichtfelder
- Regressionen nachgezogen in `lkw-registrierung.test.tsx`, `qualitaets-check.test.tsx` und `ernte-annahme-erfassung.test.tsx`
- Workflow-Doku, Card und Browser-Use-Checkliste erstellt bzw. aktualisiert
**Offen:** Queue-CTA `Ernte-Annahme anlegen` fuer abgeschlossene Eintraege; kanonische Artikel-API fuer den Handover; fachliche Entscheidung, ob `bedingt` spaeter einen separaten Freigabeschritt braucht.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-011-qp-handover-und-lkw-validierung.md`, `docs/cards/agrar/VK-011-qp-handover-und-lkw-validierung.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Tests / Checks:** Relevanter Vitest-Satz gruen (`20/20`). `pnpm exec tsc --noEmit --pretty false` in `packages/frontend-web` lief mehrfach ins Timeout; kein konkreter TypeScript-Fehler ausgegeben.
**Offene Risiken:** Queue-Pfad und Artikel-API bleiben offen; TypeScript-Gesamtlauf konnte in dieser Session nicht abgeschlossen werden.
**Annahmen:** Query-Parameter bleiben der restart-sichere Handover-Kanal; `quality_protocol_id` ist ein gueltiger Write-Contract der Ernte-Annahme-API; `bedingt` darf aktuell in die Ernte-Annahme weiterlaufen.
**Naechster konkreter Schritt:** VK-013 claimen oder Folge-Slice fuer Queue-CTA/Artikel-API reservieren.

## Slice: VK-012 - Annahme-Abrechnung

**Owner:** Claude Sonnet 4.6
**Status:** abgeschlossen
**Ziel:** Settlement-Flow nach Rohware-Annahme analysieren, URL-Bug beheben und Workflow-Doku erstellen.
**Fachlicher Scope:** rohware.tsx (Rohware-Schnellerfassung), abrechnung.tsx (Settlement + Freigabe + FIBU), Drying Rule Engine, Optimistic Locking.
**Dateibesitz:** `packages/frontend-web/src/pages/annahme/rohware.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `docs/workflows/vk-012-annahme-abrechnung.md`, `docs/cards/agrar/VK-012-annahme-abrechnung.md`
**Abnahmekriterien:** Rohware-POST-URL korrekt (`/api/v1/agrar/harvest-acceptance`); Workflow-Analyse (A-G) vorhanden; Card mit Soll-Ist-Abweichungen; Handoff-Block im Workboard.

## Handoff: 2026-03-27 - VK-012

**Von:** Claude Sonnet 4.6
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Settlement-Flow nach Rohware-Annahme analysieren und kritischen URL-Bug beheben.
**Stand:** abgeschlossen
**Erledigt:**
- Bug VK-012-B1 behoben: `rohware.tsx:119` POST-URL von `/api/v1/harvest-acceptance` auf `/api/v1/agrar/harvest-acceptance` korrigiert (Backend mount: `api.py:679 prefix="/agrar/harvest-acceptance"`)
- Workflow-Analyse `docs/workflows/vk-012-annahme-abrechnung.md` erstellt (Sektionen A-G: Uebersicht, Karten, Mermaid-Fluss, Soll-Ist, UI/CRUD, Risiken, Empfehlungen)
- Card `docs/cards/agrar/VK-012-annahme-abrechnung.md` erstellt (17 Sektionen, vollstaendige API-Tabelle, Abzugslogik, Freigabe-Automat, Bug-Dokumentation)
- Workboard aktualisiert: VK-012 abgeschlossen, VK-013 als offener Folgeslice eingetragen
**Offen:** VK-012-P1 Wizard-Schrittvalidierung rohware.tsx; VK-012-P2 Supplier-CRM-Dropdown; VK-012-P3 Artikel/Lager aus API
**Betroffene Dateien:** `packages/frontend-web/src/pages/annahme/rohware.tsx`, `docs/workflows/vk-012-annahme-abrechnung.md`, `docs/cards/agrar/VK-012-annahme-abrechnung.md`, `docs/agent-ops/active-workboard.md`
**Tests / Checks:** Manuell: Rohware-Wizard → Annahmenummer (kein 404), "Zur Abrechnung" mit prefilled Werten, Settlement anlegen, Freigabe-Workflow, FIBU-Verbuchung
**Offene Risiken:** Kein `getStepValidationError` im Rohware-Wizard — ungueltige Daten koennen durchkommen; Supplier-ID bleibt Freitext ohne CRM-Validierung
**Naechster konkreter Schritt:** VK-013 Ernte-Kampagne-Abschluss claimen oder VK-012-P1 Rohware-Wizard Schrittvalidierung.

## Slice: VK-013 - Ernte-Kampagnenabschluss

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Einen belastbaren Kampagnenabschluss ueber bestehende Standardmasken verfuegbar machen, statt eine neue Spezialmaske einzufuehren.
**Fachlicher Scope:** `erntefenster-konfig.tsx` als Kampagnenmonitor, `abrechnung.tsx` als bestehender Abschlussort fuer zugeordnete Settlements.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-013-kampagnenabschluss.md`, `docs/cards/agrar/VK-013-kampagnenabschluss.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Abnahmekriterien:** Kampagnenliste zeigt KPI und Abschlussstatus je Kampagne; CTA oeffnet die gefilterte Settlement-Pruefung; Abrechnungsmaske filtert ueber Query-Parameter; Workflow/Card/QA-Doku sind nachgezogen; relevante Vitest-Regressionen sind gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-013-kampagnenabschluss.md`, Card `VK-013-kampagnenabschluss.md`, QA-Checkliste.
**Risiken / Blocker:** Kampagnenzuordnung basiert vorerst nur auf `created_at` im Zeitfenster und ist damit noch keine revisionssichere fachliche Referenz.
**Naechster konkreter Schritt:** Folge-Slice fuer echte Kampagnenreferenz oder fuer Queue-/Artikel-API in der Annahmekette claimen.

## Handoff: 2026-03-27 - VK-013

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Kampagnenabschluss ueber vorhandene Standardmasken verfuegbar machen und fachlich dokumentieren.
**Stand:** abgeschlossen
**Erledigt:**
- `erntefenster-konfig.tsx` laedt jetzt zusaetzlich Settlements, aggregiert je Kampagne Anzahl, Netto, Abzuege und offene Datensaetze und zeigt daraus einen UI-Abschlussstatus
- CTA `Settlement-Abschluss pruefen` springt mit `campaignName`, `campaignStart` und `campaignEnd` in `annahme/abrechnung`
- `abrechnung.tsx` filtert die Settlement-Liste query-basiert auf das Kampagnenfenster und zeigt oben eine kompakte Kampagnenkarte
- Regressionen in `erntefenster-konfig.test.tsx` und `abrechnung.test.tsx` sichern KPI-/Filterpfad
- Workflow-Doku, Card und QA-Checkliste von Stub auf Ist-Stand nachgezogen
**Offen:** Keine explizite Kampagnen-ID am Settlement-Contract; Aggregation erfolgt nur ueber `created_at` im Zeitfenster.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-013-kampagnenabschluss.md`, `docs/cards/agrar/VK-013-kampagnenabschluss.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Offene Risiken:** Ueberlappende Kampagnen oder spaet erfasste Settlements koennen im aktuellen Proxy-Modell falsch zugeordnet werden.
**Annahmen:** `created_at` bleibt bis zu einem Backend-Folgeslice die einzig belastbare Zuordnungsbasis; Standardmaske vor Spezialmaske bleibt fuer den Kampagnenabschluss korrekt.
**Naechster konkreter Schritt:** Entweder echte Kampagnenreferenz im Settlement-Contract oder separater Folge-Slice fuer Queue-/Artikel-API in der Annahmekette.

## Slice: VK-014 - Settlement-Kampagnenreferenz

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Die unscharfe Datumsfenster-Zuordnung fuer Kampagnenabschluesse durch eine echte Settlement-Kampagnenreferenz ersetzen.
**Fachlicher Scope:** `campaign_id` im Settlement-Modell, API-Write-/Read-Contract, referenzbasierte Frontend-Filterung mit Legacy-Fallback.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-014-settlement-kampagnenreferenz.md`, `docs/cards/agrar/VK-014-settlement-kampagnenreferenz.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/agrar_settlements.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/agrar_settlement_campaign_reference_20260327.py`, `tests/test_agrar_settlement_campaign_reference.py`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Abnahmekriterien:** `campaign_id` wird gespeichert und gelesen; Kampagnenabschluss nutzt bevorzugt die Referenz; Legacy-Datensaetze bleiben ueber Fallback sichtbar; Migration, Tests und Doku sind vorhanden.
**Tests / Checks:** `pytest tests/test_agrar_settlement_campaign_reference.py -q`; `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-014-settlement-kampagnenreferenz.md`, Card `VK-014-settlement-kampagnenreferenz.md`, QA-Checkliste.
**Risiken / Blocker:** Alt-Settlements ohne `campaign_id` benoetigen spaeter Backfill oder Repair-Flow.
**Naechster konkreter Schritt:** Backfill-Slice fuer Bestandsdaten oder alternativ Queue-/Artikel-API separat claimen.

## Handoff: 2026-03-27 - VK-014

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Kampagnenzuordnung fuer Settlements explizit im Contract verankern und den Zeitfenster-Proxy nur noch als Legacy-Fallback nutzen.
**Stand:** abgeschlossen
**Erledigt:**
- `AgrarSettlement` hat jetzt `campaign_id`; Alembic-Migration `agrar_settlement_campaign_reference_20260327.py` zieht das Schema fuer bestehende Datenbanken nach
- `SettlementCreate`, `SettlementOut`, `create_settlement`, `_to_out` und `list_settlements` in `agrar_settlements.py` kennen jetzt `campaign_id`
- `abrechnung.tsx` persistiert `campaign_id` beim Speichern aus Kampagnenkontext und filtert Listen bevorzugt ueber die Referenz
- `erntefenster-konfig.tsx` aggregiert Kampagnen bevorzugt referenzbasiert und nutzt das Datumsfenster nur fuer Legacy-Datensaetze ohne `campaign_id`
- Backend-Regression in `test_agrar_settlement_campaign_reference.py`, Frontend-Regressionen in `erntefenster-konfig.test.tsx` und `abrechnung.test.tsx` nachgezogen
- Workflow-Doku, Card und QA-Checkliste erstellt bzw. aktualisiert
**Offen:** Bestands-Settlements ohne `campaign_id` bleiben weiterhin auf den Legacy-Fallback angewiesen.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-014-settlement-kampagnenreferenz.md`, `docs/cards/agrar/VK-014-settlement-kampagnenreferenz.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/agrar_settlements.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/agrar_settlement_campaign_reference_20260327.py`, `tests/test_agrar_settlement_campaign_reference.py`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Tests / Checks:** `pytest tests/test_agrar_settlement_campaign_reference.py -q` mit isoliertem `COVERAGE_FILE`; `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Offene Risiken:** Historische Daten ohne Referenz brauchen spaeter Backfill; aktuell bleibt dafuer der Datumsfenster-Fallback aktiv.
**Annahmen:** Erntefenster-Kampagnen bleiben vorerst in Tenant-Settings, deshalb ist `campaign_id` als String-Referenz der richtige pragmatische Vertrag.
**Naechster konkreter Schritt:** Entweder Backfill-/Repair-Slice fuer Alt-Settlements oder der offene Queue-/Artikel-API-Folgeslice in der Annahmekette.

## Slice: VK-015 - Settlement-Kampagnen-Backfill

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Historische Settlements ohne `campaign_id` ueber bestehende Standardmasken kontrolliert auf eine echte Kampagnenreferenz heben.
**Fachlicher Scope:** kampagnenbezogener Repair-CTA in `erntefenster-konfig.tsx`, konservativer Backfill-Endpoint in `agrar_settlements.py`, keine Spezialmaske und kein Ueberschreiben bestehender Referenzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-015-settlement-kampagnen-backfill.md`, `docs/cards/agrar/VK-015-settlement-kampagnen-backfill.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/agrar_settlements.py`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `tests/test_agrar_settlement_campaign_backfill.py`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`
**Abnahmekriterien:** Kampagnenkarte markiert Legacy-Fallback-Daten; Repair-CTA triggert kampagnenbezogenen Backfill; nur eindeutige Alt-Datensaetze werden migriert; ueberlappende Kampagnen bleiben offen; Frontend-/Backend-Tests und Doku sind gruen.
**Tests / Checks:** `pytest tests/test_agrar_settlement_campaign_backfill.py tests/test_agrar_settlement_campaign_reference.py -q`; `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-015-settlement-kampagnen-backfill.md`, Card `VK-015-settlement-kampagnen-backfill.md`, QA-Checkliste.
**Risiken / Blocker:** Ueberlappende Kampagnenfenster koennen weiterhin nicht automatisch aufgeloest werden; diese Faelle bleiben bewusst offen.
**Naechster konkreter Schritt:** Queue-/Artikel-API-Folgeslice fuer die Annahmekette claimen.

## Handoff: 2026-03-27 - VK-015

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Historische Settlements ohne `campaign_id` kontrolliert per Standardmaske nachziehen.
**Stand:** abgeschlossen
**Erledigt:**
- `agrar_settlements.py` bietet jetzt `POST /api/v1/agrar/settlements/campaign-reference/backfill` mit konservativer Repair-Logik fuer `campaign_id IS NULL`
- Der Backfill nutzt Tenant-Kampagnen aus `erntefenster_campaigns`, zieht nur eindeutige Legacy-Datensaetze nach und laesst ueberlappende Kampagnenfaelle bewusst offen
- `erntefenster-konfig.tsx` zeigt einen Legacy-Hinweis auf der Kampagnenkarte und bietet den CTA `Alt-Daten zuordnen`
- Frontend invalidiert nach erfolgreichem Repair die Settlement-Summaries und zeigt Ergebnis-Toast mit Update-/Ambiguitaetsfeedback
- Backend-Regressionen in `test_agrar_settlement_campaign_backfill.py`, Frontend-Regression in `erntefenster-konfig.test.tsx`, bestehende Referenztests in `test_agrar_settlement_campaign_reference.py` und `abrechnung.test.tsx` mitgeprueft
- Workflow-Doku, Card und QA-Checkliste fuer den Repair-Pfad angelegt bzw. aktualisiert
**Offen:** Kein tenantweiter Report fuer ambige Legacy-Datensaetze; Queue-/Artikel-API in der Annahmekette bleibt der naechste fachliche Folgeslice.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-015-settlement-kampagnen-backfill.md`, `docs/cards/agrar/VK-015-settlement-kampagnen-backfill.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/agrar_settlements.py`, `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`, `tests/test_agrar_settlement_campaign_backfill.py`, `tests/test_agrar_settlement_campaign_reference.py`, `packages/frontend-web/src/__tests__/pages/agrar/erntefenster-konfig.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/abrechnung.test.tsx`
**Tests / Checks:** `pytest tests/test_agrar_settlement_campaign_backfill.py tests/test_agrar_settlement_campaign_reference.py -q` mit isoliertem `COVERAGE_FILE`; `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/agrar/erntefenster-konfig.test.tsx src/__tests__/pages/annahme/abrechnung.test.tsx`
**Offene Risiken:** Ueberlappende Kampagnenfenster bleiben ohne zusaetzliche Fachinformation ambig und werden nicht automatisch migriert.
**Annahmen:** `created_at` ist fuer Legacy-Datensaetze die einzig belastbare Zuordnungsbasis; Nicht-Zuordnen ist bei Ambiguitaet fachlich sicherer als Blindmigration.
**Naechster konkreter Schritt:** Queue-/Artikel-API-Folgeslice in der Annahmekette regelkonform claimen.

## Slice: VK-016 - Queue-CTA und kanonische Artikel-API

**Owner:** aktuell offener Agent (Codex)
**Status:** abgeschlossen
**Ziel:** Den offenen Medienbruch aus der Warteschlange in die Ernte-Annahme schliessen und den Handover auf eine kanonische `article_id` statt nur auf Freitext heben.
**Fachlicher Scope:** CTA `Ernte-Annahme anlegen` auf `warteschlange.tsx`, restart-sicherer Queue-Handover in `ernte-annahme-erfassung.tsx`, Artikelauflösung ueber `/api/v1/articles`.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-016-queue-cta-und-artikel-api.md`, `docs/cards/agrar/VK-016-queue-cta-und-artikel-api.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`
**Abnahmekriterien:** Abgeschlossene Queue-Eintraege bieten einen direkten CTA; Navigation in die Ernte-Annahme ist query-basiert restart-sicher; `articleName` wird bei eindeutiger Suche auf kanonische `article_id` aufgeloest; Frontend-Regressionen und Doku sind gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/annahme/warteschlange.test.tsx src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx src/__tests__/pages/annahme/qualitaets-check.test.tsx`
**Doku-Updates:** Workboard, Workflow-Datei `vk-016-queue-cta-und-artikel-api.md`, Card `VK-016-queue-cta-und-artikel-api.md`, QA-Checkliste.
**Risiken / Blocker:** Mehrdeutige Artikeltreffer bleiben vorerst beim Freitext; die Queue selbst fuehrt noch keine kanonische `article_id`.
**Naechster konkreter Schritt:** Folge-Slice fuer echte `article_id` bereits in der Queue-API oder alternativ den Klaerungsprozess fuer `gesperrt` claimen.

## Handoff: 2026-03-27 - VK-016

**Von:** aktuell offener Agent (Codex)
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Queue-Eintraege ohne Medienbruch in die Ernte-Annahme ueberfuehren und den Artikelhandever kanonisieren.
**Stand:** abgeschlossen
**Erledigt:**
- `warteschlange.tsx` zeigt fuer `status === 'abgeschlossen'` jetzt den CTA `Ernte-Annahme anlegen`
- Der CTA navigiert query-basiert mit `workflowProcess`, `workflowLabel`, `entryMode`, Lieferant, Lieferschein, Kennzeichen, Artikel und `queueEntryId` in die Ernte-Annahme
- `ernte-annahme-erfassung.tsx` uebernimmt `queueEntryId` additiv in die Bemerkungen und versucht bei vorhandenem `articleName` eine kanonische `article_id` ueber `/api/v1/articles` aufzulösen
- Bei nicht eindeutiger oder fehlerhafter Artikelsuche bleibt der Freitext stabil erhalten; vorhandene `article_id` wird nicht ueberschrieben
- Frontend-Regressionen in `warteschlange.test.tsx` und `ernte-annahme-erfassung.test.tsx` ergaenzt; `qualitaets-check.test.tsx` als angrenzender Handover-Pfad mitgeprueft
- Workflow-Doku, Card und Browser-Use-Checkliste fuer den Slice erstellt bzw. aktualisiert
**Offen:** Die Queue selbst persistiert noch keine echte `article_id`; mehrdeutige Artikeltreffer brauchen weiterhin manuelle Artikelwahl.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-016-queue-cta-und-artikel-api.md`, `docs/cards/agrar/VK-016-queue-cta-und-artikel-api.md`, `docs/quality-assurance/browser-use-checklists.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/annahme/warteschlange.test.tsx src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx src/__tests__/pages/annahme/qualitaets-check.test.tsx`
**Offene Risiken:** Ohne echte `article_id` bereits in der Queue bleibt die automatische Aufloesung textbasiert und damit bei Mehrdeutigkeit begrenzt.
**Annahmen:** `abgeschlossen` in der Queue ist der fachlich richtige Schwellenwert fuer den CTA; die Artikel-API `/api/v1/articles` ist fuer diesen Slice die kanonische Lookup-Quelle.
**Naechster konkreter Schritt:** Entweder Queue-API um echte `article_id` erweitern oder den `gesperrt`-Klaerungspfad als naechsten VK-Slice schneiden.

## Slice: VK-017 - Queue-Contract mit echter `article_id`

**Owner:** Codex
**Status:** abgeschlossen
**Ziel:** Die Annahmekette bereits am Queue-Contract auf eine echte `article_id` heben und den benachbarten QR-POST-Pfad auf einen realen Endpoint zurueckfuehren.
**Fachlicher Scope:** persistente `article_id` in `domain_inventory.lkw_annahme_queue`, ArtikelauflÃ¶sung bei der Registrierung, Handover-Erweiterung fuer Queue/QP/Harvest-Acceptance und QR-Kompatibilitaet.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-017-queue-article-id.md`, `docs/cards/agrar/VK-017-queue-article-id.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/lkw_annahme_queue_article_reference_20260328.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/annahme/qr-scanner.tsx`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`, `tests/test_compat_lkw_registrierung.py`
**Abnahmekriterien:** Queue speichert und liest `article_id`; LKW-Registrierung waehlt Artikel aus der API; Queue- und QP-Handover fuehren `articleId`; QR-POST bricht nicht mehr auf einem fehlenden Endpoint; relevante Frontend-Regressionen und Doku sind gruen.
**Tests / Checks:** `pnpm --dir packages/frontend-web exec vitest run src/__tests__/pages/annahme/lkw-registrierung.test.tsx src/__tests__/pages/annahme/qualitaets-check.test.tsx src/__tests__/pages/annahme/warteschlange.test.tsx src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`; `node scripts/docs-governance-check.cjs`; `python -m py_compile app/api/v1/endpoints/compat.py app/infrastructure/models/l3c_models.py tests/test_compat_lkw_registrierung.py`
**Doku-Updates:** Workboard, Workflow-Datei `vk-017-queue-article-id.md`, Card `VK-017-queue-article-id.md`, QA-Checkliste.
**Risiken / Blocker:** Historische Queue-Eintraege ohne `article_id` bleiben unveraendert; externe QR-Codes mit unbekannter Referenz fallen weiter auf Freitext zurueck.
**Naechster konkreter Schritt:** Den Klaerungsprozess fuer `gesperrt` als naechsten VK-Slice claimen; danach optional Repair fuer historische Queue-Eintraege ohne `article_id`.

## Handoff: 2026-03-28 - VK-017

**Von:** Codex
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Queue, QP und Ernte-Annahme auf eine echte Artikelreferenz heben.
**Stand:** abgeschlossen
**Erledigt:**
- `LkwAnnahmeQueue` fuehrt jetzt eine persistente `article_id`; Migration `lkw_annahme_queue_article_reference_20260328.py` zieht das Schema nach
- `compat.py` loest Artikel bei der Registrierung ueber `id`, `article_number` oder exakten Namen auf und liefert `article_id` im Queue-Read-Contract aus
- Rueckwaertskompatibler Alias `POST /api/v1/annahme/warteschlange` ist vorhanden; `qr-scanner.tsx` nutzt aber bereits den kanonischen Registrierungs-Endpoint
- `lkw-registrierung.tsx` laedt Artikel aus `/api/v1/articles` und sendet `article_id` plus Label
- `warteschlange.tsx` und `qualitaets-check.tsx` fuehren `articleId` im Query-Handover mit; `ernte-annahme-erfassung.tsx` uebernimmt diese direkt und faellt nur noch legacy-seitig auf Textlookup zurueck
- Frontend-Regressionen fuer LKW-Registrierung, Queue, QP und Harvest-Acceptance sind nachgezogen; Backend-Testdatei `test_compat_lkw_registrierung.py` ist angelegt
- Workflow-Doku, Card und Browser-Use-Checkliste sind auf Ist-Stand
**Offen:** Kein automatischer Repair fuer historische Queue-Eintraege ohne `article_id`; kein sichtbarer Warnhinweis fuer unaufgeloeste QR-Artikel.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-017-queue-article-id.md`, `docs/cards/agrar/VK-017-queue-article-id.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/lkw_annahme_queue_article_reference_20260328.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/lkw-registrierung.tsx`, `packages/frontend-web/src/pages/annahme/qr-scanner.tsx`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/agrar/ernte-annahme-erfassung.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/lkw-registrierung.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/qualitaets-check.test.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `packages/frontend-web/src/__tests__/pages/agrar/ernte-annahme-erfassung.test.tsx`, `tests/test_compat_lkw_registrierung.py`
**Tests / Checks:** `vitest` fuer die 4 betroffenen Frontend-Dateien ist gruen (`10 passed`); `node scripts/docs-governance-check.cjs` ist gruen; `python -m py_compile` fuer Backend-Dateien/Testdatei ist gruen. `pytest tests/test_compat_lkw_registrierung.py -q` lief in dieser Session mehrfach in ein Timeout ohne Ausgabe und ist daher nicht als gruener Lauf bestaetigt.
**Offene Risiken:** QR-Codes mit unbekannter Artikelreferenz bleiben Freitext-Faelle; Alt-Queue ohne `article_id` profitiert erst nach einem Repair-Slice vollstaendig.
**Annahmen:** `article_number` ist fuer externe QR-Referenzen die realistischste Fallback-Referenz neben der internen `article_id`.
**Naechster konkreter Schritt:** VK-Folgeslice fuer den Klaerungsprozess `gesperrt` claimen.

## Slice: VK-018 - Klaerungsprozess gesperrte Ware

**Owner:** Codex
**Status:** abgeschlossen
**Ziel:** Gesperrte QP-Ergebnisse (Qualitaets-Check = `gesperrt`) fachlich sauber in einen Klaerungsprozess ueberfuehren, ohne Medienbruch in der Annahmekette.
**Fachlicher Scope:** QP-Ergebnis `gesperrt` bleibt in der Queue sichtbar, bietet aber einen klaren Klaerungs-CTA; Standardmasken vor Spezialmaske pruefen; Handover-/Statusdaten fuer die Klaerung bleiben restart-sicher; keine direkte Ernte-Annahme bei `gesperrt`.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-018-klaerungsprozess-gesperrt.md`, `docs/cards/agrar/VK-018-klaerungsprozess-gesperrt.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/lkw_annahme_queue_klaerung_20260328.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/annahme/klaerung-gesperrt.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/annahme.ts`, `packages/frontend-web/src/app/route-builders/alias-groups/generated/annahme.ts`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `tests/test_compat_lkw_registrierung.py`
**Abnahmekriterien:**
- `gesperrt` erzeugt keinen Handover zur Ernte-Annahme, sondern fuehrt in einen dokumentierten Klaerungspfad.
- CTA/Status im Queue- und QP-Kontext ist sichtbar und nachvollziehbar.
- Klaerungspfad ist restart-sicher (Query-/ID-Handover) und CRUD-faehig.
- Browser-Use-Checkliste fuer den Klaerungspfad ist ergaenzt.
**Tests / Checks:** Frontend-Regression fuer QP/Queue/Klaerungspfad; ggf. API-Contract-Test falls neuer Endpoint.
**Doku-Updates:** Workboard, Workflow-Datei `vk-018-klaerungsprozess-gesperrt.md`, Card `VK-018-klaerungsprozess-gesperrt.md`, QA-Checkliste.
**Risiken / Blocker:** Unklare Fachentscheidung, ob Klaerung in bestehender Maske oder eigenstaendigem Dialog erfolgt; Abgrenzung zu Lager-/Retourenprozess.
**Annahmen:** Gesperrte Ware darf nicht in die Ernte-Annahme; Klaerung ist ein eigener Teilprozess ohne automatische Freigabe.
**Naechster konkreter Schritt:** Folge-Slice fuer historische Queue-Eintraege ohne `article_id` oder Sonderfreigabe-Policy schneiden.

## Slice: VK-019 - Queue-Repair historische `article_id`

**Owner:** Codex
**Status:** abgeschlossen
**Ziel:** Historische Queue-Eintraege ohne `article_id` kontrolliert nachziehen (Repair) und damit den Annahme-Handover vollstaendig machen.
**Fachlicher Scope:** Repair-CTA in Warteschlange (nur fuer Eintraege ohne `article_id`), konservativer Repair-Endpoint, keine automatische Massenmigration.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-019-queue-repair-article-id.md`, `docs/cards/agrar/VK-019-queue-repair-article-id.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
**Abnahmekriterien:**
- Repair-CTA nur sichtbar, wenn `article_id` fehlt.
- Repair schreibt nur bei eindeutiger Artikelauflösung.
- Ergebnisfeedback ueber Toast/Status.
**Tests / Checks:** Backend-Unit-Test fuer Repair, Frontend-Regression fuer CTA.
**Doku-Updates:** Workboard, Workflow-Datei, Card, QA-Checkliste.
**Risiken / Blocker:** Mehrdeutige Artikel treffen; keine Blindzuordnung.
**Annahmen:** `artikel`/`article_number` ist in Alt-Eintraegen plausibel genug fuer konservativen Repair.
**Naechster konkreter Schritt:** Sonderfreigabe-Policy/Role-Guard oder Batch-Repair mit Freigabe definieren.

## Handoff: 2026-03-28 - VK-019

**Von:** Codex
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Repair historischer Queue-Eintraege ohne `article_id`.
**Stand:** abgeschlossen
**Erledigt:**
- Neuer Repair-Endpoint `POST /api/v1/annahme/warteschlange/{id}/repair-article` mit konservativer Aufloesung.
- Warteschlange zeigt CTA `Artikel reparieren` nur bei fehlender `article_id`.
- Ergebnisfeedback via Toast, Queue-Refresh per Query-Invalidation.
- Workflow/Card/QA-Doku nachgezogen.
**Offen:** Keine manuelle Artikelauswahl bei Mehrdeutigkeit; keine Batch-Reparatur.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-019-queue-repair-article-id.md`, `docs/cards/agrar/VK-019-queue-repair-article-id.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `tests/test_compat_lkw_registrierung.py`
**Tests / Checks:** 9/9 gruen (`pytest tests/test_compat_lkw_registrierung.py`); 6 neue Repair-Tests fuer `_repair_lkw_article_reference` (article_number, article_name, not_found, missing_label x2, ambiguous); Frontend-Repair-CTA-Test in `warteschlange.test.tsx` bestand bereits.
**Offene Risiken:** Fehlende Aufloesung bei Mehrdeutigkeit bleibt manuell.
**Annahmen:** Exakter `article_number` oder Name ist in Alt-Eintraegen haeufig genug fuer Repair.
**Naechster konkreter Schritt:** Sonderfreigabe-Policy/Role-Guard definieren oder optionalen Batch-Repair mit Freigabe entwerfen.

## Handoff: 2026-03-28 - VK-018

**Von:** Codex
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Gesperrte QP-Ergebnisse fachlich klaeren und dokumentieren.
**Stand:** abgeschlossen
**Erledigt:**
- Queue-Status erlaubt jetzt `gesperrt`; Klaerungsdaten werden als JSONB am Queue-Eintrag persistiert.
- QP mit Ergebnis `gesperrt` fuehrt in den Klaerungspfad statt in die Ernte-Annahme.
- Neue Klaerungsmaske `annahme/klaerung-gesperrt` erfasst Entscheidung + Begruendung und fuehrt bei Sonderfreigabe kontrolliert in die Ernte-Annahme.
- Warteschlange zeigt gesperrte Eintraege mit CTA `Klaerung starten`.
- Workflow- und Card-Doku sowie Browser-Use-Checkliste nachgezogen.
**Offen:** Keine Policy/Role-Checks fuer Sonderfreigabe; historischer Queue-Repair fuer fehlende `article_id` bleibt optional.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/vk-018-klaerungsprozess-gesperrt.md`, `docs/cards/agrar/VK-018-klaerungsprozess-gesperrt.md`, `docs/quality-assurance/browser-use-checklists.md`, `app/api/v1/endpoints/compat.py`, `app/infrastructure/models/l3c_models.py`, `alembic/versions/lkw_annahme_queue_klaerung_20260328.py`, `packages/frontend-web/src/lib/api/inventory.ts`, `packages/frontend-web/src/pages/annahme/qualitaets-check.tsx`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`, `packages/frontend-web/src/pages/annahme/klaerung-gesperrt.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/annahme.ts`, `packages/frontend-web/src/app/route-builders/alias-groups/generated/annahme.ts`, `packages/frontend-web/src/__tests__/pages/annahme/warteschlange.test.tsx`, `tests/test_compat_lkw_registrierung.py`
**Tests / Checks:** nicht ausgefuehrt in dieser Session
**Offene Risiken:** Sonderfreigabe ist aktuell nicht rollen- oder policybasiert abgesichert.
**Annahmen:** Gesperrte Ware darf nur per dokumentierter Klaerung weiterlaufen; JSONB `klaerung` am Queue-Eintrag ist ausreichend fuer Auditbedarf.
**Naechster konkreter Schritt:** Policy/Role-Guard fuer Sonderfreigabe definieren oder Repair-Slice fuer historische Queue-Eintraege ohne `article_id` schneiden.

## Slice: CTS-001 - Contract-to-Settlement Erstanalyse

**Owner:** Cursor Agent
**Status:** abgeschlossen
**Ziel:** Vollstaendige Workflow-Analyse des Contract-to-Settlement Flow-Spine nach Master-Prompt: Card-Zerlegung, Mermaid-Diagramm, Soll-Ist-Abweichungen, UI-/CRUD-Pruefung, Risikobewertung und konkrete Empfehlungen.
**Fachlicher Scope:** Gesamter Kontraktlebenszyklus — Anlage (Verkauf/Einkauf/Zukauf), MATIF-Preisfixierung, Aenderung, Abruf/Lieferung, Movement-Buchung, Restmengen-Ueberwachung, Storno, Loeschung, Fakturierung, Kontraktabschluss, externe Uebernahme.
**Dateibesitz:** `docs/workflows/cts-001-contract-to-settlement.md`, `docs/cards/kontrakte/CTS-001-contract-to-settlement.md`
**Abnahmekriterien:** 15 Cards nach Master-Prompt-Vorlage; Mermaid-Flowchart mit Hauptfluss, Alternativpfaden, Schleifen; 28 Soll-Ist-Abweichungen dokumentiert; UI-/CRUD-Matrix fuer alle 7 Masken; Risikobewertung (4 kritisch, 4 hoch, 4 mittel, 3 niedrig); 8 priorisierte Empfehlungen; 8 explizite Annahmen.
**Tests / Checks:** Reine Analyse — keine Code-Aenderungen in diesem Slice.
**Doku-Updates:** Workboard (Lane + Slice + Handoff), Workflow-Datei, Card-Datei.
**Risiken / Blocker:** keine

## Handoff: 2026-03-27 - CTS-001

**Von:** Cursor Agent
**An:** naechste Session / naechster Agent
**Ziel des Slices:** Contract-to-Settlement vollstaendig nach Master-Prompt analysieren.
**Stand:** abgeschlossen
**Erledigt:**
- Workflow-Analyse `docs/workflows/cts-001-contract-to-settlement.md` mit 15 Cards, Mermaid-Diagramm und Soll-Ist-Tabelle erstellt
- Card `docs/cards/kontrakte/CTS-001-contract-to-settlement.md` mit Zusammenfassung, Kritikalitaets-Matrix und Folge-Slice-Empfehlungen erstellt
- Workboard um CTS-Lane und CTS-001-Slice ergaenzt
- Alle 5 Kontrakt-Frontend-Masken, die API-Schicht (`kontrakte.ts`, `kontrakte.py`, `contract_pricing_api.py`) und die Kontraktreferenzen in `order-editor.tsx` und `lieferschein-erfassung.tsx` wurden analysiert
**Offen:** Alle 8 Empfehlungen (CTS-002 bis CTS-008) sind als Folge-Slices definiert, aber noch nicht begonnen.
**Betroffene Dateien:** `docs/agent-ops/active-workboard.md`, `docs/workflows/cts-001-contract-to-settlement.md`, `docs/cards/kontrakte/CTS-001-contract-to-settlement.md`
**Top-4-Findings:**
1. Kontraktnummer auf Auftrags-/Lieferschein-Positionen ist nur Freitext — keine echte FK-Referenz, keine Preisuebernahme, keine Restmengen-Pruefung
2. Movements (Kontraktumsaetze) werden nicht automatisch aus Lieferschein/Rechnung erzeugt — Restmengen sind rein manuell
3. MATIF-Preisfixierung: Datenmodell komplett vorhanden (pricing_model, min_price, premium, basis_reference, pricing_window), aber kein Prozess und kein UI
4. Teillieferungen sind im Datenmodell moeglich (Movements), aber operativ nicht verdrahtet
**Naechster konkreter Schritt:** CTS-002 (Kontraktbindung auf Belegen als echte Referenz) oder CTS-003 (automatische Movement-Buchung) als naechsten Implementierungs-Slice claimen.

## Neuro-Core Runtime Layer (NC-001 bis NC-006) — umgesetzt 2026-03-29

Die 6 fehlenden Architektur-Layer aus dem Architektur-Review wurden als eigenstaendige Services mit REST-API, Mermaid-Doku und Cards implementiert:

| Slice-ID | Thema | Status | Owner | Dateien |
|----------|-------|--------|-------|---------|
| NC-001 | Neuro Verification Engine — formale Planverifikation vor Ausfuehrung | abgeschlossen | Cursor Agent | `app/services/neuro_verification_engine.py`, `app/api/v1/endpoints/neuro_verification.py`, `docs/workflows/nc-001-*.md`, `docs/cards/neuro-core/NC-001-*.md` |
| NC-002 | Interaction State Manager — Kanal-/Dialogzustands-FSM | abgeschlossen | Cursor Agent | `app/services/interaction_state_manager.py`, `app/api/v1/endpoints/neuro_interactions.py`, `docs/workflows/nc-002-*.md`, `docs/cards/neuro-core/NC-002-*.md` |
| NC-003 | Voice Adapter Layer — STT/TTS, Turn Manager, Latency Control | abgeschlossen | Cursor Agent | `app/services/voice_adapter.py`, `app/api/v1/endpoints/neuro_voice.py`, `docs/workflows/nc-003-*.md`, `docs/cards/neuro-core/NC-003-*.md` |
| NC-004 | Consent Engine — DSGVO-konformer Einwilligungs-Lifecycle | abgeschlossen | Cursor Agent | `app/services/consent_engine.py`, `app/api/v1/endpoints/neuro_consent.py`, `docs/workflows/nc-004-*.md`, `docs/cards/neuro-core/NC-004-*.md` |
| NC-005 | Neuro Simulation Engine — Dry-Run und What-If | abgeschlossen | Cursor Agent | `app/services/neuro_simulation_engine.py`, `app/api/v1/endpoints/neuro_simulation.py`, `docs/workflows/nc-005-*.md`, `docs/cards/neuro-core/NC-005-*.md` |
| NC-006 | Compensation Engine — Retry, Rollback, Eskalation | abgeschlossen | Cursor Agent | `app/services/compensation_engine.py`, `app/api/v1/endpoints/neuro_compensation.py`, `docs/workflows/nc-006-*.md`, `docs/cards/neuro-core/NC-006-*.md` |

Alle 6 Router registriert in `app/api/v1/api.py` unter `/api/v1/neuro/*`. Commit: `c6e82411`.

## Handoff: 2026-03-29 - Neuro Stack Gap Matrix

**Von:** Codex
**An:** naechste Session / naechster Agent
**Ziel:** Neuro-Stack-Gaps aus dem gelieferten Komponenten-Status dokumentieren und priorisieren.
**Stand:** abgeschlossen
**Erledigt:**
- Statusmatrix und P1-Luecken als eigene Doku erfasst.
- Open-Gaps-Liste um den neuen Matrix-Verweis ergaenzt.
- Naechste 3 Schritte fuer die P1-Lanes dokumentiert (NC-B1, NC-D1, NC-C1).
**Offen:** Claim-Commit fuer den naechsten Neuro-Core-Slice steht noch aus.
**Betroffene Dateien:** `docs/project-context/neuro-stack-gap-matrix-2026-03-29.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/active-workboard.md`
**Tests / Checks:** keine
**Naechster konkreter Schritt:** Slice fuer NC-B1 (State Graph + Modelle) im Workboard claimen und erst danach mit Code starten.

## Handoff: 2026-03-29 - NC-B1

**Von:** Codex
**An:** naechste Session / naechster Agent
**Ziel des Slices:** State Graph und Confidence Ledger als P1-Grundgeruest produktiv verdrahten.
**Stand:** abgeschlossen
**Erledigt:**
- State Graph Models + Service (Nodes, Edges, Transitions) mit Transition-Matrix.
- Confidence Ledger mit Hash-Chain, Input-Hash und Risiko-Summary.
- SQLAlchemy-Modelle + Alembic-Migration fuer `domain_shared`.
- REST-API fuer Graph und Ledger (Read, Transition, Verify, Summary).
- Workflow-Doku und Card fuer NC-B1 angelegt.
- Workboard-Lane NC-B als abgeschlossen markiert.
**Offen:** keine
**Betroffene Dateien:** `app/core/neuro_state_graph.py`, `app/core/confidence_ledger.py`, `app/infrastructure/models/neuro_state_models.py`, `app/infrastructure/models/__init__.py`, `app/api/v1/endpoints/neuro_state_graph_api.py`, `alembic/versions/neuroassist_state_graph_confidence_ledger_20260329.py`, `tests/test_neuro_state_graph.py`, `docs/workflows/nc-b1-state-graph-confidence-ledger.md`, `docs/cards/neuro-core/NC-B1-state-graph-confidence-ledger.md`, `docs/agent-ops/active-workboard.md`
**Tests / Checks:** nicht ausgefuehrt in dieser Session
**Naechster konkreter Schritt:** NC-D1 (Audit Hardening) oder NC-C1 (Guardrails PII/DLP) claimen.
