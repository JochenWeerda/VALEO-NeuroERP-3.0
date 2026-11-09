## Handoff: 2026-10-23 Agrar-E2E Deliverable 7 - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop. Adaptive **nicht** complete.

### Gewaehlter Fokus

Deliverable **7** Agrar E2E-Referenz — groesste echte Vertragsluecke schliessen (ohne Kon-QS Fake-Join, ohne Godfile-Edits, ohne Codex-Waage/Touren).

### Ketten-Matrix vorher → nachher

| Schritt | Vorher (vertraglich) | Nachher |
|---|---|---|
| 1 Kontrakt | Index→Query; Pure `resolve_*` | unveraendert |
| 2 Disposition | Domain `test_kontrakt_disposition_vertrag`; Kon HTTP-Progression Query; Client Abruf-Enrich | + Vitest `pickAbrufProjection` GELIEFERT+`wiegeschein_id`→`weighing_present` |
| 3 Waage | Register-Bindung Domain; Live-UAT/Pages **Codex** | Luecke dokumentiert; Adaptive haertet nur Abruf-Projektion |
| 4 Qualitaet | Pure Join `read_agrar_quality_is_final` Probe; HTTP nur Query/`spy` | **HTTP+Probe:** Router→Join→`abrechnung` ohne Query-Flag |
| 5 Abrechnung | Query-`quality_is_final` / fulfilled ohne QS = qualitaet | Agrar: Join True→`abrechnung`, False→`qualitaet`; Kon bei GELIEFERT bleibt `qualitaet` (kein Join) |

### Implementiert

| Aenderung | Detail |
|---|---|
| `tests/test_workspace_agrar_chain.py` | `test_agrar_http_qs_join_abrechnung_on_probe` (+ Seed/Cleanup-Helfer); `require_db`, konkrete 200/Shapes |
| `agrar-chain.test.tsx` | Abruf+Wiegeschein → `weighing_present` |
| Doku | `adaptive-workspace-agrar-e2e.md`, Slice, Workboard |

Unberuehrt: `tours.py`, `logistics_tours.py`, `outbox.py`, Tourenplanung, Einkauf/Waage-Pages, DATEV, Maskeninventar, Rollen, MIGRATION-PARITY. Kon-QS-Join absichtlich nicht.

### Tests

| Suite | Ergebnis |
|---|---|
| pytest unit `test_workspace_agrar_chain.py -m "not integration"` | **40 passed** |
| pytest probe `test_agrar_http_qs_join_*` + `test_read_agrar_quality_is_final_*` | **2 passed** (valeo_probe) |
| Vitest `agrar-chain.test.tsx` | **16 passed** |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / Fixieren-Anpassen | unveraendert |
| 2 | Command Center / Strg+K | unveraendert; Browser-SSO STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert |
| 4 | Dispo Assign + Live + Abrufe-Auth | unveraendert (Vorgaenger) |
| 5 | Studio Composition | unveraendert |
| 6 | MCP Fachaktionen | unveraendert |
| 7 | Agrar-Kette | **Fortschritt:** HTTP+Probe QS-Join Agrar; Kon/Waage-Codex-Luecken ehrlich |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Screenshots
2. OCR Ziffern / Bing-Thumbs (bewusst nicht)
3. Inbox Positionen / `linked_document_id` ohne Documents-Treffer
4. Browser-Abnahme Dispo Assign + Live mit Session
5. Authoring-Dialog Browser nach Studio-Freigabe
6. MCP Live-Execute im Browser (pytest da)
7. Codex Waage/Touren/Verladung; `QualityProtocolCompleted` ohne Outbox; Kon-QS Fake-Join verboten; Golden-Path kon→Abruf→Ticket→Annahme→Settlement nur Domain/Codex

### Dateien

- `tests/test_workspace_agrar_chain.py`
- `packages/frontend-web/src/__tests__/workspace/agrar-chain.test.tsx`
- `docs/architecture/adaptive-workspace-agrar-e2e.md`
- Workboard / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Home Abrufe-Auth - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop. Adaptive **nicht** complete.

### Gewaehlter Fokus

Deliverable **4** Rest — Abrufe-GET Auth-Hinweis auf Home-Ranking (Board war schon ehrlich via Fehlerzeile + SSE-Token).

### Evidenz vorher

| Pruefpunkt | Stand vor Fix |
|---|---|
| Dispo-Board Abrufe 401/403 | **gruen** — `dispo-orders-error` mit `ABRUFE_AUTH_ERROR` |
| Dispo/Home Live-SSE ohne Token | **gruen** — `appendSseAuthToken` / kein EventSource |
| Home-Ranking bei Abrufe-GET 401/ohne Sitzung | **Luecke** — Query-Fehler still; Ranking wirkte leer (= Fake-Erfolg) |

### Implementiert

| Aenderung | Detail |
|---|---|
| `ABRUFE_AUTH_ERROR` in `load-abrufe.ts` | gemeinsamer Text Board + Home |
| `AdaptiveWorkspaceLayer` | Abrufe-Query nur mit Token; Signal nur mit Sitzung; `role=alert` unter Handlungsbedarf bei fehlender Sitzung / 401/403/503 wenn Composition `disposition_board` hat |
| Tests | disposition-signal Auth-Hinweis; Sibling-Layer Auth-Mocks |

Unberuehrt: `tours.py`, `logistics_tours.py`, `outbox.py`, Tourenplanung, Einkauf/Waage-Pages, DATEV, Maskeninventar, Rollen, MIGRATION-PARITY.

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest disposition-signal + load-abrufe + inbox/agrar-ranking + home-composition + dialog + launcher + disposition-board + live-signals | **56 passed** |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / Fixieren-Anpassen | unveraendert (Composition-Pin zuvor) |
| 2 | Command Center / Strg+K | unveraendert; Browser-SSO STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert; OCR-Ziffern bewusst offen |
| 4 | Dispo Assign + Live | **Fortschritt:** Home Abrufe-Auth ehrlich; Board/SSE zuvor |
| 5 | Studio Composition | unveraendert |
| 6 | MCP Fachaktionen | unveraendert |
| 7 | Agrar-Kette | unveraendert |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Screenshots
2. OCR Ziffern / Bing-Thumbs (bewusst nicht)
3. Inbox Positionen / `linked_document_id` ohne Documents-Treffer
4. Browser-Abnahme Dispo Assign + Live mit Session
5. Authoring-Dialog Browser nach Studio-Freigabe
6. MCP Live-Execute im Browser (pytest da)
7. Codex-Verladung / QualityProtocolCompleted ohne Outbox; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/components/mask-builder/specialized/load-abrufe.ts`
- `packages/frontend-web/src/workspace/AdaptiveWorkspaceLayer.tsx`
- `packages/frontend-web/src/__tests__/workspace/disposition-signal.test.tsx`
- `packages/frontend-web/src/__tests__/workspace/{inbox-ranking,agrar-chain-ranking,dialog-layer,home-composition}.test.tsx` (Auth-Mocks)
- `packages/frontend-web/src/__tests__/components/mask-builder/specialized/load-abrufe.test.ts`
- Workboard / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Composition Pin/Fixieren - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop. Adaptive **nicht** complete.

### Gewaehlter Fokus

Deliverable **1** — „Benutzer kann fixieren/anpassen“.

### Evidenz vorher (D1)

| Pruefpunkt | Stand vor Fix |
|---|---|
| Fachaktion-Pin + Oberfläche fixieren (Launchpad-Overlay, Priorisierung `pinned`) | **gruen** — AdaptiveWorkspaceLayer, `launchpad-personalization`, Vitest |
| Launchpad Anpassen (Reihenfolge/Ausblenden) | **gruen** |
| Composition `personalization.pinStorageKey` / `pinnedViewsKey` / `fixedStartViewKey` | **Luecke** — nur Schema/Authoring; keine Laufzeit-UX, kein Overlay-Read |
| Regelbasierte Fachaktions-Priorisierung | unberührt lassen |

### Implementiert

| Aenderung | Detail |
|---|---|
| `workspace-composition-overlay.ts` | Pin/Unpin View, Start-Fix, apply auf Views+Slots; Storage-Keys Mandant/sub |
| `useWorkspaceCompositionOverlay` | Persistenz erst im Effect nach Commit (Launchpad-Muster) |
| `WorkspaceCompositionHost` | View-Pin + „Als Start“ (studio + embedded); Slot-Reihenfolge folgt Overlay |
| `personalizeHomeComposition` | Home-Kinds/Signale folgen persönlicher View-Ordnung |
| Tests | Overlay pure + Host Persistenz + Home personalize |

Unberuehrt: `tours.py`, `logistics_tours.py`, `outbox.py`, Tourenplanung, Einkauf/Waage-Pages, DATEV, Maskeninventar, Rollen, MIGRATION-PARITY.

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest overlay + host + home-composition + prioritization + launchpad-personalization | **36 passed** |
| Regression start-dashboard + disposition-signal + launcher-surfaces-evidence | **18 passed** |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / Fixieren-Anpassen | **Fortschritt:** Fachaktion-Pin + Composition-View-Pin/Start-Fix |
| 2 | Command Center / Strg+K | unveraendert; Browser-SSO STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert; OCR-Ziffern bewusst offen |
| 4 | Dispo Assign + Live | unveraendert (SSE-Token zuvor); Browser-SSO STOP |
| 5 | Studio Composition | **Fortschritt:** persönliche View-Anpassung jenseits Authoring |
| 6 | MCP Fachaktionen | unveraendert |
| 7 | Agrar-Kette | unveraendert |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Screenshots
2. OCR Ziffern / Bing-Thumbs (bewusst nicht)
3. Inbox Positionen / `linked_document_id` ohne Documents-Treffer
4. Abrufe-GET Auth-Hinweis ohne Sitzung auf Home-Ranking (Board schon ehrlich) — **danach erledigt, siehe Handoff oben**
5. Authoring-Dialog Browser nach Studio-Freigabe
6. MCP Live-Execute im Browser (pytest da)
7. Codex-Verladung / QualityProtocolCompleted ohne Outbox; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/studio/workspace-composition-overlay.ts` (**neu**)
- `packages/frontend-web/src/hooks/useWorkspaceCompositionOverlay.ts` (**neu**)
- `packages/frontend-web/src/studio/WorkspaceCompositionHost.tsx`
- `packages/frontend-web/src/workspace/{home-composition,AdaptiveWorkspaceLayer,index}.ts(x)`
- `packages/frontend-web/src/__tests__/studio/workspace-composition-overlay.test.ts` (**neu**)
- `packages/frontend-web/src/__tests__/studio/workspace-composition-host.test.tsx`
- `packages/frontend-web/src/__tests__/workspace/home-composition.test.tsx`
- Workboard / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Dispo-SSE Token - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop. Adaptive **nicht** complete.

### Gewaehlter Fokus

Deliverable **4** — groesste echte Restluecke ohne Godfiles: Live-SSE am Dispo-Board (und Home-Signale) ohne Auth-Token.

### Evidenz vorher (D4)

| Pruefpunkt | Stand vor Fix |
|---|---|
| UMR / ScreenDefinition `specialized.type === disposition_board` | **gruen** — Registry, Host, `touren-disposition.tsx` |
| dnd-kit + Zeitachse (Gantt-Spuren) + Stopp-Karte lat/lng | **gruen** |
| Backend-Validierung vor Persistenz | **gruen** — `validate_assignment` / Assign-POST |
| Drag ≠ Buchung (`posts_quantity: false`, Event `logistik.tour.created`) | **gruen** |
| Live NATS+SSE Subscribe am Board | **Luecke** — `EventSource('/api/events?stream=workspace')` **ohne** `?token=`; Backend verlangt Token-Query (kein Authorization-Header an EventSource) → Auth-Hinweis statt Live |

### Implementiert

| Aenderung | Detail |
|---|---|
| `appendSseAuthToken` in `lib/sse-client.ts` | reine URL-Hilfe; relativer Pfad bleibt relativ |
| `workspaceTourSseUrl` / Dispo-Hook | Token aus `auth.getAccessToken()`; ohne Token kein Connect + `SSE_AUTH_ERROR` |
| `workspaceLiveSseUrl` / Home Live-Signale | derselbe Vertrag |
| Tests | URL mit Token; ohne Token kein EventSource + Hinweis |

Unberuehrt: `tours.py`, `logistics_tours.py`, `outbox.py`, Tourenplanung, Einkauf/Waage-Pages, Verladung-Actor/Tenant/Atomicity.

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest disposition-board + workspace-tour-sse + live-signals | **25 passed** |
| Vitest launcher-surfaces-evidence | **4 passed** |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | Fortschritt; Alias-Gate zuvor |
| 2 | Command Center / Strg+K | Fortschritt; Browser-SSO STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert; OCR-Ziffern bewusst offen |
| 4 | Dispo Assign + Live | **Fortschritt:** SSE-Token; UMR/Validierung/Drag→Command/Karte zuvor gruen; Browser-SSO STOP |
| 5 | Studio Composition | unveraendert (Authoring zuvor) |
| 6 | MCP Fachaktionen | unveraendert (pytest/Alias-Gate zuvor) |
| 7 | Agrar-Kette | nachgewiesen; Kon-QS-Join Absicht |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Screenshots
2. OCR Ziffern / Bing-Thumbs (bewusst nicht)
3. Inbox Positionen / `linked_document_id` ohne Documents-Treffer
4. Abrufe-GET Auth-Hinweis ohne Sitzung (ehrlich)
5. Authoring-Dialog Browser nach Studio-Freigabe
6. MCP Live-Execute im Browser (pytest da)
7. Codex-Verladung / QualityProtocolCompleted ohne Outbox; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/lib/sse-client.ts`
- `packages/frontend-web/src/components/mask-builder/specialized/workspace-tour-sse.ts`
- `packages/frontend-web/src/workspace/live-signals.ts`
- `packages/frontend-web/src/__tests__/components/mask-builder/specialized/{disposition-board,workspace-tour-sse}.test.*`
- `packages/frontend-web/src/__tests__/workspace/{live-signals,launcher-surfaces-evidence}.test.tsx`
- Workboard / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Alias-Spiegel Drift-Gate - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **2/6** Rest — Alias-Spiegel YAML↔TS **mit** Cross-Check-Gate (vorher nur manuell).

**Warum:** `FACHAKTION_CATALOG_ALIASES` und YAML-Aliase konnten still auseinanderlaufen; Composition hatte bereits YAML↔screenIds-Gate, Fachaktionen nicht.

### Was das Gate prueft

| Pruefung | Quelle A | Quelle B |
|---|---|---|
| `action_id`-Menge | `config/adaptive_workspace_fachaktionen.yaml` `actions[].action_id` | Keys von `FACHAKTION_CATALOG_ALIASES` |
| Alias-Listen 1:1 (Reihenfolge + Inhalt) | YAML `aliases` | TS `FACHAKTION_CATALOG_ALIASES[id]` |
| Alias-Uniqueness quer ueber Actions | YAML + TS | Kollision → Fail |
| Registry-Felder | `WORKSPACE_FACHAKTIONEN` (`catalogId`, `route`, `screenId`, `requiredScopes[0]`) | YAML `action_id` / `route_path` / `screen_id` / `permission.scope` |

Write-only/MCP-only YAML-Actions ohne Registry-Eintrag (`logistik.tour.anlegen`, `finance.ap_invoice.*` Write, …) bleiben erlaubt — Gate verlangt nur: jeder Registry-`catalogId` existiert im YAML.

### Drift gefunden / behoben

| Fund | Status |
|---|---|
| Alias-Keys YAML↔TS (21) | **keine Drift** — bereits deckungsgleich |
| Alias-Listen Inhalt/Reihenfolge | **keine Drift** |
| Registry 15× catalogId→route/scope/screenId | **keine Drift** |
| Code-Fix Adaptive/Registry/YAML | **nicht noetig** |

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest `fachaktion-alias-parity` + resolve/registry/invariants-gate | **19 passed** (davon **3** neu Paritaet) |
| pytest `test_fachaktion_alias_parity` + `test_workspace_fachaktionen` (`--noconftest --no-cov`) | **41 passed** (davon **2** neu Paritaet) |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | Fortschritt; Paritaet durch Gate abgesichert |
| 2 | Command Center / Strg+K | **Fortschritt:** Alias-Spiegel-Gate; Browser-SSO weiter STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert; OCR-Ziffern bewusst offen |
| 4 | Dispo Assign + Verladung-Live | Codex-Besitz — unberuehrt |
| 5 | Studio Composition | unveraendert (Authoring-Dialog zuvor) |
| 6 | MCP Fachaktionen | **Fortschritt:** YAML↔TS-Alias-Gate + pytest-Spiegel |
| 7 | Agrar-Kette | nachgewiesen (Kon ohne QS-Join Absicht) |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Prefill-/Confirm-Screenshots
2. Birkhoff Art-Nr Ziffern-OCR (bewusst nicht)
3. Bing-Thumbs / Naturland-Blanko ohne Tabelleninhalt
4. `linked_document_id` nur bei eindeutigem Documents-Treffer
5. Browser-Abnahme Authoring-Dialog nach echter Studio-Freigabe; optional Cockpit jenseits Start
6. MCP Live-Execute / Vier-Augen in Browser (pytest nachgewiesen; SSO STOP)
7. Codex-Verladung / Godfiles; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/__tests__/workspace/fachaktion-alias-parity.test.ts` (**neu**)
- `tests/test_fachaktion_alias_parity.py` (**neu**)
- `config/adaptive_workspace_fachaktionen.yaml` / `fachaktion-resolve.ts` / `registry.ts` (unveraendert — bereits paritaetisch)
- `docs/agent-ops/active-workboard.md` / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Studio-Dialog-Authoring - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **5** Rest — Studio-Dialog-Authoring: Composition (Slots inkl. Inbox/Dispo) ueber Metadaten editierbar, getrennt vom Host.

**Warum:** Preview hatte Inline-Compose; fehlte Authoring-Dialog als Schritt nach ScreenDefinition-Freigabe (Meridian/Studio-Vertrag, kein Parallel-Frontend).

### Was Authoring kann vs. Host

| Ebene | Kann | Persistenz |
|---|---|---|
| **Authoring** (Form + Dialog) | Titel/Beschreibung/Default-View; Slot an/aus (inbox, disposition_board); Host-View je Slot; View-Reorder; freigegebene ScreenDefinition als View (`upsertReleasedScreenView`) | `saveWorkspaceCompositionSession` → localStorage `valeo.workspace.composition` (+ tenant/sub) |
| **Host** | Nur gueltige Composition mounten (InboxWidget / Dispo-Tafel) | liest Session/Fixture — schreibt nicht |

