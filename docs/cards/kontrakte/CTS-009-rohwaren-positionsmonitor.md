---
card_id: CTS-009
chain: contract-to-settlement
chain_step: 1
card_type: process-step
flow_spine: flow-spine-contract-to-settlement
workflow_doc: docs/workflows/cts-009-rohwaren-positionsmonitor.md
---
# Card: CTS-009 — Rohwaren-Positionsmonitor (Long/Short)

| Feld | Wert |
|------|------|
| **Card-ID** | CTS-009 |
| **Name** | Rohwaren-Positionsmonitor (Long/Short-Deckung) |
| **Lane** | Kontrakt (Contract-to-Settlement) |
| **Prozessbereich** | Einkauf / Risikomanagement / Kontrakthandel |
| **Status** | umgesetzt |
| **Erstellt** | 2026-03-27 |
| **Bearbeiter** | Cursor Agent |

## Zweck

Zeigt dem Einkauf auf einen Blick, ob bei Rohwaren (Sojaschrot, Rapsschrot, Mais, Maismehl etc.) eine **Unterdeckung** (Short-Position) besteht. Verhindert, dass Verkaufskontrakte mit Landwirten abgeschlossen werden, ohne dass die Beschaffung am Markt gedeckt ist.

## Fachlicher Hintergrund

- **Short** = Verkaufskontrakte > Einkaufskontrakte → Lieferverpflichtung ohne Deckung → **Boersenrisiko bei steigenden Preisen**
- **Long** = Einkaufskontrakte > Verkaufskontrakte → Ware gesichert → Lagerrisiko bei fallenden Preisen
- Deckungsgrad = EK-Restmenge / VK-Restmenge × 100%

## Betroffene Dateien

| Datei | Aenderung |
|-------|-----------|
| `app/services/kontrakt_position_service.py` | NEU — Berechnungslogik |
| `app/api/v1/endpoints/kontrakte.py` | NEU — GET /kontrakte/positionen |
| `pages/kontrakte/KontraktPositionsmonitor.tsx` | NEU — Dashboard |
| `pages/kontrakte/FrmKontraktDetail.tsx` | ERWEITERT — Short-Warnung |
| `pages/kontrakte/LstKontraktUebersicht.tsx` | ERWEITERT — Link zum Monitor |
| Route-Registrierungen | ERWEITERT — /kontrakte/positionen |

## Abnahmekriterien

- [x] API liefert pro Artikel: Signal (LONG/SHORT/BALANCED), Netto-Position, Deckungsgrad, Spread
- [x] Dashboard zeigt KPI-Karten, Positionstabelle, kritische Unterdeckung
- [x] Kontraktdetail zeigt Short-Warnung wenn Artikel unterdeckt
- [x] Kontraktliste hat Link zum Monitor
- [x] Auto-Refresh (30s Dashboard, 60s Detail)

## Workflow-Dokumentation

Siehe: [docs/workflows/cts-009-rohwaren-positionsmonitor.md](../../workflows/cts-009-rohwaren-positionsmonitor.md)
