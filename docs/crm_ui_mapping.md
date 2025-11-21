# CRM UI Mapping & Transition Plan

## Existing Screens (packages/frontend-web)

| route/component | source file | data source | current usage | proposed action |
|-----------------|-------------|-------------|---------------|-----------------|
| `/verkauf/kunden-stamm` | `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx` | REST `/api/v1/crm/customers` (monolith) | Customer master edit form | **Embed into new `/crm/customers/:id/overview`** as “Master Data” panel. Reuse validation schema. |
| `/verkauf/kunden-liste` | `packages/frontend-web/src/pages/verkauf/kunden-liste.tsx` | REST `/api/v1/crm/customers` | Basic list/table | **Replace with new Customer list** that links to Customer 360°. Keep table component but add filters + AI badges. |
| `/verkauf/kunden-stamm-modern` | `packages/frontend-web/src/pages/crm/kunden-stamm-modern.tsx` | WIP mock data | Experimental page | **Redesign** – use as base for Customer 360° shell. |
| `/crm/kontakte-liste` | `packages/frontend-web/src/pages/crm/kontakte-liste.tsx` | `/api/v1/crm/contacts` | Contact grid/export | **Embed**: use same grid inside Customer 360° > “Contacts” tab. Add inline create modal. |
| `/crm/leads` (smoke spec) | `packages/frontend-web/src/pages/crm/leads-smoke.tsx` etc. | `/api/v1/crm/leads` (dev token) | Minimal list | **Redesign**: new `/crm/sales/leads` route with Kanban view + AI scoring badges. |
| `/sales/angebote-liste` | `packages/frontend-web/src/pages/sales/angebote-liste.tsx` | BFF (mock) | Quote list | **Keep-as-is** initially, show inside Opportunity drill-down. |
| `/service/tickets` (legacy) | `packages/frontend-web/src/pages/service/tickets.tsx` | placeholder data | Ticket table | **Redesign** within `/crm/service/tickets` workspace (queues + SLA). |

## Mask Builder & Field Reuse
- Reuse existing `CustomerForm` field configs (company name, address, VAT, payment terms) by exporting definitions into a shared `crmFields.ts`.
- Contacts: reuse validation logic for email/phone from current forms.
- New masks required:
  - **Interaction timeline item** (channel, direction, summary, attachments).
  - **AI panel** (prompts, generated text, actions).
  - **Opportunity card** (stage, value, probability, owner).
  - **Ticket SLA widget**.

## Routing Sketch
```
/crm
  /customers
    /:id
      /overview        <-- Customer 360°
      /interactions    <-- Timeline filtered view
      /documents
  /sales
    /leads
    /opportunities
  /marketing
    /campaigns
  /service
    /tickets
```
- The shell (sidebar, breadcrumbs) stays identical to existing VALEO layout. New breadcrumb entries added.
- Legacy masks embedded via slots within new pages until fully replaced.