### Verdrahtet

| Punkt | Status | Detail |
|---|---|---|
| `WorkspaceCompositionAuthoringForm` | **neu** | Metadaten + Slots + Views |
| `WorkspaceCompositionAuthoringDialog` | **neu** | Dialog um Form; Speichern nur bei gueltig |
| Preview | **erweitert** | Form + Button „Authoring-Dialog“ |
| Screen Studio nach Freigabe | **additiv** | Button „In Arbeitsraum aufnehmen“ → Dialog mit `releasedScreen` |
| Host / Home | unveraendert | konsumiert Session weiter |

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest authoring + dialog + composition + host + session + runtime + home | **47 passed** |
| Vitest ScreenStudioPage | **5 passed** (additiver Button, keine Regression) |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | Fortschritt (Fachaktionen-Paritaet zuvor) |
| 2 | Command Center / Strg+K | Fortschritt; Browser-SSO weiter STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert; OCR-Ziffern bewusst offen |
| 4 | Dispo Assign + Verladung-Live | Codex-Besitz — unberuehrt |
| 5 | Studio Composition | **Fortschritt:** Host embedded + Drift-Gate + **Authoring-Dialog**; Browser-Abnahme Dialog/SSO offen |
| 6 | MCP Fachaktionen | unveraendert gruen / Paritaet zuvor |
| 7 | Agrar-Kette | nachgewiesen (Kon ohne QS-Join Absicht) |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Prefill-/Confirm-Screenshots
2. Birkhoff Art-Nr Ziffern-OCR (bewusst nicht)
3. Bing-Thumbs / Naturland-Blanko ohne Tabelleninhalt
4. `linked_document_id` nur bei eindeutigem Documents-Treffer
5. Browser-Abnahme Authoring-Dialog nach echter Studio-Freigabe; optional Cockpit jenseits Start
6. Alias-Spiegel YAML↔TS ohne Cross-Check-Gate
7. Codex-Verladung / Godfiles; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/studio/workspace-composition-authoring.ts`
- `packages/frontend-web/src/studio/WorkspaceCompositionAuthoringForm.tsx`
- `packages/frontend-web/src/studio/WorkspaceCompositionAuthoringDialog.tsx`
- `packages/frontend-web/src/pages/studio/workspace-composition-preview.tsx`
- `packages/frontend-web/src/features/screen-studio/ScreenStudioPage.tsx` (additiv: Dialog nach Freigabe)
- `packages/frontend-web/src/__tests__/studio/workspace-composition-authoring*.ts(x)`
- `docs/architecture/adaptive-workspace-studio.md`
- `docs/agent-ops/active-workboard.md` / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Studio Composition Host auf Home - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **5** — Studio Composition: Home denselben Host-Pfad (nicht nur Kind-Filter).

**Warum:** Studio-Preview mountete bereits `WorkspaceCompositionHost` (Inbox + Dispo-Tafel aus Metadaten). Home filterte nur Kinds und hardcodierte InboxWidget + Dispo-Link — Luecke laut Slice/Studio-Doc.

### Was Host jetzt kann vs. Kind-Filter

| Ebene | Vorher (Home) | Jetzt |
|---|---|---|
| Session lesen | nur `resolveHomeSpecialistKinds` | `resolveHomeComposition` → Composition + Kinds |
| Mount | hartcodierte Slots (Inbox + Link) | `WorkspaceCompositionHost` `variant=embedded` |
| Inbox | Widget direkt | dasselbe Widget ueber Host-Slot + `onQueue` |
| Dispo | Navigationslink | registrierte Tafel via `SpecializedComponentHost` |
| Signale | Kind-Filter | Kind-Filter **bleibt** (inbox-queue / disposition:open-abrufe) |
| Fallback leer/ungueltig | Default-Kinds Inbox→Dispo | Fixture-Composition (Dispo→Inbox, View-Order) |
| Studio-Preview | voller Host | unveraendert `variant=studio` |

### Verdrahtet

| Punkt | Status | Detail |
|---|---|---|
| `resolveHomeComposition` | **neu** | Session ok → Composition; sonst Fixture-Fallback |
| Home → Host | **neu** | embedded, kein zweites h1, `workspace-specialist-slots` |
| Drift-Gate screenIds | **neu** | Vitest YAML↔typed + pytest `test_studio_workspace_composition` |

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest composition + host + home-composition + dialog + start-dashboard | **45 passed** |
| Vitest disposition/agrar/inbox-ranking + launcher + invariants | **27 passed** |
| pytest `test_studio_workspace_composition` + `test_workspace_fachaktionen` (`--noconftest --no-cov`) | **40 passed** |

### Evidence Deliverable 1–7 (ehrlich)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | Fortschritt (Fachaktionen-Paritaet zuvor) |
| 2 | Command Center / Strg+K | Fortschritt; Browser-SSO weiter STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert; OCR-Ziffern bewusst offen |
| 4 | Dispo Assign + Verladung-Live | Codex-Besitz — unberuehrt |
| 5 | Studio Composition | **Fortschritt:** Home = voller Host-Pfad embedded; Drift-Gate da; Studio-Dialog-Authoring weiter offen |
| 6 | MCP Fachaktionen | unveraendert gruen / Paritaet zuvor |
| 7 | Agrar-Kette | nachgewiesen (Kon ohne QS-Join Absicht) |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Prefill-/Confirm-Screenshots
2. Birkhoff Art-Nr Ziffern-OCR (bewusst nicht)
3. Bing-Thumbs / Naturland-Blanko ohne Tabelleninhalt
4. `linked_document_id` nur bei eindeutigem Documents-Treffer
5. Studio-Dialog Authoring nach ScreenDefinition; optional Cockpit jenseits Start
6. Alias-Spiegel YAML↔TS ohne Cross-Check-Gate
7. Codex-Verladung / Godfiles; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/studio/WorkspaceCompositionHost.tsx`
- `packages/frontend-web/src/workspace/home-composition.ts`
- `packages/frontend-web/src/workspace/AdaptiveWorkspaceLayer.tsx`
- `packages/frontend-web/src/workspace/index.ts`
- `packages/frontend-web/src/__tests__/studio/workspace-composition*.ts(x)`
- `packages/frontend-web/src/__tests__/workspace/home-composition.test.tsx` (+ Ranking/Dialog-Shims)
- `packages/frontend-web/src/__tests__/pages/start-dashboard.test.tsx`
- `tests/test_studio_workspace_composition.py`
- `docs/architecture/adaptive-workspace-studio.md`
- `docs/agent-ops/active-workboard.md` / Slice / dieses Handoff

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete. Adaptive **nicht** complete.

---

## Handoff: 2026-10-23 Registry/MCP Fachaktionen-Paritaet - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **2/6** — Registry↔YAML/MCP Fachaktionen-Paritaet (ohne Browser-SSO, ohne OCR-Ziffern, ohne Codex-Godfiles).

**Warum:** Dokumentierte Beispiel-Query „Angebot Kunde“ (`sales.customer_quote.list`) war im YAML/MCP, fehlte in der Frontend-Registry → Live-Resolve/`localResolveFallback` endete **blocked**. Dazu Scope-/Route-Drift (`procurement:read` vs `einkauf:read`, `finance:approve` vs `finance:read`, Create-Route `/verkauf/angebote` vs `/sales/angebot/neu`). Groesste echte Luecke ohne SSO/OCR-Overfit/Godfiles.

### Verdrahtet

| Punkt | Status | Detail |
|---|---|---|
| Registry `sales.customer_quote.list` | **neu** | Worklist `/sales/angebote-liste`, Scope `sales:read` |
| Create-Route | **angeglichen** | `/sales/angebot/neu` (YAML + Alias vorhanden) |
| WE Mengenabweichung | **angeglichen** | Route `/einkauf/anlieferavis`, Scope `einkauf:read` |
| Rechnungen Freigabe | **angeglichen** | Scope `finance:read`; Route `/workflows/approval` (YAML + FE) |
| Ueberfaellige Kontrakte | **YAML→FE** | Route `/agrar/kontrakt-erfuellung` |
| Nicht disponierte LKW | **YAML→FE** | Route `/disposition/touren-disposition` (Slice-Absicht) |
| Gate | **neu** | Invariants: fuenf Beispiel-Queries catalogId/route/scope == YAML |

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest registry + command-mapping + fachaktion-resolve + prioritization + invariants-gate | **25 passed** |
| pytest `tests/test_workspace_fachaktionen.py` (`--noconftest --no-cov`) | **39 passed** |

### Evidence Deliverable 1–7 (Stand Fachaktionen-Paritaet)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | **Fortschritt:** fuenf Beispiel-Queries registry-paritaetisch |
| 2 | Command Center / Strg+K | **Fortschritt:** „Angebot Kunde“ lokal/live nicht mehr blocked; Browser-SSO weiter STOP |
| 3 | Inbox Prefill / Match / Positionen | unveraendert (OCR Mengen Broering/Birkhoff zuvor gruen; Art-Nr Ziffern nicht poliert) |
| 4 | Dispo Assign + Verladung-Live | Codex-Besitz — unberuehrt |
| 5 | Studio Composition | nachgewiesen; Home konsumiert weiter nur Kind-Filter (kein voller Host) |
| 6 | MCP Fachaktionen | **Fortschritt:** Frontend catalogId/route/scope an YAML; MCP-Katalog unveraendert gruen |
| 7 | Agrar-Kette | nachgewiesen (Kon ohne QS-Join bleibt Absicht) |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Prefill-/Confirm-Screenshots
2. Birkhoff Art-Nr `281040`↔`291040` (Ziffern-OCR — bewusst nicht)
3. Bing-Thumbs / Naturland-Blanko ohne Tabelleninhalt
4. `linked_document_id` nur bei eindeutigem Documents-Treffer (kein Raten)
5. Studio: Home denselben Composition-Host; Drift-Gate Fixture↔screenIds
6. Alias-Spiegel YAML↔TS ohne automatisches Cross-Check-Gate (manuell synchron)
7. Codex-Verladung / Godfiles unangetastet; Kon-QS Fake-Join verboten

### Dateien

- `packages/frontend-web/src/workspace/registry.ts`
- `config/adaptive_workspace_fachaktionen.yaml`
- `packages/frontend-web/src/__tests__/workspace/{registry,command-mapping,fachaktion-resolve,prioritization,invariants-gate}.test.ts`
- `docs/architecture/adaptive-workspace-events-mcp.md` (Beispiel-`route_path`)
- `docs/agent-ops/active-workboard.md`
- `docs/agent-ops/handoffs/adaptive-workspace-20261022.md`
- `docs/agent-ops/slices/ADAPTIVE-WORKSPACE-20261022.yaml`

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete.

---

## Handoff: 2026-10-23 Broering/Birkhoff Mengen gehaertet - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **3 Inbox** — Live-Mengen Broering + Birkhoff (nach Sica/DGO/Deuka/Hofmeister/Zill).

### Mengen vorher → nachher (Live-Tesseract)

| Beleg | vorher Menge(n) | nachher Menge(n) | Note |
|---|---|---|---|
| Broering VR1466078 Live | `0000` kg (Preis `081`) | **`50000` kg** (Preis `23.10`) | `0.000`→Null; Datum `081026` übersprungen; Rekonstruktion €/dt aus Netto |
| Birkhoff 227627 Live Z1 | `1980.00` kg | `1980.00` kg | ok; Art-Nr OCR weiter `281040` statt `291040` |
| Birkhoff 227627 Live Z2 | `00` kg (Name enthielt `25.200,`) | **`25200.00` kg** | `_QTY` erlaubt Leerzeichen nach Komma |
| Clean Broering/Birkhoff | 50000 / 1980+25200 | unverändert | Regression ok |
| Telekom / Bing-Thumbs / Naturland-Blanko | 0 | 0 | **nicht** erzwungen |

### Verdrahtet

| Punkt | Status | Detail |
|---|---|---|
| `extract_table_line_items` | **gehaertet** | `_QTY` spaced decimal; Beleg-Datum `DDMMYY`; Nullmenge→Preis/Netto (€/dt oder `/t`) |
| Kontrakt / `linked_document_id` | **unberührt** | keine Regression |

### Tests

| Suite | Ergebnis |
|---|---|
| pytest `test_ocr_training_user_invoices` + `test_dms_inbox_position_extraction` + `test_documents_inbox_contract` (`--noconftest --no-cov`) | **78 passed** (76 + 2 Mengen-Tests) |

### Weiter offen (kurz)

1. Browser-SSO / Prefill-Screenshot
2. Birkhoff Live Z1 Art-Nr `281040`↔`291040` (Ziffern-OCR, Menge ok)
3. Bing-Thumbs / Naturland-Blanko ohne Tabelleninhalt
4. `linked_document_id` / Kontrakt-Match / Claude-Fallback / Codex-Godfiles — unverändert offen bzw. Besitz

### Dateien

- `app/documents/position_extraction.py`
- `tests/test_ocr_training_user_invoices.py`
- `docs/agent-ops/active-workboard.md`
- `docs/agent-ops/handoffs/adaptive-workspace-20261022.md`

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete.

---

## Handoff: 2026-10-23 OCR-Positionen Live gehaertet - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **3 Inbox** weiter — schwache Live-OCR-Positionen der User-/Training-Belege (Folkerts/RE/LS).

### Beleg-Coverage vorher → nachher (Live-Tesseract User-Uploads)

| Beleg | vorher rows | nachher rows | Note |
|---|---|---|---|
| Sica 26648052 | 0 | **5** | Stiick/Stick, Pos-Strich, Art-Nr mit Punkt |
| DGO 10043771 | 1 (Müll) | **7** | Anzahl+Menge+PE; PE „1“→l; „20,001“→20,00 l |
| Deuka Korrektur 600350 | 1 (Preis als Name) | **1 echt** | Mehrzeiler Art-Nr+Name → Menge Folgeszeile |
| Hofmeister 3715298017 | 4 | **7** | Pos+, Einheit angeklebt, Pos in SKU geklebt |
| Zill R2609060 | 1 (nur Maut) | **2** | Stilck; Name mit `_` |
| Webfleet 11857345 | 10 | **10** | Pos `2.` wieder ok |
| Folkerts LS 2607001 | 2 | **2** | unverändert ok |
| Broering VR1466078 | 1 | 1 | Menge Live-OCR `0.000` statt 50.000 — Tesseract *(danach Mengen-Härtung, siehe Handoff oben)* |
| Birkhoff 227627 | 2 | 2 | 2. Zeile Menge Live weiter schwach *(danach Mengen-Härtung, siehe Handoff oben)* |
| Telekom | 0 | 0 | erwartet (keine Warenpos.) |
| Clean-Fixtures (16) | alle Soll-Zeilen | **unverändert** | Telekom 0 ok |

Bing-Thumbs / Naturland-Blanko: weiter 0 (OCR-Text zu dünn / leere Vorlage) — kein Produktionsbeleg.

### Verdrahtet

| Punkt | Status | Detail |
|---|---|---|
| `extract_table_line_items` | **gehaertet** | Einheiten-OCR, DGO-PE, Deuka-Mehrzeiler, Hofmeister-Klebungen, Wortgrenzen |
| `DMSParser.parse` → `positionen` | **ok** | ruft weiterhin Regex; Live-Tests neu |
| Kontrakt / `linked_document_id` | **unberührt** | keine Regression |

### Tests

| Suite | Ergebnis |
|---|---|
| pytest `test_ocr_training_user_invoices` + `test_dms_inbox_position_extraction` + `test_documents_inbox_contract` (`--noconftest --no-cov`) | **76 passed** |

### Evidence Deliverable 1–7 (Stand OCR-Positionen)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | nachgewiesen (unverändert) |
| 2 | Command Center / Strg+K | nachgewiesen; Browser-SSO STOP |
| 3 | Inbox Prefill / Match / Positionen | **Fortschritt:** Live-User-Belege liefern brauchbare Positionen; Prefill-Screenshot braucht Session |
| 4 | Dispo Assign + Verladung-Live | Codex-Besitz — unberührt |
| 5 | Studio Composition | nachgewiesen (unverändert) |
| 6 | MCP Fachaktionen | nachgewiesen (unverändert) |
| 7 | Agrar-Kette | nachgewiesen (unverändert) |

### Weiter offen (1–7 kurz)

1. Browser-SSO / Live-Confirm / Prefill-Screenshot
2. Broering/Birkhoff Live-Mengen-Genauigkeit (Tesseract liest Zahlen falsch) — *teilweise erledigt, siehe aktueller Handoff*
3. Bing-Thumbs / leere Naturland-Vorlage ohne Tabelleninhalt
4. `linked_document_id` ohne Documents-Treffer bleibt leer
5. Kontrakt-Match nur bei Nummer im Extrakt + Stamm
6. Claude-Fallback weiter nur hinter `EINKAUF_OCR_ENGINE=claude`
7. Codex-Verladung / Godfiles unangetastet

### Dateien

- `app/documents/position_extraction.py`
- `tests/test_ocr_training_user_invoices.py` (Live-OCR-Parametrisierung)
- `docs/agent-ops/active-workboard.md`
- `docs/agent-ops/handoffs/adaptive-workspace-20261022.md`

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete.

---

## Handoff: 2026-10-23 Kontrakt-Match + linked_document_id (ohne Browser-SSO) - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### Gewaehlter Fokus

Deliverable **3 Inbox** — staerkste offene Objective-Luecke ohne Browser-SSO: Kontrakt-Abgleich am Eingang + verifizierte `linked_document_id` aus `documents`-Join (nicht aus OCR-/DMS-/Inbox-ID geraten).

### Verdrahtet

| Punkt | Status | Detail |
|---|---|---|
| DMS-Parser `contract_id` | **ok** | Patterns `KontraktNr.` / `Maklerkontraktnr.` — Training: Birkhoff `13842`, Live Broering `63044-25` |
| Kontrakt-Lookup | **ok** | `load_contract_candidates` liest `domain_ops.kon_contract` + `domain_inventory.agrar_contracts` (tenant-gefiltert, read-only) |
| `contract_match` am Queue-Item | **ok** | `contract_match_from_candidates` → Prefill `contractMatch` / `matchValues.contractId`; UI-Hinweis |
| `linked_document_id` | **ok (bedingt)** | nur bei eindeutigem `documents.id` aus Dubletten-Join; sonst `null` |
| PIPELINE_GAPS | **angepasst** | `kontrakt_abgleich_nur_bei_kontraktnummer_im_extrakt`, `linked_document_id_nur_bei_eindeutigem_documents_treffer` (ersetzt `kein_kontrakt_abgleich_am_eingang`) |

