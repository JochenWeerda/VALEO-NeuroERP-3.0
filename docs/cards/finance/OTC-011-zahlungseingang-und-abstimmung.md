---
card_id: OTC-011
chain: order-to-cash
chain_step: 1
card_type: process-step
parent_card: OTC-010
flow_spine: flow-spine-order-to-cash
workflow_doc: docs/workflows/otc-011-zahlungseingang-und-abstimmung.md
---
# OTC-011 — Zahlungseingang und Abstimmung (Card)

**Slice:** OTC-011 | **Lane:** Order-to-Cash (Folge) | **Status:** abgeschlossen
**Owner:** Claude Sonnet 4.6 | **Datum:** 2026-03-27

---

## 1. Zweck

Debitoren-Zahlungseingänge den offenen Posten zuordnen und mit OTC-Rechnungen abstimmen
(Folge zu **OTC-010**).

## 2. Betroffene Dateien

- `packages/frontend-web/src/pages/sales/invoice-editor.tsx` — Deep-Link-Button analysiert
- `packages/frontend-web/src/pages/finance/op-debitoren.tsx` — Zahlungserfassung + Ausgleich analysiert
- `packages/frontend-web/src/pages/finance/payment-matching.tsx` — Bankimport analysiert

## 3. API-Endpoints

| Endpoint | Methode | Zweck |
|---|---|---|
| `/api/v1/finance/open-items` | GET | OP-Liste (mit `?search=` für Rechnungsnr-Auflösung) |
| `/api/v1/finance/open-items/{id}` | GET/PUT | Einzel-OP lesen/speichern |
| `/api/v1/finance/open-items/{id}/settle` | POST | Zahlung auf OP buchen |
| `/api/v1/finance/open-items/{id}/settlements` | GET | Ausgleichshistorie |
| `/api/v1/finance/dunning/{id}/mahnung` | POST | Mahnstufe erhöhen |
| `/api/v1/finance/payments/unmatched` | GET | Ungematchte Bankzahlungen |
| `/api/v1/finance/payments/import/csv` | POST | CSV-Bankimport |
| `/api/v1/finance/payments/match-suggestions/{id}` | GET | Match-Vorschläge |
| `/api/v1/finance/payments/match/{id}` | POST | Manuelles Match |
| `/api/v1/finance/payments/auto-match` | POST | Automatisches Matching |

## 4. Client-Warnung

`op-debitoren.tsx` nutzt `@/lib/axios` (unwrapped — kein `.data`-Bug).
`payment-matching.tsx` nutzt `@/lib/api-client` (AxiosResponse — korrekt mit `{ data }`).
**Kritisch:** Mahnung-Aktion in `op-debitoren.tsx` nutzt `raw fetch()` mit
`localStorage.getItem('token')` — in OIDC-Umgebungen funktioniert das nicht.

## 5. Handover-Architektur

```
invoice-editor.tsx (docId + invoice.number gesetzt)
  → navigate('/finance/op-debitoren?rechnungsnr=<nr>')

op-debitoren.tsx
  → GET /finance/open-items?search=<nr>     (OP-ID auflösen)
  → GET /finance/open-items/<id>            (OP laden)
  → mapOpenItemApiToForm()                  (Felder mappen)
  → ZahlungenTable                          (Zahlungen erfassen)
  → Aktion "ausgleich"
      → POST /finance/open-items/<id>/settle  (je Zahlung)
      → navigate('/finance/op-debitoren')
```

## 6. Behobene Gaps

| ID | Beschreibung |
|---|---|
| OTC-011-G1 | Deep-Link von Rechnung zu OP via `?rechnungsnr=` vorhanden |
| OTC-011-G2 | OP-Auflösung per Suche implementiert (nicht mehr per manueller ID) |
| OTC-011-G3 | Zahlungserfassung und Ausgleich-Buchung vollständig implementiert |
| OTC-011-G4 | Ausgleichshistorie-Tab vorhanden |

## 7. Behobene offene Punkte

| ID | Beschreibung | Status |
|---|---|---|
| OTC-011-P1 | Debitor-Dropdown aus `GET /crm/customers` | behoben — `useQuery` mit CRM-API |
| OTC-011-P2 | Mahnung-Aktion auf `apiClient.post()` | behoben — raw fetch entfernt |
| OTC-011-P3 | Navigation nach Ausgleich zu `/finance/offene-posten` + Toast | behoben |
| OTC-011-P4 | `payment-matching.tsx` → Toast mit „OP öffnen"-Button | behoben |

## 8. Tests (manuell)

1. Rechnung speichern → Button „OP / Zahlungseingang" erscheint
2. Button klicken → `op-debitoren.tsx` öffnet mit OTC-011-Banner
3. Bei bekannter Rechnungsnr: OP wird automatisch geladen
4. Bei unbekannter Nr: Hinweis-Banner „kein OP gefunden"
5. Zahlung hinzufügen → offener Betrag aktualisiert sich live
6. „Ausgleich" → `/finance/open-items/{id}/settle` wird aufgerufen

---

*Erstellt von Claude Sonnet 4.6 — Slice OTC-011 — 2026-03-27*
