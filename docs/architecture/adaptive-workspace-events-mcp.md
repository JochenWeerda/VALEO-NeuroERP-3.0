---
title: Adaptive Workspace — Events und MCP-Fachaktionen
type: reference
audience: [agent, entwickler, architect]
owner: MCP/Events-Agent
status: aktiv
last_reviewed: 2026-10-23
version: 1.0.1
description: Katalog typisierter Fachaktionen, Alias-Resolver und Event-Luecken NATS→SSE fuer Adaptive Workspace Phase 3+4.
---

# Adaptive Workspace — Events und MCP-Fachaktionen

Phase 3+4 ohne Launcher-UI: Command Center und Agenten uebersetzen Kurzkommandos
in **berechtigte, typisierte Fachaktionen**. Schreibende Agenten gehen ausschliesslich
ueber vorhandene Domain-Commands und MCP-Adapter
([MCP-WRITE-001 bis 015](mcp-write-standard.md)). Keine direkten DB-Writes.
Vier-Augen fuer jede WRITE-Klasse R3/R4. Rahmen: [`adaptive-workspace-framework.md`](adaptive-workspace-framework.md).

## Command Center

Strg+K loest freie Eingabe deterministisch auf die YAML-Aliase und `action_id`
aus [`config/adaptive_workspace_fachaktionen.yaml`](../../config/adaptive_workspace_fachaktionen.yaml)
ab — lokal dieselbe Abbildung, live `workspace.fachaktion.resolve` im `dryRun`.
Kein Auto-Submit, kein LLM, kein Fallback auf rohe URLs oder SQL.
Unbekannter Text bleibt ohne Treffer. WRITE, Vier-Augen und `executable: false`
werden nur vorbereitet oder blockiert, nicht ausgefuehrt.

## Vertrag fuer den Frontend-Lead

Der Lead verdrahtet die Palette. Dieser Slice liefert den Katalog, nicht die UI.

| Konsum | Pfad |
|---|---|
| YAML-Katalog (Source of Truth) | [`config/adaptive_workspace_fachaktionen.yaml`](../../config/adaptive_workspace_fachaktionen.yaml) |
| Frontend `catalogId` | zeigt 1:1 auf YAML `action_id` (`lead_contract.frontend_catalog_id`) |
| MCP listen | `workspace.fachaktion.katalog` via `POST /api/v1/mcp/tools/call` |
| MCP aufloesen | `workspace.fachaktion.resolve` mit `parameters.command` |
| Resolver | `app/workspace/fachaktionen.py` (kein LLM, Alias + Action-ID) |
| Frontend-Alias-Spiegel | `FACHAKTION_CATALOG_ALIASES` in `packages/frontend-web/src/workspace/fachaktion-resolve.ts` |
| Drift-Gate YAML↔TS | Vitest `fachaktion-alias-parity` + pytest `test_fachaktion_alias_parity` (action_id, aliases, Registry route/scope/screenId) |
| Event-Projektion | `app/workspace/events.py` (Ist-Typ bleibt; Soll-Name nur Annotation) |

JSON-Form der Aufloesung (Lead-Palette):

```json
{
  "action_id": "finance.ap_invoice.approval.worklist",
  "authorized": true,
  "reason": "authorized",
  "access": "read",
  "risk_level": "R0",
  "four_eyes": false,
  "mcp_tool_id": "agent.proposal.list",
  "command_endpoint": "POST /api/v1/mcp/tools/call",
  "screen_id": "workflows/approval",
  "route_path": "/workflows/approval",
  "follow_up_writes": ["finance.ap_invoice.propose", "finance.ap_invoice.freigeben"]
}
```

Identitaet und Mandant kommen nur aus dem Token. Ein Freigabe-Boolean im Aufruf
wird vom bestehenden MCP-Adapter abgewiesen.

## Die fuenf Beispiel-Queries