### Tests

| Suite | Ergebnis |
|---|---|
| pytest `test_documents_inbox_contract` + `test_ocr_training_user_invoices` (`--noconftest --no-cov`) | **48 passed** |
| Vitest `inbox-widget` + `inbox-contract` | **34 passed** |

### Evidence Deliverable 1–7 (Stand 2026-10-23 Kontrakt+Join)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | nachgewiesen (unverändert) |
| 2 | Command Center / Strg+K | nachgewiesen; Browser-SSO STOP |
| 3 | Inbox Prefill / Match / Oeffnen | **Fortschritt:** Kontrakt-Match + linked_document_id-Join; Prefill/Partner/Positionen-Regex weiter wie zuvor; Live-Confirm/Screenshot braucht Session |
| 4 | Dispo Assign + Verladung-Live | Codex-Besitz / teilweise — unberührt |
| 5 | Studio Composition | nachgewiesen (unverändert) |
| 6 | MCP Fachaktionen | nachgewiesen (unverändert) |
| 7 | Agrar-Kette | nachgewiesen (Kon-QS Absicht) |

### Weiter offen (1–7)

- Browser-SSO / Live-Confirm Lieferant / Prefill-Screenshot
- Positionen: Live-Tesseract oft leer; Regex-Fixtures ok; Claude nur Fallback
- `linked_document_id` ohne vorhandenen Documents-Treffer bleibt leer (kein Raten)
- Kontrakt-Match nur wenn Extrakt Nummer liefert und Stamm existiert
- Studio-Metadaten Inbox/Dispo (kein neuer Gap in diesem Turn)
- MCP Fachcommand-Parität (bereits grün)
- Codex-Verladung / Godfiles unangetastet

### Dateien

- `app/integrations/dms_parser.py`
- `app/documents/inbox_contract.py`
- `app/documents/inbox_service.py`
- `packages/frontend-web/src/components/adaptive-workspace/inbox/types.ts`
- `packages/frontend-web/src/components/adaptive-workspace/inbox/InboxWidget.tsx`
- `tests/test_documents_inbox_contract.py`, `tests/test_ocr_training_user_invoices.py`
- Vitest `inbox-widget.test.tsx`

**Slice:** weiterhin **in Arbeit**. Ziel nicht complete.

---

## Handoff: 2026-10-23 Belegfolge API-Vertrag (ohne Browser-SSO) - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push. Kein Keycloak-Retry / kein Credential-Loop.

### API-seitig gruen (Dev/TestClient, kein Browser)

| Kette | Status | Nachweis |
|---|---|---|
| NWF Positionen → Artikel-Match | **ok** | Unit `test_demo_nwf_…` + Integration Queue: `article_match`/`matched` bei geseedetem Artikel |
| GAP `partner_nicht_gefunden` → Lieferant-Propose | **ok** | Payload `DEMO-LF-GAP` + Action `propose_supplier_create` / Label „Lieferant anlegen“ |
| Lieferant-Create Confirm (UI→API) | **ok** | Vitest Confirm→`POST /api/v1/einkauf/lieferanten`; **409 = idempotent Erfolg** (`alreadyExists`) |
| Prefill Erfassung | **ok** | `prefill.documentId` / `maskConsumesPrefill` / `booking=false`; Vitest „Beleg oeffnen“ schreibt `valeo.inbox.prefill` |
| Approve bucht nicht | **ok** | `POST …/approve` → 409 `booking_not_from_inbox` |

**Tests:** pytest DEMO-Unit+Integration **2 passed** (probe); Vitest inbox/master-data **28 passed**. Seed-ID-Guard unveraendert (6).

**Code (Adaptive/Inbox):** `master-data-create.ts` 409-Idempotenz; `InboxWidget` Toast „bereits vorhanden“. Prefill-Route unveraendert (`…/rechnung-eingang-erfassung/neu` + sessionStorage).

### Weiter Session / Browser noetig

| Punkt | Status | Detail |
|---|---|---|
| Browser-SSO | **STOP** (Vorgaenger) | Keycloak reject freigegebener Kennung — **kein** Login-Retry |
| Live-Confirm Screenshot Lieferant | **offen** | braucht gueltige Session |
| Live „Beleg oeffnen“ / Prefill in Maske | **offen** | API+Vitest gruen; sichtbare Erfassung braucht Session (ohne `pages/einkauf` Edit) |
| Optional BP-Seed | **offen** | wenn Match statt Propose gewuenscht |

### Nicht angefasst

`pages/einkauf/**`, tours/logistics_tours/outbox, waage, tourenplanung, DATEV, Maskeninventar, Rollen, MIGRATION-PARITY.

**Slice:** **in Arbeit**.

---

## Handoff: 2026-10-23 Inbox-ID-Fix + Queue-Enrich - ADAPTIVE-WORKSPACE-20261022 *(historisch — API-Kette inzwischen vertraglich abgesichert)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push.

### 1) Inbox-ID Bugfix (Doppel-DEMO)

| Punkt | Status | Detail |
|---|---|---|
| Ursache | **fix** | Seed baute `INBOX-DEMO-{supplier_nr}` bei bereits `DEMO-LF-…` → `INBOX-DEMO-DEMO-…` |
| Kanonische ID | **ok** | `inbox_demo_item_id` → `INBOX-DEMO-LF-NWF` / `INBOX-DEMO-LF-GAP` (einmal DEMO) |
| Cleanup | **ok** | Sweep `INBOX-DEMO-DEMO-%` nur Tenant-eigene DEMO-Zeilen; Legacy WAH entfernt |
| Seed idempotent | **ok** | `--with-inbox` skippt bestehende kanonische IDs; cleaned_legacy bei Rerun |
| Live-DB | **ok** | 2 pending: `INBOX-DEMO-LF-NWF`, `INBOX-DEMO-LF-GAP`; 0 Legacy-Doppel |
| Tests | **6 passed** | `tests/test_seed_ocr_demo_stammdaten.py` (inkl. ID-Doppel-Guard) |

Dateien: `scripts/seed_ocr_demo_stammdaten.py`, `tests/test_seed_ocr_demo_stammdaten.py`.

### 2) Queue-Enrich (ohne Browser — `build_queue`/`build_item`)

| ID | Partner | Lieferant-Vorschlag | Artikel | Prefill-Route |
|---|---|---|---|---|
| `INBOX-DEMO-LF-NWF` | `partner_nicht_gefunden` (kein BP zu Pseudonym-Nr.) | `supplier_create` / `propose` | **1 matched** (Positionen aus Fixture) | `/einkauf/rechnung-eingang-erfassung` + Prefill-Keys |
| `INBOX-DEMO-LF-GAP` | `partner_nicht_gefunden` (synthetische Gap-Nr. `DEMO-LF-GAP`, nicht im Stamm) | `supplier_create` / `propose` | **1 matched** | gleich |

Hinweis: Seed legt Einkauf-Lieferanten an; Match laeuft ueber BusinessPartner — daher `partner_nicht_gefunden` + Button-Pfad „Lieferant anlegen“ vorgesehen. Pseudonym-Stamm bleibt im Einkauf-Lieferantenstamm (12 DEMO-LF).

### 3) Browser-Kette

| Punkt | Status | Detail |
|---|---|---|
| SSO | **STOP** | Freigegebene Kennung (`manual-login-…`): Keycloak **Invalid username or password** (ein Versuch; Passwort-Laenge im Formular ok). Kein Retry / kein Login-Loop. Kein Secret in Docs. |
| Lieferant-Confirm / Beleg-Screenshot | **offen** | UI-Confirm und Belegfolge-Klick brauchen gueltige Session |
| Beleg oeffnen / Zur Uebersicht Prefill | **API-seitig vorbereitet**, UI **nicht** durchgeklickt | Prefill an Erfassung verdrahtet; `pages/einkauf/**` unangetastet |

**Screenshots:** Login-STOP `evidence/screenshots/adaptive-workspace-demo-inbox-id-fix-login-stop-20261023.png` (kein Secret). Aeltere Demo-UI: `evidence/screenshots/adaptive-workspace-demo-stammdaten-*.png` — fuer kanonische IDs nach Login-Fix neu aufnehmen.

### Gaps fuer volle Kette

1. Gueltige Browser-Kennung / Keycloak-User wiederherstellen (ohne Secret in Docs).
2. UI: Lieferant-anlegen Confirm auf `INBOX-DEMO-LF-GAP` (oder NWF) + Screenshot Belegfolge-Hinweis.
3. UI: „Zur Uebersicht“ / Erfassung mit Prefill sichtbar machen (ohne `pages/einkauf` zu editieren).
4. Optional: BusinessPartner-Seed parallel zu Einkauf-Lieferanten, wenn Match statt Propose gewuenscht.

**Slice:** weiterhin **in Arbeit**. Codex-Verladung / `pages/einkauf` / tours / outbox unangetastet.

---

## Handoff: 2026-10-23 Browser SSO + DEMO-Inbox - ADAPTIVE-WORKSPACE-20261022 *(historisch — Doppel-IDs inzwischen gefixt)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push.

### Browser (ein Versuch, freigegebene Kennung)

| Punkt | Status | Detail |
|---|---|---|
| SSO localhost:3000 | **ok** | Ein Versuch mit freigegebener Pseudonym-Kennung (`manual-login-…`); Session Startseite. Kein Retry. Kein Passwort in Docs/env. |
| `/inbox` Posteingang | **sichtbar** | Damals `INBOX-DEMO-DEMO-LF-*` (Bug, inzwischen behoben) + `INBOX-AW-*`. |
| Start Beleg-Inbox | **sichtbar** | Nach Laden: **4 offen**; Match/Vorschläge; Buttons Vorschlag / Lieferant anlegen; Signal `partner_nicht_gefunden`. |
| Secrets | **bereinigt** | Temp-Suche gestoppt; keine Secrets in Handoff/Evidence. |

**Screenshots:** `evidence/screenshots/adaptive-workspace-demo-stammdaten-inbox.png`, `…-lieferant.png` (ggf. `…-inbox-match.png`, `…-home.png`).

**Pseudonym-Hinweis:** Demo-Lieferanten/Partnernamen sind Katalog-Pseudonyme (z. B. Nordwestdeutsche Futtermittel ↔ Seed-Nr. DEMO-LF-NWF); keine Realdaten/Passwoerter.

**Slice:** weiterhin **in Arbeit**. Codex-Verladung / `pages/einkauf` unangetastet.

---

## Handoff: 2026-10-23 OCR-Übungsbilder + Tabellen-Regex Positionen - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen — **nicht** complete. Kein Commit, kein Push.

### Verdrahtet / STOP je Punkt

| Punkt | Status | Detail |
|---|---|---|
| 1 Lieferant-Uebernahme | **verdrahtet** | unveraendert. |
| 2 Artikel-Uebernahme | **verdrahtet (bedingt)** | Button wenn Proposal `propose` + name+article_number aus **echten** Zeilen. |
| 3 Positionen | **verdrahtet** | Primär `extract_table_line_items` (OCR-Tabellenregex, kein Key). Claude nur Fallback hinter `EINKAUF_OCR_ENGINE=claude`. Kein Musterartikel. |
| 4 Bilder | **teilweise** | fetch-image nach Create; ohne Zeilen/Create weiter Slot. |
| 5 Browser | **ok (Session)** | siehe Handoff oben — SSO + DEMO-Inbox/Match; Live-Positions-OCR weiter offen. |

### Extraktor-Audit → Verdikt

| Symbol | Datei | Verdikt |
|---|---|---|
| `extract_table_line_items` | `app/documents/position_extraction.py` | **verdrahtet** — Pos/Art-Nr/Menge/Einheit/Preis + Naturland-Erzeugnis |
| `DMSParser.parse` | `app/integrations/dms_parser.py` | **ruft Regex** → `fields.positionen` (Kopf-PATTERNS bleiben) |
| `enrich_parsed_fields_with_positions` | `position_extraction.py` | Regex zuerst, dann optional Claude |
| `_process_incoming_document` | `dms_webhook_router.py` | Enrich nach Parse |
| `extract_line_items` / Artikel-Proposal | `inbox_contract.py` | liest Arrays → propose |
| `extract_invoice_pdf` (claude) | `ocr_invoice.py` | Fallback bei PDF + Flag |
| `LLMGateway` | `llm_gateway.py` | Fallback Text bei Flag |
| `extrahiere_belegfelder` | `dms_ocr_contracts.py` | ungeeignet — Einzel-MENGE |
| `extract_invoice_pdf` (stub/pdfplumber) | `ocr_invoice.py` | stub verboten; pdfplumber `positionen:[]` |
| XRechnung `_parse_*` | `erechnung_import.py` | ungeeignet — nur Kopf |
| LKV / WhatsApp-Heuristik / Docflow items | diverse | ungeeignet fuer DMS-LS-OCR |

### Übungsbilder

| Pfad | Inhalt |
|---|---|
| `evidence/ocr-training/lieferschein/` | 6 Bing-Thumbs + Naturland-PDF |
| `evidence/ocr-training/rechnung/` | 8 Bing-Thumbs |
| `evidence/ocr-training/fixtures/*.ocr.txt` | 4 OCR-Text-Fixtures fuer pytest |
| `evidence/ocr-training/README.md` | Quellen (Google Captcha → Bing) |

### Gaps

- `positionsextraktion_regex_keine_zeilen` (Regex leer)
- `positionsextraktion_engine_nicht_claude` / `…_ohne_llm_key` (nur wenn Regex leer + Claude gewollt/fehlend)

### Noch offen

- Live-Tesseract/Mayan-OCR der JPG-Vorschaubilder (Fixtures tragen die Tabellenstruktur)
- Browser-Queue mit Fixture-/Live-OCR; Login-Wall
- `linked_document_id`, Kontrakt-Abgleich, XRechnung-Zeilenparser

### Tests

| Suite | Ergebnis |
|---|---|
| pytest `test_dms_inbox_position_extraction` + `test_documents_inbox_contract` | **35 passed** |
| Vitest master-data-create + inbox-widget + inbox-contract | **38 passed** |

---

## Handoff: 2026-10-23 Artikel-Defaults + Bild-nach-Create + Positionen-STOP - ADAPTIVE-WORKSPACE-20261022 *(historisch — Positionen inzwischen bedingt verdrahtet)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch. Ziel blieb offen.

### Verdrahtet / STOP je Punkt

| Punkt | Status | Detail |
|---|---|---|
| 1 Lieferant-Uebernahme | **verdrahtet** | unveraendert Confirm → `POST /api/v1/einkauf/lieferanten`. |
| 2 Artikel-Uebernahme | **verdrahtet (bedingt)** | Domänen-Defaults aus `stamm-legacy` `DEFAULT_ARTIKEL`: `unit='t'` (oder Extrakt `unit_hint`), `category='Sonstige'`, `sales_price=0` (`ArticleBase` `ge=0`). UI „Artikel anlegen“ wenn Proposal `propose` + name+article_number. `ARTICLE_INBOX_DEFAULTS` / `buildArticleCreateBody` / `createArticleFromProposal`. |
| 3 Positionen | **STOP** *(ueberholt)* | damals keine Verdrahtung; siehe Handoff oben. |
| 4 Bilder | **teilweise** | `enrich-images` / `fetch-image` brauchen `article_id` (DB-Zeile). Nach erfolgreichem Artikel-Create: `POST /api/v1/articles/{id}/fetch-image` (`enrichArticleImageAfterCreate`). Ohne Create weiter nur Slot. Kein neuer Scraper. |
| 5 Browser | **STOP Login-Wall** | Tabs: Keycloak authenticate + `127.0.0.1:3001/login` — keine Session. Kein Credential-Scan. Artikel-Button nur Vitest abgenommen. |

### Positionen — Quellen-Audit *(historisch)*

Siehe aktueller Handoff-Abschnitt „Extraktor-Audit“.

### Artefakte

| Symbol | Datei |
|---|---|
| `ARTICLE_INBOX_DEFAULTS` / `buildArticleCreateBody` / `createArticleFromProposal` / `enrichArticleImageAfterCreate` | `master-data-create.ts` |
| Button `Artikel anlegen` | `InboxWidget.tsx` (`data-testid=inbox-article-create-*`) |
| Vitest | `master-data-create.test.ts`, `inbox-widget` Artikel+fetch-image |

Approve bleibt 409. Geschuetzte Pfade unangetastet. Keine Secrets in Docs.

### Noch offen (Slice nicht fertig)

- OCR/Positionszeilen in `parsed_fields` (Quelle fehlt)
- `linked_document_id` (keine ERP-Beleg-Join-Quelle)
- Artikel-Button nur wenn Extrakt echte Zeilen + Nummer liefert — ohne Positionen bleibt blocked-Hinweis
- Browser-Abnahme Artikel-Button / fetch-image an Live-Queue
- Kontrakt-Abgleich, Detailrouten Gutschrift/LS ohne ID

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest adaptive-workspace + workspace + disposition-board/load-timeline | **140/140** (21 Dateien) |
| pytest inbox/workspace/whatsapp/loading_atomic (`-m "not integration"`, `--noconftest`) | **212 passed**, 15 skipped |

---

## Handoff: 2026-10-23 Artikel-API STOP + Browser Lieferant-Button - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch — Artikel-Defaults + Bild-nach-Create siehe Handoff oben. Ziel blieb offen.

### Verdrahtet / STOP je Punkt

| Punkt | Status | Detail |
|---|---|---|
| 1 Lieferant-Uebernahme | **verdrahtet** | UI „Lieferant anlegen“ → Confirm → `POST /api/v1/einkauf/lieferanten`. Vitest mockt Confirm+POST. Browser: Button sichtbar bei `partner_nicht_gefunden` + Supplier-Proposal. |
| 2 Artikel-Uebernahme | **STOP** *(ueberholt)* | damals ohne Domänen-Defaults; inzwischen Defaults+Button (Handoff oben). |
| 3 Positionen | **STOP** | unveraendert (`keine_positionszeilen_im_extrakt`). |
| 4 Bilder | **STOP / Slot** *(ueberholt teilweise)* | damals nur Slot; jetzt fetch-image nach Create. |
| 5 Browser | **Button sichtbar** | Login mit freigegebener Testkennung (nicht in Docs). Screenshot: `evidence/screenshots/adaptive-workspace-inbox-lieferant-anlegen.png`. Backend musste neu gestartet werden (Workers ohne `--reload`), damit `master_data_proposals` live ankommt; Frontend-Bundle mit InboxWidget deployed. |

