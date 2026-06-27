---
title: Workflow-Index
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: >
  Katalog aller 161 Workflow-Dokumente in docs/workflows/ — kategorisiert nach
  Domäne, Security, Integration und NeuroCore. Dateien sind im Repo unter
  docs/workflows/ verfügbar, aber nicht im gebauten Docs-Site enthalten.
---

# Workflow-Index

Alle Workflow-Dokumente liegen im Repo unter `docs/workflows/`. Sie sind nicht im gebauten Docs-Site enthalten (ausgenommen via `exclude_docs`). Dieser Index katalogisiert sie nach Kategorie und gibt eine Kurzbeschreibung für die Navigation.

## Geschäftsprozess-Workflows (vk / otc / p2p / cts / crm / fin / inv / rek)

| Datei | Beschreibung |
|-------|-------------|
| `vk-010-ernte-annahme.md` | Ernteannahme – Wiegung, Qualitätsprüfung, Einbuchung |
| `vk-011-qp-handover-und-lkw-validierung.md` | QP-Übergabe und LKW-Validierung |
| `vk-012-annahme-abrechnung.md` | Annahme-Abrechnung |
| `vk-013-kampagnenabschluss.md` | Kampagnenabschluss |
| `vk-014-settlement-kampagnenreferenz.md` | Settlement Kampagnenreferenz |
| `vk-015-settlement-kampagnen-backfill.md` | Settlement Backfill |
| `vk-016-queue-cta-und-artikel-api.md` | Queue CTA + Artikel-API |
| `vk-017-queue-article-id.md` | Queue Artikel-ID |
| `vk-018-klaerungsprozess-gesperrt.md` | Klärungsprozess gesperrter Positionen |
| `vk-019-queue-repair-article-id.md` | Queue Repair Artikel-ID |
| `vk-020-rohware-wizard-schrittvalidierung.md` | Rohware-Wizard Schritt-Validierung |
| `otc-010-order-to-cash.md` | Order-to-Cash Hauptprozess |
| `otc-011-zahlungseingang-und-abstimmung.md` | Zahlungseingang und Abstimmung |
| `p2p-001-procure-to-pay-direktbestellung.md` | Procure-to-Pay Direktbestellung |
| `p2p-040-procure-to-pay-vorbelegung.md` | P2P Vorbelegung |
| `p2p-040-vorbelegung-requisition-vertrag-rfq.md` | Vorbelegung Requisition/Vertrag/RFQ |
| `p2p-050-wizard-schrittvalidierung.md` | P2P Wizard Schritt-Validierung |
| `cts-001-contract-to-settlement.md` | Kontrakt-to-Settlement |
| `cts-009-rohwaren-positionsmonitor.md` | Rohwaren-Positionsmonitor |
| `crm-001-crm-to-revenue.md` | CRM-to-Revenue |
| `fin-001-finance-to-close.md` | Finance-to-Close |
| `fin-001-finance-to-reporting.md` | Finance-to-Reporting |
| `finance-closing-compatibility-2026-06-26.md` | Finance Closing Kompatibilitätscheck |
| `inv-001-inventory-to-settlement.md` | Inventory-to-Settlement |
| `rek-001-complaint-to-resolution.md` | Reklamation-to-Resolution |
| `svc-001-service-to-customer.md` | Service-to-Customer |
| `cmp-001-compliance-to-report.md` | Compliance-to-Report |
| `com-001-compliance-to-audit.md` | Compliance-to-Audit |

## Domain-Deepening-Workflows (dom-*)

| Datei | Beschreibung |
|-------|-------------|
| `dom-agrar-004-agrar-deepening-2026-06-23.md` | Agrar DOM-004 Spine-Ausbau |
| `dom-compliance-004-compliance-deepening-2026-06-23.md` | Compliance DOM-004 Spine-Ausbau |
| `dom-con-003-fixierung-markt-mahnung.md` | Kontrakt DOM-003: Fixierung/Markt/Mahnung |
| `dom-controlling-004-controlling-deepening-2026-06-23.md` | Controlling DOM-004 Spine-Ausbau |
| `dom-crm-003-fall-und-ownership.md` | CRM DOM-003: Fall/Ownership |
| `dom-doc-003-nachweis-und-rueckmeldung.md` | DOC DOM-003: Nachweis/Rückmeldung |
| `dom-fin-003-fibu-operatorparitaet.md` | FiBu DOM-003: Operator-Parität |
| `dom-finance-004-finance-deepening-2026-06-23.md` | Finance DOM-004 Spine-Ausbau |
| `dom-inv-004-inventory-deepening-2026-06-23.md` | Inventory DOM-004 Spine-Ausbau |
| `dom-log-004-logistik-deepening-2026-06-23.md` | Logistik DOM-004 Spine-Ausbau |
| `dom-proc-003-beschaffungsausnahmen.md` | Procurement DOM-003: Beschaffungsausnahmen |
| `dom-proc-004-procurement-deepening-2026-06-23.md` | Procurement DOM-004 Spine-Ausbau |
| `dom-sales-004-sales-deepening-2026-06-23.md` | Sales DOM-004 Spine-Ausbau |
| `dom-supply-003-physische-kette.md` | Supply DOM-003: Physische Kette |

