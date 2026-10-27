---
title: Adaptive Workspace Framework
type: architecture
audience: [agent, entwickler, architect]
owner: Cursor Grok
status: aktiv
last_reviewed: 2026-10-22
version: 0.1.0
description: Master-Ist/Soll fuer den Adaptive Workspace innerhalb von VALEO — Registry, Command Center, Priorisierung, Phasen. Kein zweites Frontend.
---

# Adaptive Workspace Framework

Stand 2026-10-22. Phase-1-Lead: Slice `ADAPTIVE-WORKSPACE-20261022`.
Geschwister-Docs (Inhalt dort, hier nur Verweis):

- Inbox / Beleg-Pipeline: [`adaptive-workspace-inbox.md`](adaptive-workspace-inbox.md)
- LKW-Disposition: [`adaptive-workspace-disposition.md`](adaptive-workspace-disposition.md)
- Domain-Events / MCP: [`adaptive-workspace-events-mcp.md`](adaptive-workspace-events-mcp.md)
- ERPNext/Frappe-Ableitungen: [`adaptive-workspace-erpclow-lessons.md`](adaptive-workspace-erpclow-lessons.md)
- Studio-Zusammensetzung: [`adaptive-workspace-studio.md`](adaptive-workspace-studio.md)
- Agrar-E2E: [`adaptive-workspace-agrar-e2e.md`](adaptive-workspace-agrar-e2e.md)

Leitprinzip: Der Benutzer sucht nicht die App; das System stellt Aufgaben,
Infos und Aktionen kontextbezogen bereit. Agrarhandel ist Referenzbranche,
nicht Architekturgrenze.

## Nicht-Ziele

- Keine drei Apps (Launcher / Beleg-Inbox / Dispo) und kein Python-Frontend.
- Kein Frappe-/ERPNext-Port, kein zweites Masken-Framework.
- Keine parallele Belegverwaltung; Buchungen nur ueber autorisierte Domaenendienste.
- ProcessBand und ProcessRibbon bleiben getrennt.
- Codex-Godfiles (Tourenplanung, Training, Bestellvorschlaege) und STUDIO-*-Claims
  bleiben unangetastet.
- KI darf empfehlen und Fachcommands vorbereiten, nicht persistieren.

## Ist-Bestand (gemessen, nicht geraten)

### Launcher / Home

| Baustein | Pfad | Stand |
|---|---|---|
| Spaces/Pages-Katalog | `packages/frontend-web/src/app/navigation/launchpad-spaces.ts` | Arbeitswelten (Handel, Ernte, Logistik, …), Kachelarten app/task/kpi/alert |
| Personalisierung | `launchpad-personalization.ts`, `hooks/useLaunchpadPersonalization.ts` | Overlay lokal (`valeo.launchpad.overlay`): Reihenfolge, Ausblenden, eigene Gruppen |
| Pin | `hooks/usePinnedTiles.ts` | Sidebar-Pins (`valeo.start.pinnedTiles`), getrennt vom Overlay |
| Launchpad-UI | `components/navigation/LaunchpadBoard.tsx` | Anpassen-Modus, Katalog, Drag; nimmt `rankedTileIds` und Overlay-Pin/`surfaceLocked` |
| Startseite | `pages/start-dashboard.tsx` | **Schicht:** `AdaptiveWorkspaceLayer` (Registry, Handlungsbedarf, Launchpad) **darueber**, `UniversalNativeCockpitPage` `screenId="start-dashboard"` darunter |
| Cockpit-SD | `app/core/screen_definitions_cockpit.py` `workspace/start-dashboard` | Fuenf Workspace-Kacheln (Einkauf/Verkauf/Lager/FiBu/Leitung) |
| Rollen-Workspaces | `pages/workspace/{einkauf,verkauf,lager,fibu,leitung}.tsx` | Native Cockpits, Flag `roleWorkspaces` default aus |

Home-Draht (Phase 1): `AdaptiveWorkspaceLayer` liest Spaces aus der Navigation,
rangiert Fachaktionen aus `src/workspace/`, pinnt/`surfaceLocked` im Overlay
und reicht `rankedTileIds` an `LaunchpadBoard`. Das Native-Cockpit bleibt die
Meridian-Runtime fuer Rollen-Kacheln, nicht eine zweite Start-App. Live-Zaehler kommen aus Queue-GETs und dem SSE-Kanal `/api/events?stream=workspace`
unter Originalnamen (keine Soll-Rename); bei 401/Offline bleibt der
Kalender-Fallback. Die Agrar-Kette liest KonContracte plus
`GET /api/v1/agrar/contracts` (`id`+`status`, `source_model=agrar`; QS/Settlement
fehlen dort, Kon-`abrechnung` bleibt unprojizierbar). Studio-Preview haengt additiv
unter `/studio/workspace-composition-preview` in `router.tsx`, ohne `route-tree.gen`.
401/Offline blendet die Sektion aus, andere Fehler bleiben sichtbar. Keine Buchung.
Gueltige Session `valeo.workspace.composition` steuert, ob Home Inbox und Dispo-Tafel mountet und in welcher View-Reihenfolge; leer oder ungueltiges JSON faellt auf den bisherigen Default Inbox-dann-Dispo zurueck.

