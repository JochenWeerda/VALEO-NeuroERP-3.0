# Warehouse / WMS â€” Doku-Index

KurzÃ¼berblick Ã¼ber **Lager**, **Agrar-Silo** und **Materialfluss** (Erweiterungen zum generischen WMS).

## Agrar-Materialfluss (WM-AGRI-SILO-001)

| Dokument | Inhalt |
|----------|--------|
| [agri-silo-material-flow-benchmark-2026-06-12.md](./agri-silo-material-flow-benchmark-2026-06-12.md) | Zielbild, interne/externe Referenzen |
| [reusable-open-source-silo-material-flow-2026-06-12.md](./reusable-open-source-silo-material-flow-2026-06-12.md) | OSS-Bausteine (Karten, Graphen) |
| [agri-silo-vendor-interface-research-2026-06-12.md](./agri-silo-vendor-interface-research-2026-06-12.md) | Hersteller-Schnittstellen |
| [agrar-silo-materialfluss-studio-baustein.md](./agrar-silo-materialfluss-studio-baustein.md) | AI-Studio-Prototyp-Paket (`packages/agrar-silo-materialfluss-studio`) |
| [folkerts-landhandel-hofplan.md](./folkerts-landhandel-hofplan.md) | Referenz-Hofplan (Beispiel), Bird-View spÃ¤ter WM-AGRI-MAP-001 |
| [wm-agri-silo-supply-chain-integration-2026-06-13.md](../workflows/wm-agri-silo-supply-chain-integration-2026-06-13.md) | **Prozessketten:** SILO-001 â†” DOM-SUPPLY-004 â†” Logistik-Welle; Tool-/MCP-Hinweise |

**Frontend:** `lager/materialfluss` (Betrieb, Tabellen, Route), `lager/materialfluss-visualisierung` (Layout-Editor, Referenzbild).
**Slice:** [WM-AGRI-SILO-001](../agent-ops/slices/WM-AGRI-SILO-001.yaml).

## Design

UI-Orientierung: [EMPFEHLUNG.md](../design/EMPFEHLUNG.md) (MERIDIAN, `PageToolbar`). Masken-Prinzip: [MASKEN.md](../MASKEN.md).