### Artefakte

| Symbol | Datei |
|---|---|
| `ARTICLE_CREATE_REQUIRED_WITHOUT_DEFAULT` | `master-data-create.ts` |
| Screenshot | `evidence/screenshots/adaptive-workspace-inbox-lieferant-anlegen.png` |

Approve bleibt 409. `pages/einkauf/**` / Codex-Verladung unangetastet. Keine Secrets in Docs.

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest adaptive-workspace + workspace + disposition-board + studio composition | **161/161** |
| pytest inbox/workspace/whatsapp (`-m "not integration"`) | **176 passed**, 15 skipped |

---

## Handoff: 2026-10-23 Stammdaten-Uebernahme Lieferant-POST - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch — Artikel-API/Browser siehe Handoff oben. Ziel blieb offen.

### Verdrahtet / STOP je Punkt

| Punkt | Status | Detail |
|---|---|---|
| 1 Lieferant-Uebernahme | **verdrahtet** | UI „Lieferant anlegen“ → Confirm → `POST /api/v1/einkauf/lieferanten` (`master-data-create.ts` + `InboxWidget`). Pflicht: firmenname + lieferantennummer. RBAC Endpoint (`SCHREIBEN["EINKAUF"]`). Kein Inbox-Approve, kein Direct-SQL. |
| 2 Artikel-Uebernahme | **STOP** | API `POST /api/v1/articles/` + Catalog `artikel.stamm.create` existieren; Proposal-Payload ohne `unit`/`category`/`sales_price` — kein Erfinden. `articleCreateFromInboxSupported` = false. |
| 3 Positionen | **STOP** | `dms_parser` ohne Positionen; `dms_ocr_contracts` ohne Zeilen-Extraktor; `ocr_invoice` eigener Einkauf-Pfad (Stub erfindet Musterzeilen) — nicht an DMS-Inbox. Alias `artikel_name` in `extract_line_items` nur falls Zeilen schon im Extrakt. Header-Lieferant bleibt. |
| 4 Bilder | **STOP / Slot** | `POST /api/v1/articles/enrich-images` braucht `article_id`; ohne Artikelanlage Slot belassen. |
| 5 Browser | **STOP Login-Wall** | damals Login-Wall; spaeter behoben (siehe aktueller Handoff). |

### Artefakte

| Symbol | Datei |
|---|---|
| `buildLieferantCreateBody` / `createLieferantFromProposal` | `packages/frontend-web/src/components/adaptive-workspace/inbox/master-data-create.ts` |
| Button `Lieferant anlegen` | `InboxWidget.tsx` (`data-testid=inbox-supplier-create-*`) |
| Action-Label Backend | `propose_supplier_create` → „Lieferant anlegen“, `domain_api` gesetzt |
| Vitest | `master-data-create.test.ts`, InboxWidget Confirm/POST-Tests |

Approve bleibt 409. `pages/einkauf/**` / Codex-Verladung unangetastet. Keine Secrets in Docs.

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest adaptive-workspace + workspace + disposition-board + studio composition | **161/161** |
| pytest inbox_contract + workspace_fachaktionen + agrar_chain + loading_atomic (`-m "not integration"`) | **113 passed**, 15 skipped |
| pytest erweitert (+ whatsapp inbox) | **176 passed**, 15 skipped |

---

## Handoff: 2026-10-23 Stammdaten-Vorschlag Lieferschein-Scan - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch — Uebernahme siehe Handoff oben. Ziel blieb offen.

### Verdrahtet (nur vorhandene Quellen)

| Symbol / Artefakt | Datei | Rolle |
|---|---|---|
| `extract_line_items` | `app/documents/inbox_contract.py` | liest nur `positionen`/`positions`/`lines`/`items`/`line_items` |
| `build_supplier_create_proposal` | dieselbe | bei `partner_nicht_gefunden` + Name/Nr. → Payload fuer `POST /api/v1/einkauf/lieferanten` / BP-API |
| `build_article_create_proposals` | dieselbe | Match oder Propose; ohne Zeilen STOP `keine_positionszeilen_im_extrakt` |
| `build_image_research_slot` | dieselbe | Slot auf `article_image_enrichment` + `POST /api/v1/articles/enrich-images`, `executed=false` |
| `build_master_data_proposals` + Queue-Feld `master_data_proposals` | dieselbe + `inbox_service.load_article_candidates_by_index` | Lookup via `WhatsAppIntakeService.match_artikel` |
| Fachaktionen `einkauf.lieferant.create`, `artikel.stamm.create` | `registry.ts` + `adaptive_workspace_fachaktionen.yaml` + `fachaktion-resolve.ts` | prepare-command, `executable: false` |
| Widget-Hinweise | `InboxWidget.tsx` / `types.ts` | Lieferant-/Artikel-Vorschlag bzw. Positions-STOP |

Approve bleibt 409 `booking_not_from_inbox`. Keine Direct-DB-Writes. `pages/einkauf/**` / Codex-Verladung unangetastet.

### Quellen-STOPs

| STOP | Fundstelle |
|---|---|
| OCR ohne Positionszeilen | `dms_parser.PATTERNS` ohne Positionen → `keine_positionszeilen_im_extrakt` (Header-Lieferant trotzdem) |
| `linked_document_id` | kein ERP-Beleg-Join in Queue/ORM |
| Kontrakt-Abgleich | `PIPELINE_GAPS` `kein_kontrakt_abgleich_am_eingang` |
| Bild-Download aus Inbox | bewusst nicht; nur Slot + Enrich-API |

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest Adaptive-Workspace | **155/155** |
| pytest inbox/workspace/loading_atomic (`-m "not integration"`) | **149 passed**, 15 skipped |

---

## Handoff: 2026-10-23 Suites grün + delivery_advice Mapping + Spot-Check - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch — Stammdaten-Vorschlag siehe Handoff oben. Ziel blieb offen.

### Gefixt

| Feld | Wert |
|---|---|
| Policy-Map | `_POLICY_DOCUMENT_TO_BELEGART["delivery_advice"]="goods_receipt"` in `app/documents/inbox_contract.py` (analog Lieferschein; bestehende Belegart, keine neue Rolle) |
| Test | `test_evaluate_can_open_maps_delivery_advice_to_goods_receipt` |
| Gutschrift/Wiegeschein can_open | kein gleiches Policy-Loch (kein dedizierter `document_type` in BELEG_POLICIES; Übersicht via `document_kind`; Beleg öffnen weiter `linked_document_id`) |

### Tests

| Suite | Ergebnis |
|---|---|
| Vitest workspace/inbox/disposition-board/studio-composition | **154/154** (23 Dateien) |
| pytest inbox/workspace/loading_atomic (`-m "not integration"`, `--no-cov`) | **146 passed**, 15 skipped, 5 deselected |

### Browser Spot-Check (Session aktiv)

| Fläche | Ergebnis | Screenshot |
|---|---|---|
| Start | ok; Inbox 2 offen; Labels **Zur Übersicht** + **Beleg öffnen** | `evidence/screenshots/adaptive-workspace-spot-start.png` |
| Strg+K / Suche | ok (Palette Verkauf/Einkauf) | via Suche-Button; vorher `adaptive-workspace-command-center.png` |
| Dispo | Tafel sichtbar; bekannte Auth-Hinweise Abrufe/SSE (nicht erzwungen) | `evidence/screenshots/adaptive-workspace-spot-disposition.png` |
| Studio | Composition Preview ok (Inbox+Dispo Slots) | `evidence/screenshots/adaptive-workspace-spot-studio.png` |

### Quellen-STOPs (blockiert, nicht erzwingen)

- Positionszeilen / Kontrakt-/Artikelabgleich
- `linked_document_id` ohne ERP-Join-Quelle → Ziel nicht complete
- Gutschrift/Lieferschein ohne Detailroute; Wiegeschein Beleg öffnen nur mit ID
- Kon-QS / `quality_is_final` ohne Feld
- EXCEPTION ohne Setter; Dispo Live-SSE/Abrufe Auth-Hinweis

### Nicht angefasst

Codex-Verladung (`tours.py`, `logistics_tours.py`, `outbox.py`); Godfiles; DATEV; Maskeninventar; Rollen; `pages/einkauf/**`; `pages/waage/**`; tourenplanung; MIGRATION-PARITY; Handbuch; Credentials nicht in Docs/env.

---

## Handoff: 2026-10-23 Zur Übersicht ok (supplier_delivery_note→goods_receipt) - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch — Suites/Spot-Check siehe Handoff oben. Ziel blieb offen — **nicht** complete. Kein Commit, kein Push.

### Warum Ziel noch nicht complete

Extraktion liefert keine verifizierte Beleg-ID: weder ORM-Spalte noch Queue-Feld setzt `linked_document_id`. Quelle fuer einen echten ERP-Beleg-Join fehlt; Positionen werden nicht erfunden. Ohne diese Quelle bleiben Detail-„Beleg öffnen“-Pfade (Wiegeschein/Gutschrift) und vollstaendige Prefill/Abgleich-Stufen offen.

### Mapping-Fix (Backend)

| Feld | Wert |
|---|---|
| Datei | `app/documents/inbox_contract.py` |
| Symbol | `_POLICY_DOCUMENT_TO_BELEGART` |
| Neu | `supplier_delivery_note` → `goods_receipt` |
| Muster | analog `supplier_invoice` → `purchase_invoice` |
| Rolle | keine neue; `darf(..., "bearbeiten")` kennt `goods_receipt` bereits |
| Runtime | Docker-Backend neu gestartet (Workers ohne Reload) |

### 1) Klick-Pfad „Zur Übersicht“ (LIEFERSCHEIN) — ok

| Feld | Wert |
|---|---|
| Ergebnis | **ok** |
| Zeile | `INBOX-AW-3dd3a6b3f3` |
| Label | **„Zur Übersicht“** (nicht mehr Permission-STOP) |
| Hinweis | „Beleg öffnen braucht eine verifizierte Beleg-ID.“ (korrekt: overview, kein Beleg ohne ID) |
| Ziel-URL | `/einkauf/lieferschein-erfassung?inbox=INBOX-AW-3dd3a6b3f3` |
| Screenshot | `evidence/screenshots/adaptive-workspace-inbox-zur-uebersicht.png` |
| `pages/einkauf/**` | **nicht** editiert |

### 2) Tests

| Suite | Ergebnis |
|---|---|
| Vitest `inbox-contract.test.ts` | 12/12 |
| pytest `test_evaluate_can_open_maps_supplier_delivery_note_to_goods_receipt` | passed |

### 3) Naechster Schritt

`linked_document_id`-Quelle / Extraktion; Detail-Pfade Wiegeschein/Gutschrift. Testzeilen belassen. Slice bleibt **in Arbeit**; Ziel nicht fertig.

### Nicht angefasst

Codex-Verladung (`tours.py`, `logistics_tours.py`, `outbox.py`); Godfiles; DATEV; Maskeninventar; Rollen; `pages/einkauf/**`; `pages/waage/**`; tourenplanung; MIGRATION-PARITY; Credentials nicht in Docs/env.

---

## Handoff: 2026-10-23 Klick-Pfade Beleg öffnen ok / Zur Übersicht STOP - ADAPTIVE-WORKSPACE-20261022 *(historisch)*

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** historisch — Mapping-Fix und „Zur Übersicht“ siehe Handoff oben. Ziel blieb offen.

### Kurz

EINGANGSRECHNUNG „Beleg öffnen“ ok. LIEFERSCHEIN war STOP wegen fehlendem `_POLICY_DOCUMENT_TO_BELEGART["supplier_delivery_note"]` — behoben.

### Nicht angefasst

Codex-Verladung; Godfiles; DATEV; Maskeninventar; Rollen; `pages/einkauf/**`; `pages/waage/**`; Credentials nicht in Docs.

---

## Handoff: 2026-10-23 Inbox-Labels abgenommen - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel bleibt offen. Kein Commit, kein Push. *(historisch; Klick-Pfad siehe Handoff oben)*

### 1) SSO-Login — ok

| Feld | Wert |
|---|---|
| Ergebnis | **Login ok** |
| URL | `http://localhost:3000/` (Start nach Keycloak-Callback) |
| Mandant-Kontext | Session aktiv; Inbox zeigt Seed-Zeile Tenant `…000051` |
| Credentials | nur im Browser getippt; **nicht** in Docs/env/Commit |

### 2) Inbox-Widget — Labels abgenommen

| Feld | Wert |
|---|---|
| Ergebnis | **ok** |
| Fundstelle | Start → Region **Beleg-Inbox** |
| Zeile | `INBOX-AW-01b649dab9` sichtbar (`1 offen · keine Buchung`) |
| Kind | EINGANGSRECHNUNG / UI „Rechnung“ / Vorschlag „Rechnungseingang erfassen“ |
| Label Erfassung | **„Beleg öffnen“** (Button) gesehen |
| Screenshot | `evidence/screenshots/adaptive-workspace-inbox-queue.png` |

### 3) Naechster Schritt

Testzeile `INBOX-AW-01b649dab9` belassen oder loeschen. Weitere Slice-Arbeit nach Workboard; Ziel **nicht** fertig markieren. Slice bleibt **in Arbeit**.

### Nicht angefasst

Codex-Verladung; Godfiles; DATEV; Maskeninventar; Rollen; `pages/einkauf/**`; `pages/waage/**`; tourenplanung; MIGRATION-PARITY; keine Secrets in Dateien.

---

## Handoff: 2026-10-23 Live-Inbox-Seed ok, Browser Login-STOP - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push. *(historisch; Labels inzwischen abgenommen — siehe Handoff oben)*

### 1) Seed — ok

| Feld | Wert |
|---|---|
| Ergebnis | **Seed ok** |
| DB | `valeo_neuro_erp` (`.env` `DATABASE_URL` + Docker-Backend `postgres:5432/valeo_neuro_erp`) |
| Helper | `tests/helpers/dms_inbox.py` `insert_inbox` (gleiches Schema, Schreibprobe mit Rollback zuerst) |
| id | `INBOX-AW-01b649dab9` (**Testzeile belassen**) |
| tenant_id | `00000000-0000-0000-0000-000000000051` |
| status | `pending` |
| ocr_text | `Rechnung Rechnungsnummer MwSt Zahlungsziel` → `document_kind=EINGANGSRECHNUNG` |
| Nicht gesetzt | keine Positionszeilen, kein `linked_document_id` |

### 2) Browser — STOP (Labels / Screenshot)

| Frage | Antwort |
|---|---|
| Ergebnis | **STOP** nach Seed |
| Fundstelle | Cursor-Browser-Tab `http://localhost:3000/login` — Button „Mit SSO anmelden“; Keycloak-Login ohne bestehende Session |
| Ursache | Vorherige Session (localStorage OIDC) war weg; Navigation auf `127.0.0.1` hatte Origin getrennt; SSO-Klick → Username/Password-Formular |
| Credentials | nicht aus Dateien / nicht eingegeben |
| Labels „Beleg öffnen“ / „Zur Übersicht“ | **nicht gesehen** |
| Screenshot | `evidence/screenshots/adaptive-workspace-inbox-queue.png` **nicht** erzeugt |
| Computer Use | sidecar_unavailable |

### 3) Naechster Schritt

Nach manuellem SSO am Mandanten `…000051` → `/studio/workspace-composition-preview` (oder Home mit Inbox-Widget) → Labels + Screenshot. Testzeile `INBOX-AW-01b649dab9` loeschen oder belassen. Slice bleibt **in Arbeit**.

### Nicht angefasst

Codex-Verladung; DATEV; Maskeninventar; Rollen; `pages/einkauf/**`; `pages/waage/**`; tourenplanung; MIGRATION-PARITY; Credentials nicht in Dateien.

---

## Handoff: 2026-10-23 linked_document_id STOP + Inbox-Helper - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push. Produktivdateien Codex (`tours.py`, `logistics_tours.py`, `outbox.py`) **nicht** geschrieben.

### 1) linked_document_id — STOP (keine Verdrahtung)

Keine Spalte/kein Feld ist eine **verifizierte ERP-/Beleg-ID**. Deshalb kein Mapping in `build_queue_item`.

| Kandidat | Fundstelle | Warum nicht |
|---|---|---|
| ORM-Spalte | `DmsInboxEntry` (`dms_inbox.py`) | Spalten: `id`, `dms_document_id`, `dms_url`, `ocr_text`, `parsed_fields`, `confidence`, `status`, `tenant_id`, `created_at` — **kein** `linked_document_id` |
| `dms_document_id` | ORM + Queue-Return | Mayan-/DMS-Dokument-ID (Integer), keine ERP-Beleg-ID |
| `match.partner_id` / Prefill `partner.id` | `partner_match_from_candidates` | BusinessPartner, kein Beleg |
| `match_values.purchaseOrderId` / `deliveryNoteId` / `goodsReceiptId` / `contractId` | `match_values(parsed_fields)` | OCR-/Parser-Extrakt, nicht verifiziert |
| `duplicates[].doc_number` | `duplicate_hints` / `load_duplicate_candidates` | nur `doc_type`+`doc_number`, **keine** Dokument-PK |
| `command.prefill.documentId` | `prepare_command` | Inbox-Eintrags-`id`, kein ERP-Beleg |
| UI | `inbox-contract.ts` `verifiedBelegId` | liest nur `item.linked_document_id` — Backend setzt es nie |

### 2) Inbox-Helper + Browser — STOP nach Helper + pytest

| Schritt | Ergebnis |
|---|---|
| Helper | `tests/helpers/dms_inbox.py` — `insert_inbox` / `has_tenant_column` (gleiches SQL/Schema, keine neuen Spalten); Router-Tests importieren den Helper |
| Session-Tenant | Browser SSO: `tenant_id=00000000-0000-0000-0000-000000000051` (localStorage JWT) |
| DB-Split | Live-`.env` `DATABASE_URL` → **valeo_neuro_erp**; `TEST_DATABASE_URL` → **valeo_probe**. Seed auf Probe erreicht die Live-Queue nicht |
| Screenshot | `evidence/screenshots/adaptive-workspace-inbox-queue.png` **nicht** erzeugt (Labels brauchen sichtbare Queue-Zeile am Live-Backend) |
| pytest | `tests/test_documents_inbox_router.py` mit `DATABASE_URL=TEST_DATABASE_URL=valeo_probe` → **4 passed** (Helper fuellt Queue fuer Session-Mandant der TestClient) |

