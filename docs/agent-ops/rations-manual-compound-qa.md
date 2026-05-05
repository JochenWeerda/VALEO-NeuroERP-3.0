# Manuelle QA — Lieferschein / Mischfutter-Etikett (Rationsoptimierung)

Kurzcheckliste ohne Pflicht zu privaten Fotos im Repo. Für Regression nutzt das Projekt das PDF-Fixture unter `packages/frontend-web/tests/fixtures/rations/e2e-compound-label.pdf`.

## Vorbedingungen

- Backend: `uvicorn` auf Port **8000** (oder `E2E_BACKEND_URL`).
- Auth für Agrar-Routes: Header `Authorization: Bearer <E2E_API_DEV_TOKEN>` (Standard im Repo oft `dev-token`).
- Frontend: Playwright startet Vite automatisch (`playwright.config.ts`), oder eigener Dev-Server mit passender `FRONTEND_BASE_URL`.

## Schritte (manuell mit eigenem JPG/PDF)

1. Wizard öffnen → Schritt 2 → Datei auswählen (privates Bild/PDF nur lokal).
2. Nach Upload: Produktname und mindestens eine Nährstoffspalte (z. B. ME oder sidP) plausibel > 0.
3. Optimierung durchlaufen → Workbench: dieselbe Futtermittelzeile zeigt ME-/sidP-Beitrag konsistent (> 0 wenn das Mittel ME/sidP hat).
4. Bei Duplikat-Anzeigenamen in der Tabelle: zweite Spalte zeigt `(feed_id)` zur Unterscheidung.

## Automatisierung

- E2E (Compound-PDF): `pnpm test:e2e:rations-compound` im Paket `frontend-web`.