### Command Center (Strg+K)

| Baustein | Pfad |
|---|---|
| Palette UI | `packages/frontend-web/src/components/navigation/CommandPalette.tsx` |
| Command-Katalog | `command-palette-model.ts` (hartcodierte Navigation + Mask-Registry + Omnibox) |
| Shortcuts | `app/navigation/action-shortcuts.tsx`, `ai-shortcuts.tsx` |
| NL-Navigate | `lib/omnibox/intent-compiler.ts` (UIX-060) |
| NL-Command-Draft | `lib/omnibox/command-compiler.ts` (UIX-070, kein Auto-Submit) |
| Tastatur | `AppShell.tsx` Strg+K, Feature-Flag `commandPalette` default an |

Zweite Paletten (`components/command/CommandPalette.tsx`,
`components/innendienst/CommandPalette.tsx`) sind Altpfade und nicht kanonisch.

YAML ist Source of Truth; Frontend-`catalogId` ist die YAML-`action_id`.
Phase 1 haengt berechtigte Fachaktionen aus `src/workspace/` an denselben
Katalog (`command-mapping.ts`). Optional konsumiert das Command Center live
`workspace.fachaktion.resolve` (`POST /api/v1/mcp/tools/call`, dryRun) und
faellt bei Offline/401 auf den lokalen Katalog zurueck. Nur `navigate` /
`open-worklist` / `prepare-command`; `prepare-command` setzt `omniboxAction`.
Kein Auto-Submit, keine Client-Umgehung von WRITE/Vier-Augen.

### Masken-Pipeline (unveraendert)

```text
ScreenDefinition → RenderPlan → useUniversalMaskRuntime → UniversalMaskRenderer
```

Cockpit-Kacheln: `TileGridRenderer`. Home konsumiert zwei Geschwister-Slots,
ohne deren Quellen zu besitzen:

| Slot | Home | Vertrag (Details in Geschwister-Docs) |
|---|---|---|
| Inbox | `InboxWidget` in `AdaptiveWorkspaceLayer` | `GET /api/mcp/documents/inbox/queue`; Klick → bestehende Belegmaske; approve bleibt 409; Prefill-Luecke wird angezeigt, nicht umgangen |
| Dispo | Kachel/View | Route `/disposition/touren-disposition`, Studio-Kind `disposition_board`, id `lkw-disposition-board`. Godfile `tourenplanung.tsx` bleibt aussen vor |

Gantt und die Basiskarte bleiben Metadaten. `DispositionBoard` zeigt `lat`/`lng` aus `GET /api/v1/logistik/tours/{id}` (`laneFromTourDetail`), ohne neue Kartenbibliothek und ohne Basiskachel. `SchlagKarte` bleibt Flaechen-GeoJSON.

### Beleg-Inbox, Dispo, MCP/Events

Nur Orientierung, Besitz bei Geschwister-Agenten. Details in den
verlinkten Docs. Kurz: DMS-Inbox unter `/inbox` (Cockpit +
`/api/v1/dms/inbox`), Touren-Disposition als Cockpit-SD, MCP-Writes ueber
`mask.action.execute` und MCP-WRITE-001–015, Outbox + SSE (`useSSE.ts`)
bereits vorhanden.

## Soll

Vier Ebenen im **einen** VALEO-Workspace:

| Ebene | Inhalt | Quelle in Phase 1 |
|---|---|---|
| Persoenlich | Rollen, Rechte, Favoriten, Pin, Arbeitsweise | `UserContext` + Launchpad-Overlay |
| Situativ | Saison, Tageszeit, offene Aufgaben, Vorfaelle | deterministische Signale (`WorkspaceSignal`) |
| Proaktiv | Engpaesse, Fristen, Handlungsbedarf | dieselben Signale, hoehere Severity/Deadline |
| Dialog | natuerliche Sprache + Tastatur | Die Startflaeche oeffnet die bestehende Palette per Strg+K; freie Eingabe laeuft dort ueber `workspace.fachaktion.resolve` (dryRun) plus lokalen Alias-Fallback, ohne Auto-Submit und ohne zweite Kommandozeile. |

Priorisierung ist regelbasiert und nachvollziehbar (`reasonCodes`).
KI ist ein optionaler `RankingAdvisor`, Default ist Identitaet (kein LLM).
Fixierte Oberflaeche (`surfaceLocked`) verhindert automatisches Umsortieren
der Launchpad-Kacheln; die Work-Item-Leiste bleibt priorisiert.

