# Benchmark: Agrar-Silo, Materialfluss, QS (Kurzstudie)

**Datum:** 2026-06-12
**Bezug:** WM-AGRI-SILO-001 (additiv zu WM-STRUCT-001 Lager â†’ Zone â†’ Gang â†’ Fach)

## Zielbild Landhandel / Agrar

Ãœber die generische WMS-Hierarchie hinaus sind typischerweise relevant:

- **Lagerobjekte:** Lagerhaus, HofgelÃ¤nde, Siloanlage, Silo, Silozelle/Kammer, Flachlager/Box, FÃ¶rderweg, Waage, Annahme, Verladung, mobile Misch-/Mahlwagen (MMX).
- **Prozess:** Chargen/Lots, QS-Freigabe, Sperre, Schwund, **Verschleppungsschutz** (SpÃ¼lcharge, Reinigungsnachweis).
- **Visualisierung:** Bird-View (Hofplan), graphischer Materialfluss (Knoten/Kanten), spÃ¤ter ggf. Anlagen-/SCADA-Anbindung (nur Architektur, keine PLC-Pflicht in Slice 001).

## Interne Repo-Referenzen

| Thema | Ort |
|--------|-----|
| WMS-Struktur Zone/Gang/Fach | `WM-STRUCT-001`, `warehouse_wms`, `lagerplaetze.tsx` |
| RÃ¼ckverfolgbarkeit / Kette / QS-Stufen | `DOM-SUPPLY-004` â€” `rueckverfolgbarkeit.tsx`, Supply-Chain-API |
| Karten-Baustein (Hof spÃ¤ter) | `maplibre-gl` bereits in `packages/frontend-web/package.json` |
| UI-Studio (Flowsheet, Zellen, Route, Mock-API) | `packages/agrar-silo-materialfluss-studio` â€” siehe `agrar-silo-materialfluss-studio-baustein.md` |
| Referenz-Hofplan (Beispiel Landhandel) | `docs/warehouse/folkerts-landhandel-hofplan.md` + Bild unter `docs/warehouse/references/` |
| Externes Betriebshandbuch (Windows `C:\Handbuch`) | `docs/warehouse/handbuch-c-inventar.md` (Warenflussdiagramm, Lager, QS) |

## Externe Muster (keine 1:1-Produkte)

- **Getreide-/Agrar-ERP:** Marktangebote kombinieren oft Lagerverwaltung mit Partie/Chargen und QS; fachliche Tiefe liegt in **Silo-Zellen** + **Materialwechsel-Regeln**, nicht nur in Lagerplatz-Codes.
- **Feed-Mill / Batching:** Typisch Chargenprotokoll, Rohwarenfreigabe, Formelversionen; technisch oft Ã¼ber MES/PLC oder InsellÃ¶sungen â€” VALEO priorisiert zuerst **digitales Modell + API + UI-Skizze**.
- **WMS mit Layout:** Yard-/Warehouse-Maps sind oft Custom (GIS + Overlay oder Canvas-Editor); wiederverwendbar sind **Karten-Engines** und **Graph-Editoren** (siehe `reusable-open-source-silo-material-flow-2026-06-12.md`).

## Empfehlung fÃ¼r VALEO

1. **Datenmodell** Siloanlage / Silozelle / Materialfluss-Knoten/-Kanten in `domain_inventory` (umgesetzt in WM-AGRI-SILO-001).
2. **Route-Validierung** rein digital (BFS, QS-Sperre, Verschleppungs-Hinweis).
3. **UI:** React Flow fÃ¼r Editor/Visualisierung; MapLibre spÃ¤ter fÃ¼r Bird-View.

## Folge-Slices (Roadmap)

| ID | Inhalt |
|----|--------|
| WM-AGRI-MAP-001 | Bird-View Hof/Lagerhaus mit Luftbild/MapLibre, zeichnbare Silos |
| WM-AGRI-FLOW-002 | Simulation / Live-ZustÃ¤nde auf dem Graph |
| WM-AGRI-QS-003 | Rohwarenfreigabe, LaborÃ¼bergabe, Freigabe MMX |
| WM-AGRI-MOBILE-004 | Mobile Anlagen, Standort, Mischprotokoll Tablet |
| WM-AGRI-PLC-005 | OPC-UA / MQTT / CSV-Import Hersteller |
| WM-AGRI-FLUSH-006 | SpÃ¼lchargen, Verschleppungsmatrix, QS-Nachweis |

Siehe auch `WM-AGRI-FLOW-001.yaml`.
