# Ackerschlagkartei — IST-Audit

Stand: 2026-07-16
Quellen: Lastenheft `lastenheft-ackerschlagkartei-lwk-2017-plus-valeo.md`, Code-Inventar Portal/ERP

## Portal

| Artefakt | Pfad | Status |
|---|---|---|
| UI Feldbuch | `packages/frontend-web/src/pages/portal/feldbuch.tsx` | vorhanden + Inkrement-1 |
| UI DüV-Auswertungen | `packages/frontend-web/src/pages/portal/feldbuch-auswertungen.tsx` | vorhanden (AS-W10) |
| API | `app/api/v1/endpoints/portal_feldbuch.py` | vorhanden + Inkrement-1 |
| Domain | `app/agrar/feldbuch/*` | Rechenkerne + Inkrement-1 |
| Modelle | `FeldbuchSchlag`, `FeldbuchMassnahme` | flaches Journal-Modell |

## ERP-Agrar (Dienstleister)

| Artefakt | Pfad | Status |
|---|---|---|
| Schlagkartei UI | `pages/agrar/feldbuch/schlagkartei.tsx` | vorhanden (MapLibre/GIS) |
| Maßnahmen UI | `pages/agrar/feldbuch/massnahmen.tsx` | vorhanden |
| API | `app/api/v1/endpoints/agrar_feldbuch.py` | CRUD, GeoJSON, Bilanz, QS/LEA |

## Bereits geschlossen (AS-W1…W10)

Düngung/Reinnährstoffe, Düngebedarf, Stoffstrom, PSM-Compliance, Nmin/Boden, Ernte/DFL, Anbauplan, ANDI-Import, Auswertungs-UI.

## Inkrement-1 (2026-07-16, TDD)

Arbeitskontext, Schlaginfo, Jahreswechsel, Sammelbuchung Düngung, `wirtschaftsjahr` am Schlag.

## Offene Cluster (ehrlich)

Mobile/Offline, volles Stammdaten-UI Portal, Sachkundenachweis-Freigabe, NÄON/ENNI, Precision Farming, Geometrieversionierung, Vier-Augen, volles Aggregate-Modell Kap. 41.
