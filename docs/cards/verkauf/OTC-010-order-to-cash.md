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

# OTC-010 — Order-to-Cash (Card)

**Slice:** OTC-010 | **Lane:** Order-to-Cash | **Owner:** Claude Sonnet 4.6 | **Datum:** 2026-03-27
**Status:** abgeschlossen

---

## 1. Zweck

End-to-End Analyse und QA-Härtung der Order-to-Cash Lane: Angebot → Verkaufsauftrag → Lieferschein → Rechnung → Zahlung.

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/sales/invoice-editor.tsx` — `.data`-Bug behoben
- `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx` — Handover-Gap behoben
- `packages/frontend-web/src/pages/workflow/flow-spine-order-to-cash.tsx` — analysiert (kein Bug)
- `packages/frontend-web/src/pages/sales/order-editor.tsx` — analysiert (kein Bug)
- `docs/workflows/otc-010-order-to-cash.md` — Workflow-Analyse

## 3. Fachlicher Kontext

Der Verkauf von Agrarprodukten (Saatgut, Dünger, PSM) und Handelsware folgt dem OTC-Prozess. Landhandel-spezifisch: Kontrakt-Referenz in Positionen, Frühabnahme-Kennzeichen, Gefahrgutpunkte. Die Belegkette Auftrag → LS → Rechnung muss lückenlos nachverfolgbar sein (GoBD-Anforderung).

## 4. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/sales/orders` | GET/POST | Auftrags-CRUD |
| `/api/v1/sales/orders/{id}` | GET/PUT/DELETE | Einzel-Auftrag |
| `/api/v1/sales/orders/{id}/print` | POST | Druckprotokoll |
| `/api/v1/sales/orders/{id}/post` | POST | Auftrag buchen |
| `/api/v1/sales/delivery-notes` | GET/POST | LS-CRUD |
| `/api/v1/sales/delivery-notes/{id}` | GET/PUT/DELETE | Einzel-LS |
| `/api/v1/docflow/{id}/convert` | POST | LS/Auftrag → Rechnung |
| `/api/v1/docflow` | GET/POST | Rechnung CRUD via Docflow |
| `/api/v1/docflow/{id}` | GET/PUT | Rechnung Einzel |
| `/api/v1/docflow/{id}/record-print` | POST | Druck protokollieren |
| `/api/v1/crm/customers/{id}` | GET | Kundendaten für Prefill |

## 5. Client-Warnung

**Wichtig:** `invoice-editor.tsx` importiert `apiClient` von `@/lib/api-client` (gibt `AxiosResponse<T>` zurück). Alle anderen Masken nutzen `apiClient` von `@/lib/axios` (gibt `T` direkt zurück). Mischung führt zu `.data`-Bugs wenn nicht aufgepasst.

## 6. Behobene Bugs

### Bug OTC-010-B1: invoice-editor.tsx — Edit-Mode lädt nichts
- **Symptom:** Bestehende Rechnung öffnen → alle Felder leer
- **Ursache:** `const doc = await apiClient.get(...) as any` → `doc` ist `AxiosResponse`, nicht Daten. `doc.id`, `doc.doc_number` etc. sind `undefined`.
- **Fix:** `const { data: doc } = await apiClient.get(...) as any`

### Bug OTC-010-B2: invoice-editor.tsx — Create setzt docId auf "undefined"
- **Symptom:** Neue Rechnung speichern → `docId = "undefined"` → Folgeaktionen schlagen fehl
- **Ursache:** `(created as { id?: string }).id` auf `AxiosResponse`-Objekt — `.id` ist undefined
- **Fix:** `const { data: created } = await apiClient.post(...) as any`

### Bug OTC-010-B3: lieferschein-erfassung.tsx — `?auftrag=` ignoriert
- **Symptom:** Aus Auftragsmaske "Lieferschein erstellen" → leerer Lieferschein, kein Kunde prefilled
- **Ursache:** Kein `useSearchParams`, `?auftrag=<id>` wird nie gelesen
- **Fix:** `useSearchParams` + `useEffect([sourceOrderId])` → lädt Auftrag → prefilled Kunden + Toast

## 7. Handover-Architektur (nach Fix)

```
order-editor.tsx
  → navigate('/verkauf/lieferschein-erfassung?auftrag=<id>')

lieferschein-erfassung.tsx
  → useSearchParams() → sourceOrderId = '...'
  → GET /api/v1/sales/orders/<id> → order
  → GET /api/v1/crm/customers/<order.customer_id> → customer
  → setState({ customer, vertreter })
  → push('Lieferschein aus Auftrag XY eröffnet')
```

## 8. Offene Punkte

| ID | Beschreibung | Priorität |
|---|---|---|
| OTC-010-P1 | Positionen aus Auftrag in Lieferschein übernehmen | Mittel |
| OTC-010-P2 | `source_order_id` Backend-Feld im Lieferschein | Mittel |
| OTC-010-P3 | Route `/verkauf/rechnungen/<id>` prüfen → Weiterleitung zu invoice-editor | Mittel |
| ~~OTC-011~~ | Zahlungseingangs-Flow | **abgeschlossen** (Card OTC-011) |

## 9. Tests (manuell)

1. Neuer Auftrag → Kunde auswählen → Positionen → "In Lieferschein wandeln"
2. Lieferschein öffnet sich mit Kundendaten prefilled + Toast
3. Lieferschein drucken → Sofort-Rechnung
4. Rechnung öffnen (Edit-Mode) → alle Felder geladen (kein Bug mehr)
5. Rechnung speichern (Create) → `docId` != `"undefined"`

## 10. Handoff

**Nächste Slices:**
- OTC-011: Zahlungseingang und Abstimmung
- OTC-012: Belegkette-Visualisierung im Flow-Spine Cockpit

---

*Erstellt von Claude Sonnet 4.6 — Slice OTC-010 — 2026-03-27*