| Kurzkommando | Action-ID | Zugang | MCP / REST | Event Soll |
|---|---|---|---|---|
| nicht disponierte LKW | `logistik.undispatched_vehicles.list` | R0 `logistics:read` | `GET /api/v1/logistik/tours?status=GEPLANT` plus Fuhrpark-Liste | — (Lesen); Follow-up `logistik.tour.created` → `assignment_confirmed` |
| ueberfaellige Kontrakte | `agrar.contract.overdue.list` | R0 `agrar:read` | `GET /api/v1/contracts/dunning/candidates`; Kontext `agrar.contract.get` | — (Lesen); Mahnung ohne Outbox |
| Angebot Kunde | `sales.customer_quote.list` | R0 `sales:read` | `GET /api/v1/sales/offers`; Kundenkontext `crm.customer.open` | Anlegen ohne Outbox → Luecke `document_proposed` |
| WE Mengenabweichung | `einkauf.goods_receipt.quantity_variance.list` | R0 `einkauf:read` | `GET /api/v1/procurement/match` | Buchen: `goods_receipt.created` → `document_posted` |
| Rechnungen Freigabe | `finance.ap_invoice.approval.worklist` | R0 `finance:read` | `agent.proposal.list` | Vorschlag `document_proposed`; Freigabe `assignment_confirmed` / `document_posted` |

Handshake Phase-1-Lead (Frontend-`catalogId` ohne YAML-`action_id`, jetzt additiv):

| Frontend catalogId = YAML action_id | Zugang | REST | Hinweis |
|---|---|---|---|
| `harvest.intake-queue` | R0 `logistics:read` | `GET /api/v1/annahme/warteschlange` | Ernte-Annahme-Queue; Aliase Annahme-Warteschlange / warteschlange |
| `workspace.document-inbox` | R0 `dms:read` | `GET /api/mcp/documents/inbox/queue` | Beleg-Inbox Queue lesen |
| `document.capture.open` | Follow-up, `executable: false` | `POST /api/mcp/documents/inbox/{item_id}/prepare` | kein Auto-Approve, fuer Agenten verboten |

Frontend-catalogId `agrar.qualitaets-handlungsbedarf` ist R0/read (`agrar:read`) auf `GET /api/v1/agrar/quality-protocols` / `/annahme/qualitaets-check`; executable nur fuer Lesen, keine Buchung.

WRITE-Folgen derselben Beispiele:

| Kurzkommando | Action-ID | Klasse | Agent |
|---|---|---|---|
| tour anlegen / LKW disponieren | `logistik.tour.anlegen` | R2 | berechtigt bei `logistics:write` (vorhandener MCP-Write) |
| kontrakt mahnen | `agrar.contract.reminder.create` | R2 | **verboten** — kein MCP-Command, keine Outbox |
| angebot anlegen | `sales.customer_quote.create` | R1 | **verboten** — kein MCP-Write |
| wareneingang buchen | `einkauf.anlieferavis.wareneingang` | R2 | berechtigt bei `einkauf:write` |
| rechnungsfreigabe vorschlagen | `finance.ap_invoice.propose` | R3 Vier-Augen | Agent darf vorschlagen |
| rechnungen freigeben | `finance.ap_invoice.freigeben` | R4 Vier-Augen | **verboten** fuer Agenten |

## MCP-WRITE-Abbildung

| Regel | Umsetzung hier |
|---|---|
| 001 / 015 | Resolver fuehrt nichts aus. Writes bleiben `mcp_tool_id` / Command-Endpoint. |
| 002 | Neue Writes ohne Domain-Command sind `enabled_for_agents: false`. |
| 003 / 004 | Scope aus Token; Mandant unveraendert beim Zieladapter. |
| 006 | `idempotency: required` an jedem Write. |
| 008 / 013 / 014 | AP-Freigabe Vier-Augen; Agent schlaegt vor, Mensch gibt frei. Unabgenommene Writes bleiben deaktiviert. |
| 009 / 010 | Audit- und Outbox-Felder im Katalog; Transaktion bleibt beim bestehenden Adapter. |
| 012 | Resolver-Tests ohne MagicMock-DB: berechtigt vs verboten. |

## Events: Ist versus Soll

Soll-Namen fuer Adaptive Workspace bleiben Annotation, kein eigener NATS-Topic:

- `assignment_confirmed`
- `document_proposed`
- `document_posted`

NATS-Soll wird **nicht** publiziert: `tenant.{tenantId}.workspace.<soll>`
(keine neuen Topic-Namen). SSE: bestehender Kanal
`/api/events?stream=workspace` (Tenant aus Token). Kein neuer SSE-Router.
NC-G3-Handler bleiben unveraendert. Der Workspace-Spiegel haengt sich additiv
an Outbox (`store_event` / `publish_pending_events`) und als zusaetzlicher
NATS-Handler.

