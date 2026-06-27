---
title: Wiederverwendbare Open-Source-Bausteine Silo/Materialfluss
type: reference
audience: [entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Recherche wiederverwendbarer Open-Source-Pakete fuer Silo- und Materialfluss-Visualisierung — Abgleich mit Repo-Dependencies und WM-AGRI-SILO-001.
---

# Open-Source-Bausteine: Silo-, Materialfluss-, Karten-Visualisierung

**Datum:** 2026-06-12 â€” Abgleich mit Repo-Dependencies und Architekturentscheid WM-AGRI-SILO-001.

## Repo-Check (Stand Branch)

| Paket | In `packages/frontend-web/package.json`? | Nutzen |
|--------|------------------------------------------|--------|
| `maplibre-gl` | Ja | Hof-/Bird-View, Geo-Layer |
| `zustand` | Ja | Client-State (bestehend) |
| `@xyflow/react` / `reactflow` | Nein (Slice ergÃ¤nzt `@xyflow/react`) | Materialfluss-Graph |
| `konva` / `react-konva` | Nein | Freies 2D-Layout auf Canvas |
| `d3` / `elkjs` / `dagre` | Nein | Layout-Algorithmen optional spÃ¤ter |
| `node-opcua` | Nein (Backend Node-only) | SpÃ¤tere OPC-UA-Anbindung |
| `mqtt` / Modbus-Libs | Nein | IoT/PLC spÃ¤ter |

## Kandidaten

### 1. xyflow / React Flow (`@xyflow/react`)

- **GitHub:** https://github.com/xyflow/xyflow
- **Lizenz:** MIT
- **Nutzen fÃ¼r VALEO:** Knoten (Annahme, Waage, Elevator, Silozelle, Mischer, MMX) und Kanten (FÃ¶rderweg); Statusfarben (frei, gesperrt, Reinigung, Wartung, QS). Passt zu React 18 + TypeScript.
- **Risiken:** Bundle-GrÃ¶ÃŸe; Performance bei sehr groÃŸen Graphen (Landhandel meist Ã¼berschaubar).
- **Empfehlung:** **verwenden** fÃ¼r `/lager/materialfluss` (Prototyp + spÃ¤tere API-Anbindung).
- **Integration:** Dependency im Frontend-Web; Knoten-`data` aus API `material_flow_nodes` mappen (`node_type`, `status`, `layout_x`/`layout_y`).

### 2. MapLibre GL JS

- **GitHub:** https://github.com/maplibre/maplibre-gl-js
- **Lizenz:** BSD-3-Clause
- **Nutzen:** GPS fÃ¼r Silos, Waagen, mobile Einheiten; Luftbild-Underlay.
- **Risiken:** Styling/Token fÃ¼r Kartenquellen; kein Built-in â€žSilo-ERPâ€œ.
- **Empfehlung:** **verwenden** (bereits im Repo) â€” Bird-View in WM-AGRI-MAP-001.
- **Integration:** Geo-Felder `geo_lat`/`geo_lng` an `material_flow_nodes` (Migration WM-AGRI-SILO-001).

### 3. Konva / react-konva

- **GitHub:** https://github.com/konvajs/konva
- **Lizenz:** MIT
- **Nutzen:** Freies Zeichnen (Silos als Polygone, Pfeile, Symbole) auf statischem Hintergrund.
- **Risiken:** Eigenaufwand fÃ¼r Persistenz/Snap; Konkurrenz zu React Flow fÃ¼r reinen Fluss â€” eher **Layout-Editor** als Routing-Logik.
- **Empfehlung:** **spÃ¤ter prÃ¼fen** / optional parallel zu MapLibre-Overlay.
- **Integration:** Nur bei Bedarf fÃ¼r â€žHofplan zeichnenâ€œ.

### 4. FUXA

- **GitHub:** https://github.com/frangoteam/FUXA
- **Lizenz:** MPL-2.0 (zu prÃ¼fen bei Embedding)
- **Nutzen:** Referenz fÃ¼r webbasierte SCADA/HMI, Protokoll-Matrix.
- **Risiko:** Volles SCADA-System nicht als Drop-in ins Monorepo.
- **Empfehlung:** **nur inspirieren** (Adapter-Muster, Tag-Modell).

### 5. node-opcua / Apache PLC4X / pymodbus

- **Empfehlung:** **spÃ¤ter prÃ¼fen** im Slice WM-AGRI-PLC-005; Python-Backend kann `pymodbus` o. Ã¤. evaluieren, getrennt von UI.

### 6. Node-RED / ThingsBoard / JaamSim / SimPy

- **Empfehlung:** **nur inspirieren** â€” Orchestrierung bzw. Simulation nicht Teil von WM-AGRI-SILO-001.

## Architekturentscheid (Slice 001)

| Schicht | Wahl |
|---------|------|
| Materialfluss-UI (Graph) | **React Flow** (`@xyflow/react`) |
| Hof-/Bird-View | **MapLibre** (bereits vorhanden), Slice WM-AGRI-MAP-001 |
| Freier Zeichen-Editor | **Konva** optional spÃ¤ter |
| PLC/SCADA | **Kein** Einbau in 001; Doku + WM-AGRI-PLC-005 |
