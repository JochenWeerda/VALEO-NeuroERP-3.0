---
title: Adaptive Workspace — LKW-Disposition
type: architecture
audience: [architect, entwickler, agent]
owner: Dispo-Agent
status: aktiv
last_reviewed: 2026-10-22
---

# Adaptive Workspace — LKW-Disposition

LKW-Disposition ist eine **registrierbare Spezialkomponente** im
`UniversalMaskRenderer`, keine eigene App. Drag-and-Drop ist UX. Das Backend
validiert **vor** jeder Persistenz. Kontraktmengenbuchung entsteht erst beim
fachlichen Buchungsereignis, nie beim Drop.

## SpecializedComponent-Vertrag

| Feld | Wert |
|---|---|
| `type` | `disposition_board` (einziger erlaubter Specialized-Typ in diesem Slice) |
| `id` | `lkw-disposition-board` |
| `events` | `logistik.tour.created` (Ist, Soll `assignment_confirmed`), `logistics.tour.quantity_posted`, `disposition.board.drop_proposed` |
| `permissions` | `logistics.write` für Drop/Bestätigung, `logistics.read` für die Tafel |
| `liveChannel` | `disposition.board` |

ScreenDefinition-Erweiterung (Frontend, `schema.ts`):

```ts
specialized?: {
  type: 'disposition_board'
  id: string
  events?: string[]
  permissions?: string[]
  liveChannel?: string
}
```

Der RenderPlan trägt dasselbe Objekt. `UniversalMaskRenderer` löst über
`components/mask-builder/specialized/registry.ts` auf.

### Drei synchrone Sichten

1. **Aufträge / Kontrakte** — vorhandene Kontrakt-Abrufe als Drag-Quelle
   (`GET /api/v1/kontrakte` plus `GET /api/v1/kontrakte/{id}/dispositionen`).
   KonContract und AgrarContract bleiben getrennte Modelle.
2. **Ressourcen / Planung** — Fuhrpark, Spedition, Fahrer als Drop-Ziele;
   Timeline aus der bestehenden Tourenlage; Karte bewusst optional/Stub.
3. **Betriebszustände** — echte Signale: offene Wiegescheine (`GET /api/v1/weighing-tickets`) als „Waage belegt“ und Workspace-SSE `agrar.weighing_ticket.allocated` / `lager.einlagerung.created` / `goods_receipt.created` als Zeilen mit Zeit; kein Occupancy-GET, keine erfundenen Verladung-/Störungs-KPIs.

## Event-Namen (verbindlich)

Kein NATS-Rename. Der Workspace-Spiegel mappt Ist → Soll, der Stream trägt den Ist-Typ.

| Ist (Outbox / stream=workspace) | Soll-Annotation | Wann | Nicht wann |
|---|---|---|---|
| `logistik.tour.created` | `assignment_confirmed` | Prüfung bestanden **und** Tour/Stopp persistiert | Hover, Drop ohne API, dry-run |
| — | `quantity_posted` / intern `logistics.tour.quantity_posted` | Waage, ePOD, Kontraktabruf geliefert | **nie** beim Drop |
| `disposition.board.drop_proposed` | — | nur Client-UX | Persistenz / Outbox |

Drop-Payload enthält immer `quantityPosted: false`. Ist die Quelle ein Abruf,
geht `abruf_id` additiv mit (Assignment-Service, nicht `logistics_tours.py`).
`posts_quantity=true` am
Assign-Endpunkt ist ein 422 (`quantity_post_on_drop_forbidden`).

## Domänenpersistenz

| Frage | Stand |
|---|---|
| Persistiert? | **Ja** — nach bestandener Prüfung, in derselben Transaktion wie die Outbox |
| Tabellen | `domain_logistics.tours`, `domain_logistics.tour_stops` (Schema `log_logistics_core_20260612`) |
| Schreibweg | `app/services/disposition_assignment_repository.py` — additiv, **ohne** `logistics_tours.py` |
| Event | `logistik.tour.created` über `_write_outbox` (Ist-Publisher; Spiegel `assignment_confirmed`) |
| Mengenbuchung | nein; Stopp trägt `delivery_note_ref`, keine Kontraktmenge |
| Drop → API | **Ja** — `disposition_board` POSTet `/api/v1/logistik/disposition/assignments` (`posts_quantity: false`). Godfile-Tafel unverändert. Nach erfolgreichem POST und bei SSE `logistik.tour.created` auf `/api/events?stream=workspace` laden Auftrags- und Ressourcenspalte neu (kein zweiter Bus; 401 bleibt sichtbar). Zeitachse liest nur `planned_arrival` der Tour-Detail-API (kein `start`/`ende`/`zeitfenster` am Tour-Kopf; nichts erfunden). |