Auf dem Stream landet der **Ist-Typ** (`type` / `event_type`), nicht der Soll-Name.

| Ist (Outbox / NATS) | Soll (Annotation) | `stream=workspace` |
|---|---|---|
| `logistik.tour.created` | `assignment_confirmed` | erreicht |
| `lkw.registered` | `assignment_confirmed` | erreicht |
| `finance.ap_invoice.approved` | `assignment_confirmed` | erreicht |
| `finance.ap_invoice.approval_granted` | `assignment_confirmed` | erreicht |
| `finance.ap_invoice.approval_requested` | `document_proposed` | erreicht |
| `sales.invoice.proposed` | `document_proposed` | erreicht |
| `sales.gutschrift.proposed` | `document_proposed` | erreicht |
| `goods_receipt.created` | `document_posted` | erreicht |
| `finance.ap_invoice.posted` | `document_posted` | erreicht |
| `docflow.document.posted` | `document_posted` | erreicht |
| `sales.invoice.posted` | `document_posted` | erreicht |
| `lager.einlagerung.created` | `document_posted` | erreicht |
| `agrar.weighing_ticket.allocated` | `document_posted` | erreicht |
| `agrar.quality_protocol.completed` | `document_posted` | erreicht (Finalize in `quality_protocols.py` → Outbox; `outbox.py` unberuehrt) |

Bewusst **nicht** auf `stream=workspace`:

| Quelle | Grund |
|---|---|
| `assignment_confirmed` / `document_proposed` / `document_posted` | Soll-Namen, kein Publisher |
| `sales.offer.created` / Angebot anlegen | keine Outbox, Luecke `document_proposed` |
| Kontraktmahnung | keine Outbox |
| `audit.entry_created`, `inventory.movement_created`, `settlement.created` | NC-G3, nicht Workspace |
| Inbox-Capture / Dispo-Drag | kein Event, kein WRITE |
| `agrar.contract.allocated` | Outbox ja (Begleiter der Wiegeschein-Allokation), aber kein Waage-/Qualitaets-Typ |
| inventierte `weighing_ticket.completed` / supply_chain `stage=wiegung` | kein NATS-/Outbox-Typ |

Luecken ohne Ist-Event: Sales-Angebot anlegen, Kontraktmahnung, kanonischer
WE-Posted-Typ neben `goods_receipt.created`. Fachmodule behalten ihre Topics.

Projektionen: vorhandene Cockpit-Consumer (`ap_invoice_cockpit`) hoeren bereits
`*.finance.ap_invoice.*`. Ein Workspace-Read-Model ist nicht angebunden.

## Transaktionsgrenzen

Unveraendert bei den bestehenden Adaptern: Geschaeftsaenderung, Audit und
Outbox in einer Transaktion (MCP-WRITE-010). Der Resolver hat keine
Transaktion, weil er nicht schreibt.

## Kollisionen und Nicht-Besitz

- `config/mcp_mask_action_map.yaml` ist generiert. Additive MCP-Lesewerkzeuge
  aendern nur die Zaehlung `mcp_read_tools_count`, keine Mask-Mappings.
- `app/config/mcp_erp_tools.yaml` ist ein Altbestand und nicht kanonisch.
  Source of Truth bleibt `config/mcp_erp_tools.yaml`.
- `mask.data.read` und `studio.migration.plan` bleiben im Katalog (HEAD);
  Workspace-Tools sind zusaetzlich.
- Dispo-Tafel, Godfile-Touren, Inbox-UI und Navigation wurden nicht beruehrt.
  Disposition laeuft ueber `logistik.tour.anlegen`.
- `app/services/nats_event_handlers.py` (NC-G3) unveraendert.
- Workboard und Studio-CLI-Generatoren unveraendert.

## Tests

`tests/test_workspace_fachaktionen.py` — Action-Aufloesung (berechtigt vs
verboten), Katalog-Kollisionen, Event-Mapping. Keine DB, kein MagicMock-DB.

`tests/test_fachaktion_alias_parity.py` und Vitest
`fachaktion-alias-parity.test.ts` — Alias-/ID-Paritaet YAML↔TS-Spiegel und
Registry-Felder gegen YAML.

`tests/test_workspace_sse_mirror.py` — reiner Unit-Test des SSE-Spiegels:
Ist-Typ bleibt, Soll-Namen bleiben draussen, Hub isoliert je Mandant.