Command Center erzeugt nur **berechtigte typisierte Fachaktionen**:
`navigate`, `open-worklist`, `prepare-command`. Keine freien API/DB-Calls.
`prepare-command` oeffnet die Zielmaske mit `omniboxAction` — Ausfuehrung
bleibt Masken-Ritual / Server. Client-Filter ist UX; Rechte bleiben
serverseitig.

Studio soll spaeter Arbeitsraeume und Spezialkomponenten ueber Metadaten
zusammensetzen. Phase 1 liefert die IDs, nicht die Renderer.

## Uebernahme erpclow / ERPNext / Fiori (kurz)

Ausfuehrung und Verwerfung: [`adaptive-workspace-erpclow-lessons.md`](adaptive-workspace-erpclow-lessons.md).
Phase 1 uebernimmt nur das, was zu Meridian/Studio/MCP-WRITE/Mandant passt:

| Ansatz | Uebernahme | Verworfen |
|---|---|---|
| ERPNext Workspace-Seiten statt App-Kacheln | VALEO-Spaces/Pages + Registry-Module | Frappe Desk / DocType-UI |
| AwesomeBar (Ctrl+K) auf berechtigte Aktionen | bestehendes Command Center + Fachaktionsvertrag | globale Record-Suche als Schreibweg |
| ToDo / Notifications als proaktive Ebene | `WorkspaceSignal` + Ranking | Frappe-ToDo-DocType |
| Desk-Bootstrapping aus Metadaten | Registry als Katalog fuer Studio (Phase 2) | Frappe-Client-Scripts, zweites Framework |
| SAP Fiori Spaces/Pages | bereits VALEO-IA (`launchpad-spaces.md`) | Belize, Transaktionscodes, Kachelfarben |
| Odoo systray | nicht in Phase 1 | Discuss-Port |

## Phasen

| Phase | Ziel | Diese Session |
|---|---|---|
| **1** | Registry, User-Context, Command-Mapping, Priorisierung, Pin/Fixieren | **geliefert** — Fachaktion-Pin + Oberfläche; Composition-View-Pin/Start-Fix im Overlay `valeo.workspace.composition.overlay` (Code + Tests, kein Feature-Commit) |
| **2** | Inbox-Widget und Dispo-Tafel als Spezialkomponenten; Studio-Bindung | Home konsumiert die Slots; Implementierung bleibt Geschwister |
| **3** | Domain-Events, Transaktionsgrenzen, Echtzeitprojektionen | nicht dieser Slice |
| **4** | KI-Orchestrierung auf MCP-Fachcommands | leerer Ranking-Hook, sonst Geschwister |
| **5** | Agrar-E2E Kontrakt → Dispo → Waage → Qualitaet → Abrechnung | nicht dieser Slice |

## Dateibesitz Phase 1

Erlaubt:

- `packages/frontend-web/src/workspace/**`
- `packages/frontend-web/src/app/navigation/**`
- `packages/frontend-web/src/pages/start-dashboard.tsx` (Home-Draht; Cockpit bleibt)
- `packages/frontend-web/src/components/navigation/LaunchpadBoard.tsx` (`rankedTileIds`, Overlay-Pin/Lock)
- Command-Palette-Mapping (`command-palette-model.ts`, `CommandPalette.tsx`)
- `docs/architecture/adaptive-workspace-framework.md`
- eigene Tests unter `src/__tests__/workspace` und die Home-/Launchpad-/Palette-Tests

Nicht:

- Inbox, Documents, CaptureScreenHost
- Touren / Dispo / Fuhrpark-Godfiles
- MCP-Execution, Mask-Action-Runtime, NATS-Core
- Geschwister-Docs und Codex-Slices STUDIO-*, Touren, Training, Bestellvorschlag

## Offene Luecken nach Phase 1

- Home konsumiert Ist-Typen auf SSE `workspace` (Originalnamen) plus Inbox-/
  Freigabe-Queue-GETs; bei 401/Offline bleibt der Kalender-Fallback.
  Gemappte Ist-Typen in `live-signals.ts` (Delta): u. a. live auf SSE `agrar.weighing_ticket.allocated`
  → `harvest.intake-queue` und `agrar.quality_protocol.completed` → `agrar.qualitaets-handlungsbedarf`
  (Soll-Annotation `document_posted` wird ignoriert). QS-Finalize schreibt Outbox in
  `quality_protocols.py` (Spiegel ueber bestehendes `OutboxPublisher.store_event`).
- Client-RBAC der lokalen Palette bleibt UX; Live-Resolve prueft serverseitig
  und wird bei 401/Offline nicht erzwungen.
- Inbox-/Dispo-Renderer und Event-Projektionen bleiben Geschwisterbesitz;
  Home zeigt nur die Slots.
