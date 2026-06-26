---
card_id: OTC-010
chain: order-to-cash
chain_step: 0
card_type: overview
related_cards: [OTC-011]
flow_spine: flow-spine-order-to-cash
workflow_doc: docs/workflows/otc-010-order-to-cash.md
overlaps: [SEC-031, SEC-032]
---

# OTC-010 - Order-to-Cash (Card)

**Slice:** OTC-010 | **Lane:** Order-to-Cash | **Owner:** Codex | **Datum:** 2026-06-26
**Status:** abgeschlossen

## 1. Zweck

End-to-End Analyse und QA-Haertung der Order-to-Cash Lane:
Angebot -> Verkaufsauftrag -> Lieferschein -> Rechnung -> Zahlung.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/sales/invoice-editor.tsx` - Edit-Mode und Deep-Link per Path-ID.
- `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx` - Handover aus Auftrag inklusive Positionen und `sales_order_id`.
- `packages/frontend-web/src/pages/sales/order-editor.tsx` - Sofort-Rechnung mit vollstaendigem Sales-Handover-Kontext.
- `app/api/v1/endpoints/sales_delivery_notes.py` - `sales_order_id` auch im Update-Payload.
- `docs/workflows/otc-010-order-to-cash.md` - Workflow-Analyse und Nachweis.

## 3. Fachlicher Kontext

Der Verkauf von Agrarprodukten und Handelsware folgt dem OTC-Prozess. Landhandel-spezifisch relevant sind Kontrakt-Referenz in Positionen, Fruehabnahme-Kennzeichen, Gefahrgutpunkte und eine lueckenlose Belegkette Auftrag -> Lieferschein -> Rechnung.

## 4. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/sales/orders` | GET/POST | Auftrags-CRUD |
| `/api/v1/sales/orders/{id}` | GET/PUT/DELETE | Einzel-Auftrag |
| `/api/v1/sales/delivery-notes` | GET/POST | LS-CRUD |
| `/api/v1/sales/delivery-notes/{id}` | GET/PUT/DELETE | Einzel-LS |
| `/api/v1/docflow/{id}/convert` | POST | LS/Auftrag -> Rechnung |
| `/api/v1/docflow` | GET/POST | Rechnung CRUD via Docflow |
| `/api/v1/docflow/{id}` | GET/PUT | Rechnung Einzel |
| `/api/v1/crm/customers/{id}` | GET | Kundendaten fuer Prefill |

## 5. Handover-Architektur

```text
order-editor.tsx
  -> buildSalesHandoverPath('/verkauf/lieferschein-erfassung', { sourceOrderId })

lieferschein-erfassung.tsx
  -> parseSalesHandover() liest ?auftrag=<id>
  -> GET /api/v1/sales/orders/{id}
  -> prefill Kunde + Positionen
  -> POST/PUT /api/v1/sales/delivery-notes mit sales_order_id

order-editor.tsx / lieferschein-erfassung.tsx
  -> POST /api/v1/docflow/{id}/convert
  -> /verkauf/rechnungen/<targetId>?rechnungId=<targetId>&...

invoice-editor.tsx
  -> editId = ?rechnungId || ?id || path id
  -> GET /api/v1/docflow/{editId}
```

## 6. Behobene Bugs

| ID | Beschreibung | Status |
|---|---|---|
| OTC-010-B1 | `invoice-editor.tsx` Edit-Mode laedt Daten per `.data` korrekt | behoben |
| OTC-010-B2 | Rechnung-Create setzt keine `"undefined"`-ID mehr | behoben |
| OTC-010-B3 | `?auftrag=` wurde ignoriert | behoben |
| OTC-010-P1 | Auftragpositionen werden in den Lieferschein uebernommen | behoben 2026-06-26 |
| OTC-010-P2 | Lieferschein persistiert Belegkette ueber `sales_order_id` | behoben 2026-06-26 |
| OTC-010-P3 | `/verkauf/rechnungen/<id>` oeffnet den invoice-editor korrekt | behoben 2026-06-26 |

## 7. Tests

- `pnpm.cmd --dir packages/frontend-web exec tsc --noEmit --pretty false` - gruen.
- `pytest -q -o addopts= tests/test_sales_o2c_001.py tests/test_sales_orders_api.py tests/test_sales_delivery_notes_api.py tests/test_docflow_conversion_order.py --maxfail=3` - 30 passed.

## 8. Externe Abnahme

Die technische Belegkette ist repo-seitig geschlossen. Fachlich offen bleibt nur die UAT-Abnahme durch Vertrieb/FiBu fuer reale Belegnummern, Drucklayout und Prozessfreigabe.