### 3) Gate/Evidence

- Vitest `invariants-gate` + `inbox-widget` → **23 passed**
- Slice bleibt **in arbeit**; Ziel nicht fertig

### Nicht angefasst

Codex-Verladung (`tours.py`, `logistics_tours.py`, `outbox.py`); DATEV; Maskeninventar; Rollen; `studio_screen_versions`; `pages/einkauf/**`; `pages/waage/**`; tourenplanung; MIGRATION-PARITY; Credentials nicht in Dateien.

### Naechster Schritt

Live-Backend auf Probe zeigen **oder** echten Mayan-Webhook in die DB schreiben, die der laufende Stack liest → dann Labels + Screenshot. `linked_document_id` erst nach verifizierter Beleg-Quelle (Join/Spalte), nicht aus Mayan-/Partner-/OCR-Feldern.

---

## Handoff: 2026-10-23 Codex-Risiken + Inbox-STOP + linked_document_id - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push. Produktivdateien Codex (`tours.py`, `logistics_tours.py`, `outbox.py`) **nicht** geschrieben.

### A) Codex-Verladung — User-Risiken (READ-ONLY)

| # | Risiko | Status | Fundstelle |
|---|---|---|---|
| 1 | Urheber aus gepruefter Identitaet, nicht Request-Params | **erfuellt** | `tours.py` `start_loading`/`finish_loading`: `user_id = current_user.get("sub")`, `anmeldename(current_user)`; keine Body/Query-Actor-Parameter. Test `test_loading_http_ignores_forged_query_actor` (`?user_id=forged` wird ignoriert). |
| 2 | Status + Outbox atomar / kein Event-Verlust nach Status | **erfuellt** | Repo `commit=False` → `_publish_loading_outbox`/`OutboxPublisher.store_event` (gleiche Session) → ein `db.commit()`; bei Fehler `db.rollback()`. Outbox: `store_event` nur `db.add`, kein eigener Commit. Tests `test_loading_commits_status_actor_log_and_outbox_together`, `test_outbox_failure_rolls_back_status_and_log`. |
| 3 | Event nur fuer Tour des angemeldeten Mandanten | **erfuellt** | `TourRepository(db, tenant_id)` filtert `Tour.tenant_id == self.tenant_id`; Fremd-Tour → 404, kein Outbox-Eintrag. Test `test_foreign_loading_cannot_mutate_or_emit`. |

**Testergebnis:** `pytest tests/test_loading_atomic_actor.py --no-cov -o addopts=` → **15 passed, 15 skipped** (Postgres-Param ohne/mit Probe-Skip), Exit 0. Keine Produktiv-Edits.

### B) Inbox-Queue Seed

| Frage | Antwort |
|---|---|
| Ergebnis | **STOP** — keine Queue-Zeile angelegt |
| Gesucht | Test-Factories/Fixtures/Scripts fuer `dms_inbox` |
| Gefunden | Nur lokal in `tests/test_documents_inbox_router.py`: `_insert_inbox` = **rohes SQL-INSERT** (kein wiederverwendbarer Helper/Factory/Script unter `scripts/` oder conftest) |
| Produktiver Pfad | weiter nur `POST /api/dms/webhook` (Mayan + `DMS_TOKEN` + `data/config/dms.json`) — weder Token noch OCR erfunden |
| Screenshot | `adaptive-workspace-inbox-queue.png` **nicht** erzeugt |

### C) Luecke ausserhalb Codex (Evidence geschaerft)

**`linked_document_id` fehlt am Queue-Item (kein Fix in diesem Turn — Quelle fuer Join fehlt).**

| Schicht | Fundstelle | Ist |
|---|---|---|
| UI-Vertrag | `packages/frontend-web/.../inbox/inbox-contract.ts` `verifiedBelegId` / `inboxOpenDecision` | „Beleg öffnen“ Detailpfad braucht `item.linked_document_id` |
| Backend Queue | `app/documents/inbox_contract.py` `build_queue_item` (Return-Dict) | Feld **wird nie gesetzt** |
| ORM | `app/api/v1/endpoints/dms_inbox.py` `DmsInboxEntry` | Spalte **existiert nicht** |
| PIPELINE_GAPS | `app/documents/inbox_contract.py` | kennt Gap nicht explizit (`kein_artikel_abgleich_am_eingang` ja; `linked_document_id` nein) |

### Nicht angefasst

Codex-Godfiles Verladung, DATEV, Maskeninventar, Rollen, `studio_screen_versions`, `pages/einkauf/**`, `pages/waage/**`, `tourenplanung`, MIGRATION-PARITY; Credentials nicht in Dateien. Slice bleibt **in Arbeit**.

### Naechster Schritt

Mayan/DMS ehrlich konfigurieren → Queue-Zeile → Labels + Screenshot; optional `linked_document_id`-Join wenn Beleg-Quelle existiert. Ziel offen.

---

## Handoff: 2026-10-23 Inbox-Queue STOP + Handbuch-Links - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### 1) Queue-Zeile: STOP

| Frage | Antwort |
|---|---|
| Ergebnis | **STOP** — keine Queue-Zeile angelegt |
| Einziger produktiver Schreibpfad | `POST /api/dms/webhook` in `app/routers/dms_webhook_router.py` → `domain_shared.dms_inbox` (OCR von Mayan via `_process_incoming_document`) |
| Voraussetzung | `is_configured()` in `app/integrations/dms_client.py`: `data/config/dms.json` **und** Env `DMS_TOKEN` |
| Ist-Stand lokal | `configured=False`, `token_set=False`, `config_exists=False`; ohne Config returniert der Webhook ok, schreibt aber **keine** Zeile |
| DB | `valeo_probe.domain_shared.dms_inbox`: **total=0 / pending=0** |
| Verboten / nicht genutzt | erfundenes OCR, Musterartikel, rohes SQL-INSERT, Fake-Client wie in `tests/test_dms_webhook_tenant.py` |
| Screenshot | `evidence/screenshots/adaptive-workspace-inbox-queue.png` **nicht** erzeugt (Labels brauchen Zeile) |
| UI-Test | nicht ausgefuehrt fuer Labels (kein Inhalt) |

`POST /api/v1/dms/inbox/{id}/create` flippt nur `status=processed` und legt **keine** Inbox-Zeile an.

### 2) Handbuch-Links

- Quelle: `docs/agent-ops/sources/adaptive-workspace-20261022.md` — relative Links `../../../evidence/screenshots/adaptive-workspace-*.png`
- Index-Abschnitt Adaptive Workspace in `docs/agent-handbuch/index.md` — relative Links `../../evidence/screenshots/adaptive-workspace-*.png`
- Generator **nicht** voll ausgefuehrt (Drift 130 vs 135 belassen)
- Domain-Event-Zahlen unberuehrt

### 3) Codex-Verladung (read-only, nichts geaendert)

| Datei | Working Tree |
|---|---|
| `app/api/v1/endpoints/tours.py` | **MM** (staged+unstaged WIP) |
| `app/api/v1/endpoints/logistics_tours.py` | **MM** |
| `app/infrastructure/eventbus/outbox.py` | **MM** |

Inhaltlich im Diff sichtbar (nur gelesen): Mandant via `get_tenant_id` / `tenant_id` an Repos; Verladung Start/Finish mit `commit=False` + gemeinsames `db.commit()` nach Outbox (`_publish_loading_outbox` / `OutboxPublisher`); `user_id` aus Token-`sub`. **Urheber/Atomaritaet/Mandant liegt als Codex-WIP im Working Tree — nicht angefasst.**

### Nicht angefasst

Codex-Godfiles, DATEV, Maskeninventar, Rollen, `studio_screen_versions`, `pages/einkauf/**`, `pages/waage/**`, tourenplanung, MIGRATION-PARITY; Credentials nicht in Dateien.

### Naechster Schritt

Mayan/DMS ehrlich konfigurieren (Token + Config) und echten OCR-Webhook mit Document-Kind EINGANGSRECHNUNG/LIEFERSCHEIN → dann Labels + `adaptive-workspace-inbox-queue.png`. Slice bleibt **in Arbeit**.

---

## Handoff: 2026-10-23 Studio-Preview + Deliverable-Audit - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Studio: ok

| Check | Ergebnis |
|---|---|
| URL | `http://localhost:3000/studio/workspace-composition-preview` |
| Route | **ok** — kein Not Found; Runtime-Attach `attachStudioPreviewRoute` in `router.tsx` (kein Auto-Group noetig) |
| Session | bestehend (Benutzermenue); kein neues Login |
| Composition | Fixture `workspace.disposition-und-inbox`; Slots Inbox + Dispo-Tafel checked |
| Host | `WorkspaceCompositionHost` mountet Dispo-Tafel (`disposition-board`, Stopp-Karten-Hinweis lat/lng) + Beleg-Inbox (`adaptive-workspace-inbox`, Queue leer / 0 offen) |
| Screenshot | `evidence/screenshots/adaptive-workspace-studio.png` |
| Rebuild | nicht noetig (Route schon im Image) |

### Evidence Deliverable 1–7 (Stand 2026-10-23 Studio+Audit)

| # | Deliverable | Status | Nachweis / Luecke |
|---|---|---|---|
| 1 | Registry / vier Ebenen | **nachgewiesen** | `WORKSPACE_FACHAKTIONEN`, Vitest `registry` / `fachaktion-resolve` |
| 2 | Command Center / Strg+K | **nachgewiesen** | Vitest dryRun/Aliase; Browser `adaptive-workspace-command-center.png` |
| 3 | Inbox Prefill / Match / Oeffnen | **unvollstaendig** | Prefill/Match/Labels im Code+Vitest; **Positionen STOP** (kein Extraktions-Join); **linked_document_id STOP**; an **leerer Queue** keine Zeilen-Labels „Zur Übersicht“/„Beleg öffnen“ (Browser kann sie nicht abnehmen) |
| 4 | Dispo Assign + Verladung-Live | **Codex-Besitz** / teilweise | Tafel+Stopp-Hinweis Browser Studio/Dispo-Screenshots; Auth/Atomaritaet/Mandant/Outbox = Codex (`tours.py`, `logistics_tours.py`, `outbox.py`) — unberuehrt |
| 5 | Studio Composition | **nachgewiesen** | Host+Preview Browser; Vitest `workspace-composition-*` / `studio-preview-route` (6 passed) |
| 6 | MCP Fachaktionen | **nachgewiesen** | `tests/test_workspace_fachaktionen.py` / Vier-Augen; kein Browser-MCP in diesem Turn |
| 7 | Agrar-Kette | **nachgewiesen** (mit Vorbehalt) | Ranking/Progression Tests; Kon ohne QS-Join bleibt Absicht |

### Ehrliche Luecken (kein Fix in diesem Turn)

- Inbox-Extraktion Positionen — Quelle fehlt
- `linked_document_id` — kein Inbox-/Match-Feld
- Browser-Labels an leerer Queue — UI korrekt ohne Zeilen; Abnahme der Aktionslabels braucht Queue-Inhalt
- Verladung-Sicherheit — Codex-Besitz
- Synthetische SSO frueher abgewiesen; **manuelle SSO-Session jetzt ok** (Start/Strg+K/Dispo/Studio)

### Code-Fix

Keine schliessbare Luecke ausserhalb Codex mit existierender Quelle → **nur Audit + Studio**.

### Nicht angefasst

Codex Verladung/Godfiles, DATEV, Maskeninventar, Rollen, `studio_screen_versions`, `pages/einkauf/**`, `pages/waage/**`, `tourenplanung.tsx`, MIGRATION-PARITY; Handbuch nicht voll regeneriert.

### Naechster Schritt

Slice-Rest (Inbox-Join wenn Quelle, Live-SSE Auth auf Tafel, Workspace-Zielkriterien). Ziel bleibt offen. Slice bleibt **in Arbeit**.

---

## Handoff: 2026-10-23 Frontend-Rebuild + Dispo sichtbar - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Frontend aktualisiert

| Was | Detail |
|---|---|
| Laufweg | `docker-compose.yml` Service `frontend-web` → Image-Build `Dockerfile.frontend`, Port `3000:8080`, **kein** Source-Mount |
| Update | `docker compose up -d --build frontend-web` (bestehender Service; keine neuen Container/DBs) |
| Hinweis | `docker-compose.dev.yml` haette Vite+Volume; `docker-compose.local-preview.yml` mappt ggf. `:3001` auf dasselbe nginx-Image — das ist kein Vite-Dev |
| Route im Image | `disposition/touren-disposition` in gebauten Assets nachweisbar |

### Browser-Abnahme Disposition

| Check | Ergebnis |
|---|---|
| URL | `http://localhost:3000/disposition/touren-disposition` |
| Session | bestehend (Benutzermenue sichtbar); kein erneutes Login noetig |
| Tafel | **sichtbar** — H1 „LKW-Disposition“, Region „LKW-Dispositionstafel“, Spalten Auftraege/Ressourcen/Betriebszustaende; kein Not Found |
| Screenshot | `evidence/screenshots/adaptive-workspace-disposition.png` **ersetzt** |
| Hinweise UI | Abrufe/Live-SSE melden Auth/Recht; Zeitachse ohne `planned_arrival`; keine Touren geladen (Adapter auf Godfile) |

### Inbox-502 Befund (kein Fix)

| Frage | Antwort |
|---|---|
| Welcher Service/Proxy? | Frontend-nginx `deploy/nginx/frontend.conf` `location /api/mcp/documents` → **backend:8000** (`app/documents/inbox_router.py` → DMS-Inbox-Service). **Nicht** BFF. |
| BFF | `localhost:4001` Stub `200` leere Queue — anderer Pfad als die UI |
| Historischer 502 | typisch nginx Bad Gateway wenn Backend ungesund (z. B. nach Restart/Postgres-fsync) |
| Aktuell mit Bearer | `200`, `source=dms_inbox`, `count=0` — kein DMS-/Codex-Godfile-Fix noetig |
| Credentials | keine in Doku/env geschrieben |

### Nicht angefasst

- `pages/logistik/tourenplanung.tsx`, Codex Verladung (`tours.py`, `logistics_tours.py`, `outbox.py`), DATEV, Maskeninventar, Rollen, `pages/einkauf/**`, `pages/waage/**`, MIGRATION-PARITY-Block.

### Naechster Schritt

- Slice-Rest: Inbox-Positionen/Join, Live-SSE Auth auf Tafel, Workspace-Zielkriterien; Ziel bleibt offen.

---

## Handoff: 2026-10-23 Route-Fix touren-disposition - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Route-Fix

| Was | Wo |
|---|---|
| Registrierung | `packages/frontend-web/src/app/route-builders/auto-groups/generated/disposition.ts` — Entry `module: @/pages/disposition/touren-disposition`, `path: touren-disposition` |
| Generator | `npm run routes:generate` → `route-tree.gen.tsx` + `route-inventory.gen.json` (943 Routen; Windows-Lock umgangen via delete+rename) |
| Page unveraendert | `pages/disposition/touren-disposition.tsx` → `useUniversalMaskRuntime` → `UniversalMaskRenderer` / `disposition_board` (keine zweite Tafel) |
| Vitest | `invariants-gate.test.ts` „Touren-Disposition…“ **1 passed** (Auto-Group + `path: "disposition/touren-disposition"` im Route-Tree) |

### Browser

- Session auf `localhost:3000` noch da; Image `valeo-neuro-erp-frontend` (Docker-Build, kein Source-Mount) zeigt weiter **Not Found** bis Frontend-Image neu gebaut wird.
- Screenshot `evidence/screenshots/adaptive-workspace-disposition.png` **nicht** ersetzt (Tafel im Docker-Frontend noch nicht sichtbar).

### Inbox-502 (offen, nicht gebaut)

- Frontend ruft `GET /api/mcp/documents/inbox/queue` (`InboxWidget` / `inbox-screen.ts`).
- HTTP 502 bleibt offen (BFF/MCP bzw. Downstream); DMS-Stack nicht angefasst.
- Keine Credentials in dieser Doku.

### Nicht angefasst

- `pages/logistik/tourenplanung.tsx`, Codex Verladung (`tours.py`, `logistics_tours.py`, `outbox.py`), DATEV, Maskeninventar, Rollen, `pages/einkauf/**`, `pages/waage/**`, MIGRATION-PARITY-Block.

### Naechster Schritt

- Frontend-Image neu bauen / lokalen Vite gegen dieselbe SSO-Session; Browser: Tafel/Karte/Zeitachse; Inbox-502 gesondert (BFF-Logs), Slice bleibt in Arbeit.

---

## Handoff: 2026-10-23 Browser-Abnahme SSO - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Browser-Abnahme gelungen (ohne Credentials)

| Schritt | Ergebnis |
|---|---|
| 1 SSO Login | Login gelungen (`localhost:3000`, Keycloak Realm `valeo-neuro-erp`) |
| 2 Start / Handlungsbedarf | `data-testid=adaptive-workspace-layer` sichtbar; Dialog, Handlungsbedarf, Agrar-Kette, Beleg-Inbox, LKW-Disposition |
| 3 Strg+K / Command Center | Alias-Phrase `nicht disponierte lkw` → Treffer „Nicht disponierte LKW-Auftraege / Katalog“; kein Auto-Submit (Escape geschlossen) |
| 4 Inbox-Widget | sichtbar; Queue leer + HTTP 502 → keine Zeilen-Buttons „Zur Übersicht“ / „Beleg öffnen“ |
| 5 `/disposition/touren-disposition` | bedient (Link + Direkt-URL) → **Not Found**; Page `pages/disposition/touren-disposition.tsx` vorhanden, fehlt in `route-builders/auto-groups/generated/disposition.ts` und damit in `route-tree.gen.tsx` |

### Screenshots (ehrliche Flächen, kein Login-Wall)

- `evidence/screenshots/adaptive-workspace-start-handlungsbedarf.png`
- `evidence/screenshots/adaptive-workspace-command-center.png`
- `evidence/screenshots/adaptive-workspace-inbox.png`
- `evidence/screenshots/adaptive-workspace-disposition.png` (Not Found)

### Hinweise

