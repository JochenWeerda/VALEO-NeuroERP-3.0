---
title: StammObjectPageParent Rollout — QA
type: qa-evidence
audience: [agent, entwickler, qa]
owner: Cursor Composer
status: abgeschlossen
last_reviewed: 2026-10-22
version: 1.1.0
description: Nachweis UIX-STAMM-OBJECTPAGE-PARENT-20261022 & UIX-STAMM-OBJECTPAGE-ALL-20261022 — Parent-Factory, alle 12 Stamm-Children, Studio Gates A-C und Listen-Detailnavigation.
---

# StammObjectPageParent Rollout (2026-10-22)

## Slices

- `UIX-STAMM-OBJECTPAGE-PARENT-20261022` — Pilot (Factory + 5 Children)
- `UIX-STAMM-OBJECTPAGE-ALL-20261022` — Vollrollout aller 12 Stamm-ObjectPage-ScreenDefinitions + Listen-Detailnavigation + Studio Gates A–C

## Geliefert

| Artefakt | Inhalt |
|---|---|
| `app/core/stamm_object_page_parent.py` | Factory `build_stamm_object_page` + Helfer `stamm_kopf_tab`, `stamm_entity_tab`, `stamm_lazy_table_tab`, `stamm_entity_source`, `stamm_tab_source` |
| Pilot-Builder in `screen_definitions.py` | `agrar/duenger`, `agrar/saatgut`, `einkauf/supplier`, `finance/debitor`, `finance/kreditor` |
| Weitere Stamm-Builder in `screen_definitions.py` & `screen_definitions_stamm.py` | `finance/bankkonto`, `lager/article-stock`, `crm/opportunity`, `crm/lead`, `futtermittel/einzelfuttermittel`, `futtermittel/mischfuttermittel`, `artikel/stamm` |
| Frontend-Listen (Detail-Navigation auf native Runtime) | `banken/konten.tsx` (`/banken/konto/:id` → `/finance/bankkonto/:id`); `NativeListPage`-Klassifikation in `scripts/mask_route_migration_inventory.py` |
| Tests | `tests/test_stamm_object_page_parent.py` (29 Tests), `packages/frontend-web/src/__tests__/pages/mask-primary-nav-native.test.ts` (6 Tests) |

## Parent-Vertrag (Shell)

- `mode=detail`, adapter native non-temporary
- `layout.floorplan=objectPage`, `sectionNavigation=anchors`, `columnNavigation=single`, sticky header/footer
- `tabs[0].key=kopf`, dataSource `entity`
- Primaeraktion `edit` (bzw. `bearbeiten` bei `artikel/stamm`, safe); optionale `extra_actions`, `edit_action_zone`, `edit_action_overrides`
- `identityField` + summary mit `kind=identity` (bei `finance/bankkonto` `identity_field=None`, da `id` Trivial-Key ist)
- `noWorkflowReason` oder deklarativer `workflow` Pflicht

## Alle 12 Stamm-Children (Overrides erhalten)

| Screen | identityField | density / rail / profile | Besonderheit |
|---|---|---|---|
| `agrar/duenger` | `artikelnummer` | compact / combined / standard | Tabs Verwendung, Preise |
| `agrar/saatgut` | `artikelnummer` | compact / combined / standard | Tabs Lagerbestaende, Vertraege |
| `einkauf/supplier` | `lieferantennummer` | expertDense / combined / standard | summaryEndpoint, Aktion `neue_bestellung` |
| `finance/debitor` | `debitoren_nr` | expertDense / audit / financial | OP + Umsaetze |
| `finance/kreditor` | `kreditoren_nr` | expertDense / audit / financial | OP + Bestellungen |
| `finance/bankkonto` | `None` (`id` im Kopf) | expertDense / audit / financial | Buchungen-Tab (pageSize 50) |
| `lager/article-stock` | `article_number` | expertDense / combined / inventory | summaryEndpoint, `zone=commit`, `enterMovesFocus`, `rowRouteTemplate` auf Lagerbewegung |
| `crm/opportunity` | `name` | compact / combined / standard | summaryEndpoint, Entity-Tab `zuordnung`, Aktion `create_activity` |
| `crm/lead` | `company_name` | expertDense / combined / standard | `creation`, `workflow` (`crm-party-lifecycle`), Aktion `qualifizieren` |
| `futtermittel/einzelfuttermittel` | `artikel_nummer` | compact / combined / standard | Tabs Naehrstoffe, Preise, Historie (`serverPagination=False`) |
| `futtermittel/mischfuttermittel` | `produkt_code` | compact / combined / standard | Tabs Rezeptur, Naehrstoffe |
| `artikel/stamm` | `article_number` | expertDense / combined / inventory | `creation`, 4 Entity-Tabs + 3 Register, Aktion `bearbeiten` mit `inputFields` |