Vorhandene Tour (gleicher Mandant): neuer Stopp. Unbekannte `resource_id`: INSERT Tour + Stopp. Fremder Mandant: kein Schreib, 422.

## Ist-Pfade

### UI (bestehende Tafel — nicht neu gebaut)

| Pfad | Rolle | Besitz |
|---|---|---|
| `packages/frontend-web/src/pages/logistik/tourenplanung.tsx` | Operative Touren-Tafel (Godfile) | **Codex-Besitz, nicht anfassen** |
| `packages/frontend-web/src/pages/logistik/tour-fracht-arbeitsraum.tsx` | Kombinierter Dispo-Arbeitsraum | **Codex-Besitz, nicht anfassen** |
| `packages/frontend-web/src/masks/capture-screens.ts` (`tourenplanungScreen`) | ScreenDefinition der Godfile-Tafel | **Codex-Besitz, nicht anfassen** |
| `packages/frontend-web/src/pages/disposition/touren-disposition.tsx` | Adaptive-Workspace-Host der Spezialkomponente | Dispo-Agent |
| `packages/frontend-web/src/pages/disposition/bestell-vorschlag.tsx` | Bestellvorschlag-Cockpit | **Codex-Besitz, nicht anfassen** |
| `packages/frontend-web/src/lib/logistik/disposition.ts` | Dispositionsstand-Helfer (read-only genutzt) | gemeinsam, hier nur gelesen |
| `packages/frontend-web/src/lib/api/misc-modules.ts` (`useTouren`) | Touren-Read-Model | gemeinsam, hier nur gelesen |
| `packages/frontend-web/src/lib/api/supply-chain.ts` | Waage/Lager/Sperren-Read-Model | gemeinsam, hier nur gelesen |

Es gibt **kein** `pages/touren/`. Die kanonische Tafel ist `/logistik/tourenplanung`.

### Backend-Assign / Check

| Pfad | Was er tut | Lücke |
|---|---|---|
| `POST /api/v1/logistik/tours/{id}/disposition-check` in `app/api/v1/endpoints/logistics_tours.py` | Kapazität + Zeitfenster **nach** vorhandenen Stopps | Codex-nahe Tourenplanung-Engine; **nicht gehärtet** in diesem Slice |
| `app/services/logistics_disposition_service.py` | Implementierung des Checks, schreibt `tour_disposition_checks` | kein Mandant/Recht/Kontrakt/Concurrency/Freigabe vor Assign |
| `POST /api/v1/tours/{id}/stops/{stop_id}/delivery-notes` in `app/api/v1/endpoints/tours.py` | Lieferschein an Stopp | keine Assign-Validierung vor Persistenz |
| `POST /api/v1/logistik/disposition/assignments` | Prüfung, dann Tour/Stopp + Outbox `logistik.tour.created` | keine Mengenbuchung; schreibt nicht über `logistics_tours.py`; optionales Feld `abruf_id` |
| `GET /api/v1/kontrakte/{kontrakt_id}/dispositionen` | bestehende Abruf-Liste (Agrar, Rollen `ROLE_LESEN`/`BEARBEITEN`/`ADMIN`) | Tafel-Adapter, kein neuer List-Endpunkt; 401/403/503 = ehrlicher Fehler, kein Mock |
| `app/api/v1/endpoints/disposition.py` | **andere** Fachlichkeit (Nachbestell-Positionen) | Namenskollision, nicht LKW-Dispo |
| `app/services/kontrakt_disposition_service.py` | Agrar-Kontraktabruf / Mengen | `quantity_posted`-Pfad, nicht Drop; zwei Kontrakt-Modelle bleiben getrennt |

## Codex-Kollisionen (nicht anfassen)