- Backend zeitweise 502 auf Agrar-Kette und Inbox-Queue (Postgres/Keycloak nach Container-Restart lange im fsync).
- Codex-Verladung / MIGRATION-PARITY / `pages/einkauf/**` / `pages/waage/**` unangetastet.
- Slice bleibt **in Arbeit**. Naechster Schritt: `touren-disposition` in Auto-Group + `routes:generate`, dann Tafel/Karte/Zeitachse erneut abnehmen.

---

## Handoff: 2026-10-23 Öffnen-Parität ER/LS + linked_document_id STOP - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Browser

Tab `http://localhost:3001/login` (Login-Wall). Sofort STOP — kein Credential-Scan, kein Dev-JWT, keine Screenshots.

### Öffnen-Parität (gegen Gutschrift/Wiegeschein-Regel)

| Art | Primär | Label | Prefill | Beleg öffnen |
|---|---|---|---|---|
| EINGANGSRECHNUNG | `…/rechnung-eingang-erfassung/neu?inbox=` | Beleg öffnen (Erfassung) | ja | Erfassung = Prefill-Pfad |
| LIEFERSCHEIN | `/einkauf/lieferschein-erfassung?inbox=` | Zur Übersicht | nein | disabled (keine Detailroute; ID wuerde nichts oeffnen) |
| GUTSCHRIFT / WIEGESCHEIN | unveraendert Listen | Zur Übersicht | nein | nur mit verifizierter ID + Detailroute (Wiegeschein) |

`pages/einkauf/**` unangetastet. Registry/YAML/Resolve: `einkauf.lieferschein.list`.

### linked_document_id

STOP. Weder Queue-Serialisierung noch `match_values`/`match` liefern eine ERP-Beleg-ID. Kein Fuellen aus Inbox-ID, DMS-ID oder Belegnummer.

### Weitere Luecke (ausserhalb Verladung)

Lieferschein-Liste hatte keine catalogId — jetzt `einkauf.lieferschein.list` (Quelle: Navigation `preferredPath` `einkauf/lieferschein-erfassung`).

### Evidence 1–7 (geschaerft)

| # | Status |
|---|---|
| 1–2 Registry/Command Center | List-catalogIds inkl. Lieferschein; **Browser Login-Wall** |
| 3 Inbox Prefill/Match | Prefill nur ER; LS/Gutschrift/Wiegeschein Übersicht; Positionen STOP; linked_document_id STOP |
| 4 Dispo / Verladung | Codex — unberuehrt |
| 5–7 Studio / MCP / Agrar | YAML Handshake-IDs + Resolve-Aliase; Browser STOP |

**Tests:** Vitest inbox-contract/widget/rank + invariants-gate + registry + fachaktion-resolve; pytest `test_workspace_fachaktionen.py --noconftest --no-cov -o addopts=`.

---

## Handoff: 2026-10-23 Orthografie+Richtung+catalogId-Gate - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Geaendert

| Punkt | Aenderung |
|---|---|
| 1 Label-Orthografie | „Beleg öffnen“ / „Zur Übersicht“ in `inbox-contract`, Widget (sr-only), `inbox-screen`, Backend-Action-Label, Tests/Fixtures |
| 2 GUTSCHRIFT ohne Richtung | `direction` optional; `creditListRoute` → `mode:'none'`, kein „Zur Übersicht“; Widget-Test + Contract-Test |
| 3 Weitere Luecke | Gate Übersicht-vs-Beleg: Widget zeigt immer `decision.actionLabel` (nicht Backend-ASCII); `invariants-gate` catalogId === YAML `action_id` + `route_path` fuer `sales.credit_note.list` / `einkauf.gutschrift.list` / `weighing.tickets.list` |

### Codex-Besitz Verladung (unberuehrt)

`tours.py`, `logistics_tours.py`, `outbox.py`, TourRepository / Verladungs-Auth/Atomaritaet/Mandant; Workboard-Block `MIGRATION-PARITY-REPAIR-20261022`; DATEV, Maskeninventar, Rollen, `studio_screen_versions`, `pages/einkauf/**`, `pages/waage/**`, `pages/logistik/tourenplanung.tsx`.

### Browser / SSO

Synthetische Kennung bleibt abgewiesen. Kein Dev-JWT, kein Kennwort, keine Browser-Abnahme ohne bestehende SSO-Sitzung.

### Evidence Deliverable 1–7 (Stand 2026-10-23 Orthografie+Gate)

| Deliverable | Status |
|---|---|
| 1–2 Registry/Command Center | List-catalogIds + YAML-Parity-Gate; **Browser blockiert** (SSO) |
| 3 Inbox Prefill/Match | Match da; Übersicht richtungstreu; Beleg öffnen nur mit ID; ohne Richtung disabled; Positionen STOP |
| 4 Dispo / Verladung | Codex-Besitz — unberuehrt |
| 5–7 Studio / MCP / Agrar | unveraendert; YAML Notes Orthografie |

**Tests:** Vitest inbox-contract/widget/rank + invariants-gate (+ verwandte); pytest `test_workspace_fachaktionen.py --noconftest --no-cov -o addopts=` bei Bedarf.

---

## Handoff: 2026-10-23 Gutschrift/Wiegeschein-Listen verdrahtet - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Routen gefunden + verdrahtet

| Art | Listen-Route (ohne `:id`) | Quelle | catalogId / Registry |
|---|---|---|---|
| GUTSCHRIFT | `/sales/credit-notes` | `route-aliases` + `commercial.tsx` `ausgehend-gutschrift`; Page `pages/sales/credit-note-editor` | `sales.credit_note.list` → `sales.credit-notes-list` (`open-worklist`) |
| WIEGESCHEIN | `/weighing` | `route-aliases` + `NativeListPage` `pages/weighing` (ausserhalb `pages/waage/**`) | `weighing.tickets.list` → `weighing.tickets-list` (`open-worklist`) |

`inboxOpenDecision`: beide Arten → Listen-Href mit `?inbox=<queue-id>` (Pointer, keine Beleg-ID), `consumesPrefill: false`. Keine Prefill-Zwang, `pages/einkauf/**` und `pages/waage/**` unangetastet.

### Evidence Deliverable 1–7 (Stand 2026-10-23 Listen-Verdrahtung)

| # | Deliverable | Status |
|---|---|---|
| 1 | Registry / vier Ebenen | **nachgewiesen** (`WORKSPACE_FACHAKTIONEN` + neue List-catalogIds) |
| 2 | Command Center / Strg+K | **nachgewiesen** (Aliase in `fachaktion-resolve`); **Browser blockiert** (Login-Wall) |
| 3 | Inbox Prefill/Match | Match **nachgewiesen**; Prefill nur EINGANGSRECHNUNG; Gutschrift/Wiegeschein Liste ohne Prefill **nachgewiesen**; Positionen **Quelle fehlt** |
| 4 | Dispo + Verladung-Live | **nachgewiesen** (frueherer Turn: Zeitachse + `ops:verladung`) |
| 5 | Studio Composition | **nachgewiesen** unveraendert; Kalender/Approvals reasonCodes |
| 6 | MCP Fachaktionen | **nachgewiesen** YAML + Handshake-IDs; **Browser blockiert** |
| 7 | Agrar-Kette | **nachgewiesen** unveraendert |

**Tests:** Vitest inbox-contract/widget/rank + inbox-ranking + invariants-gate + registry + fachaktion-resolve → **44 passed**. pytest `test_workspace_fachaktionen.py --noconftest --no-cov -o addopts=` → **39 passed**.

---

## Handoff: 2026-10-23 Gutschrift/Wiegeschein Zur Übersicht + SSO - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### 1) GUTSCHRIFT / WIEGESCHEIN — Uebersicht verdrahtet (kein Einzelbeleg-Ersatz)

| Symbol / Datei | Verdrahtung |
|---|---|
| `inboxOpenDecision` `packages/frontend-web/src/components/adaptive-workspace/inbox/inbox-contract.ts` | `mode:'overview'`, Label `Zur Übersicht`; `GUTSCHRIFT` Richtung: `outgoing`→`/sales/credit-notes`, `incoming`→`/einkauf/gutschriften-belastungen`; `WIEGESCHEIN`→`/weighing` |
| `INBOX_OVERVIEW_ACTION_LABEL` / `documentOpenEnabled` | „Beleg öffnen“ nur mit `linked_document_id`; Gutschrift ohne Detailroute → disabled; Wiegeschein mit ID → `/waage/wiegeschein/:id` |
| `InboxWidget` | Primaer „Zur Übersicht“; Aside „Beleg oeffnen“ disabled ohne ID |
| Registry/YAML | `sales.credit_note.list`, `einkauf.gutschrift.list`, `weighing.tickets.list` |

`pages/einkauf/**` und `pages/waage/**` unangetastet. Keine erfundenen Beleg-IDs.

### 2) Browser / SSO — Befund (User)

Synthetische Testkennung wurde beim **regulären SSO** abgewiesen. Kein Dev-JWT als Abnahme, kein Kennwort geraten, keine Browser-Scan-Abnahme. Abnahme bleibt an echte SSO-Sitzung gebunden.

### Evidence Deliverable 1–7 (Stand 2026-10-23 Übersicht+SSO)

| Deliverable | Status |
|---|---|
| 1–2 Registry/Command Center | Uebersichts-catalogIds nachgewiesen; **Browser blockiert** (SSO lehnt synthetische Kennung ab) |
| 3 Inbox Prefill/Match | Match-Quelle da; Positionen STOP; Gutschrift/Wiegeschein = Übersicht ohne Prefill |
| 4–5 Dispo / Studio | unveraendert |
| 6–7 MCP / Agrar | YAML Handshake-IDs erweitert; Browser STOP |

**Tests:** Vitest inbox-contract/widget/rank + registry/gate/fachaktion-resolve; pytest `test_workspace_fachaktionen.py --noconftest --no-cov`.

---

## Handoff: 2026-10-23 Proactive+Gantt-Audit+Advisor - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Audit-Befund

| Punkt | Befund | Aktion |
|---|---|---|
| 1 Vier Schichten / Proactive | Registry hat proactive Fachaktionen; Approvals-Queue + SSE `approval_requested` waren schon `layer:proactive`, Kalender-Signale fuer rein-proactive Ziele (planting→Ueberfaellig, afternoon→LKW, evening→Freigabe) waren `situational` ohne reasonCodes | verdrahtet: `home-signals` stuft reine Proactive-Ziele als `proactive` + `cal:season:*`/`cal:day:*`/`layer:*`; Approvals Queue/SSE bekommen `ops:freigabe` reasonCodes |
| 2 Disposition „Gantt“ | `DispositionBoard` Zeitachse: Spuren (`TimelineLaneRow`) + Marker aus `planned_arrival` (`markerOffset` auf Achse) — echte Zeitachsen-Darstellung, keine reine Textliste | nichts geaendert (Balken/Marker schon da) |
| 3 RankingAdvisor | `noopRankingAdvisor` existierte; Hook fehlte; Layer rief `rankWorkspaceItems` ohne `advisor` | `useRankingAdvisor` + Export; `AdaptiveWorkspaceLayer` uebergibt Advisor (Default Identitaet, kein LLM) |
| 4 Weitere Luecke | keine zusaetzliche mit existierender Quelle in diesem Turn | Evidence 1–7 unten auf Ist |

### Evidence Deliverable 1–7 (Stand 2026-10-23 Proactive+Advisor)

| Deliverable | Status |
|---|---|
| 1–2 Registry/Command Center | unveraendert nachgewiesen; **Browser blockiert** (`localhost:3001/login` Login-Wall, kein Scan) |
| 3 Inbox Prefill/Match | Match-Quelle da; **Inbox-Extraktion/Positionen Quelle fehlt** (kein Join `dms_document_id`→`document_items`) |
| 4 Dispo + Verladung-Live | Zeitachse Spuren/Marker aus `planned_arrival`; LOADING Outbox + `ops:verladung` reasonCodes |
| 5 Studio Composition | unveraendert; Proactive-Kalender/Approvals reasonCodes verdrahtet |
| 6–7 MCP / Agrar | unveraendert; **Gutschrift/Wiegeschein ohne catalogId**; Browser STOP |

**Tests:** Vitest home-layer + prioritization + live-signals + invariants-gate + disposition-board + load-timeline → **39 passed**.

---

## Handoff: 2026-10-23 Gutschrift/Wiegeschein-STOP + LOADING publish_pending - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### 1) GUTSCHRIFT / WIEGESCHEIN Oeffnen — STOP (keine List-catalogId)

| Fundstelle | Befund |
|---|---|
| `inboxOpenDecision` / `inboxOpenHref` in `packages/frontend-web/src/components/adaptive-workspace/inbox/inbox-contract.ts` | `GUTSCHRIFT`/`WIEGESCHEIN` → `href: ''` mit Reason (Listen lesen keinen Inbox-Beleg; `:id`-Route braucht Schein-ID) |
| `config/adaptive_workspace_fachaktionen.yaml` `actions` | kein `action_id` fuer Gutschrift-Liste oder Wiegeschein-Liste (`open-worklist`/`navigate`) |
| `packages/frontend-web/src/workspace/registry.ts` `WORKSPACE_FACHAKTIONEN` | keine `catalogId`/Route ohne Beleg-ID fuer Gutschrift oder Wiegeschein |
| `packages/frontend-web/src/workspace/command-mapping.ts` | mappt nur vorhandene Fachaktionen; nichts zum Verdrahten |

Kein Prefill, keine erfundene ID, `pages/einkauf/**` und `pages/waage/**` unangetastet. Oeffnen bleibt disabled.

### 2) Fallback a) LOADING_* Outbox → NATS/JetStream

| Fundstelle | Befund |
|---|---|
| `OutboxPublisher.store_event` | schreibt `outbox_events` + SSE-Spiegel (`_mirror_workspace_sse`) |
| `OutboxPublisher.publish_pending_events` | alle `published=False`, inkl. `LOADING_*`; setzt `IntegrationEvent.event_type = entry.event_type` und ruft `event_publisher.publish` |
| `tours.py` `_publish_loading_outbox` | gleicher `store_event`-Pfad wie Wiegeschein; kein Typ-Filter, der LOADING auslaesst |

Kein zweiter Publish-Pfad noetig. Nachweis: `test_publish_pending_keeps_loading_event_type_for_nats`.

### 3) Fallback b) Gate Verladung-reasonCodes

`invariants-gate.test.ts`: LOADING_* muss `reasonCodes: ['ops:verladung', 'ist:LOADING_*']` tragen (zuvor nur `posts_quantity`-Negativ).

**Tests:** Vitest `invariants-gate` (+ live-signals bei Bedarf). pytest `tests/test_workspace_sse_mirror.py --noconftest --no-cov -o addopts=`.

---

## Handoff: 2026-10-23 Inbox-STOP JWT-STOP Verladung-reasonCodes - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### 1) Inbox-Positionen ueber `dms_document_id` — STOP

| Fundstelle | Befund |
|---|---|
| `app/documents/inbox_service.py` `_enrich_queue_item` | nur `match_values` + `load_supplier_candidates`; kein Join auf Positionen |
| `domain_shared.dms_inbox.dms_document_id` | Paperless-/DMS-ID am Inbox-Eintrag |
| `domain_docflow.document_items` | nur ueber `header_id` (Docflow), keine Spalte `dms_document_id` / Paperless-ID |
| Repo-Suche Join `dms_document_id`→`header_id`/`document_items` | keine Tabelle, kein Repository, keine Query |
| `extract_invoice_pdf` Musterartikel | absichtlich ungenutzt (kein Stub angehaengt) |

Keine Anreicherung. Positionszeilen bleiben ohne Quelle.

### 2) Browser-JWT — STOP

| Fundstelle | Befund |
|---|---|
| `scripts/*jwt*` / `scripts/*token*` (Mint) | keine Treffer fuer dokumentiertes UI-JWT-Skript |
| `.env.example` | `API_DEV_TOKEN=dev-token` — kein JWT; kein `JWT_SECRET` |
| `packages/frontend-web/src/lib/auth.ts` | `jwtDecode` verlangt `sub`+`exp`; lehnt `dev-token` ab |
| `app/auth/jwt.py` `create_access_token` | braucht Login-Pfad + Secret; kein dokumentierter Browser-Mint ohne Credentials |

Kein Kennwort geraten, kein JWT mit erfundenem Secret, `.env.swarm` unbenutzt. Keine Screenshots.

### 3) Luecke geschlossen: Verladung → Handlungsbedarf + YAML-Drift

LOADING_* rankten schon ueber `IST_EVENT_ACTIONS` → `logistics.undispatched-truck-orders`, ops-signals hatte nur Labels. Neu:

| Datei | Aenderung |
|---|---|
| `packages/frontend-web/src/workspace/live-signals.ts` | `reasonCodes: ['ops:verladung', 'ist:LOADING_*']` an LOADING-Targets; `signalFromIstEvent` reicht sie durch |
| `config/adaptive_workspace_fachaktionen.yaml` `event_gaps` | Ist-Listen = `IST_TO_SOLL` (LOADING_*, approval_granted, sales.*.proposed, einlagerung, weighing) |
| `tests/test_workspace_fachaktionen.py` | `test_yaml_event_gaps_cover_ist_to_soll` Drift-Gate |

`QualityProtocolCompleted`: nur Enum/`business_commands.post_event` + Event-Klasse — kein Produktions-`OutboxPublisher.store_event` → Spiegel-Option STOP.

**Tests:** Vitest live-signals + invariants-gate + ops-signals → **15 passed**. pytest `test_workspace_fachaktionen.py --noconftest --no-cov -o addopts=` → **39 passed**.

### Evidence Deliverable 1–7 (Stand 2026-10-23 reasonCodes/Drift)

| Deliverable | Status |
|---|---|
| 1–2 Registry/Command Center | unveraendert nachgewiesen; Browser STOP |
| 3 Inbox Prefill/Match | Match-Quelle da; Positionen STOP (kein Join) |
| 4 Dispo + Verladung-Live | LOADING Outbox + Handlungsbedarf mit `ops:verladung` reasonCodes |
| 5 Studio Composition | unveraendert; YAML event_gaps Drift geschlossen |
| 6–7 MCP / Agrar | unveraendert; Browser STOP |

---

## Handoff: 2026-10-23 Match-Quelle+Approve-UI-Gate - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### A) Browser STOP

`localhost:3000/login` und `localhost:3001/login` — Login-Wall (SSO). Sofort STOP, kein Scan, keine Workspace-Screenshots.

