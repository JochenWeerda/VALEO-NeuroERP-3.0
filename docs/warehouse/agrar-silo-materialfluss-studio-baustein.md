---
title: Grafik-Baustein Agrar-Silo / Materialfluss / Route (Studio-Prototyp)
type: explanation
audience: [entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Studio-Prototyp fuer Agrar-Silo- und Materialfluss-Visualisierung — Baustein-Beschreibung und Einbindung fuer WM-AGRI-SILO-001.
---

# Grafik-Baustein: Agrar-Silo, Materialfluss, Route (Studio-Prototyp)

**Quelle:** Archiv `agrar-silo-materialfluss.zip` (Google AI Studio Export, Juni 2026), eingebunden als eigenstÃ¤ndiges Paket.

**Ort im Monorepo:** `packages/agrar-silo-materialfluss-studio/`

**Bezug Produkt:** Slice **WM-AGRI-SILO-001** â€” produktive UI: `materialfluss.tsx` (Betrieb, Tabellen, Route) und `materialfluss-visualisierung.tsx` (Layout-Werkstatt, **PageToolbar** / MERIDIAN-Tokens laut `docs/design/EMPFEHLUNG.md`). Das Studio ist absichtlich **getrennt**: Es dient als **UX-/Interaktionsreferenz** (Flowsheet, Zellenliste, Routenplaner mit Mock-API), nicht als produktiver Screen.

## Inhalt des Bausteins

| Baustein | Datei | Zweck |
|----------|--------|--------|
| Flowsheet / Ãœberwachung | `src/components/SiloFlowsheet.tsx` | Grafische Darstellung Knoten/Kanten, Auswahl Quelle/Ziel |
| Silozellen / SchÃ¼ttgut | `src/components/SiloCellList.tsx` | Tabellarische Silozellen mit QS-Status, KapazitÃ¤t |
| Materialfluss / Steuerung | `src/components/RoutePlanner.tsx` | Routenwahl, Validierungsergebnis (inkl. SpÃ¼lcharge-Hinweis) |
| Mock-Backend | `server.ts` | Express + Vite: `/api/warehouse/silo-cells`, `material-flow/nodes`, `edges`, `validate-route` â€” **Demo-Daten**, nicht FastAPI |

Typdefinitionen: `src/types.ts` (an VALEO-Domain angleichbar, wenn Komponenten portiert werden).

## Lokal starten

```bash
cd packages/agrar-silo-materialfluss-studio
pnpm install   # oder npm install
pnpm run dev
```

Der Dev-Server startet Ã¼ber `tsx server.ts` (Vite Middleware + Mock-Routen). Eine **GEMINI_API_KEY** ist in der ursprÃ¼nglichen AI-Studio-Anleitung genannt; der aktuelle `server.ts` nutzt sie fÃ¼r die Mock-API **nicht** â€” Keys nur setzen, wenn ihr spÃ¤ter KI-Hilfen aus `@google/genai` anbindet.

## Integration ins NeuroERP (Richtung)

1. **Daten:** Produktiv weiterhin `GET/PATCH â€¦/api/v1/lager/wms/agri/â€¦` und `agri-material-flow.ts` im Frontend.
2. **UI:** Interaktionsmuster aus `SiloFlowsheet` / `RoutePlanner` schrittweise in `materialfluss.tsx` / `materialfluss-visualisierung.tsx` oder Mask-Builder Ã¼bernehmen (React Flow ist im Haupt-Frontend bereits im Einsatz). Shell: **PageToolbar** wie in anderen Modulen (`docs/design/EMPFEHLUNG.md` Phase 3).
3. **Kein Doppel-ORM:** Demo-Entities in `server.ts` nicht mit Alembic-Tabellen verwechseln.

## Verwandte Doku

- `docs/warehouse/agri-silo-material-flow-benchmark-2026-06-12.md`
- `docs/warehouse/reusable-open-source-silo-material-flow-2026-06-12.md`
- `docs/agent-ops/slices/WM-AGRI-SILO-001.yaml`
