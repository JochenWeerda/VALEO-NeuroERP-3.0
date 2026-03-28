# Card: INV-001 — Inventory-to-Settlement

| Feld | Wert |
|------|------|
| **Card-ID** | INV-001 |
| **Name** | Inventory-to-Settlement (Lager bis Abrechnung) |
| **Flow-Spine** | `flow-spine-inventory-to-settlement` |
| **Prozessbereich** | Lagerverwaltung / Bestandsfuehrung / Versand |
| **Status** | alle Slices umgesetzt |
| **Erstellt** | 2026-03-27 |
| **Bearbeiter** | Cursor Agent |

## Zweck

Vollstaendige Workflow-Analyse des Lagerprozesses im Landhandel — Einlagerung, Bestandsfuehrung, Umlagerung, Kommissionierung, Versand, Inventur.

## Betroffene Bereiche

### Frontend
- `pages/lager/bestandsuebersicht.tsx` — Dashboard (KPIs, MHD, Renner/Penner)
- `pages/lager/einlagerung.tsx` — Einlagerungs-Wizard
- `pages/lager/auslagerung.tsx` — Auslagerungs-Wizard (FIFO/FEFO)
- `pages/lager/lagerbewegungen.tsx` — Bewegungs-CRUD
- `pages/lager/inventur.tsx` — Inventurliste + Abschluss
- `pages/lager/lagerplaetze.tsx` — Lagerplatz-Uebersicht
- `pages/lager/terminal.tsx` — Barcode-Scanner

### Backend
- `app/api/v1/endpoints/warehouses.py` — Lager-Stammdaten
- `app/api/v1/endpoints/inventory_counts.py` — Inventur
- `app/api/v1/endpoints/warehouse_transfers.py` — Transfers + Korrekturen

## Top-4-Risiken

1. Bestandsuebersicht zeigt Stub-KPIs statt echte Bestandsdaten
2. Ein-/Auslagerung hat keine Backend-Buchungslogik (StockMovement)
3. Artikel und Lagerorte in Einlagerung sind hart codiert
4. Transfers/Korrekturen aktualisieren keinen Bestand

## Empfohlene Slices

| Slice-ID | Thema | Prio | Status |
|----------|-------|------|--------|
| INV-002 | Bestandsuebersicht: echte KPIs | P1 | **umgesetzt** |
| INV-003 | Ein-/Auslagerung Backend-Buchung | P1 | **umgesetzt** |
| INV-004 | Einlagerung Stammdaten-Anbindung | P1 | **umgesetzt** |
| INV-005 | Transfer-Verbuchung | P2 | **umgesetzt** |
| INV-006 | Inventur-Kopf CRUD | P2 | **umgesetzt** |
| INV-007 | Lagerplaetze echte Belegung | P2 | **umgesetzt** |

## Workflow-Dokumentation

Siehe: [docs/workflows/inv-001-inventory-to-settlement.md](../../workflows/inv-001-inventory-to-settlement.md)
