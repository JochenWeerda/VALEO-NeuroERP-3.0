# Nächste Arbeitsslices (priorisiert)

> Erzeugt am 2026-05-05 21:01:23 aus dem Merge (Fokus-Pfade wie im Kurz-Backlog).
> **Reihenfolge der Slices:** zuerst Bereiche mit der höchsten Dringlichkeit (min. Priorität), dann mehr „Hoch“, dann mehr Einträge.
> **Innerhalb eines Slices:** Hoch → Normal → Niedrig, dann Dateipfad.
> Vollständige Rohdaten: `todo-report.json` → `next_slices`; Zeilenlisten: `todo-repo-scan.md`.

## 1. `erp-domain/src` — 58 TODO(s) (11 Hoch · 47 Normal · 0 Niedrig) _(Hoch zuerst)_

- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/anfrage.controller.ts`:L89 — total: anfragen.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/angebot.controller.ts`:L91 — total: angebote.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/anlieferavis.controller.ts`:L82 — total: avise.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/audit-log.controller.ts`:L26 — total: logs.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/auftragsbestaetigung.controller.ts`:L81 — total: abs.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/rechnungseingang.controller.ts`:L92 — total: rechnungen.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/sales-offer.controller.ts`:L49 — const actorId = 'system' // TODO: Aus Auth-Middleware
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/sales-offer.controller.ts`:L51 — // TODO: CustomerInquiry laden und SalesOffer erstellen
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/sales-offer.controller.ts`:L109 — total: salesOffers.length // TODO: Pagination-Info
- **[Hoch] [TODO]** `packages/erp-domain/src/presentation/controllers/workflow-execution.controller.ts`:L83 — total: executions.length // TODO: Pagination-Info
- *… 48 weitere in diesem Slice*

## 2. `services/crm-marketing` — 20 TODO(s) (0 Hoch · 20 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-marketing/app/api/v1/endpoints/campaigns.py`:L63 — created_by="system",  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-marketing/app/api/v1/endpoints/campaigns.py`:L148 — campaign.updated_by = "system"  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-marketing/app/api/v1/endpoints/campaigns.py`:L373 — TODO: Implement test send logic
- **[Normal] [TODO]** `services/crm-marketing/app/api/v1/endpoints/segments.py`:L54 — created_by="system",  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-marketing/app/api/v1/endpoints/segments.py`:L130 — segment.updated_by = "system"  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-marketing/app/api/v1/endpoints/segments.py`:L306 — member.removed_by = "system"  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-marketing/app/services/email_sender.py`:L22 — self.smtp_host = "localhost"  # TODO: Get from config
- **[Normal] [TODO]** `services/crm-marketing/app/services/email_sender.py`:L24 — self.smtp_user = None  # TODO: Get from config
- **[Normal] [TODO]** `services/crm-marketing/app/services/email_sender.py`:L25 — self.smtp_password = None  # TODO: Get from config
- **[Normal] [TODO]** `services/crm-marketing/app/services/email_sender.py`:L43 — TODO: Implement actual email sending
- *… 10 weitere in diesem Slice*

## 3. `services/crm-gdpr` — 10 TODO(s) (0 Hoch · 10 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L58 — created_by=request_data.requested_by,  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L81 — TODO: Send verification email
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L239 — TODO: Collect data from all CRM modules
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L245 — "contacts": [],  # TODO: Fetch from crm-core
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L246 — "opportunities": [],  # TODO: Fetch from crm-sales
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L247 — "activities": [],  # TODO: Fetch from crm-sales
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L248 — "consents": [],  # TODO: Fetch from crm-consent
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L249 — "campaigns": [],  # TODO: Fetch from crm-marketing
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L264 — TODO: Convert to CSV format
- **[Normal] [TODO]** `services/crm-gdpr/app/api/v1/endpoints/gdpr.py`:L323 — TODO: Implement actual deletion/anonymization logic

## 4. `services/crm-communication` — 6 TODO(s) (0 Hoch · 6 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-communication/app/api/v1/api.py`:L10 — TODO: Add email campaigns, templates, and analytics routers when implemented
- **[Normal] [TODO]** `services/crm-communication/app/api/v1/endpoints/communication.py`:L32 — TODO: Queue email for sending via SMTP
- **[Normal] [TODO]** `services/crm-communication/app/api/v1/endpoints/communication.py`:L33 — TODO: Process attachments
- **[Normal] [TODO]** `services/crm-communication/app/api/v1/endpoints/communication.py`:L34 — TODO: Apply template if specified
- **[Normal] [TODO]** `services/crm-communication/app/api/v1/endpoints/communication.py`:L218 — TODO: Queue campaign for sending
- **[Normal] [TODO]** `services/crm-communication/app/api/v1/endpoints/communication.py`:L256 — TODO: Process inbound email webhooks from email service provider

