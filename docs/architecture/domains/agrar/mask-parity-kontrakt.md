---
title: Agrar Kontrakt — Mask Parity Matrix
type: reference
audience: [agent, entwickler, fachlich]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-28
version: 1.0.0
description: Paritaetsmatrix Legacy FrmKontraktDetail vs. Universal Mask Generator (Agrar Kontrakt Pilot).
---

# Agrar Kontrakt — Paritaetsmatrix

Referenz fuer Wave 41 (`UIX-AGrar-PILOT-017`).

| Legacy (FrmKontraktDetail) | Generator-Tab | Inhalt | API | RenderPlan | Status |
|---|---|---|---|---|---|
| Kopf / Partner / Mengen | `kopf` | Kontraktkopf-Felder | `GET /api/v1/kontrakte/{id}` | compiled | partial |
| Positions-Grid | `positionen` | Kontraktzeilen | `GET .../tabs/positionen` | lazy table plan | partial |
| Umsaetze / Bewegungen | `umsaetze` | Kontraktmovements | `GET .../tabs/umsaetze` | lazy table plan | partial |
| Speichern / Aenderungen | — | Mutation | Legacy only | — | gap |
| Nachtraege / Dispositionen | — | Subflows | Legacy only | — | gap |
| Druck / Alarme / Steering | — | Aktionen | Legacy only | — | gap |

## Lazy-Load Vertrag

- Summary zuerst: `GET /api/v1/kontrakte/{id}/screen-summary`
- Tab-Listen: `GET /api/v1/kontrakte/{id}/tabs/{tab_key}` (max. 25 Zeilen, read-only)
- Neuanlage (`/kontrakte/neu`): immer Legacy (`KontraktDetailRoute` Route-Switch)

## Offene Luecken

- Speichern, Positionen bearbeiten, Umsatz buchen: bewusst Legacy.
- Nachtraege, Dispositionen, MATIF/Hedge-Steuerung: noch nicht im Pilot.