| Claim / Datei | Haltung |
|---|---|
| Tourenplanung-Godfile `pages/logistik/tourenplanung.tsx` | Adapter verweist darauf; keine zweite Tafel, keine Edits |
| Tour-Fracht-Arbeitsraum | Godfile; Claim-Schutz laut Maskenfamilien-Taxonomie |
| Bestellvorschlag / Training | fremder Dateibesitz |
| STUDIO-BELEG-THEME / STUDIO-MODEL / CI-GRUEN | **Codex-Besitz, nicht anfassen** |
| `app/core/screen_definitions_cockpit_batch14.py` | generiertes Backend-Cockpit für `disposition/touren-disposition`; Spezialkomponente sitzt lokal im Frontend |
| `app/api/v1/endpoints/logistics_tours.py` + `command_handlers/logistics.py` | Tourenplanung-Engine; Assign-Check bleibt Gap |
| Fuhrpark-Tenant-Migrationen | **Codex-Besitz, nicht anfassen** |
| `app/documents/**`, MCP-Execution, Workboard, Navigation/Launchpad, Command Palette | außerhalb des Dateibesitzes |
| `config/architecture-index.yaml` | generiert; nicht manuell |

## Gebaute Dateien

### Frontend

- `packages/frontend-web/src/components/mask-builder/specialized/` — Registry, Vertrag, Board-Adapter, Host, Abruf-GET (`load-abrufe.ts`)
- `packages/frontend-web/src/pages/disposition/touren-disposition.tsx` — Host im UniversalMaskRenderer
- ScreenDefinition-Feld `specialized` in `schema.ts` **nur** für `disposition_board`
- minimale Durchleitung in `render-plan/types.ts`, `schema-compiler.ts`, `UniversalMaskRenderer.tsx`

### Backend

- `app/services/disposition_assignment_validation.py` — reine Prüfung
- `app/services/disposition_assignment_repository.py` — INSERT tours/tour_stops
- `app/services/disposition_assignment_service.py` — Prüfung, Persistenz, Outbox
- `app/api/v1/endpoints/disposition_assignment.py` — `POST /api/v1/logistik/disposition/assignments`
- Eintrag in `app/api/v1/api.py` (Include, kein Touren-Godfile)

### Tests

- `tests/test_disposition_assignment_validation.py` — unit/pure inkl. INSERT-Spalten, keine MagicMock-DB
- `tests/test_disposition_assignment_persist.py` — Integration nur `valeo_probe` / `TEST_DATABASE_URL`
- `packages/frontend-web/src/__tests__/components/mask-builder/specialized/disposition-board.test.tsx`
- `packages/frontend-web/src/__tests__/components/mask-builder/specialized/load-abrufe.test.ts`
- `packages/frontend-web/src/__tests__/components/mask-builder/specialized/post-assignment.test.ts`

## Validierung vor Persistenz

Die Prüfung blockt, bis alle Punkte grün sind:

1. Mandant (Sitzung = Ressource)
2. Recht (`logistics.write` aus Token-Rollen, **nicht** aus dem Body)
3. Kapazität (Ist-Last + Drop ≤ Fahrzeugkapazität)
4. Zeitfenster (Start/Ende innerhalb Window, Ende nach Start)
5. Vertrags-/Mengengrenzen (`allow_overdelivery` analog Kontraktregel)
6. konkurrierende Änderungen (`expected_version` vs. `current_version`)
7. Freigaben (`approval_required` ohne `approval_granted`)
8. `posts_quantity` am Drop → immer Sperre

Erst danach schreibt das Repository Tour/Stopp und die Outbox
`logistik.tour.created`. Godfile-Router bleiben unberührt.

## Bewusst Stub / Gap

- **Keine zweite Tafel.** Ressourcen-Spalte ist ein Adapter über `useTouren`;
  die operative Planung bleibt `/logistik/tourenplanung`.
- **Karte** optional, nicht eingebunden.
- **Live-Kanal** `disposition.board` ist Vertrag; SSE-Consumer ist nicht
  verdrahtet (würde Command Palette / Plattform berühren).
- **`POST .../disposition-check`** bleibt der nachgelagerte Kapazitätscheck der
  Godfile-Engine — nicht der Drop-Pfad.
- **`quantity_posted`** wird hier nur benannt, nicht ausgelöst. Buchung bleibt
  bei Waage / Kontraktabruf / ePOD.
- **Keine Navigation, kein Launchpad, kein Route-Generator-Lauf.** Die Seite
  `touren-disposition.tsx` existiert; Routing bleibt fremder Besitz.
- **Kein Feature-Commit.**

## Abnahme

- Drop ohne gültige Prüfung → 422, kein Event.
- Drop gültig → Zeile in `tours`/`tour_stops` + Outbox `logistik.tour.created`; `quantity_posted` bleibt aus.
- Spezialkomponente rendert die drei Sichten **innerhalb**
  `UniversalMaskRenderer`.
- Godfiles unverändert.
