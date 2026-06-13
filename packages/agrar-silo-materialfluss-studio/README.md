# Agrar-Silo-Materialfluss-Studio (Baustein)

EigenstÃ¤ndiger **Vite + React**-Prototyp fÃ¼r Silozellen-, SchÃ¼ttgut- und Materialfluss-UI (Flowsheet, Liste, Routenplaner). Die **Mock-REST-API** liegt in `server.ts` und entspricht fachlich grob dem Agrar-WMS-Materialfluss â€” **nicht** dem produktiven FastAPI-Endpunkt.

## VALEO NeuroERP

- Produktive API und ERP-OberflÃ¤che: Slice **WM-AGRI-SILO-001**, Route `lager/materialfluss`, Backend `agri_silo_material_flow`.
- Archiv-Einbindung und Abgrenzung: `docs/warehouse/agrar-silo-materialfluss-studio-baustein.md`.

## Start

```bash
pnpm install
pnpm run dev
```

## Komponenten

- `src/components/SiloFlowsheet.tsx` â€” Graphik / Materialfluss
- `src/components/SiloCellList.tsx` â€” Silozellen / QS
- `src/components/RoutePlanner.tsx` â€” Route und Validierung

## Herkunft

UrsprÃ¼nglich aus **Google AI Studio** exportiert (Metadaten: `metadata.json`). Lizenzhinweise in den Quelldateien beachten (Apache-2.0-Kommentare im Export).