## 5. `services/crm-sales` — 4 TODO(s) (0 Hoch · 3 Normal · 1 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-sales/app/api/v1/api.py`:L10 — TODO: Add quotes and sales activities routers when implemented
- **[Normal] [TODO]** `services/crm-sales/app/services/events.py`:L17 — TODO: Initialize event bus connection
- **[Normal] [TODO]** `services/crm-sales/app/services/events.py`:L28 — TODO: Publish to actual event bus
- **[Niedrig] [TODO]** `services/crm-sales/app/services/events.py`:L8 — TODO: Integrate with actual event bus (RabbitMQ/Kafka)

## 6. `app/domains` — 3 TODO(s) (0 Hoch · 2 Normal · 1 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `app/domains/agrar/api/psm_proplanta.py`:L83 — TODO: Could send notification or update status
- **[Normal] [TODO]** `app/domains/crm/services/daily_report_service.py`:L385 — TODO: Send via email, Teams, Telegram, etc.
- **[Niedrig] [TODO]** `app/domains/agrar/api/psm_proplanta.py`:L78 — TODO: Optionally update local database with synced data

## 7. `frontend-web/tests` — 3 TODO(s) (0 Hoch · 3 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `packages/frontend-web/tests/e2e/crm-consent.spec.ts`:L16 — // TODO: Setup authentication
- **[Normal] [TODO]** `packages/frontend-web/tests/e2e/crm-gdpr.spec.ts`:L18 — // TODO: Setup authentication
- **[Normal] [TODO]** `packages/frontend-web/tests/e2e/crm-opportunities.spec.ts`:L15 — // TODO: Setup authentication

## 8. `services/compliance` — 2 TODO(s) (0 Hoch · 2 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/compliance/infrastat/README.md`:L39 — TODO
- **[Normal] [TODO]** `services/compliance/zoll/README.md`:L36 — TODO

## 9. `services/crm-consent` — 2 TODO(s) (0 Hoch · 2 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-consent/app/api/v1/endpoints/consents.py`:L55 — created_by=consent_data.tenant_id,  # TODO: Get from auth context
- **[Normal] [TODO]** `services/crm-consent/app/api/v1/endpoints/consents.py`:L85 — TODO: Send double opt-in email

## 10. `services/crm-multichannel` — 2 TODO(s) (0 Hoch · 2 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-multichannel/app/api/v1/api.py`:L10 — TODO: Add dedicated routers for specific platforms when implemented
- **[Normal] [TODO]** `services/crm-multichannel/app/api/v1/endpoints/multichannel.py`:L30 — TODO: Implement webhook signature verification

## 11. `services/crm-workflow` — 2 TODO(s) (0 Hoch · 2 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-workflow/app/api/v1/api.py`:L10 — TODO: Add triggers, notifications, and events routers when implemented
- **[Normal] [TODO]** `services/crm-workflow/app/api/v1/endpoints/workflows.py`:L128 — TODO: Actually execute the workflow actions

## 12. `services/finance` — 2 TODO(s) (0 Hoch · 2 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/finance/app/domains/finance/service.py`:L294 — is_closed=False,  # TODO: Check period closing status
- **[Normal] [TODO]** `services/finance/app/domains/finance/service.py`:L295 — balance_check="balanced",  # TODO: Real balance check

## 13. `app/api` — 1 TODO(s) (0 Hoch · 1 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `app/api/v1/endpoints/strecke.py`:L76 — In-memory store (TODO: replace with DB table)

## 14. `app/einkauf` — 1 TODO(s) (0 Hoch · 1 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `app/einkauf/router.py`:L658 — TODO(phase-4): Echte Extraktion via pdfplumber / tesseract / Cloud-OCR einbauen

## 15. `frontend-web/src/components` — 1 TODO(s) (0 Hoch · 1 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `packages/frontend-web/src/components/sales/ArtikelSuchDialog.tsx`:L245 — // TODO: Implement proper filtering when backend supports these fields

## 16. `services/crm-ai` — 1 TODO(s) (0 Hoch · 1 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-ai/app/api/v1/api.py`:L10 — TODO: Add model management, training, and monitoring routers when implemented

## 17. `services/crm-analytics` — 1 TODO(s) (0 Hoch · 1 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-analytics/app/api/v1/api.py`:L10 — TODO: Add dashboards, reports, and metrics management routers when implemented

## 18. `services/crm-service` — 1 TODO(s) (0 Hoch · 1 Normal · 0 Niedrig) _(Normal dominiert)_

- **[Normal] [TODO]** `services/crm-service/app/api/v1/api.py`:L10 — TODO: Add knowledge-base and categories routers when implemented
