---
title: Sales Order — Mask Parity Matrix
type: reference
audience: [agent, entwickler, fachlich]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 1.0.0
description: Paritaetsmatrix Legacy OrderEditor vs. Universal Mask Generator (Sales Order Pilot).
---

# Sales Order — Paritaetsmatrix

Referenz fuer Wave 32 (`UIX-SALES-PARITY-008`).

| Legacy (OrderEditorLegacyPage) | Generator-Tab | Inhalt | API | RenderPlan | Status |
|---|---|---|---|---|---|
| Kopf / Kunde / Belegnr. | `kopf` | Auftragskopf-Felder | `GET /api/v1/sales/orders/{id}` | compiled | partial |
| Positionen-Grid | `positionen` | Positionsliste | `GET .../tabs/positionen` | lazy table plan | partial |
| Liefertermin / Versand | `lieferung` | Kopf-Felder + Lieferscheinliste | Summary + `GET .../tabs/lieferung` | lazy table plan | partial |
| Lieferschein anlegen | — | Mutation | Legacy only | — | gap |
| Druck / DMS / Belegfolge | — | Aktionen | Legacy only | — | gap |
| Rechnungsbelege | `dokumente` | LS mit Rechnungsnr. | `GET .../tabs/dokumente` | lazy table plan | partial |

## Lazy-Load Vertrag

- Summary zuerst: `GET /api/v1/sales/orders/{id}/screen-summary`
- Tab-Listen: `GET /api/v1/sales/orders/{id}/tabs/{tab_key}` (max. 25 Zeilen, read-only)
- Neuanlage / Workflow-Einstieg: immer Legacy (`order-editor.tsx` Route-Switch)

## Offene Luecken

- Speichern, Positionen bearbeiten, Lieferschein erzeugen: bewusst Legacy.
- DMS-Anhaenge: noch nicht angebunden (leere `dokumente`-Liste wenn keine Rechnungsnr.).
