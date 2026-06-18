# Warehouse / WMS — Doku-Index

Kurzüberblick über **Lager**, **Agrar-Silo** und **Materialfluss** (Erweiterungen zum generischen WMS).

## Agrar-Materialfluss (WM-AGRI-SILO-001 + WMS-FLOW-001)

| Dokument | Inhalt |
|----------|--------|
| [agri-silo-material-flow-benchmark-2026-06-12.md](./agri-silo-material-flow-benchmark-2026-06-12.md) | Zielbild, interne/externe Referenzen, Roadmap-Status |
| [reusable-open-source-silo-material-flow-2026-06-12.md](./reusable-open-source-silo-material-flow-2026-06-12.md) | OSS-Bausteine (Karten, Graphen) |
| [agri-silo-vendor-interface-research-2026-06-12.md](./agri-silo-vendor-interface-research-2026-06-12.md) | Hersteller-Schnittstellen |
| [agrar-silo-materialfluss-studio-baustein.md](./agrar-silo-materialfluss-studio-baustein.md) | AI-Studio-Prototyp-Paket (`packages/agrar-silo-materialfluss-studio`) |
| [folkerts-landhandel-hofplan.md](./folkerts-landhandel-hofplan.md) | Referenz-Hofplan (Beispiel), Bird-View später WM-AGRI-MAP-001 |
| [wm-agri-silo-supply-chain-integration-2026-06-13.md](../workflows/wm-agri-silo-supply-chain-integration-2026-06-13.md) | **Prozessketten:** SILO-001 ↔ DOM-SUPPLY-004 ↔ Logistik; **Code-Ist-Tabelle** |

**Frontend:** `lager/materialfluss` (Betrieb, Tabellen, Route, **Materialtransfer**), `lager/materialfluss-visualisierung` (Layout-Editor, Referenzbild).

**Slices:**

- [WM-AGRI-SILO-001](../agent-ops/slices/WM-AGRI-SILO-001.yaml) — Stammdaten, Graph, Route-Validierung, UI (Status: erledigt 2026-06-19)
- [WMS-FLOW-001](../agent-ops/slices/WMS-FLOW-001.yaml) — kg-Transfer + `inventory_stock_movements` + Transfer-UI (Status: erledigt 2026-06-19)
- [WM-AGRI-CHAIN-002](../agent-ops/slices/WM-AGRI-CHAIN-002.yaml) — Supply-Chain-Events + Outbox

**Bewusst offen:** WM-AGRI-LOT-LINK (Lot-Sync), WM-AGRI-MAP-001 (Bird-View), WM-AGRI-PLC-005 (Anlagenanbindung).

## Design

UI-Orientierung: [EMPFEHLUNG.md](../design/EMPFEHLUNG.md) (MERIDIAN, `PageToolbar`). Masken-Prinzip: [MASKEN.md](../MASKEN.md).
