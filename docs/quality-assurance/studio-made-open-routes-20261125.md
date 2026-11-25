---
title: Studio-made offene Routen — Hebung
type: qa-evidence
audience: [agent, entwickler, qa]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-25
description: Inventar und Create-Paritaet fuer Altmasken (Agrar, CRM, Finance).
---

# Studio-made offene Routen (2026-11-25)

## Inventar (main, `mask_route_migration_inventory.py`)

| Klasse | Anzahl |
|--------|--------|
| Routen gesamt | 1147 |
| runtime_wired | 1037 |
| legacy_wrapper (`createLegacyMaskPage`) | 35 |
| hand_built | 69 |
| legacy_mask_pattern (Routen) | 0 |
| ObjectPage/ListReport-Seiten (`*-legacy.tsx` u. a.) | 16 |

Qualitaetskatalog: [made-by-studio-qualitaetsversprechen.md](../architecture/uix/made-by-studio-qualitaetsversprechen.md).

## Erste Hebung

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/saatgut` (+ Stamm-Routen) | Detail native, Create → ObjectPage-Legacy | `creation` in SD + `createStammNativeDetailPage` ohne Legacy |
| `agrar/duenger` (+ Stamm-Routen) | wie oben | wie oben |
| `crm/lead-detail` Anlage | LeadMaskBuilder / LegacyLeadDetail | `UniversalNativeCreatePage` (`crm/lead`) |
| `finance/debitoren-stamm` | totgeladener Legacy-Import | native Detail + Capture `finance/debitoren/new` |

## Zweite Hebung (Batch 2)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `finance/bankkonto` (`bankkonten-stamm`) | Create → ObjectPage-Legacy (+ Client-IBAN-Lookup) | `creation` → POST `/api/v1/banken/konten`; IBAN-Pruefung serverseitig |
| `finance/kreditor` (`kreditoren-stamm`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/finance/creditors` (CreditorWrite-Felder) |
| `crm/opportunity` (`opportunity-detail`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/crm/opportunities/`; `tenant_id` optional im Schema |

Permission-Projektion (UI): `finance.bankkonto.*` / `finance.kreditor.*` → FINANCE_*; `crm.opportunity.*` → CRM_* / SALES_*.

## Dritte Hebung (Batch 3)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `einkauf/anfrage` (`anfrage-stamm`) | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/einkauf/anfragen` |
| `qualitaet/reklamation` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/reklamationen` (`responseIdKey=reklamation_id`, Positionen-Tabelle) |
| `crm/kontakt` (`kontakt-detail`) | ScreenId `crm/kontakte/new` + Legacy | `crm/kontakt` + POST `/api/v1/crm/contacts/` (nested `data.id`) |
| `qualitaet/labor-detail` | Legacy-ObjectPage | `creation` → POST `/api/v1/qualitaet/labor-auftraege` |
| `service/anfrage-detail`, `service/anfrage/neu` | Legacy-ObjectPage | `creation` → POST `/api/v1/service/anfragen` |
| `crm/betriebsprofil` | fehlende ScreenId + Legacy | POST `/api/v1/crm/betriebsprofile` |
| `personal/mitarbeiter/neu` | Legacy | POST `/api/v1/personal/mitarbeiter` |
| `stammdaten/betriebsstaetten` | Legacy | POST `/api/v1/stammdaten/betriebsstaetten` (`responseIdKey=filial_nr`) |
| `stammdaten/hausbanken` | Legacy | POST `/api/v1/stammdaten/hausbanken` (`responseIdKey=bank_nr`) |
| `stammdaten/mengeneinheiten` | Legacy | POST `/api/v1/artikel/mengeneinheiten/stamm` |
| `crm/vertreter` (`vertreterstamm`) | fehlende ScreenId + Legacy | POST `/api/v1/crm/vertreter` (`responseIdKey=vertreter_nr`) |
| `UniversalNativeCreatePage` | nur `response.data.id` | `responseIdKey` + Defaults ausserhalb der Formularfelder + nested `data.id` |

## Sechste Hebung (Batch 6)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `stammdaten/artikelbestandteile` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/bestandteile/stamm` (`responseIdKey=bestandteil_nr`); GET `/stamm/{nr}` |
| `stammdaten/artikelverpackung` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/verpackungen` (`responseIdKey=verpackungs_nr`) |
| `stammdaten/artikel-stoffstrom` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/stoffstrom`; GET `/{id}` |
| `stammdaten/individuelle-artikelnummern` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/artikel/individuelle-nummern` |
| `verkauf/kunde-neu`, `verkauf/kunden-stamm-enhanced` | Create → ObjectPage-Legacy | `creation` → POST `/api/v1/crm/customers/` → `/crm/customer-360/{id}` |

Permission-Projektion (UI): `stammdaten.stoffstrom|bestandteil|verpackung|indiv_artikel.*` → STAMMDATEN-Rollen; `verkauf.kunde.*` → CRM/SALES.

## Siebte Hebung (Batch 7)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `preise/individualpreise` | Legacy-ObjectPage | POST `/api/v1/preise/individualpreise` |
| `preise/rabattgruppen` | Legacy-ObjectPage | POST `/api/v1/preise/rabatte/gruppen` |
| `preise/zu-abschlaggruppen` | Legacy-ObjectPage | POST `/api/v1/kontrakte/zuabschlagsgruppen` |
| `verkauf/dauerauftraege` | Legacy-ObjectPage | POST `/api/v1/dauerauftraege` (`responseIdKey=da_nr`, Positionen-Tabelle) |
| `produktion/rezepturgruppen` | Legacy-ObjectPage | POST `/api/v1/produktion/mischfutter/rezepturgruppen` (`responseIdKey=gruppe_nr`) |

## Achte Hebung (Batch 8)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `fibu/geschaeftsjahre` | Legacy-ObjectPage | POST `/api/v1/fibu/geschaeftsjahre` (finance_admin) |
| `lager/massebilanz` | Legacy-ObjectPage | POST `/api/v1/massebilanz` |
| `lager/permanente-inventur` | Legacy-ObjectPage | POST `/api/v1/inventur/piv`; GET `/{id}` |

## Neunte Hebung (Batch 9)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `fibu/zahlungsmeldungen` | Legacy-ObjectPage | POST `/api/v1/fibu/zahlungsmeldungen` |
| `fibu/op-skonto-auszifferung` | Legacy-ObjectPage | POST `/api/v1/fibu/op-auszifferung` |
| `fibu/stammdaten` | Legacy-ObjectPage | POST `/api/v1/fibu/stammdaten/zahlungsformulare` |

## Zehnte Hebung (Batch 10)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `finance/bank-stamm` | Legacy-Factory | Alias auf `finance/bankkonto` Create |
| `agribusiness/field-service-task-neu` | Legacy + fehlende SD | neue SD + POST `/api/v1/agribusiness/field-service-tasks` |

## Elfte Hebung (Batch 11)

| Maske / Runtime | Vorher | Nachher |
|-----------------|--------|---------|
| `UniversalNativeCreatePage` | nur flaches POST | optional `payloadEnvelope` (z. B. `data`) |
| `personal/schulung-neu` | Legacy (Training `{data}`) | Native Create mit `payloadEnvelope=data` |

## Zwoelfte Hebung (Batch 12)

Ops-/Workspace-Masken vom falschen `createStammNativeDetailPage`-Factory geloest:
`admin/ai-approvals`, `admin/command-monitor`, `admin/agenten-integration` (spezialisiert),
`kontrakte/mengenzeitraeume` (pfadgebundenes Workspace).

## Dreizehnte Hebung (Batch 13)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/rohwarengruppen` | `createLegacyMaskPage` | SD + POST `/api/v1/rohware/gruppen` (`responseIdKey=gruppe_nr`); GET `/{nr}` |

## Vierzehnte Hebung (Batch 14)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `agrar/vermehrungsvertraege` | `createLegacyMaskPage` | SD + POST `/api/v1/saatzucht/vermehrungsvertraege` (`responseIdKey=vertrag_nr`) |

## Fuenfzehnte Hebung (Batch 15)

Alle verbleibenden `createLegacyMaskPage`-Wrapper (Admin-Suite, Admin-Ops, Agrar-Prozess,
Home, Konditionen, KIM-Panels) auf direkte Re-Exports umgestellt.
Inventar: `legacy_wrapper` **0** (vorher 35).

## Sechzehnte Hebung (Batch 16)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `fibu/abschluss-checklist-detail` | Factory+Legacy | POST `/api/v1/finance/closing-checklists` |

## Siebzehnte Hebung (Batch 17)

| Maske | Vorher | Nachher |
|-------|--------|---------|
| `einkauf/angebot` | Factory+Legacy (kein POST) | POST `/api/v1/einkauf/angebote` + SD `creation` |
| `einkauf/anlieferavis` | Factory+Legacy (kein POST) | POST `/api/v1/einkauf/anlieferavis` + SD `creation` |

Live `createStammNativeDetailPage` + `legacyImport`: **0**.

## Paritaets-Nachzug (Batch 17b) — verbindliche Invariante

Studio-made Masken duerfen gegenueber dem Vorgaenger **keine Funktionseinschränkung
und keine fehlenden Datenfelder** haben. Human, CI und MCP bedienen dieselben
`commandEndpoint`s (MCP-WRITE-015 / Made-by-Studio Gate C).

| Maske | Nachweis |
|-------|----------|
| `einkauf/angebot` | Legacy-Felder (Stammdaten/Angebot/Konditionen) + Aktionen pruefen/genehmigen/ablehnen/inBestellung + PUT; Test `tests/test_einkauf_studio_field_parity.py` |
| `einkauf/anlieferavis` | Legacy-Felder (Bestellung/Fahrzeug/Positionen/Bemerkungen) + senden/bestaetigen/stornieren (+ wareneingang additiv) + PUT; gleicher Test |

Inventar: `belegSeite(...)` zaehlt als `runtime_wired` (`mask_runtime_evidence`).

## Achtzehnte Hebung (Batch 18)

| Maske / Thema | Nachher |
|---------------|---------|
| `agrar/zinsabrechnung` | `NativeListPage` + SD mit Anlegen (alle Legacy-Formfelder) + buchen/stornieren/drucken |
| Kundenakte / Kontrakt-Detail | Universal-Mask Standard (Opt-out statt Opt-in) |
| Reine `<Navigate replace>`-Seiten | Inventar-Klasse `technical_page` (keine Altmasken) |

Inventar nach Batch 18: `hand_built`-Routen ~50 (Domain), `legacy_wrapper` 0.

## Neunzehnte Hebung (Batch 19) — Paritaet Human/CI/MCP

| Maske | Nachher |
|-------|---------|
| `agrar/sammelabrechnung` | `NativeListPage` + Create (alle Wizard-Felder inkl. `harvest_acceptance_ids`) + berechnen/buchen/löschen |
| `agrar/annahmen-qualitaet-nachtrag` | Worklist `missing_quality` + Zeilen-Nachtrag (`/qualitaetsprotokoll`) + Batch (`/quality-batch`, JSON-rows) |
| `kontrakte/mengenzeitraeume` | Stub-SD ersetzt: volle Aktionsmenge (Zeitraum anlegen/generieren/löschen, Gruppe, Abschlag); JSON-Body fuer `/generieren` |
| Redirects (`verkauf/kunden-stamm`, `crm/kunden-cockpit`, …) | Inventar `technical_page` via programmatisches `navigate(…, {replace:true})` |
| `NativeListPage` | Pfad-Platzhalter aus Eingabewerten (Header-Aktionen pfadgebunden) |

Inventar nach Batch 19: `runtime_wired` ~1088, `hand_built` ~38, `legacy_wrapper` 0.

## Zwanzigste Hebung (Batch 20)

| Maske / Fix | Nachher |
|-------------|---------|
| `agrar/erntefenster-konfig` | NativeListPage: Create aus Vorlage (alle Felder), Settlement-Nav, Sandbox-Nav, Backfill-Pfad-Alias |
| Inventar | `technical_page` nicht mehr in Handgebaut-Liste; Redirects sauber getrennt |

Inventar nach Batch 20: `hand_built` ~37.

## Einundzwanzigste Hebung (Batch 21)

| Maske | Nachher |
|-------|---------|
| `agrar/milchvieh-crosssell` | `UniversalNativeCockpitPage` mit KPI-Summary, Kundenliste (alle Legacy-Spalten), Produktgruppen-Tabelle; GET `/produktgruppen` |

Inventar: `hand_built` ~36.

## Zweiundzwanzigste Hebung (Batch 22)

| Maske | Nachher |
|-------|---------|
| `admin/ai-approvals` | `NativeListPage` mit Freigabe-Parität (Human/CI/MCP) |

## Dreiundzwanzigste Hebung (Batch 23)

| Maske | Nachher |
|-------|---------|
| `admin/command-monitor` | `UniversalNativeCockpitPage`: Idempotenz-KPIs (flach aus Overview), Tabellen Commands/Aggregate/Lookup-Pfade; GET `/idempotency/commands|aggregates|lookup-paths`; gefährlicher Batch13-Stamm-Stub entfernt |
| `annahme/rohware` | `IntakeWeighingPage` + spezialisierter Wizard (alle Legacy-Felder) + POST `/api/v1/agrar/harvest-acceptance/rohware` (Compat→HarvestAcceptanceCreate); Human/CI/MCP gleicher Submit-Kanal |

Inventar: Command-Monitor und Rohware runtime_wired über Studio-Hosts.

## Vierundzwanzigste Hebung (Batch 24)

| Maske | Nachher |
|-------|---------|
| `admin-suite` | `UniversalNativeCockpitPage`: Readiness-KPIs + Evidenzliste + Nav-Kacheln; GET `/readiness/evidence` |
| `admin-suite/connectors\|devices\|operations\|compliance\|system-status\|diagnostics` | `NativeListPage` (gleiche Katalog-Endpunkte, `id=key`) |
| `admin-suite/setup` | `NativeListPage` + PATCH `/setup/steps/{entity_id}` (In Arbeit / Abschliessen) |

Inventar nach Batch 24: `runtime_wired` ~1101, `hand_built` ~25.

## Fuenfundzwanzigste Hebung (Batch 25)

| Maske | Nachher |
|-------|---------|
| `admin-suite/migration` | `UniversalNativeCockpitPage`: Profile/Batches-Tabellen, Dry-Run anlegen (POST `/migration/batches`), Freigabe-Row-Action; GET `/migration/overview\|profiles\|batches` |
| `admin-suite/security` | `UniversalNativeCockpitPage`: Menschen-/Agentenrollen + SoD-Simulation (POST `/security/simulate`, kommagetrennte Rollen); GET `/security/overview\|roles\|agent-roles` |
| `admin-suite/ki-anbieter` | `UniversalNativeCockpitPage`: PUT `/llm-gateway` + POST `/llm-gateway/test` (gleiche commandEndpoints Human/CI/MCP) |
| `admin-suite/connectoren` | `UniversalNativeCockpitPage`: flache PUT `/capture-connectors/stt\|imap` + Test/Poll; GET `/capture-connectors/overview` |
| `admin-suite/pos-fiscalization` | `UniversalNativeCockpitPage`: PUT `/pos/fiscalization/config` (+ `terminal_id`→settings); GET `/pos/fiscalization/overview\|products` |

Inventar nach Batch 25: Admin-Suite Rest runtime_wired; verbleibende schwere `hand_built`: materialfluss, abrechnung, Ernte-Erfassung, Schlagkartei, Milchvieh-Karte.

## Sechsundzwanzigste Hebung (Batch 26)

| Maske | Nachher |
|-------|---------|
| `agrar/kunden-schlagkartei` | `UniversalNativeCockpitPage` + `agrar_workbench`: Legacy-Surface (PortalKontoGate/Dialoge) + commandEndpoints POST `/portal/lohndienste` (lohn_spritz/mahl_misch) und `/portal/empfehlungen/generieren/schlagkartei` |
| `agrar/milchvieh-karte` | `UniversalNativeCockpitPage` + `agrar_workbench`: MapLibre-Surface + GET `/agrar/milchvieh-crosssell/map` |

Inventar nach Batch 26: Schlagkartei und Milchvieh-Karte runtime_wired; verbleibend u. a. materialfluss, abrechnung, Ernte-Erfassung.

## Siebenundzwanzigste Hebung (Batch 27)

| Maske | Nachher |
|-------|---------|
| `agrar/ernte-annahme-erfassung` | `agrar_workbench`: Legacy-Surface + POST/PUT/calculate/release/DELETE `/agrar/harvest-acceptance` |
| `annahme/abrechnung` | `agrar_workbench`: Legacy-Surface + Settlement preview/create/post-fibu/freigabe/cancel |
| `lager/materialfluss` | neuer Typ `lager_workbench`: ReactFlow-Surface + WMS-Agri nodes/edges/transfer/lot-link |

Inventar nach Batch 27: die drei schweren Prioritaetsmasken runtime_wired. Verbleibend u. a. duenne Admin-Ops-Seiten und Dialog-Hilfsmodule; Gate D Browser.

## Achtundzwanzigste Hebung (Batch 28)

| Maske | Nachher |
|-------|---------|
| `admin/externe-gates` | Cockpit: Overview/Items flach (`/external-gates/overview`, `/items`) — Paritaet Legacy-Karten |
| `admin/control-center/agent-ops` | `admin_workbench` + Legacy-Surface; Persistence-Read `/agents/neuroassist/ops/persistence` |
| `admin/control-center/superglue` | `admin_workbench` + Legacy-Surface; Commands connector/policy/wizard/apply (MCP-WRITE-015) |

### Batch 28b — restliche duenne Admin/Meta-Routen

Alle verbleibenden Routen-`hand_built` (GapPipeline, agenten-integration, screen-studio,
setup/dms, voice, vordruck, postfaecher-rueckruf, studio workspace-preview) auf
`admin_workbench` + Legacy-Surface; Commands wo API vorhanden (Vordruck/DMS/GAP/Postfach).

Inventar nach 28b: Routen-`hand_built` **0** (Dlg*/Charts bleiben Nicht-Routen-Module).

### Batch 29 — Konditionssystem + tote Altmasken

| Route / Artefakt | Aenderung |
|------------------|-----------|
| `konditionen/konditionssystem` | Neu in Route-Tree (`auto-groups/generated/konditionen.ts`); `pricing_workbench` + Legacy-Surface; Commands Preislisten/Rabatte/Individualpreise/Pricing (MCP-WRITE-015) |
| Tote Nested-Altmasken | Entfernt: `kunden-stamm-modern/{Legacy,CustomerMaskEdit}`, `kunde-neu/KundeNeuMaskBuilderPage`, `lead-detail/{LeadMask,LegacyLead}` — Routen waren bereits native |
| Switch-Test | `kunden-stamm-modern-switch` prueft Re-Export auf `customer-360-native` |

### Batch 30 — fehlende Nav-Routen

| Route / Artefakt | Aenderung |
|------------------|-----------|
| `admin-suite/connectoren` | In `auto-groups/generated/admin-suite.ts` verdrahtet (SD/Cockpit war schon da) |
| `fuhrpark/fahrzeug-vertiefung` | Route + `fleet_workbench` + Legacy-Surface (Status/Schaeden/Bussgelder/Leasing); gleiche Fuhrpark-commandEndpoints |

Nav-`preferredPath` ohne Route-Inventory: **0** (ausser `/` als leerer Pfad).

### Batch 31 — Gate E Ablöse-Aliase

Made-by-Studio Gate E: 5 Alt-Screen-IDs ohne Runtime-Marker → Aliase auf verdrahtete Kanäle
(`finance/bankkonto`, `crm/customer-360`, `beleg-liste/sales-order`, `zertifikate/liste`).

### Batch 32 — Gate C OpenAPI + Endpoint-Korrekturen

- `docs/schnittstellen/openapi.json` regeneriert (`generate_openapi.py`, 3247 Pfade)
- SD-Fixes: Superglue `{tenant_id}`, Rohware→Warteschlange, FiBu→asset-accounting,
  Kostenstellen→kostenrechnung, Rezepte→futtermittel/rezepte, Command-Monitor Tabellen-Spalten
- Verifier: **A/B/C/E = 829/829** (`scripts/verify_made_by_studio_gates.py`)

### Batch 33 — Draft-clean + Permission-Projektion

- Ungültiges `dangerLevel: destructive` → `critical` (6 Masken + Capture-Spiegel)
- Flow-Spine-Katalog: Draft-Projektion akzeptiert `baseScreenId` (822→**829 Draft-clean**)
- `generate_action_permission_projection.py`: Leaf-APIRoute unter FastAPI-Include-Routern;
  Projektion neu geschrieben (231 Aktionsrechte), `--check` grün

### Batch 34 — Advisory Score 1.0

- Hydrate: Tabellen erhalten fehlende `sortable`/`filterable`; Agent-Contract Defaults
- `cockpit_content` erkennt `specialized`, Flow-Spine und Twin-Panels (keine False-Positives)
- `workflow_declared` akzeptiert `flowSpineWorkspace.processKey`
- Verifier: **A/B/C/E = 829/829**, Draft-clean **829/829**, advisory Ø **1.0**

### Batch 35 — ProcessBand (FSX-030) auf Beleg-/Kettenmasken

- `BelegMaskeParent`: Default-`workflow.phases` (Erfasst → Freigegeben → ggf. Gebucht) + `documentType`
- Hydrate ergänzt Phasen für Beleg- und `processChain`-Detailmasken
- Document-Screen-Versions **1.14.0** (9 Belegvarianten)
- Prioritäre ProcessBand-Abdeckung: Belegfamilie + Prozessketten-Masken (Stammdaten mit `noWorkflowReason` bewusst ohne Band)

### Batch 36 — Design-Token-Invarianten (Mask-Builder)

- Flow-Spine-Renderer/Dialoge: Rohpalette → `text/border/bg-status-*`
- Waage-Tickets + Mobile-Fütterung: Statusfarben semantisch
- Rationsoptimierung: `text-[10px]` → `text-2xs` (64×)
- Mask-Builder-Tree: 0 Treffer auf Rohpalette/`text-[10px]` (Scan)

### Batch 37 — Tabs ARIA (Fleet/Pricing)

- `fahrzeug-vertiefung-legacy`, `konditionssystem-legacy` → `Tabs`/`TabsList`/`TabsTrigger`/`TabsContent`
- Head `d439080d1` — CI grün

### Batch 38 — Tabs + Tokens (Rohwarengruppen / Legacy-Surfaces)

- `rohwarengruppen-legacy` → ARIA Tabs
- Status-Tokens: Materialfluss, Service/Qualität/Artikel-Legacy
- Rohpalette-Scan `pages` + `mask-builder` = 0
- Head `f525b07d0` — CI grün (mkdocs/docs-governance/role-contracts)

### Batch 39 — Gate-D Theme-Smoke + DMS Error-Feedback

- Gate-D Cockpit-Smoke: Hell+Dunkel (`localStorage.theme` + `html.dark|light`) inkl. Screenshots
- DMS-Setup: Status-Load-Fehler sichtbar (`role="alert"`) statt stilles `setStatus(null)`
- Hinweis: Theme-Smoke ersetzt **nicht** Live-SSO; Image-CI bleibt Codex

### Batch 40 — Gate-D Smoke-Lauf belegt + Qualitätsversprechen nachgezogen

- `npx playwright test tests/e2e/uix-gate-d-studio-cockpit-smoke.spec.ts` → **6/6 passed** (Europe/Berlin 2026-11-25 ~22:02)
- Screenshots: `packages/frontend-web/test-results/gate-d-*-{light,dark}.png` (Artifact-Kopie unter Agent-Store `media/gate-d-smoke/`)
- `made-by-studio-qualitaetsversprechen.md` Belegstand aktualisiert (A/B/C/E 829/829, Routen-`hand_built` 0; Gate-D Rest Live-SSO/Image)

### Batch 41 — Page-Module-Groups + Workbench Gate-D Smoke

- Fehlende Prefixe in `page-module-loader`/`page-module-groups` geschlossen:
  `konditionen`, `aktien`, `analysis`, `betrieb`, `contracts`, `dms`, `schnittstelle`, `studio`
  (sonst Runtime-Fehler `unsupported page group` — Konditionen-Workbench war tot)
- Gate-D Smoke erweitert um Materialfluss, Konditionssystem, Fahrzeug-Vertiefung → **12/12 passed**
- Vitest `page-module-loader.test.ts` deckt die neuen Prefixe ab

### Batch 42 — Inventar-Prefix-Ratschen + DMS/Betrieb Smoke

- Vitest: jedes `@/pages/*`-Prefix aus `route-inventory.gen.json` muss `getPageModuleLoader` ohne `unsupported page group` liefern
- Alle 8 reparierten Prefixe werden konkret geladen
- Gate-D Smoke + DMS Archiv-Suche + Betrieb Maschinen-Stamm → **16/16 passed**

### Batch 43 — Fehlende Sales-Delivery-Editoren + Inventar-Load-Ratsche

- `sales/delivery-editor` und `sales/delivery-editor-new` fehlten als Dateien (Route → `unknown module`)
- Wiederhergestellt als `belegSeite('sales_delivery')` (wie `lieferung-neu` / `order-editor`)
- Vitest `page-module-inventory-load.test.ts`: **jedes** Inventar-`@/pages/*`-Modul lädt (5/5 inkl. Loader-Tests)

### Batch 44 — Specialized-Workbench Gate-D Smoke (Surface-Tiefe)

- Mock-SD fuer Workbenches enthält `specialized.type` + Contract-Felder (`pricing`/`fleet`/`lager`)
- Asserts: ARIA-`tablist` (Konditionen, Fuhrpark) bzw. „Hinweis Prototyp“ (Materialfluss)
- Query-sichere List/Overview-Mocks + gezielte Surface-API-Doubles (`price-lists` als Array)
- Gate-D Smoke weiter **16/16 passed** — jetzt mit Specialized-Surface, nicht nur Shell/Titel

### Batch 45 — ObjectPage-Legacy-Altlasten entfernt

- 9 tote `*-legacy.tsx` ObjectPage/ListReport-Dateien geloescht (Saatgut/Duenger/Opportunity/Anfrage/Angebot/Anlieferavis/Bankkonten/Debitoren/Kreditoren)
- Inventar: `pages_legacy` **9 → 0**; Routen `hand_built` weiter **0**
- IBAN-Race-Schutz in `useIbanLookup` (Sequenz-Guard); Vitest deckt Hook statt ObjectPage ab
- Angebot→Bestellung-Nav-Vertrag an ScreenDefinition `resultNavigationRoute` gebunden
- Einkauf-Feldparitaet: eingefrorene Legacy-Feldvertraege statt Dateilesen

### Batch 46 — TabsList aria-label + Agrar Gate-D Smoke

- Alle `TabsList` unter `src/pages` ohne `aria-label` nachgezogen (19 Dateien / 20 Listen)
- Gate-D Smoke + Kundenschlagkartei / Ernte-Annahme-Erfassung (agrar_workbench + Tabs)
- Portal-Kundenkonten-Mock fuer Schlagkartei-Surface → **20/20 passed**

### Batch 47 — Component TabsList + Finance Gate-D

- `TabsList` aria-label in Mask-Builder/Patterns ObjectPage, LazyTabs, FlowSpine, DMS, Sales-Dialoge
- DMS-Badges: `text-2xs` + `text-status-warning` (keine Rohpalette/`text-[10px]`)
- Gate-D + `finance/bank-abgleich` (finance_workbench Surface) → **22/22 passed**

### Batch 48 — TabsList-Ratsche + Mahnlauf Gate-D

- Vitest-Ratsche: jedes `TabsList` in `pages/` und `components/` braucht `aria-label`
- Mahnlauf-Surface: `aria-label="Mahnlauf Arbeitsbereich"`
- Gate-D + `mahnwesen/mahnlauf` → **24/24 passed**

### Batch 49 — Micro-Label-Ratsche + Milchvieh-Karte Gate-D

- FlowSpine + Mobile-Feeding: arbiträre 10/11px → `text-2xs`
- Vitest-Ratsche gegen Micro-Label-Arbitraries (Allowlist nur Rationsoptimierung)
- Milchvieh-Karte: Status-Token-Legende + Landmark; Gate-D → **26/26 passed**

### Batch 50 — Workflow/UI Micro-Labels

- `ux-standard`, CompactDecisionCard, PolicyBadge, Table/KPI/VirtualDataTable, CustomerCombobox, Idempotency-Panel → `text-2xs`
- Micro-Label-Ratsche um `workflow`/`policy`/`ui` erweitert (Allowlist weiter nur Rationsoptimierung)

### Batch 51 — Feed Gate-D + Legacy-Altlasten

- Orphan ObjectPage-Legacy entfernt (Saatgut/Dünger/Reklamation/Rohware)
- Feed-Workbench: Mobile Fütterung + Rationseditor Landmark + Gate-D → **30/30 passed**

### Batch 52 — Orphan-Legacy-Sweep + Waage Gate-D

- 54 unverlinkte `*-legacy.tsx` mit Native-Sibling entfernt; Paritäts-Tests auf eingefrorene Baselines
- Waagenliste Landmark + Gate-D (`weighing`) → **32/32 passed**

### Batch 53 — Stamm/Detail-Legacy + Intake Gate-D

- 12 ObjectPage-Stamm/Detail-Legacy entfernt (Artikel/Charge/Finance/…); Ratsche erweitert
- Annahme-Warteschlange Landmark + Gate-D (`intake`) → **34/34 passed**

### Batch 54 — Intake-Vollkette + Wiegungen Gate-D

- Landmarks: LKW-Registrierung, Qualitätsprüfung, Rohware, Wiegungen
- Gate-D Intake/Waage-Vollkette → **42/42 passed**

### Batch 55 — Annahme-Abrechnung + Admin Voice Gate-D

- Landmarks: Annahme-Abrechnung, Voice-Kanal
- Gate-D `agrar_workbench`/`admin_workbench` → **46/46 passed**

### Batch 56 — Admin Vordruck/Studio/GAP Gate-D

- Landmarks: Vordruck-Editor, Masken-Studio, GAP-Pipeline
- `StudioGateSummary`: sichere Optional-Chain auf `readiness`/`violations` (Crash bei Teilantwort)
- Gate-D Admin-Workbench → **52/52 passed**

### Batch 57 — Agenten-Integration + DMS-Setup Gate-D

- Landmarks: Agenten-Integration, DMS-Integration
- Gate-D Admin-Workbench → **56/56 passed**

### Gate D Browser / Image (Stand 2026-11-25, Europe/Berlin)

Bezug: [Made-by-Studio Qualitaetsversprechen](../architecture/uix/made-by-studio-qualitaetsversprechen.md) §D;
`scripts/verify_made_by_studio_gates.py` / `generate_studio_screen_versions.py` pruefen Gate D **nicht**.

| Gate-D-Teil | Stand | Beleg / Blocker |
|-------------|-------|-----------------|
| Browser-Smoke native-cockpit (publizierte Routen, Mock-SD) | **Teilbeleg gruen (lokal, 2026-11-25)** | `uix-gate-d-studio-cockpit-smoke.spec.ts` — **56/56 passed** (28 Masken × Hell/Dunkel; inkl. Agenten/DMS); Screenshots `test-results/gate-d-*-{light,dark}.png` |
| Reale SSO-Bedienung + Hell/Dunkel Screenshots | **teilweise / blockiert** | Theme-Smoke (Mock-Auth) vorhanden; **Live-SSO** weiterhin nicht in diesem Environment; Qualitaetsversprechen verlangt reale SSO der *publizierten* Maske |
| Image-/CI-Nachlauf mit kanonischem `table-catalog.json` | **blockiert (Codex)** | Workboard-Slice `STUDIO-ENTITY-RELEASE-20261021` **reserviert, Owner Codex**; Dateibesitz Katalog/Image-Nachlauf dort. Lokal vorhanden und verdrahtet: `docs/admin/table-catalog.json` (31 Schemas), `Dockerfile.backend` COPY, `docker-compose.yml` RO-Mount, `.dockerignore` Freigabe — das ist **kein** Image-CI-Gruen-Nachweis |

**Was dieser PR bewusst nicht anfasst:** `docs/admin/table-catalog.json` / `.md` (Codex-Besitz), kein Image-Rebuild, kein SSO-Mock als „Gate D gruen“.

Inventar-Hinweis: `Dlg*` und Report-Chart-Module unter `pages/` sind keine Routenmodule.

## Noch offen (Folge / Goal)

- Gate D SSO Hell+Dunkel + Image-CI `table-catalog` → Codex `STUDIO-ENTITY-RELEASE` (oder Freigabe Dateibesitz)
- Playwright Gate-D-Smoke einmal gegen laufendes Frontend ausfuehren
- Goal-Complete erst nach Gate-D-Image/SSO-Beleg

## Tests

```bash
python -m pytest tests/test_studio_parity_batch19.py tests/test_studio_parity_batch23.py \
  tests/test_studio_parity_batch24.py tests/test_studio_parity_batch25.py \
  tests/test_studio_parity_batch26.py tests/test_studio_parity_batch27.py \
  tests/test_studio_parity_batch28.py tests/test_studio_parity_batch28b.py \
  tests/test_studio_parity_batch29.py tests/test_studio_parity_batch30.py \
  tests/test_zinsabrechnung_studio_parity.py tests/test_einkauf_studio_field_parity.py \
  -q --noconftest -o addopts=
cd packages/frontend-web && npx vitest run \
  src/__tests__/pages/mask-objectpage-stamm-native-route.test.ts \
  src/__tests__/pages/crm/kunden-stamm-modern-switch.test.tsx \
  src/__tests__/bank-account-form-contract.test.tsx \
  src/__tests__/components/mask-builder/screen-permissions.test.ts
# Gate D Browser (wenn Playwright/Frontend bereit):
# npx playwright test tests/e2e/uix-gate-d-studio-cockpit-smoke.spec.ts
```



