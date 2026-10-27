---
title: Adaptive Workspace — Studio-Metadaten (WorkspaceComposition)
type: architecture
audience: [architect, agent, entwickler]
owner: Cursor Grok (Studio-Metadaten-Agent)
status: aktiv
last_reviewed: 2026-10-23
version: 1.4.0
description: >
  Phase-2-Vertrag und Runtime: Arbeitsräume aus Studio-Metadaten zusammensetzen
  (Slots, View-Reihenfolge) — lokal validiert, ohne Server-Write.
  Home mountet denselben Host (variant=embedded). Authoring-Dialog nach
  ScreenDefinition-Freigabe.
---

# Adaptive Workspace — Studio-Metadaten (Phase 2)

**Stand:** 2026-10-23. Vertrag + Parser/Validator + Fixture + Runtime-Host + **lokaler Compose**
+ **Home embedded Host** + **Studio-Authoring-Dialog**. Kein Studio-Release/CLI, kein Feature-Commit.

## 1. Ziel

Screen Studio so erweitern, dass **Arbeitsräume** und **Spezialkomponenten** (Document-Inbox, Dispo-Tafel) über Metadaten komponierbar sind. Kundenlayouts entstehen als versionierte `WorkspaceComposition`, nicht als neue React-Seiten.

Die Meridian-Pipeline bleibt verbindlich und unangetastet:

```text
ScreenDefinition → RenderPlan → useUniversalMaskRuntime → UniversalMaskRenderer
```

`WorkspaceComposition` sitzt **über** ScreenDefinitions: sie wählt Module, Views (jeweils eine `screenId`), Spezial-Slots und Fachaktions-Refs. Sie ersetzt weder `ScreenDefinition` noch den Launchpad-Katalog.

## 2. Ist (gelesen, nicht geändert)

| Artefakt | Rolle |
|---|---|
| `ScreenDefinition` (`mask-builder/schema.ts`) | Maskenvertrag; `adapter.type` kann `specialized` sein |
| `CockpitOverviewParent` | Shell für `floorplan=cockpit` |
| Screen Studio (`features/screen-studio/*`) | Authoring einzelner Masken; nach Freigabe Button → Composition-Dialog |
| [studio-semantic-standard.md](studio-semantic-standard.md) | Fachkatalog / STUDIO-SEMANTIC-001 |

## 3. Vertrag `WorkspaceComposition`

- Types/Validator: `packages/frontend-web/src/studio/workspace-composition.ts`
- Parser: `workspace-composition-parser.ts`
- Fixture: `config/studio_workspace_composition.fixture.yaml` + typed Spiegel

Determinismus: Issues sortiert nach `path`/`code`; `normalizeWorkspaceComposition` sortiert nach `order` dann `id`.

## 4. Runtime + lokaler Compose + Authoring

| Datei | Rolle |
|---|---|
| `workspace-composition-runtime.ts` | Mount-Plan aus Composition |
| `workspace-composition-session.ts` | Toggle/Reorder, localStorage, resolve via Parser |
| `workspace-composition-authoring.ts` | Reine Mutationen: Meta, Host-View, freigegebene Screen als View |
| `WorkspaceCompositionAuthoringForm.tsx` | Formular: Metadaten, Slot-Toggles, Host-View, View-Reorder |
| `WorkspaceCompositionAuthoringDialog.tsx` | Studio-Dialog um Formular; Speichern nur gültig |
| `WorkspaceCompositionHost.tsx` | Views-Liste + Slots (InboxWidget / registrierte Dispo-Tafel); `variant=studio|embedded` |
| `pages/studio/workspace-composition-preview.tsx` | Form + Dialog-Trigger + Host nur bei gültiger Composition |
| `workspace/home-composition.ts` | `resolveHomeComposition` → Session oder Fixture-Fallback |
| `workspace/AdaptiveWorkspaceLayer.tsx` | Home mountet denselben Host (`variant=embedded`) |

### Authoring vs. Host

| Ebene | Verantwortung |
|---|---|
| **Authoring** (Form/Dialog) | Composition editieren, validieren, localStorage speichern |
| **Host** | Nur gültige Composition mounten (Inbox/Dispo aus Metadaten) |

