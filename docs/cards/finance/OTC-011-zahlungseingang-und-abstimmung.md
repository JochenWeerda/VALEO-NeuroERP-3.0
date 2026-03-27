# OTC-011 — Zahlungseingang und Abstimmung (Card)

**Slice:** OTC-011 | **Lane:** Order-to-Cash (Folge) | **Status:** `in arbeit`  
**Owner:** Cursor Agent | **Datum:** 2026-03-27

---

## 1. Zweck

Debitoren-Zahlungseingänge den offenen Posten zuordnen und mit OTC-Rechnungen abstimmen (Folge zu **OTC-010**).

## 2. Workflow

Siehe `docs/workflows/otc-011-zahlungseingang-und-abstimmung.md`.

## 3. Betroffene Bereiche (Ziel)

- `packages/frontend-web/src/pages/finance/op-debitoren.tsx` — OP-Debitoren
- ggf. `packages/frontend-web/src/pages/finance/mahnwesen.tsx` — bei Zahlungsbuchung aus Mahnwesen
- API: zu inventarisieren (`/api/v1/finance/...`)

## 4. Lane-Konflikt vermeiden

**Nicht parallel** dieselben Dateien wie Slice **VK-013** (Agrar-Kampagne) bearbeiten; siehe Workboard.