## Studio-Gates Status (A–C)

- **Gate A (Definition & Vertrag):** Alle 12 Stamm-Masken bestehen `_check_readiness` (`generatorReady=True`, 0 mandatory errors) und liefern einen vollstaendigen `AgentMaskContract` (`_generate_agent_contract`).
- **Gate B (Studio-Quellen & Katalog):** Alle 11 in `_SCREEN_DEFINITIONS` registrierten Stamm-Masken sind ueber `studio_native_import.list_sources` (`valeo_cli studio quellen`) mit deterministischem `definition_hash` als Studio-Ausgangsfassung uebernehmbar.
- **Gate C (Runtime & Feldvertrag):** Alle 11 aktiven Detailrouten sind in `route-inventory.gen.json` auf `*-native` (`UniversalNativeDetailPage` / `FeedingFeedDetail`) verdrahtet; `check_field_contracts.py` meldet 0 Abweichungen.

## Umgestellte Frontend-Listen & Inventar-Delta

- `packages/frontend-web/src/pages/banken/konten.tsx`: Zeilenklick von `/banken/konto/:id` (Selbstlink auf Liste) auf die native Route `/finance/bankkonto/:id` (`finance/bankkonto`) umgestellt; Neuanlage `/banken/konto/neu` bleibt Legacy.
- Die uebrigen Stammdaten-Listen (`finance/debitoren-liste`, `finance/kreditoren-liste`, `artikel/liste`, `crm/opportunities-liste`, `futtermittel/mischfuttermittel-liste`, `futtermittel/einzelfuttermittel-liste`, `futter/misch/liste`, `futter/einzel/liste`, `agrar/duenger/liste`, `agrar/saatgut/liste`) laufen in `HEAD` bereits ueber `NativeListPage` bzw. Re-Export auf die kanonischen Native-Detailrouten (lokale WIP-Altlasten aus dem Working Tree auf `HEAD` zurueckgesetzt).
- `scripts/mask_route_migration_inventory.py` erkennt nun auch `NativeListPage` und `UniversalNativeCockpitPage` als `runtime_wired`:
  - **Vorher:** 941 Routen — `61` `runtime_wired`, `115` `legacy_mask_pattern`, `764` `hand_built` (52/57/591 Seiten).
  - **Nachher:** 941 Routen — **`104` `runtime_wired` (+43)**, **`106` `legacy_mask_pattern` (-9)**, **`730` `hand_built` (-34)** (`89` `pages_runtime` (+37), `52` `pages_legacy` (-5), `560` `pages_hand` (-31)).

## Tests

```bash
python -m pytest tests/test_stamm_object_page_parent.py tests/test_meridian_party_objectpage.py tests/test_l3_habit_bridge_screen_definitions.py tests/test_feeding_feed_catalog.py -q --noconftest -o addopts=
cd packages/frontend-web && npx vitest run src/__tests__/pages/mask-primary-nav-native.test.ts
python scripts/mask_route_migration_inventory.py
```

## Abgrenzung

- `fuhrpark/fahrzeug-stamm` bleibt in `screen_definitions_capture.py` (eigener `speichern`/`loeschen`-Vertrag + TS-Paritaet in `capture-screens.ts` / `test_tourenplanung_definition.py`).
- `crm/customer-360` bleibt explizite Cockpit-Ausnahme laut Taxonomie §2.8.
- Gate D Image/CI/Browser publiziert: weiter Codex `STUDIO-ENTITY-RELEASE`.
- Belegfamilie / `screen_definitions_beleg.py`: unangetastet.
- Touren/Training/Bestellvorschlag: unangetastet.