## Process Kernel & Workflow-Leitstand

| Datei | Beschreibung |
|-------|-------------|
| `flow-spine-instance-lifecycle-overview.md` | Flow-Spine Instanz-Lebenszyklus |
| `kernel-action-execution-mutations.md` | Kernel Action Execution Mutations |
| `valeo-wf-cockpit-001-workflow-leitstand-2026-06-23.md` | Workflow-Leitstand (WF-COCKPIT-001) |

## Security-Workflows (sec-*)

> 34 Dokumente — Härtung aller API-Endpoints, Tenant-Isolation, Security CI Lane, Observability.

| Datei | Beschreibung |
|-------|-------------|
| `sec-001-hardcoded-secrets-remediation.md` | Hardcoded Secrets Bereinigung |
| `sec-002-local-secret-management.md` | Lokales Secret Management |
| `sec-003-auth-tenant-hardening.md` | Auth/Tenant Härtung |
| `sec-004-supplier-portal-hardening.md` | Lieferantenportal Härtung |
| `sec-005-realtime-websocket-hardening.md` | Realtime/WebSocket Härtung |
| `sec-006-accounting-period-tenant-hardening.md` | Buchungsperiode Tenant Härtung |
| `sec-007-creditors-tenant-hardening.md` | Kreditoren Tenant Härtung |
| `sec-008-einkauf-tenant-hardening.md` | Einkauf Tenant Härtung |
| `sec-009-admin-mobile-sql-whitelist.md` | Admin/Mobile SQL-Whitelist |
| `sec-010-vies-xml-hardening.md` | VIES XML Härtung |
| `sec-011-documents-info-disclosure.md` | Dokumente Info-Disclosure |
| `sec-012-webhook-ssrf-hardening.md` | Webhook SSRF Härtung |
| `sec-013-print-xss-hardening.md` | Print XSS Härtung |
| `sec-014-external-vault-startup-guard.md` | External Vault Startup Guard |
| `sec-015-accruals-tenant-hardening.md` | Abgrenzungen Tenant Härtung |
| `sec-016-egress-ssrf-policy.md` | Egress SSRF Policy |
| `sec-017-security-ci-lane.md` | Security CI Lane |
| `sec-018-frontend-html-sink-inventory.md` | Frontend HTML Sink Inventar |
| `sec-019-ap-approval-workflow-hardening.md` | AP Approval Workflow Härtung |
| `sec-020-subsidiary-ledger-reconciliation-hardening.md` | Nebenbuch-Abstimmung Härtung |
| `sec-021-tax-keys-hardening.md` | Steuerschlüssel Härtung |
| `sec-022-vat-return-export-hardening.md` | USt-Voranmeldung Export Härtung |
| `sec-023-sales-credit-notes-hardening.md` | Gutschriften Härtung |
| `sec-024-sales-reports-hardening.md` | Verkaufsberichte Härtung |
| `sec-025-sales-delivery-notes-hardening.md` | Lieferscheine Härtung |
| `sec-026-articles-tenant-hardening.md` | Artikel Tenant Härtung |
| `sec-027-warehouse-transfers-hardening.md` | Lagertransfers Härtung |
| `sec-028-security-observability.md` | Security Observability |
| `sec-029-agrar-contracts-hardening.md` | Agrar-Kontrakte Härtung |
| `sec-030-security-dashboard-alerting.md` | Security Dashboard Alerting |
| `sec-031-sales-orders-hardening.md` | Verkaufsaufträge Härtung |
| `sec-032-sales-offers-hardening.md` | Verkaufsangebote Härtung |
| `sec-034-security-event-persistence.md` | Security Event Persistenz |

## NeuroCore-Workflows (nc-*)

> 24 Dokumente — KI-Kernel, Tool-Broker, Guardrails, Audit-Hardening, Copilot-Backend.