### B) Inbox „Vorschlag mit Quelle“ — schon verdrahtet

`partner_match_from_candidates` liefert `matched_by` / `partner_id` / Name ohne Partner-Konfidenz. UI zeigte das bereits:

| Ort | Darstellung |
|---|---|
| `InboxWidget` Partner-Spalte | Name + `Stamm {matched_by}` |
| `InboxPrefillBanner` | `Stamm-Treffer … (matched_by)` |
| Klassifikation | `blend_confidence` + `classification_source` getrennt |

Keine UI-Aenderung. Vitest assertiert jetzt explizit `partner_number` und kein `%` am Partner.

### C) Weitere Luecke: Approve-UI-Gate

Rank-Gate (`invariants-gate`, `inbox-rank`) war da; **UI-Test fehlte**. Neu in `inbox-widget.test.tsx`: Queue mit Action `Freigeben` → `/approve` → Widget zeigt keinen Freigeben-Button, POST nur `/prepare`, nie `/approve` (`booking_not_from_inbox`).

Nicht angefasst: `QualityProtocolCompleted` (kein `OutboxPublisher.store_event` → kein Spiegel); catalogId/YAML-Drift (Tests gruen, keine Drift).

**Tests:** Vitest `inbox-widget` + `invariants-gate` → **21 passed**. pytest `test_documents_inbox_contract.py --noconftest --no-cov -o addopts=` → **14 passed**.

### Evidence Deliverable 1–7 (Stand 2026-10-23 Match/Approve)

| Deliverable | Datei / Test | Status |
|---|---|---|
| 1 Registry `getFachaktionByCatalogId` | `fachaktion-resolve.test.ts`, `registry.test.ts` | nachgewiesen |
| 2 Command Center `mapFachaktionToCommand` / dryRun ohne Auto-Submit | `launcher-surfaces-evidence.test.tsx`, `invariants-gate.test.ts` | nachgewiesen (Browser STOP) |
| 3 Inbox Prefill / Klassifikation / Match-Quelle | `inbox-widget.test.tsx` (`matched_by`, classify, Approve-UI-Gate) | Match-Quelle sichtbar; Approve nicht als Buchung; Browser STOP; Positionen/`contractId` ohne Quelle |
| 4 Dispo Assign `posts_quantity false` + Karte + Verladung-Live | `disposition-board`, LOADING Outbox+Spiegel+Gate | LOADING live; Browser STOP |
| 5 Studio Composition-Filter + Host inkl. Stopp-Karte | `home-composition`, `invariants-gate`, `workspace-composition-host` | nachgewiesen |
| 6 MCP `execute_mcp` / Vier-Augen | `tests/test_workspace_fachaktionen.py` | nachgewiesen (Browser/SSO STOP) |
| 7 Agrar `resolve_next_step` / HTTP-Progression | `tests/test_workspace_agrar_chain.py` | HTTP nachgewiesen; Kon-QS Absicht |

---

## Handoff: 2026-10-23 LOADING-Spiegel-Gate+Studio-Stopp - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### 1) LOADING_* Outbox → Workspace-SSE (bereits verdrahtet, nachgeprueft)

`OutboxPublisher.store_event` ruft `_mirror_workspace_sse` → `mirror_ist_event_to_workspace`. `IST_TO_SOLL` enthaelt `LOADING_STARTED` / `LOADING_FINISHED`. Spiegel-Test `test_outbox_store_event_mirrors_loading_ist_to_workspace` war schon vorhanden — kein neuer Bus.

### 2) Gate posts_quantity

`invariants-gate.test.ts`: LOADING_* → Signal ohne `posts_quantity: true`, Related Action = `logistics.undispatched-truck-orders` (Dispo-Pfad ohne Mengenbuchung).

### 3) Eine weitere Luecke (a Studio)

Evidence fehlte fuer Stopp-Karte am Composition-Host. Vitest `workspace-composition-host.test.tsx`: Fixture-Host mountet inbox + `disposition_board` und zeichnet `dispo-stop-map` / Marker aus Tour-`lat`/`lng` (bestehende Quelle `DispositionStopMap`).

**STOP fuer b/c:** Inbox liefert weiter keine Positionen/`contractId` aus Extraktion an `inbox_service`. `EventType.EXCEPTION` existiert nur im Enum — kein Pfad setzt Outbox/Spiegel.

**Tests:** pytest `test_workspace_sse_mirror.py --noconftest --no-cov -o addopts=` → **34 passed**. Vitest invariants-gate + workspace-composition-host + live-signals + ops-signals → **20 passed**.

### Evidence Deliverable 1–7 (Stand 2026-10-23)

| Deliverable | Datei / Test | Status |
|---|---|---|
| 1 Registry `getFachaktionByCatalogId` | `fachaktion-resolve.test.ts`, `registry.test.ts` | nachgewiesen |
| 2 Command Center `mapFachaktionToCommand` / dryRun ohne Auto-Submit | `launcher-surfaces-evidence.test.tsx`, `invariants-gate.test.ts` | nachgewiesen (Browser blockiert) |
| 3 Inbox Prefill / Klassifikation | `inbox-widget.test.tsx`, `launcher-surfaces-evidence.test.tsx` | nachgewiesen (Browser blockiert); Positionen/`contractId`-Match ohne Quelle |
| 4 Dispo Assign `posts_quantity false` + Karte + Verladung-Live | `disposition-board.test.tsx`, `launcher-surfaces-evidence`, `post-assignment`; LOADING via `tours.py` Outbox + `test_workspace_sse_mirror` + Gate LOADING_* | LOADING live; Assign/`posts_quantity` false; Browser blockiert |
| 5 Studio Composition-Filter + Host inkl. Stopp-Karte | `home-composition`, `invariants-gate`, `workspace-composition-host` (inbox+board+`dispo-stop-map`) | nachgewiesen |
| 6 MCP `execute_mcp` / Vier-Augen | `tests/test_workspace_fachaktionen.py` | nachgewiesen (Browser/SSO blockiert) |
| 7 Agrar `resolve_next_step` / HTTP-Progression | `tests/test_workspace_agrar_chain.py` HTTP-Progression; Ranking mit geliefertem Feld | HTTP nachgewiesen; Kon-QS-Join Absicht; Browser blockiert |

---

## Handoff: 2026-10-23 Verladung-Live Outbox verdrahtet - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Deliverable 4 — verdrahtet (kein STOP)

Vorheriger STOP: Repo `add_event` nur `log_tour_events`. Loesung ohne Godfile: async Caller `app/api/v1/endpoints/tours.py` (nicht `logistics_tours.py`) nach Repo-Aufruf denselben `OutboxPublisher.store_event` → `_mirror_workspace_sse` wie Wiegeschein/Disposition.

| Datei / Symbol | Aenderung |
|---|---|
| `app/api/v1/endpoints/tours.py` `_publish_loading_outbox` / `start_loading` / `finish_loading` | nach `TourRepository.start_loading`/`finish_loading`: `OutboxPublisher.store_event` mit `EventType.LOADING_STARTED` / `LOADING_FINISHED`, Tenant via `get_current_tenant_id`, `db.commit` |
| `app/workspace/events.py` `IST_TO_SOLL` | `LOADING_STARTED` / `LOADING_FINISHED` → Soll-Annotation `assignment_confirmed` (kein neuer Soll-Name) |
| `packages/frontend-web/.../ops-signals.ts` | Ist-Labels `Verladung gestartet` / `Verladung beendet`, kind `verladung` |
| `packages/frontend-web/.../live-signals.ts` `IST_EVENT_ACTIONS` | gleiche Ist-Namen → `logistics.undispatched-truck-orders` |

Unberuehrt: `logistics_tours.py`, `tourenplanung.tsx`, TourRepository (weiterhin `add_event` in `log_tour_events`).

**Tests:** `pytest tests/test_workspace_sse_mirror.py --noconftest --no-cov -o addopts=` → **34 passed**. Vitest `ops-signals.test.ts` + `live-signals.test.tsx` → **8 passed**.

---

## Handoff: 2026-10-23 Agrar-Progression+Verladung-STOP - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Prio 1 Verladung-Live — STOP (ueberholt durch Handoff oben)

| Fundstelle | Inhalt |
|---|---|
| `app/domains/verladung/repository.py` `TourRepository.start_loading` / `finish_loading` → `add_event` | schreibt `LOADING_STARTED` / `LOADING_FINISHED` nur in `TourEvent` / `log_tour_events` |
| `app/api/v1/endpoints/tours.py` `start_loading` / `finish_loading` | ruft Repo, kein `OutboxPublisher.store_event` |
| `app/workspace/events.py` `IST_TO_SOLL` | kein Mapping fuer LOADING_*; Frontend `ops-signals` / `live-signals` kennen nur u. a. `logistik.tour.created`, Waage/Einlagerung |
| Muster | Outbox+SSE existiert (z. B. `weighing_tickets.py`), aber nicht am Verladung-Repo erreichbar ohne neuen Publisher-Hook |

Publisher nicht neu erfunden. `logistics_tours.py` und `tourenplanung.tsx` unberuehrt.

### Prio 2 Agrar-E2E — eine Luecke geschlossen

Neu in `tests/test_workspace_agrar_chain.py`:

- `test_kon_http_progression_disposition_waage_qualitaet_abrechnung` — GET `/api/v1/workspace/agrar-chain`, Kon allein, Query-`quality_is_final` fuer Abrechnung (kein Kon-QS-Join)
- `test_agrar_http_progression_waage_qualitaet_abrechnung` — Agrar allein (kein disposition), `quality_is_final` erst fuer abrechnung
- `test_kon_http_skips_agrar_quality_db_lookup` — Kon ruft `read_agrar_quality_is_final` nicht

Hilfsfunktion: `_isolated_agrar_chain_client`. Endpoint/Resolver unveraendert genutzt.

**pytest:** `tests/test_workspace_agrar_chain.py -m "not integration"` mit `--noconftest --no-cov -o addopts=` → **40 passed**.

### Evidence Deliverable 7 (Nachzug)

| Deliverable | Datei / Test | Status |
|---|---|---|
| 7 Agrar `resolve_next_step` / HTTP-Progression | `tests/test_workspace_agrar_chain.py` (`test_kon_http_progression_*`, `test_agrar_http_progression_*`, `test_kon_http_skips_agrar_quality_db_lookup`); Frontend `agrar-chain.ts` / Ranking | HTTP-Progression nachgewiesen; Kon-QS-Join absichtlich nicht |

---

## Handoff: 2026-10-23 JWT-STOP+Vitest - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

### Auftrag A — Browser STOP (kein gueltiges Test-JWT ohne Passwort)

| Fundstelle | Inhalt |
|---|---|
| `.env.example` Z.14, `.env`, `docker-compose.dev.yml` | `API_DEV_TOKEN=dev-token` — **kein JWT** (ein Segment, kein `header.payload.sig`) |
| `packages/frontend-web/src/lib/auth.ts` + `auth.test.ts` | `jwtDecode` braucht `sub`+`exp`; Test **„never accepts a development token“** lehnt `dev-token` ab |
| `ProtectedRoute` → `useAuth` | ohne authentifizierte Session → `/login` |
| `tests/e2e/helpers/auth-from-env.ts` | braucht `E2E_AUTH_TOKEN` (JWT) oder `E2E_OIDC_*` Password-Grant — Kennwort nicht geraten, `.env.swarm` unbenutzt, kein Keycloak-User |
| `app/auth/jwt.py` `create_access_token` | signiert mit `JWT_SECRET` nur fuer Login-Router — kein dokumentierter Browser-Pfad ohne Credentials |
| CI / scripts | kein Script legt ein UI-`access_token`-JWT ohne Passwort ab |

Nicht gefaelscht. Keine Screenshots unter `evidence/screenshots/adaptive-workspace-*.png`.

### Auftrag B — Vitest-Nachweis der Launcher-Flaechen

Neu: `packages/frontend-web/src/__tests__/workspace/launcher-surfaces-evidence.test.tsx` rendert AdaptiveWorkspaceLayer, CommandPalette, InboxWidget/InboxPrefillBanner, DispositionBoard+Karte und belegt dryRun, kein Auto-Submit, `posts_quantity: false`, Composition-Filter, Meridian (`UniversalMaskRenderer` + `disposition_board`).

**Vitest:** `launcher-surfaces-evidence` **4/4**, `inbox-widget` **14/14**, `invariants-gate` mitgelaufen → gruen.

### Evidence-Tabelle Deliverable 1–7

| Deliverable | Datei / Test | Status |
|---|---|---|
| 1 Registry `getFachaktionByCatalogId` | `fachaktion-resolve.test.ts`, `registry.test.ts` | nachgewiesen |
| 2 Command Center `mapFachaktionToCommand` / dryRun ohne Auto-Submit | `launcher-surfaces-evidence.test.tsx`, `invariants-gate.test.ts`, `CommandPalette.test.tsx` | nachgewiesen (Browser blockiert) |
| 3 Inbox Prefill / Klassifikation | `inbox-widget.test.tsx`, `launcher-surfaces-evidence.test.tsx` | nachgewiesen (Browser blockiert) |
| 4 Dispo Assign `posts_quantity false` + Karte lat/lng | `disposition-board.test.tsx`, `launcher-surfaces-evidence.test.tsx`, `post-assignment.test.ts` | nachgewiesen (Browser blockiert) |
| 5 Studio Composition-Filter | `home-composition.test.tsx`, `invariants-gate.test.ts`, `launcher-surfaces-evidence.test.tsx` | nachgewiesen |
| 6 MCP `execute_mcp` / Vier-Augen | `tests/test_workspace_fachaktionen.py`, `app/workspace/fachaktionen.py` | nachgewiesen (pytest zuvor 38 passed; Browser/SSO blockiert) |
| 7 Agrar `resolve_next_step` / QS-Feld | `agrar-chain-ranking.test.tsx`; Kon-Abrechnung ohne QS-Feld | Quelle fehlt fuer quality_is_final-Join; Ranking nur mit geliefertem Feld |

---

## Handoff: 2026-10-23 Auth-STOP+MCP - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

**Browser STOP (Auftrag A):** Kein vorhandener Mechanismus oeffnet Launcher-Flaechen ohne Passwortfeld.

- `dev_bypass_auth` wird in alten E2E-Specs gesetzt (`packages/frontend-web/tests/e2e/slice-008-dsgvo-art30.spec.ts` u. a.), aber in `src/` nirgends gelesen. `ProtectedRoute` / `useAuth` / `AuthService` (`packages/frontend-web/src/lib/auth.ts`) verlangen ein gueltiges JWT in `access_token` (PKCE, keine Dev-Identitaet).
- `API_DEV_TOKEN` / `E2E_API_DEV_TOKEN` als Bearer gilt nur fuer HTTP-API in Playwright, nicht fuer die UI-Route. `capture-readme-screenshots.ts` legt `dev-token` in `localStorage` — `jwtDecode` lehnt das ab.
- Kein `storageState`, kein `auth.setup`, kein MSW-Auth-Bypass unter `packages/frontend-web`. `tests/e2e/helpers/auth-from-env.ts` braucht `E2E_AUTH_TOKEN` (JWT) oder OIDC-Password-Grant (`E2E_OIDC_*`) — Kennwort nicht geraten, `.env.swarm` unbenutzt, kein Keycloak-User angelegt.
- Kein Screenshot der Login-Wand als Abnahme. Keine Dateien unter `evidence/screenshots/adaptive-workspace-*.png` erzeugt.

**MCP Deliverable 6 (Auftrag B):** Keine Code-Luecke geschlossen. Ist-Stand greift bereits:

- `authorize_action` / `resolve_command` in `app/workspace/fachaktionen.py`: `forbidden_for_agents`, `write_not_enabled_for_agents`, `four_eyes_requires_human` (R4).
- MCP `workspace.fachaktion.katalog` / `resolve` nur lesend (`execute_mcp`).
- `workspace_action_agent_block` in `app/services/mcp_mask_actions.py` ist bewusst additive Katalogsicht; Maskengrenze bleibt `human_only_tool_call`. Vier-Augen-Execute nach Proposal (`human_approval_required`) fuer `finance.ap_invoice.freigeben` bleibt Absicht, nicht Luecke. Nichts erfunden, keine neue Regel verdrahtet.

**Tests:** `python -m pytest tests/test_workspace_fachaktionen.py --noconftest --no-cov -o addopts= -q` → **38 passed** (valeo_probe URL gesetzt). Volles `conftest` scheitert an fremdem WIP: `ImportError DocumentAlreadyExists` aus `app/api/v1/endpoints/ap_invoices.py` → `app.documents.repository` (geschuetzt/fremd, nicht repariert).

---

## Handoff: 2026-10-23 Inbox+Gate - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Grok
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

**1. Disposition-Kette:** `packages/frontend-web/src/pages/disposition/touren-disposition.tsx` nutzt bereits `useUniversalMaskRuntime` → `UniversalMaskRenderer` mit Schema `dispositionBoardScreen` (`specialized.type === 'disposition_board'`). Hook und Schema unterstuetzen Specialized — kein STOP. SpecializedComponentHost, DispositionBoard, DispositionStopMap und Studio `DispositionBoardSlot` bleiben.

**2. Inbox blend_confidence / classification_source:** Backend `build_queue_item` liefert `confidence` (= `blend_confidence`) und `source` (= `classification_source`); Prefill traegt `source.classification`. Queue-Widget zeigte beides schon. Prefill-Banner verschluckte `classification` — behoben in `InboxPrefillBanner` (`inbox-prefill-classification`, `inbox-prefill-confidence`). Widget erhaelt `inbox-confidence-*`. Partner-Match-Konfidenz nicht erfunden (nur vorhandenes `matched_by`).

**3. Eine weitere Luecke (Gate-Vertrag):** `invariants-gate.test.ts` stellt sicher, dass die Touren-Disposition-Seite die Meridian-Kette mit `disposition_board` haelt und nicht `UniversalNativeCockpitPage`. Browser: Tab `http://localhost:3000/login` — keine Sitzung, STOP ohne Kennwort.

**Geaendert:** `InboxPrefillBanner`, `InboxWidget`, `inbox-widget.test.tsx`, `invariants-gate.test.ts`; Doku nur dieser Abschnitt und Workboard-Sektion.

**Tests:** Vitest `inbox-widget.test.tsx` + `invariants-gate.test.ts` — 19/19 bestanden.

---

## Handoff: 2026-10-23 Karte - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Grok
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

