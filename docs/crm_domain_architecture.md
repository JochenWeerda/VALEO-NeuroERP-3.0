# VALEO NeuroERP – CRM Domain Architecture (AI-First)

## 1. Guiding Goals
- **360° customer view** shared with Sales, Inventory, Logistics, Finance, DMS.
- **Three CRM perspectives** in one bounded context: Operational, Analytical, Interactive.
- **AI-first** by default (LLM tooling, RAG, predictive models).
- **Seamless integration** with existing VALEO identity, UI shell, event bus and shared master data.

---

## 2. Interaction & Channels Layer
- Omni-channel ingestion via UI, email, CTI, social, partner APIs.
- Every inbound/outbound touchpoint is normalised into an `InteractionEvent`.
- REST endpoints (to be implemented in `crm-interaction`) expose:
  - `POST /api/v1/interactions` – receive event, persist, publish `crm.interaction.created`.
  - `GET /api/v1/interactions?customer_id=&channel=&from=&to=` – query timeline views.
- Events are mirrored on the event bus (`crm.interaction.created`, `crm.interaction.tagged`, `crm.interaction.reply-appended`).
- JSON schema: `docs/schemas/interaction_event.schema.json`.

---

## 3. CRM Front-End Skeleton (Operational CRM)

### 3.1 Routes
| Route | Workspace | Notes |
|-------|-----------|-------|
| `/crm/customers/:id/overview` | Customer 360° | Embeds master data, interactions, AI panels. |
| `/crm/sales/leads` | Sales | List + Kanban + AI lead score badges. |
| `/crm/sales/opportunities` | Sales | Pipeline with drill-down into opportunities/offers. |
| `/crm/marketing/campaigns` | Marketing | Campaign list, journeys, segmentation entry. |
| `/crm/service/tickets` | Service | Ticket queue, SLA indicators, knowledge base lookup. |

### 3.2 Customer 360° Composition
- **Header**: display name, tier, lifecycle stage, risk/churn score badges, key KPIs.
- **Left column**: master data (addresses, legal entities, linked contacts, consent flags).
- **Center**: unified timeline (interactions, documents, orders, tickets); filter chips by channel/type.
- **Right column**: open opportunities, tickets, quotes; AI panel with next-best-actions, summarised intent, follow-up tasks.
- State shape:
```ts
type Customer360State = {
  customer: CustomerReference & CRMCoreDetails;
  interactions: InteractionEvent[];
  documents: DocumentRef[];
  opportunities: OpportunitySummary[];
  tickets: TicketSummary[];
  aiRecommendations: NextBestAction[];
};
```

---

## 4. CRM Core Services (Back-End)

| Service | Responsibilities | Key Aggregates | Domain Events |
|---------|------------------|----------------|---------------|
| **crm-core** | Customer/Account master, contacts, relationships, consent, GDPR, canonical reference. | `Customer`, `Contact`, `Relationship`, `ConsentRecord`. | `crm.customer.created`, `crm.contact.updated`, `crm.customer.status-changed`. |
| **crm-sales** | Leads, opportunities, quotes, sales activities. | `Lead` (with score/status), `Opportunity`, `Quote`, `SalesActivity`. | `crm.lead.created`, `crm.lead.stage-moved`, `crm.opportunity.closed-won/lost`, `crm.quote.issued`. |
| **crm-marketing** | Segments, audiences, campaigns, journeys, send-out stats. | `Segment`, `Audience`, `Campaign`, `JourneyNode`, `Experiment`. | `crm.segment.refreshed`, `crm.campaign.launched`, `crm.journey.node-triggered`. |
| **crm-service** | Tickets/cases, SLAs, knowledge base, entitlements. | `Ticket`, `CaseActivity`, `SLAAgreement`, `Entitlement`, `KnowledgeArticle`. | `crm.ticket.created`, `crm.ticket.closed`, `crm.article.published`. |
| **crm-interaction** | Interaction events, linking to customers, referencing other aggregates. | `InteractionEvent`, `InteractionThread`, `TimelineEntry`. | `crm.interaction.created`, `crm.interaction.tagged`, `crm.timeline.snapshot-updated`. |
| **crm-analytics** | KPIs, dashboards, feature store, AI scores, segmentation views. | `AnalyticsSnapshot`, `ScoreCard`, `SegmentView`. | `crm.analytics.score-updated`, `crm.analytics.segment-materialized`. |
| **crm-sync** | Anti-corruption adapters to ERP domains (orders, invoices, inventory, dms). Handles CDC/event ingestion, mapping to CRM aggregates. | `ExternalOrderProjection`, `InvoiceLedger`, `DocumentLinkMap`. | Publishes `crm.sync.order-linked`, `crm.sync.invoice-linked`, plus replays foreign events to CRM bus. |
| **ai-crm** | LLM + RAG orchestration for CRM use-cases (compose, summarise, next-best-action). | Stateless, maintains prompt templates, caches embeddings. | `crm.ai.requested`, `crm.ai.response-logged` (for audit). |