| Datei | Beschreibung |
|-------|-------------|
| `nc-a-neuro-core-kernel.md` | NeuroCore Kernel |
| `nc-001-neuro-verification-engine.md` | Verification Engine |
| `nc-002-interaction-state-manager.md` | Interaction State Manager |
| `nc-003-voice-adapter-layer.md` | Voice Adapter Layer |
| `nc-004-consent-engine.md` | Consent Engine |
| `nc-005-simulation-engine.md` | Simulation Engine |
| `nc-006-compensation-engine.md` | Compensation Engine |
| `nc-a6-neuro-tool-broker.md` | Tool Broker |
| `nc-a7-broker-openapi-execution.md` | Broker OpenAPI Execution |
| `nc-a8-verification-policy-wave2.md` | Verification Policy Wave 2 |
| `nc-a9-intent-llm-fallback.md` | Intent LLM Fallback |
| `nc-a10-dynamic-plan-generation.md` | Dynamic Plan Generation |
| `nc-a11-cross-entity-integrity.md` | Cross-Entity Integrity |
| `nc-a12-risk-scoring.md` | Risk Scoring |
| `nc-a13-tenant-policy-overrides.md` | Tenant Policy Overrides |
| `nc-a14-broker-tenant-overrides.md` | Broker Tenant Overrides |
| `nc-a15-external-http-execution.md` | External HTTP Execution |
| `nc-a16-tool-contract-harmonization.md` | Tool Contract Harmonization |
| `nc-b1-state-graph-confidence-ledger.md` | State Graph Confidence Ledger |
| `nc-c-guardrails-pii.md` | Guardrails PII |
| `nc-d-audit-hardening.md` | Audit Hardening |
| `nc-e-fast-track-compensation.md` | Fast Track Compensation |
| `nc-f-copilot-backend.md` | Copilot Backend |
| `nc-g2-nats-consumer.md` — `nc-g8-monitoring-surfacing.md` | NATS Consumer, Handler, Policy/Prompt Registry, Monitoring |
| `nc-h-channels-integration.md` | Channels Integration |

## Superglue-Integration-Workflows (int-sg-*)

> 56 Dokumente — Compose Stack, Edge Proxy, K8s, Helm, Backup/Restore, Monitoring, Deploy, Secrets, Tool-Lifecycle.

| Prefix | Thema |
|--------|-------|
| `int-sg-021–026` | Compose Stack, Edge Proxy, K8s Base/Overlay, Backup/Restore |
| `int-sg-027–034` | Infra CI, Ops Runbook, ArgoCD, Secrets, Monitoring, Dashboard, Deploy, Bootstrap |
| `int-sg-035–044` | Runtime Contract, REST v1, Run Envelope, Bootstrap/Provisioning, Smoke, Target Structure, Tool Provisioning, Dev Egress, Tenant Bootstrap, Secret Resolver |
| `int-sg-045–056` | Tool Lifecycle, Result Normalization, DMS Connector, Partner EDI, CRM Masterdata, File References, Execute Gates, Idempotency, Quarantine/Retry, Admin Surface, Monitoring, CI Smoke |

## Sonstige

| Datei | Beschreibung |
|-------|-------------|
| `pcp-007-012-agent-ops-rollout.md` | PCP Agent-Ops Rollout |
| `perf-multiuser-001-middleware-asgi-2026-06-25.md` | PERF-MULTIUSER-001 ASGI-Middleware |
| `portal-openapi-summary-gate-2026-06-26.md` | Portal OpenAPI Summary Gate |
| `wave-physical-chain-feed-production-audit-2026-06-12.md` | Physical Chain Feed Production Audit |
| `wave-physical-chain-logistics-audit-2026-06-12.md` | Physical Chain Logistics Audit |
| `wm-agri-silo-supply-chain-integration-2026-06-13.md` | WM-AGRI Silo Supply Chain Integration |
| `workflow-analysis-master-prompt.md` | Master Prompt für Workflow-Analyse (Agent-Nutzung) |

## Hinweis für Entwickler

Die Workflow-Dokumente sind **nicht im gebauten Docs-Site** enthalten. Sie dienen als:

- **Slice-Begleitdokumentation** für den AI-Harness (Claim → YAML → Code → Abschluss)
- **Fachliche Referenz** für Domänenlogik und Prozessketten
- **Analyse-Input** für Agent-gestützte Weiterentwicklung

Zum Lesen direkt im Repo unter `docs/workflows/` navigieren oder via IDE öffnen.