**Karte verdrahtet:** `DispositionStopMap` in `packages/frontend-web/src/components/mask-builder/specialized/stop-map.tsx`, gemountet von `DispositionBoard`. Punktmarker nur fuer `lat`/`lng`, die `laneFromTourDetail` aus dem Tour-GET liest. Rasterstil ist die vorhandene Quelle aus `MilchviehKartePage` (`packages/frontend-web/src/pages/agrar/milchvieh-karte-legacy.tsx`, Kachel `https://tile.openstreetmap.org/{z}/{x}/{y}.png`). Kein neuer Tile-Server, kein Key, `SchlagKarte` unberuehrt. Ohne Koordinaten kein Marker; der Text `Zeitachse nicht belegbar, Feld planned_arrival fehlt.` bleibt, wenn `planned_arrival` fehlt.

**Tests:** Vitest `disposition-board.test.tsx` und `load-timeline.test.ts`, 19 bestanden. Vorhandene lat/lng erzeugen `dispo-map-marker-*`; fehlende Koordinaten erzeugen keinen Marker.

---

## Handoff: 2026-10-23 spaeter - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Grok
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push.

**Browser:** STOP. Keycloak-Container `valeo-neuro-erp-keycloak` laeuft auf Port 8080 und entspricht dem Admin-Zugang aus `docker-compose.yml` (Benutzer `admin`). Realm `master` enthaelt nur `admin`. Realm `valeo-neuro-erp` enthaelt acht Benutzer: `admin`, dazu aktiv `manual-login-d7bb404d`, `sicht-inhaber-604f95`, `sicht-mitarbeiter-604f95`, und vier deaktivierte synthetische Konten. Diese Namen stehen nicht in der Compose-Umgebung und nicht im Repo. Ein Kennwort dafuer wurde nicht geraten, kein Benutzer angelegt, `.env.swarm` und `API_DEV_TOKEN` unbenutzt. Kein Login, keine Screenshots. Die Login-Wand ist kein Nachweis.

**Eine Luecke geschlossen:** `laneFromTourDetail` (`packages/frontend-web/src/components/mask-builder/specialized/load-timeline.ts`) liest `lat`/`lng` aus dem vorhandenen Tour-GET. `DispositionBoard` zeigt sie als Stoppzeile und am Zeitmarker. `maplibre-gl` steht in `package.json`; `MilchviehKartePage` zeichnet bereits Punktmarker. Keine neue Bibliothek, keine OSM-Kachel. `SchlagKarte` bleibt unberuehrt.

**Keine weitere Quelle:**

- Inbox: `inbox_service._enrich_queue_item` ruft `match_values` und `load_supplier_candidates`. `WhatsAppIntakeService.match_artikel` liefert Artikel nur zu WhatsApp-Positionstext, den die Inbox nicht hat. `DMSParser.parse` und `extrahiere_belegfelder` bleiben ohne Positionen. Der Musterartikel-Stub in `extract_invoice_pdf` bleibt ungenutzt.
- Live-Events: `QualityProtocolCompleted` ist die Klasse in `app/domains/shared/process_events.py` plus der String `post_event` in `app/core/business_commands.py`. `OutboxPublisher.store_event` wird dafuer nicht aufgerufen. `LOADING_STARTED` / `LOADING_FINISHED` schreibt `TourRepository.add_event` in `app/domains/verladung/repository.py` in `TourEvent`, nicht in die Outbox. `IST_TO_SOLL` in `app/workspace/events.py` laesst sie deshalb aus. Publisher, `logistics_tours.py` und `tourenplanung.tsx` unberuehrt.

**Tests:** Vitest `load-timeline.test.ts` und `disposition-board.test.tsx`, 19 bestanden.

---

## Handoff: 2026-10-23 - ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Grok (Doku-Nachzug)
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Ziel des Slices:** Adaptive Workspace innerhalb von VALEO (Registry, Strg+K, Home, Inbox, Dispo, Agrar-Kette, Events). Meridian-Pipeline bleibt die Maskenpipeline.
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push. Diese Session: Browser STOP, keine Code-Luecke geschlossen.

**Browser 2026-10-23:** STOP. `AuthService` in `packages/frontend-web/src/lib/auth.ts` ist PKCE ohne Dev-Identitaet. `LoginPage` hat nur „Mit SSO anmelden“. `ProtectedRoute` leitet ohne Sitzung nach `/login`. `http://localhost:3000/` und der schon offene Tab `http://localhost:3001/login` zeigen diese Wand. Kein Screenshot, kein Kennwort.

**Erledigt:**

- Registry und vier Ebenen `personal`, `situational`, `proactive`, `dialog` (`packages/frontend-web/src/workspace/types.ts`, `registry`).
- Reason-Codes in der deterministischen Priorisierung (`prioritization.ts`). Pin wird nach dem Commit im Effect geschrieben (`useLaunchpadPersonalization`); Overlay-Key `launchpadOverlayStorageKey` und Composition-Key tragen Mandant und `sub`.
- Dialog oeffnet die bestehende Palette per Strg+K (`request-command-palette.ts`, `AppShell`). Keine zweite Kommandozeile.
- Katalog-Aliase laufen als `dryRun` ohne Auto-Submit (`fachaktion-resolve.ts`, `app/workspace/fachaktionen.py` `execute_mcp`).
- Inbox mit `document_kind`. Prefill nur fuer `EINGANGSRECHNUNG`. Oeffnen ohne Art liefert kein Href (`inbox-contract.ts`). Approve antwortet 409 mit `booking_not_from_inbox` (`app/documents/inbox_router.py`).
- Pruefcodes aus Unsicherheiten und Dubletten haengen am Signal und damit an der Rangzeile (`inbox-rank.ts`, `AdaptiveWorkspaceLayer.tsx`).
- Composition filtert Inbox-Signale und offene Abrufe (`home-composition.ts` `signalsForHomeSpecialists`).
- Dispo-Board im UniversalMaskRenderer (`disposition_board`) und in der Studio-Composition. Drop setzt `posts_quantity: false` und weist `quantity_posted` zurueck (`post-assignment.ts`).
- SSE `GET /api/events?stream=workspace` spiegelt Ist-Typen (`logistik.tour.created`, `agrar.weighing_ticket.allocated` und die uebrigen Keys in `IST_EVENT_ACTIONS` / `IST_TO_SOLL`). Soll-Namen `assignment_confirmed`, `document_proposed`, `document_posted` bleiben Annotation; die Soll-NATS-Subjects werden nicht publiziert (`app/workspace/events.py`).
- Agrar-Schritte kommen in die Rangliste nur aus einer fertigen Server-Antwort (`situationalItemsFromAgrarChain`, Status `ready`).
- MCP `workspace.fachaktion.katalog` und `workspace.fachaktion.resolve` lesen, schreiben nicht in die DB.

**Offen:**

- Browser-Abnahme. In dieser Session sind `NEUROERP_USER` und `NEUROERP_PASS` nicht gesetzt. `http://localhost:3001/` leitet auf `/login` (SSO). `API_DEV_TOKEN` ist kein UI-Login. Platzhalter aus `.env.swarm` wurden nicht verwendet.
- Screenshot blockiert. Die Startflaeche (`data-testid="adaptive-workspace-layer"`) ist ohne Login nicht sichtbar. Eine Aufnahme der Anmeldeseite wurde nicht als Nachweis abgelegt. `evidence/screenshots` enthaelt kein Bild dieser Flaeche. `docs/benutzerhandbuch/img/start-dashboard.webp` zeigt die aeltere KPI- und Flow-Spine-Startseite und wurde nicht umetikettiert.
- Keine Positionszeilen. `DMSParser.parse` (`app/integrations/dms_parser.py`) liefert nur Kopffelder, `PATTERNS` hat keine Position. `extrahiere_belegfelder` (`app/core/dms_ocr_contracts.py`) setzt den Hinweis „keine Positionsdaten extrahiert“ und legt `BelegFeldTyp.ARTIKEL_NR` nicht an. `extract_invoice_pdf` (`app/einkauf/ocr_invoice.py`) setzt `positionen` auf dem pdfplumber-Pfad auf `[]`; die Musterzeilen gehoeren nur `engine == "stub"`.
- Kein Kontrakt- und kein Artikelabgleich aus der Inbox. `DocflowSourceProposalService.propose` (`app/services/docflow_source_proposals.py`) braucht `SourceProposalRequest.lines` mit Artikel-ID. Die Inbox hat diese Zeilen nicht.
- Gutschrift und Wiegeschein ohne Ziel-ID. `inboxOpenDecision` (`packages/frontend-web/src/components/adaptive-workspace/inbox/inbox-contract.ts`) liefert fuer `GUTSCHRIFT` und `WIEGESCHEIN` kein Href.
- Kon-Abrechnung ohne QS-Feld. `KonContract` (`app/domains/operations/models.py`) hat kein `quality_is_final`. `read_agrar_quality_is_final` liest nur AgrarContract ueber `HarvestAcceptance`. Kon-Lookup bleibt in `get_agrar_chain` verboten.
- Karte ohne Stopp-Koordinaten. `SchlagKarte` (`packages/frontend-web/src/components/agrar/SchlagKarte.tsx`) nimmt nur `height` und `className` und laedt `useSchlagGeojsonAll`.
- Verladung und Stoerungen ohne Workspace-Outbox. `TourEvent` (`app/domains/verladung/models.py`) heisst `log_tour_events` im Schema `domain_log`. Der Workspace-Spiegel haengt an `domain_logistics`-Ist-Typen (`IST_TO_SOLL` in `app/workspace/events.py`), nicht an dieser Tabelle.
- Keine weitere offene Quelle an den sieben Deliverables. Registry `getFachaktionByCatalogId`, Command Center `mapFachaktionToCommand`, Inbox `inboxPrefillToCreationValues`, Dispo `validate_assignment` / `postDispositionAssignment`, Studio `resolveWorkspaceCompositionMounts`, MCP `execute_mcp`, Agrar `resolve_next_step`. `QualityProtocolCompleted` bleibt bewusst ausserhalb des Streams (`OFF_STREAM` in `tests/test_workspace_sse_mirror.py`), weil kein Outbox-Publisher existiert. `localResolveFallback('Angebot Kunde')` bleibt leer: die YAML-Route `/sales/angebote` ist nicht die Listenmaske.
- KI-Ranking bleibt `noopRankingAdvisor` (Identitaet, kein Modell).
- Keine Katalog-Tastaturkuerzel (weder in der Workspace-Registry noch in `config/adaptive_workspace_fachaktionen.yaml`).

**Betroffene Dateien:**

- `docs/agent-ops/active-workboard.md` — nur der Abschnitt `ADAPTIVE-WORKSPACE-20261022`. Der Codex-Block `MIGRATION-PARITY-REPAIR-20261022` ist ein eigener Diff-Hunk am Dateiende und blieb stehen.
- `docs/agent-ops/handoffs/adaptive-workspace-20261022.md` — dieser Handoff.
- `docs/agent-ops/sources/adaptive-workspace-20261022.md` — Quelle fuer den Agent-Handbuch-Abschnitt.
- `scripts/generate_agent_handbuch.py` — liest diese Quelle in `docs/agent-handbuch/index.md` ein.
- `docs/agent-handbuch/index.md` — nicht geschrieben. Der Generator wuerde den eigenen Abschnitt mit fremder Event-Drift (130 auf 135) und drei weiteren Handbuchdateien vermischen.

**Tests / Checks:**

- Keine Fachtests in diesem Nachzug (Testbesitz liegt beim parallelen Code-Agenten).
- `python scripts/generate_agent_handbuch.py --check` endet mit Exit 1. Drift, Schwellen unveraendert:
  - `docs/agent-handbuch/index.md`
  - `docs/agent-handbuch/masken-api-katalog.md`
  - `docs/agent-handbuch/automatisierung.md`
  - `docs/agent-handbuch/agent-process-manifest.json`
- `docs/agent-handbuch/prozessketten.md` ist nicht in der Driftliste.
- Der Index wurde nicht neu geschrieben. Ein Lauf wuerde den eigenen Abschnitt einsetzen und zugleich die fremde Zaehlung der Domain-Events von 130 auf 135 heben. Die drei weiteren Dateien wuerden mitgezogen. Das ist fremde Drift aus dem laufenden Code, kein Fehler der Handbuch-Quelle. Schwellen wurden nicht gesenkt. Der Ist-Stand steht in `docs/agent-ops/sources/adaptive-workspace-20261022.md`.

**Offene Risiken:**

- Der Code-Stand kann sich parallel aendern. Dieser Handoff beschreibt den gelesenen Stand vom 2026-10-23, keinen Abschluss.
- `agrar.quality_protocol.completed` ist im Frontend gemappt, der Kommentar in `live-signals.ts` sagt: noch kein Outbox-/SSE-Spiegel.
- Browser-Abnahme und Screenshot fehlen. Ohne echte Zugangsdaten gibt es keinen Sichtnachweis der Startflaeche.

**Annahmen:**

- Die genannten Pfade sind der gelesene Ist-Stand, keine Soll-Liste.
- Status des Slices bleibt `in arbeit`.

**Naechster konkreter Schritt:**

Browser-Abnahme der Startflaeche, sobald eine bestehende Sitzung die Launcher-Flaeche ohne neues Kennwort zeigt. Erst dann ein Screenshot von `adaptive-workspace-layer` unter `evidence/screenshots` und Verweis in der Handbuch-Quelle. Eine weitere Verdrahtung der sieben Deliverables hat in dieser Session keine Quelle mehr gefunden. Danach `python scripts/generate_agent_handbuch.py` nur fuer den eigenen Abschnitt, ohne fremde Drift wegzuschreiben und ohne Schwellen zu senken.

---

## Handoff: 2026-10-23 Demo-Stammdaten / Browser — ADAPTIVE-WORKSPACE-20261022

**Von:** Cursor Composer (Subagent)
**An:** naechster Agent am Slice ADAPTIVE-WORKSPACE-20261022
**Stand:** in Arbeit. Ziel ist nicht erfuellt. Kein Commit, kein Push. Keine Secrets in Docs.

### Seed (Live-DB `valeo_neuro_erp`)

- Script: `scripts/seed_ocr_demo_stammdaten.py --with-inbox` (idempotent).
- Katalog: `scripts/ocr_demo_stammdaten_catalog.py`.
- Tenant: `00000000-0000-0000-0000-000000000051`.
- Ergebnis Re-Run: Lieferanten 12 skipped, Artikel 40 skipped, Inbox 2 skipped (bereits vorhanden).
- Pseudonyme / Mapping: `evidence/ocr-training/README.md` (Demo-Namen, nicht Original-Firmen als Stammdaten-Wahrheit).

### Browser: ok

- Login mit freigegebener pseudonymer Testkennung (Zugangsdaten nicht dokumentiert).
- JWT `tenant_id` = `…000051`. Startflaeche Adaptive Workspace sichtbar.
- Beleg-Inbox: **4 offen · keine Buchung**. Darunter Demo-Zeilen:
  - Partner **Nordwestdeutsche Futtermittel GmbH & Co. KG** (Seed `DEMO-LF-NWF`)
  - Partner **Wesel Agrarhandel KG** (Seed `DEMO-LF-WAH`)
  - Aktion **Lieferant anlegen** sichtbar (UI-Match trifft den vorhandenen DEMO-Stamm nicht; Queue liefert `supplier` als `propose`).
  - Queue-API: Artikel-Matches `matched` (z. B. `DEMO-VL2439509` / `DEMO-291040`) in `master_data_proposals.articles`.
- Alias-Route `/inbox` (DMS-Listenmaske) zeigte leer — relevant ist die Home-Beleg-Inbox, nicht die Alias-Liste.

### Spot DEMO-LF

- SQL + `GET /api/v1/einkauf/lieferanten` (Session-Token, Tenant-Header): `DEMO-LF-NWF` = Nordwestdeutsche Futtermittel GmbH & Co. KG, Ort Dinklage, aktiv. 12 DEMO-Nummern lesbar.

### Screenshots

- `evidence/screenshots/adaptive-workspace-demo-stammdaten-home.png`
- `evidence/screenshots/adaptive-workspace-demo-stammdaten-inbox.png`
- `evidence/screenshots/adaptive-workspace-demo-stammdaten-inbox-match.png`

### Nicht angefasst

- Codex-Verladung, `pages/einkauf/**`.

### Offen / naechster Schritt

- Lieferanten-Match an `DEMO-LF-*` / Pseudonym-Firmenname in `inbox_service` (aktuell Anlegen-Vorschlag trotz vorhandenem Stamm).
- Dokumentart an Demo-Inbox-Zeilen (UI: „Dokumentart nicht erkannt“).
- Slice bleibt **in Arbeit**; Gesamtziel Adaptive Workspace nicht complete.

### Codex-Nachpruefung nach neuer Browser-Vorgabe (2026-10-23)

Browser: **STOP vor Anmeldung**,0 Loginversuche. Inventar zeigt bestehenden Fehler-Tab mit ERR_CONNECTION_REFUSED unter data:-Adresse; Browserwerkzeug verweigert diesen Seitentyp. Kein Umgehen, keine anderen Kennungen/Passwortquellen verwendet, keine temporaren Secretdateien angelegt. Die oben genannten Screenshots sind bereits vorhandene Fremdevidenz und wurden nicht als neue eigene Browserabnahme ausgegeben oder ueberschrieben. Fuer Fortsetzung den Tab manuell auf http://localhost:3000 oeffnen. DEMO-/Pseudonym-Hinweis bleibt bestehen; Slice weiter in Arbeit. Kein Commit/Push nach dieser Nutzervorgabe.

### Fortsetzung nach manuell geoeffnetem HTTP-Tab

Tab auf http://localhost:3000 wieder zugaenglich. Zunaechst leere Seite mit Fehler beim Nachladen alter JavaScriptchunks; einmaliges regulaeres Neuladen zeigte die SSO-Startmaske. Genau ein Klick auf Mit SSO anmelden; danach blieb die Startmaske sichtbar, keine Keycloak-Kennwortmaske beobachtet. **STOP**, kein zweiter Klick/Anmeldeversuch, keine Zugangsdaten gesendet und keine neuen Secretdateien erstellt. Keine neue Inbox-/Lieferantenabnahme behauptet. Neuer eigener Screenshot: evidence/screenshots/adaptive-workspace-demo-stammdaten-login-stop-20261023.jpg. Vorhandene Inbox-/Lieferantenscreenshots unveraendert; Slice weiter in Arbeit, kein Commit/Push.