Canonical customer reference schema shared via `customer_reference.schema.json`.

```json
{
  "customer_id": "UUID",
  "external_ids": [{"system":"sap","value":"1000234"}],
  "type": "company|person",
  "display_name": "Müller Agrar GmbH",
  "status": "active|prospect|former",
  "master_domain_owner": "crm-core|finance|erp"
}
```

---

## 5. Data & Analytics Layer
- Streams all CRM/ERP events into warehouse.
- Minimal shared tables:
  - `dim_customer(customer_id, type, industry, lifecycle_stage, risk_score, lead_score, churn_score, region, master_owner, created_at, updated_at)`
  - `fact_interaction(interaction_id, customer_id, channel, direction, sentiment, subject, duration_sec, agent_id, campaign_id, occurred_at)`
  - `fact_opportunity(opportunity_id, customer_id, amount, currency, stage, probability, owner_id, opened_at, closed_at)`
  - `fact_ticket(ticket_id, customer_id, category, priority, sla_breach_flag, first_response_minutes, resolution_minutes, status, opened_at, closed_at)`
- Scores are produced in `crm-analytics` feature pipelines, then written back to `crm-core` through synchronous API (`PATCH /api/v1/customers/{id}/scores`) and exposed via GraphQL/REST to UI.

---

## 6. AI-First Services
- Central AI APIs (`ai-crm`) (see detailed contracts in `docs/api/*.json`):
  - `POST /ai/crm/compose-email`
  - `POST /ai/crm/summarize-thread`
  - `POST /ai/crm/next-best-actions`
  - `POST /ai/crm/rag/search`
- Prompts always include:
  - Customer profile summary (from canonical reference + latest scores).
  - Recent interaction snippet (passed via RAG context).
  - Compliance/tone guardrails (language, formal degree, regulatory hints).
- Predictive models feature sets:
  - **Lead scoring**: source channel, engagement counts, deal size, segment fit, product interest, past conversion velocity, marketing touches.
  - **Churn prediction**: usage metrics, ticket volume/SLAs, payment delays, NPS, product lifecycle stage, contract renewals.
  - **Ticket routing**: category, keywords, sentiment, channel, customer tier, SLA class, past escalations.
- Event bus feeds model pipelines with `crm.lead.stage-moved`, `crm.ticket.created`, `inventory.shipment.delayed`, `order.created`, etc.

---

## 7. Integration With Other Domains
- Subscribe to ERP/Finance/Inventory events:
  - `order.created`, `order.fulfilled`, `invoice.posted`, `payment.overdue`, `delivery.shipped`, `inventory.shortage.detected`, `contract.renewal.due`.
- `crm-sync` maps them into CRM projections (example: `CustomerOrderHistoryProjection` storing last 20 orders, amounts, statuses for UI timeline).
- CRM publishes its own events for other domains (e.g., `crm.customer.blacklisted` consumed by order processing).

---

## 8. Deliverables Linked
- `docs/crm_reuse_inventory.md` – existing modules reuse strategy.
- `docs/crm_ui_mapping.md` – mapping of current UI masks to new CRM views.
- `docs/schemas/interaction_event.schema.json`, `docs/schemas/customer_reference.schema.json`.
- API contracts – see `docs/api/`.
- ADR – `docs/adr/ADR-CRM-001.md`.
- Service skeletons located under `services/crm-*` and `services/ai-crm`.

---

## 9. Next Steps
1. Implement adapters in `crm-sync` for current ERP events.
2. Flesh out domain models for `crm-core` and `crm-sales`.
3. Incrementally migrate existing UI masks into the new route layout described above.