```text
ScreenDefinition freigeben (bestehendes Studio)
  → Dialog „In Arbeitsraum aufnehmen“ (releasedScreen)
  → upsertReleasedScreenView + Slot-/Meta-Edit
  → saveWorkspaceCompositionSession (localStorage)
  → Host (Preview/Home) liest Session
```

### Mount-Delta

| `kind` | Runtime mountet | Nicht |
|---|---|---|
| `inbox` | `InboxWidget` | keine zweite Inbox |
| `disposition_board` | registrierte `DispositionBoard` über `SpecializedComponentHost` (dieselbe Komponente wie `/disposition/touren-disposition`, dnd-kit, `posts_quantity` false) | keine zweite Tafel, kein Navigationslink, keine zweite Pipeline auf der Dispositionsseite |

| Host-Variante | Chrome | Konsum |
|---|---|---|
| `studio` (Default) | Titel + Views-Band + Slots | Studio-Preview |
| `embedded` | nur Slots (`workspace-specialist-slots`) | Home/Start — kein zweites `h1` |

Views erscheinen im Studio-Host in Composition-Reihenfolge (Metadaten-Band, keine Meridian-Pipeline).
Home nutzt dieselbe Mount-Plan-Ableitung; Kind-Filter gilt weiter für Live-Signale.

### Compose-Verhalten (Preview / Dialog)

```text
Draft (React)
  → setSpecializedKindEnabled / moveWorkspaceView / patchMeta / upsertReleased
  → resolveComposableWorkspace (Parser + Validator)
       ├─ ok  → Host remount + optional Speichern
       └─ fail → Issues anzeigen, Host nicht mounten
```

- **localStorage-Key:** `valeo.workspace.composition` (fixiert über Tab-Close; gleicher Key/JSON wie zuvor, API `readWorkspaceCompositionSession` unverändert)
- Speichern nur bei gültiger Composition (kein stilles Überschreiben mit Ungültigem)
- Katalog für Slot-Wiederherstellung: typed Fixture (kein YAML-Parser im Browser)
- Kein Server-Write, kein `studio_screen_versions.json`

**Preview-Route:** `/studio/workspace-composition-preview` (bestehend; `router.tsx` nicht anfassen).

## 5. Abgrenzung

| Nicht in diesem Slice | Begründung |
|---|---|
| Studio-Release / CLI / screen_versions | Codex STUDIO-* |
| Inbox-/Dispo-Implementierung | Inbox nur bestehendes Widget; Dispo nur Registry-Mount der bestehenden Tafel |
| Feature-Commit | Auftrag |

## 6. Geschwister-Dokumente (nur Verweis)

- `adaptive-workspace-framework.md`, `adaptive-workspace-inbox.md`, `adaptive-workspace-disposition.md`
- `adaptive-workspace-events-mcp.md`, `adaptive-workspace-erpclow-lessons.md`
- [studio-semantic-standard.md](studio-semantic-standard.md)

## 7. Tests

- `workspace-composition.test.ts` — Vertrag/Parser + YAML↔typed `screenId`-Drift
- `workspace-composition-runtime.test.ts` — Mount-Plan
- `workspace-composition-session.test.ts` — Toggle/Reorder/Session
- `workspace-composition-authoring.test.ts` — Meta/Host/Released-View Mutationen
- `workspace-composition-authoring-dialog.test.tsx` — Dialog Speichern / releasedScreen
- `workspace-composition-host.test.tsx` — Host + Preview-Compose + embedded
- `home-composition.test.tsx` — Home → denselben Host
- `tests/test_studio_workspace_composition.py` — pytest Drift-Gate Fixture↔screenIds/Kinds

## 8. Nächste Schritte (nicht dieser Slice)

1. Optional: Cockpit-Floorplan-Hosts jenseits Start/Home
2. Alias-Spiegel YAML↔TS ohne automatisches Cross-Check bleibt manuell
3. Browser-Abnahme Authoring-Dialog nach echter Studio-Freigabe (SSO)
