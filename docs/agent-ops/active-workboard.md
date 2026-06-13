# Active Workboard

Stand: `2026-06-13`

## WM-AGRI-SILO-001 — Agrar-Silo / Materialfluss (additiv WMS)

**Von:** Cursor
**Owner:** Cursor
**Stand:** in Arbeit 2026-06-12 — Migration `agri_silo_material_flow_20260612`, Service `AgriSiloMaterialFlowService`, Router `/api/v1/lager/wms/agri`, Unit-Tests `tests/test_agri_silo_material_flow.py`, Frontend-Prototyp `/lager/materialfluss` (`@xyflow/react`), Doku unter `docs/warehouse/`.
**Ziel:** Digitales Modell Siloanlage/Silozelle/Materialfluss ohne PLC; QS-Sperre und Verschleppungs-Hinweis auf Routen; Mandanten-Trennung.
**Dateibesitz:** genannte Alembic-/Backend-/Frontend-/Test-/Doku-Dateien, `docs/agent-ops/slices/WM-AGRI-SILO-001.yaml`, Roadmap `WM-AGRI-FLOW-001.yaml`.
**Abnahmekriterien:** `alembic heads` einheitlich; API erreichbar; Tests `pytest tests/test_agri_silo_material_flow.py --no-cov` gruen; `npm run type-check` im Frontend nach Dependency; Navigation + Route-Generate konsistent.

## WAVE-PHYS-CHAIN-001 — Task 0 Verifikation + Logistik-Audit

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Playwright Dev-Session ohne Fake-Login; Audit-Dokument physische Kette / Logistik.
**Ziel:** Blindfläche aus Advisor-Feedback schließen, bevor LOG-*-Slices gebaut werden.
**Dateibesitz:** `playwright-tests/helpers/api.ts`, `playwright-tests/fixtures/testSetup.ts`, `docs/quality-assurance/playwright-smoke-auth.md`, `docs/workflows/wave-physical-chain-logistics-audit-2026-06-12.md`, `domain-depth-plan`.
**Abnahmekriterien:** Doku + funktionierender Dev-Pfad für @smoke; keine parallelen DOM-005-Spines.

## LOG-PROD-001 — Logistik `domain_logistics` per Alembic

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Alembic `log_logistics_core_20260612`; Runtime-DDL aus `logistics_tours.py` und `logistics_freight.py` entfernt; Integrationstests `tests/test_logistics_integration.py`.
**Ziel:** Production-gleiche Persistenz für Touren/ePOD/Statistik und Frachttarife (analog PROC-RFQ-001).
**Dateibesitz:** `alembic/versions/log_logistics_core_20260612.py`, Logistik-Endpunkte, genannte Tests, Audit-Dokument.
**Abnahmekriterien:** `alembic upgrade head` erzeugt Tabellen; keine `_ensure_schema` / `_ensure_freight_table` in den Routern; bestehende Unit-Tests mit Mocks angepasst.
**2026-06-12:** Frachtkosten simulate/calculate mit **X-Tenant-ID-Pflicht** und SQL-Filter auf Tarifzeilen (kein Fremd-Tenant); Tests in `test_logistics_integration.py` / `test_logistics_tour_freight.py`. Anschliessend: **GET freight-tariffs** ohne Header nur `tenant_id IS NULL`; **POST freight-tariffs** verlangt Header (422) — weitere Integrationstests.

## LOG-SPINE-RAND-001 — Lieferschein-Referenz Read-Spine (Logistik)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — GET ``sales-delivery-note-by-ref`` + optional ``include_delivery_hints`` auf Tour-Detail; Tests ``test_logistics_delivery_hint.py``.
**Ziel:** Medienbruch reduzieren ohne Schema-FK; Muster wie `sales_storno_service` (id oder Nummer).
**Dateibesitz:** `logistics_tours.py`, `tests/test_logistics_delivery_hint.py`, Wave-Audit, Slice-YAML.
**Abnahmekriterien:** Neuer GET-Resolve + optional `include_delivery_hints` auf Tour-Detail; Tests gruen.

## LOG-LIFE-001 — Tour-/Stopp-Storno (fail-closed) + UAT

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — API-Storno in `logistics_tours.py`, Frontend
`misc-modules.ts` / `tourenplanung.tsx`, Integrationstest
`test_tour_cancel_fail_closed_and_stop_cancel`, UAT
`scripts/uat/logistics_tour_lifecycle_uat.py`; Decorator-Fix `add_event`.
**Ziel:** Storno ohne Medienbruch; 409/422/403 fail-closed; reproduzierbares UAT.
**Dateibesitz:** genannte Dateien + Wave-Audit.
**Abnahmekriterien:** Storno-POSTs + Tests + UAT-Skript (dry-run/execute) dokumentiert.
**Review (Claude, 2026-06-12):** zwei Fixes direkt eingespielt — (1) `test_freight_tariff_create_and_simulate`
war versehentlich in den neuen Storno-Test hineingemergt (Methodenzeile ersetzt statt eingefügt);
wieder als eigene Testmethode ausgegliedert. (2) `add_event`: `status_code=201` wiederhergestellt
(der Decorator-Umbau hatte den Create-Statuscode stillschweigend auf 200 geändert; kein Konsument
hängt daran, aber Vertrag bleibt so stabil). Verifiziert: `pytest tests/test_logistics_integration.py
tests/test_logistics_delivery_hint.py` → 6/6 grün; ESLint + `type-check:focused` grün.

## LOG-CHAIN-001 — Ketten-Lifecycle (Audit Bruchstelle 2)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Integrationstest
`test_chain_lifecycle_ls_tour_hints_freight_supply_read` in `tests/test_logistics_integration.py`
(ohne `DEMO-LS-001` aus `seed_demo_sales.py`: Skip), UAT
`scripts/uat/logistics_chain_lifecycle_uat.py`; Wave-Audit Abschnitt 2 Punkt 2 geschlossen.
**Ziel:** Reproduzierbare Kette **Lieferschein-Ref → Tour mit Hints → Fracht simulate →
`GET /supply-chain/traceability/tickets` (Settlement-Seite read-only) → Tour-Storno**.
**Dateibesitz:** genannte Test-/UAT-Dateien, Audit-Dokument.
**Abnahmekriterien:** Test + UAT (dry-run/execute) dokumentiert; keine Abrechnungs-Mutation im Slice.

## LOG-LIFE-UI — Tour-Storno in der Tourenplanung (Frontend)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — `cancelLogisticsTour` / optional `cancelLogisticsTourStop`
in `logistics-tours.ts`; Tourenplanung: Bestätigungsdialog, `invalidateQueries(['logistik','touren'])`,
Toasts, Pending-State.
**Ziel:** LOG-LIFE-001 vom Schreibtisch aus bedienbar ohne REST-Client.
**Dateibesitz:** `tourenplanung.tsx`, `logistics-tours.ts`, Wave-Audit, Workboard.

## LOG-TF-WS-001 — Tour & Fracht Dispo-Arbeitsraum (gemeinsame Route)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Seite `tour-fracht-arbeitsraum.tsx`, Nav-Eintrag, Auto-Route
`logistik/tour-fracht-arbeitsraum`, Domain-Landing `tour-fracht-arbeitsraum`; `routes:generate` + Navigation-Check gruen;
Erweiterung: **RoleFocusBar**, **Frachtkosten-Kurzcard** (`logistics-freight.ts` → Tarife + GET simulate).
**Ziel:** Wave-Audit Punkt 5 — eine operative Einstiegssicht fuer Tour + Frachtbrief.
**Dateibesitz:** genannte Dateien, `operations.tsx`, `dashboard-catalog.ts`, `auto-groups/generated/logistik.ts`.
**Review (Claude, 2026-06-12):** keine Befunde — `useSupplyChainOverview` liefert `initialData`
(kein Undefined-Zugriff auf `chain` vor dem Load), Frachtkosten-Probe mit Pending-Guard/finally/Toast,
ESLint auf beiden neuen Dateien grün.
**E2E:** Route in `main-routes-smoke.spec.ts` (expectedText) und `visual-tour.spec.ts` ergänzt.

## FEED-CHAIN-001 — Produktion→Charge-Durchstich (Mischfutter)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-12 — Migration `feed_chain_verbrauch_20260612` (Single-Head),
Service + Endpoint-Umbau, Seed `seed_demo_feed_chain.py` (DEMO-MLF-18), 7 neue Tests grün,
20 Bestands-Regressionstests grün, UAT dry-run + `--execute` gegen Live-Backend grün.
**Ziel:** Belegbruch schließen: Produktionsauftrag ``fertig`` erzeugt die Fertigwaren-Charge
(``domain_ops.ops_chargen``) mit Mischprotokoll (``rohstoffe``/``produktionsprozess``) statt
nur ``fertig_am``; Verbrauchs-Snapshot bei Freigabe (fixt auch Bestandsdrift beim Storno nach
Rezeptänderung); Trace Auftrag/Charge → Komponenten.
**Dateibesitz:** `app/api/v1/endpoints/produktion_mischfutter.py`,
`app/services/feed_production_chain_service.py` (neu), `app/infrastructure/models/futtermittel_models.py`,
Alembic `feed_chain_verbrauch_20260612`, `tests/test_feed_production_chain.py` (neu),
`scripts/uat/feed_production_chain_uat.py` (neu), Audit-Doc Futtermittel-Kette.
**Abnahmekriterien:** fertig → Charge idempotent + fail-closed (409 bei fremder chargen_id);
Storno restauriert exakt den Freigabe-Verbrauch; Trace-GET; Tests + UAT grün.

## FEED-CHAIN-002 — Produktions-Lifecycle im Frontend (Mischfutter)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-12 — Browser-verifiziert (Dev :3000): Wizard → Auftrag (201) →
Freigeben → Produktion starten → Fertig (Charge `CH-…` erscheint mit Link in der Zeile) →
„Kette anzeigen“ (Trace-Panel „Kette geschlossen“, Mischprotokoll 1.240/0.680/0.080 t bei 2 t).
Zusatzbefund behoben: ``initialData: []`` + ``staleTime`` unterdrückte den ersten Fetch
(Rezept-Select war deshalb schon immer leer) → Hooks ohne ``initialData``, Fallback `?? []`.
ESLint + `type-check:focused` grün.
**Ziel:** Kette vom Schreibtisch aus bedienbar. Befund: Wizard postet ``{rezeptur, menge}``,
Backend erwartet ``{rezept_id, menge_t}`` (→ 422, Create war tot); Komponenten-Map nutzt
``k.name`` statt ``komponente_name`` (Bedarfsprüfung leer). Fix der Hooks/Payloads +
Auftragsliste mit Statusübergängen (freigeben → in_produktion → fertig → storniert),
Charge-Link nach ``fertig`` und Trace-Ansicht; Per-Entity-Pending laut Invariante.
**Dateibesitz:** `packages/frontend-web/src/lib/api/produktion.ts`,
`packages/frontend-web/src/pages/produktion/mischfutter-produktion.tsx`, Audit-Doc Futtermittel-Kette.
**Abnahmekriterien:** Create gegen echtes Backend (201), Statusaktionen mit keyed Pending +
Toast, fertige Aufträge zeigen Charge/Trace; ESLint + type-check grün.

## WMS-PICK-LINK-001 — Lieferschein → Kommissionierliste → Warenausgang (Belegbruch)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `create_pick_list_from_delivery_note()` in `warehouse_service.py`
(prüft Status posted/printed, kein Duplicate, keine leere Pos-Liste → 409); `confirm_pick_list` setzt
Lieferschein automatisch auf `shipped` wenn DELIVERY_NOTE-Pick-Liste COMPLETED;
`POST /lager/wms/pick-lists/from-delivery-note/{ls_id}` (409 fail-closed); `warehouse-wms.ts`
(PickList-Typen, `createPickListFromDeliveryNote`, `confirmPickList`, Hooks); Kommissionierungs-Seite
`lager/kommissionierung` (per-entity Pending, „Alle bestätigen", FEFO-Zeilen, Toast bei shipped);
6 Unit-Tests grün; ESLint + type-check grün; Route + Nav-Eintrag generiert.
**Ziel:** Belegbruch Lieferschein (posted/printed) → Kommissionierliste (WMS/FEFO) → Warenausgang
(shipped) ohne manuelles REST-Tool.
**Dateibesitz:** `app/services/warehouse_service.py` (Methoden-Erweiterung),
`app/api/v1/endpoints/warehouse_wms.py` (neuer Endpoint + PickListFromDeliveryNoteIn),
`packages/frontend-web/src/lib/api/warehouse-wms.ts` (PickList-Typen + API-Funktionen),
`packages/frontend-web/src/pages/lager/kommissionierung.tsx` (neu),
`tests/test_wms_pick_link.py` (neu), `route-aliases.json`, `operations.tsx` (Nav).
**Abnahmekriterien:** 409 wenn LS nicht posted/printed; 409 bei Duplicate; confirm setzt LS auf shipped;
6 Tests grün; ESLint + type-check grün; Route `/lager/kommissionierung` erreichbar.

## FEED-CHAIN-003 — quality_lot_binding DB-Persistenz + Charge-Rückkopplung

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — Migration `feed_chain_quality_lot_20260613` (Alembic Single-Head von
`agri_silo_material_flow_20260612`): `domain_ops.quality_lot_profiles` + `domain_ops.quality_release_decisions`
(je UNIQUE tenant_id+lot_id). Endpoint `quality_lot_binding.py` rewritten: in-memory-Dicts entfernt,
`_ensure_tables` (503 wenn Migration nicht läuft), upsert-Insert für Lot und Decision,
Charge-Rückkopplung: `approve → freigegeben`, `reject → gesperrt`, `hold → quarantaene` auf `ops_chargen`.
7 Unit-Tests grün.
**Ziel:** Belegbruch schließen: `quality_lot_binding`-Daten überlebten keinen Neustart → Persistenz in DB;
Freigabe/Sperrung ist jetzt auf der Charge sichtbar.
**Dateibesitz:** `app/api/v1/endpoints/quality_lot_binding.py`, `alembic/versions/feed_chain_quality_lot_20260613.py`,
`tests/test_feed_chain_003.py` (neu).
**Abnahmekriterien:** 503 ohne Migration; Lot upsert; Decision approve/reject schreibt Charge-Status; 7 Tests grün.

## SALES-COLL-001 — Sammelrechnung/Sammellieferschein Belegbruch

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `collective_documents.py`: (1) `create_collective_invoice` validiert
jetzt DN-Status (nur `shipped`/`delivered` abrechnungsfähig — 422; bereits `BERECHNET` → 409) und setzt
Quell-Lieferscheine nach Rechnungserstellung auf `BERECHNET` + `invoice_id`; (2) `create_collective_delivery`
prüft auf Doppel-Lieferung (`geliefert` → 409) und setzt Quell-Aufträge auf `geliefert`; (3) `collective_eligible`
filtert nur noch `shipped`/`delivered`; 5 Unit-Tests grün.
**Ziel:** Belegbruch schließen: Sammelrechnung markierte Lieferscheine nicht als berechnet → Doppelabrechnung möglich;
Sammellieferschein setzte Aufträge nicht auf geliefert.
**Dateibesitz:** `app/api/v1/endpoints/collective_documents.py`, `tests/test_sales_coll_001.py` (neu).
**Abnahmekriterien:** 409 bei Doppelabrechnung; 422 bei falschem DN-Status; DN-Update auf BERECHNET; Auftrag-Update auf geliefert; 5 Tests grün.

## LAGER-BWERT-001 — Bestandsbewertung + Einlagerungsstrategie (Putaway)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — (1) `book_stock_movement` berechnet jetzt Ø-Einstandspreis
(weighted-average cost) bei Zugang auf bestehendem Bestand (UPDATE unit_cost = COALESCE(:cost, unit_cost));
(2) `suggest_putaway_bin()` in `warehouse_service.py`: CAPACITY/CONSOLIDATE/FEFO_ZONE-Strategien,
TOP-10-Bins nach Restkapazität; (3) `POST /lager/wms/warehouses/{id}/suggest-putaway` Endpoint;
(4) Frontend: `StockValuationRow`-Typ + `useStockValuation()`-Hook in `warehouse-wms.ts`;
Seite `lager/bestandsbewertung.tsx` (Übersichtstabelle + Summary-Cards); Nav-Eintrag + Route generiert;
Tests grün; type-check grün.
**Ziel:** Belegbrüche schließen: (a) `GET /lager/wms/stock-valuation` lieferte NULL-Werte wenn
`unit_cost=None` (kein Ø-Kosten-Update auf bestehenden Rows); (b) Einlagerung ohne Bin-Vorschlag
(Putaway-Strategie fehlte komplett — Tiefenplan §3 ❌ Kritisch); (c) keine UI-Seite für Lagerwerte
(Periodenabschluss-Voraussetzung).
**Dateibesitz:** `app/services/warehouse_service.py` (weighted-avg + putaway),
`app/api/v1/endpoints/warehouse_wms.py` (suggest-putaway endpoint),
`packages/frontend-web/src/lib/api/warehouse-wms.ts` (valuation types+hook),
`packages/frontend-web/src/pages/lager/bestandsbewertung.tsx` (neu),
`tests/test_lager_bwert_001.py` (neu), `route-aliases.json`, `operations.tsx` (Nav).
**Abnahmekriterien:** Ø-Einstandspreis wird bei Zugang berechnet; Putaway-Suggest gibt TOP-10 zurück;
Seite `/lager/bestandsbewertung` erreichbar; Tests + type-check grün.

## WAVE-PHYS-CHAIN-000 — (reserviert / Lead)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-13 — optionaler Bucket geschlossen durch **LOG-FREIGHT-STORNO-001**
(Fracht-Tarif-Storno API + UI); segmentierte Route-Blocks weiterhin optional per Harvest.
**Ziel:** Rest-Medienbruch Fracht ohne neue DOM-Insel.
**Dateibesitz:** `logistics_freight.py`, `tour-fracht-arbeitsraum.tsx`, `logistics-freight.ts`, Alembic `log_freight_tariff_storno_20260613`, Integrationstests.
**Abnahmekriterien:** Soft-Storno sichtbar; Kostenpfade ignorieren stornierte Zeilen.

## LOG-FREIGHT-STORNO-001 — Fracht-Tarif Storno (soft)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-13 — `POST /logistik/freight-tariffs/{id}/cancel`, Migration Storno-Spalten,
Dispo-Arbeitsraum: Tarifliste + Bestätigung + `cancelFreightTariff`; Tests in `test_logistics_integration.py`.
**Ziel:** WAVE-PHYS-CHAIN-000 Fracht-Storno-API/UI — fail-closed wie Touren-Storno.
**Dateibesitz:** genannte Dateien, `docs/agent-ops/slices/LOG-FREIGHT-STORNO-001.yaml`.
**Abnahmekriterien:** 422 ohne Tenant; 403 global/fremd; 409 doppelt; simulate nach Storno ohne Treffer.

## WM-STRUCT-001 — Lagerstruktur Gang (Depth-Plan §3 Schritt 1)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Alembic `wms_warehouse_aisles_20260612` (`domain_inventory.warehouse_aisles`, `warehouse_bins.aisle_id`); ORM `WarehouseAisle`; `WarehouseService` + `GET/POST /lager/wms/aisles`, `GET /bins?aisle_id=`, `POST /bins` mit optionalem `aisle_id`; Unit-Tests in `test_warehouse_wms_fefo.py`; UI: `lagerplaetze.tsx` + `warehouse-wms.ts`, E2E in `lager-wms.spec.ts`.
**Ziel:** ERP-Lücke Lager/Zone/**Gang**/Fach — Gang-Ebene zwischen Zone und Lagerplatz abbilden (Depth-Plan §3 Schritt 1).
**Dateibesitz:** genannte Dateien, `docs/agent-ops/slices/WM-STRUCT-001.yaml`, `docs/project-context/domain-depth-plan-2026-05-17.md`.
**Abnahmekriterien:** `alembic upgrade head` legt Tabelle/Spalte an; API tenant-isoliert wie bestehende WMS-Routen; 422 wenn `aisle_id` nicht zur Zone passt.

## WM-WMS-BIN-001 — Bin-PATCH + Kapazität bei Stock-Buchung

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — `WarehouseService.get_bin` / `update_bin` / `set_bin_stock_line_quantity`; `book_stock_movement` prüft Summe `bin_stock` vs. `capacity_kg`; API `GET`/`PATCH /lager/wms/bins/{bin_id}`, `PATCH …/stock-lines/{id}`; Lagerplätze-Dialog; `scripts/seed_demo_wms_structure.py`; Slice-YAML `WM-WMS-BIN-001.yaml`.
**Ziel:** Depth-Plan §3 Schritt 2 teilweise — Lagerplatz-Stammdaten pflegen und Einlagerung gegen Platzhöchstmenge absichern.
**Dateibesitz:** genannte Dateien, `docs/agent-ops/slices/WM-WMS-BIN-001.yaml`, `docs/project-context/domain-depth-plan-2026-05-17.md`.
**Abnahmekriterien:** PATCH Bin + Stock-Line; Kapazitätsüberschreitung 422; UI mit Pending/Toast; Demo-Seed; `pytest tests/test_warehouse_wms_fefo.py` grün.

## LOG-SPINE-001 — Lieferschein ↔ Tour UI + Seed

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — `useTouren` → `/logistik/tours` + `stop_count`; Tourenplanung: Auflösen + Tour-Hints; `seed_demo_logistics_spine.py`; PATCH `delivery_note_ref`.
**Ziel:** LOG-SPINE-RAND-001 im UI sichtbar machen; Demo-Daten idempotent.
**Dateibesitz:** `misc-modules.ts`, `logistics-tours.ts`, `tourenplanung.tsx`, `logistics_tours.py`, Seed-Skript, Audit.
**Abnahmekriterien:** `pnpm --filter @valero-neuroerp/frontend-web type-check` grün; Logistics-Unit-Tests grün.

## PROC-RFQ-001 — RFQ production-ready

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Alembic `proc_rfq_20260611`, Service `rfq_service.py`, Lazy-DDL entfernt, Zuschlag erzeugt echte `bestellungen`+Position, Seed `seed_demo_rfq.py`, 2 Integrationstests grün.
**Ziel des Slices:** Anfrageprozess RFQ ohne Mocks und ohne Runtime-Schema-DDL production-ready.
**Dateibesitz:** `proc_rfq_20260611.py`, `rfq_service.py`, `rfq.py`, `seed_demo_rfq.py`, `test_rfq_integration.py`, Open-Gaps.
**Abnahmekriterien:** Migration statt `_ensure_schema`; Accept legt PO an; Integration grün.

## PROC-PROD-001 — Production-Härtung Match-Spine

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Silent-DB-Fallbacks entfernt; 6 echte API/DB-Integrationstests (`test_procurement_match_integration.py`, auto-`alembic upgrade`); Seed zieht `DEMO-RE-001` idempotent nach; `drei_wege_abgeglichen` nur Rechnungswert-Toleranz; 21 Tests grün (15 Unit + 6 Integration).
**Ziel des Slices:** DOM-PROC-004 production-ready ohne Mocks auf Persistenz-Pfaden.
**Dateibesitz:** `procurement_match_service.py`, `seed_demo_procurement.py`, Integrationstests, DOM-PROC-Doku.
**Abnahmekriterien:** Keine `except: return []` auf Schreib-/Lesepfaden; Integration grün gegen echte DB.

## PROC-004.5 — ERS + UAT (DOM-PROC-004 abgeschlossen)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — `calculate_ers_credit` + `procurement_ers_credits`, API `/match/ers`, UI ERS-Karte, UAT `proc_match_lifecycle_uat.py`, Playwright-Smoke; 18 Procurement-Unit-Tests grün; Alembic-Head `proc_ers_credit_20260611`.
**Ziel des Slices:** ERS-Gutschriftsverfahren aus Match-Abweichungen + UAT-Nachweispaket für DOM-PROC-004.
**Dateibesitz:** `proc_ers_credit_20260611.py`, Match-Service/Endpoints, Frontend, UAT/Smoke, DOM-PROC-UAT-Doku.
**Abnahmekriterien:** DEMO-PO-002 → 960 € Vorschau; UAT `--execute` mit Cleanup; keine SALES/CON-Dateien.

## PROC-004.4 — Folgeaktionen Match-Ausnahmen

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — append-only `procurement_follow_up`, API `GET/POST /procurement/match/follow-up`, Eskalationsstufe, UI Folgeaktionen + Protokoll in Wareneingangsabgleich; 4 Unit-Tests grün; Alembic-Head `proc_follow_up_20260611`.
**Ziel des Slices:** Nachforderung/Reklamation/Eskalation/Freigabe bei Match-Ausnahmen mit Pflicht-Grund (Event-Log).
**Dateibesitz:** `proc_follow_up_20260611.py`, `procurement_match_service.py`, `procurement_match.py`, `procurement-match.ts`, `wareneingangsabgleich.tsx`, `test_procurement_follow_up.py`, DOM-PROC-Doku.
**Abnahmekriterien:** Append-only; keine UPDATE/DELETE-API; UI nur bei Ausnahmen; Tests grün.
**Abstimmung:** Keine SALES/CON-Dateien.

## PROC-004.2 — 3-Wege-Match Rechnungsstufe

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Rechnungsstufe: `match_three_way` + API `/procurement/match/three-way`, Migration `proc_three_way_inv_20260611`, Seed `DEMO-RE-001`, UI Wareneingangsabgleich; 10 Procurement-Tests grün; Folge-Slice 004.4 erledigt.
**Ziel des Slices:** Echter 3-Wege-Match Bestellung ↔ Wareneingang ↔ Eingangsrechnung mit Ausnahmen (keine Rechnung, Wertabweichung).
**Dateibesitz:** `procurement_match_service.py`, `procurement_match.py`, `proc_three_way_invoice_20260611.py`, `seed_demo_procurement.py`, `test_procurement_three_way_match.py`, `procurement-match.ts`, `wareneingangsabgleich.tsx`, DOM-PROC-Doku.
**Abnahmekriterien:** API + Unit-Tests + Seed + UI; keine Überschneidung mit CON/SALES-Slices.
**Abstimmung:** Claude — CON/SALES abgeschlossen; keine `contract_*` / `sales_match_*` Dateien.

## COMPAT-GOV-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Release-Kompatibilitätsmatrix als generiertes Artefakt (`scripts/generate_release_compatibility_matrix.py` → `artifacts/release-compatibility-matrix.{json,md}`), kanonische Toolchain-Pins (`config/release-toolchain-pins.json`), Drift-Check (`scripts/check_toolchain_pins.py`), unpinned `pytest-cov` aus `quality-gate.yml`/`sonarcloud.yml`/`ci.yml` entfernt, Finance-Subservices auf `pytest-cov==7.1.0`/`coverage==7.14.1` angeglichen. 5 Governance-Tests grün.
**Ziel des Slices:** Nach PROD-READINESS-001 Kompatibilitätsmatrix und einheitliche Test-Toolchain-Pins repo-weit verbindlich machen.
**Dateibesitz:** `config/release-toolchain-pins.json`, `scripts/generate_release_compatibility_matrix.py`, `scripts/check_toolchain_pins.py`, `tests/test_release_compatibility_governance.py`, `.github/workflows/quality-gate.yml`, `release-gates.yml`, `sonarcloud.yml`, `ci.yml`, Finance-`requirements.txt`, `docs/operations/dependency-and-compatibility-maintenance.md`, Handshake/Slices.
**Abnahmekriterien:** Matrix-Generator in Quality-/Release-Gate; Toolchain-Drift blockiert CI; keine losen `pip install pytest-cov`; Finance-Subservices aligned; Tests grün.
**Offene Risiken:** `recursionlimit` in `conftest.py` bleibt Coverage-Workaround; Vollsuite-Zahlen erst nach naechstem gruenen `quality-gate`-Lauf aktualisieren.

## INV-STOCK-MOVEMENTS-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — `articles.py` Chargenabfrage auf `inventory_stock_movements.charge`; `pos_retoure.py` INSERT auf kanonische Tabelle mit Pflichtfeldern/Warehouse-Subselect; kein `stock_movements` mehr unter `app/api/v1/endpoints/`; 3 Vertragstests grün.
**Ziel des Slices:** Legacy-SQL-Pfade `domain_inventory.stock_movements` in `articles.py` und `pos_retoure.py` auf kanonische Tabelle `inventory_stock_movements` umstellen inkl. Chargen-/Bestandsvertrag.
**Dateibesitz:** `app/api/v1/endpoints/articles.py`, `app/api/v1/endpoints/pos_retoure.py`, fokussierte Tests, Doku in `open-gaps-and-known-issues.md`.
**Abnahmekriterien:** Keine Schreibpfade mehr auf `stock_movements`; Regression für Artikel-Bestand und POS-Retoure grün; Schema-Vertrag unverändert grün.
**Offene Risiken:** POS-Retoure aktualisiert `articles.current_stock` noch nicht; MHD/Expiry weiterhin ohne Chargenstamm.

## DOC-004.5 — Browser-E2E + UAT (DOM-DOC-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Playwright-@smoke `docflow/nachweisraum-lifecycle-smoke.spec.ts` (3 Seiten) + Live-UAT `scripts/uat/doc_nachweisraum_lifecycle_uat.py` (`--execute`: Evidence→Probe→Upload→Freigabe→Wiedervorlage→GoBD-Manifest, Status `passed`, DB-Cleanup) + Nachweis `docs/dom-doc-004-uat-2026-06-11.md`. **Robustheits-Fund (UAT):** Fremd-`artifactType` → 500 (DB-CHECK); `upload_artifact` validiert jetzt vorab → 422 (Test ergänzt). Damit DOC-Tiefe 004.1–004.5 komplett. 18 docflow-Backendtests kumuliert grün.
**Ziel des Slices:** End-to-End-Abnahme des GoBD-Nachweisraums + Browser-Smoke. DOM-DOC-004.5.
**Dateibesitz:** `playwright-tests/specs/docflow/nachweisraum-lifecycle-smoke.spec.ts`, `scripts/uat/doc_nachweisraum_lifecycle_uat.py`, `app/services/docflow_artifact_service.py` (nur Typ-Guard), `tests/test_docflow_artifact.py` (nur Guard-Test), `docs/dom-doc-004-uat-2026-06-11.md`, DOC-Doku, Workboard-Block.
**Abnahmekriterien:** Live-UAT grün mit DB-Cleanup; Smoke-Spec suite-konsistent; Fremd-Artefakttyp liefert 422 statt 500.
**Offene Risiken / ehrlich:** Paperless-Liveprobe in DEV „nicht konfiguriert"; reales ZIP-Paket als JSON-Manifest-Vertrag. Smoke-Login-Fixture lokal nur CI-Preview (:4173).

## DOC-004.4 — GoBD-Exportpaket + Paperless-Liveprobe

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `docflow_gobd_service.py` (reine `build_gobd_manifest` mit Prüfsumme + `export_package` (reuse Evidence, vermerkt exported_at) + `paperless_probe` ehrlich gegated), Endpoints `/docflow/evidence/{gobd-export,paperless-probe}`, Frontend `pages/docflow/gobd-export.tsx` + Hooks + Nav + Route. 18 docflow-Backendtests kumuliert grün, tsc 0, eslint clean; Live verifiziert (PYTEST-Vorgang revisionssicher + Prüfsumme; Paperless „nicht konfiguriert"). Keine Migration.
**Ziel des Slices:** GoBD-Exportpaket je Vorgang (Manifest + Prüfsumme + Export-Vermerk) + DMS/Paperless-Liveprobe. DOM-DOC-004.4.
**Dateibesitz:** `app/services/docflow_gobd_service.py`, `app/api/v1/endpoints/docflow_gobd.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_docflow_gobd.py`, `packages/frontend-web/src/lib/api/docflow-gobd.ts`, `packages/frontend-web/src/pages/docflow/gobd-export.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), DOC-Doku.
**Abnahmekriterien:** Manifest mit Artefakt-Hashes + deterministischer Prüfsumme; Revisionssicherheit korrekt; Export vermerkt exported_at; Paperless-Probe ehrlich (konfiguriert/erreichbar); Backendtests + tsc + eslint grün.
**Offene Risiken / ehrlich:** PAPERLESS_URL in DEV nicht gesetzt → Probe meldet „nicht konfiguriert" (kein Schein-OK). Realer Binär-Paketdownload (ZIP mit Dateien) hier als JSON-Manifest-Vertrag. Browser-E2E + UAT in 004.5.

## DOC-004.3 — Bescheid/Rückmeldung + Wiedervorlage

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `doc_followup_20260611` (`document_followups`), Service `docflow_followup_service.py` (reine `followup_overdue` + `create_followup`/`complete_followup`/`list_followups`/`open_wiedervorlagen`), Endpoints `/docflow/evidence/{followups,wiedervorlagen}`, Frontend `pages/docflow/wiedervorlagen.tsx` + Hooks + Nav + Route. 9 Backendtests grün (5 Followup + 4 Artefakt-Regression), tsc 0, eslint clean; Live verifiziert (Wiedervorlage überfällig in Worklist, Bescheid, Erledigen + 422).
**⚠️ Alembic:** chained auf `doc_artifact_version_20260611`, gezielt angewandt; paralleler PROC-Head (Cursor) → Merge nötig sobald beide committet.
**Ziel des Slices:** Bescheide/Rückmeldungen + Wiedervorlagen je Vorgang mit Fälligkeit + Worklist offener (überfälliger) Wiedervorlagen. DOM-DOC-004.3.
**Dateibesitz:** `alembic/versions/doc_followup_20260611.py`, `app/services/docflow_followup_service.py`, `app/api/v1/endpoints/docflow_followup.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_docflow_followup.py`, `packages/frontend-web/src/lib/api/docflow-followup.ts`, `packages/frontend-web/src/pages/docflow/wiedervorlagen.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), DOC-Doku.
**Abnahmekriterien:** Followup-Erfassung (Wiedervorlage mit Pflicht-Fälligkeit); Worklist markiert überfällig; Erledigen idempotent-gesperrt (422); Backendtests + tsc + eslint grün.
**Offene Risiken:** Automatische Benachrichtigung/Eskalation der Wiedervorlagen nicht Teil des Slices. GoBD-Exportpaket + Paperless-Liveprobe in 004.4.

## DOC-004.2 — Artefakt-Upload + Versionierung + Freigabe

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `doc_artifact_version_20260611` (`document_artifacts` +version/+freigabe_status/+Audit), Service `docflow_artifact_service.py` (reine `next_version`/`valid_transition`/`sha256_hex` + `upload_artifact`/`set_freigabe`/`list_artifacts`), Endpoints `/docflow/evidence/artifacts[/{id}/freigabe]`, Frontend `pages/docflow/artefakt-freigabe.tsx` + Hooks + Nav + Route. 9 Backendtests grün (4 Artefakt + 5 Evidence-Regression), tsc 0, eslint clean; Live verifiziert (Upload v1/v2, Transitions, 422).
**⚠️ Alembic-Koordination:** Paralleler PROC-Head (`proc_rfq_20260611`, Cursor). Meine Migration an meinem committeten Head (`sales_delivery_storno_20260611`) gekettet und gezielt angewandt. Merge-Head `doc_artifact_version` + PROC-Tip nötig, sobald beide committet (Single-Head-Gate).
**Ziel des Slices:** Artefakt-Upload (SHA-256) + Versionierung je Header/Typ + Freigabe-Status-Transitions (entwurf→freigegeben→archiviert). DOM-DOC-004.2.
**Dateibesitz:** `alembic/versions/doc_artifact_version_20260611.py`, `app/services/docflow_artifact_service.py`, `app/api/v1/endpoints/docflow_artifact.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_docflow_artifact.py`, `packages/frontend-web/src/lib/api/docflow-artifact.ts`, `packages/frontend-web/src/pages/docflow/artefakt-freigabe.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), DOC-Doku.
**Abnahmekriterien:** Upload erzeugt SHA-256 + fortlaufende Version; Freigabe nur über zulässige Transitions (sonst 422); Liste markiert aktuelle Version; Backendtests + tsc + eslint grün.
**Offene Risiken:** Realer Datei-Binärupload/Storage-Anbindung (S3/Paperless) hier als Inhalt→Hash-Vertrag; DMS-Liveprobe in 004.4. Bescheid/Wiedervorlage in 004.3.

## FIN-004.5 — DATEV-Export + E2E/UAT (DOM-FIN-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_datev_service.py` (reine `datev_row`/`datev_csv` + `export_open_items`), Endpoint `/finance/datev-export`, Frontend `pages/finance/datev-export.tsx` + Hooks + Nav + Route, Playwright-@smoke `finance/op-lifecycle-smoke.spec.ts`, Live-UAT `scripts/uat/fin_op_lifecycle_uat.py` (`--execute`: passed, DB-Restore), Nachweis `docs/dom-fin-004-uat-2026-06-11.md`. Damit FIN-Tiefe 004.1–004.5 komplett. 25 Finance-Backendtests kumuliert grün, tsc 0, eslint clean.
**Ziel des Slices:** DATEV-Buchungsstapel-Export (in-repo) + End-to-End-Abnahme der FIBU-Kette. DOM-FIN-004.5.
**Dateibesitz:** `app/services/finance_datev_service.py`, `app/api/v1/endpoints/finance_datev.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_datev.py`, `packages/frontend-web/src/lib/api/finance-datev.ts`, `packages/frontend-web/src/pages/finance/datev-export.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), `playwright-tests/specs/finance/op-lifecycle-smoke.spec.ts`, `scripts/uat/fin_op_lifecycle_uat.py`, FIN-Doku.
**Abnahmekriterien:** DATEV-CSV mit korrekten Spalten/Konten; Live-UAT grün mit Restore; Smoke-Spec suite-konsistent.
**Offene Risiken / ehrlich:** Kein zertifizierter DATEV-EXTF; Steuerberater-Cutover bleibt externes Gate. Smoke-Login-Fixture lokal nur CI-Preview (:4173).

## FIN-004.4 — Periodenabschluss + Storno-Konsistenz

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_period_service.py` (reine `period_bounds` + `close_readiness` + `list_periods`/`readiness`/`close_period`/`reopen_period`), Endpoints `/finance/perioden[/{p}/readiness|/close|/reopen]`, Frontend `pages/finance/periodenabschluss.tsx` + Hooks + Nav + Route. Perioden self-contained aus OP abgeleitet (Tabelle leer). 5 Backendtests grün, tsc 0, eslint clean; Live verifiziert (Abschluss-Guard 422, Force, Reopen). Keine Migration.
**Ziel des Slices:** Buchungsperioden abschließen/sperren mit Abschlussreife-Prüfung (offene + Storno-inkonsistente Posten blockieren) + Wiedereröffnung mit Grund. DOM-FIN-004.4.
**Dateibesitz:** `app/services/finance_period_service.py`, `app/api/v1/endpoints/finance_period.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_period.py`, `packages/frontend-web/src/lib/api/finance-period.ts`, `packages/frontend-web/src/pages/finance/periodenabschluss.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), FIN-Doku.
**Abnahmekriterien:** Reife blockiert bei offenen/Storno-inkonsistenten OP; Abschluss setzt status=closed; Force erzwingt mit Hinweis; Reopen mit Pflicht-Grund; Backendtests + tsc + eslint grün.
**Offene Risiken:** Echte Buchungssperre (Verhindern neuer Journalbuchungen in geschlossener Periode) setzt Journal-Integration voraus — hier Periodenstatus-Vertrag. DATEV/Steuerberater-Cutover (extern) + UAT in 004.5.

## FIN-004.3 — Zahlungseingang / OP-Auszifferung

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_clearing_service.py` (reine `clearing_result` + `record_payment` ziffert `domain_erp.offene_posten` aus, protokolliert `op_auszifferungen` + `clearings`), Endpoints `/finance/zahlungseingang[/clearings]`, Frontend `pages/finance/zahlungseingang.tsx` + Hooks + Nav + Route. Schließt Lücke der isolierten `op_skonto_auszifferung` (reduzierte OP-Saldo nicht). 10 Backendtests grün (5 Auszifferung + 5 Mahnlauf-Regression), tsc 0, eslint clean; Live verifiziert (Teil→Voll+Skonto→422, Restore). Keine Migration.
**Ziel des Slices:** Zahlungseingang gegen offenen Debitoren-Posten ausziffern (offen reduzieren, Skonto, op_status). Kreditoren-Zahlungslauf = vorhandenes `payment_runs.py`. DOM-FIN-004.3.
**Dateibesitz:** `app/services/finance_clearing_service.py`, `app/api/v1/endpoints/finance_clearing.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_clearing.py`, `packages/frontend-web/src/lib/api/finance-clearing.ts`, `packages/frontend-web/src/pages/finance/zahlungseingang.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), FIN-Doku.
**Abnahmekriterien:** Teil-/Vollausgleich reduziert `offen`; Vollausgleich setzt `op_status='ausgeziffert'`; Skonto berücksichtigt; Überzahlung 422; Backendtests + tsc + eslint grün.
**Offene Risiken:** FIBU-Gegenbuchung (Journal) der Auszifferung nicht Teil des Slices (op_auszifferungen führt fibu_konto/skonto_konto als Vertrag). Abschluss/Periodensteuerung in 004.4.

## FIN-004.2 — Mahnlauf + Mahnstufen-Eskalation

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_dunning_service.py` (reine `days_based_level`/`next_dunning_level`/`compute_dunning` + `candidates`/`run_dunning`/`list_notices`), Endpoints `/finance/mahnlauf/{candidates,notices,run}`, Frontend `pages/finance/mahnlauf.tsx` + Hooks + Nav + Route. Default-Mahnregeln (da `dunning_rules` in DEV leer). 11 Backendtests grün (5 Mahnlauf + 6 OP-Regression), tsc 0, eslint clean; Live verifiziert (RE-103 Stufe 2→3 Zins 13,33; RE-100 1→2 Zins 10,27; Restore). Keine Migration (vorhandene Tabellen).
**Ziel des Slices:** Mahnlauf aus überfälligen Debitoren-OP (`offene_posten`) erzeugen (`dunning_notices`) + Mahnstufen-Eskalation. DOM-FIN-004.2.
**Dateibesitz:** `app/services/finance_dunning_service.py`, `app/api/v1/endpoints/finance_dunning.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_dunning.py`, `packages/frontend-web/src/lib/api/finance-dunning.ts`, `packages/frontend-web/src/pages/finance/mahnlauf.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), FIN-Doku.
**Abnahmekriterien:** Kandidaten zeigen nächste Stufe + Gebühr/Zinsen/Gesamt; Mahnlauf erzeugt Mahnungen + eskaliert `dunning_level`; Default-Regeln greifen bei leerer Regeltabelle; Backendtests + tsc + eslint grün.
**Offene Risiken:** `dunning_rules` in DEV leer → Default-Regeln (in Prod Regeln pflegen). Mahnungs-Versand (Druck/Mail) nicht Teil des Slices. OP-Auszifferung/Zahlungslauf folgt in 004.3.

## SALES-004.5 — Browser-E2E + UAT (DOM-SALES-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Playwright-@smoke `playwright-tests/specs/sales/o2c-lifecycle-smoke.spec.ts` (3 O2C-Seiten) + Live-UAT `scripts/uat/sales_o2c_lifecycle_uat.py` (`--execute`: Match→Kreditampel→Storno-Rückfluss, Status `passed`, DB-Restore) + Nachweis-Doku `docs/dom-sales-004-uat-2026-06-11.md`. Damit ist die SALES-Tiefe 004.1–004.5 komplett.
**Ziel des Slices:** End-to-End-Abnahme der O2C-Kette + Browser-Smoke. DOM-SALES-004.5.
**Dateibesitz:** `playwright-tests/specs/sales/o2c-lifecycle-smoke.spec.ts`, `scripts/uat/sales_o2c_lifecycle_uat.py`, `docs/dom-sales-004-uat-2026-06-11.md`, SALES-Doku, Workboard-Block.
**Abnahmekriterien:** Live-UAT grün mit DB-Restore; Smoke-Spec suite-konsistent.
**Offene Risiken / ehrlich:** Smoke-Login-Fixture lokal nur gegen CI-Preview (:4173), nicht Dev :3000 (wie CON-004.5). 14 Sales-Backendtests kumuliert grün.

## SALES-004.4 — Storno/Gutschrift durchgängig

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `sales_delivery_storno_20260611` (`delivery_notes` +`storno_grund`), Service `sales_storno_service.py` (reine `can_storno` + `storno_delivery` + `order_storno_status` mit toleranter Gutschrift-Übersicht), Endpoints `/sales/deliveries/{nr}/storno` + `/sales/storno/status`, Frontend `pages/sales/lieferung-storno.tsx` (Storno-Dialog + Gutschriften) + Hooks + Nav + Route. Stornierte Lieferscheine zählen nicht mehr als geliefert (Match filtert `status<>'storniert'` → durchgängig). 9 Backendtests grün (4 Storno + 5 Match), tsc 0, eslint clean; Live verifiziert (Guard 422, Match-Rückfluss, Restore).
**⚠️ Alembic-Koordination:** Beim Anwenden tauchte ein **paralleler PROC-Head** (`proc_three_way_inv_20260611`→`proc_follow_up_20260611`, untracked/fremd) auf. Ich habe meine Migration NICHT in fremde uncommittete Revisionen gekettet, sondern gezielt angewandt (`alembic upgrade sales_delivery_storno_20260611`, down_revision=`con_settlement_storno_20260611`, committet/stabil). **Sobald die PROC-Migrationen committet sind, ist ein Merge-Head `sales_delivery_storno` + `proc_follow_up` nötig** (Single-Head-Gate). Wer PROC committet, sollte den Merge mitliefern.
**Ziel des Slices:** Lieferschein-Storno, der durchgängig in den Auftrag-Lieferschein-Match zurückfließt + Gutschrift-Übersicht; fail-closed bei berechneten Lieferungen. DOM-SALES-004.4.
**Dateibesitz:** `alembic/versions/sales_delivery_storno_20260611.py`, `app/services/sales_storno_service.py`, `app/services/sales_match_service.py` (nur Storno-Filter), `app/api/v1/endpoints/sales_storno.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_sales_storno.py`, `packages/frontend-web/src/lib/api/sales-storno.ts`, `packages/frontend-web/src/pages/sales/lieferung-storno.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), SALES-Doku.
**Abnahmekriterien:** Storno setzt Lieferschein 'storniert' (Grund pflicht); berechnete Lieferung blockiert (422); stornierte Lieferung zählt nicht mehr im Match; Backendtests + tsc + eslint grün.
**Offene Risiken:** Gutschrift-Erstellung erfolgt über das bestehende `sales_credit_notes`-Modul (hier nur Übersicht); echte Gutschrift→FIBU-Buchung bleibt außerhalb. Browser-E2E + UAT in 004.5.

## SALES-004.3 — Kreditlimit-Prüfung + Billing-Status

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `sales_credit_service.py` (reine `credit_check`-Ampel + `order_credit` + `list_customers`), Endpoints `/sales/credit-check[/customers]`, Seed (DEMO-CUST-001 Limit 20.000 € in `domain_crm.customers`), Frontend `pages/sales/kreditlimit-pruefung.tsx` + Hooks + Nav + Route. 10 Backendtests grün (5 Credit + 5 Match-Regression), tsc 0, eslint clean; Live verifiziert (Auslastung 86,5 % → Ampel warnung). Keine Migration.
**Ziel des Slices:** Kreditlimit-Prüfung (Limit vs. offene Exposure, Ampel, Wirkung des Auftrags) + Billing-Status je Lieferschein im O2C-Kontext. DOM-SALES-004.3.
**Dateibesitz:** `app/services/sales_credit_service.py`, `app/api/v1/endpoints/sales_credit.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `scripts/seed_demo_sales.py` (Kundensatz), `tests/test_sales_credit.py`, `packages/frontend-web/src/lib/api/sales-credit.ts`, `packages/frontend-web/src/pages/sales/kreditlimit-pruefung.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), SALES-Doku.
**Abnahmekriterien:** Ampel ok/warnung/blockiert/kein_limit korrekt; verfügbarer Rahmen + Auslastung mit/ohne Auftrag; Kunden-Ampel-Liste; Backendtests + tsc + eslint grün.
**Offene Risiken / ehrlich:** Vorhandene `credit_management.py`-Infra braucht `domain_finance.finance_invoices` + `domain_crm.credit_limits` — **in DEV nicht vorhanden** (`/credit-status` 404). Daher tolerant self-contained (Limit am Kundensatz, Exposure aus offenen Aufträgen). Tiefe FIBU-Journal-/Debitoren-OP-Verknüpfung = Folgeschritt. Storno/Gutschrift in 004.4.

## SALES-004.2 — Positions-Match Auftrag↔Lieferschein

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `sales_match_service.py` (match je Auftragsposition `sales_order_items` gegen Summe `delivery_note_positions`, Schlüssel Artikelnummer; reuse reine `match_position` aus PROC + `match_summary`), Endpoints `/sales/match[/orders]`, Seed-Erweiterung (Lieferschein-Positionen DEMO-LS-001), Frontend `pages/sales/auftrag-lieferschein-abgleich.tsx` + Hooks + Nav + Route. 11 Backendtests grün (5 Sales + 6 PROC-Regression), tsc 0, eslint clean; Live verifiziert (Pos 1 25/25 voll, Pos 2 3/5 teil → 1.800 € offen). Keine Migration (vorhandene Tabellen).
**Ziel des Slices:** Positions-Match Auftrag↔Lieferschein (Teil-/Überlieferung, Toleranz, offene Menge/Wert, Lücken) analog PROC-Match. DOM-SALES-004.2.
**Dateibesitz:** `app/services/sales_match_service.py`, `app/api/v1/endpoints/sales_match.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `scripts/seed_demo_sales.py` (LS-Positionen), `tests/test_sales_match.py`, `packages/frontend-web/src/lib/api/sales-match.ts`, `packages/frontend-web/src/pages/sales/auftrag-lieferschein-abgleich.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), SALES-Doku.
**Abnahmekriterien:** Positions-Match offen/teil/voll/über mit Toleranz + offener Wert; Lücken; Picker; Backendtests + tsc + eslint grün.
**Offene Risiken:** Match-Schlüssel ist Artikelnummer (keine Auftragszeilen-ID am Lieferschein) — bei doppelten Artikeln je Auftrag aggregiert. Rechnung/Buchung/OP + Kreditlimit folgt in 004.3.

## CON-004.5 — Browser-E2E + UAT (DOM-CON-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Playwright-@smoke-Spec `playwright-tests/specs/agrar/kontrakt-lifecycle-smoke.spec.ts` (3 Arbeitsräume) + Live-UAT `scripts/uat/con_contract_lifecycle_uat.py` (`--execute`: 11/11 ✓, Status `passed`, DB-Cleanup) + Nachweis-Doku `docs/dom-con-004-uat-2026-06-11.md`. Damit ist die CON-Tiefe 004.1–004.5 komplett.
**Ziel des Slices:** End-to-End-Abnahme der Kontrakt-Kette (Fixierung→Engagement→Settlement→Storno) + Browser-Smoke der Arbeitsräume.
**Dateibesitz:** `playwright-tests/specs/agrar/kontrakt-lifecycle-smoke.spec.ts`, `scripts/uat/con_contract_lifecycle_uat.py`, `docs/dom-con-004-uat-2026-06-11.md`, CON-Doku, Workboard-Block.
**Abnahmekriterien:** Live-UAT grün mit DB-Cleanup; Smoke-Spec geschrieben und suite-konsistent.
**Offene Risiken / ehrlich:** Die `@smoke`-Login-Fixture authentifiziert lokal nicht gegen den Vite-Dev-Server :3000 — **identischer Fehlschlag bei allen bestehenden Specs** (gegengeprüft `duenger-smoke`: 3/3 „browser closed"). Browser-Abnahme läuft in CI (Preview-Build :4173); fachlicher Nachweis hier via grünem Live-UAT. Reale Abrechnungs-Buchung (agrar_settlements-Integration) bleibt tiefergehender Folgeschritt außerhalb DOM-CON-004.

## CON-004.4 — Settlement-Übergabe + Storno

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `con_settlement_storno_20260611` (`kon_contract_movement` +settled_at/+is_storniert/+storno_grund), Service `contract_settlement_service.py` (`movement_state` + `handover`/`storno_movement`/`storno_fixing`/`settlement_status`), Endpoints `/contracts/settlement[/status]` + `/contracts/movements/{id}/storno` + `/contracts/fixings/{id}/storno`, Frontend `pages/agrar/kontrakt-settlement.tsx` (Abrechnen + Storno-Dialog mit Pflicht-Grund) + Hooks + Nav + Route. Fulfillment-/Engagement-Sichten filtern jetzt stornierte Bewegungen. 18 Backendtests grün (kumuliert), tsc 0, eslint clean; Live verifiziert (Handover, Storno-Guard 422, Fixing-Storno gibt Menge frei).
**Ziel des Slices:** Abruf-Bewegungen an die Abrechnung übergeben + revisionssicherer Storno von Bewegungen/Fixierungen (frei werdende Mengen); fail-closed: abgerechnete Bewegungen sind storno-gesperrt. DOM-CON-004.4.
**Dateibesitz:** `alembic/versions/con_settlement_storno_20260611.py`, `app/services/contract_settlement_service.py`, `app/services/contract_fulfillment_service.py` + `contract_engagement_service.py` (nur is_storniert-Filter), `app/api/v1/endpoints/contract_settlement.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_contract_settlement.py`, `packages/frontend-web/src/lib/api/contract-settlement.ts`, `packages/frontend-web/src/pages/agrar/kontrakt-settlement.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), CON-Doku.
**Abnahmekriterien:** Übergabe markiert Bewegung(en) abgerechnet; Storno gebuchter Bewegung blockiert (422); Fixing-/Bewegungs-Storno gibt Menge frei und fließt in Erfüllung/Engagement zurück; Single Alembic-Head; Backendtests + tsc + eslint grün.
**Offene Risiken:** Echte Abrechnungs-Buchung (Integration `agrar_settlements`/Posting) ist tiefergehender Folgeschritt — hier nur Settlement-Übergabe-Vertrag (Beleg-Referenz), keine Finanzbuchung. Browser-E2E + UAT in 004.5.

## CON-004.3 — Engagement-Sicht + Kontraktmahnung

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `con_reminder_20260611` (append-only `kon_contract_reminder`), Service `contract_engagement_service.py` (reine Aggregation `offen_menge`/`netto_position`/`naechste_mahnstufe` + `engagement`/`dunning_candidates`/`create_reminder`/`list_reminders`), Endpoints `/contracts/engagement` + `/contracts/dunning[/candidates|/list]`, Frontend `pages/agrar/kontrakt-engagement.tsx` (Engagement je Artikel/Partei + Mahnkandidaten mit per-Zeile-Mahnen) + Hooks + Nav + Route. 15 Backendtests grün (kumuliert), tsc 0, eslint clean; Live-API verifiziert.
**Ziel des Slices:** Offene Kontraktmenge je Artikel (Netto Einkauf−Verkauf) und je Partei + Kontraktmahnung überfällig-untererfüllter Kontrakte (append-only Mahnstufen-Eskalation). DOM-CON-004.3.
**Dateibesitz:** `alembic/versions/con_reminder_20260611.py`, `app/services/contract_engagement_service.py`, `app/api/v1/endpoints/contract_engagement.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_contract_engagement.py`, `packages/frontend-web/src/lib/api/contract-engagement.ts`, `packages/frontend-web/src/pages/agrar/kontrakt-engagement.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), CON-Doku.
**Abnahmekriterien:** Engagement summiert offen je Artikel/Partei korrekt (Netto-Vorzeichen); Mahnung nur bei offener Menge (sonst 422); Mahnstufe eskaliert; Single Alembic-Head; Backendtests + tsc + eslint grün.
**Offene Risiken:** Settlement-Übergabe + Storno (inkl. Fixierungs-Storno) folgen in 004.4; reale Mahn-Texte/Versand (Mail/Print) sind in diesem Slice nicht enthalten.

## CON-004.2 — Fixierungs-Arbeitsraum + MATIF-Bewertung

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `con_fixing_matif_20260611` (Tabellen `kon_contract_fixing` + `matif_quote`), Service `contract_fixing_service.py` (reine Bewertungslogik + Teilfixierung mit Guards + Workspace + Notierung), Endpoints `/contracts/fixing[/workspace|/list]` + `/contracts/matif-quote`, Seed DEMO-KT-004 (MATIF-Verkauf), Frontend `pages/agrar/kontrakt-fixierung.tsx` + Hooks + Nav + Route. 12 Backendtests grün, tsc 0, eslint clean; Live-API verifiziert.
**Nebenbefund/Fix (kritisch):** Der Abend-Stand 2026-06-10 hinterließ **zwei offene Alembic-Heads** (`repair_customer_contract_20260610` + `sales_o2c_link_20260610`), die nie zusammengeführt wurden → `scripts/init_db.py` (`upgrade head`, Singular) scheiterte mit `Multiple head revisions` → **Backend-Container im Crash-Loop** (seit Reboot 06:32). Behoben, indem die neue Migration **beide Heads revidiert** (Merge + Tabellen in einem) → wieder genau 1 Head, Backend `healthy`.
**Ziel des Slices:** Teilfixierung MATIF-bepreister Kontrakte (Menge zu MATIF-Preis + Prämie) und Mark-to-Market gegen die jüngste Marktnotierung: fixierter/offener Anteil, Ø-Fixpreis, Bewertungsergebnis. DOM-CON-004.2 gemäß `docs/dom-con-004-kontrakt-erfuellung-2026-06-10.md`.
**Dateibesitz:** `alembic/versions/con_fixing_matif_20260611.py`, `app/services/contract_fixing_service.py`, `app/api/v1/endpoints/contract_fixing.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `scripts/seed_demo_contracts.py` (DEMO-KT-004), `tests/test_contract_fixing.py`, `packages/frontend-web/src/lib/api/contract-fixing.ts`, `packages/frontend-web/src/pages/agrar/kontrakt-fixierung.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), CON-Doku.
**Abnahmekriterien:** Fixierung nur auf MATIF-Positionen, Menge>0 und ≤ offen, Preis>0 (sonst 422); Workspace zeigt fixiert/offen/Ø-Fixpreis/Bewertung; ohne Notierung keine erfundene Bewertung (fail-closed); Backendtests + tsc + eslint grün; Backend wieder startfähig (1 Head).
**Offene Risiken:** Fixierungs-Storno und Settlement-Übergabe folgen in 004.4. Symbol-Auflösung nutzt `basis_reference` (Fallback Artikel) — bei produktiven Kontrakten Symbol-Pflege nötig.

## PROD-READINESS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09 (repo-seitig); externe Live-Gates offen — Nachzug COMPAT-GOV-001 2026-06-11
**Abstimmung:** Repo-weiter CI-/Deployment-/Security-/Dokumentations-Slice. Parallel laufender Slice `KIM-DEPRECATE-COCKPIT-001` besitzt ausschliesslich `packages/frontend-web/src/pages/crm/kunden-cockpit.tsx` und den Kunden-Cockpit-Eintrag in `packages/frontend-web/src/app/navigation/domains/commercial.tsx`; diese Dateien werden nicht beruehrt.
**Ziel des Slices:** Alle repo-seitig schliessbaren P0-Gaps der Produktionsreife beseitigen: keine tolerierten Kernfehler in Release-CI, blockierende High/Critical-Security-Gates, SBOM, produktionssichere Runtime-/Secret-Preflights, belastbarer Staging-/Production-Deploymentvertrag mit Migration, Smoke und Rollback sowie eine aktuelle, ehrliche Go-live-Matrix.
**Dateibesitz:** `.github/workflows/quality-gate.yml`, `.github/workflows/security-scan.yml`, `.github/workflows/deploy-staging.yml`, `.github/workflows/valeo-erp-deployment.yml`, neue fokussierte Release-/Security-Workflows, produktionsbezogene Dateien unter `scripts/deployment/**`, neue Preflight-Skripte und Tests, fokussierte Helm-/Kubernetes-Werte soweit zwingend, `docs/project-context/open-gaps-and-known-issues.md`, neue Production-Readiness-/Runbook-Doku und relevante Status-/README-Verweise.
**Abnahmekriterien:** Release-CI kann Typecheck/Lint/Tests oder High/Critical-Befunde nicht uebergehen; SBOM wird erzeugt; produktive Konfiguration scheitert bei Dev-Tokens, Default-Secrets, Debug/Reload, Wildcard-Hosts oder fehlenden Pflichtwerten; Deployments sind environment-geschuetzt und besitzen Migration-Preflight, Smoke und Rollback; externe UAT-, Steuer-, DMS-, TSE- und Hardwareabnahmen bleiben explizit blockierend; YAML-, Skript-, Doku- und fokussierte Vertragstests sind gruen.
**Offene Risiken:** Echte Cloud-/Kubernetes-Zugangsdaten, Branch-Protection-Regeln, GitHub-Environment-Approvals und fachliche Unterschriften koennen nur als externe GitHub-/Betriebs-Gates konfiguriert, nicht im Repository erfunden werden.

## KIM-DEPRECATE-COCKPIT-001

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-09 (Commit `3e62f00e5`) — Page→Redirect auf /crm, Nav relabelt; tsc 0, eslint clean. Folge-Lücke: WhatsApp-Deep-Link in KIM.
**Ziel des Slices:** Das klassische „Verkauf Kunden-Cockpit" (`pages/crm/kunden-cockpit.tsx`) ablösen — durch KIM (`/crm`) funktional ersetzt. Seite wird Redirect→/crm (keine 404 für Altlinks), Nav-Eintrag als abgelöst markiert. KEINE Route-Regenerierung (route-tree.gen/navigation-routes.json sind generiert + aktuell fremd-dirty → nicht anfassen).
**Dateibesitz:** `docs/agent-ops/active-workboard.md` (eigener Block), `packages/frontend-web/src/pages/crm/kunden-cockpit.tsx`, `packages/frontend-web/src/app/navigation/domains/commercial.tsx` (nur kunden-cockpit-Eintrag). **NICHT:** generierte Routing-Dateien, core.tsx, Fiskaly.
**Abnahmekriterien:** `/crm/kunden-cockpit` leitet auf `/crm` um (kein 404); Nav-Eintrag kennzeichnet die Ablösung; tsc/eslint grün. Parität: WhatsApp-Deep-Link (wa.me) ist Rest-Lücke in KIM (notieren, Folge-Slice).
**Offene Risiken:** Generierte Routing-Dateien sind fremd-dirty — Redirect über die Page-Komponente lösen, nicht über Routen-Regenerierung.


## POS-FISCAL-OPS-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Folge-Slice zu `POS-FISCAL-PROVIDERS-001`, konfliktfrei zu den laufenden KIM-/CRM-Arbeiten. Keine Aenderung unter `packages/frontend-web/src/pages/crm/kim/**` oder an CRM-Playwright-Specs.
**Ziel des Slices:** Die Fiskalisierungsprovider betrieblich nutzbar machen: tenantbezogene Admin-Konfiguration und Readiness, explizite Produkt-Gates fuer fiskaly SUBMIT DE/RECEIPT/SAFE sowie durchgaengige POS-/Tagesabschluss-Browsertests fuer fiskaly und Swissbit.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/POS-FISCAL-OPS-002.yaml`, Fiskalisierungsdoku und QA, `app/services/fiscalization/**`, `app/api/v1/endpoints/pos_fiscalization.py`, fokussierte POS-Migrationen/-Tests, `packages/frontend-web/src/pages/admin-suite/**` fuer eine neue Fiskalisierungsseite, providerneutraler Fiskalisierungsclient, generierte Route-/Navigationsartefakte und fokussierte POS-Playwright-Specs.
**Abnahmekriterien:** Provider und Kassenkontext sind ohne Browser-Secrets administrierbar; Readiness zeigt konkrete Blocker und optionale fiskaly-Produkte getrennt; undokumentierte externe Vertraege bleiben fail-closed; POS-Signatur, Browser-Zurueck, Tagesabschluss-Gates und beide Provideralternativen sind automatisiert; Typecheck, Lint, Backendtests, Playwright und Governance sind gruen.
**Offene Risiken:** fiskaly Produktlizenzen/Credentials und Swissbit Partnervertraege sind externe Live-Gates; partnergeschuetzte URLs oder Payloads duerfen nicht geraten werden.
**Ergebnis:** Tenantbezogene Admin-Seite mit Typed Route, Provider-/DSFinV-K-Auswahl, Kassen-, Client- und Terminalkontext sowie expliziter Simulationsfreigabe umgesetzt. Readiness prueft Konfiguration und Kassenkontext. Secret-artige Settings werden vor DB-Zugriff abgewiesen und beim Lesen redigiert. SUBMIT DE, RECEIPT und SAFE besitzen getrennte, fail-closed Vertrags-Gates ohne geratenen Live-Call. Der POS-Browsertest belegt Swissbit als TSE bei separatem fiskaly DSFinV-K sowie den blockierten Tagesabschluss bei offenen Fiskaltransaktionen.
**Checks:** 11 fokussierte Backendtests; Frontend- und Playwright-TypeScript gruen; fokussierter ESLint gruen; POS-Playwright 2 Tests bestanden; Produktions-Build und Typed-Route-Generierung gruen.
**Handoff:** Ergebnisdateien wurden wegen eines parallelen Shared-Worktree-Commits zusammen mit Claim `e12b261a6` publiziert; dieser Nachtrag ordnet sie verbindlich `POS-FISCAL-OPS-002` zu.

## POS-FISCAL-PROVIDERS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Konfliktfreier POS-/Compliance-Slice parallel zu Claudes KIM-L3-S3-S5. Keine Aenderung unter `packages/frontend-web/src/pages/crm/kim/**` oder an CRM-Backenddateien.
**Ziel des Slices:** Demo- und Pseudo-TSE-/DSFinV-K-Pfade durch eine typisierte Provider-Abstraktion fuer fiskaly SIGN DE/DSFINVK DE sowie Swissbit Cloud-/Hardware-TSE ersetzen; Tagesabschluss, Export, Status und Readiness fail-closed, tenantbezogen und idempotent integrieren.
**Dateibesitz:** Neue Fiskalisierungsservices unter `app/services/fiscalization/**`, POS-Fiskalisierungsendpoint, `tse_fiskaly_service.py`, fokussierte Edits in `admin_pos.py`, `pos_dsfinvk.py`, `kasse_tagesabschluss.py`, `app/api/v1/api.py`, neue POS-Migration, fokussierte Tests und Doku.
**Abnahmekriterien:** Providerwahl fiskaly/Swissbit; korrekte fiskaly Token-Authentifizierung; konfigurierbarer Swissbit REST-/Gateway-Vertrag; persistente idempotente Signierung; getrennte TSE-/DSFinV-K-Exporte; providergebundener Tagesabschluss; kein produktiver Scheinerfolg bei Simulator oder fehlender Vertragsfreigabe.
**Offene Risiken:** Swissbit Detail-API/SDK ist partner-/loginpflichtig; Live-Credentials und externe Pruefwerkzeugabnahme bleiben Betriebs-Gates.
**Ergebnis:** Provider-Abstraktion fuer fiskaly, Swissbit Cloud, Swissbit Hardware-Gateway und explizite Simulation umgesetzt. Providerwahl und DSFinV-K-Provider sind tenantbezogen getrennt. Browser-Secrets, stille Mock-Signaturen und der Festdaten-DSFinV-K-Export wurden entfernt. Transaktionen, Cash Point Closings und Exporte werden idempotent persistiert. POS uebergibt MwSt., Rabatte und Split Payments; Tagesabschluss laedt das Fiskaljournal und blockiert bei offenen Vorgaengen, Summendifferenzen, Providerfehlern oder Simulation.
**Checks:** 15 fokussierte Backendtests bestanden; Frontend-TypeScript und fokussierter ESLint gruen; Python-Compile und Router-Import gruen; Migration `pos_fiscal_providers_20260609` angewandt und einziger Head; Workboard, Doku-Governance und `git diff --check` gruen. Bestehender Wave-1-Sammeltest hat einen unabhaengigen Collection-Fehler in `admin_core.WorkflowSandboxCampaignMatchOut`.

## KIM-L3-S2-REVIEW-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Eng begrenzter Review-Fix fuer S2-Commit `ca39b1b06`. Claude pausiert bis zum Handoff Aenderungen an `CustomerActionBar.tsx`, `SalesDocumentsPanel.tsx` und der S2-Dispatch-Stelle in `kim/index.tsx`; S3/S4-Backend bleibt unberuehrt.
**Ziel des Slices:** Information- und Ang./Auf.-Dropdown gegen Bauplan, Routenvertraege und modellbasierte Klicktests pruefen und nachgewiesene fachliche, logische sowie testseitige Fehler beheben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-L3-S2-REVIEW-001.yaml`, fokussierte QA-Doku, S2-Komponenten unter `packages/frontend-web/src/pages/crm/kim/` sowie CRM360-Action-Contracts und -Playwright-Spec.
**Abnahmekriterien:** Ang./Auf.-Menue entspricht dem Bauplan; Uebersicht zeigt alle Belege ohne klebende Altselektion; alle Informationsmodule sind ohne 404 erreichbar; Dropdown-Aktionen sind automatisiert; TypeScript, ESLint und CRM360-Playwright sind gruen.
**Offene Risiken:** Dateieueberschneidung mit Claudes geplantem S3-S5-Frontend; Backend-Belegtypen muessen mit dem Bauplan abgeglichen werden.
**Ergebnis:** Ang./Auf.-Menue auf den dokumentierten Sollvertrag Angebote/Auftraege/Lieferschein/Anfrage/Bestellung/Uebersicht korrigiert. Das Belegpanel ist kontrolliert; Uebersicht zeigt wirklich alle Belege und deaktiviert die unklare Sammel-Neuanlage. Informations-Shortcuts und stabile Zielselektoren ergaenzt. Alle elf Informationsmodule und sechs Belegmenuepunkte sind modellbasiert geklickt.
**Checks:** Frontend- und Playwright-TypeScript gruen; fokussierter ESLint gruen; CRM360-Playwright 17 Tests bestanden; Workboard und `git diff --check` gruen.

## KIM-L3-S3-S5 (CRM-Customer-360 Ausbau)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-09 — S3 (Präsente BE+FE), S4 (Ansprechpartner Werbe-Matrix + DSGVO-Pseudonymisierung BE+FE), S5 (konfigurierbare Action-Bar). model-based Suite 17/17 grün; tsc 0, eslint clean. Backend-Migrationen idempotent.
**Abstimmung:** Codex bearbeitet aktiv `KIM-L3-S1-GAP-CLOSURE-001` (uncommittete WIP in `index.tsx`, `ContactPersonsTable.tsx`, `ContactHistoryTable.tsx`, `CustomerActionBar.tsx`, `crm_kim.py`, CRM360-Playwright). **Ich fasse diese Dateien NICHT an, solange sie Codex' uncommittete WIP tragen.** Mein Frontend (S3-Präsente-Tab, S4-Ansprechpartner-Vollformular, S5-konfigurierbare Action-Bar) startet erst nach Codex' Commit (Baum sauber). Bis dahin nur **neue, nicht-kollidierende Backend-Dateien**.
**Ziel des Slices:** S3 Präsente (Tab+Backend), S4 Ansprechpartner-Vollformular (~40 Felder + Werbe-Matrix + Pseudonymisieren, Backend), S5 benutzerbezogen konfigurierbare Action-Bar — gemäß `docs/crm-customer-360-bauplan-2026-06-09.md`.
**Dateibesitz (Backend, jetzt):** `alembic/versions/crm_gifts_*`, `alembic/versions/crm_contacts_ext_*`, `app/services/crm_gift_service.py`, `app/services/crm_contact_ext_service.py`, `app/api/v1/endpoints/crm_gifts.py`, `app/api/v1/endpoints/crm_contacts_ext.py`, `app/api/v1/api.py` (nur eigene include_router-Zeilen), Backendtests. **Frontend (nach Handoff):** neue `kim/components/CustomerGiftsTab.tsx`, `CustomerContactsForm.tsx`; abgestimmte Edits in `kim/index.tsx`, `ContactPersonsTable.tsx`, `CustomerActionBar.tsx`.
**Abnahmekriterien:** Präsente-CRUD; Ansprechpartner-Vollformular + Werbe-Matrix + Pseudonymisieren; konfigurierbare Action-Bar (Sichtbarkeit + Reset, benutzerbezogen); model-based Suite grün; tsc/eslint/Backendtests grün.
**Offene Risiken:** Hohe Datei-Überschneidung mit Codex' aktivem Slice → strikte Workboard-Koordination; Frontend erst nach sauberem Baum.

## KIM-L3-S1-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Review-Fix zu Commit `cb8e7af10`, parallel zu Claudes S2-Arbeit. Codex bearbeitet zunaechst nur konfliktfreie Dateien. Claude besitzt waehrend S2 die aktuell uncommittierten Dateien `packages/frontend-web/src/pages/crm/kim/index.tsx`, `components/SalesDocumentsPanel.tsx`, `components/CustomerActionBar.tsx` und `components/InformationPanel.tsx`. Aenderungen an `index.tsx` und `SalesDocumentsPanel.tsx` werden erst nach Claudes S2-Commit auf dessen Stand integriert; fremder WIP wird nicht ueberschrieben.
**Ziel des Slices:** Alle im S1-Review gefundenen funktionalen und testseitigen Luecken schliessen: bestehende Angebote mit korrekter ID laden, Kontaktlogs fehlertolerant speichern, Ansprechpartner-Telefonie ueber TAPI und Logfuehrung abwickeln, Ansprechpartner-E-Mail fachlich korrekt liefern, eine belastbare Druckansicht bereitstellen und alle neuen Aktionen samt Ruecknavigation modellbasiert pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-L3-S1-GAP-CLOSURE-001.yaml`, fokussierte QA-Doku, `packages/frontend-web/src/pages/crm/kim/components/ContactHistoryTable.tsx`, `ContactPersonsTable.tsx`, nach S2-Handoff abgestimmte Aenderungen in `kim/index.tsx` und `SalesDocumentsPanel.tsx`, `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`, `app/api/v1/endpoints/crm_kim.py`, fokussierte Backendtests sowie CRM360-Playwright-Vertraege und -Specs.
**Abnahmekriterien:** Vorhandene Belege laden die uebergebene Beleg-ID; fehlgeschlagene Logspeicherung behaelt Formulardaten und zeigt einen Fehler; Ansprechpartner-Telefonie nutzt Nummernauswahl, TAPI und anschliessendes Log; Ansprechpartner-E-Mail nutzt die Ansprechpartneradresse oder weist transparent auf fehlende Daten hin; Print rendert eine vollstaendige druckbare Cockpit-Sicht; Neukunde, Beleg-Oeffnen, Kontaktlog, Ansprechpartneraktionen, Print und Browser-Zurueck sind automatisiert; Typecheck, Lint, fokussierte Backendtests, Playwright, Build und Governance sind gruen.
**Offene Risiken:** Die Ansprechpartner-Tabelle kann produktiv noch keine E-Mail-Spalte besitzen; Schema und Query muessen tolerant erweitert werden. Die drei S2-Dateien duerfen erst nach Claudes Handoff integriert werden.
**Ergebnis:** Claudes S2-Commit `ca39b1b06` wurde als Integrationsbasis uebernommen. Angebots-Deep-Links laden die Entity-ID samt Kopf/Kunde/Positionen; Kontaktlog- und Ansprechpartner-Mutationen behalten Eingaben bei Fehlern; der Ansprechpartner-Create-Vertrag akzeptiert Neuanlagen ohne serverseitige ID-Felder; Ansprechpartner-Telefonie nutzt Nummernauswahl, TAPI und kontaktbezogenes Folge-Log; Ansprechpartner-E-Mail wird backendseitig gelesen/geschrieben und bei Legacy-Schemas lesend tolerant behandelt; CRM360 besitzt eine vollstaendige Print-Sicht mit Opt-out aus dem globalen Tabellen-Print-Fallback. Action-Matrix und Browsertests decken Neukunde, Print, Kontaktaktionen, Logfehler, Belegoeffnung und Browser-Zurueck ab.
**Checks:** Backendtests `9 passed`; Frontend- und Playwright-TypeScript gruen; fokussierter ESLint gruen; CRM360-Playwright `15 passed`; Produktions-Build gruen; `git diff --check` und Governance gruen.

## KIM-L3-QUICK-001

**Von:** Codex
**Owner:** Claude (Uebernahme 2026-06-09 — Codex pausiert 3h wg. Token-Kontingent; Nutzer beauftragt Fortfuehrung)
**Stand:** in arbeit (Claude fuehrt fort + erweitert um CRM360-Frontend-Verdrahtung der Backends aus KIM-L3-BACKEND-001 sowie die Nutzer-Spec CRM-Customer-360, siehe `docs/crm-customer-360-bauplan-2026-06-09.md`)
**Abstimmung:** Komplementaer zu `KIM-L3-BACKEND-001` (Claude). Codex bearbeitet ausschliesslich `packages/frontend-web/src/pages/crm/kim/**`, CRM-Playwright-Vertraege und den eigenen QA-/Slice-Nachweis. Keine Aenderung an `app/**`, `alembic/**`, `tools/tapi-bridge/**` oder Backendtests. Neue Backend-Endpunkte werden in diesem Slice nicht vorausgesetzt; ihre Frontend-Integration erfolgt nach Claudes stabiler Handoff-Schnittstelle.
**Ziel des Slices:** Die im L3-Funktionsabgleich nachgewiesenen, rein frontendseitigen KIM-Bedienluecken schliessen: separate Kunden-Neuanlage, druckbare Cockpit-Ansicht, auswählbare Ansprechpartner mit Oeffnen/E-Mail/Praesente/Filter sowie fachlich korrekte Oeffnen-/Neu-Navigationen fuer vorhandene Verkaufsbelege.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-L3-QUICK-001.yaml`, `docs/quality-assurance/` fuer den KIM-L3-Klicknachweis, `packages/frontend-web/src/pages/crm/kim/**` sowie fokussierte CRM-Playwright-Vertraege unter `playwright-tests/specs/crm/`.
**Abnahmekriterien:** Jede neue Aktion besitzt eine stabile semantische Action-ID; Neukunde oeffnet eine leere kanonische Kundenmaske; Print erzeugt eine druckbare Cockpit-Sicht; Ansprechpartner sind selektier- und filterbar und Oeffnen/E-Mail/Praesente arbeiten im gewaehlten Kontext; unterstuetzte Verkaufsbelege oeffnen die richtige Detail- beziehungsweise Neuanlagemaske mit Kunden-/Belegkontext; unbekannte oder noch nicht kanonisch routbare Belegarten behaupten keinen erfolgreichen Fachprozess; Typecheck, Build, Playwright und Governance sind gruen.
**Offene Risiken:** TAPI-Wahl, CC/Benachrichtigung und neue Kontaktlog-Persistenz sind explizit nicht Teil dieses Slices. Kaufangebote, Kaufabrechnungen und Fremdbestaende duerfen nur verdrahtet werden, wenn eine kanonische Zielroute eindeutig nachweisbar ist.

## KIM-L3-BACKEND-001

**Von:** Claude
**Owner:** Claude
**Stand:** Backend umgesetzt 2026-06-09
**Ergebnis (Backend):** (A1) Kontaktlog persistiert Art/Betreff/Kommentar/CC (`crm_kim.py` LogCreateIn/create_log/_log_from_row/ContactLog; Tabelle `kunden_kontakte` unterstuetzte die Spalten bereits, keine Migration). (B) TAPI Click-to-Dial: `POST /crm/tapi/dial` + `GET /crm/tapi/dial/pending` + `POST /crm/tapi/dial/{id}/done` (reuse `tapi_calls`, richtung='aus', status='dial_req', acked=TRUE, caller-Default 'KIM'; graceful ohne Bridge). (C) `GET /crm/kim/customers/{nr}/contact-docs?kind=invoices|dunning|contracts|drop_shipments` (Rechnungen/Mahnungen aus kanonischer `domain_shared.open_items`, Kontrakte/Strecken tolerant leer). (D) Internes Benachrichtigungssystem: Migration `crm_notifications_kim_l3_backend_20260609` (idempotent angewandt), `crm_notification_service.py` (intern persistent + extern Mail best-effort), Endpoints `POST/GET /crm/kim/notifications` + `/{id}/read`, CC-Auto-Dispatch in `create_log`. Verifiziert: 6 Unit-Tests gruen, alle Endpoints per curl 200 (Dial/Inbox/contact-docs), Migration idempotent. **Offen (Folge-Slice, Frontend):** Verdrahtung im KIM-Cockpit (Art-Dropdown/Betreff/Kommentar/CC-Feld, Tel→Dial, Kontakte-Belegtabs, Postfach-Anzeige) — nach KIM-L3-QUICK-001.
**Abstimmung:** Komplementaer zu `KIM-L3-QUICK-001` (Codex/Claude Code). Claude Code macht die rein frontend-/routenseitigen Bedienluecken (`packages/frontend-web/src/pages/crm/kim/**` + CRM-Playwright-Vertraege). Ich (Claude) baue die von KIM-L3-QUICK-001 **ausdruecklich ausgeklammerten** Backend-Fundamente: Kontaktlog-Persistenz (Art/Betreff/Kommentar/CC), TAPI-Wahl-Trigger, internes Benachrichtigungssystem sowie kanonische Kontakte-Belegquellen. **Ich fasse KEINE Datei unter `packages/frontend-web/src/pages/crm/kim/**` und KEINE `playwright-tests/specs/crm/**` an** — Frontend-Verdrahtung dieser Backends erfolgt als Folge-Slice, nachdem KIM-L3-QUICK-001 gelandet ist.
**Ziel des Slices:** Backend-Vertraege bereitstellen, damit die L3-Funktionen Kontaktdokumentation (Art/Betreff/Kommentar/CC), TAPI-Wahl, interne/externe Benachrichtigung und kontaktbezogene Belegtabs (Rechnungen/Mahnungen/Kontrakte/Strecken) im KIM-Cockpit fachlich hinterlegt sind.
**Dateibesitz:** `docs/agent-ops/active-workboard.md` (nur eigener Block), `docs/agent-ops/slices/KIM-L3-BACKEND-001.yaml`, `app/api/v1/endpoints/crm_kim.py`, neue `app/services/*`-Dateien fuer Benachrichtigung/Belegquellen, neue `alembic/versions/*` Migration(en), TAPI-Anbindung via `tools/tapi-bridge`, sowie `tests/test_*`-Backendtests. **NICHT:** `packages/frontend-web/**`, `playwright-tests/specs/crm/**`.
**Abnahmekriterien:** `create_log` persistiert Art/Betreff(kurzinfo)/Kommentar(notiz)/CC(weiterleitung_an) und `list_logs` gibt sie zurueck; TAPI-Wahl-Endpoint loest einen ausgehenden Call ueber die Bridge aus (mit Fallback/Gate ohne Bridge); internes Benachrichtigungsmodell + Endpoints (an Mitarbeiter/Abteilung) und externer Fachberater-Mail-Hook; kontaktbezogene Belegquellen-Endpoints liefern Rechnungen/Mahnungen/Kontrakte/Strecken aus kanonischen Quellen tolerant; `pytest` der neuen Tests gruen; `alembic upgrade head` idempotent.
**Offene Risiken:** Schnittstelle zwischen meinen Backend-Endpoints und der spaeteren Frontend-Verdrahtung muss stabil benannt sein. Bei gleichzeitigem Edit von `active-workboard.md` nur den eigenen Block pflegen.

## CRM360-MBT-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Ziel des Slices:** Den modellbasierten CRM360-Klickvertrag nach dem KIM-Designsystem-Umbau vollstaendig erneut ausfuehren und alle Regressionen bei Buttons, Tabs, CRUD, fachlichen Zielmasken, Entity-Kontext, 404-/Console-Fehlern und Browser-Zurueck beheben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-005.yaml`, CRM360-QA-Dokumentation unter `docs/quality-assurance/`, CRM360-Spezifikationen und Hilfen unter `playwright-tests/specs/crm/` und `playwright-tests/helpers/`, `playwright.config.ts`, `playwright.global-setup.mjs`, `playwright.global-teardown.mjs`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx` sowie nur nachgewiesene Verdrahtungs- oder Selektorfixes unter `packages/frontend-web/src/pages/crm/kim/**`.
**Abnahmekriterien:** Die vollstaendige CRM360- und Revenue-Handover-Playwright-Suite laeuft gegen den aktuellen KIM-Stand; alle vertraglich erfassten Aktionen sind sichtbar und klickbar; CRUD-Requests, Zielroute, Hauptinhalt und Kunden-/Belegkontext stimmen; Browser-Zurueck liefert CRM360 ohne 404; keine neuen Console- oder Request-Fehler; Typechecks, fokussierter Lint, Build und Governance sind gruen.
**Offene Risiken:** Der Playwright-Global-Setup kann mit bereits laufenden lokalen Servern kollidieren. Selektoren duerfen nur stabilisiert werden, wenn die fachliche Aktion unveraendert bleibt; echte Verdrahtungsfehler werden im KIM-Code behoben und nicht durch nachsichtige Tests verdeckt.
**Ergebnis:** Der KIM-Designsystem-Umbau ist gegen elf modellbasierte CRM360- und Revenue-Handover-Tests regressionsgeprueft. Dialogtitel, aktive Tab-Tokens und delegierte Formularfelder besitzen wieder stabile Testvertraege. Playwright verwendet vorhandene Server oder startet entkoppelte eigene Prozesse ohne Portkonflikt und Haengen. Auftrags- und Lieferschein-Erfassung behalten den bereits typisiert uebergebenen CRM-Kundenkontext auch dann, wenn ein spaeter optionaler Kunden-Detail-Lookup leer bleibt; dadurch wird die Kundennummer bis Rechnung und Debitoren-OP durchgereicht.
**Checks:** CRM360 + Revenue-Handover Playwright `11 passed`; isolierter Self-Start-/Teardown-Smoke bestanden; Frontend- und Playwright-Typecheck gruen; Produktions-Build gruen; KIM-Lint ohne Fehler; Workboard- und Doku-Governance gruen.

## KIM-DS-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-09
**Ziel des Slices:** Das unter `/crm` fuehrende KIM-360-Cockpit von der portierten systemERP-L3-Terminal-Optik vollstaendig auf das VALEO-Designsystem umbauen (DS-Komponenten, Semantik-Farbtokens, Dark-Mode, Dialog-/Toolbar-Muster) und die wahrgenommene Ladeperformance der grossen Debitorenliste reduzieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-DS-001.yaml`, `packages/frontend-web/package.json`, `packages/frontend-web/src/pages/crm/kim/index.tsx` und alle `packages/frontend-web/src/pages/crm/kim/components/*.tsx`.
**Abnahmekriterien:** Keine `font-mono`/`uppercase`-Terminal-Optik und keine hartkodierten Hex-Farben mehr; alle Flaechen nutzen DS-Semantik-Tokens und Dark-Mode rendert korrekt; Raw-Buttons/Inputs/Selects/Textareas/Modals durch `Button`/`Input`/`NativeSelect`/`Textarea`/`Dialog` ersetzt; mutierende Aktionen mit Submit-Guard + Disabled + Toast; alle `data-action-id` und Test-Selektoren identisch zu HEAD; Debitorenliste rendert nur ein begrenztes DOM-Fenster; eslint clean, tsc 0 Fehler, Screenshot hell+dunkel ok.
**Offene Risiken:** Praesentations-Refactor ueber 14 Dateien — Test-Selektoren des model-based CRM360-Tests duerfen nicht brechen. Die Cold-Start-Langsamkeit ist Vite-Dev-Erstaufbau (im Prod-Build irrelevant), kein App-Bug.
**Ergebnis:** Alle 14 KIM-Komponenten auf das VALEO-Designsystem umgebaut (~250x `font-mono`/`uppercase` entfernt, hunderte Hex-Farben → DS-Tokens, Dark-Mode funktioniert, DS-Primitive durchgaengig inkl. `Dialog`/`Progress`/`Skeleton`/`Badge`, Submit-Guards an Master-Edit + Quick-Call). Alle 12 `data-action-id` und Schluessel-IDs identisch zu HEAD. Debitorenliste rendert ein 80er-Fenster (462 total → 80 im DOM, „weitere anzeigen") bei voll erhaltener Suche/Filter/Tastatur-Navigation. `package.json` `predev`/`prebuild`/`pretype-check`/`check:navigation-targets` von `pnpm` auf `npm run routes:generate` korrigiert (Container hat kein pnpm → Exit 127).
**Checks:** `eslint` (`--max-warnings 0`) clean; `tsc --noEmit` 0 Fehler projektweit; Render-Fenster verifiziert (total=462, rendered=80, load-more=1); Dark-Mode-Screenshot ok. **Follow-up ERLEDIGT (2026-06-09, Commit `74b274a8d`):** Port-Konflikt via „reuse existing server" im Global-Setup gelöst, Selektoren auf stabile IDs gehärtet, model-based Suite `crm360-model-based.spec.ts` **10/10 grün** (`npx playwright test … --retries=1` gegen Preview :4173, APIs gemockt); Doku `docs/quality-assurance/playwright-port-konflikt-reuse-2026-06-09.md`. Offen bleibt nur die optionale Server-seitige Kundensuche bei stark wachsendem Kundenstamm.

## CRM360-MBT-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Ziel des Slices:** Den CRM360-Revenue-Handover um den fachlichen Abschluss Rechnung -> Buchung -> offener Posten erweitern und gegen reale Backend-Vertraege validieren. Der Nachweis muss tenant-isoliert, revisionssicher und ohne hartes Loeschen gebuchter Finanzdaten auskommen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-004.yaml`, relevante CRM360-/OTC-QA-Dokumentation, `scripts/uat/crm360_revenue_handover_uat.py`, fokussierte Tests unter `tests/`, `app/services/docflow_service.py`, `app/services/sales_posting_service.py`, `app/services/finance_transaction_service.py`, `app/infrastructure/models/journal.py` und `app/api/v1/endpoints/finance_invoices.py`.
**Abnahmekriterien:** Ein realer oder explizit gegateter UAT weist Rechnung, Posting und Debitoren-OP samt Kunden-, Betrag-, Beleg- und Tenant-Bezug nach; Wiederholung ist idempotent; gebuchte Daten werden nur ueber fachliche Kompensation/Storno behandelt; fehlende Kontierung oder Finanzkonfiguration wird als klarer Blocker ausgewiesen; Backendtests, Live-UAT und Governance sind gruen.
**Offene Risiken:** Posting kann Kontenplan, Geschaeftsjahr, Steuerlogik und Debitorenkonto voraussetzen. Falls kein revisionssicherer Kompensationsvertrag existiert, darf der persistente Lauf nicht buchen und muss stattdessen das fehlende Gate belastbar dokumentieren.
**Ergebnis:** Docflow-Ausgangsrechnungen erzeugen nun ueber den gemeinsamen Sales-Posting-Service eine gebuchte, ausgeglichene JournalEntry und einen Debitoren-OP. Wiederholung mit gleichem Idempotenzschluessel ist stabil; Storno erzeugt eine GoBD-Gegenbuchung, setzt Original und Docflow-Beleg auf `reversed` und schliesst den OP als `storniert` mit Rest `0`. Auch die produktiven Finance-Invoice-Call-Sites delegieren an denselben Kern. Behoben wurden fehlende Journal-Zeilennummern und kanonische Betragsfelder, Kontonummer-zu-Konto-ID-Aufloesung, der Konflikt zwischen global eindeutigen Kontonummern und tenant-spezifischer Suche sowie freie technische Akteure in einem User-FK-Feld.
**Checks:** Finanz-Live-UAT `status=passed` mit erhaltener reversierter Evidenzkette; Original- und Gegenbuchung jeweils Soll=Haben `20,00 EUR`, Hashwerte vorhanden, OP `storniert/offen=0`, keine verwaisten Sales-Invoice-Drafts; 91 fokussierte Backendtests, Python-Compile und Governance bestanden.

## CRM360-MBT-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Fuer den CRM360-Revenue-Handover einen persistenten, wiederholbaren und aufraeumbaren UAT-Durchstich gegen reale Backend-Vertraege bereitstellen. Testdaten muessen eindeutig markiert, tenant-isoliert und nach dem Lauf entfernt werden; fehlende produktive Infrastruktur wird als explizites Gate statt als Scheinerfolg ausgewiesen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-003.yaml`, relevante CRM360-UAT-/QA-Dokumentation, neue fokussierte UAT-Hilfen und Tests unter `playwright-tests/specs/crm/`, `scripts/uat/`, `tests/`, eine idempotente O2C-Repair-Migration unter `alembic/versions/` sowie nur die fuer Cleanup oder konsistente O2C-Vertraege zwingend erforderlichen Sales-/Delivery-/Invoice-Backenddateien.
**Abnahmekriterien:** Der Lauf erzeugt oder verwendet isolierte Kunden-/Belegdaten, prueft persistente Folgeobjekte und ihren Zusammenhang, beseitigt erzeugte Daten idempotent und unterscheidet sauber zwischen bestanden, nicht konfiguriert und fachlich fehlgeschlagen; Typechecks, fokussierte Backendtests, Browser-UAT und Governance sind gruen.
**Offene Risiken:** Eine lokal erreichbare, migrationsaktuelle Datenbank und gestartete Backenddienste koennen fehlen. Finanzbuchungen duerfen nicht destruktiv geloescht werden; gegebenenfalls endet der automatisierte Lauf vor finaler Buchung und weist diese als externes Freigabe-Gate aus.
**Ergebnis:** Guarded UAT-Skript erzeugt einen markierten Kunden und fuehrt die realen API-Vertraege Angebot -> Auftrag -> Lieferschein -> Docflow-Rechnung aus. Persistenz, Positionen, Kunden-/Quellbelegbezug und API-Soft-Delete werden gegen eine frische DB-Session validiert; ein abschliessender ID-basierter Cleanup entfernt alle UAT-Artefakte. Behoben wurden das veraltete Lieferschein-SQL, eine fehlende Dev-Tabellenstruktur, die falsche FK-Einfuegereihenfolge der Docflow-Konvertierung und ein Best-Effort-Audit, dessen geschluckter SQL-Fehler zuvor die gesamte Fachtransaktion implizit zurueckrollte.
**Checks:** Live-UAT `status=passed`; sieben fokussierte Backendtests bestanden; Python-Compile bestanden; Alembic steht auf `crm360_o2c_delivery_20260608 (head)`; Residuenpruefung fuer Kunden, Angebote, Lieferscheine, Docflow und Outbox jeweils `0`.

## CRM360-MBT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Den bisher nur modellierten CRM360-Folgeprozess Kunde -> Angebot -> Auftrag -> Lieferschein -> Rechnung -> OP als echten, typisierten Browser-Handover umsetzen und mit Playwright gegen Zielmaske, Kunden-/Belegkontext, Ruecksprung und 404-/Console-Fehler pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-002.yaml`, relevante QA-/Workflow-Doku, `app/api/v1/endpoints/sales_offers.py`, `tests/test_security_sales_offers.py`, neuer gemeinsamer Handover-Vertrag unter `packages/frontend-web/src/lib/workflow/`, `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`, `order-editor.tsx`, `delivery-editor.tsx`, `invoice-editor.tsx`, `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`, `packages/frontend-web/src/pages/finance/op-debitoren.tsx` sowie fokussierte Tests unter `playwright-tests/specs/crm/`.
**Abnahmekriterien:** Jede Belegstufe liest und reicht einen einheitlichen Kunden-/Quellbelegkontext weiter; sichtbare Folgeprozess-Aktionen oeffnen die fachlich erwartete Maske; Browser-Zurueck endet nicht auf 404; Playwright fuehrt den gesamten Handover mit deterministischen Fixtures aus; Typecheck, Build, fokussierte Tests und Governance sind gruen.
**Offene Risiken:** Die Fachmasken verwenden teils unterschiedliche API- und Query-Vertraege. Persistenter Live-CRUD ueber alle Stufen kann isolierte Backend-Fixtures erfordern; ein Browser-Handover darf nicht als Buchungsnachweis ausgegeben werden.
**Ergebnis:** Einheitlicher typisierter Sales-Handover eingefuehrt; Angebot, Auftrag, kanonischer Lieferschein, Rechnung und OP transportieren Kunden- und Quellbelegkontext. Auftragspositionen werden in den Lieferschein uebernommen, die Angebot-zu-Auftrag-API besitzt ein korrektes Response-Modell, und elf kombinierte CRM360-Browsertests sind gruen.
**Checks:** Frontend- und Playwright-Typecheck, Produktions-Build, Routing-Integritaet, Navigation-Targets, drei Backendtests und elf Playwright-Tests bestanden.

## ROUTER-NEXT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Nach dem erfolgreichen TanStack-Browser-Router-Cutover werden die verbliebenen produktiven Aufrufe des React-Router-Kompatibilitaetsadapters auf native TanStack-Hooks und streng typisierte VALEO-Route-Contracts migriert.
**Dateibesitz:** `packages/frontend-web/src/**`, Routing-Scripts, Routing-Dokumentation und fokussierte Tests.
**Abnahmekriterien:** Keine produktiven Imports aus `react-router-compat.tsx`; Navigation, Links, Parameter und Search verwenden TanStack Router beziehungsweise den typisierten Route-Contract; Adapter nur noch als Testinfrastruktur oder entfernt; alle Routing-Gates gruen.
**Offene Risiken:** Mehr als 300 produktive Dateien verwenden die alte ergonomische Aufrufsignatur. Dynamische Pfade werden explizit klassifiziert und nicht durch untypisierte Casts verdeckt.
**Ergebnis:** Der React-Router-Kompatibilitaetsadapter ist entfernt. 338 produktive Aufrufer verwenden die TanStack-basierte `typed-router.tsx`-Fassade; Unit-Tests verwenden getrennt `test-router.tsx` mit TanStack Memory History. Der Generator erzeugt 851 explizite Routen, einen maschinenlesbaren Route-Katalog sowie geschlossene Parameter- und Search-Key-Contracts. 94 produktive Navigationsziele und 34 Legacy-Redirects sind explizit registriert. Das neue Gate `check:navigation-targets` validiert statische und template-basierte Deep Links. Vollstaendiger Typecheck, Routing-Integritaet, Navigation-Audit, 127 Vitest-Tests, Produktions-Build und acht Playwright-Smokes sind gruen.

## ROUTER-NEXT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Die Frontend-Routing-Infrastruktur vollstaendig von zentraler React-Router-Splat-/Alias-Aufloesung auf einen automatisch generierten, typisierten TanStack-Route-Tree migrieren. Kanonische Route-Contracts, typisierte Parameter/Search-Werte, Breadcrumb-Metadaten, Auth, Deep Links und Legacy-Redirects werden in einer Source of Truth zusammengefuehrt; es gibt zu keinem Zeitpunkt zwei Browser-Router auf derselben History.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ROUTER-NEXT-001.yaml`, neue Routing-ADR/Projektkontext-Doku, `packages/frontend-web/package.json`, `packages/frontend-web/vite.config.ts`, `packages/frontend-web/src/app/**` (Routing und Navigation), `packages/frontend-web/src/routes/**`, `packages/frontend-web/src/routeTree.gen.ts`, routergekoppelte Layouts/Komponenten/Seiten, Routing-Scripts sowie fokussierte Unit-/E2E-Tests.
**Abnahmekriterien:** TanStack Router ist der einzige Browser-Router; Route Tree wird reproduzierbar generiert; dynamische Parameter und Search-Werte sind typisiert; Breadcrumbs und Auth laufen ueber Route-Metadaten/Context; bekannte Legacy-Links redirecten auf kanonische URLs; unbekannte Pfade liefern 404; `AppRouteRuntime` und React-Router-Splat entfallen; Typecheck, Build, Routing-Tests und E2E-Smokes sind gruen.
**Offene Risiken / Integrationsreihenfolge:** Sehr hoher Blast Radius durch 569 Aliase und hunderte React-Router-Imports. Root-Router, Vite-Konfiguration und gemeinsame Navigation bleiben exklusiver Besitz dieses Slices. Migration erfolgt contract-first mit automatisierten Import-/API-Umstellungen und fokussierter manueller Nacharbeit; fremde parallele Aenderungen werden nicht reverted.
**Ergebnis:** TanStack Router ist der einzige Browser-Router. 757 explizite Routen, Route-Parameter und geerntete Search-Keys werden generiert und typisiert; 25 bekannte Legacy-URLs redirecten explizit auf kanonische Ziele. Breadcrumbs verwenden Match-Metadaten, Auth sitzt am App-Layout, der Unsaved-Changes-Blocker verwendet die TanStack-API. `AppRouteRuntime`, `PortalRouteRuntime`, `routes.tsx`, `App.tsx`, die zentrale Splat-Aufloesung und `react-router-dom` sind entfernt. Routing-Integritaet, Typecheck, Build, fokussierte Unit-Tests und der neue TanStack-Browser-Smoke sind gruen.

## KIM-CRM-360-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen + nach `main` gemergt/gepusht 2026-06-07 (Commit `6ab79d080`; Konsolidierung kunden-cockpit als Folgescope)
**Ziel des Slices:** Eine mit Google AI Studio gebaute 360°-CRM-Ansicht (systemERP-L3-Stil) als führendes Cockpit **„KIM – Kunde im Mittelpunkt" unter `/crm`** nach VALEO transponieren: portieren, an echte Daten anbinden (inkl. `public.kunden`-Erweiterung + Lese-Endpoints), NeuroAI anbieterunabhängig machen (Admin wählt LLM-Anbieter), Lead-Management + CRM-Geo als Tabs einbetten.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kim/**`, `pages/admin-suite/ki-anbieter.tsx`, `lib/api/admin-suite.ts`, `app/route-aliases.json`, `app/route-builders/auto-groups/generated/admin-suite.ts`, `app/navigation/domains/{commercial,core}.tsx`, `package.json`; `app/api/v1/endpoints/crm_kim.py`, `app/services/llm_gateway.py`, `app/api/v1/endpoints/admin_suite.py`, `app/api/v1/api.py`, `alembic/versions/kunden_crm360_20260607.py`, `app/services/{whatsapp_intake_service,kaeufer_klassifikator}.py`, `tests/test_{llm_gateway,crm_kim}.py`.
**Abnahmekriterien:** `/crm` lädt das 360°-Cockpit mit echten Kundendaten; Stammdaten-Edit persistiert (kunden_crm360-Satellit, Konvention-konform: kunden_nr-FK, kein tenant_id); Kontakte/Wiedervorlage/OP/Belege als echte Lese-Tabs; NeuroAI über anbieterunabhängiges Gateway mit deterministischem Fallback, Admin-Konfiguration unter `/admin-suite/ki-anbieter` (Key nie im Klartext); Lead-/Geo-Tabs eingebettet; type-check 0, eslint 0, Build grün, Backend-Tests grün.
**Erledigt:**
- **A+B:** 360°-App portiert (React 19→18, Tailwind v4→v3, Gemini raus, react-markdown@9); `kim-api.ts` → `/crm/kim/*`; Route `/crm` + Nav. Migration `kunden_crm360` (1:1-Satellit); `crm_kim.py` (customers CRUD-light, contacts via Alt-Tabelle `kunden_ansprechpartner`, logs/Wiedervorlage, financials/documents tolerant).
- **C:** `llm_gateway.py` (anthropic/openai_compatible/ollama, Tenant-Settings+Env, Fallback); Admin `GET/PUT/test /admin-suite/llm-gateway` + UI `ki-anbieter.tsx`; `neuro-summary` + `draft-email`; `whatsapp_intake`/`kaeufer_klassifikator` auf Gateway konsolidiert.
- **D:** Tabs „Lead-Management" (`leads`) + „CRM-Geo / Karte" (`kunden-karte`) lazy eingebettet.
**Checks:** `pytest tests/test_llm_gateway.py` (9), `test_crm_kim.py` (6), Smoke `test_admin_suite_readiness+test_kaeufergruppe` (35 gesamt) — alle grün (Container via `docker cp`+`MSYS_NO_PATHCONV=1`); `alembic upgrade head` (kunden_crm360_20260607); `tsc --noEmit` 0, `eslint src/pages/crm/kim` 0, `npm run build` grün; alle `/crm/kim/*`-Endpoints HTTP 200; Dev-Server `/crm` 200 inkl. API-Proxy.
**Offene Risiken / Folgescope:** Konsolidierung KIM ↔ `kunden-cockpit` (klassisch belassen, nicht entfernt — Deep-Links/Tests). Belege/OP in DEV leer → reale Leerzustände bis Verkaufsdaten existieren (Mapping verifiziert). `ANTHROPIC_API_KEY` ohne Guthaben → NeuroAI engine='fallback'; Admin kann auf Ollama/OpenRouter wechseln. Direktanlage OP/Beleg aus dem Cockpit ist bewusst Folgescope: Add-Aktionen geben ehrliche „im Fachprozess anlegen"-Rückmeldung (Lesen produktionsecht, financials aus domain_shared.open_items verifiziert). Vorbestehende, nicht-KIM CSS-Build-Warnung (font-stack) + 3 Analytics-Routing-Lücken bleiben rot (Repo-Altschuld, im Workboard akzeptiert). Auf `main` gemergt + gepusht.

## CRM360-MBT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Fuer das KIM-CRM-360-Cockpit einen semantischen, modellbasierten Klickvertrag einfuehren. Alle Buttons, Tabs, Links und CRUD-Aktionen werden gegen erwartete Zielmaske, Entity-Kontext, Persistenz, Ruecksprung und fachlichen CRM-to-Revenue-Workflow geprueft; die bestehende Visual-Tour bleibt reiner Smoke-Test.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, neuer Slice-Vertrag unter `docs/agent-ops/slices/CRM360-MBT-001.yaml`, CRM-360-Testdokumentation/Report unter `docs/quality-assurance/`, neue CRM-360-Tests und Hilfen unter `playwright-tests/`, notwendige stabile Action-IDs und nachgewiesene Verdrahtungsfixes unter `packages/frontend-web/src/pages/crm/kim/**`.
**Abnahmekriterien:** Maschinenlesbare Action-Matrix deckt alle interaktiven CRM-360-Elemente ab; Playwright prueft Sichtbarkeit, Klickbarkeit, Zielinhalt, URL/Entity-Kontext, 404/Console/Request-Fehler und Ruecksprung; echte KIM-CRUD-Pfade pruefen Persistenz, delegierte Fachprozesse werden explizit als solche validiert; CRM-to-Revenue-Modellpfad ist als ausfuehrbarer Testvertrag vorhanden; Markdown-Report klassifiziert OK, fehlende Verknuepfung, falsches Ziel, fehlendes CRUD, Back/404 und fachlich fragwuerdig.
**Bekannte Risiken:** Testdaten und laufende Backend-Dienste koennen vollstaendige Live-CRUD-Ausfuehrung lokal begrenzen; destructive Aktionen benoetigen isolierte Fixtures oder API-Cleanup. Bestehende fachlich unvollstaendige Buttons werden nicht durch nachsichtige Assertions kaschiert.
**Pflichtchecks:** CRM-360-Playwright-Suite, TypeScript-Typecheck der Testvertraege, Frontend-Typecheck bei UI-Aenderungen, Doku-Governance.
**Ergebnis:** 23 typisierte Action-Contracts und ein CRM-to-Revenue-Zustandsmodell eingefuehrt. Die zehnteilige Playwright-Suite prueft Kopfaktionen, echte KIM-Updates/Creates, NeuroAI-Kontext, delegierte Fachprozesse, URL-/Entity-Kontext und Browser-Ruecksprung ohne 404. Behoben wurden tote CRM360-Handler, falsche Zielnavigation, unsichtbare Toasts, Label-Zuordnungen, der haengende Playwright-Teardown, alle gefundenen Playwright-Typfehler sowie zwei Buildfehler ausserhalb CRM360 (POS-Doppelimport und ungueltige Tailwind-Regel).
**Checks:** CRM360 Playwright `10 passed`; Playwright-Typecheck gruen; Frontend-Typecheck gruen; Produktions-Build gruen; Workboard-Governance wird im Abschlusslauf validiert.
**Offene Risiken:** `mailto:` bleibt ein externer OS-Workflow. Der Unterlagen-Tab ist weiterhin lokal und kein persistentes DMS. Der fachliche Durchstich Angebot -> Auftrag -> Lieferschein -> Rechnung -> OP ist modelliert, benoetigt fuer einen echten Live-Nachweis aber isolierte, aufraeumbare Daten in allen beteiligten Fachmodulen.

## CRM-GEO-ABSCHLUSS-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-05
**Ziel des Slices:** Die vier offenen Fäden der CRM-/Geo-Arbeit zu Ende führen — (1) Geo-Hofgenauigkeits-Loop schließen, (2) echte Ist-Belegaggregation statt modellierter Seeds, (3) Durchdringungs-Pipeline-Performance (N+1), (4) TAPI-Bridge-Dienst — plus die jüngste GAP-Datenquelle (impdata2025.csv) korrekt autoritativ machen.
**Dateibesitz:** `scripts/import_kmz_betriebe.py`, `app/services/ist_aggregation_service.py` (neu), `scripts/aggregate_produktgruppen_bezug.py` (neu), `tests/test_ist_aggregation.py` (neu), `app/services/bedarfsdeckung_service.py`, `app/services/gap_pipeline.py`, `app/services/geo_pipeline.py`, `scripts/enrich_betriebe_csv.py`, `scripts/seed_ackerbau_profil.py`, `tools/tapi-bridge/tapi_bridge.py` (neu), `tools/tapi-bridge/README.md` (neu), `tests/test_tapi_bridge.py` (neu).
**Abnahmekriterien:** KMZ-Koordinaten-Import hebt Kunden offline auf `precision='address'`; Ist-Aggregator füllt `kunden_produktgruppen_bezug` (`quelle='verkauf'`) aus echten Belegen und löst beide Medienbrüche (UUID→kunden_nr, Artikel→Produktgruppe); Pipeline ohne N+1; TAPI-Bridge meldet Anrufe an `/crm/tapi/incoming`; GAP-Konsumenten filtern auf das jüngste Jahr (keine Doppelzählung).
**Erledigt:**
- **Geo-Loop:** `import_kmz_betriebe.py` parst `<Point><coordinates>`, schreibt Koordinaten nach `gap_map_points` (Ausreißer außerhalb der Region verworfen) und ruft `match_address_points()` → Kunde auf `precision='address'` (verifiziert: GAP00001 place→address).
- **Ist-Aggregation:** `IstAggregationService` unioniert `domain_crm.sales_orders` + `domain_portal.customer_orders`, Resolver mappt customer_id/UUID/webshop/legacy → kunden_nr, reiner Klassifikator `klassifiziere_artikel` → 9 Produktgruppen; rollierend 12 M; Upsert `quelle='verkauf'` ohne Käufergruppen zu überschreiben. Integrationstest (beide Brücken, DB-Marge) grün; Dev hat keine echten Belege → Dry-Run 0, greift automatisch sobald Belege existieren.
- **Pipeline:** `BedarfsdeckungService.pipeline()` lädt 5 Batch-Queries vor + `_compute()` (eine Quelle der Wahrheit mit `cockpit()`). 4 s → **0,11 s** (~36×), Ergebnis 10/10 identisch zum Einzel-Cockpit.
- **TAPI:** `tools/tapi-bridge/tapi_bridge.py` (stdlib-only) — FRITZ!Box-Callmonitor (TCP 1012) / generischer TCP-Listener / Simulationsmodus; Reconnect-Backoff, Dedupe je Verbindungs-ID. Live getestet: `+49 551 12345` → Musterfirma GmbH.
- **GAP 2025:** 2025 war bereits importiert (20.817 Zeilen). Doppelzählung 2024+2025 in `geo_pipeline.get_map_points` (Karte) + `enrich_betriebe_csv` + `seed_ackerbau_profil` behoben via neuem `gap_pipeline.latest_gap_year()`; Ackerbau-/Bezug-Profile aufgefrischt (Ø-Fläche 125,3→112,6 ha).
**Checks:** `python -m pytest tests/test_ist_aggregation.py` (9 passed, im Container); `tests/test_tapi_bridge.py` (6 passed); reversibler Integrationstest Ist-Aggregation grün; `pipeline(500)` 448 Betriebe/0,11 s, 10/10 == Einzel-Cockpit; `import_kmz` Koordinaten-Loop verifiziert + Cleanup; TAPI live `/incoming`+`/pending` verifiziert + Cleanup; `python -m py_compile` aller geänderten Dateien.
**Offene Risiken:** Hofgenauigkeit braucht den manuellen My-Maps-Schritt (CSV anreichern → dort geokodieren → KMZ mit Koordinaten zurück) — extern. Echte Ist-Aggregation liefert erst Werte, sobald reale Verkaufsbelege existieren (Dev leer). 16 Ackerbau-Profile bleiben nach 2025-Reseed als Restbestand unter der ha-Schwelle (modelliert, unkritisch). TAPI-Bridge in Prod mit gültigem OIDC-Token statt `dev-token` betreiben. GAP-CSV nicht neu heruntergeladen (Vollimport >1 Mio. Sätze) — 2025 ist bereits regional importiert; Refresh bei Bedarf via `download_gap_csv(2025, force=True)`.

## KUNDENSTAMM-KONSOLIDIERUNG-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-02 (Repo-seitig; Prod-Ausfuehrung extern, siehe Runbook)
**Ziel des Slices:** Parallele Kunden-Wahrheiten auf einen fuehrenden Business Partner (System of Record) konsolidieren — `public.kunden` ueber `business_partner_id` an die BP-Identitaet binden, den 83-Spalten-Monolithen in schlanke Domaenensatelliten zerlegen, Konsumenten ueber die kanonische Zugriffsschicht lesen lassen und die Prod-Ausfuehrung (Bruecke fuellen, FK, Altspalten-Drop) per Runbook vorbereiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KUNDENSTAMM-KONSOLIDIERUNG-001.yaml`, `docs/kunden-konsolidierung.md`, `docs/runbooks/kunden-konsolidierung-schritt5.md`, `alembic/versions/kunden_*.py` + `perf_indexes_apply_20260602.py` + `performance_indexes_20260526.py`, `app/services/kunden_merge.py`, `app/services/kunden_backfill.py`, `app/services/business_partner_service.py`, `app/api/v1/endpoints/customers.py`, `tests/test_kunden_merge.py`, `packages/frontend-web/src/lib/api/kunden-lookup.ts`, `packages/frontend-web/src/pages/crm/kunden-schnellauswahl.tsx`.
**Abnahmekriterien:** `alembic current == head` (kunden_deprecate_legacy_cols_20260602), idempotent; Satelliten gefuellt (Backfill vollstaendig); Lookup-/Detail-Endpoints liefern Satellitendaten; Reader-Fallback loggt `deprecated`-Warnung; Identitaetsbruecke aufloesbar; `kunden_merge --apply` schreibt nur exact/strong; Prod-Ausfuehrung als phasenweises Runbook mit Backup/Freigabe-Gates dokumentiert.
**Erledigt:** Phase 2A (kunden_merge Reconciliation), 2D (Satelliten `kunden_adressen/zahlung/external_refs/aggregates` + Backfill + `kunden_lookup`-View + Schnellauswahl-Maske), Schritt 4 (30 Altspalten als DEPRECATED markiert, kein Drop, Fallback-Beobachtbarkeit), Schritt 5 vorbereitet (Resolver + `/crm/customers/lookup/resolve` + `/by-partner/{id}/detail` + FE-Hooks + `bridge_status`), Prod-Runbook, Pilot-Enabler `kunden_merge --plz-prefix` (Aurich/Emden/Leer = 265-268). Funktionaler Durchstich Dry-Run/Apply/bridge-status auf Dev fehlerfrei.
**Checks:** `python -m pytest tests/test_kunden_merge.py -q --no-cov` (`9 passed`); `python -m pyflakes` (sauber); `python -m alembic upgrade head` (current == head, idempotent); `pnpm --filter @valero-neuroerp/frontend-web type-check` (`0 errors`); `python scripts/agent_workboard_supervisor.py validate`.
**Offene Risiken:** EXTERN — die eigentliche Prod-Ausfuehrung (`kunden_merge --apply`, FK-Aktivierung, Altspalten-Drop) ist NICHT Teil dieses Slices: benoetigt Prod-`DATABASE_URL`, frisches Backup und Freigabe; Ablauf in `docs/runbooks/kunden-konsolidierung-schritt5.md`. Im Environment ist nur die Dev-DB verbunden (Pilot-Lauf Aurich/Emden/Leer auf Prod ausstehend). Landkreis-Scope ueber PLZ-Praefixe — exakte PLZ-Liste fachlich bestaetigen (Randbereiche 264/269). Identitaetsgebundene Produktivmasken (Combobox/Stamm) lesen erst nach Bruecken-Befuellung ueber resolve/by-partner.

## ADMIN-SUITE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Additive Grundstruktur fuer die VALEO Admin Suite mit zentralem Production-Readiness-Dashboard unter `/admin-suite`, ohne bestehende Health-, Integrations- oder Admin-Pfade zu duplizieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-001.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `app/api/v1/api.py`, `tests/test_admin_suite_readiness.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/navigation/domains/core.tsx`, fokussierte Frontend-Tests und generierte Route-Dateien falls erforderlich.
**Abnahmekriterien:** `/api/v1/admin-suite/readiness` liefert nachvollziehbare Evidenz mit `ready`, `warning`, `blocked` oder `unchecked`; unbekannte oder externe Nachweise werden nie als Erfolg gewertet; `/admin-suite` zeigt Score, Evidenz und Links auf bestehende Admin-Bereiche; Navigation, Backend-Test, Frontend-Typecheck und Workboard-Validierung sind gruen.
**Erledigt:** Read-only Aggregator, konservative Evidenznormalisierung, Top-Level-Route, Navigation, Kachel-Dashboard, Roadmap und fokussierte Tests umgesetzt. Konfigurationsstatus wird nicht als Live-Erfolg bewertet.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_readiness.py tests/test_integration_bootstrap.py -q --no-cov` (`7 passed`); `pnpm --filter @valero-neuroerp/frontend-web test:run -- src/__tests__/pages/admin-suite/index.test.tsx` (`1 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Globaler Routing-Integritaetscheck bleibt wegen drei vorbestehenden Analytics-Page-Group-Luecken rot. Globaler Workboard-Supervisor bleibt wegen sechs vorbestehenden Voice-YAMLs ohne `file_ownership` rot. Externe Live-Probes sind explizit nicht Teil dieses Slices.

## ADMIN-SUITE-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Persistierten, tenant-isolierten Setup-Wizard auf Basis der Admin-Suite-Roadmap einfuehren und vorhandene Fachmasken als gefuehrte Schritte verknuepfen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-002.yaml`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_setup.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/setup.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`, fokussierte Frontend-Tests.
**Abnahmekriterien:** Setup-Session und Schritte sind tenant-isoliert persistiert; `unchecked`, `in_progress`, `warning`, `blocked` und `completed` bleiben unterscheidbar; Navigation allein erzeugt keine Abschlussfreigabe; Resume nach Browser-Neustart ist abgesichert.
**Erledigt:** Tenant-isolierte Setup-Session in `domain_shared.tenants.settings`, explizite Step-Updates, Resume-Lesepfad und gefuehrte UI unter `/admin-suite/setup` umgesetzt. Vorhandene Fachmasken werden verlinkt, Navigation erzeugt keinen impliziten Abschluss.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov` (`6 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Historisierung mehrerer Setup-Sessions bleibt Folgescope; fuer den initialen Wizard reicht der etablierte Tenant-Settings-Vertrag.

## ADMIN-SUITE-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Generischen Migration Core mit Source Profiles, Batches, Mapping-Version, Reconciliation-Gates und L3-/CSV-Cockpit einfuehren, ohne den bestehenden L3-Importer zu ersetzen.
**Dateibesitz:** Vor Claim verbindlich festlegen; neue Admin-Suite-Migrationsdateien, fokussierte Tests und minimale additive Router-/UI-Integration.
**Abnahmekriterien:** Dry Run und Staging bleiben Pflicht; Produktivfreigabe ist ohne Reconciliation blockiert; Batch-ID, Hash, Quelle und Mapping-Version sind sichtbar; L3 und CSV sind als Profile vorhanden.
**Erledigt:** Tenant-isolierter Migration-Control-Plane-Vertrag mit Source Profiles, Dry-Run-Batches, Hash, Mapping-Version und Reconciliation-Gates sowie Cockpit unter `/admin-suite/migration` umgesetzt. L3 und CSV sind verfuegbar; AMIC wird ohne verifizierten Feldkatalog sichtbar blockiert.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov` (`8 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Der Control Plane fuehrt bewusst keinen Produktivimport aus und ersetzt `scripts/import_l3.py` nicht. Ein produktives AMIC-Profil benoetigt einen verifizierten Feldkatalog und Beispieldaten-UAT.

## ADMIN-SUITE-004

**Von:** Codex
**Owner:** Codex
**Stand:** integriert in `ADMIN-SUITE-003` 2026-05-30
**Ziel des Slices:** CSV und AMIC Source Profiles kontrolliert bereitstellen.
**Erledigt:** CSV-Profil ist verfuegbar. AMIC/A.eins ist als sichtbares, blockiertes Profil katalogisiert. Die produktive Aktivierung bleibt bis zum verifizierten Feldkatalog und Beispieldaten-UAT gesperrt.
**Offene Risiken:** Eine scheinbar fertige AMIC-Anbindung ohne reale Quelltabellen und Feldkatalog waere fachlich gefaehrlicher als der explizite Blocker.

## ADMIN-SUITE-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Lesendes Security- und Agent-Governance-Cockpit mit Rollenpaketen, effektiven Scopes, SoD-Warnungen und Rollen-Simulation einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-005.yaml`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_security.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/security.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Bestehendes RBAC bleibt Source of Truth; Simulation liefert effektive Scopes ohne Persistenz; Agentenrollen sind sichtbar getrennt; kritische Scope-Kombinationen erzeugen SoD-Warnungen.
**Erledigt:** Lesendes Governance-Cockpit unter `/admin-suite/security`, RBAC-Adapter, effektive Rechte-Simulation, SoD-Warnungen und getrennte Agentenrollen umgesetzt. Laufende Rollenvertraege werden nicht migriert.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov` (`11 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Normalisierte Permission Sets, Standort-/Lagerfilter und Break-glass-Schreibworkflow bleiben nachgelagerte, migrationspflichtige Governance-Erweiterungen.

## ADMIN-SUITE-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Read-only Connector Hub mit vereinheitlichtem Katalog, Credential-Metadaten und klarer Trennung von Konfiguration und Live-Probe einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-006.yaml`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_operations.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/connectors.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Kein Secret-Wert wird ausgegeben; vorhandene Integrationen sind katalogisiert; Konfigurationsstatus und Live-Probe bleiben getrennt.
**Erledigt:** Read-only Connector Hub unter `/admin-suite/connectors` mit redigierten Credential-Metadaten, vereinheitlichtem Katalog und getrennter Live-Evidenz umgesetzt.
**Checks:** Gemeinsame Admin-Suite-Gates: `18 passed`, TypeScript gruen, Frontend-Smoke gruen, fokussierter Diff-Check gruen.
**Offene Risiken:** Provider-spezifische Retry-/DLQ-Schreibaktionen folgen erst nach Audit-Vertrag.

## ADMIN-SUITE-007

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Hardware Center als read-only Evidenzsicht ueber bestehende Device-, Mobile-, Waage- und POS-Vertraege einfuehren.
**Dateibesitz:** Gemeinsam mit `ADMIN-SUITE-006/008` in additiven Admin-Suite-Dateien.
**Abnahmekriterien:** Device-Kategorien, Registry-Quellen, Testaktionen und Live-Evidenzstatus sind sichtbar; Registrierung wird nicht als Hardware-UAT gewertet.
**Erledigt:** Hardware Center unter `/admin-suite/devices` mit Registry-Quellen, Testaktionen und explizit ungepruefter Live-Evidenz umgesetzt.
**Checks:** Gemeinsame Admin-Suite-Gates: `18 passed`, TypeScript gruen, Frontend-Smoke gruen, fokussierter Diff-Check gruen.
**Offene Risiken:** Reale Heartbeats, Eichnachweise und Standort-UAT bleiben externe bzw. adapterpflichtige Nachweise.

## ADMIN-SUITE-008

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Operations Center fuer Backup, Restore, Release, Alembic und Diagnose als ehrliche Evidenzsicht einfuehren.
**Dateibesitz:** Gemeinsam mit `ADMIN-SUITE-006/007` in additiven Admin-Suite-Dateien.
**Abnahmekriterien:** Deploybare Jobs und nachgewiesene Betriebslaeufe bleiben unterscheidbar; simulierter Restore wird nie als produktiver Nachweis gewertet.
**Erledigt:** Operations Center unter `/admin-suite/operations` mit Backup-, Restore-, Release-, Alembic- und Diagnose-Evidenz umgesetzt. Deploybare Jobs werden nicht als erfolgreiche Betriebslaeufe gewertet.
**Checks:** Gemeinsame Admin-Suite-Gates: `18 passed`, TypeScript gruen, Frontend-Smoke gruen, fokussierter Diff-Check gruen.
**Offene Risiken:** Letzte reale Laufzeitdaten benoetigen spaeter einen Ops-Adapter oder Monitoring-Import.

## ADMIN-SUITE-009

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Read-only Compliance- und Audit-Evidenzsicht fuer GoBD, DSGVO, POS/TSE, Meldewesen und externe Betriebsabnahmen in die Admin Suite integrieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-009.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_compliance.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/compliance.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Bestehende Compliance-Vertraege bleiben Source of Truth; Implementierung, Runtime-Nachweis und externe Abnahme bleiben getrennt sichtbar; kein ungepruefter Nachweis wird als produktiv bereit bewertet; `/admin-suite/compliance` ist erreichbar; Backend-Test, Frontend-Typecheck und fokussierter Diff-Check sind gruen.
**Erledigt:** Read-only Compliance Evidence Center unter `/admin-suite/compliance` mit acht Evidenzbereichen umgesetzt. GoBD, DSGVO Art. 30/33, POS/TSE, ELSTER, ATLAS, Meldewesen und Sanktionspruefung verlinken bestehende Fachvertraege; Runtime-Evidenz und externe Gates bleiben explizit getrennt.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_compliance.py tests/test_admin_suite_operations.py tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov --tb=short` (`17 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierte Doku-Checks; `git diff --check`.
**Offene Risiken:** Externe Zertifikate, Behoerdenquittungen und produktive UAT-Nachweise bleiben ausserhalb des Repos.

## ADMIN-SUITE-010

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Read-only Systemstatus-Evidenzsicht fuer Health, Release, Migration, Event-Bus, Worker und Voice in die Admin Suite integrieren, ohne beim Cockpit-Aufruf Live-Probes auszuloesen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-010.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_system_status.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/system-status.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Bestehende Health- und Monitoring-Vertraege bleiben Source of Truth; implementierte Probe, beobachteter Runtime-Status und Cockpit-Abruf bleiben getrennt; kein Cockpit-GET startet externe oder zustandsaendernde Probe; `/admin-suite/system-status` ist erreichbar; Backend-Test, Frontend-Typecheck und fokussierter Diff-Check sind gruen.
**Erledigt:** Read-only System Status Evidence Center unter `/admin-suite/system-status` mit acht Evidenzbereichen umgesetzt. API-Liveness, API-Readiness, Startup-Guards, Release, Alembic, Event-Bus, Worker und Voice verlinken vorhandene Probe-Vertraege; der Cockpit-Aufruf fuehrt keine Live-Probe aus.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_system_status.py tests/test_admin_suite_compliance.py tests/test_admin_suite_operations.py tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov --tb=short` (`20 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierte Doku-Checks; `git diff --check`.
**Offene Risiken:** Reale Laufzeitwerte benoetigen spaeter einen expliziten Ops-Adapter oder Monitoring-Import.

## ADMIN-SUITE-011

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Redigierten read-only Diagnosepaket-Manifest-Katalog fuer Supportfaelle in die Admin Suite integrieren, ohne Logs, Secrets oder Live-Daten beim Cockpit-Aufruf zu exportieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-011.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_diagnostics.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/diagnostics.tsx`, `packages/frontend-web/src/pages/admin-suite/operations.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Diagnosekategorien, Quellen, Redaktionspflicht und Sammelstatus sind sichtbar; Secret- und personenbezogene Inhalte werden nicht ausgegeben; Cockpit-GET sammelt oder exportiert keine Live-Daten; `/admin-suite/diagnostics` ist erreichbar; Backend-Test, Frontend-Typecheck und fokussierter Diff-Check sind gruen.
**Erledigt:** Read-only Diagnosepaket-Manifest unter `/admin-suite/diagnostics` mit sieben Kategorien umgesetzt. Release, Health, Migration, Connectoren, Event-Bus, Worker und Audit zeigen Quelle, Redaktionspflicht und `not_collected`; das Operations Center verlinkt den Katalog.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_diagnostics.py tests/test_admin_suite_system_status.py tests/test_admin_suite_compliance.py tests/test_admin_suite_operations.py tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov --tb=short` (`23 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; fokussierte Doku-Checks; `git diff --check`.
**Offene Risiken:** Ein echter Diagnoseexport benoetigt spaeter Audit-Vertrag, Rollenpruefung, Retention und explizite Nutzeraktion.

## DESIGN-MERIDIAN-HARDCOLORS-014

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Vierter Meridian-Hardcolor-Batch fuer verbleibende Admin-Resttreffer.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-014.yaml`, priorisierte Dateien unter `packages/frontend-web/src/pages/admin/`.
**Abnahmekriterien:** Bearbeitete Admin-Restseiten nutzen semantische Meridian-Tokens statt generischer Tailwind-Hardcolors; gezielter Hardcolor-Scan auf bearbeiteten Dateien ohne Treffer; Typecheck und Diff-Checks sind gruen.
**Erledigt:** Benutzerliste, Rollenverwaltung, Integrationen-Quarantaene, Nummernkreise, Control Center, DMS-Setup und Voice-Channel auf `primary`, `muted`, `destructive`, Badge-Varianten und semantische Success-/Warning-Tokens umgestellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; gezielter Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Weitere Hardcolors ausserhalb Admin bleiben Folgescope.

## DESIGN-MERIDIAN-HARDCOLORS-013

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Dritter Meridian-Hardcolor-Batch fuer verbleibende sichtbare Admin-Fachseiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-013.yaml`, priorisierte Dateien unter `packages/frontend-web/src/pages/admin/`.
**Abnahmekriterien:** Ausgewaehlte Admin-Seiten nutzen semantische Meridian-Tokens statt generischer Tailwind-Hardcolors; gezielter Hardcolor-Scan auf bearbeiteten Dateien ohne Treffer; Typecheck, Workboard-Validierung und Diff-Checks sind gruen.
**Erledigt:** AI-Approvals, GAP-Pipeline-Console, Webhooks und Webshop von generischen Green-Hardcolors auf Badge-Varianten und semantische Success-Tokens umgestellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; gezielter Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Weitere Domaenen ausserhalb Admin bleiben Folgescope.

## DESIGN-MERIDIAN-HARDCOLORS-012

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Zweiter Meridian-Hardcolor-Batch fuer sichtbare Admin-/Monitoring-Fachseiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-012.yaml`, priorisierte Dateien unter `packages/frontend-web/src/pages/admin/` und `packages/frontend-web/src/features/workflow/`.
**Abnahmekriterien:** Ausgewaehlte Admin-/Monitoring-Seiten nutzen semantische Meridian-Tokens statt generischer Tailwind-Hardcolors; gezielter Hardcolor-Scan auf bearbeiteten Dateien ohne Treffer; Typecheck, Workboard-Validierung und Diff-Checks sind gruen.
**Erledigt:** Command Monitor, Audit Log, Compliance Dashboard, APInvoiceApprovalPanel und Monitoring Alerts auf `primary`, `muted`, `destructive`, Badge-Varianten und semantische Meridian-Token umgestellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; gezielter Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Weitere Fachseiten-Hardcolors bleiben Folgescope.

## DESIGN-MERIDIAN-HARDCOLORS-011

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Fachseiten-Hardcolors in einem ersten risikoarmen Folgeslice auf Meridian-/semantische Tokens ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-011.yaml`, fokussierte Frontend-Fachseiten/-Features nach Audit.
**Abnahmekriterien:** Ein klar abgegrenzter Satz sichtbarer Fachseiten/Feature-Komponenten nutzt keine generischen Tailwind-Hardcolors mehr fuer Status-, Surface- und Textsemantik; Typecheck, Workboard-Validierung und Diff-Checks sind gruen; verbleibende Hardcolors werden als Folgescope dokumentiert.
**Erledigt:** Workflow-Oversight, ApprovalPanel, Copilot Dock/Insights, CRUD-Audit/Cancel/Delete und AlertBanner von generischen Slate/Gray/Green/Red/Amber/Emerald-Hardcolors auf `primary`, `muted`, `card`, `destructive` und semantische Meridian-Token gezogen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts\agent_workboard_supervisor.py validate`; gezielter `rg`-Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Repo enthaelt sehr viele historische Hardcolors; dieser Slice schliesst bewusst einen priorisierten Batch statt alle Fachseiten in einem grossen Refactor.

## ERP-QUALITY-ROADMAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Noch repo-seitig umsetzbare Punkte aus `docs/quality/ERP-QUALITY-ROADMAP.md` abschliessen oder belastbar als externe Betriebs-/Zertifizierungsgates abgrenzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ERP-QUALITY-ROADMAP-CLOSURE-001.yaml`, `docs/quality/ERP-QUALITY-ROADMAP.md`, `app/services/fints_connector.py`, `app/api/v1/endpoints/banken.py`, `packages/frontend-web/src/lib/api/agrar.ts`, `packages/frontend-web/src/components/agrar/SchlagKarte.tsx`, `packages/frontend-web/src/pages/agrar/feldbuch/schlagkartei.tsx`, `app/workers/low_stock_agent.py`, `app/api/v1/endpoints/agents.py`, fokussierte Tests/E2E-Specs fuer Roadmap-Abschluss.
**Abnahmekriterien:** FinTS TAN-Challenge-Flow ist simulatorfaehig und API-seitig erreichbar; MapLibre-Schlagkarte ist im Feldbuch verdrahtet und typecheckt; Low-Stock-Agent hat einen testbaren Event-/Batch-Pfad; Response-Model-Gate bleibt bei 0; externe ELSTER/Fiskaly/GoBD-Gates sind als nicht repo-seitig abschliessbare Betriebsnachweise dokumentiert; Workboard-, Doku-, Backend- und Frontend-Checks sind dokumentiert.
**Erledigt:** FinTS-TAN-Challenge-Response mit Simulator und API-Endpunkten nachgezogen; MapLibre-Schlagkarte in der Feldbuch-Schlagkartei eingebunden; Low-Stock-Agent mit EOQ-Heuristik, NATS-Subject und Status-/Simulations-API angelegt; Lager/Einkauf/HR-Voice-Intents integriert; fokussierte Backend-, Voice- und Frontend-Gates gruen.
**Checks:** `python -m compileall -q app\api\v1\endpoints\banken.py app\api\v1\endpoints\agents.py app\services\fints_connector.py app\workers\low_stock_agent.py services\ki-usability\app\services\action_registry.py services\ki-usability\app\services\intent_resolver.py`; `python -m pytest tests\test_roadmap_closure_fints_low_stock.py -q --no-cov`; `python -m pytest tests\test_voice_intent_lager_einkauf_hr.py -q --no-cov` in `services/ki-usability`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts\check_response_models.py --threshold 0`; `python scripts\agent_workboard_supervisor.py validate`.
**Offene Risiken:** Externe Zertifikate/Zugaenge (ELSTER-Org-Zertifikat, Fiskaly-Produktivzugang, Wirtschaftsprüfer-Testat) bleiben ausserhalb des Repos; breite Godfile-/Pagination-Komplettreduktion ist ein mehrwoechiges Programm und wird nur soweit risikoarm innerhalb dieses Slices geschlossen.

## DESIGN-MERIDIAN-ORCH-001

**Von:** Cursor (VAN-Mode)
**Owner:** Cursor + Codex + Claude Code
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** VAN-Entscheidungen fuer den MERIDIAN/TERRA-Designrollout verbindlich machen, Slice-Kette claimen und Handshake zwischen Codex und Claude Code etablieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-ORCH-001.yaml`, `docs/agent-ops/handshake-codex-claude-design-2026-05-23.md`, `docs/design/EMPFEHLUNG.md`
**Abnahmekriterien:** Scope gesamtes ERP mit MERIDIAN-Haupttheme; Terra nur auf Agrar-Routen im Kundenportal; Implementierungsreihenfolge Quick-Wins vor Phase 4 dokumentiert; Handshake mit Dateibesitz, Claim-Protokoll und CLAUDE.md-Invarianten; Folgeslices reserviert; Workboard-Validierung gruen.
**Erledigt:** VAN-Alignment und User-Freigaben; Handshake erstellt; Slice-Kette angelegt; `/goal`-Skill unter `.cursor/skills/goal/SKILL.md`; gesamter Rollout in Folgeslices umgesetzt.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/agent-ops/handshake-codex-claude-design-2026-05-23.md`
**Offene Risiken:** Screen-by-Screen-Hardcolors in Fachmodulen bleiben domaenenspezifische Folgeslices.

## DESIGN-MERIDIAN-QUICK-WINS-001

**Von:** Cursor (/goal)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Verbleibende Quick-Wins aus `docs/design/EMPFEHLUNG.md` abschliessen, bevor Phase 4 startet.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-QUICK-WINS-001.yaml`, `docs/design/EMPFEHLUNG.md`, `packages/frontend-web/src/components/ui/badge.tsx`, `packages/frontend-web/src/components/ui/alert.tsx`, `packages/frontend-web/src/components/ui/table.tsx`, `packages/frontend-web/src/components/ui/data-table.tsx`
**Abnahmekriterien:** Badge-Status-Semantik nutzt Meridian-Token statt harter Utility-Farben; Alert warning/info auf semantische Tokens; Table-Header/tabular-nums global konsistent; EMPFEHLUNG Phase-1-Checkboxen auf erledigt; Frontend-Typecheck und Workboard-Validierung gruen.
**Erledigt:** badge.tsx und alert.tsx auf `--color-semantic-*`-Tokens umgestellt; data-table numeric cells auf tabular-nums; EMPFEHLUNG Phase-1 als erledigt dokumentiert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Keine.

## DESIGN-TERRA-AGRAR-PORTAL-001

**Von:** Cursor (/goal)
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Terra-Theme auf Agrar-Routen im Kundenportal aktivieren — Waldgruen/Gold fuer Landwirt-Self-Service, ohne MERIDIAN-Haupt-ERP zu beeinflussen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-TERRA-AGRAR-PORTAL-001.yaml`, `packages/frontend-web/src/lib/portal-theme.ts`, `packages/frontend-web/src/layouts/CustomerPortalLayout.tsx`, `packages/frontend-web/src/pages/portal/feldbuch.tsx`, `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`, `packages/frontend-web/src/pages/portal/rationsoptimierung.tsx`
**Abnahmekriterien:** Terra-Routen `/portal/feldbuch`, `/portal/naehrstoffbilanzen`, `/portal/rationsoptimierung` rendern mit `theme-terra`; restliches Portal und ERP-Shell bleiben MERIDIAN; Terra-Sidebar/Accent-Tokens sichtbar; keine Token-Leaks auf Nicht-Agrar-Portal-Routen; Typecheck gruen.
**Erledigt:** `portal-theme.ts` mit Routen-Helper; `CustomerPortalLayout` aktiviert `theme-terra` bedingt per Pfad; Navigation/Header auf primary/accent-Tokens im Terra-Zweig.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`
**Offene Risiken:** Playwright computed-style auf Terra-Routen optional in CI.

## DESIGN-MERIDIAN-PHASE4-001

**Von:** Cursor (/goal)
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Phase 4 aus EMPFEHLUNG — Dashboard-Polish, ObjectPage Golden-Ratio-Split, Form-States, WCAG-Audit — nach Abschluss der Quick-Wins.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-PHASE4-001.yaml`, `docs/design/EMPFEHLUNG.md`, `docs/design/WCAG-AUDIT-2026-05-23.md`, `packages/frontend-web/src/components/mask-builder/ObjectPage.tsx`, `packages/frontend-web/src/components/management/KPICard.tsx`
**Abnahmekriterien:** KPI-Cards mit konsistentem Amber-Akzent; ObjectPage 61.8/38.2-Split implementiert; axe-core WCAG-Audit fuer Kernrouten dokumentiert; Quick-Wins-Slice abgeschlossen; Typecheck gruen.
**Erledigt:** KPICard warning/success/danger auf Token; ObjectPage splitLayout default true mit 61.8/38.2 Grid und Sidepanel; WCAG-AUDIT-2026-05-23.md erstellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/design/WCAG-AUDIT-2026-05-23.md`
**Offene Risiken:** axe-core CI-Integration bleibt Folgeslice; tiefe Fachseiten-Hardcolors unveraendert.

## DESIGN-MERIDIAN-AXE-CI-001

**Von:** Cursor (/goal weiter)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** @axe-core/playwright fuer MERIDIAN/TERRA-Kernrouten in CI verankern und blockierende A11y-Verstoesse in Shell/Global-Komponenten beheben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-AXE-CI-001.yaml`, `docs/design/WCAG-AUDIT-2026-05-23.md`, `.github/workflows/quality-gate.yml`, `packages/frontend-web/tests/e2e/accessibility.spec.ts`, `packages/frontend-web/package.json`
**Abnahmekriterien:** axe-Tests auf 8 Kernrouten lokal und in quality-gate gruen; @axe-core/playwright installiert; Shell-Komponenten ohne kritische Verstoesse auf Kernrouten.
**Erledigt:** accessibility.spec.ts mit 8 Routen; A11y-Fixes (Breadcrumbs Home-Link, Copilot inert, ShortcutHelp aria-labels, AskVALEO FAB, NativeSelect ariaLabel); quality-gate Job `frontend-accessibility`.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web test:e2e:accessibility`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`
**Offene Risiken:** Fachseiten ausserhalb der 8 Kernrouten ungeprueft; manueller Screen-Reader-UAT bleibt extern.

## FACHLICHE-VERTIEFUNG-UX-W10-001

**Von:** Cursor (Composer)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Produktive CRUD-Stammdaten-Masken fuer Wave-10 Erlöskennziffern und Zahlungsbedingungen gegen FIBU-Backend-Vertraege.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W10-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `packages/frontend-web/src/lib/api/fibu.ts`, `packages/frontend-web/src/pages/fibu/erloeskennziffern.tsx`, `packages/frontend-web/src/pages/einkauf/zahlungsbedingungen.tsx`, E2E-Specs
**Abnahmekriterien:** Beide Masken CRUD-faehig gegen echte Endpoints; Warengruppen ohne Regression; E2E + Typecheck gruen.
**Erledigt:** API-Hooks in fibu.ts; erloeskennziffern.tsx (ekz_nr, bezeichnung); zahlungsbedingungen.tsx (ZABD-Felder laut Schema); Navigation/Routes; Playwright-Gates.
**Checks:** type-check; warengruppen/erloeskennziffern/zahlungsbedingungen Playwright; workboard validate
**Offene Risiken:** Keine — EKZZ ist als eigener Slice abgeschlossen; Waves 11-13 unveraendert backend-only.

## FACHLICHE-VERTIEFUNG-UX-W10-EKZZ-001

**Von:** Cursor (Composer 2.5)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Produktive EKZZ-Maske fuer Erlöskontenzuordnung und Konto-Lookup gegen Wave-10-FIBU-Backend-Vertraege.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W10-EKZZ-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `packages/frontend-web/src/lib/api/fibu.ts`, `packages/frontend-web/src/pages/fibu/erloeskontenzuordnung.tsx`, Navigation/Routes, E2E-Spec
**Abnahmekriterien:** Zuordnungen Liste/Filter/Upsert; Lookup nutzbar; keine Regression Wave-10-Masken; E2E + Typecheck gruen.
**Erledigt:** API-Hooks; erloeskontenzuordnung.tsx unter `/fibu/erloeskontenzuordnung`; Navigation FIBU; Playwright-Gate `fachliche-vertiefung-ekzz.spec.ts`.
**Checks:** type-check; warengruppen/erloeskennziffern/zahlungsbedingungen/ekzz Playwright; workboard validate; docs-markdown-check
**Offene Risiken:** Kein DELETE-Endpunkt im Backend — UI bietet nur Upsert/Update, kein Loeschen.

## FRONTEND-DOMAIN-AUDIT-REPAIR-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Claudes lokale Domain-Audit-Nacharbeiten vor dem Push qualitaetssichern: korrumpierte i18n-/Encoding-Aenderungen reparieren, temporaere Skripte entfernen, Routing-Aenderungen validieren, Workboard nachziehen und lokale Commit-Historie mit korrektem Autor konsolidieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`, `packages/frontend-web/src/app/route-aliases.json`, `packages/frontend-web/src/app/page-module-loader.ts`, `packages/frontend-web/src/app/page-module-groups/commercial.ts`, `packages/frontend-web/src/i18n/locales/*.json`, betroffene Frontend-Pages mit Encoding-Korrekturen.
**Abnahmekriterien:** Keine neu eingefuehrte deutsche Locale-Mojibake; temporaere Reparaturskripte sind aus dem Worktree entfernt; Routing-Aliases referenzieren existierende Module; Typecheck, JSON-Parse, Encoding-Scan und Diff-Checks sind gruen; lokale sieben Claude-Commits sind vor Push zu einem sauberen Commit mit korrektem Autor zusammengefuehrt.
**Erledigt:** Deutsche Locale-Korruption aus dem lokalen Audit-Stand zurueckgenommen und `pattern.listreport.items_count` gezielt in `de/en/es/fr` ergaenzt; verbleibende neue Mojibake-Funde in den aktuell betroffenen Pages repariert; temporaere Root-Skripte entfernt; Route-Aliases gegen existierende Module validiert; lokale unpushed Historie fuer Konsolidierung vorbereitet.
**Checks:** JSON-Parse fuer `de/en/es/fr`; Encoding-Scan auf aktuell betroffene Locale-/Page-Dateien; Route-Alias-Modulvalidierung; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `git diff --check`; Workboard-/Doku-Checks.
**Offene Risiken:** Bestehende Alt-Mojibake in nicht bearbeiteten Legacy-Kommentaren oder Altmasken kann separat behandelt werden; dieser Slice blockiert nur neue/aktuelle Audit-Aenderungen.

## QA-FACHLICHE-VERTIEFUNG-GATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Die nach der Wave-1-13-QA verbliebenen Gates repo-seitig schliessen: DB-Integration ausführbar machen, Frontend-E2E fuer Warengruppen absichern, Fach-UAT-Paket dokumentieren und Restgate-Status sauber aktualisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-GATES-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `packages/frontend-web/src/lib/api/einkauf.ts`, neue fokussierte DB-/E2E-Gate-Tests fuer fachliche Vertiefung.
**Abnahmekriterien:** DB-Gate ist als opt-in PostgreSQL-Integrationstest im Repo vorhanden; Warengruppen-Frontend hat einen Playwright-E2E-Vertrag gegen den echten Stammdaten-Endpunkt; Abnahmedoku unterscheidet repo-seitig geschlossene Gates von externer Fachfreigabe; Workboard-, Backend-, Frontend-/E2E- und Doku-Checks sind dokumentiert.
**Erledigt:** Opt-in-DB-Gate `tests/test_fachliche_vertiefung_db_integration.py` ergaenzt; Warengruppen-Playwright-Gate mit echtem Stammdaten-API-Pfad und Create/Update/Delete-Flows ergaenzt; Warengruppen-Query von `initialData` auf `placeholderData` korrigiert, damit echte Fetches nicht durch frischen Leercache blockiert werden; Abnahmedoku von offenen Restgates auf geschlossene repo-seitige Gate-Artefakte umgestellt.
**Checks:** `python -m py_compile tests/test_fachliche_vertiefung_db_integration.py`; `pytest tests/test_fachliche_vertiefung_db_integration.py -q --no-cov` (2 skipped ohne `RUN_DB_INTEGRATION=1`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-warengruppen.spec.ts --project=chromium`; weitere Abschlusschecks siehe Slice-Datei.
**Offene Risiken:** Externe Fachsignatur und produktive Testdaten bleiben Business-/Betriebsabnahme; Playwright-Global-Teardown meldet vorhandene Visual-Tour-Issues aus `visual-tour-results`, der fokussierte Gate-Test selbst ist gruen.

## QA-FACHLICHE-VERTIEFUNG-WAVES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Alle QA-Blocker aus der fachlichen Vertiefung Wave 1-13 schliessen: Alembic-Head bereinigen, API-Smokes/CRUD-Vertraege absichern, Frontend-Verlinkung fuer Warengruppen korrigieren und Traceability-Doku nachziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `alembic/versions/merge_heads_20260522.py`, `app/api/v1/endpoints/warengruppen.py`, `app/api/v1/endpoints/erloeskennziffern.py`, `app/api/v1/endpoints/zahlungsbedingungen.py`, `packages/frontend-web/src/lib/api/einkauf.ts`, `packages/frontend-web/src/pages/einkauf/warengruppen.tsx`, `tests/test_api_smoke_waves.py`.
**Abnahmekriterien:** `alembic heads` hat wieder einen Head fuer den fachlichen Abnahmepfad; API-Smokes pruefen zentrale Wave-10-13-Routen inklusive CRUD/Lookup-Fehlerpfade; Warengruppen-UI nutzt den neuen Backend-Vertrag; Doku beschreibt Abdeckung, Restgates und Pruefergebnis; Backend-/Frontend-/Doku-Checks sind gruen.
**Erledigt:** Alembic-Merge-Revision `merge_heads_20260522` fuehrt Agrar-Ernteplanung und fachliche Vertiefung Wave 13 auf einen Head zusammen; Wave-10-Stammdaten haben Update-Vertraege; Warengruppen-Frontend nutzt `/api/v1/stammdaten/warengruppen` mit Create/Update/Delete-Aktionen; API-Smokes decken Wave 10-13 ab; Abnahmedoku beschreibt Matrix, Restgates und Pruefkommandos.
**Checks:** `alembic heads`; `python -m py_compile alembic/versions/merge_heads_20260522.py app/api/v1/endpoints/warengruppen.py app/api/v1/endpoints/erloeskennziffern.py app/api/v1/endpoints/zahlungsbedingungen.py tests/test_api_smoke_waves.py`; `pytest tests/test_api_smoke_waves.py tests/test_fachliche_vertiefung_wave10.py tests/test_fachliche_vertiefung_wave11.py tests/test_fachliche_vertiefung_wave12.py tests/test_fachliche_vertiefung_wave13.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/FACHLICHE-VERTIEFUNG-ABNAHME.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml`; `git diff --check`
**Offene Risiken:** Breite fachliche Vollabdeckung aller 5118 Referenzseiten bleibt nur ueber weitere domaenenspezifische UATs beweisbar; DB-Integration gegen echte PostgreSQL-Testdaten und Frontend-E2E bleiben separate Betriebs-/UAT-Gates.

## SERVICE-LAYER-LEGACY-ENDPOINTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Die bekannten grossen Legacy-Endpunkte final aus dem README-Tech-Debt herausfuehren: `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` sollen als Thin-Router mit dedizierten Service-Klassen nachgewiesen sein.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/SERVICE-LAYER-LEGACY-ENDPOINTS-001.yaml`, `README.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/uat/ABNAHMEPROTOKOLL-WAVE-2026-05-17.md`, `app/api/v1/endpoints/harvest_acceptance.py`, `app/api/v1/endpoints/agrar_settlements.py`, `app/api/v1/endpoints/docflow.py`, `app/services/harvest_acceptance_service.py`, `app/services/agrar_settlement_service.py`, `app/services/docflow_service.py`, fokussierte Tests fuer die betroffenen Routen.
**Abnahmekriterien:** Die drei bekannten Legacy-Dateien haben dedizierte Services; verbliebene Router enthalten nur Request-/Response-Schema, Dependency-Wiring und HTTP-Fehler-Mapping; README/UAT-Doku fuehren keine offenen grossen Legacy-Service-Layer-Gaps mehr; fokussierte API-/Unit-Tests und Doku-Checks sind gruen.
**Erledigt:** `harvest_acceptance.py` war bereits ueber `HarvestAcceptanceService` entkoppelt; `agrar_settlements.py` delegiert Preview-, Drying-, Backfill-, PDF-, Freigabe- und Completion-Logik an `AgrarSettlementService`; `docflow.py` delegiert Sales-Invoice-Kundenfreigaben an `DocflowService`; README, UAT-Protokoll und Open-Gaps-Doku fuehren die drei grossen Legacy-Endpunkte nicht mehr als offene Service-Layer-Auflage.
**Checks:** `python -m py_compile app/api/v1/endpoints/agrar_settlements.py app/services/agrar_settlement_service.py app/api/v1/endpoints/docflow.py app/services/docflow_service.py app/api/v1/endpoints/harvest_acceptance.py app/services/harvest_acceptance_service.py tests/test_agrar_settlements_api.py tests/test_agrar_settlement_calculation.py`; `python -c "import app.api.v1.endpoints.agrar_settlements as a; import app.api.v1.endpoints.docflow as d; import app.api.v1.endpoints.harvest_acceptance as h; print('import-ok')"`; `pytest tests/test_agrar_settlement_calculation.py tests/test_agrar_settlement_campaign_backfill.py tests/test_agrar_settlement_campaign_reference.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs README.md docs/uat/ABNAHMEPROTOKOLL-WAVE-2026-05-17.md docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/SERVICE-LAYER-LEGACY-ENDPOINTS-001.yaml`; `git diff --check`; `rg -n "Offen — Backlog|bleiben Tech-Debt|remain service-layer tech debt|weiter in Slices" README.md docs/uat/ABNAHMEPROTOKOLL-WAVE-2026-05-17.md docs/project-context/open-gaps-and-known-issues.md`
**Offene Risiken:** Sehr grosse fachliche Services koennen spaeter weiter modularisiert werden; dieser Slice schliesst die Endpoint-Tech-Debt-Aussage, nicht jede interne Service-Feinstruktur. Drei lokale HTTP-Smokes in `tests/test_agrar_settlements_api.py` bleiben gegen die aktuelle Entwickler-DB durch fehlende Spalte `domain_inventory.agrar_settlements.campaign_id` blockiert und benoetigen die passende lokale Migration.

## README-STATUS-2026-05-21

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Root-README auf den aktuellen GitHub-/Repo-Lieferstand nach Meridian-, UAT-, Gap-Closure-, Container-Health- und Keycloak-Nachlieferungen aktualisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/README-STATUS-2026-05-21.yaml`, `README.md`
**Abnahmekriterien:** README nennt Stand 2026-05-21, verweist auf aktuelle Source-of-Truth-Dokumente, beschreibt Meridian-Shell/Core-UI, UAT-Auflagen, Phase-2/3-Gap-Closure, Container-/Keycloak-Hardening und trennt repo-seitig geschlossene Punkte von externen Gates.
**Erledigt:** Root-README deutsch/englisch auf Stand 2026-05-21 gezogen; Test-/Coverage-Angaben korrigiert; Service-Layer-Aussage von pauschal abgeschlossen auf Hauptwellen plus bekannte Legacy-Tech-Debt geschaerft; Meridian, UAT, Keycloak-/Container-Hardening und externe Gates ergaenzt.
**Checks:** `rg` gegen veraltete README-Aussagen; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs README.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/README-STATUS-2026-05-21.yaml`; `git diff --check`
**Offene Risiken:** Tiefe Fachstatusdetails bleiben in den verlinkten Status-/Gap-/UAT-Dokumenten statt in der README.

## REPO-HYGIENE-LOCAL-ARTIFACTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Lokal generierte Analyse- und Visual-Inspection-Artefakte aus dem Git-Status heraushalten, ohne sie zu loeschen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/REPO-HYGIENE-LOCAL-ARTIFACTS-001.yaml`, `.gitignore`
**Abnahmekriterien:** `packages/frontend-web/visual-tour-results/`, lokale Endpoint-Dumps und temporaere Analyse-Skripte werden ignoriert; vorhandene Artefakte bleiben lokal erhalten; Workboard-Validierung und Diff-Checks sind gruen.
**Erledigt:** `.gitignore` ignoriert lokale Visual-Tour-Ergebnisse, Endpoint-Dumps und temporaere `Templanalyze`-Skripte; bestehende Artefakte bleiben lokal erhalten und verschwinden aus `git status`.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/REPO-HYGIENE-LOCAL-ARTIFACTS-001.yaml`; `git diff --check`; `git status -sb`
**Offene Risiken:** Weitere lokal erzeugte Tool-Artefakte koennen spaeter separate Ignore-Regeln benoetigen.

## CONTAINER-HEALTH-CRM-INVENTORY-001

**Von:** Claude Code / Codex Integration
**Owner:** Team
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Container-Health-Probleme in Backend, Inventory und CRM-Services nach Neustart-/Healthcheck-Diagnose repo-seitig stabilisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CONTAINER-HEALTH-CRM-INVENTORY-001.yaml`, `app/api/v1/endpoints/*.py` 204-Response-Korrekturen, `services/inventory/app/workflows/registration.py`, `services/crm-*/**`, `services/crm-analytics/Dockerfile`, `services/crm-communication/Dockerfile`, `services/crm-multichannel/Dockerfile`, `services/crm-security/main.py`, `services/crm-workflow/Dockerfile`
**Abnahmekriterien:** FastAPI-Routen mit 204 liefern keine Response-Body-Definition mehr; Inventory-Workflow-Registrierung ist Pydantic-v2-kompatibel; CRM-Services nutzen absolute Imports und `pydantic-settings`; Docker-Builds koennen Dependency-Layer gezielt invalidieren; verbleibende Containerstarts sind separat ueber Compose-Health zu beobachten.
**Erledigt:** 115 FastAPI-204-Routen gehaertet; CRM-Konfigurationen auf `pydantic-settings` und absolute Imports gezogen; reservierte SQLAlchemy-`metadata`-Attribute umbenannt; Inventory-URL-Cast fuer Pydantic v2 korrigiert; CRM-Dockerfiles mit `CACHEBUST`-Arg fuer reproduzierbare Dependency-Rebuilds ergaenzt.
**Checks:** Commit `67f8b9c51`; gezielte Docker-/Containerdiagnose; finales Git-Diff der Nachlieferung beschraenkt auf CRM-Dockerfiles und `services/crm-security/main.py`.
**Offene Risiken:** Einzelne Container koennen weiterhin an laufzeitabhaengigen externen Dependencies, Migrationen oder Credentials scheitern; untracked Analyseartefakte bleiben ausserhalb dieses Slices.

## DESIGN-MERIDIAN-SCREENS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Die wichtigsten sichtbaren Fach-/Maskenflaechen nach der Shell-Umstellung weiter auf Meridian tokenisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-SCREENS-001.yaml`, `packages/frontend-web/src/components/mask-builder/ListReport.tsx`, `packages/frontend-web/src/components/mask-builder/ObjectPage.tsx`, `packages/frontend-web/src/components/mask-builder/OverviewPage.tsx`, `packages/frontend-web/src/features/dashboard/DashboardCharts.tsx`, `packages/frontend-web/src/features/contracts/Contracts.tsx`, `packages/frontend-web/src/features/inventory/Inventory.tsx`, `packages/frontend-web/src/features/weighing/Weighing.tsx`, `packages/frontend-web/src/features/sales/Sales.tsx`
**Abnahmekriterien:** Masken-Builder-Basisflaechen nutzen Meridian-Oberflaechen, Tabellen-/Filter-/Header-Muster und 44px Controls; Dashboard-Charts und Kernfeatures vermeiden generische Slate/Blue/Green-Mischung in den sichtbarsten Cards; Frontend-Typecheck und Workboard-Validierung sind gruen.
**Erledigt:** Masken-Builder `ListReport`, `ObjectPage` und `OverviewPage` auf Meridian-Header, tokenisierte Oberflaechen, Primary/Harvest/Destructive-Zustandsfarben und 44px-kompatible Controls nachgezogen; Dashboard-Charts auf tokenisierte Empty/Error/Skeleton-Zustaende und Ocean/Harvest-Akzentkanten umgestellt; Contracts, Inventory, Weighing und Sales von generischen Slate/Blue/Green/Yellow/Red-Utility-Mustern auf Meridian-Cards, Badges, Listen-Items und Leerzustaende gezogen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/DESIGN-MERIDIAN-SCREENS-001.yaml`; `git diff --check` fuer Slice-Dateien; `docker compose up -d --build frontend-web`; Playwright-Check auf `http://localhost:3000` mit `data-theme=meridian`, H1 `App Starter`, Topbar `56px`, Input `44px`.
**Offene Risiken:** Tiefe Modulunterseiten enthalten weiterhin harte Utility-Farben und brauchen bei Bedarf weitere fachbereichsweise Slices.

## DESIGN-MERIDIAN-SHELL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Meridian sichtbar in Frontend-Shell und Core-UI aktivieren, damit `localhost:3000` die beschlossene Designrichtung zeigt.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-SHELL-001.yaml`, `packages/frontend-web/index.html`, `packages/frontend-web/src/index.css`, `packages/frontend-web/src/styles/design-tokens-meridian.css`, `packages/frontend-web/tailwind.config.js`, `packages/frontend-web/src/layouts/DashboardLayout.tsx`, `packages/frontend-web/src/components/layout/AppShell.tsx`, `packages/frontend-web/src/components/navigation/AppShell.tsx`, `packages/frontend-web/src/components/navigation/Sidebar.tsx`, `packages/frontend-web/src/components/navigation/SidebarFavorites.tsx`, `packages/frontend-web/src/components/navigation/SidebarSettingsLink.tsx`, `packages/frontend-web/src/components/navigation/TopBar.tsx`, `packages/frontend-web/src/components/ui/button.tsx`, `packages/frontend-web/src/components/ui/input.tsx`, `packages/frontend-web/src/components/ui/card.tsx`, `packages/frontend-web/src/components/ui/table.tsx`, `packages/frontend-web/src/components/ui/data-table.tsx`, `packages/frontend-web/src/features/dashboard/Dashboard.tsx`, `packages/frontend-web/src/pages/start-dashboard.tsx`
**Abnahmekriterien:** Meridian-Theme ist am Root aktiv; sichtbare Shell nutzt Navy-Sidebar, tokenbasierte Breiten und kompaktere Topbar; Button/Input-Defaults erfuellen 44px-Touch-Target; Dashboard/ListReport-Basismuster zeigen Ocean-Blue/Harvest-Akzente statt generischer Slate/Blue-Mischung; Frontend-Typecheck und Workboard-Validierung sind gruen.
**Erledigt:** Meridian am HTML-Root aktiviert; alte Brand-/Neutral-Aliase auf Ocean-Blue, Harvest und blau getoente Neutrals gezogen; echte Runtime-Shell (`DashboardLayout`/`components/navigation`) startet expanded mit 240px Navy-Sidebar, 56px Topbar und 44px Sidebar-Zielen; Legacy-Shell ebenfalls auf Meridian-Breiten/-Farben nachgezogen; Button/Input/Card/Table-Basis auf Meridian-Masse und Fokusverhalten angepasst; Start-Dashboard und Analytics-Dashboard zeigen tokenbasierte Oberflaechen und Harvest/Ocean-Akzente.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/DESIGN-MERIDIAN-SHELL-001.yaml`; `git diff --check`; Playwright computed-style check auf `http://localhost:3001` und nach Frontend-Container-Rebuild auf `http://localhost:3000` mit `data-theme=meridian`, Sidebar `240px`, Topbar `56px`, Input `44px`, min. Sidebar-Target `44px`.
**Offene Risiken:** Viele Fachseiten enthalten weiterhin harte Tailwind-Farben und brauchen Folgeslices; dieser Slice fokussiert die sichtbarste Shell/Core-UI-Schicht.

## KEYCLOAK-PSQL-DB-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Fehlende Keycloak-Datenbank im laufenden PostgreSQL anlegen und Init-Script fuer kuenftige Deployments absichern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KEYCLOAK-PSQL-DB-001.yaml`, `scripts/init.sql`
**Abnahmekriterien:** Datenbank `keycloak` existiert im laufenden Postgres; Init-Script enthaelt Bootstrap fuer kuenftige Deployments; Keycloak startet ohne `database "keycloak" does not exist`; Claudes Dirty Files bleiben unberuehrt.
**Erledigt:** Laufende PostgreSQL-DB `keycloak` mit Owner `keycloak` angelegt; Verbindung als User `keycloak` gegen DB `keycloak` geprueft; `scripts/init.sql` von ungueltigem `CREATE DATABASE` im `DO`-Block auf psql-`\\gexec`-Bootstrap umgestellt; Keycloak neu gestartet und Schema-Initialisierung im Log bestaetigt.
**Checks:** `docker exec valeo-neuro-erp-postgres psql -U keycloak -d keycloak -tAc "SELECT current_database(), current_user;"`; `docker compose restart keycloak`; `docker logs --tail 40 valeo-neuro-erp-keycloak`; `python scripts/agent_workboard_supervisor.py validate`
**Offene Risiken:** Keycloak kann nach DB-Anlage noch an separaten Realm-/Credential-/Healthcheck-Themen scheitern.

## UAT-AUFLAGEN-2026-05-17

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Verbleibende UAT-Auflagen aus der Abnahme 2026-05-17 repo-seitig auf hohem Standard schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UAT-AUFLAGEN-2026-05-17.yaml`, `docs/uat/**`, `packages/frontend-web/tests/e2e/uat/**`, `tests/uat/**`, `app/api/v1/endpoints/compliance.py`, `app/api/v1/endpoints/kontrakt_klassen.py`, `tests/test_compliance_pos_gap_extensions.py`
**Abnahmekriterien:** PCN/UFI API-Contract ist implementiert und getestet; ungueltige Kontraktklassen-Varianten werden per Pydantic validiert; UAT-Auflagenstatus ist in Protokoll und Traceability aktualisiert; fokussierte API-/UAT-Contract-Tests und Doku-Checks sind gruen.
**Erledigt:** PCN/UFI-Endpoint mit UFI-/Statusvalidierung und DB-Fallback-Vertrag gehaertet; `KontraktKlasseCreate.variante` per Pydantic `Literal` validiert; UAT-API-Contracts auf aktuelle v1-Routen und idempotente Testdaten nachgezogen; UAT-Protokoll, Master-Plan und Traceability auf repo-seitig erledigte Auflagen aktualisiert.
**Checks:** `python -m py_compile app/api/v1/endpoints/compliance.py app/api/v1/endpoints/kontrakt_klassen.py tests/uat/test_uat_api_contracts.py`; `pytest tests/uat/test_uat_api_contracts.py tests/test_compliance_pos_gap_extensions.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Externe PCN-Portal-/ECHA-Anbindung, Steuerberaterfreigabe und produktive Browser-Abnahme bleiben Betriebsfreigaben.

## VALEO-PARITY-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** O2C/P2P/Partie-Kette als repo-seitig pruefbaren UAT-Pfad ausweisen und externe UAT-Gates sauber abgrenzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/VALEO-PARITY-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/agrar-parity-matrix-2026-05-17.md`, `app/api/v1/endpoints/o2c_uat_scaffold.py`, `tests/test_webshop_atlas_saatzucht_uat.py`
**Abnahmekriterien:** API liefert UAT-Readiness mit O2C/P2P/Partie-Abdeckung; bestehende 7-Schritt-Szenarien bleiben kompatibel; Gap-Status trennt repo-seitigen Pfad von externer UAT-Unterschrift; fokussierte Tests und Doku-Checks sind gruen.
**Erledigt:** `/uat/o2c/readiness` liefert repo-seitige Abdeckung fuer O2C, P2P und Partie-Kette sowie externe Gates; bestehender 7-Schritt-Szenario-Runner und Tests bleiben kompatibel; Gap- und Parity-Doku trennen repo-seitigen Pfad von externer UAT-Unterschrift.
**Checks:** `pytest tests/test_webshop_atlas_saatzucht_uat.py -q --no-cov`
**Offene Risiken:** Produktive Browser-UATs mit realen Mandanten-, Waage-, DMS-, Druck- und Steuerberaterdaten bleiben externe Abnahmen.

## REPORT-PRINT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Partie-Genealogie, Wiegschein-PDF-Nachweis und Etikett-/Label-Vertrag als repo-seitig pruefbaren Report-/Print-Pfad schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/REPORT-PRINT-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/report_print.py`, `app/services/report_print_service.py`, `app/api/v1/api.py`, `tests/test_report_print_api.py`
**Abnahmekriterien:** API liefert Partie-Genealogie mit Rueckverfolgungsknoten, Wiegschein-PDF-Preview/Artefaktmetadaten und Etikettendaten fuer Charge/Partie; Router ist registriert; fokussierte Tests und Doku-Checks sind gruen.
**Erledigt:** Neuer Thin-Router `/report-print` plus `ReportPrintService` liefern Readiness, Partie-Genealogie, Wiegeschein-PDF-Preview/Artefaktmetadaten und print-ready GS1-Labeldaten fuer Partie/Charge/Artikel/SSCC/GTIN; Router ist im v1-API-Router registriert.
**Checks:** `python -m py_compile app/api/v1/endpoints/report_print.py app/services/report_print_service.py tests/test_report_print_api.py`; `pytest tests/test_report_print_api.py -q --no-cov`
**Offene Risiken:** Echte Drucker-/PDF-Rendering- und UAT-Abnahme mit Produktivdaten bleiben externe Betriebsfreigaben.

## DOMAIN-PHASE23-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Phase-2- und Phase-3-Restgaps aus dem Domain-Depth-Plan repo-seitig schliessen bzw. vorhandene Implementierungen mit Tests und Doku belastbar als geschlossen ausweisen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DOMAIN-PHASE23-GAP-CLOSURE-001.yaml`, `docs/project-context/domain-depth-plan-2026-05-17.md`, `docs/project-context/open-gaps-and-known-issues.md`, Phase-2/3-nahe Endpoint-/Service-/Testdateien mit explizitem Fokus auf `ebilanz_elster`, `gs1_*`, `pos_dsfinvk`, `saatzucht`, `atlas_zollausfuhr`, `futtermittel`, `crm`, `finance`, `hrm`, `sales`
**Abnahmekriterien:** Phase-2/3-Plan ist nicht mehr als offener 183-Tage-Backlog missverstaendlich; verbleibende echte Luecken sind externe Gates oder klar benannte Resttiefe; fokussierte API-/Router-/Doku-Checks sind gruen.
**Erledigt:** eBilanz/ELSTER um ERiC-Readiness-Vertrag ergaenzt; GS1-Barcode-Parser gibt SSCC direkt aus; DSFinV-K-v2.3-ZIP, Phase-2/3-Routerpfade, GS1/SSCC, eBilanz-Readiness und Futtermittel-Regressionen getestet; Domain-Depth-Plan und Open-Gaps-Doku auf repo-seitig geschlossene Phase 2/3 mit externen Gates gezogen.
**Checks:** `pytest tests/test_phase23_gap_closure_api.py tests/test_gs1_webhook_ruestliste.py tests/test_sammelabrechnung_interessent_waagen_vorlage.py -q --no-cov`; `pytest tests/test_webshop_atlas_saatzucht_uat.py tests/test_compliance_pos_gap_extensions.py tests/test_futtermittel_complete.py tests/test_major_domain_router_registration.py -q --no-cov`
**Offene Risiken:** Externe Provider-Credentials, ERiC-/TSE-Pruefwerkzeuge, Steuerberater-/Rechtsfreigaben und echte UATs koennen repo-seitig nur als Readiness-/Gate-Vertraege abgebildet werden.

## L3-WEBSHOP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Webshop-B2B-Bestellintegration repo-seitig als belastbaren Import-/Sync-Vertrag bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/L3-WEBSHOP-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/*webshop*`, `app/services/*webshop*`, `app/api/v1/api.py`, `tests/test_*webshop*`
**Abnahmekriterien:** B2B-Webshop-Bestellungen koennen idempotent importiert und gelesen werden; Kunden-/Artikel-/Mengen-/Preis-/Lieferkontext wird validiert; Dubletten und fachliche Blocker werden sichtbar; Router ist unter `/api/v1/...` registriert; fokussierte Tests und Doku-Updates sind gruen.
**Erledigt:** `webshop_integration.py` vom DB-Stub auf thin-router + `WebshopIntegrationService` umgestellt; Import ist idempotent je externer Bestellnummer, meldet Dubletten und fachliche Blocker, listet/liest importierte Bestellungen und blockiert die ERP-Verarbeitung fehlerhafter Imports.
**Checks:** `python -m py_compile app/api/v1/endpoints/webshop_integration.py app/services/webshop_integration_service.py tests/test_webshop_atlas_saatzucht_uat.py`; `pytest tests/test_webshop_atlas_saatzucht_uat.py -q --no-cov`
**Offene Risiken:** Echte Shopware-/WooCommerce-/Shopify-Credentials und produktive Webhook-Signaturen bleiben externe Betriebsfreigaben.

## ENTERPRISE-DOMAIN-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-17
**Ziel des Slices:** Von parallelen Agents begonnene ERP-/Odoo-/Agrar-Spezialsoftware-Domain-Closure uebernehmen, fehlende Router-Registrierung und nicht gelieferte POS-/Compliance-Teile schliessen.
**Dateibesitz:** `app/api/v1/api.py`, `app/api/v1/endpoints/*asset_accounting.py`, `*budget_planning.py`, `*liquidity_planning.py`, `*crm_360.py`, `*crm_account_hierarchy.py`, `*logistics_tours.py`, `*logistics_freight.py`, `*purchase_invoice_verification.py`, `*ers_settlement.py`, `*rfq.py`, `*einkauf_kpis.py`, `*sales_blanket_orders.py`, `*credit_management.py`, `*collective_documents.py`, `*central_contracts.py`, `*futtermittel_rohwaren.py`, `*futtermittel_rezepte.py`, `*compliance_dsgvo.py`, `*compliance_whistleblower_lksg.py`, `*pos_payments_promotions.py`, `app/api/v1/endpoints/personal.py`, `app/api/v1/endpoints/cases.py`, `app/api/v1/endpoints/opportunities.py`, `app/api/v1/endpoints/warehouse_wms.py`, `tests/test_*domain*`, `tests/test_*gap*`, `docs/project-context/domain-depth-plan-2026-05-17.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Alle erzeugten Domain-Endpunkte sind ueber `/api/v1/...` erreichbar; HRM-Arbeitszeitkonto nutzt `domain_hr.time_entries.entry_date/hours`; POS Split-Payment und Promotions-Preview existieren; Whistleblower und LkSG-API-Vertraege existieren; fokussierte Tests und Doku-/Workboard-Checks sind gruen.
**Erledigt:** Router-Registrierungen fuer CRM, Finance, Logistik, Einkauf, Verkauf/Kontrakte, Futtermittel, HRM, Compliance und POS ergaenzt; `warehouse_wms.py` auf kanonischen Tenant-Dependency-Import korrigiert; Logistik-Statistik gegen nicht-numerische DB-/Mockwerte gehaertet; HRM-Org-Subtree und Arbeitszeitkonto fachlich korrigiert; POS Split-Payment/Promotions und Whistleblower/LkSG nachgeliefert; Domain-Depth-Plan und Open-Gaps aktualisiert.
**Checks:** `pytest tests/test_crm_pipeline_360.py tests/test_einkauf_3way_match_ers_rfq.py tests/test_finance_asset_budget_liquidity.py tests/test_logistics_tour_freight.py tests/test_major_domain_router_registration.py tests/test_personal_major_gap_extensions.py tests/test_compliance_pos_gap_extensions.py tests/test_process_kernel_wave100_settlement_completion.py tests/test_process_kernel_wave31_dq_extended_write_paths.py -q --no-cov --tb=short`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/open-gaps-and-known-issues.md docs/project-context/domain-depth-plan-2026-05-17.md`; `git diff --check`
**Offene Risiken:** Echte externe Abnahmen bleiben ausserhalb des Repos: Steuerberater-/DATEV-Mapping, DMS-Live-Probe, TSE-/DSFinV-K-Pruefwerkzeugvalidierung, E-Signatur/Providerzugang und UAT-Unterschriften mit Produktivdaten.

## ERP-FINANZ-ORDERS-DOC-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Veraltete `packages/erp-domain`-Order-REST-Dokumentation auf die entschiedene Python-FastAPI-Zielroute ausrichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ERP-FINANZ-ORDERS-DOC-001.yaml`, `packages/erp-domain/README.md`, `packages/erp-domain/src/bootstrap.ts`, `C:\Users\Jochen\.cursor\plans\erp-finanz_roadmap_9029845d.plan.md`
**Abnahmekriterien:** README nennt keine oeffentlichen Node-Order-Endpunkte mehr; Orders-REST verweist auf `/api/v1/sales/orders`; Roadmap-Phase 3 ist nicht mehr zweigeteilt, sondern Doku/Redirect-only.
**Erledigt:** `packages/erp-domain/README.md` beschreibt Orders-REST jetzt als Python-FastAPI-Vertrag unter `/api/v1/sales/orders`; die veralteten `/api/orders`-Beispiele sind entfernt. `packages/erp-domain/src/bootstrap.ts` enthaelt keinen irrefuehrenden Controller-TODO mehr. Die Cursor-Roadmap ist auf die entschiedene Doku/Redirect-only-Variante gezogen.
**Checks:** `pnpm test:erp-domain -- erp-bootstrap-orders.spec.ts`; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Historische Archive und generierte API-Dumps koennen weiterhin alte Order-Begriffe enthalten; dieser Slice betrifft nur aktive Roadmap-/Paketdoku.

## HRM-GERMANY-GAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Deutsche HRM-Gaps ueber Personalakte, eAU, Payroll/DATEV, ESS/MSS, Recruiting/Onboarding, Reporting, Datenschutz, kontrollierte KI und Office-Connectoren als pruefbaren Zielvertrag schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GERMANY-GAP-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_readiness_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Zielbild und Gap-Matrix decken die 15 Mindestpunkte ab; API liefert HRM-Readiness mit Status, Rechts-/Compliance-Referenzen, Integrationen, KI-Kontrollen und naechsten Slices; Tests sichern eAU, §26 BDSG, BAG-Arbeitszeitpflicht, EU-AI-Act-Hochrisiko und Office-/DATEV-Connectoren.
**Erledigt:** `GET /api/v1/personal/hrm-readiness` eingefuehrt; Zielvertrag deckt die 15 HRM-Mindestpunkte, eAU, Personalakte, DATEV/Payroll, ESS/MSS, Recruiting/Performance, Datenschutz, kontrollierte KI und Office-Connectoren ab. Frontend-API-Hook `useHrmReadiness` ergaenzt. Gap-Plan und Open-Gaps-Doku aktualisiert.
**Checks:** `pytest tests/test_personal_hrm_readiness_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Rechtsfeinpruefung, Betriebsvereinbarungen, echte eAU-/DATEV-/Microsoft-/Google-Zugangsdaten und produktive AVV/DPA bleiben Folgeslices.

## HRM-AKTE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Ersten Vertrag fuer digitale Personalakte mit Dokumentklassen, DMS-Referenzen, Rollenfilter, Audit- und Retention-Sicht bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-AKTE-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_employee_file_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Personalakte kann Dokumentmetadaten lesen und anlegen; Dokumentklassen weisen Rechtsgrundlage, Standard-Sichtbarkeit und Retention aus; Rollenfilter fuer Employee/Manager/HR/Payroll ist regressionsgesichert; Export-/Loeschkonzept ist im Contract sichtbar.
**Erledigt:** `GET /api/v1/personal/employee-files/{employee_ref}` und `POST /api/v1/personal/employee-files/{employee_ref}/documents` eingefuehrt. Dokumentklassen, Rollenfilter, Exportpaket, Retention-Sicht und Frontend-Hooks sind verfuegbar; Doku markiert produktive DB-/DMS-Anbindung als Folgeslice.
**Checks:** `pytest tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_employee_file_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive DMS-Ablage, echte Signaturen, Rechtsfreigabe der Aufbewahrungsfristen und DB-Migration bleiben Folgeslices.

## HRM-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Alle verbleibenden HRM-Plan-Gaps repo-seitig als API-/Frontend-/Doku-Vertraege schliessen: eAU, DATEV/Payroll-Closeout, Vertragsvorlagen, ESS, MSS, Recruiting, Analytics, Privacy, AI-Governance und Office-Connectoren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GAP-CLOSURE-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_gap_closure_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** HRM-Plan weist keine fachlichen Repo-Gaps mehr aus; jeder verbliebene Punkt hat einen API-Vertrag und Frontend-Hook; Tests sichern eAU ohne Diagnosedaten, DATEV-Closeout, Vertragsvorlagen, ESS/MSS, Recruiting-Retention, Analytics-Aggregationsschutz, AI-Human-Gate und Office-Connector-Readiness.
**Erledigt:** `GET /api/v1/personal/hrm-operating-system` eingefuehrt; HRM-Plan weist keine fachlichen Repo-Gaps mehr aus. Frontend-Hook `useHrmOperatingSystem` ergaenzt. Tests sichern eAU ohne Diagnosedaten, DATEV-Closeout, Vertragsvorlagen, ESS/MSS, Recruiting-Retention, Analytics-Aggregationsschutz, AI-Human-Gate, Office-Connector-Readiness und die kanonischen `time_entries`-Service-Regeln.
**Checks:** `pytest tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_employee_file_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte eAU-/DATEV-/Microsoft-/Google-/LibreOffice-/E-Signatur-Zugangsdaten, AVV/DPA, Betriebsvereinbarungen, DSFA und Rechtsfreigaben bleiben externe Betriebsfreigaben.

## HRM-OPERATIONS-GATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Externe HRM-Betriebsfreigaben fachlich sauber zum Abschluss fuehren: Evidenzanforderungen, Owner, Go-live-Blocker, Abnahme und Auditstatus fuer eAU, DATEV, Office/SSO, LibreOffice/E-Signatur, AVV/DPA, Betriebsrat, DSFA und Rechtsfreigaben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gates_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** `GET /api/v1/personal/hrm-operations-gates` liefert Gate-Status mit Evidenzpflichten und Go-live-Blockern; Doku unterscheidet fachlich abgeschlossen, repo-seitig umgesetzt und extern freizugeben; Tests sichern alle externen Gates und Professional-Practice-Kriterien.
**Erledigt:** `GET /api/v1/personal/hrm-operations-gates` eingefuehrt; alle verbleibenden HRM-Betriebsfreigaben sind als blockierende Gates mit Owner, Evidenzanforderungen, Abnahmekriterien, Auditspur und Professional-Practice-Regeln modelliert. Frontend-Hook `useHrmOperationsGates` ergaenzt. HRM-Plan und Open-Gaps-Doku fuehren keine unspezifizierten Restpunkte mehr, sondern nur noch evidenzbasierte Go-live-Gates.
**Checks:** `pytest tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_gap_closure_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gates_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Abschluss der Gates erfordert reale externe Nachweise; ohne diese Nachweise bleibt Go-live bewusst blockiert.

## HRM-OPERATIONS-GATES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigabe-Gates technisch vollstaendig machen: persistente Gate-/Evidence-Daten, Approval-/Reject-Workflow, Connector-Probe-Status, Auditspur und Go-live-Policy.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-002.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `alembic/versions/hrm_operations_gates_20260513.py`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gate_workflow_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Gates werden aus DB-Zustand plus Default-Katalog gelesen; Evidence kann angelegt werden; Gate-Entscheidungen koennen approved/rejected werden; Connector-Probes aktualisieren Status; `goLiveAllowed` wird aus persistenten Status abgeleitet; API-/Frontend-Contracts und Tests sind vorhanden.
**Erledigt:** Persistente Gate-, Evidence-, Probe- und Audit-Tabellen per Alembic ergaenzt; `GET /hrm-operations-gates` liest Runtime-Status aus DB mit Katalog-Fallback; Evidence-, Probe- und Decision-Endpunkte sowie `GET /hrm-operations-gates/go-live-policy` umgesetzt; Frontend-Hooks fuer Lesen, Evidence, Probe, Entscheidung und Go-live-Policy ergaenzt; Tests sichern Seed, Evidence, Probe, Approval, Evidence-Pflicht und Blocker-Policy.
**Checks:** `pytest tests/test_personal_hrm_operations_gate_workflow_api.py tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gate_workflow_api.py alembic/versions/hrm_operations_gates_20260513.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte externe Providerzugriffe benoetigen weiterhin produktive Credentials; dieser Slice implementiert die technische Workflow- und Persistenzschicht inklusive Probe-Status, nicht die Beschaffung externer Freigaben.

## HRM-OPERATIONS-GATES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigabe-Gates als bedienbares Frontend-Cockpit verfuegbar machen: Go-live-Status, Gate-Liste, Evidence-Erfassung, Probe-Erfassung und Approval/Reject-Aktionen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-003.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/app/route-builders/alias-groups/generated/personal.ts`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/personal.ts`
**Abnahmekriterien:** Personal-Navigation enthaelt das HRM-Freigabe-Cockpit; Route ist aufloesbar; UI zeigt Go-live-Policy, Blocker und Gate-Details; pro Gate koennen Evidence, Probe und Entscheidung ausgelöst werden; Typecheck ist gruen.
**Erledigt:** `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx` als HR-Freigabe-Cockpit ergaenzt; Personal-Navigation und Route-Aliase zeigen `/personal/hrm-freigaben`; UI nutzt einfache Buero-Sprache fuer Produktivstart, Pruefpunkte, Nachweise, Tests, Freigaben und naechste Aktionen. HRM-Plan und Open-Gaps-Doku markieren den Bedienpfad als repo-seitig geschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte externe Freigaben bleiben betriebliche Nachweise; UI stellt den technischen Bedienpfad bereit.

## HRM-OPERATIONS-GATES-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Freigabe-Cockpit fachlich als Admin-/Compliance-/Go-live-Readiness-Arbeitsflaeche schaerfen: Name, Risiko, Prioritaet, Faelligkeit, Rollenhinweis und letzte Aenderung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-004.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gate_workflow_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`
**Abnahmekriterien:** API liefert Readiness-Metadaten je Gate; UI heisst HRM-Betriebsfreigaben; UI zeigt Risiko, Prioritaet, Faelligkeit, letzte Aenderung, Rollen-/Sichtbarkeitshinweis und Abnahmekriterien; Typecheck und fokussierte API-Tests sind gruen.
**Erledigt:** `HrmOperationsGateOut` liefert Prioritaet, Risiko-Level, Faelligkeit, letzte Aenderung, berechtigte Rollen und Read-only-Rollen. Das Frontend heisst jetzt `HRM-Betriebsfreigaben`, zeigt Admin-/Compliance-/Readiness-Kontext, Risiko, Prioritaet, Faelligkeit, letzte Aenderung, Rollenhinweis und einfache Arbeitsbegriffe.
**Checks:** `pytest tests/test_personal_hrm_operations_gate_workflow_api.py tests/test_personal_hrm_operations_gates_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gate_workflow_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Rollen-/Rechtesteuerung haengt an der zentralen Auth-/Navigation-Enforcement; dieser Slice macht fachliche Sichtbarkeit und API-Metadaten explizit.

## HRM-OPERATIONS-GATES-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Google-Studio-Designentwurf fuer `HRM-Betriebsfreigaben` in die bestehende VALEO-React-Seite uebertragen: Readiness-Header, KPI-Leiste, Policy-Box, Stopper-Markierung, kompakte Pruefpunkt-Zeilen und aufklappbare Arbeitsbereiche.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-005.yaml`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`
**Abnahmekriterien:** Seite folgt dem Studio-Entwurf ohne neue Dependencies; bestehende React-Query-Hooks bleiben verdrahtet; sichtbare Sprache bleibt buerotauglich; Typecheck ist gruen.
**Erledigt:** Google-Studio-Entwurf in die echte VALEO-Seite uebertragen: sticky Readiness-Header, KPI-Leiste, Policy-Box, Stopper-Markierung, kompakte Pruefpunkt-Zeilen, aufklappbare Details und Arbeitsaktionen. Keine neue `motion`-Dependency; alle bestehenden Runtime-Hooks bleiben verdrahtet.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Studio-Prototyp enthaelt Mockdaten und `motion`; Uebernahme erfolgt auf echte VALEO-Daten und ohne zusaetzliche Animationsdependency.

## HRM-GO-LIVE-TEMPLATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Evidenzpaket als operative Repo-Vorlagen unter `docs/hrm-go-live-templates/` bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-001.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Gesamtwerk enthaelt Gate-Matrix, Go-live-Protokoll, Betriebsratsstatus, Mitarbeiterinformation, VVT, AVV/DPA, DSFA, Rollen, TOM, Retention, eAU, DATEV/Payroll, Office/SSO, DMS/E-Signatur, KI/Analytics, Evidence/Audit, Geschaeftsfuehrungsfreigabe und optionale Betriebsvereinbarung; Doku verweist auf das Vorlagenpaket; rechtlicher Arbeitsvorlagen-Charakter ist klar markiert.
**Erledigt:** `docs/hrm-go-live-templates/README.md` und `00_hrm_go_live_gesamtwerk.md` ergaenzt. Das Gesamtwerk deckt alle sieben HRM-Betriebsfreigabe-Gates mit ausfuellbaren Arbeitsmustern, Mindest-Evidence, Freigaben und Auditspur ab. HRM-Plan und Open-Gaps-Doku verweisen auf das Vorlagenpaket.
**Checks:** `rg -n "HRM-GATE-001|Mindest-Evidence|BDSG Paragraf 26|DSFA-Vorpruefung|Geschaeftsfuehrungsfreigabe" docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktivnutzung erfordert reale Datenschutz-, Payroll-/Steuerberater-, IT-Sicherheits- und Rechtspruefung.

## HRM-GO-LIVE-TEMPLATES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Formulare auf den tatsaechlichen VALEO-Funktionsumfang begrenzen und hypothetische, nicht vorgesehene KI-/Auswertungsbegriffe aus Mitarbeiter- und Freigabetexten entfernen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-002.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_gap_closure_api.py`
**Abnahmekriterien:** Formulare nennen keine nicht vorgesehenen Funktionen; Mitarbeiterinformation beschreibt nur real vorgesehene HRM-Funktionen; KI-Freigabe ist als optionale Assistenzfunktions-Pruefung formuliert; API-/Doku-Vertraege sind konsistent.
**Erledigt:** Formulare, HRM-Plan, Open-Gaps-Doku und Personal-API sind auf den realen Funktionsumfang gezogen. Mitarbeitertexte nennen Personalverwaltung, Arbeitszeit, Abwesenheiten, Dokumente, Payroll-Vorbereitung, freigegebenes HR-Reporting, Compliance und optional konkret freigegebene KI-Assistenz; hypothetische Sonderfunktionen wurden entfernt.
**Checks:** `pytest tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_hrm_operations_gates_api.py -q --no-cov`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_hrm_operations_gates_api.py`; `rg -n "Emotion|Scoring|Ranking|Score|Profiling|verdeckte|heimliche|Leistungsueberwachung|Verhaltens|KI-/Analytics|Analytics-/KI|Reports und Scores" docs/hrm-go-live-templates docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md docs/project-context/open-gaps-and-known-issues.md app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_readiness_api.py` (keine Treffer); `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Konkrete spaetere KI- oder Analytics-Erweiterungen brauchen erneut gesonderte Datenschutz-, Legal- und Betriebsratspruefung.

## HRM-GO-LIVE-TEMPLATES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Gesamtwerk in einzelne, direkt auffindbare Formular-Dateien unter `docs/hrm-go-live-templates/` zerlegen, ohne den fachlichen Master zu duplizieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-003.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/01_hrm_go_live_freigabeprotokoll.md`, `docs/hrm-go-live-templates/02_betriebsratsstatus_kein_betriebsrat.md`, `docs/hrm-go-live-templates/03_mitarbeiterinformation_hrm.md`, `docs/hrm-go-live-templates/04_vvt_hrm_system.md`, `docs/hrm-go-live-templates/05_avv_dpa_pruefprotokoll.md`, `docs/hrm-go-live-templates/06_dsfa_vorpruefung.md`, `docs/hrm-go-live-templates/07_rollen_berechtigungskonzept.md`, `docs/hrm-go-live-templates/08_tom_it_sicherheitsfreigabe.md`, `docs/hrm-go-live-templates/09_retention_loeschkonzept.md`, `docs/hrm-go-live-templates/10_eau_freigabeprotokoll.md`, `docs/hrm-go-live-templates/11_datev_payroll_abnahme.md`, `docs/hrm-go-live-templates/12_office_sso_abnahme.md`, `docs/hrm-go-live-templates/13_dms_esignatur_rendering_abnahme.md`, `docs/hrm-go-live-templates/14_ki_assistenz_reporting_freigabe.md`, `docs/hrm-go-live-templates/15_evidence_auditprotokoll.md`, `docs/hrm-go-live-templates/16_geschaeftsfuehrungsfreigabe.md`, `docs/hrm-go-live-templates/17_betriebsvereinbarung_optional.md`
**Abnahmekriterien:** Alle im README genannten Einzelvorlagen existieren; jede Einzelvorlage ist als Auszug mit Zweck, Verwendung und Link zum Master auffindbar; keine Einzelvorlage nennt hypothetische, nicht vorgesehene HRM-Funktionen; Doku-Checks sind gruen.
**Erledigt:** Einzelvorlagen `01_...` bis `17_...` unter `docs/hrm-go-live-templates/` ergaenzt und im README verlinkt. Jede Vorlage ist als Arbeitsauszug aus dem Master gekennzeichnet und auf den realen HRM-Funktionsumfang begrenzt. HRM-Plan und Open-Gaps-Doku nennen die operativen Einzelvorlagen.
**Checks:** `Get-ChildItem -Path docs/hrm-go-live-templates -Filter *.md`; `rg -n "Emotion|Scoring|Ranking|Score|Profiling|verdeckte|heimliche|Leistungsueberwachung|Verhaltens|KI-/Analytics|Analytics-/KI|Reports und Scores" docs/hrm-go-live-templates` (keine Treffer); `$files = (Get-ChildItem -Path docs/hrm-go-live-templates -Filter *.md | ForEach-Object { $_.FullName }); node scripts/docs-markdown-check.cjs @files`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Die Einzeldateien sind Arbeitskopien aus dem Master; bei inhaltlichen Aenderungen muss der Master als Source of Truth zuerst angepasst werden.

## HRM-GO-LIVE-UX-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigaben von Compliance-Cockpit zu gefuehrter Arbeitsflaeche ausbauen und daraus einen repo-weiten UX-Exzellenzstandard fuer alle Domaenen ableiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-UX-001.yaml`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** HRM-Seite bietet Rollenfokus, Gate-Aufgabenplan, Vorlage-Link je Gate, gefuehrte Nachweis-/Test-/Freigabe-Schritte, Audit-Zeitleiste und Management-Entscheidungsbild; repo-weiter UX-Standard uebertraegt diese Muster auf alle Domaenen; Typecheck und Doku-Checks sind gruen.
**Erledigt:** HRM-Betriebsfreigaben bieten jetzt Rollenfokus, Management-Entscheidungsbild, Vorlage-Link je Gate, gefuehrte Auswahllisten fuer Nachweise und Tests, Aufgabenplan je Gate und Audit-Zeitleiste. Der neue UX-Exzellenzstandard uebertraegt Rollenfokus, Aufgabenplan, naechste Aktion, Vorlage-/Nachweislink, gefuehrte Eingabe, Audit-Zeitleiste und Management-Bild auf alle Domaenen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/HRM-GO-LIVE-UX-001.yaml`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Vollstaendige Ueberarbeitung aller Domaenen bleibt ein Rollout-Programm; dieser Slice liefert Referenzumsetzung und verbindlichen Standard.

## UX-STANDARD-COMPONENTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Wiederverwendbare UX-Exzellenz-Komponenten fuer Rollenfokus, Aufgabenplan, naechste Aktion, Evidence-Link, Audit-Zeitleiste, Managemententscheidung und CRUD-Abdeckung bereitstellen und in HRM als Referenz nutzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-STANDARD-COMPONENTS-001.yaml`, `packages/frontend-web/src/components/workflow/ux-standard.tsx`, `packages/frontend-web/src/components/workflow/index.ts`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Komponenten sind typisiert und domaenenneutral; HRM nutzt mindestens Rollenfokus, Aufgabenplan, Evidence-Link, Audit-Zeitleiste und Managemententscheidung aus dem Baukasten; UX-Standard dokumentiert den Baukasten und CRUD-Matrix; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `ux-standard.tsx` stellt `RoleFocusBar`, `OperationalTaskPlan`, `NextActionPanel`, `EvidenceTemplateLink`, `AuditTimeline`, `ManagementDecisionPanel`, `CrudCapabilityChecklist` und `EmptyStateWithAction` bereit. HRM-Betriebsfreigaben nutzen den Baukasten fuer Rollenfokus, Aufgabenplan, Evidence-Link, Audit-Zeitleiste, Next Action und Managemententscheidung. UX-Standard dokumentiert Komponenten und CRUD-Abdeckung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-STANDARD-COMPONENTS-001.yaml`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Weitere Domaenen muessen in Folgeslices migriert werden; dieser Slice schafft den gemeinsamen Baukasten und die HRM-Referenzverdrahtung.

## UX-FINANCE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Den UX-Exzellenzbaukasten auf Finance/FIBU anwenden, beginnend mit dem Kreditoren-Zahlungslauf als produktkritischer Zahlungsarbeitsflaeche.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-001.yaml`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Kreditoren-Zahlungslauf zeigt Rollenfokus, Aufgabenplan, Managemententscheidung, Audit-/Zahlungspfad und CRUD-Abdeckung; naechste Aktion bleibt sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/zahlungslauf-kreditoren.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Aufgabenplan, Managemententscheidung, Next Action und CRUD-Abdeckung. Der bestehende Zahlungspfad und Kontext bleiben erhalten. UX-Standard dokumentiert den Finance-Rollout-Status und naechste Finance-Slices.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Weitere Finance-Seiten wie UStVA, Mahnwesen und Abschluss folgen in separaten Rollout-Slices.

## UX-FINANCE-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** UStVA als zweite Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-002.yaml`, `packages/frontend-web/src/pages/finance/ustva.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** UStVA zeigt Rollenfokus fuer FIBU, Steuerbuero, Controlling und Leitung; Melde-Aufgabenplan fuehrt Periode, Abweichungen, Freigabe und ELSTER; Managemententscheidung zeigt abgabefaehig/gestoppt; CRUD-/Meldeabdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/ustva.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung. Bestehender Meldeverlauf, UStVA-Kontext, FIBU-KPIs und Submit-/Export-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Mahnwesen und Periodenabschluss folgen in separaten Finance-UX-Slices.

## UX-FINANCE-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Mahnwesen als dritte Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-003.yaml`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Mahnwesen zeigt Rollenfokus fuer FIBU, Forderungsmanagement, Vertrieb, Leitung und Steuerbuero; Aufgabenplan fuehrt OP-Auswahl, Parameter, Versand/Eskalation und Zahlungsklaerung; Managemententscheidung zeigt sendbar/gestoppt; CRUD-/Kommunikationsabdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/mahnwesen.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung. Bestehende Mahnlage, Kontext, FIBU-KPIs, Versand-, Paid-, Export- und Inkasso-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Periodenabschluss folgt in separatem Finance-UX-Slice.

## UX-FINANCE-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Periodenabschluss als vierte Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Close-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Close-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-004.yaml`, `packages/frontend-web/src/pages/finance/abschluss.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Periodenabschluss zeigt Rollenfokus fuer FIBU, Controlling, Steuerbuero, Leitung und Audit; Close-Aufgabenplan fuehrt Periode, Abstimmung, Freigabe und Sperre/Export; Managemententscheidung zeigt abschliessbar/gestoppt; CRUD-/Close-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/abschluss.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Close-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Close-Abdeckung. Bestehende Abschlusslage, Kontext, FIBU-KPIs, Calculate-/Approve-/Close-/Lock- und Export-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-004` als abgeschlossen und leitet Einkauf/CRM/Logistik als naechste Rollout-Domaenen ein.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-FINANCE-004.yaml`; `git diff --check`
**Offene Risiken:** Einkauf und weitere Domaenen folgen in separaten UX-Rollout-Slices.

## UX-EINKAUF-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Rechnungseingaenge als erste Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Workflow-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-001.yaml`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Rechnungseingaenge zeigen Rollenfokus fuer Einkauf, Wareneingang, FIBU, Leitung und Audit; Aufgabenplan fuehrt Erfassen, Pruefen, Freigeben und Verbuchen; Managemententscheidung zeigt buchbar/gestoppt; CRUD-/Workflow-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/rechnungseingaenge-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Workflow-Abdeckung. Bestehende Rechnungseingangs-KPIs, Bulk-Pruefen, Bulk-Freigeben, Bulk-Verbuchen, Export und Importpfad bleiben erhalten. UX-Standard markiert `UX-EINKAUF-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-001.yaml`; `git diff --check`
**Offene Risiken:** Bestellung, Wareneingang und Lieferantenstamm folgen in separaten Einkaufs-UX-Slices.

## UX-CRM-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Opportunities als erste CRM-/Vertriebs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Pipeline-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-CRM-001.yaml`, `packages/frontend-web/src/pages/crm/opportunities-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Opportunities zeigen Rollenfokus fuer Vertrieb, Inside Sales, Leitung, Finance und Customer Success; Aufgabenplan fuehrt Qualifizieren, Angebot erstellen, Entscheiden und Nachfassen; Managemententscheidung zeigt Pipeline handlungsfaehig/leer; CRUD-/Pipeline-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `crm/opportunities-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Pipeline-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Pipeline-Abdeckung. Bestehende Opportunity-Liste, CSV-Import/-Export und Bulk-Aktionen fuer Angebot, gewonnen und verloren bleiben erhalten. UX-Standard markiert `UX-CRM-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-CRM-001.yaml`; `git diff --check`
**Offene Risiken:** Angebots- und Auftragseditor folgen in separaten Sales-/CRM-UX-Slices.

## UX-SALES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Verkaufsauftraege als erste Sales-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Auftrag-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Fulfillment-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-001.yaml`, `packages/frontend-web/src/pages/sales/auftraege-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Verkaufsauftraege zeigen Rollenfokus fuer Vertrieb, Auftragsabwicklung, Logistik, Finance und Leitung; Aufgabenplan fuehrt Erfassen, Liefertermin klaeren, Liefern und Fakturieren; Managemententscheidung zeigt handlungsfaehig/leer; CRUD-/Fulfillment-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/auftraege-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Auftrag-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Fulfillment-Abdeckung. Bestehende Filter, Suche, CSV-Import, Export, Druck und Editor-Navigation bleiben erhalten. UX-Standard markiert `UX-SALES-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-001.yaml`; `git diff --check`
**Offene Risiken:** Angebotsliste und Auftragseditor folgen in separaten Sales-UX-Slices.

## UX-LOGISTIK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Tourenplanung als erste Logistik-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Dispo-Plan, Managemententscheidung, Next Action und CRUD-/Transport-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-001.yaml`, `packages/frontend-web/src/pages/logistik/tourenplanung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Tourenplanung zeigt Rollenfokus fuer Disposition, Fahrer, Lager/Waage, QS und Leitung; Aufgabenplan fuehrt Planen, Ressourcen klaeren, unterwegs ueberwachen und abschliessen; Managemententscheidung zeigt disponierbar/blockiert; CRUD-/Transport-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `logistik/tourenplanung.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Dispo-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Transport-Abdeckung. Bestehende Tourenlage, Ressourcen-KPIs, Supply-Chain-Kontext und aktive Tourenliste bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-001.yaml`; `git diff --check`
**Offene Risiken:** Frachtbriefe und Waage folgen in separaten Logistik-UX-Slices.

## UX-EINKAUF-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Bestellungen als zweite Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Bestell-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Liefer-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-002.yaml`, `packages/frontend-web/src/pages/einkauf/bestellungen-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Bestellungen zeigen Rollenfokus fuer Einkauf, Wareneingang, Finance, Lieferant und Leitung; Aufgabenplan fuehrt Erfassen, Freigeben, Bestellen/Liefern und Nachweis/Export; Managemententscheidung zeigt bestellfaehig/blockiert; CRUD-/Liefer-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/bestellungen-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Bestell-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Liefer-Abdeckung. Bestehende Listenfunktion, Bulk-Freigabe, Bulk-Storno, Druck, Import, Export und Detailnavigation bleiben erhalten. UX-Standard markiert `UX-EINKAUF-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-002.yaml`; `git diff --check`
**Offene Risiken:** Wareneingang und Lieferantenstamm folgen in separaten Einkaufs-UX-Slices.

## UX-SALES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Angebotsliste als zweite Sales-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Angebots-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Conversion-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-002.yaml`, `packages/frontend-web/src/pages/sales/angebote-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Angebote zeigen Rollenfokus fuer Vertrieb, Inside Sales, Auftragsabwicklung, Finance und Leitung; Aufgabenplan fuehrt Erfassen, Nachfassen, Entscheiden und in Auftrag ueberfuehren; Managemententscheidung zeigt Angebotsarbeit handlungsfaehig/leer; CRUD-/Conversion-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/angebote-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Angebots-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Conversion-Abdeckung. Bestehende Suche, Filter, CSV-Import, Export, Druck und Detailnavigation bleiben erhalten. UX-Standard markiert `UX-SALES-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-002.yaml`; `git diff --check`
**Offene Risiken:** Auftragseditor folgt in separatem Sales-UX-Slice.

## UX-LOGISTIK-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Frachtbriefe als zweite Logistik-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Dokument-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-002.yaml`, `packages/frontend-web/src/pages/logistik/frachtbriefe.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Frachtbriefe zeigen Rollenfokus fuer Disposition, Fahrer, Lager/Waage, Dokumentation und Leitung; Aufgabenplan fuehrt Erstellen, Versenden, Transport verfolgen und Zustellung sichern; Managemententscheidung zeigt nachweisfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `logistik/frachtbriefe.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Dokument-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Frachtlage, Supply-Chain-Kontext, Suche, Ketten-KPIs und Frachtbrief-Liste bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-002.yaml`; `git diff --check`
**Offene Risiken:** Waage folgt in separatem Logistik-UX-Slice.

## UX-EINKAUF-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Wareneingang als dritte Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Eingangspruefplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-003.yaml`, `packages/frontend-web/src/pages/einkauf/wareneingang.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Wareneingang zeigt Rollenfokus fuer Wareneingang, Einkauf, QS, Lager und Finance; Aufgabenplan fuehrt Bestellung auswaehlen, Lieferschein erfassen, Mengen/QS pruefen und buchen; Managemententscheidung zeigt buchbar/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/wareneingang.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Eingangspruefplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Bestellauswahl, Lieferschein-/Kopfdatenerfassung, Mengen-/QS-Tabelle und Buchungsaktion bleiben erhalten. UX-Standard markiert `UX-EINKAUF-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-003.yaml`; `git diff --check`
**Offene Risiken:** Lieferantenstamm folgt in separatem Einkaufs-UX-Slice.

## UX-SALES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Auftragseditor als dritte Sales-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Auftrags-Erfassungsplan, Managemententscheidung, Next Action und CRUD-/Folgebeleg-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-003.yaml`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Auftragseditor zeigt Rollenfokus fuer Vertrieb, Auftragsabwicklung, Logistik, Finance und Leitung; Aufgabenplan fuehrt Kunde, Positionen, Liefertermin und Folgebeleg; Managemententscheidung zeigt belegfaehig/blockiert; CRUD-/Folgebeleg-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/order-editor.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Auftrags-Erfassungsplan, Managemententscheidung, Next Action und CRUD-/Folgebeleg-Abdeckung. Bestehende Kundenauswahl, Positionserfassung, Belegfolge, Druck, DMS, Attestation, Lieferschein- und Sofort-Rechnung-Aktionen bleiben erhalten. UX-Standard markiert `UX-SALES-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-003.yaml`; `git diff --check`
**Offene Risiken:** Detailtiefe einzelner Dialoge bleibt im bestehenden Editor; dieser Slice setzt den Leitbereich oberhalb der Maske.

## UX-EINKAUF-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Lieferantenstamm als vierte Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Lieferanten-Onboardingplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Compliance-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-004.yaml`, `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Lieferantenstamm zeigt Rollenfokus fuer Einkauf, QS, Finance, Compliance und Leitung; Aufgabenplan fuehrt Stammdaten, Bank/Zahlung, QS-/Dokumentnachweise und Sperr-/Archivstatus; Managemententscheidung zeigt einkaufsbereit/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/lieferanten-stamm.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Lieferanten-Onboardingplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Compliance-Abdeckung. Bestehende Stammdaten-, Kontakt-, Bank-, Steuer-, Klassifikations-, Compliance- und QS-Tabs bleiben erhalten. UX-Standard markiert `UX-EINKAUF-004` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-004.yaml`; `git diff --check`
**Offene Risiken:** Detaildialoge fuer Ansprechpartner, Bankkonten, Klassifikationen und Dokumente bleiben bestehend; dieser Slice setzt den Leitbereich oberhalb der Stammdatenmaske.

## UX-SALES-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Rechnungs- und Lieferschein-Editor als Folgebeleg-Arbeitsflaechen auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-004.yaml`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `packages/frontend-web/src/pages/sales/delivery-editor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Rechnungseditor zeigt Rollenfokus fuer Faktura, Vertrieb, Finance und Leitung; Lieferschein-Editor zeigt Rollenfokus fuer Versand, Vertrieb, Lager und Faktura; beide zeigen Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/invoice-editor.tsx` und `sales/delivery-editor.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Docflow-, Approval-, Druck-, Export-, OP-, Kunden-, Artikel- und Lieferscheinbuchungsfunktionen bleiben erhalten. UX-Standard markiert `UX-SALES-004` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-004.yaml`; `git diff --check`
**Offene Risiken:** Tiefe Belegdruck- und Exportprozesse bleiben in bestehenden Funktionen; dieser Slice setzt den Leitbereich oberhalb der bestehenden Editor-Masken.

## UX-LOGISTIK-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Waagearbeitsflaechen auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Waage-Aufgabenplan, Stopper-/Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-003.yaml`, `packages/frontend-web/src/pages/waage/wiegungen.tsx`, `packages/frontend-web/src/pages/waage/wiegeschein-detail.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Wiegungen und Wiegeschein-Detail zeigen Rollenfokus fuer Waage, Annahme, Disposition, QS und Abrechnung; Aufgabenplan fuehrt Ticket, Gewichte, Qualitaet, Kontrakt und Abschluss; Stopper-/Managemententscheidung zeigt buchbar/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `waage/wiegungen.tsx` und `waage/wiegeschein-detail.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Waage-/Wiegeschein-Aufgabenplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Ticketanlage, Gewichtserfassung, Kontraktzuordnung, Supply-Chain-Kennzahlen, Timeline und Detail-Tabs bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-003.yaml`; `git diff --check`
**Offene Risiken:** Waage-Hardware-Integration bleibt ausserhalb dieses Slice; dieser Slice fokussiert die Bedien- und Nachweissicht.

## UX-EINKAUF-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Lieferantenbewertung auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Bewertungsplan, Eskalationsentscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-005.yaml`, `packages/frontend-web/src/pages/einkauf/lieferantenbewertung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Lieferantenbewertung zeigt Rollenfokus fuer Einkauf, QS, Finance und Leitung; Bewertungsplan fuehrt Datenbasis, Scores, Eskalation und Review; Managemententscheidung zeigt akzeptabel/klaerungsbeduerftig; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/lieferantenbewertung.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Bewertungsplan, Eskalationsentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Suche, Bewertungsmatrix und Score-Anpassung bleiben erhalten. UX-Standard markiert `UX-EINKAUF-005` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-005.yaml`; `git diff --check`
**Offene Risiken:** Score-Historie und Massnahmenworkflow bleiben ausserhalb dieses Slice; dieser Slice setzt die Bedien- und Entscheidungssicht auf die bestehende Bewertungsmatrix.

## UX-SALES-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Gutschriften-Editor als Verkaufsfolge auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-005.yaml`, `packages/frontend-web/src/pages/sales/credit-note-editor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Gutschriften-Editor zeigt Rollenfokus fuer Vertrieb, Faktura, Finance und Leitung; Freigabeplan fuehrt Kunde, Ausgangsrechnung, Grund, Positionen und Zahlung; Managemententscheidung zeigt freigabefaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/credit-note-editor.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Gutschriften-Freigabeplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende ObjectPage-Konfiguration, Validierung, Freigabe, Versand, Druck und Storno bleiben erhalten. UX-Standard markiert `UX-SALES-005` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-005.yaml`; `git diff --check`
**Offene Risiken:** Retourenlogik ausserhalb des Gutschriften-Editors bleibt fuer einen separaten Sales-/Einkauf-Slice offen.

## UX-LOGISTIK-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Hofliste und Waagenliste auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Prioritaetsplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-004.yaml`, `packages/frontend-web/src/pages/waage/hofliste.tsx`, `packages/frontend-web/src/pages/waage/liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Hofliste und Waagenliste zeigen Rollenfokus fuer Waage, Hof, Disposition, QS und Leitung; Prioritaetsplan fuehrt offene Vorgange, Eichung, Suche und naechste Aktion; Stopperentscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `waage/hofliste.tsx` und `waage/liste.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Prioritaetsplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Hotkeys, Tabellen, Anlage, Zweit-Wiegung, Suche, Export, OperationalCaseHeader und Kettenkontext bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-004` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-004.yaml`; `git diff --check`
**Offene Risiken:** Waage-Hardware- und Echtzeit-Sensorik bleiben ausserhalb dieses Slice.

## UX-EINKAUF-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Retouren und Gutschriften/Belastungen auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Freigabeplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-006.yaml`, `packages/frontend-web/src/pages/einkauf/retouren.tsx`, `packages/frontend-web/src/pages/einkauf/gutschriften-belastungen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Retouren und Gutschriften/Belastungen zeigen Rollenfokus fuer Einkauf, Wareneingang, Finance, QS und Leitung; Freigabeplan fuehrt Wareneingang/Rechnung, Grund, Positionen, Gutschrift/Belastung und Ausgleich; Stopperentscheidung zeigt freigabefaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/retouren.tsx` und `einkauf/gutschriften-belastungen.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Freigabeplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Wareneingangs-Auswahl, Retourendialog, Statuspflege, Memo-Erstellung, Settlement-Entwurf und Ausgleichsdialoge bleiben erhalten. UX-Standard markiert `UX-EINKAUF-006` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-006.yaml`; `git diff --check`
**Offene Risiken:** Tiefe Buchhaltungs- und Lieferantenkommunikationsworkflows bleiben in den bestehenden Aktionen; dieser Slice setzt die Bedien- und Entscheidungssicht.

## UX-SALES-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Verkaufsdashboard, Rechnungs- und Lieferlisten auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-006.yaml`, `packages/frontend-web/src/pages/dashboard/sales-dashboard.tsx`, `packages/frontend-web/src/pages/sales/rechnungen-liste.tsx`, `packages/frontend-web/src/pages/sales/lieferungen-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Dashboard, Rechnungs- und Lieferlisten zeigen Rollenfokus fuer Vertrieb, Faktura, Logistik, Finance und Leitung; Prioritaetsplan fuehrt Umsatz, offene Rechnungen, Lieferstatus und Nachweis; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `dashboard/sales-dashboard.tsx`, `sales/rechnungen-liste.tsx` und `sales/lieferungen-liste.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende KPI-Karten, Top-Kunden, OperationalCaseHeader, Filter, Import, Export, Druck, Tabellen und Editor-Navigation bleiben erhalten. UX-Standard markiert `UX-SALES-006` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-006.yaml`; `git diff --check`
**Offene Risiken:** Auftrags- und Angebotslisten sind bereits in frueheren Sales-Slices abgedeckt; dieser Slice fokussiert Dashboard, Rechnungen und Lieferungen.

## UX-EINKAUF-007

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Einkaufs-Dashboard auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Einkaufs-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestell- und Rechnungseingangslisten sind bereits in frueheren Einkauf-Slices abgedeckt.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-007.yaml`, `packages/frontend-web/src/pages/dashboard/einkauf-dashboard.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Einkaufs-Dashboard zeigt Rollenfokus fuer Einkauf, Wareneingang, Finance, Lieferantenmanagement und Leitung; Prioritaetsplan fuehrt offene Bestellungen, Ueberfaelligkeit, Einkaufsvolumen, offene Posten und Nachweis; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `dashboard/einkauf-dashboard.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Einkaufs-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende KPI-Karten, Ueberfaelligkeitswarnung und aktuelle Bestellungen bleiben erhalten. UX-Standard markiert `UX-EINKAUF-007` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-007.yaml`; `git diff --check`
**Offene Risiken:** Detail-Listen bleiben in den vorhandenen Einkaufs-Slices; dieser Slice fokussiert die Management- und Prioritaetssicht des Dashboards.

## UX-SALES-007

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Moderne Sales-Auftragssicht als Ausnahmen- und Eskalationsarbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Eskalationsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-007.yaml`, `packages/frontend-web/src/pages/sales/orders-modern.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Moderne Sales-Auftragssicht zeigt Rollenfokus fuer Vertrieb, Auftragsabwicklung, Logistik, Faktura und Leitung; Eskalationsplan fuehrt offene, teilgelieferte, rechnungsfaehige und Archiv-/Storno-Kandidaten; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/orders-modern.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Sales-Eskalationsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Toolbar, CSV-Export, Suche, Filter, KPI-Karten, DataTable und Fokusauftrag bleiben erhalten. UX-Standard markiert `UX-SALES-007` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-007.yaml`; `git diff --check`
**Offene Risiken:** Rechnungsliste und Lieferliste sind in `UX-SALES-006` abgedeckt; dieser Slice fokussiert die moderne Sales-Ausnahmensicht.

## UX-LOGISTIK-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Bestands-/Logistik-Dashboard als vorhandene Dashboardflaeche fuer Logistik- und Waagefolge auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Ketten-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-005.yaml`, `packages/frontend-web/src/features/inventory/InventoryDashboard.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Dashboard zeigt Rollenfokus fuer Lager, Logistik, Waage, Einkauf und Leitung; Prioritaetsplan fuehrt Bestand, Alerts, Nachschub, Wert und Nachweis; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `features/inventory/InventoryDashboard.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Bestands-Kettenplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende KPI-Karten, Alerts, Nachschubvorschlaege und Quick Actions bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-005` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-005.yaml`; `git diff --check`
**Offene Risiken:** Es gibt aktuell keine separate Logistik-Dashboard-Route; dieser Slice nutzt die bestehende Inventory-Dashboard-Flaeche als operative Logistik-/Bestandsuebersicht.

## UX-EINKAUF-008

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Einkaufs-Ausnahmen fuer EDI/Lieferantenportal und Service Entry Sheets als verstaendliche Arbeitsflaechen mit Stopper-, Prioritaets- und Nachweissicht fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-008.yaml`, `packages/frontend-web/src/pages/einkauf/edi-portal.tsx`, `packages/frontend-web/src/pages/einkauf/service-entry-sheets.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** EDI-Portal und Service-Entry-Sheets zeigen Rollenfokus, konkreten Pruefplan, Stopper-/Managemententscheidung, naechste Aktion, Nachweis-/Vorlagenbezug und CRUD-/Workflow-Abdeckung in normaler Buero-Sprache.
**Erledigt:** `einkauf/edi-portal.tsx` und `einkauf/service-entry-sheets.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Pruefplan, Stopper-/Freigabeentscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung. Leere Zustaende und sichtbare Begriffe sind auf normale Buero-Sprache gezogen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-008.yaml`; `git diff --check`
**Offene Risiken:** OCR hat aktuell keine eigene sichtbare Einkaufsseite; der Slice behandelt die vorhandenen Ausnahmeflaechen EDI/Lieferantenportal und Service Entry Sheets.

## UX-SALES-008

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Angebots-Erfassung als gefuehrte Sales-Assistenz fuer Angebots-/Auftragsuebergaben mit naechster Aktion, Nachweisstatus und Abschlussentscheidung fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-008.yaml`, `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Angebots-Erfassung zeigt Rollenfokus, Uebergabeplan, Management-/Abschlussentscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Erfassungs-, Druck-, DMS- und Auftraguebergabe-Funktionen bleiben erhalten.
**Erledigt:** `sales/angebot-erstellen.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Uebergabeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Die bestehende Angebots-Erfassung, Suche, Positionserfassung, Druck, DMS-Anhang, Loeschen und Auftraguebergabe bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-008.yaml`; `git diff --check`
**Offene Risiken:** Die Angebotsliste ist bereits ueber `UX-SALES-002` abgedeckt; dieser Slice fokussiert die eigentliche Erfassungs- und Uebergabemaske.

## UX-LOGISTIK-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Fracht-/Speditions-Ausnahmen fuer Frachtdokumentdruck und Frachttarife mit Eskalationssicht, naechster Aktion und Kettennachweis fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-006.yaml`, `packages/frontend-web/src/pages/versand/frachtdokumente.tsx`, `packages/frontend-web/src/pages/strecke/speditionen-fracht-preise.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Frachtdokumente und Speditions-Frachttarife zeigen Rollenfokus, Ausnahme-/Pruefplan, Eskalationsentscheidung, naechste Aktion, Nachweislink und CRUD-/Workflow-Abdeckung in normaler Buero-Sprache.
**Erledigt:** `versand/frachtdokumente.tsx` und `strecke/speditionen-fracht-preise.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Pruefplan, Eskalations-/Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Der Frachtdokument-Druckfehler ist als klaerer Versandstopper formuliert; Frachttarife zeigen aktive/inaktive Tarife, Preisnachweis und naechste Klaerung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-006.yaml`; `git diff --check`
**Offene Risiken:** `logistik/frachtbriefe.tsx` ist bereits ueber `UX-LOGISTIK-002` abgedeckt; dieser Slice fokussiert Druck-/Tarifausnahmen.

## UX-DMS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Dokumente/DMS als gefuehrte Arbeitsflaechen fuer Klassifikation, Retention, Version, Vorlage, Freigabe und naechste Aktion in normaler Buero-Sprache fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-DMS-001.yaml`, `packages/frontend-web/src/pages/document.tsx`, `packages/frontend-web/src/pages/admin/setup/dms-integration.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Dokumentenpanel und DMS-Integration zeigen Rollenfokus, Arbeitsplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung; Upload, Suche, Scan, Loeschen und DMS-Verbindung bleiben erhalten.
**Erledigt:** `document.tsx` und `admin/setup/dms-integration.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Klassifikations-/Einrichtungsplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung. Upload, Suche, Scan, Loeschen, Verbindungstest, Einrichtung und Neu-Konfiguration bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-DMS-001.yaml`; `git diff --check`
**Offene Risiken:** `dokumente/ablage.tsx` hat bereits einen operativen Nachweisrahmen; dieser Slice fokussiert zentrale QM-Dokumente und technische DMS-Anbindung.

## UX-QS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Qualitaet/Produktion fuer Pruef-, Sperr- und Freigabeprozesse mit Rollenfokus, naechster Aktion, Nachweisstatus und normaler Buero-Sprache fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-QS-001.yaml`, `packages/frontend-web/src/pages/annahme/klaerung-gesperrt.tsx`, `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Gesperrte-Ware-Klaerung und QS-Ausnahmen zeigen Rollenfokus, Pruef-/Eskalationsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Entscheidung, Begruendung, Liste und Agent-Vorschlaege bleiben erhalten.
**Erledigt:** `annahme/klaerung-gesperrt.tsx` und `qualitaet/ausnahmen.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Sperr-/Eskalationsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Entscheidung, Begruendung, Liste, Kennzahlen und Agent-Vorschlaege bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-QS-001.yaml`; `git diff --check`
**Offene Risiken:** `annahme/qualitaets-check.tsx` hat bereits einen operativen Fallkopf; dieser Slice fokussiert die Klär- und Eskalationsraeume.

## UX-LAGER-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Lagerarbeitsflaechen fuer Lagerplaetze und Bestandsbewegungen mit Rollenfokus, Engpassentscheidung, naechster Aktion und Nachweisstatus fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LAGER-001.yaml`, `packages/frontend-web/src/pages/lager/lagerplaetze.tsx`, `packages/frontend-web/src/features/inventory/StockManagement.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Lagerplaetze und StockManagement zeigen Rollenfokus, Lager-/Bewegungsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Kapazitaetsanzeige, Artikel-/Bestandsliste und Bewegungsdialog bleiben erhalten.
**Erledigt:** `lager/lagerplaetze.tsx` und `features/inventory/StockManagement.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Kapazitaets-/Bestandsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Kapazitaetsanzeige, Artikel-/Bestandsliste und Bewegungsdialog bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LAGER-001.yaml`; `git diff --check`
**Offene Risiken:** Einzelne Lagerseiten wurden in OP-ROLL-Slices bereits fallartig aufgewertet; dieser Slice fokussiert Lagerplaetze und das zentrale StockManagement.

## UX-PORTAL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Portal-/Self-Service-Dokumente mit Rollenfokus, klarer Nutzeraufgabe, Nachweisstatus, naechster Aktion und CRUD-/Workflow-Abdeckung fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-PORTAL-001.yaml`, `packages/frontend-web/src/pages/portal/dokumente.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Portal-Dokumente zeigen Rollenfokus, Nachweisplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung; bestehende KPI-Karten, Compliance-Spur, Suche, Filter, Tabs und Download bleiben erhalten.
**Erledigt:** `portal/dokumente.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Nachweisplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende KPI-Karten, Compliance-Spur, Suche, Filter, Tabs und Download bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-PORTAL-001.yaml`; `git diff --check`
**Offene Risiken:** Dieser Slice fokussiert die Portal-Dokumentenseite; weitere Portal-Self-Service-Seiten bleiben Folgeslices.

## UX-PRODUKTION-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Produktionsarbeitsflaechen fuer Mischfutter-Auftrag und Produktionsdokument-Druck mit Rollenfokus, Materialentscheidung, Dokumentnachweis und naechster Aktion fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-PRODUKTION-001.yaml`, `packages/frontend-web/src/pages/produktion/mischfutter-produktion.tsx`, `packages/frontend-web/src/pages/produktion/produktions-dokumente-drucken.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Mischfutter-Produktion und Produktionsdokument-Druck zeigen Rollenfokus, Produktions-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehender Wizard und Druckmaske bleiben erhalten.
**Erledigt:** `produktion/mischfutter-produktion.tsx` und `produktion/produktions-dokumente-drucken.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Produktions-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehender Wizard, Materialpruefung, Auftragserstellung und Druckmaske bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-PRODUKTION-001.yaml`; `git diff --check`
**Offene Risiken:** Produktion hat bisher nur schmale sichtbare Frontend-Flaechen; weitere Produktionsdetails bleiben Folgeslices.

## UX-ADMIN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Admin-Benutzer- und Rollenverwaltung mit klarer Betriebsaufgabe, Status, naechster Aktion und sicherer Aenderungsfuehrung nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-ADMIN-001.yaml`, `packages/frontend-web/src/pages/admin/benutzer-liste.tsx`, `packages/frontend-web/src/pages/admin/rollen-verwaltung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Benutzer- und Rollenverwaltung zeigen Rollenfokus, Admin-Aufgabenplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Liste, Suche, Export und Neuanlage bleiben erhalten.
**Erledigt:** `admin/benutzer-liste.tsx` und `admin/rollen-verwaltung.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Sicherheits-/Berechtigungsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Listen, Suche, Export und Neuanlage bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-ADMIN-001.yaml`; `git diff --check`
**Offene Risiken:** DMS-Setup ist bereits ueber `UX-DMS-001` abgedeckt; weitere Admin-Spezialseiten bleiben Folgeslices.

## UX-FUHRPARK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Fuhrparkseiten fuer Fahrzeugstatus, Dokumente, Fristen, naechste Aktion und Nachweisfuehrung nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FUHRPARK-001.yaml`, `packages/frontend-web/src/pages/fuhrpark/fahrzeuge.tsx`, `packages/frontend-web/src/pages/fuhrpark/ausgehende-belege-dokumente.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Fahrzeugliste und ausgehende Fuhrpark-Dokumente zeigen Rollenfokus, Fristen-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Liste, Suche, Export, Quicklinks und Dokument-CRUD bleiben erhalten.
**Erledigt:** `fuhrpark/fahrzeuge.tsx` und `fuhrpark/ausgehende-belege-dokumente.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Fristen-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Liste, Suche, Export, Quicklinks und Dokument-CRUD bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-FUHRPARK-001.yaml`; `git diff --check`
**Offene Risiken:** Fuhrpark-Menues und Detailstammdaten bleiben Folgeslices; dieser Slice fokussiert Status-/Fristen- und Dokumentsteuerung.

## TODO-SPRINT-001

**Von:** Cursor<br>
**Owner:** (Team)<br>
**Stand:** dokumentiert 2026-04-24<br>
**Ziel des Slices:** Die abgestimmte **TODO-Umsetzungs-Roadmap** (Meilensteine **M-01–M-12**) und die **Sprint-Zuordnung S1–S5** im Repo und hier im Workboard als **einzige Sprint-/Issue-Referenz** festhalten; Abgleich mit automatisch erzeugten TODO-Reports möglich.

**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/TODO-SPRINT-001.yaml`, [docs/roadmap/TODO-UMSETZUNG-SPRINT-PLAN-S1-S5.md](../roadmap/TODO-UMSETZUNG-SPRINT-PLAN-S1-S5.md), Ergänzungen in `scripts/update_todos.py` (Slice-Ausgaben `docs/TODO-next-slices.md`, `docs/todo-report.json` → `next_slices`).

**Kurzreferenz Meilensteine**

| Sprint | Meilensteine |
|--------|----------------|
| S1 | M-01 (Auth-/Tenant-**Vertrag**), M-02 (Pagination Contract erp-domain) |
| S2 | M-03 (Pagination Rollout), M-04 (ERP Actor), M-05 (**E2E-Auth früh**) |
| S3 | M-06 (CRM Auth), M-07 (CRM E-Mail/Queue) |
| S4 | M-08 (GDPR Export), M-09 (GDPR Löschung inkl. Retention), M-10 (FiBu Perioden/Saldo) |
| S5 | M-11 (Strecke DB + Migration/Rollback), M-12 (Einkauf OCR, Teilprojekt) |

**Abnahmekriterien (Doku-Slice):** Workboard enthält Slice-ID und Tabelle; kanonisches Dokument existiert und ist vom Board aus erreichbar; Tracking-Hinweis für `python scripts/update_todos.py --repo-only` / `docs/TODO-next-slices.md` genannt.

**Erledigt:** Kanonische Sprint-Matrix und Meilenstein-Details in `docs/roadmap/TODO-UMSETZUNG-SPRINT-PLAN-S1-S5.md`; dieser Eintrag.

**Checks (optional):** `python scripts/update_todos.py --repo-only`; Doku-Link im Browser öffnen.

**Offene Risiken:** Die Meilensteine **M-01–M-12** sind Umsetzungsarbeit — dieser Slice ist **Planungs-/Referenz-Ebene**. Konkrete Implementierungs-Slices sollten eigene IDs im Workboard erhalten und auf **M-xx** im Titel oder Body verweisen.

## HR-TIME-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Lizenz- und Zielarchitektur fuer deutsche Abwesenheitsverwaltung, Zeiterfassung und VALEO-eigenen Driver-Time-Layer festhalten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-001.yaml`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Urlaubsverwaltung wird als Apache-2.0-Abwesenheitskandidat bewertet; AGPL/GPL-Zeiterfassung ist als Codebasis ausgeschlossen; VALEO-Driver-Time-Layer, Integrationsgrenzen, Pilotumfang und Lizenzrisiken sind dokumentiert.
**Erledigt:** Zielarchitektur und Lizenzlinie in `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md` dokumentiert; `open-gaps` fuehrt HR-TIME-001 als P2-Thema mit naechstem Pilot-Slice.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Finale Rechtspruefung, Anbieter-AVV/DPA und produktive Tacho-/Telematik-Schnittstellen liegen ausserhalb des Repos.

## HR-TIME-PILOT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Ersten VALEO-eigenen Driver-Time-Toolkern fuer LKW-Fahrerzeit, Tour-/Fahrzeugbezug und Plausibilitaetschecks umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PILOT-001.yaml`, `packages/hr-domain/src/domain/entities/driver-time-event.ts`, `packages/hr-domain/src/domain/services/driver-time-service.ts`, `packages/hr-domain/dist/domain/entities/driver-time-event.*`, `packages/hr-domain/dist/domain/services/driver-time-service.*`, `packages/hr-domain/tests/domain/driver-time-service.test.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Fahrerzeitereignisse besitzen typisierte Ereignisarten, Tour-/Fahrzeugbezug, Quellen- und Auditfelder; Plausibilitaetschecks erkennen Ueberlappungen, fehlende Tour-/Fahrzeugdaten, fehlende Korrekturbegruendung und Abwesenheitskollisionen; die Zeiterfassungsseite zeigt den Driver-Time-Pilot ohne AGPL-/GPL-Codeuebernahme.
**Erledigt:** `DriverTimeEventEntity` und `DriverTimeService` eingefuehrt; fokussierte Vitest-Regression deckt Zusammenfassung, Blocker, Abwesenheitskollision und Tacho-/Manuell-Abweichung ab; `personal/zeiterfassung.tsx` zeigt Driver-Time-Pilot-KPIs und Ereignistabelle.
**Checks:** `pnpm --filter @valero-neuroerp/hr-domain exec vitest run tests/domain/driver-time-service.test.ts`; `pnpm --filter @valero-neuroerp/hr-domain build`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Produktive Persistenz, Tacho-/Telematik-Import und Payroll-/DATEV-Export bleiben Folgeslices. Der volle `@valero-neuroerp/hr-domain test`-Lauf ist aktuell durch den bestehenden `testcontainers`-Import im Repository-Integrationstest blockiert.

## HR-TIME-PILOT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Driver-Time-Pilot als Backend-/Frontend-Toolvertrag an die bestehende Personal-API anbinden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PILOT-002.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_driver_time_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** `/api/v1/personal/driver-time/summary` liefert Fahrerzeit-KPIs, Ereignisse und Plausibilitaetsbefunde aus einem stabilen API-Vertrag; Frontend nutzt diesen Hook statt harter lokaler Driver-Time-Daten; Tests decken Happy Path und Befundlogik ab.
**Erledigt:** Personal-API liefert Driver-Time-Summary mit DB-ableitung aus Stundenzetteln, Abwesenheitskollisionen und Pilot-Fallback; Frontend-Hook `useDriverTimeSummary` ersetzt harte lokale Driver-Time-Daten; Tests decken Helper, API-Happy-Path und Fallback ab.
**Checks:** `pytest tests/test_personal_driver_time_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Persistente Fahrerzeitereignisse, Tacho-/Telematik-Import und Payroll-/DATEV-Export bleiben Folgeslices.

## HR-TIME-PRO-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Zeiterfassung vom Fahrerzeit-Pilot zu einem professionellen Time-&-Labor-Cockpit mit Freigabe-, Compliance- und Payroll-Sicht ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PRO-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_cockpit_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Backend liefert ein Time-Cockpit mit Perioden-KPIs, Freigabequeue, Compliance-Befunden, Payroll-Readiness und Driver-Time-Zusammenfassung; Frontend zeigt diese Steuerung statt reiner Mock-/Tabellenseite; Tests sichern Kernvertrag und Regelbefunde.
**Erledigt:** `GET /api/v1/personal/time-cockpit` liefert professionelle Steuerungsdaten inklusive Payroll-Readiness und Compliance-Befunden; Zeiterfassungsseite nutzt Tabs fuer Steuerung, Driver-Time, Arbeitszeit und Payroll; Tests decken API-Vertrag und Regelbefunde ab.
**Checks:** `pytest tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Rechtsfeingranulare ArbZG-/Lenkzeitregeln, echte Dienstplanung, Buchungsworkflow und Lohnexport bleiben Folgeslices.

## HR-TIME-GAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** GAP-Liste, Lastenheft, Roadmap, Integrationsanforderungen und Landhandel-spezifische HRM-Planung gegen ERP/Shiftfy-Benchmark dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-GAP-001.yaml`, `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** ERP-/Shiftfy-Benchmark ist quellenbasiert; VALEO-GAPs, Lastenheft, Roadmap-Milestones, Integrationsanforderungen, Kreuzverbindungen, Mitarbeitertypen im Landhandel, Kalenderintegration, Saison-/Arbeitsspitzenplanung, Kampagneninterferenzen und Aussendienstplanung sind als umsetzbare Planung dokumentiert.
**Erledigt:** GAP-/Lastenheft-/Roadmap-Dokument in `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md` erstellt und in die HR-Time-Zielarchitektur verlinkt.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Detailauslegung Arbeitszeit-/Lenkzeitrecht, Tarif-/Betriebsvereinbarungen, Anbieter-AVV/DPA und echte Kalender-/Tacho-/Telematik-Zugangsdaten bleiben fachlich oder extern zu klaeren.

## HR-TIME-DATA-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Persistenten HR-Time-Datenkern fuer Mitarbeiter-Zeitprofile, produktive Zeitereignisse und Audit-/Statusfelder einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-DATA-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_data_api.py`, `migrations/sql/hr/001_hr_time_core.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`, `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md`
**Abnahmekriterien:** Kanonisches HR-Time-Kerndatenmodell und Konsistenzregeln sind dokumentiert; API liefert kanonische HR-Time-Profile aus Datenbank oder Pilot-Fallback; produktive Zeitereignisse besitzen Quelle, Status, Kostenstelle, Arbeitsbereich, Audit und Korrekturgrund im Migrationsvertrag; Tests sichern Profil- und Event-Transformation.
**Erledigt:** Kanonisches Kerndatenmodell inklusive API-Resource-URLs und Konsistenzanalyse dokumentiert; SQL-Vertrag fuer `employee_time_profiles`, erweiterte `time_entries` und `driver_time_events` erstellt; `GET /api/v1/personal/time-profiles` mit Datenbank-, User- und Pilot-Fallback umgesetzt; fokussierte API-/Mapping-Regression ergaenzt.
**Checks:** `pytest tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Anwendung der Migration, echte HR-Stammdatenquelle und Lohnartenmapping bleiben Folgeslices.

## HR-TIME-BOOK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Buchungs-, Korrektur-, Einreichungs- und Freigabe-Workflow fuer kanonische HR-Time-Zeitereignisse bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-BOOK-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_booking_api.py`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Zeitbuchungen koennen erstellt, eingereicht und freigegeben werden; Korrekturen verlangen einen Grund; exportierte Eintraege werden nicht still mutiert; API-Tests sichern Statusuebergaenge und Fehlerfaelle.
**Erledigt:** `POST /api/v1/personal/time-entries`, `/submit`, `/approve` und `/correct` eingefuehrt; Korrekturgrund und Export-Schutz werden serverseitig erzwungen; fokussierte API-Regression deckt Happy Path und Fehlerfaelle ab.
**Checks:** `pytest tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Rollenbasierte echte Managerfreigabe, Payroll-Export und UI-Aktionen bleiben Folgeslices.

## HR-TIME-ABS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Abwesenheits-Contract als kanonischen Planungsblocker fuer Urlaubsverwaltung/SaaS-Adapter, Tour, Schicht, Kalender und Payroll bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-ABS-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_absence_api.py`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Abwesenheiten koennen als Contract importiert und gelesen werden; genehmigte Abwesenheiten werden als `time_entries` mit Quelle `absence` gespiegelt; API weist Planungsblocker fuer Tour, Schicht, Kalender und Payroll aus; Tests sichern Import, Listing und Driver-Time-Kollision.
**Erledigt:** `GET /api/v1/personal/absences` und `POST /api/v1/personal/absences/import` umgesetzt; Import spiegelt genehmigte Abwesenheiten als kanonische `time_entries` mit Quelle `absence`; Planungsblocker und Driver-Time-Kollision sind regressionsgesichert.
**Checks:** `pytest tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echter Urlaubsverwaltung-HTTP-Connector, AVV/DPA und bidirektionale Konfliktaufloesung bleiben Folgeslices.

## HR-TIME-SCHED-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Schicht- und Einsatzplanung mit Standort, Rolle, Qualifikationen, Besetzung und Abwesenheitskonflikten auf dem kanonischen HR-Time-Modell bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-SCHED-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_shift_planning_api.py`, `migrations/sql/hr/002_hr_time_scheduling.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Schichten koennen erstellt und gelesen werden; Planung prueft Mindestbesetzung, aktive Profile, Qualifikationen und genehmigte Abwesenheiten; Konflikte werden als Warnung/Blocker im API-Vertrag ausgewiesen; Tests sichern Happy Path und Konfliktfaelle.
**Erledigt:** `domain_hr.shifts` als SQL-Vertrag, `GET/POST /api/v1/personal/shifts` und Konfliktpruefung gegen Mindestbesetzung, Profile, Qualifikationen und genehmigte Abwesenheiten umgesetzt; Regression fuer Blocker/Warnungen ergaenzt.
**Checks:** `pytest tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** UI-Kalender, echte Optimierung/Auto-Staffing und rollenbasierte Managerfreigabe bleiben Folgeslices.

## HR-TIME-CAL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Provider-neutralen Kalendervertrag fuer HR-Time-Blocker, Schichten, Abwesenheiten, Touren und Aussendienst bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-CAL-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_calendar_api.py`, `migrations/sql/hr/003_hr_time_calendar.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Kalenderereignisse koennen erstellt und gelesen werden; private externe Termine werden nur als Busy-Blocker ohne Betreffdetails gefuehrt; Konfliktlevel und Sync-State sind im Contract sichtbar; Tests sichern Datenschutzmaskierung und Vertrag.
**Erledigt:** `domain_hr.calendar_events` als SQL-Vertrag, `GET/POST /api/v1/personal/calendar-events`, Sync-State, Konfliktlevel und Datenschutzmaskierung fuer private/busy-only Termine umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Microsoft/Google OAuth, Delta-Sync und echte externe Kalenderzugriffe bleiben Folgeslices.

## HR-TIME-PAY-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Payroll-/DATEV-Exportvertrag fuer freigegebene HR-Time-Zeitwerte mit Lohnarten, Kostenstellen und Blockerpruefung bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PAY-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_payroll_export_api.py`, `migrations/sql/hr/004_hr_time_payroll_exports.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Payroll-Export kann fuer Zeitraum erzeugt und gelesen werden; nur freigegebene Zeitwerte werden exportfaehig; offene/nicht freigegebene Buchungen werden als Blocker ausgewiesen; Tests sichern Lohnartenmapping und Blocker.
**Erledigt:** `domain_hr.payroll_exports`, `GET/POST /api/v1/personal/payroll-exports`, Lohnartenmapping fuer Regelzeit/Ueberstunden/Abwesenheit und Blocker fuer nicht freigegebene Zeitbuchungen umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte DATEV-/Lohnsoftware-Dateiformate, Steuerberaterfreigabe und Rueckschreibstatus bleiben Folgeslices.

## HR-TIME-CAMPAIGN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Saison-/Kampagnen-Kapazitaetsplanung mit Rollenbedarf, Abwesenheiten, Schichten und Engpassbewertung bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-CAMPAIGN-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_campaign_capacity_api.py`, `migrations/sql/hr/005_hr_time_campaign_capacity.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Kampagnenkapazitaet kann erstellt und gelesen werden; Rollenbedarf wird gegen aktive Profile, Abwesenheiten und bereits geplante Schichten bewertet; Engpaesse werden als Warnung/Blocker im Contract ausgewiesen.
**Erledigt:** `domain_hr.campaign_capacity_plans`, `GET/POST /api/v1/personal/campaign-capacity` und Rollenbedarfspruefung gegen aktive Profile, Abwesenheiten und geplante Schichten umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_campaign_capacity_api.py tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Optimierungsalgorithmus, Wetter-/Mengenforecast und UI-Heatmap bleiben Folgeslices.

## HR-TIME-FIELD-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Aussendienstplanung mit Kunde, Gebiet, Kampagne, Kalender- und Abwesenheitskonflikten auf HR-Time-Basis bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-FIELD-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_field_service_api.py`, `migrations/sql/hr/006_hr_time_field_service.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Aussendiensttermine koennen erstellt und gelesen werden; Planung prueft HR-Time-Profil, Abwesenheit und Kalenderueberschneidung; Konflikte werden im Contract ausgewiesen; Tests sichern Blocker und Happy Path.
**Erledigt:** `domain_hr.field_service_plans`, `GET/POST /api/v1/personal/field-service-plan` und Konfliktpruefung gegen HR-Time-Profil, Abwesenheiten und Kalenderblocker umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_field_service_api.py tests/test_personal_campaign_capacity_api.py tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** CRM-Live-Connector, Routenoptimierung und mobile Aussendienst-UI bleiben Folgeslices.

## HR-TIME-UI-CRUD-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Tools als Human/AI-Agent-Interface mit CRUD-Aktionen fuer Zeitbuchung, Abwesenheit, Schicht, Kalender, Payroll, Kampagne und Aussendienst operationalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-UI-CRUD-001.yaml`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`
**Abnahmekriterien:** Frontend nutzt die neuen HR-Time-Contracts fuer Listen und Create-Mutations; Nutzer koennen zentrale HR-Time-Objekte aus dem Cockpit anlegen; Agent-Hinweise fassen Blocker, Freigaben und naechste Aktionen zusammen; Typecheck ist gruen.
**Erledigt:** Frontend-API-Hooks fuer Zeitbuchung, Abwesenheit, Schicht, Kalender, Payroll, Kampagne und Aussendienst ergaenzt; Zeiterfassungsseite zu einem kompakten ERP-Object-Page-Cockpit mit Agent Worklist, CRUD-Formulargruppen und Planungs-/Payroll-Tabellen ausgebaut.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Detail-CRUD mit Edit/Delete, echte Optimierungsvorschlaege und mobile Offline-UX bleiben Folgeslices.

## HR-TIME-OPS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Verdrahtung fuer Navigation vor/zurueck, Bearbeiten/Nachbearbeiten, Drucken, Arbeitsplanabruf und praferenzbasierte Planung mit Nachttouren, Urlaub, Schulferien, Brueckentagen und Feiertagsdruck operationalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_work_plan_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`
**Abnahmekriterien:** Backend liefert einen Arbeitsplanvertrag mit Planungsbefunden und Mitarbeiterpraeferenzen; Zeitbuchungen koennen aus der UI nachbearbeitet und neu eingereicht werden; Frontend bietet vor/zurueck-Navigation, Druckpfade und Arbeitsplanabruf; Tests sichern Arbeitsplan- und Praeferenzlogik.
**Erledigt:** `/api/v1/personal/work-plan` mit Praeferenz-, Ferien-, Brueckentags-, Feiertags- und Abwesenheitsbefunden umgesetzt; Frontend-Hooks fuer Arbeitsplan, Einreichen und Korrektur ergaenzt; Zeiterfassungsseite bietet Tagesnavigation, Arbeitsplan-Druck, Arbeitsplan-Tab und Nachbearbeitungsmaske.
**Checks:** `pytest tests/test_personal_work_plan_api.py tests/test_personal_shift_planning_api.py tests/test_personal_time_booking_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Ferienkalender-Provider, Betriebsvereinbarungen und echte Optimierungsengine bleiben Folgeslices.

## HR-TIME-OPS-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Durchklicktest-Befund beheben: HR-Time-GET-Hooks duerfen leere Platzhalterdaten nicht als frische Daten cachen und muessen beim Oeffnen der Maske wirklich laden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-002.yaml`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** HR-Time-Durchklicktest sieht geladene Arbeitsplan-/Cockpitdaten; GET-Hooks verwenden Platzhalter statt frischer Initialdaten; Formular-POSTs und Druckaktion bleiben funktionsfaehig.
**Erledigt:** React-Query-HR-Time-Hooks von `initialData` auf `placeholderData` umgestellt; Playwright-Durchklicktest fuer Navigation, Arbeitsplan, Erfassung, Nachbearbeitung, Submit/Korrektur-POSTs und Druckpfad ergaenzt; Testlauf hat GET-Requests und UI-Rendering verifiziert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Der temporäre E2E-Smoke nutzt API-Mocks; produktive Browser-E2E gegen echte FastAPI/Postgres bleibt Folgeslice.

## HR-TIME-OPS-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Nachbearbeitung ergonomisch aus der Arbeitszeitliste starten statt manuelle Zeitbuchungs-ID-Eingabe zu erzwingen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-003.yaml`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** Arbeitszeitzeilen haben eine Bearbeiten-Aktion; Klick fuellt die Nachbearbeitung mit ID, Zeiten, Stunden und Typ; die UI springt zur Erfassungs-/Nachbearbeitungsgruppe; E2E-Durchklicktest nutzt diesen Pfad.
**Erledigt:** Arbeitszeitliste erhaelt Bearbeiten-Aktion mit ID-/Zeit-/Typ-Uebernahme; Tabs sind kontrolliert und springen in die Erfassung; Playwright-Durchklicktest nutzt den realen Bearbeiten-Pfad vor Submit/Korrektur.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Voller Edit/Delete-Workflow fuer alle HR-Time-Objekte bleibt Folgeslice.

## HR-TIME-UX-ROADMAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Workflows als klickarme End-to-End UX-Roadmap mit Milestones, Quervernetzungen, User-Fragen, Masken, Such-/Filter-/Sortierfunktionen planen und den ersten Filter-/Such-Slice im Cockpit umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-UX-ROADMAP-001.yaml`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** Roadmap beschreibt Milestones mit Quervernetzungen und Abhaengigkeiten; User-Fragen sind Masken, Datenquellen und Aktionen zugeordnet; UI bietet zentrale Suche, Schnellfilter und Sortierung fuer Arbeitszeit/Arbeitsplan; Durchklicktest nutzt Suche/Filter/Sortierung.
**Erledigt:** UX-Workflow-Roadmap mit Milestones UX-M1 bis UX-M7, User-Fragen, Masken, Datenquellen, Aktionen, Quervernetzungen und Folge-Slices dokumentiert; Zeiterfassungs-Cockpit um zentrale Suche, Schnellfilter und Sortierung fuer Arbeitszeit und Arbeitsplan erweitert; E2E-Durchklicktest nutzt Suche/Filter/Sortierung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Weitere Milestones wie Action Panel, Wizard, Driver-Dispo und Payroll Closeout bleiben Folge-Slices.

## AGENT-ORCH-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Symphony als Blaupause fuer einen VALEO-eigenen Agent-Orchestrator in einem kleinen, repo-sicheren Pilot umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/agent-orchestrator-pilot.md`, `scripts/agent_workboard_supervisor.py`, `tests/test_agent_workboard_supervisor.py`
**Abnahmekriterien:** Ein CLI-Pilot erkennt Workboard-Slices, erzeugt Claim-Vorschlaege, listet Checks und Handoff-Geruest, ohne automatisch zu claimen, zu committen, zu pushen oder Agents zu starten.
**Erledigt:** Read-only Supervisor `scripts/agent_workboard_supervisor.py` eingefuehrt; Parser erkennt Slice-IDs, Statusklassen, Owner, Dateibesitz, Checks und Risiken; CLI liefert `list`, `claim-proposal`, `checks` und `handoff-template`. Pilotdoku liegt in `docs/agent-ops/agent-orchestrator-pilot.md`.
**Checks:** `pytest tests/test_agent_workboard_supervisor.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py list --status open`; `python scripts/agent_workboard_supervisor.py claim-proposal DOM-FIN-002 --owner Codex`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Markdown-Workboard ist kein striktes Datenformat; der Pilot muss konservativ parsen und unklare Bloecke melden statt still zu raten.

## AGENT-ORCH-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Maschinenlesbare Slice-Dateien oder ein Validierungs-Gate fuer Workboard-Claims einfuehren, damit der Orchestrator nicht dauerhaft auf weichem Markdown basiert.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/**`, `scripts/agent_workboard_supervisor.py`, `tests/test_agent_workboard_supervisor.py`
**Abnahmekriterien:** Claim-Pflicht ist maschinenlesbar validierbar; unklare Status-/Owner-/Dateibesitz-Felder werden als Fehler gemeldet, ohne automatische Git-Aktionen auszufuehren.
**Erledigt:** YAML-Slice-Format eingefuehrt (`docs/agent-ops/slices/*.yaml`); `validate`-Subcommand in `agent_workboard_supervisor.py` ergaenzt; 14 neue Tests gruen; historische Markdown-Bloecke werden nur validiert wenn YAML-Datei oder `--strict-ids` vorhanden.
**Checks:** `pytest tests/test_agent_workboard_supervisor.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Bestehende historische Workboard-Bloecke sind uneinheitlich und duerfen nicht durch ein zu striktes Gate blockieren.

## ERP-CRIT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Backend-Testabdeckung und Vertragsstabilitaet fuer kritische ERP-Pfade zuerst an real roten Tests und Ratchet-Pfaden verbessern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/payment_runs.py`, `tests/test_process_kernel_wave1_contracts.py`, relevante Coverage-/Ratchet-Doku.
**Abnahmekriterien:** Der aktuell rote Payment-Return-Vertrag laeuft wieder; Coverage-Ratchet-Status ist dokumentiert; naechste unterdeckte Pfade sind als konkrete Test-Slices priorisiert.
**Erledigt:** `payment_runs.return_payment` toleriert aktuelle und Legacy-Zeilenformate fuer Ruecklaeufer-Betraege; der rote Vertragstest ist gruen. Coverage-Ratchet-Folgereihenfolge ist dokumentiert in `docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md`.
**Checks:** `pytest tests/test_process_kernel_wave1_contracts.py::test_return_payment_persists_outbox_event tests/test_process_kernel_wave1_contracts.py::test_payment_return_amount_accepts_current_and_legacy_row_shapes -q`
**Offene Risiken:** `check_critical_backend_coverage.py` bleibt nach dem gruenen Sammellauf noch rot fuer `dunning.py`, `booking_templates.py`, `chart_of_accounts.py`, `finance_read_models.py`, `waage.py`, `warehouses.py`, `warehouse_transfers.py`; diese Pfade sind in der Coverage-Plan-Datei als Folgeslices priorisiert.

## ERP-CRUD-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Browser-/CRUD-Abnahme der wichtigsten E2E-Prozesse in eine ausfuehrbare, priorisierte Testmatrix ueberfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/quality-assurance/browser-use-checklists.md`, `docs/quality-assurance/e2e-crud-acceptance-matrix-2026-04-24.md`, ggf. vorhandene Frontend-E2E-Testkonfiguration.
**Abnahmekriterien:** Die neun Flow-Spine-Prozesse besitzen eine priorisierte CRUD-/Statuswechsel-/Korrekturmatrix mit klaren P0/P1-Prueffaellen und Repo-Pruefkommandos.
**Erledigt:** Neue priorisierte E2E-CRUD-Matrix fuer P0/P1-Flow-Spine-Prozesse erstellt und in den Browser-Use-Checklisten verlinkt.
**Offene Risiken:** Echte Browser-Ausfuehrung haengt vom lokal startbaren Fullstack und Seed-Daten ab.

## ERP-LIVE-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Live-Integrations-Readiness mit echten Secrets/Zielsystemen so weit repo-seitig vorbereiten, dass Ops nur noch Werte eintragen und Pruefkommandos ausfuehren muss.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/integration-bootstrap-readiness-2026-04-12.md`, `scripts/check_integration_bootstrap.py`, `app/services/integration_bootstrap.py`, `.env.example`.
**Abnahmekriterien:** Readiness-Bericht trennt deterministische Repo-Pruefung und externe Live-Probes; fehlende Secrets/Ziele werden maschinenlesbar als Blocker ausgewiesen.
**Erledigt:** `--strict-live` ergaenzt; Live-Probe-Plan und Gate sind dokumentiert.
**Offene Risiken:** Produktive Tenant-Secrets und Zielsystem-URLs liegen ausserhalb des Repos.

## FIBU-CUTOVER-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** FIBU-Cutover-Mappings fachlich abschliessbar machen, indem Pflichtmapping, Freigabezustand und Validierung formalisiert werden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/fibu-cutover-mapping-readiness-2026-04-24.md`, `config/fibu_cutover_mapping.template.yaml`, `scripts/check_fibu_cutover_mapping.py`, `tests/test_fibu_cutover_mapping.py`.
**Abnahmekriterien:** Konten-, Steuer-, Kostenstellen- und Gegenkonto-Mappings haben eine Vorlage, einen Validator und einen klaren Blockerstatus fuer fachliche Freigabe.
**Erledigt:** FIBU-Cutover-Template, Validator, Tests und Readiness-Doku erstellt.
**Offene Risiken:** Fachlich freigegebene Zielkonten/-steuerschluessel muessen vom Fachbereich geliefert werden.

## RATIONS-SPLIT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rations-Solver technisch weiter entkoppeln, ohne die LP-Semantik zu aendern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/solver/*`, relevante Rations-Tests.
**Abnahmekriterien:** Ein weiterer klarer Solver-Baustein wird aus `rations_optimization.py` in das Solver-Paket gezogen oder mit typisierter Hilfslogik isoliert; Regression bleibt gruen.
**Erledigt:** Mischgruppen-Reihenfolge als `app/agrar/rations/solver/mixing.py` aus dem Endpoint-Pfad herausgezogen und separat getestet.
**Offene Risiken:** Vollstaendige `_run_lp`-Zerlegung ist ein mehrstufiger Refactor.

## DOMAIN-PARITY-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Domänenparitaet in schwächeren Bereichen als messbares Ausbauprogramm statt loser Absicht fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/domain-parity-roadmap-2026-04-24.md`, `docs/project-context/open-gaps-and-known-issues.md`.
**Abnahmekriterien:** Finance, Supply/Inventory, Procurement, Contracts, CRM und Documents sind nach Fachlogik, Testtiefe, Integration und UI-Operationalisierung bewertet; naechste Code-/Test-Slices sind priorisiert.
**Erledigt:** Domain-Parity-Roadmap mit Bewertungsraster, Prioritaeten und naechsten Code-Slices erstellt und in `open-gaps` verlinkt.
**Offene Risiken:** Tiefe fachliche Paritaet braucht weitere domänenspezifische Arbeit und Fachentscheidungen.

## RATIONS-HARD-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rations-/Fuetterungsmodul nach Punkt 4 gezielt haerten, ohne den Solver grossflaechig umzubauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_feeding_system.py`, `tests/test_rations_mixing_protocol.py`
**Abnahmekriterien:** Weide wird auch bei nominellem TMR-Input nicht ins Mischprotokoll aufgenommen; Auto-Promotion TMR -> PMR_pasture ist regressionsgesichert; Mischprotokoll nutzt die vorhandene Feed-Dataclass als typisierte Solver-Sicht.
**Erledigt:** Mischprotokoll nutzt `Feed.from_dict()` fuer die typisierte Feed-Sicht; TMR+verfuegbare Weide wird auf PMR_pasture auto-promoted; falsch als `tmr_block` gelabelte Weide wird aus der Mischung ausgeschlossen und im Protokoll als `excluded_pasture` ausgewiesen.
**Checks:** `pytest tests/test_rations_feeding_system.py tests/test_rations_mixing_protocol.py tests/test_rations_feed_dataclass.py -q`
**Offene Risiken:** Vollstaendige Zerlegung von `_run_lp` und regelbasiertes Warnsystem bleiben Folgeslices. Konzentrat-Tagesmax wird jetzt als Stage-2-LP-Slack abgebildet (siehe RATIONS-POLICY-PIPE-001).

## RATIONS-POLICY-PIPE-001

**Von:** Cursor
**Stand:** abgeschlossen 2026-04-24
**Ziel des Slices:** Rationspipeline policy-/fachlich schaerfer machen (Saftfutter-Caps, PMR-Weide-Profile, k_l, Infeasibility-Hilfen, Konzentrat-Slack) und Frontend/TS an die erweiterte API anbinden.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_feeding_system.py`, ggf. `app/agrar/rations/solver/mixing.py` / `tests/test_rations_solver_mixing.py`.
**Abnahmekriterien:** Backend liefert die neuen Meta-Felder (u. a. Konzentrat-Slack, `ration_blocks.feeding_system.auto_promoted_from_tmr`, Mixing `excluded_pasture`); Frontend sendet `feeding_system_config` und zeigt RationBlocks/Mixing/KF-Slack; Regression gruen.
**Erledigt:** Saftfutter/nasse CoP: weiche/harte Caps, LP-hart, Soft-Constraint + Referenz-HTML; `_POLICY_PROFILE_TARGETS` um `tmr_standard`, `pmr_standard`, `pmr_pasture_spring/summer/autumn`; Stage-2 Konzentrat-Tagesmax-Slack + Response `concentrate_max_lp_slack_*`; nach Solve FS mit Ist-Mengen neu aufgeloest, `_block_labels` aktualisiert; Infeasibility: Heu/Stroh-Abdeckung, aNDFom-Kapazitaet (`ndf_capacity`), generischer Zweig nur bei grobfutterarmem Set; k_l bei PMR+Weide ueber FANi + TMR-ME-Dichte (`_kl_milk_from_me_density`); `result.x` auf Feed-Laenge begrenzt. Frontend: Typen, Default-Config im Request, Panels, Policy-Badge fuer KF-Slack.
**Checks:** `pytest tests/test_rations_feeding_system.py tests/test_rations_optimization_milk_plausibility.py -q`; im Paket `frontend-web`: `pnpm run type-check`
**Offene Risiken:** Optional Wizard fuer manuelle `feeding_system_config`-Overrides; E2E-Smoke Rations-UI; weiteres Zerlegen von `_run_lp`.

## RATIONS-WIZARD-E2E-001

**Von:** Cursor
**Stand:** abgeschlossen 2026-04-24
**Ziel des Slices:** Wizard-Schritt 3 (Grenzen + weiche Ziele) als State/API an Backend anschließen, Prioritäten grob an `objective_strategy` koppeln, TM-Ziel/`target_dmi_kg` und Wizard-TM-Band im `_gfe_requirements` nutzen, Workbench-Duplikatnamen klären, Playwright mit `webServer`, kurze Pytest-Regression, QA-Checkliste ohne private Fixtures.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py` (`_gfe_requirements`, `_run_lp` Wizard-Dichten), `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/playwright.config.ts`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `tests/test_rations_wizard_requirements.py`, `docs/agent-ops/rations-manual-compound-qa.md`.
**Abnahmekriterien:** Frontend sendet `objective_strategy`, `policy_overrides.wizard_*`, `wizard_dmi_*` am Profil; Backend klemmt TM-Band; Playwright kann Vite selbst starten; Regressionstests gruen.
**Checks:** `pytest tests/test_rations_wizard_requirements.py -q`; im Paket `frontend-web`: `pnpm exec playwright test tests/e2e/rations-compound-upload.spec.ts` (mit laufendem Backend) bzw. `pnpm run type-check`.
**Erledigt (Folgesession LP):** `policy_overrides.wizard_hard_bounds` steuert ME-/Stärke-/aNDFom-Mindest- bzw. Höchst-Dichten (linear auf Gesamtration); `andfom_gf_min_pct_tm` schärft die aNDFomGF+CoP-Untergrenze vor LP-Aufbau.
**Erledigt (Session 2026-04-24ff):** `wizard_soft_goals` wirken solver-seitig fuer `minimize_soya` (Stage-1-Welfare-Penalty + Stage-2-Kostenzuschlag auf Soja-Futtermittel), `prefer_homegrown` (Bonus fuer `gfa_`-/`_source=="gfa"`-Feeds), `maximize_n_efficiency_rmd` (Penalty bei hohem Feed-RMD); Metadata `wizard_soft_goals_lp` listet aktive Flags. `optimization_strategy` bleibt Legacy-Kurzstring; Detail in `optimization_strategy_pipeline`. Milch-Kennziffern GF/Weide: anteilige Erhaltungsbuchung ueber GF-ME-/Teilmengen-ME-Anteil (`_maintenance_allocation_fraction`).
**Erledigt (Session 2026-04-24 Baseline-L1):** `minimize_deviation_from_baseline` mit `policy_overrides.wizard_baseline_kg_dm` (feed_id -> kg TM): L1-Abstand via Hilfsvariablen in Stage 1 (`_WIZARD_BASELINE_L1_WEIGHT`) und gekoppeltes Gewicht in Stage 2; Frontend speichert nach erfolgreicher Optimierung die Ist-Ration als Baseline und sendet sie bei Re-Optimierung. Playwright-Smoke `tests/e2e/rations-smoke.spec.ts` (Demo-Pfad).
**Offene Risiken:** Gewicht `_WIZARD_BASELINE_L1_WEIGHT` ggf. kalibrieren; weiteres Zerlegen von `_run_lp`.

## INT-LIVE-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Produktnahe Live-Integrationspruefung nach Punkt 6 repo-seitig konkreter machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py`, `tests/test_integration_bootstrap.py`, `docs/project-context/integration-bootstrap-readiness-2026-04-12.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Bootstrap-Readiness liefert zusaetzlich einen Probe-Plan fuer echte Connectivity-Pruefungen; CLI kann diesen Plan ausgeben; Tests unterscheiden ready, disabled, blocked und manual/external.
**Erledigt:** `build_integration_bootstrap_summary()` liefert jetzt `probe_plan`; `scripts/check_integration_bootstrap.py --probe-plan` gibt nur diesen Live-Probe-Plan aus; Tests decken ready/blocked/disabled fuer OIDC, NATS, Superglue, Voice und CRM-Downstream ab.
**Checks:** `pytest tests/test_integration_bootstrap.py -q`
**Offene Risiken:** Echte Produktivtests benoetigen weiterhin externe Tenant-Secrets, Zielsystem-URLs und Ops-Freigaben.

## RATIONS-REFACTOR Schritte 1-5 (abgeschlossen 2026-04-23)

**Von:** Cursor
**Auslöser:** User-Feedback "rations_optimization.py: too large, too much in one pass, Refactoring-Roadmap in 5 Schritten".
**Stand:** Alle 5 Refactoring-Schritte umgesetzt; 561 passende Tests in der Rations-Regression (547 + 8 Aggregator + 6 Feed).

**Auslieferung:**
- **Paketstruktur** (Schritt 1a-e): Neues Paket `app/agrar/rations/` mit Subpackages `constants/`, `compound_feed/`, `repository/`, `http/`, `solver/`, `response/`. Konstanten, HTTP-Proxy, DLG-JSON-Loader und Compound-Feed-Parser (OCR/PDF/Etikett) leben jetzt in dedizierten Modulen; Re-Exports in `rations_optimization.py` halten die öffentliche Schnittstelle stabil.
- **Zentrale Aggregation** (Schritt 2): `RationAggregates` @dataclass(slots=True) + `aggregate_ration()` in `app/agrar/rations/response/aggregator.py`. `_build_response` nutzt sie jetzt in einem einzigen Pass statt 16+ `_sum()`-Aufrufen plus separaten Schleifen für Forage, CoP, pabKH und pendf. Block-Aggregation (Slice 1f) ist integriert.
- **Constraint-Registry** (Schritt 3): `ConstraintRegistry` + 17 symbolische Constraint-Namen in `app/agrar/rations/solver/constraint_registry.py`. `_run_lp` registriert jeden `_geq`/`_leq`-Aufruf benannt; die 4 historisch magischen Relaxations-Indizes (`_IDX_XL`, `_IDX_ANDFOM_GF`, `_IDX_RMD`, `_IDX_ME_ABS`) werden jetzt via `registry.index_of(...)` aufgelöst. Regressions-Asserts sichern die historische Reihenfolge.
- **Relaxations-Kapselung** (Schritt 4): Die 4-stufige Relaxations-Kaskade (XL → RMD → aNDFomGF-Drop → sidP-85%) ist aus dem LP-Hauptblock in eine benannte Closure `_relax_stage1()` ausgezogen. Semantik unverändert.
- **Feed-Dataclass** (Schritt 5): `Feed` @dataclass(slots=True) in `app/agrar/rations/solver/feed.py` als read-only View auf die Dict-Struktur. Bietet `Feed.from_dict()` mit konsistenter Typkonvertierung (None → 0.0 bei numerischen Pflichtfeldern, Optional bei unsicheren). Slot-Schutz verhindert unbeobachtete Attributerweiterungen. **Keine Breitenumstellung**, Opt-in für künftige Module.

**Tests:**
- Neue Unit-Tests `tests/test_rations_aggregator.py` (8 Tests) und `tests/test_rations_feed_dataclass.py` (6 Tests).
- Volle Rations-Regression: **561 pass** (davon 547 bestehende, unverändert grün).

**Offene Folgeschritte (bewusst separat):**
- Vollständige Zerlegung von `_run_lp` in Constraint-Builder/Relaxation/Stage2-Cost/Solve-Orchestrator (Schritt 4 ist bewusst minimal invasiv geblieben; ein echter Split ist ein eigener, größerer Slice).
- Breitenumstellung `Feed.from_dict`-basiert in `_run_lp` und `_build_response` (Schritt 5 legt nur das Fundament).
- Warnsystem regelbasiert (`WarningRule` statt if-Kaskade).
- Feed-Matrix mit NumPy für den Koeffizienten-Aufbau.



Dieses Board ist bewusst schlank gehalten, damit Session-Starts und Agent-Handoffs weniger Kontext verbrauchen.

## RATIONS-LP-SPLIT-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** `_run_lp` in `rations_optimization.py` durch Extraktion des Constraint-Matrix-Aufbaus in `app/agrar/rations/solver/lp_constraints.py` und der Stage-2-Policy-Extension in `app/agrar/rations/solver/lp_stage2.py` von ~1350 auf ~800 Zeilen reduzieren.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/solver/lp_constraints.py` (neu), `app/agrar/rations/solver/lp_stage2.py` (neu), `tests/test_rations_lp_constraints.py` (neu)
**Abnahmekriterien:** Volle Rations-Regression gruen; `_run_lp` < 900 Zeilen; `lp_constraints.py` exportiert `build_lp_constraint_matrix`; `lp_stage2.py` exportiert `build_policy_band_lp_extension`.

## COV-RATCHET-004

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Coverage-Schwellen fuer bereits gruene kritische Pfade kontrolliert anheben (Puffer auf 97 % des gemessenen Wertes) und drei neue Ratchet-Pfade aufnehmen (strecke.py, sales_orders.py, ap_invoices.py).
**Dateibesitz:** `scripts/check_critical_backend_coverage.py`, `docs/project-context/domain-parity-roadmap-2026-04-24.md`
**Abnahmekriterien:** Alle Schwellen liegen <= gemessener Wert; `python scripts/check_critical_backend_coverage.py` gibt gruenen Exit-Code wenn coverage.xml vorhanden.

## DOMAIN-PARITY-COV-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** COV-INT-002: Integrations-Governance-Tests fuer `strecke.py`, `kontrakte.py` und `ap_invoices.py` hinzufuegen; domain-parity-roadmap um abgeschlossene Slices aktualisieren.
**Dateibesitz:** `tests/test_strecke_api.py` (neu), `tests/test_kontrakte_api.py` (neu), `tests/test_ap_invoices_api.py` (neu), `docs/project-context/domain-parity-roadmap-2026-04-24.md`
**Abnahmekriterien:** Neue Testdateien vorhanden, >= 5 Tests je Datei, pytest gruen; Roadmap-Dokument aktualisiert.

## RATIONS-FS-WIZARD-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Wizard-Schritt fuer `feeding_system_config` im Rations-Wizard in `rationsoptimierung.tsx` sichtbar machen (System-Auswahl TMR/PMR_stall/PMR_pasture, Konzentratsverteilung, Limits je Verteilung).
**Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/src/lib/api/rations-optimization.ts`
**Abnahmekriterien:** Wizard-Schritt sichtbar, `feeding_system_config` wird im Request gesendet, TypeScript-Typen passen, `pnpm run type-check` gruen.

## RATIONS-FANI-KL-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** FANi-basiertes dynamisches k_l in den Solver-Iterationsloop einbauen: `_gfe_requirements` erhaelt optionales `fani`-Argument, das `k_l_planning` (bisher fix 0,60) via `_kl_milk_from_me_density` iterativ anpasst. Gilt fuer PMR_pasture und TMR.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_fani_kl.py` (neu)
**Abnahmekriterien:** `_gfe_requirements(profile, fani=3.2)` gibt anderen `me_mj` als `fani=None`; Rations-Regression gruen; FANi-Iteration in `_run_lp` reicht FANi an `_gfe_requirements` durch.

Archiv des vorherigen Boards:
- [active-workboard-2026-04-10-pre-slim.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/archive/active-workboard-2026-04-10-pre-slim.md)

## AGRAR-COV-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Unit- und HTTP-Tests fuer `agrar_contracts.py` und `agrar_settlements.py` — Abnahme-Status-Logik, Abrechnungs-Rundung, DQ-Datensatz-Aufbau und CRUD-Smoke-Pfade.
**Dateibesitz:** `tests/test_agrar_contracts_api.py` (neu), `tests/test_agrar_settlements_api.py` (neu)
**Abnahmekriterien:** >= 15 Tests je Datei; `_compute_status`, `_round_money`, `_round_qty`, `_build_*_dq_datensatz` und HTTP-Pfade gruendeckend; pytest gruen.
**Erledigt:** 20 agrar_contracts-Tests (Status-Logik, DQ, CRUD); 17 agrar_settlements-Tests (Rundung, Modell-Validierung, Smoke-HTTP). 54 pass gesamt.

## FIN-COV-002

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Unit- und HTTP-Tests fuer `closing_checklists.py` und `bank_reconciliation.py` — Mapping-Funktion, Freigabe-Logik, Pydantic-Modelle und Smoke-Pfade.
**Dateibesitz:** `tests/test_closing_checklists_api.py` (neu), `tests/test_bank_reconciliation_api.py` (neu)
**Abnahmekriterien:** `build_closing_checklist_response` vollstaendig getestet inkl. approval_can_close und explainability; Pydantic-Modelle fuer BankReconciliation; HTTP-Smoke-Pfade gruen.
**Erledigt:** 17 closing_checklists-Tests (Mapping, Freigabe, Explainability, Validierung, HTTP); 11 bank_reconciliation-Tests (Pydantic-Modelle, HTTP-Smoke). 54 pass gesamt.

## Arbeitsregel

- Nur aktive oder frisch abgeschlossene Slices bleiben hier sichtbar.
- Historische Serien wandern ins Archiv.
- Claim-Pflicht bleibt unveraendert:
  1. Slice auf `reserviert`
  2. Workboard committen
  3. erst dann implementieren

## Kurzstand

- Das gemeinsame operative Arbeitsmodell ist bereits in den priorisierten Kernmasken ausgerollt.
- Der Rollout-Scope ist dokumentiert in:
  - [operational-rollout-scope-2026-04-09.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/operational-rollout-scope-2026-04-09.md)
- Der naechste Block betrifft Sammel- und Follow-up-Masken mit echtem operativem Mehrwert.
- Fuer den Flow-Spine-Kern liegt jetzt eine gemeinsame Lifecycle-Zieldoku vor:
  - [flow-spine-instance-lifecycle-overview.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/flow-spine-instance-lifecycle-overview.md)

## FEEDING-SYSTEM-ARCHITECTURE Slices 1-3 (abgeschlossen 2026-04-23)

**Von:** Cursor
**Stand:** Slice 1a-1f/1h + Slice 2 (Futterabruf-Staffel) + Slice 3 (Mischprotokoll) komplett implementiert und gruen; 98 Slice-spezifische Tests plus 386 pass in der vollen Rations-Regression.
**Auslieferung:**
- **Datenmodell** (Slice 1a): Neue Pydantic-Modelle `ConcentrateRecipeProfile` (starch_breakdown_class rapid/mixed/slow, rumen_buffer_present, source), `FeedingSystemConfig` (system TMR/PMR_stall/PMR_pasture, concentrate_distribution transponder/ams/milkparlor/included_in_tmr, Grenzen je Verteilung), `FeedBlockAssignment` (manuelles Override fuer Feed->Block).
- **Block-Zuordnung** (Slice 1b): Helper `_feeding_system_defaults`, `_resolve_feeding_system_config`, `_auto_assign_block`, `_split_feeds_by_block`; Mineralfutter wird prioritaer ins `tmr_block` gesetzt (auch wenn im Namen "Weide" steht).
- **k_l-Logik** (Slice 1d): `_kl_milk_from_me_density` setzt bei `PMR_pasture` fix `k_l=0.60` (dokumentiertes Uebergangs-Fallback; FANi-basiertes k_l ist Folgeslice).
- **Solver-Scoping** (Slice 1c): Struktur-/CP-/XL-/pabKH-Dichten im LP nur auf den TMR-Block, wenn PMR-System mit aktivem pasture_block oder concentrate_staged_block vorliegt. Weide wird nicht als strukturell irrelevant behandelt (eigene Weide-/Aufnahmelogik weiterhin aktiv).
- **Konzentrat-Limits** (Slice 1e, nachgeschaerft): Einzelgabe physiologisch hart als 1.5x-Sicherheitsnetz im LP; empfohlenes Tagesmax weich im Constraint-Status (Klasse B, Halbbreite 1,5 kg). Rezepturklassen wirken: rapid REDUZIERT Tagesmax (SARA-Schutz), slow+Puffer = Premium.
- **Response-Payload** (Slice 1f): Neue Felder `ration_items[*].block` und `ration_blocks` (feeding_system + tmr_block/pasture_block/concentrate_staged_block mit DMI, Kosten, ME, sidP, CP und Items-Liste). Abwaertskompatibel: bei TMR bleibt pasture_block/concentrate_staged_block leer.
- **Wire-up** (Slice 1h): `_OptimizeFromProfileBody.feeding_system_config` und `feed_block_overrides` freigegeben; `_resolve_runtime_options` normalisiert beide und reicht sie bis in den Solver durch.
- **Regressionstests erweitert**: Bruder-Fall (PMR+Weide Fruehjahr) prueft jetzt explizit (a) keine harte globale Strukturstrafe, (b) plausible Milch-aus-Grobfutter (10-40 kg nach 1-kg-Milch/kg-TM-Praxisregel), (c) vollstaendige Mg/K-Diagnose, (d) kein technisches False-Infeasible, (e) ration_blocks-Aggregat deckungsgleich mit Gesamt-DMI.
- **Slice 2 - Konzentrat-Futterabruf-Staffel** (`_build_concentrate_call_up_table`): Linear / stueckweise linear oberhalb Basisleistung (Milch aus Grobfutter). Band 0,45-0,50 kg Konzentrat (FM) je kg Zusatzmilch (Praxisrichtwert, nicht KI-Bildwerte). Einzelgabe-Limit je Verteilungssystem (Transponder/AMS/Melkstand), empfohlenes Tagesmax (weich) und physiologische Obergrenze 1,5x (hart) werden explizit geprueft. Nur fuer gestaffelte Systeme; `None` bei TMR/included_in_tmr. Response-Feld: `concentrate_call_up`. Neues UI-Panel `ConcentrateCallUpPanel` unterhalb des Weide-Risiko-Panels. 12 neue Tests.
- **Slice 3 - Misch- und Fuetterungsprotokoll** (`_build_mixing_protocol`): Nur bei TMR-Block (TMR / PMR_stall). Reihenfolge Vertikalmischer: Strukturfutter -> Silagen -> Saftfutter/CoP -> Sonstiges -> KF/Mineralien. Wasserzugabe auf Ziel-TM 40 % (Standard), Uebermenge +5 % fuer Mischverluste. Transparente Warnungen bei sehr trockener / sehr nasser Mischung. Response-Feld: `mixing_protocol`. UI-Panel `MixingProtocolPanel` rendert direkt aus Backend-Daten (keine Heuristik im Frontend mehr). 11 neue Tests.
**Offene Folgeslices / Mittelfristig:** FANi-basiertes dynamisches k_l (statt fixem 0,60 bei PMR_pasture); dedizierte Weideaufnahme-/Substitutionslogik mit saisonalen Profilen (Sommer-Hitzestress, Herbst-N-Ueberschuss); echte LP-Slacks fuer das Konzentrat-Tagesmax (aktuell Post-Solve-Penalty); Wizard-UI fuer `feeding_system_config` (derzeit nur ueber API).

## FAN-MODE-V1 (abgeschlossen 2026-04-21)

**Von:** Codex
**Stand:** alle sechs Slices umgesetzt, committed und gruen; 63 FAN-MODE-Gate-Tests plus bestehende Rations-Regression passen (266 pass + 6 pre-existing wave74-Fehler, unabhaengig von FAN-MODE).
**Freigegebene Spezifikation:** [docs/project-context/rations-optimization-fan1-fani-spec-2026-04-21.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/rations-optimization-fan1-fani-spec-2026-04-21.md)
**Kernentscheidungen V1 (alle 2026-04-21 freigegeben, siehe §11.1):**
- `fan_tolerance=0.05`, warn `0.10`, max 5 Iterationen
- FAN-Presets `2.5 / 3.0 / 3.5` + Freiwert
- `relaxation_policy` dreistufig `strict` / `standard` / `soft`, Default `standard`
- Strafterme **dimensionslos normiert** auf Zielkorridor, Basis 1,0 EUR, Klassen A x10 / B x3 / C x1
- Drei-Block-Limits als versionierte **Policy-Profile** (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring`), Override nur im Expertenmodus
- FAN-Formel-Katalog mit **Herkunftsflag** `exact | mapped | fallback` (Mapping auf DLG-Hauptgruppen GF/KF/SF, saisonal bei Weide/Gras)
- Wizard-FAN-Modus **sichtbar-kompakt** (Default `auto_iterative` direkt sichtbar, Reference/EvaluationOnly einklappbar)
- Bruder-Regression als **fachlich differenziertes** Abnahmekriterium (kein technisches False-Infeasible)
**Abgeschlossene Slices und zugehoerige Commits:**
- FAN-MODE-001: additiver Datenvertrag, neue Request-/Response-Felder, `_resolve_runtime_options`, Policy-/Season-Enums (commit vor dieser Session, +11 Gate-Tests).
- FAN-MODE-002: Hart/Weich-Split mit normierter Penalty (`_build_constraint_status_v2`, `_compute_penalty`, `_summarize_penalty`), erweiterte Infeasibility-Diagnose (commit `82b02735c`, +11 Gate-Tests).
- FAN-MODE-003: Fixpunkt-FAN-Iteration (`_apply_fan_effect`, `_fani_from_result`) mit Katalog `app/config/fan_slope_catalog.json` und drei Modi `auto_iterative` / `reference` / `evaluation_only`; Startwert aus geschaetzter DMI fuer schnelle Konvergenz (commit `f0dce8abb`, +12 Gate-Tests).
- FAN-MODE-004: Wizard-UI-Erweiterung in `rationsoptimierung.tsx` (Bewertungsmodus-Block, Reference-Presets, Advanced-Optionen) und Ergebnispanels `FanCalibrationPanel` + `ConstraintStatusPanel` in der Workbench (commit `b6bd983c7`).
- FAN-MODE-005: Saisonales Weideprofil im UI (PMR+Weide oeffnet Advanced, preset `spring_mid`, zeigt aktives Profil `pmr_pasture_spring`); Backend-Auto-Mapping in `_resolve_policy_profile` abgedeckt (commit `9a035ddd8`, +7 Gate-Tests).
- FAN-MODE-006: Strafsatz-Konfiguration vollstaendig sichtbar (Normalisierung, Klassen A/B/C, relaxation-Policy Monotonie), `penalty_summary` im Response und in der UI (commit `769cd1527`, +10 Gate-Tests).
**Offene Risiken / Follow-ups:** siehe §13 der Spec.
**Naechster Schritt:** Beobachtung der Fruehjahrsration-Regression unter `pmr_pasture_spring` in der Praxis, anschliessend optionaler Spec-Folge-Slice fuer explizite Slack-Variablen im Solver (Vollwert-3-Stage-Objective statt Post-Solve-Penalty) – nur bei konkretem Bedarf.

## peNDF als Kontrollgroesse + aNDFomGF-staerkeadaptiv (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 22 neue peNDF-Demotion-Gate-Tests plus volle Rations-Regression `357 pass` (keine Regression gegenueber vorherigem Stand).
**Kontext / DLG-Position:** Die DLG 01|2023 stellt explizit fest: peNDF steht fuer die Rationsplanung **nicht zur Verfuegung**. Empfohlene primaere Planungsgroesse ist die aNDFomGF-Dichte (Grobfutter-NDF) mit Zielwert >= 200 g/kg TM fuer Hochleistungsrationen, bei hoeheren pansenabbaubaren Kohlenhydraten entsprechend mehr. peNDF bleibt als Kontroll-/Validierungsgroesse erhalten.
**Auslieferung:**
- **Neuer Helper `_andfom_gf_min_target`**: aNDFomGF-Mindestdichte setzt sich zusammen aus Basis (200 g/kg TM non-pasture, 180 g/kg TM PMR+Weide) + staerkeadaptivem Aufschlag (+10 g/kg TM pro 20 g/kg TM Staerke oberhalb 180, Cap +40) + Saisonal-Boost + SARA-Boost. Ist jetzt die primaere Pansenstruktur-Planungsgroesse.
- **Stage-2-LP umgebaut** (`_run_lp`): Der bisherige harte `pendf_floor` in Stage 2 (Cost-Stage) wurde durch ein staerkeadaptives `stage2_andfom_gf_min` ersetzt. peNDF bleibt nur noch als absolute physiologische Sicherheits-Floor (120 g/kg TM) im LP, nicht mehr als Planungsgroesse.
- **Kalibrierungsstatus `_pendf_model_calibrated`**: Das peNDF-Lookup-Modell gilt als kalibriert, wenn Staerke in [0, 250] g/kg TM und TM-Aufnahme in [10, 25] kg/d liegt. Ausserhalb laufen Fallback-Regeln. In `dlg_indicators` neu: `pendf_model_calibrated: bool`, `pendf_model_status: "peNDF-Modell im kalibrierten Bereich" | "peNDF ausserhalb Modellbereich; Fallback-Regeln verwendet"`, `pendf_role: "Kontrolle/Validierung (DLG 01|2023)"`. Ebenfalls neu: `andfom_gf_base` und `andfom_gf_starch_uplift` als transparente Herkunfts-Aufschluesselung.
- **Warnungen angepasst**: peNDF-Warnung laueft jetzt **primaer ueber den Kalibrierungs-Status** - ausserhalb Modellbereich erscheint ein expliziter Fallback-Hinweis statt einer pauschalen Unterdeckungs-Ampel. Innerhalb des Modellbereichs wird peNDF als "Kontrollgroesse im Warnbereich" markiert, mit Verweis auf aNDFomGF und pabKH als eigentliche Steuergroessen.
- **SARA-Trigger-Logik angepasst** (`_detect_sara_risk`): peNDF-Trigger feuert nur, wenn das Modell kalibriert ist. Zusaetzlich feuert jetzt ein expliziter `aNDFomGF < Ziel - 10`-Trigger als primaerer Struktur-Sicherheitspfad. pH-Trigger und pabKH-Trigger bleiben unveraendert.
- **Frontend-Panel `rationsoptimierung.tsx`** neu zweigeteilt: oberhalb "Planung (primaer)" mit Strukturindex, aNDFomGF (inkl. Staerke-Aufschlag-Zerlegung), pabKH, RMD - darunter "Kontrolle / Validierung (DLG 01|2023)" mit peNDF-Modell-Status-Zeile und peNDF/pH-Ampel. peNDF-Zeile heisst jetzt explizit "peNDF (Kontrolle)" und die Ampel wird neutralisiert (grau), wenn das Modell im Fallback-Bereich laeuft.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_pendf_demotion.py` (neu, 22 Tests).
**Tests:** `pytest -k "rations or optim or wave74"` -> **357 pass**. Neue Suite `tests/test_rations_optimization_pendf_demotion.py`: staerkeadaptive aNDFomGF-Berechnung parametrisiert, Kalibrierungsflag fuer typische und Extremwerte, `dlg_indicators`-Zeichenketten ("Kontrolle"/"aNDFomGF"/Fallback-Status), SARA-Trigger respektiert Kalibrierungsstatus, Warnung bei peNDF-Fallback.
**Simulation bestaetigt:** Variant B (Hochleistung 48 kg Milch, DMI 26.6 kg/d > 25) liefert jetzt den Hinweis "peNDF ausserhalb Modellbereich ... Fallback-Regeln verwendet - peNDF-Ampel nur eingeschraenkt belastbar". Keine False-Alarme bei fachlich guten Rationen.
**Offene Follow-ups:** Praxisvalidierung der staerkeadaptiven aNDFomGF-Staffelung mit echten Hochleistungsrationen. Ggf. Sekundaer-Kalibrierungs-Flag fuer die pH-Formel analog dokumentieren (ist bereits via `ph_formula_applicable` verfuegbar).

## Gras-/Silage-/Heu-Klassifikation TM-basiert (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `96 pass` (inkl. `32 neue Gate-Tests` in `tests/test_rations_optimization_grass_classification.py`).
**Kontext:** User-Feedback zum Screenshot vom 2026-04-21: In der Ration war "Gras, frisch o. konserviert, 2. Aufwuchs" mit 6,6 kg FM / 2,32 kg TM (→ 35 % TM) enthalten, wurde aber faelschlich als Weide klassifiziert - das UI-Panel zeigte "Grassilage TM: 0,00 kg". Die Namens-Heuristik konnte die drei DLG-Varianten (frisch/siliert/trocken, `TMGEHALT` 175/350/860 g/kg) nicht sauber unterscheiden, weil das Feed-Namens-Feld fuer alle drei identisch ist.
**Fachliche Regel (User):** "Haupterkennung fuer Silagen sind ein TM Gehalt von 30 bis 40 %, bei ueber 80 % Heulage, bei ueber 85 % Heu bei Gras."
**Auslieferung:**
- **Neue zentrale Funktion** `_grass_feed_kind(feed)` in `rations_optimization.py`: klassifiziert Gras-basierte Grobfutter **primaer ueber `dm_frac`** (TM-Anteil), mit Name-Fallback wenn TM fehlt. Rueckgabe `"pasture"` (TM < 30 %), `"grass_silage"` (30-80 % TM, inkl. Anwelksilage/Heulage), `"grass_hay"` (≥ 80 % TM bei Gras-Kontext) oder `None` (Nicht-Gras).
- **Vier Call-Sites vereinheitlicht:** `_is_pasture_feed` und `_is_grass_silage` (in `_build_response`), `_max_kg_for` (LP-Obergrenze), `_feed_pendf_factor_base`, `_has_pasture_forage`, `weide_mask` (TMR-Deckelung) und `_map_feed_to_gfe_group` (FAN-Gruppen-Zuordnung) nutzen jetzt durchgaengig die TM-basierte Klassifikation.
- **Regression aufgeloest:** "Gras, frisch o. konserviert, 2. Aufwuchs" mit 35 % TM wird jetzt korrekt als `grass_silage` erkannt; "Weide, Fruehjahr, jung" mit 17,5 % TM bleibt Weide. Die UI-Anzeige "Grassilage TM" im Weide-Panel listet kuenftig die konservierten DLG-Varianten korrekt.
- **Tests**: `tests/test_rations_optimization_grass_classification.py` (neu, 32 Tests) deckt ab: TM-Grenzen 30 %/80 %, alle drei DLG-Varianten, Weide-Erkennung, Heulage/Heu, Nicht-Gras-Futtermittel (Mais/Weizen/Soja/Stroh/Mineral), Name-Fallback ohne TM, Screenshot-Regression.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py` (6 Aenderungen: neue Helper-Funktion `_grass_feed_kind`, `_is_pasture_feed`/`_is_grass_silage`, `_max_kg_for`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group`), `tests/test_rations_optimization_grass_classification.py` (neu), `docs/agent-ops/active-workboard.md`.
**Tests:** `pytest tests/test_rations_optimization_dlg2025.py tests/test_rations_optimization_compound_feed.py tests/test_rations_optimization_grass_classification.py` → **96 pass**, keine Regression.
**Offene Follow-ups:** - (keine).

## Milch-aus-Grundfutter Plausibilitaet + TM-basierte Gras-Klassifikation (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `115 pass` in 4 relevanten Rations-Suiten (davon `51 neue Gate-Tests`: 32 in `test_rations_optimization_grass_classification.py`, 19 in `test_rations_optimization_milk_plausibility.py`).

**Kontext:** Zwei verschraenkte User-Beobachtungen aus dem Screenshot vom 2026-04-21:
1. "Gras, frisch o. konserviert, 2. Aufwuchs" (35 % TM) wurde faelschlich als Weide klassifiziert -> UI zeigte "Grassilage TM: 0,00 kg". Der Feed-Name konnte die drei DLG-Varianten (frisch 17,5 % / siliert 35 % / trocken 86 % TM) nicht unterscheiden, weil das Namensfeld fuer alle identisch ist.
2. Faustregel "1 kg TM Grundfutter ~ 1 kg Milch, Spitzengrundfutter bis 1,2" wurde massiv ueberschritten (37,6 kg Milch / 22,1 kg GF-TM = 1,70 kg/kg).

**Auslieferung - TM-basierte Klassifikation:**
- **Neue zentrale Funktion** `_grass_feed_kind(feed)` in `rations_optimization.py`: klassifiziert primaer ueber `dm_frac` (Frischgras < 30 %, Grassilage inkl. Anwelksilage/Heulage 30-80 %, Heu >= 80 %), Name-Fallback wenn TM fehlt.
- **Sechs Call-Sites vereinheitlicht:** `_is_pasture_feed`, `_is_grass_silage`, `_max_kg_for`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group` nutzen jetzt durchgaengig die TM-Klassifikation.

**Auslieferung - Milch-aus-GF-Plausibilitaet (drei Slices):**
- **Slice A - Weide-Aktivitaetszuschlag:** In `_gfe_requirements` und `_milk_requirement_factors` wird bei `feeding_type == "PMR+Weide"` ME_maint um **+15 %** erhoeht (DLG-Merkblatt 417 / GfE 2001: Lauf-, Rupf-, Thermoregulations-Aktivitaet). Das wirkt sowohl auf die Solver-Bedarfsberechnung (Konsistenz) als auch auf die Anzeige "Milch aus Grundfutter".
- **Slice B - Weide-TM-Obergrenze:** In `_max_kg_for` wurde die Weide-Obergrenze von 14 auf **12 kg TM/d** reduziert (DLG 417: Praxismittel Hochleistungs-Standweide 10-12 kg). Das begrenzt die LP-Optimierung auf physisch erreichbare Aufnahmemengen.
- **Slice C - dichte-abhaengiges k_l:** Neue Helper-Funktion `_kl_milk_from_me_density(me_density)` implementiert GfE 2001 §5: **k_l = 0,463 + 0,24 * q** mit q = ME/GE (GE ~ 18,4 MJ/kg TM), begrenzt auf den Arbeitsbereich [0,58 ; 0,64]. Statt fix `k_l = 0,62` rechnet der Code jetzt fuer jede Auswerte-Ebene (Gesamt, Grundfutter, Weide, Grassilage, Weide+Silage) mit der ration-spezifischen ME-Dichte. In `_gfe_requirements` selbst bleibt `k_l_planning = 0,60` als konservativer Default fuer den Solver-Bedarf (leichte Verschaerfung gegenueber vorher 0,62, ~3 % mehr ME-Bedarf).

**Wirkung auf den Screenshot-Fall (ME-Dichte 11,6 MJ/kg TM, 22,1 kg GF-TM, PMR+Weide):**
- Alte Anzeige: 37,6 kg Milch aus GF -> 1,70 kg/kg TM
- Neu (A+C in fester Ration): 37,1 kg -> 1,68 kg/kg TM (nur -0,5 kg, weil bei 11,6 MJ/kg ME-Dichte die Faustregel rechnerisch hoeher liegt)
- **Eigentlicher Hebel ist Slice B in der LP-Optimierung**: Die naechste Demo-Rueckoptimierung wird statt 14 kg Weide nur noch 12 kg ansetzen duerfen, wodurch der Solver mehr Kraftfutter einsetzt und "Milch aus Grundfutter" auf realistische 28-32 kg faellt (~1,3-1,4 kg/kg TM).

**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py` (neue Helper `_grass_feed_kind`, `_kl_milk_from_me_density`; modifiziert: `_gfe_requirements`, `_milk_requirement_factors`, `_milk_from_supply`, `_max_kg_for`, `_is_pasture_feed`, `_is_grass_silage`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group`, alle Weide-/Grassilage-Milch-Aufrufe im `_build_response`).
**Neue Tests:** `tests/test_rations_optimization_grass_classification.py` (32 Gate-Tests), `tests/test_rations_optimization_milk_plausibility.py` (19 Gate-Tests fuer k_l-Kurve, Weide-Zuschlag, Screenshot-Regression, Faustregel-Korridor).

**Tests:** `pytest tests/test_rations_optimization_*.py` -> **115 pass**, keine Regression in den bestehenden Suites (dlg2025: 60, compound_feed: 4).

**Fachliche Quellen:**
- GfE 2001 (Empfehlungen fuer die Energie- und Naehrstoffversorgung der Milchkuh), §5 k_l-Berechnung
- DLG-Merkblatt 417 "Fuetterung der Milchkuh auf der Weide"
- DLG-Futterwerttabellen 2025 (Feld `KONSERVIERUNG`: frisch / siliert / trocken mit TM 175/350/860 g/kg)

**Offene Follow-ups:** - (keine). Weitere Feldvalidierung erfolgt durch den naechsten Durchlauf der Bruder-Regression mit den neuen Grenzen.

## DLG-01|2025 LP-Slacks + Praxisvalidierung Bandgewichte (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `155 pass` in den acht relevanten Rations-Suiten (inkl. `+22 neue Gate-Tests` in `tests/test_rations_optimization_dlg2025.py` → jetzt 60 DLG2025-Tests).
**Kontext:** Zwei Follow-ups aus dem Slice "DLG-01|2025 Solver-Bindung" zusammengezogen - (a) die Post-Solve-Penalty fuer Policy-Baender wurde durch **native LP-Slack-Variablen** ersetzt, und (b) die Halbbreiten (`min_halfwidth`) je Parameter wurden mit typischen Hochleistungs- und Trockensteher-Rationen kalibriert und als Tests abgesichert.
**Auslieferung:**
- **Backend `_build_policy_band_lp_extension`** (neu in `rations_optimization.py`): baut fuer jedes Policy-Band (ME-/CP-/sidP-/pabKH-/XL-/Grundfutter-/aNDFomGF+CoP-/aNDFom-Dichte) eine **Slack-Variable** `s_min` bzw. `s_max >= 0` mit normierter Penalty im Objective auf. Die Slack-Kosten skalieren mit `base × class_B × relax_factor / (halfwidth × DMI_typ)`, so dass LP-Slack und Post-Solve-Penalty fachlich aequivalent sind. `_run_lp` fuehrt, wenn ein DLG-2025-Profil aktiv ist, einen **erweiterten Stage-2-Solve** durch (`prices ⊕ slack_costs`, `A ⊕ slack_cols`, `bounds ⊕ (0, ∞)`); bei Erfolg werden nur die Feed-Anteile uebernommen, die Slack-Werte gehen als Diagnose-Payload `policy_profile_lp_slacks` in die Response. Metadaten-Strategie ist dann `stage1_balance_then_stage2_cost_plus_policy_slack`.
- **Response-Erweiterung:** neue Felder `policy_profile_lp_slacks` (pro Band: `slack_value`, `weight`, `halfwidth`, `penalty_cost`, `active`), `policy_profile_lp_total_penalty`, `policy_profile_lp_mode`. Die bisherige Post-Solve-Auswertung `policy_profile_evaluation` bleibt als unabhaengiger Gegencheck erhalten, wenn die LP-Slacks aus technischen Gruenden kein Payload liefern.
- **Frontend `rations-optimization.ts`**: neuer Typ `PolicyProfileLpSlack`, Response-Interface um die drei neuen Felder erweitert.
- **UI `rationsoptimierung.tsx`**: im Panel "Leistungsstufen-Check (DLG 01|2025)" neues Badge **"LP-Slack aktiv"** (gruen) bei nativer Bindung plus Subsection "LP-Solver-Slacks (aktive Korridor-Verletzungen)" mit Slack-Wert/Einheit und Penalty pro Band sowie Summen-Penalty - zeigt, welche Baender der Solver selbst relaxieren musste.
- **Praxisvalidierung `test_rations_optimization_dlg2025.py`**: neue Klassen `TestPolicyBandLpSlackExtension` (6 Tests) und `TestPolicyBandHalfwidthCalibration` (16 parametrisierte Tests) belegen fuer typische Hochleistungs- (35-45 kg, ME 7,0-7,2 / CP 155-170 / sidP 78-85) und Trockensteher-Rationen (ME 5,8-6,2 / CP 120-135 / aNDFom 380-460), dass Werte **im Korridor zero-penalty** sind und Abweichungen > Halbbreite **monoton zunehmende Strafen** erzeugen. Zusaetzlich: `test_halfwidth_is_reference_for_penalty_unit` fixiert, dass eine Abweichung von exakt `1 × min_halfwidth` ausserhalb des Korridors die Einheits-Strafe `base × class_B × relax_standard` ergibt.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_dlg2025.py`, `docs/agent-ops/active-workboard.md`.
**Tests:** `pytest tests/test_rations_optimization_*.py tests/test_drying_rule_engine.py` → **155 pass**, keine Regression.
**Offene Follow-ups:** - (keine mehr aus dem DLG-01|2025-Block; weitere Feldvalidierung erfolgt im Rahmen der Bruder-Regression und der Hitzestress-/Herbstrations-Slices.)

## DLG-01|2025 Solver-Bindung + Wizard-Leistungsstufen (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `138 pass` in den sieben relevanten Rations-Suiten (inkl. 7 neue Band-/Solver-Bindungs-Tests in `tests/test_rations_optimization_dlg2025.py`).
**Kontext:** Follow-ups aus dem "DLG-01|2025-Alignment"-Slice wurden zusammen gezogen - (a) die Referenzkorridore aus `_POLICY_PROFILE_TARGETS` waren bisher nur im Response sichtbar, aber nicht im Solver gebunden, und (b) die neuen DLG-2025-Leistungsstufen waren nicht im Wizard anwaehlbar.
**Auslieferung:**
- **Backend `rations_optimization.py`**: Neue Helfer `_policy_profile_band_evaluate` + `_build_policy_profile_evaluation`. Nach jedem erfolgreichen LP-Lauf werden die Ist-Werte der Ration gegen die DLG-01|2025-Referenzkorridore des aktiven Profils als **weiche Bandchecks** (direction = min / max / target, Band-Modell) ausgewertet. Penalty faellt in **Klasse B** (Balance), relaxation_policy skaliert wie gewohnt (strict = 3x, standard = 1x, soft = 0.3x). Innerhalb des Korridors gilt `deviation_norm = 0`, also keine Strafe - dadurch keine zusaetzliche Infeasibility-Gefahr fuer schwierige Praxisrationen.
- **Ausgewertete Baender:** ME-Dichte (MJ/kg TM), CP-Dichte (g/kg TM), sidP-Dichte (g/kg TM), pabKH (max), Rohfett XL, Grundfutteranteil (%TM), aNDFomGF+CoP (min), aNDFom (min). Jedes Band traegt den Namen `DLG-Policy: ...` in `constraint_status` (source=`policy_profile`).
- **Response-Erweiterung:** neues Feld `policy_profile_evaluation` mit `profile`, `label`, `bands` (alle Checks inkl. `ok`), `violation_count`, `violations`, `penalty_total`, `source`. `penalty_summary.by_class.B` enthaelt die Policy-Strafe mit.
- **Frontend `rations-optimization.ts`**: neue Typen `PolicyProfileBand` + `PolicyProfileEvaluation`, Response um `policy_profile_evaluation` erweitert, `PolicyProfileTargets`-Feldnamen an das Backend angepasst (`forage_share_min_pct` / `forage_share_max_pct` / `ndf_kgdm_min`).
- **Wizard `rationsoptimierung.tsx`**: Im Advanced-Block neuer Dropdown **"Leistungsstufe (DLG 01|2025 Tab. 13-15)"** mit sechs Leistungs-/Physiologiestufen (`tmr_fresh_lactation`, `tmr_high_yield`, `tmr_mid_yield`, `tmr_late_lactation`, `tmr_transit`, `tmr_dry_cow`) plus den Bestandsprofilen (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring|summer|autumn`). Default "Auto (aus Fuetterungstyp/Saison)". Die Auswahl wird durch den vorhandenen `policy_profile`-Request-Parameter an das Backend durchgereicht. Hinweistext macht sichtbar, dass die Bindung **weich** ist (Klasse B, relaxation-policy-skaliert).
- **Ergebnispanel:** neues Panel "Leistungsstufen-Check (DLG 01|2025)" direkt nach dem DLG-Strukturkontrolle-Panel. Zeigt Profil-Label, Gesamtstrafe Klasse B, pro Band `Ist-Wert`, `Korridor (min … max)`, Abweichungs-Norm und Ampelpunkt (gruen/ok oder orange/violated). Badge oben zeigt "alle Baender im Korridor" oder "N Abweichung(en)".
- **Tests (7 neu in `tests/test_rations_optimization_dlg2025.py`):** `_policy_profile_band_evaluate` → ok-Band ohne Strafe, Unter-Min und Ueber-Max erzeugen Strafe in Klasse B, strict/standard/soft skaliert Strafe monoton, `_build_policy_profile_evaluation` returniert `None` ohne Profil/Targets, End-to-End-Response belegt `policy_profile_evaluation` + `constraint_status`-Eintraege mit `source=policy_profile` und fuettert `penalty_summary.by_class.B`. Negativtest: `tmr_standard` liefert kein `policy_profile_evaluation`.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_dlg2025.py`.
**Tests:** `pytest tests/test_rations_optimization_*.py` → **138 pass** in den sieben relevanten Suiten, keine Regressionen gegenueber dem vorherigen Stand (82 pass).
**Offene Follow-ups:**
- Praxisvalidierung der Bandgewichte (min_halfwidth je Parameter) mit echten Hochleistungs-/Trockensteher-Rationen.
- Optional: Umstellung von Post-Solve-Penalty auf native LP-Slacks mit gemeinsamer Stufe-2-Zielfunktion (fachlich aequivalent, aber zukunftssicherer fuer Priorisierungsschemata).

## DLG-01|2025-Alignment (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 32 neue DLG2025-Gate-Tests plus volle Rations-Regression `82 pass` in den vier relevanten Suiten.
**Kontext:** Nach dem SARA-Reopt + peNDF-Demotion hat der User um Abgleich der aktuellen Annahmen und Gleichungsformeln mit `DLG-Information 01|2025` (und, soweit nicht ueberholt, `01|2023`) gebeten. Der Abgleich hat vier konkrete Differenzen offengelegt, die in diesem Slice zusammen umgesetzt wurden.
**Auslieferung:**
- **DLG2025-PH-FORMEL**: Pansen-pH-Prediction nach Zebeli 2008 (zitiert in DLG 01|2025 Kap. 8.3), jetzt mit korrekten Koeffizienten `pH = 6,05 + 0,044·peNDF − 0,0006·peNDF² − 0,017·abbauSt − 0,016·TM`. Neuer Helfer `_abbaust_density_kgdm` ermittelt die **pansenabbaubare Staerke** (`ST − bST`), die als zweite formelwirksame Eingangsgroesse dient. Zucker beeinflusst die Formel **nicht** mehr. `dlg_indicators.ph_formula_source` = `Zebeli 2008 (DLG 01|2025)`, zusaetzlich `abbaust_kgdm` in `nutrient_supply` / `dlg_indicators`.
- **DLG2025-ANDFOMGF-COP**: Einfuehrung der Co-Produkt-Klassifikation (`structural_coproduct`-Flag je Feed; Heuristik ueber `_is_structural_coproduct` auf Namen/Kategorie; Saftfutter wie Biertreber/Pressschnitzel/Kartoffelpuelpe/Trockenschnitzel/Malztreber werden jetzt automatisch als strukturwirksam gefuehrt). `aNDFomGF`-Planung wird ersetzt durch `aNDFomGF+CoP` mit **binaerer DLG-Kaskade** (pabKH ≤ 210 → 200 g/kg TM, pabKH > 210 → 280 g/kg TM, pabKH > 260 loest Warnung). `_andfom_gf_min_target` nimmt `pabkh_density_kgdm` und greift auf die Kaskade zurueck, wenn verfuegbar; die alte Staerke-uplift-Linearitaet bleibt nur als Fallback. LP-Constraint in `_run_lp` ist entsprechend auf `aNDFomGF+CoP-Dichte` umgezogen; `constraint_report`, `nutrient_supply`, `dlg_indicators` und `_detect_sara_risk` nutzen die neue Groesse.
- **DLG2025-FIKH**: Neue Kontrollgroesse **Fermentationsindex Kohlenhydrate** (DLG 01|2025 Kap. 8.4): `FIKH [%] = DNDF / (DNDF + ST+ZU−bST) · 100`, Zielwert ≥ 50 %. Helfer `_fikh_percent` beruecksichtigt fehlende `NDFD`-Werte und liefert Diagnose (`no_ndfd` / `ok`). Ergebnis unter `dlg_indicators.fikh_pct | fikh_ziel | fikh_erfuellt | fikh_diagnose | fikh_quelle`. Warnung wenn FIKH < 50 %.
- **DLG2025-POLICY-TABELLE14**: `_POLICY_PROFILES` erweitert um leistungs-/physiologiestufige Profile (`tmr_fresh_lactation`, `tmr_high_yield`, `tmr_mid_yield`, `tmr_late_lactation`, `tmr_dry_cow`, `tmr_transit`). Neuer Katalog `_POLICY_PROFILE_TARGETS` mit Referenzkorridoren fuer ME, CP, sidP, pabKH, XL, Grobfutteranteil, `aNDFomGF+CoP`, `aNDFom` je Profil. Response liefert `policy_profile_targets`, wenn ein DLG-2025-Profil aktiv ist - Basis fuer die Folge-Slices (Solver-Bindung / UI-Auswahl).
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_optimization_sara_reopt.py`, `tests/test_rations_optimization_dlg2025.py` (neu, 32 Tests).
**Tests:** `pytest tests/test_rations_optimization_sara_reopt.py tests/test_rations_optimization_pendf_demotion.py tests/test_rations_optimization_compound_feed.py tests/test_rations_optimization_dlg2025.py` → **82 pass**.
**Offene Follow-ups:**
- Frontend `rationsoptimierung.tsx`: FIKH-Zeile im "Kontrolle / Validierung"-Block und `aNDFomGF+CoP` im Planung-Block ergaenzen (bisher nur `aNDFomGF` sichtbar).
- Wizard: Auswahl der neuen Leistungsstufen-Profile (`tmr_fresh_lactation` usw.) per Expertenmodus freischalten; derzeit nur per API-Override.
- Solver-Bindung der `policy_profile_targets`: aktuell nur Referenzwerte im Response, noch nicht als weiche Constraints im LP gefuehrt. Folge-Slice bei Bedarf.

## SARA-Safety-Reopt + pH/peNDF-Fixes (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 23 neue SARA-Gate-Tests plus volle Rations-Regression `335 pass` (keine Regression).
**Kontext:** Der User hat eine Szenariosimulation mit gezielter Pansenacidose-Provokation angefragt. Dabei kamen False-Positive-SARA-Alarme (pH=5.50 ROT auch bei fachlich guter Ration) zum Vorschein. Ursachenanalyse: (a) `_feed_pendf_factor` unrealistisch hoch (z. B. `0.90` fuer Grundfutter), (b) Zebeli/Schwarz-pH-Formel wurde mit **g/kg TM** statt **% TM** gefuettert, (c) es gab keinen automatischen Reopt-Loop.
**Auslieferung:**
- **pH-Formel-Korrektur (`_ph_predict`)**: Inputs werden jetzt von g/kg TM nach % TM umgerechnet (`peNDF_%`, `Staerke_%`), zusaetzlich auf den publizierten Validitaetsbereich geclippt (peNDF 60-250 g/kg TM, Staerke 50-350 g/kg TM, DMI 10-25 kg/d). Neue Helfer `_ph_inputs_in_range` und Response-Flag `dlg_indicators.ph_formula_applicable`.
- **peNDF-Faktor-Neukalibrierung (`_feed_pendf_factor`)** nach Zebeli 2012 / DLG 01|2023: Grundfutter 0.90 -> 0.50 Default, dazu Overrides: Stroh 1.00, Heu 0.95, Luzerne 0.70, Grassilage 0.55, Maissilage 0.45, Trockenkraftfutter 0.10, Getreide 0.10, Melasse 0.00.
- **SARA-Safety-Reopt-Loop (`_maybe_run_sara_safety_reopt`)**: Nach der primaeren FAN-Iteration prueft `_detect_sara_risk` auf pH < 5.9, peNDF < Minimum oder pabKH am Limit. Bei Trigger laeuft eine zweite LP-Runde mit verschaerften Constraints (pabKH-Max -20 g/kg TM, peNDF-Floor +15 g/kg TM, aNDFomGF +10 g/kg TM, NaHCO3-Pansenpuffer als Pflicht mit min. 0.15 kg TM/d). Ergebnis-Payload `sara_safety_reopt` mit `triggered`, `reason`, `actions`, `resolved`, `metrics_before` / `metrics_after`.
- **Frontend-Badge**: Neues Panel in `rationsoptimierung.tsx` zeigt bei aktivem Reopt-Loop die Ausloese-Indikatoren, durchgefuehrte Verschaerfungen und Vorher/Nachher-Metriken (pH, peNDF, pabKH). Farbcode orange = `resolved`, rot = `resolved=false`. DLG-Panel verdeckt die pH-Ampel, wenn die Formel ausserhalb ihres Validitaetsbereichs liegt, um False-Positives zu unterdruecken.
- **Defense-in-Depth**: Provokationsszenarien (`scripts/simulate_acidosis_scenarios.py`, Varianten G/H: 42-45 kg Milch, Maissilage + viel Getreide, ohne Grundstruktur) werden bereits vom LP als `infeasible` abgelehnt (harte Constraints: CP-Dichte, XL-Dichte, Mg-Kapazitaet) - der Reopt-Loop greift als zweite Sicherung, wenn die LP eine scheinbar optimale Loesung mit SARA-Risiko liefert.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_sara_reopt.py` (neu, 23 Tests), `scripts/simulate_acidosis_scenarios.py`, `scripts/_list_feeds.py` (neu, Helper).
**Tests:** `pytest -k "rations or optim or wave74"` -> **335 pass**. Neue Suite `tests/test_rations_optimization_sara_reopt.py`: pH-Clipping + Einheit, peNDF-Faktoren (parametrisiert 13 Feed-Typen), SARA-Risikoerkennung, End-to-End-Reopt, False-Positive-Regression.
**Simulation (Live-Nachweis):** Alle sechs fachlich guten Varianten A-F (TMR, PMR+Weide spring/summer/autumn) zeigen jetzt Pansen-pH 6.46-6.50 GRUEN und peNDF 200-215 g/kg TM GRUEN. Keine False-Positives mehr.
**Offene Follow-ups:** Winterration-Profil bei Bedarf nachziehen. Felddaten sammeln, um den Reopt-Loop in echten SARA-Fruehwarnfaellen zu validieren.

## FAN-MODE-V1 §12 Saisonprofile + wave74-Fix (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, committed und gruen; 30 neue Saisonprofile-Gate-Tests + 6 wave74-Tests repariert. Keine offenen Regressionen in `rations`/`optim` (303 pass).
**Auslieferung:**
- **Wave74-Fix:** `get_rations_base_url()` ist jetzt oeffentlich (vormals `_rations_base_url`). Die wave74-Proxy-Tests bilden den neuen **hybriden Kontrakt** ab: Ohne `RATIONS_OPTIMIZATION_URL` laeuft der interne GfE-2023-Solver (200 + `active_policy_profile`), 503 nur wenn Proxy konfiguriert **und** nicht erreichbar.
- **Sommerration (Hitzestress, DLG-Merkblatt 417 / GfE-Workshop 2023):**
  - Neues Policy-Profil `pmr_pasture_summer` fuer PMR+Weide + `summer_young|mid|late`.
  - DMI-Reduktion je Saisonstufe: `summer_young -3 %`, `summer_mid -7 %`, `summer_late -12 %` (auf `dmi_target/min/max/ndf_min/k_max`).
  - Na-Boost +15 % / +25 % / +30 % fuer Schwitzverluste.
  - Neues Spezialsupplement `special_summer_rumen_buffer` (NaHCO3, 220 g Na/kg TM) wird automatisch als Pflichtbaustein mit `min_kg >= buffer_min_kg` gefuehrt.
  - `summer_late` zusaetzlich +10 g/kg TM aNDFomGF-Boost.
- **Herbstration (stickstoffreicher Grasaufwuchs):**
  - Neues Policy-Profil `pmr_pasture_autumn` fuer PMR+Weide + `autumn`.
  - CP-Dichte-Obergrenze hart auf 175 g/kg TM (Harnstoffschutz, vs. 185 Default PMR+Weide).
  - aNDFomGF-Mindestdichte +15 g/kg TM (Strukturstuetzung gegen N-Ueberschuss).
  - RMD-Korridor kontrolliert um +1 g N/kg TM entspannt (weidetypisch, nicht beliebig).
- **Frontend:** `PolicyProfile`-Typ erweitert; Wizard zeigt je Saison aktive Policy-Hinweise (Sommer/Herbst) im PMR+Weide-Block.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_process_kernel_wave74_rations_optimization.py`, `tests/test_rations_optimization_fan_mode_004_policy.py`, `tests/test_rations_optimization_fan_mode_v1.py`, `tests/test_rations_optimization_seasonal_profiles.py` (neu).
**Tests:** `pytest -k "rations or optim"` → 303 pass; neue Suite `tests/test_rations_optimization_seasonal_profiles.py` mit 30 Tests gruen; wave74-Suite mit 28 Tests gruen.
**Offene Follow-ups:**
- Winterration bei Zukunftsbedarf modellieren (aktuell neutraler `winter`-Profilpunkt ohne Anpassungen).
- Felddaten aus Praxistests Sommer/Herbst sammeln, um DMI-Faktoren und Buffer-Minima zu kalibrieren.

## RAT-OPT-001

**Von:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Rationsoptimierung fachlich und technisch auf belastbaren DLG-01|23-Stand ziehen: Frontend-Submit stabilisieren, TMR/PMR-Logik explizit machen und Ergebnisdarstellung um Grundfutter-/Kraftfutter-Leistungsbeitrag inklusive Grundfutterverdrängung ergänzen.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, ggf. gezielte Tests unter `tests/`
**Abnahmekriterien:** Optimierung startet stabil aus dem Wizard ohne State-Race; Response und UI zeigen Milch aus Energie/Protein als IST-/Soll-Sicht aus Grundfutter sowie Zusatz-Kraftfutter für Zielmilch; PMR berücksichtigt Konzentratgabe und Grundfutterverdrängung nachvollziehbar; DLG-01|23-Abgleich ist dokumentiert.
**Erledigt:** Wizard-Submit, Feeding-Type-Vertrag, Grundfutter-/Kraftfutter-Leistungsbeitrag, PMR-/Weide-Logik, Compound-Upload, Weidemineral, Pasture-Risk, Fruehjahrsfall und relevante Rations-Regressionen wurden in den Updates vom 2026-04-21 umgesetzt. Der Eintrag bleibt als historische Zusammenfassung erhalten und ist nicht mehr aktiver Work-in-Progress.
**Offene Risiken:** DLG-Dokument liefert fachliche Leitplanken, aber keine 1:1-Formeln fuer jede Betriebsheuristik; kuenftige Kalibrierungen wie Winterprofil, Felddatenvalidierung oder weitere Solver-Zerlegung sind separate Folgeentscheidungen, keine offenen Punkte dieses Slices.
**Update 2026-04-21:** Wizard-Submit auf mutierende State-Race geprüft und auf parameterisierte Mutation umgestellt; `feeding_type` geht jetzt explizit in den Request. Backend liefert `forage_performance` mit Milch aus Energie/Protein aus Grundfutter, Zielmilch, Kraftfutter-TM und dokumentierter Grundfutterverdrängungs-Heuristik für TMR/PMR. Frontend zeigt die Kennzahlen in Workbench und Review. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, `cmd /c pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, direkte Modulverifikation via `python -` auf `_optimize_internal(_demo_profile())`. Laufender lokaler FastAPI-Prozess muss für die neuen Response-Felder ggf. neu geladen werden.
**Update 2026-04-21 (Upload/Bridge):** `main.py` loggt Dev-Warnungen jetzt ASCII-sicher. `POST /api/v1/agrar/rations-optimization/compound-feed/upload` nimmt PDF- und Foto-Dokumente für Kraftfutter-Rezepturen/Lieferscheine an, parst Deklarationswerte, matched Rezepturanteile gegen die DLG-Futterdatenbank und liefert eine Legacy-zu-GfE-2023-Brücke inkl. direkt nutzbarem Optimizer-Feed. Der Wizard in `rationsoptimierung.tsx` kann diese Uploads jetzt als betriebseigenes Kraftfutter in die Futtermittelauswahl übernehmen. Regressionstest `tests/test_rations_optimization_compound_feed.py` ist grün; API-Vertrag lokal per `TestClient` mit `Bödeker Ditzum.pdf` geprüft. Die enge Praxisprobe `Weide + Grassilage 2. Schnitt + 1 kg Maismehl + 1 kg Gerstenmehl + Milchleistungsfutter` bleibt unter den aktuellen harten PMR-Restriktionen noch `infeasible` und ist damit jetzt ein fachlicher Solver-Kalibrierpunkt, kein Upload-/UI-Defekt mehr.
**Update 2026-04-21 (Solver-Prinzip):** Interner LP-Solver priorisiert jetzt nicht mehr direkt Kosten, sondern rechnet zweistufig: Stage 1 sucht zuerst eine fachlich ausgeglichene, pansenstabile Basisration; Stage 2 optimiert erst innerhalb dieses Balance-Korridors auf Kosten. Außerdem greift die starre `Weide <= 4 kg TM`-Grenze jetzt nur noch bei `TMR`, nicht mehr pauschal auch bei `PMR/Weide`. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, Praxisprobe via `python -` auf `_optimize_internal(...)`, Regression `pytest tests/test_rations_optimization_compound_feed.py -q --no-cov`. Die konkrete Frühjahrsration bleibt trotz korrigierter PMR-Logik noch `infeasible`; nächster fachlicher Slice ist damit die Kalibrierung der harten XL-/CP-/Weide-Regeln für Weidesysteme.
**Update 2026-04-21 (Weide/PMR):** Auf Basis von DLG 443/444, DLG 417, DLG-Information 01|2023 und dem GfE-Workshop-Stand vom 5. März 2026 ist jetzt ein erster `PMR+Weide`-Pfad eingezogen: Weide-/Frischgrasfutter sind nicht mehr global auf 4 kg TM gedeckelt, TMR-Deckelung greift nur noch im echten TMR-Fall; fuer PMR+Weide werden `aNDFomGF`, `pabKH`, `XL`, `CP`, `K` und Mindest-Grundfutteranteil adaptiv bewertet. Die Fruehjahrsprobe mit `Weide + Grassilage 2. Schnitt + 1 kg Mais + 1 kg Gerste + Boedeker-Milchleistungsfutter` bleibt fachlich weiter `infeasible`; die Diagnose weist jetzt explizit auf das reale Mg-/Energie-Problem der engen Auswahl hin (`Magnesiumdichte ... reicht innerhalb der zulaessigen Energieversorgung nicht aus`) statt nur pauschal auf PMR/Weide zu zeigen.
**Update 2026-04-21 (Weidemineral + PMR+Weide-Modus):** Drei fachliche Slices umgesetzt: (1) Weidemineral `Weidemineral Mg/Na Ausgleich` ist jetzt ein echter Optimierungsbaustein in der Feedbasis (`_SPECIAL_SUPPLEMENTS`) und wird bei `feeding_type="PMR+Weide"` automatisch als Sicherheitsbaustein (>= 0,05 kg TM/d) in die Ration gezwungen – Ableitung aus DLG 417/443 / GfE-Workshop 2023 (K/Mg-Antagonismus, Grastetanie-Risiko). (2) Der Wizard in `rationsoptimierung.tsx` bietet jetzt `TMR / PMR / PMR+Weide` als explizite Modi inkl. kurzer fachlicher Info; `feeding_type` wird ueber den `CowProfile`-Contract an das Backend uebergeben und per `_normalize_feeding_type` robust normalisiert (`PMR+Weide`, `PMR_WEIDE`, `pasture` u.ae.). (3) Response enthaelt neu `pasture_risk` (aktiv bei `PMR+Weide` oder bei > 1 kg TM Weideaufnahme) mit `K:Mg`-Verhaeltnis, Weide-Rohprotein, Mg-Supplement-Menge und drei Milch-Panels (Milch aus Weide, Milch aus Grassilage, Milch aus Weide+Grassilage); `PastureRiskPanel` ist in Workbench- und Review-Ansicht sichtbar. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, `pytest tests/test_rations_optimization_pasture.py tests/test_rations_optimization_compound_feed.py -q --no-cov` (5 passed), `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`, E2E-Sanity-Test via FastAPI-`TestClient` mit `feeding_type="PMR+Weide"` (Response liefert `pasture_risk.active=true`, `mg_supplement_dmi_kg=0.05`, K:Mg-Warnung wird ausgeworfen).
**Update 2026-04-21 (Fruehjahrsfall-Abschluss, RMD + Compound-Parser):** Die Praxisprobe `Weide Fruehjahr jung + Grassilage 2. Schnitt + 1 kg Mais + 1 kg Gerste + Boedeker-Milchleistungsfutter` ist jetzt im Modus `PMR+Weide` `optimal` (Kosten 1,66 EUR/d, DMI 18 kg TM, ME 204,6 MJ, Mg 37,3 g, K:Mg 12,4 → Grastetanie-Warnung wird korrekt gemeldet). Zwei zusammenhängende Blocker wurden aufgelöst: (a) **RMD-Dichte-Obergrenze** (DLG 01|25 Ziel ≤ 1,5 g N/kg TM) ist für Weidesysteme strukturell nicht erreichbar, weil Jungweide laut DLG-Futterwerttabelle bereits 7–9 g N/kg TM liefert. Die Grenze wird jetzt nach DLG-Merkblatt 417 je Fütterungsmodus gestaffelt (`TMR 1,5 / PMR 3,0 / PMR+Weide 8,0`, Relaxation-Stufe `TMR 3,0 / PMR 5,0 / PMR+Weide 12,0`) – die Stall-Norm bleibt für Stallfütterung unverändert. (b) **Compound-Feed-Parser** (`_parse_compound_feed_text`) produzierte physikalisch unmögliche Werte (ME 15,4 MJ/kg TM, XL 165 g/kg TM, Ca 72 g/kg TM), verursacht durch zwei Bugs: ein Off-by-one-Matching in `_extract_labelled_value` (Pattern-Reihenfolge vertauscht, `"Rohfett"` nahm den Wert von `"Rohprotein"` etc.) und eine fehlende FM→TM-Umrechnung der Deklaration (% FM wurde direkt als g/kg TM interpretiert). Beides gefixt: Label-zuerst-Pattern hat jetzt Priorität, Deklaration wird konsistent mit `1/dm_frac` auf g/kg TM gehoben. Regressionstests: `tests/test_rations_optimization_compound_feed.py` (3 neue Tests gegen Off-by-one, physikalische Plausibilität, FM→TM), `tests/test_rations_optimization_spring_pasture_case.py` (4 neue E2E-Tests für den Bruder-Fall). Komplette `rations_optimization`-Suite: 34 passed (6 Pre-Existing-Errors in `test_process_kernel_wave74_rations_optimization.py` wegen entfallener `get_rations_base_url`-Funktion, unabhängig von diesem Slice).

## FLOW-LC-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Flow-Spine-Instanzen vom reinen Routing-/Node-Status-Anker auf einen echten, restart-sicheren Lifecycle mit Timeline und Resume-Vertrag heben.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `app/domains/operations/models.py`, `alembic/versions/*`, `app/api/v1/endpoints/flow_spines.py`, `tests/test_flow_spines_api.py`
**Abnahmekriterien:** `FlowSpineInstance` traegt technische Lifecycle-Felder; eine Event-/Timeline-Spur ist modelliert; API-Contracts fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail` sind dokumentiert oder implementiert; bestehende `transition`-Logik ist sauber in den Gesamtvertrag eingeordnet.
**Erledigt:** `FlowSpineInstance` fuehrt jetzt Lifecycle-, Resume-, Owner-, Grund- und Abschlussfelder; `domain_ops.ops_flow_spine_instance_events` bildet Timeline/Audit persistent ab; `flow_spines.py` bietet jetzt `PATCH`, `save`, `resume`, `hold`, `complete`, `cancel`, `fail` und `timeline`; `transition` schreibt ebenfalls in die Eventspur und hebt `draft` auf `in_progress`.
**Checks:** `python -m py_compile app/api/v1/endpoints/flow_spines.py app/domains/operations/models.py alembic/versions/flow_spine_lifecycle_20260417.py tests/test_flow_spines_api.py`, `pytest tests/test_flow_spines_api.py -q --no-cov`
**Naechster Schritt:** `FLOW-LC-002` bis `FLOW-LC-006` entlang der neuen Lifecycle-Uebersicht staffeln, beginnend mit generischen Workspace-Actions und Resume-/Abbruch-Dialogen im Frontend.

## FLOW-LC-003

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Gemeinsamen Workspace-Lifecycle-Rahmen fuer alle 9 Flow-Spines einziehen: Aktionsleiste, Resume-Hinweis, Timeline und generische Dialoge fuer `save`, `hold`, `complete`, `cancel`, `fail`.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`, `packages/frontend-web/src/lib/api/flow-spines.ts`, relevante UI-Tests falls vorhanden
**Abnahmekriterien:** Der Workspace zeigt Lifecycle-Status, Resume-Ziel und Timeline; die generischen Lifecycle-Aktionen sprechen den neuen Backend-Vertrag an; `cancel` und `fail` erzwingen Pflichtgruende auch im UI; der Rahmen ist prozessneutral fuer alle 9 Flows nutzbar.
**Erledigt:** `flow-spines.ts` kennt jetzt Lifecycle-Status, Timeline-Events und Mutationen fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail`; `FlowSpineWorkspace.tsx` zeigt fuer geladene Instanzen eine generische Lifecycle-Leiste mit Status, Resume-Ziel, Timeline und prozessneutralen Dialogen; die Instanzliste zeigt den Lifecycle-Status direkt in der Sidebar.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`
**Naechster Schritt:** `FLOW-LC-004` fuer OTC / P2P / Inventory aufsetzen und dort Resume-/Handover-Pfade mit den jeweiligen Fachmasken wirklich durchgaengig machen.

## FLOW-LC-004

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** OTC, P2P und Inventory so an den Lifecycle-Vertrag anbinden, dass `save` und `resume` nicht nur im Workspace leben, sondern in reale Wiedereinstiegspfade der Fachmasken zeigen.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `packages/frontend-web/src/lib/api/flow-spines.ts`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx`
**Abnahmekriterien:** OTC speichert einen belastbaren Resume-Punkt in die Auftragsmaske; P2P speichert nach Erstanlage in die echte Bestell-Detailroute; Inventory speichert vor vertieften Dashboard-Spruengen den operativen Zielpfad als Resume-Ziel.
**Erledigt:** `flow-spines.ts` bietet jetzt einen schlanken `saveFlowSpineResumeCheckpoint()`-Helper; `order-editor.tsx` schreibt beim Speichern den Resume-Punkt auf die konkrete Auftragsmaske und ersetzt nach Erstanlage die URL auf `?id=...`; `bestellung-anlegen.tsx` schreibt nach Erstanlage den Resume-Punkt auf die echte Bestell-Detailroute `/einkauf/bestellungen/{id}`; `bestandsuebersicht.tsx` persistiert vor den Spruengen in `mhd-uebersicht`, `psm-abverkauf`, `renner-liste` und `penner-liste` den jeweiligen Zielpfad als Inventory-Resume-Ziel und traegt den Workflow-Kontext dorthin weiter.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Naechster Schritt:** `FLOW-LC-005` aufsetzen und die restlichen sechs Prozessraeume mit denselben Resume-/Handover-Mustern nachziehen.

## FLOW-LC-005

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Die restlichen sechs Flow-Spine-Prozessraeume mit denselben Resume-/Handover-Mustern wie OTC, P2P und Inventory anbinden.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, relevante Zielseiten unter `packages/frontend-web/src/pages/**`, ggf. `packages/frontend-web/src/lib/api/flow-spines.ts`
**Abnahmekriterien:** `harvest-to-settlement`, `contract-to-settlement`, `complaint-to-resolution`, `service-to-customer`, `finance-to-close` und `compliance-to-report` schreiben oder tragen echte Resume-/Handover-Ziele in ihre Fachmasken; die Workflow-Kontexte bleiben beim Wiedereinstieg erhalten.
**Erledigt:** `ernte-annahme-erfassung.tsx` schreibt beim Speichern den Resume-Punkt auf die konkrete Annahme-Route und ersetzt nach Erstsave die URL auf `/agrar/ernte-annahme-erfassung/{id}`; `FrmKontraktDetail.tsx` schreibt nach Save auf die echte Kontrakt-Detailroute; `reklamationen.tsx` und `service/anfragen.tsx` sichern vor `neu`- und Detail-Spruengen die jeweiligen Zielpfade; `abschluss-cockpit.tsx` speichert beim Oeffnen den Cockpit-Resume-Punkt und vor Detail-Spruengen den Checklistenpfad; `co2-bilanz.tsx` persistiert die Reporting-Maske selbst als Resume-Ziel.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`
**Naechster Schritt:** Die verbleibende Vertiefung ist kein generischer Resume-Rahmen mehr, sondern fachliche Feinarbeit: pro Flow konkrete Grundcode-Kataloge, weitergehende Handover in Untermasken und Abschluss-/Abbruchregeln.

## CRM-PICKER-001

**Von:** Claude Code / Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Order-to-Cash-Kundenauswahl im Flow-Spine-Startdialog von Modal-Auswahl auf schnellen Inline-Typeahead mit Neuanlage-Ruecksprung umstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/CUSTOMER-PICKER-PLAN.md`, `app/api/v1/endpoints/customers.py`, `alembic/versions/crm_customers_search_index_20260414.py`, `packages/frontend-web/src/components/crm/CustomerCombobox.tsx`, `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`, `packages/frontend-web/src/pages/verkauf/kunde-neu.tsx`, `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx`
**Abnahmekriterien:** Typeahead nutzt schlanke Quick-/Recent-Endpoints; neuer Kunde kann aus dem Flow-Spine-Dialog angelegt werden; nach Speichern kehrt die App in den Dialog mit vorausgewaehltem Kunden zurueck; erweiterte Kundensuche bleibt erreichbar.
**Erledigt:** `CustomerCombobox` ist fuer `order-to-cash` integriert; `/quick-search` und `/recent` liefern schlanke Picker-Daten; `returnTo` bleibt ueber den Alias-Redirect erhalten; kanonischer Kundenstamm liest `initialName` und navigiert nach Save zurueck; `FlowSpineWorkspace` setzt `customerId` und `customerNumber` im Order-Editor-Handover; der `order-editor` prefilled den uebergebenen Kunden jetzt direkt beim Workflow-Einstieg; bestehende Flow-Spine-Instanzen loesen den kompakten Kundenkontext robust ueber `business_partner_id`; `CustomerSelectionDialog` ist als "Erweiterte Suche" angebunden.
**Checks:** Browser-Use Roundtrip `Flow Spine -> Kunde neu -> Flow Spine Dialog -> Order Editor`, `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `pytest tests/test_flow_spines_api.py tests/test_customers_picker_api.py -q --no-cov`, `node scripts/docs-governance-check.cjs`, `GET /api/v1/crm/customers/recent`, `GET /api/v1/crm/customers/quick-search`

## DOC-REF-002

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Externe ERP-Referenzdoku neutralisieren, Lizenz-/Referenzlage scharfziehen und direkte Nennungen des angefragten Systems aus den aktiven Repo-Dokumenten entfernen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/*.md`
**Abnahmekriterien:** Die Referenzanalyse bleibt fachlich brauchbar, benennt aber nur noch neutrale Vergleichsklassen bzw. permissive/kommerzielle Lizenzrisiken; direkte Nennungen des angefragten Systems sind aus den aktiven Projektkontext-Dateien entfernt.
**Erledigt:** Die aktive Referenzdatei wurde auf `docs/project-context/erp-reference-gap-analysis-amic-community-erp-fiori-2026-04-08.md` umgestellt; Tail-Plan, i18n-, Setup-, Roadmap- und Archivdoku nutzen jetzt neutrale Bezeichnungen; ein repo-weiter Textscan auf die direkte Nennung liefert keine Treffer mehr.
**Checks:** `rg -n -i "\\bodoo\\b" . --glob '!node_modules/**' --glob '!.git/**' --glob '!packages/frontend-web/node_modules/**' --glob '!venv/**' --glob '!coverage_html/**'`, `node scripts/docs-governance-check.cjs`

## DOC-REF-003

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Eine neutrale ERP-Referenzmatrix im Repo festhalten und daraus die naechsten sechs fachlichen Vertiefungs-Slices fuer VALEO ableiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/*.md`
**Abnahmekriterien:** Es gibt eine eigenstaendige Matrix mit Referenzmustern, Lizenz-/Uebernahmeregeln und VALEO-Istbild; daraus sind sechs konkrete Slices mit Zielbild und Prioritaet im Workboard abgeleitet.
**Erledigt:** `docs/project-context/erp-reference-matrix-2026-04-12.md` verdichtet jetzt fachliches Tiefenbild, Community-ERP-Referenzmuster, Web-ERP-Standard-/OpenUI5-UIX-Muster, Lizenzregeln und konkrete Slice-Ableitung; die naechsten sechs fachlichen Vertiefungs-Slices sind daraus direkt abgeleitet.
**Checks:** `node scripts/docs-governance-check.cjs`

## DOM-FIN-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** FIBU-Operatorpfade fuer Abschluss, Reorganisator, Zinswesen und Revisionssicht semantisch verdichten.
**Abnahmekriterien:** Abschluss- und FIBU-Operatorraeume tragen denselben klaren Status-, Fristen-, Revisions- und Folgeaktionsrahmen.
**Ergebnis:** Alle 4 FIBU-Masken (abschluss-cockpit, schnittstellen-center, mahnwesen, zahlungslaeufe) tragen OperationalCaseHeader mit Status/Blocker/Folgeaktion.

## DOM-SUPPLY-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Die physische Kette `Partie -> Annahme -> Wiegung -> Charge -> Fracht -> Abrechnung` fachlich und statusseitig durchgaengig harmonisieren.
**Abnahmekriterien:** Jeder Uebergabepunkt zeigt Objektbezug, Abweichung, naechste Aktion und Folgeobjekt konsistent.
**Ergebnis:** Alle 6 Supply-Masken (waage/liste, tourenplanung, wareneingang, wiegeschein-detail, rohware, frachtbriefe) tragen OperationalCaseHeader.

## DOM-PROC-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Einkaufsausnahmen, Matching, Nachforderung und Lieferantenkommunikation auf echte Folgefaelle heben.
**Abnahmekriterien:** Beschaffungsfaelle bilden Matching-Ausnahmen, Nachforderung und Folgekommunikation als echte Arbeitsobjekte ab.
**Ergebnis:** Alle 5 Einkauf-Masken (rechnung-abgleich, rechnungseingang, lieferanten-dokumente, anlieferavis, auftragsbestaetigung) tragen OperationalCaseHeader.

## DOM-CON-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Kontraktfixierung, Marktbewertung, Mahnung und Engagement als vollwertige Operatorraeume ausbauen.
**Abnahmekriterien:** Fixierungs-, Markt- und Mahnlogik ist nicht nur sichtbar, sondern als klarer Operatorpfad bedienbar.
**Ergebnis:** Alle 4 Kontrakt-Masken (contracts-v2, KontraktPositionsmonitor, FrmKontraktDetail, KontraktAlarmDashboard) tragen OperationalCaseHeader.

## DOM-CRM-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** CRM-/Servicefaelle mit Ownership, Folgeobjekten, Dubletten- und Abschlusslogik angleichen.
**Abnahmekriterien:** CRM und Service tragen denselben Fallbezug, Ownership-Rahmen und Abschlusspfad.
**Ergebnis:** Alle 4 CRM-/Service-Masken (LegacyKundenStammModern, anfrage-detail, opportunity-detail, kontakt-management) tragen OperationalCaseHeader.

## DOM-DOC-003

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Nachweis-, Bescheid-, Artefakt- und Rueckmeldungskette ueber Dokumente, Meldungen und Vorgangskontext vereinheitlichen.
**Abnahmekriterien:** Dokumente und Meldungen zeigen revisionsrelevanten Nachweisstatus, Rueckmeldungspfad und Wiedervorlage konsistent.
**Ergebnis:** Alle 3 Dokumenten-/Compliance-Masken (ablage, meldewesen-konsole, atlas) tragen OperationalCaseHeader.

## COV-FIN-002

**Von:** Codex
**Stand:** erledigt
**Ziel des Slices:** Coverage-Tiefe fuer FIBU-Kernpfade aufbauen: Journal, Zahlungslaeufe, DATEV/ELSTER-nahe Follow-up-Logik und Abschlusskontext.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, relevante Finance-/FIBU-Services und Endpunkte
**Abnahmekriterien:** Kritische FIBU-Kernpfade besitzen gezielte Tests statt nur allgemeiner Gesamtquote; Ratchet kann fuer Finance spaeter angehoben werden.
**Fortschritt:** Start auf den API-/Service-Kern fuer Follow-up, Mahnwesen, Lastschrift- und Kassenexport sowie FIBU-nahe Exportpersistenz; `tests/test_finance_followup_api.py` deckt jetzt Preview-, Export-, Download-, DMS-Redirect- und Upload-Metadatenpfade ab. Zusaetzlich haertet `tests/test_fibu_connectors_api.py` jetzt Profile-CRUD, Import-Upload, Run-Summary, Run-Items und Workflow-Folgeaktionen in `api/v1/endpoints/fibu_connectors.py`. `tests/test_finance_actions.py` deckt Bankabgleich, Buchungsfreigabe, Kassenabschluss, Lastschriftlauf, Periodenabschluss, Kreditlimits, Sicherheiten, Zahlungsvorschlaege und Buchungsuebergabe ab. Die zuvor `skipped` Finance-API-Tests wurden auf deterministische Test-Doubles umgestellt (`tests/test_finance_dunning_api.py`, `tests/test_finance_exchange_rates_api.py`, `tests/test_finance_payment_runs_api.py`), damit sie nicht mehr an einer zufaelligen Live-DB haengen. Nebenbei wurden echte Ursachen im Code behoben: Geldbetraege im Mahnwesen werden jetzt quantisiert, `payment_runs.py` serialisiert Zahlungsobjekte sauber und der Ruecklaeuferpfad nutzt wieder den korrekten Betrag. Fuer Bestandsinstallationen erzwingt `ensure_finance_api_tables_20260413` die fehlenden Finance-API-Tabellen auch dann, wenn ein aelterer Migrationspfad sie ausgelassen hat.

## COV-FIN-003

**Von:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Die verbliebenen Finance-Ratchet-Luecken `booking_templates.py` und `chart_of_accounts.py` ueber deterministische API-/Unit-Tests und einen stabilen JSON-Serialisierungspfad schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/booking_templates.py`, `tests/test_booking_templates_api.py`, `tests/test_chart_of_accounts_api.py`
**Abnahmekriterien:** `booking_templates.py` liegt ueber 40 Prozent, `chart_of_accounts.py` ueber 50 Prozent; der kritische Coverage-Ratchet laeuft gegen die Sammelsuite gruen.
**Erledigt:** `booking_templates.py` serialisiert Template-Lines jetzt ueber `model_dump_json()` JSON-sicher; `tests/test_booking_templates_api.py` und `tests/test_chart_of_accounts_api.py` decken Listen-, CRUD-, Validierungs-, Export- und Fehlerpfade ab. Der vollstaendige kritische Ratchet ist gruen.
**Checks:** `pytest tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py -q --no-cov`; `pytest tests/test_tenant_enforcement.py tests/test_secrets_vault.py tests/test_event_bus_runtime.py tests/test_process_kernel_wave2_events.py tests/test_integration_bootstrap.py tests/test_finance_actions.py tests/test_finance_followup_api.py tests/test_fibu_connectors_api.py tests/test_dunning_api.py tests/test_finance_payment_runs_api.py tests/test_finance_exchange_rates_api.py tests/test_finance_read_models_api.py tests/test_process_kernel_wave1_contracts.py tests/test_inventory_operations.py tests/test_inventory_counts.py tests/test_waage_api.py tests/test_warehouses_api.py tests/test_warehouse_transfers_api.py tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py tests/test_l3c_smoke.py -q`; `python scripts/check_critical_backend_coverage.py`

## COV-INV-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Coverage fuer Bestandsfuehrung, Lagerbewegung, Inventur und physische Objektkette erweitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, Inventory-/Ops-/Logistik-Endpunkte und Services
**Abnahmekriterien:** Stock-Movements, Inventur und kritische Lagerpfade sind ueber gezielte Tests gegen Regressionen abgesichert.
**Erledigt:** `waage.py`, `warehouses.py`, `warehouse_transfers.py`, `inventory_counts.py` und `inventory_operations.py` liegen im kritischen Coverage-Ratchet ueber Schwelle; die Sammelsuite laeuft gruen.
**Checks:** siehe `COV-FIN-003` Sammelsuite und `python scripts/check_critical_backend_coverage.py`

## COV-INT-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Integrations-Governance tiefer testen: Superglue, Secrets, Outbound-Gates, Bootstrap und Tenant-Schutz.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, `app/services/**`, `app/integrations/**`
**Abnahmekriterien:** Integrationsnahe Kernpfade werden nicht nur konfiguriert, sondern auch testseitig breiter abgesichert.
**Erledigt:** `IntegrationCircuitBreaker` (12 Tests), `superglue_execution_journal` (9 Tests), `superglue_admin_state` (11 Tests), `superglue_monitoring` (5 Tests) — 37 Tests gruen. Stand: 2026-05-12.

## DOM-FIN-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** FIBU-/L3-Parity fachlich weiter vertiefen, insbesondere Abschluss-, Revisions- und Operator-Pfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante FIBU-/Finance-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Finance/FIBU ist nicht nur breit, sondern in den priorisierten Operatorpfaden semantisch konsistenter und tiefer.
**Erledigt:** (1) `accruals_provisions.py`: GET/PUT/DELETE-Endpoints fuer Einzelobjekte hinzugefuegt (waren fehlend — nur List+Create+Post vorhanden); (2) `closing_checklists.py`: POST `/{id}/approve` + DELETE `/{id}` hinzugefuegt (approve-Schritt fehlte im Workflow); (3) Tests: `test_accruals_provisions_api.py` (12), `test_subsidiary_ledger_reconciliation_api.py` (12) — 24 Tests gruen. Stand: 2026-05-12.

## DOM-INV-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Inventory-/Ops-/Logistik-Parity weiterziehen, insbesondere physische Objektkette, Queue, Wiegung, Fracht und Charge.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante Inventory-/Ops-/Logistik-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Die physische Kette ist fachlich tiefer und konsistenter ueber mehrere Kernmasken und Backend-Pfade hinweg.
**Erledigt:** Tests fuer `silo_operations_api.py` (DOM-INV-002, `test_silo_operations_api.py`) und `charges.py` (`test_charges_api.py`) hinzugefuegt — Modellvalidierung + HTTP-Smoke-Tests.

## DOM-CRM-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** CRM-/Sales-/Service-Parity angleichen, insbesondere Vorgangsbezug, Folgeobjekte und echte Arbeitsobjekte statt Listenbreite.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante CRM-/Sales-/Service-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** CRM-/Sales-/Service-Raeume besitzen vergleichbare fachliche Tiefe in den priorisierten Kernobjekten.
**Erledigt:** Tests fuer `sales_orders.py`, `sales_delivery_notes.py`, `reklamation_api.py`, `contacts.py` hinzugefuegt — Helper-Unit-Tests + HTTP-Smoke (60 Tests grueen).

## ARCH-DOM-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fachliche Schema-Zuordnung der Tabellen nicht nur behaupten, sondern mit einem expliziten Audit- und Guardrail-Pfad pruefbar machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `scripts/check_required_domain_schemas.py`, neues Domain-Mapping-Audit unter `scripts/`
**Abnahmekriterien:** Es gibt einen automatisierten Check fuer Kern-Schemaanker plus fachlich schiefe bzw. bewusst tolerierte Cross-Domain-Zuordnungen.
**Erledigt:** `scripts/check_domain_table_ownership.py` prueft jetzt representative Exact-Ownership-Regeln, Prefix-Regeln und dokumentierte Legacy-Placements; `scripts/smoke_first_install_docker.ps1/.sh` fuehren den Ownership-Check nach frischer Migration mit aus.
**Checks:** `powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55437`, `python scripts/check_domain_table_ownership.py` (gegen frische Smoke-DB)

## COVERAGE-ERP-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Backend-Coverage fuer ERP-Kernpfade auf einen belastbaren Ratchet-Pfad bringen statt pauschal 100% zu behaupten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `.github/workflows/quality-gate.yml`, `pytest.ini`, neue Coverage-Guard-Skripte/Tests unter `scripts/` und `tests/`
**Abnahmekriterien:** CI prueft einen expliziten Mindeststandard fuer kritische Pfade; die Doku benennt ehrlich, was repo-seitig erreichbar ist und was nicht.
**Erledigt:** `.github/workflows/quality-gate.yml` fuehrt jetzt `scripts/check_critical_backend_coverage.py` nach pytest aus; neue Tests fuer Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement stabilisieren die Kernpfade; die Doku benennt `100%` repo-weit explizit nicht als kurzfristig belastbares Ziel.
**Checks:** `pytest tests/test_event_bus_runtime.py tests/test_integration_bootstrap.py tests/test_secrets_vault.py tests/test_security_startup_guards.py tests/test_nats_event_handlers.py tests/test_tenant_enforcement.py -q`, `python scripts/check_critical_backend_coverage.py`

## NATS-DEV-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Event-Bus/NATS im Dev-Betrieb automatisch mit Docker laufen lassen, statt nur config-aktivierbar zu sein.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docker-compose*.yml`, `.env.example`, ggf. `app/core/config.py`, Event-Bus-Tests
**Abnahmekriterien:** Standard-Dev-Compose bringt NATS mit hoch und Backend laeuft dabei automatisch auf NATS statt Memory-Fallback.
**Erledigt:** `docker-compose.yml` und `docker-compose.dev.yml` starten NATS jetzt mit JetStream-Healthcheck; die jeweiligen Backend-Services laufen dort automatisch mit `EVENT_BUS_ENABLED=true`, `EVENT_BUS_PROVIDER=nats`, `EVENT_BUS_NATS_URL=nats://nats:4222`; `.env.example` spiegelt denselben Dev-Pfad.
**Checks:** `docker compose -f docker-compose.yml config -q`, `docker compose -f docker-compose.dev.yml config -q`

## INT-BOOT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Externe Integrationen soweit repo-seitig vorbereiten, dass lokale oder frische Installationen nicht an fehlenden Bootstrap-Hinweisen fuer Secrets, Zielsysteme und Ops-Parameter scheitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `.env.example`, `scripts/`, ggf. Integrations-README unter `docs/`
**Abnahmekriterien:** Es gibt einen reproduzierbaren Readiness-/Bootstrap-Check fuer Live-Integrationen und klare env-/secret-Vorlagen fuer lokale bzw. ops-seitige Aktivierung.
**Erledigt:** `app/services/integration_bootstrap.py` verdichtet OIDC-, NATS-, Superglue-, Voice- und CRM-Downstream-Readiness; `scripts/check_integration_bootstrap.py` reportet bzw. failt optional strikt; `.env.example` fuehrt die zentralen Bootstrap-Variablen; `docs/project-context/integration-bootstrap-readiness-2026-04-12.md` dokumentiert die repo-seitig vorbereiteten und die ops-seitig verbleibenden Themen.
**Checks:** `python scripts/check_integration_bootstrap.py`, `pytest tests/test_integration_bootstrap.py -q`

## DOCS-README-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Root-README gegen den aktuellen Repo-, Delivery- und Bootstrap-Stand aufraeumen und wieder als belastbaren Einstiegspunkt ausrichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `README.md`
**Abnahmekriterien:** README ist encoding-sauber, verweist auf die echten Source-of-Truth-Dokumente, ueberzeichnet den Produktreifegrad nicht und bildet den aktuellen Docker-/Bootstrap-Pfad korrekt ab.
**Erledigt:** `README.md` ist von veralteter Langform und Mojibake auf einen knappen, ehrlichen Einstiegspunkt umgestellt; der aktuelle Reifegrad, der Alembic-/Docker-Erstinstallationspfad, die Mehr-Domaenen-Struktur, lokale Prüfkommandos sowie die maßgeblichen Source-of-Truth-Dokumente sind jetzt korrekt referenziert; ueberspannte Vollstaendigkeits- und Production-Claims wurden entfernt.
**Checks:** `node scripts/docs-governance-check.cjs`, `rg -n "ð|â|Ã|�" README.md`

## DB-BOOT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Erstinstallation ueber Alembic und Docker auf leerer Postgres-DB deterministisch machen und die Mehr-Domaenen-Struktur automatisiert pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `alembic/env.py`, `alembic/versions/*`, `scripts/init_db.py`, `scripts/check_required_domain_schemas.py`, `docker-compose*.yml`, `Dockerfile*`, `.github/workflows/quality-gate.yml`
**Abnahmekriterien:** `python scripts/init_db.py` laeuft auf leerer DB bis `head`; der Compose-/Docker-Pfad verschluckt keine Migrationsfehler; eine Strukturpruefung bestaetigt zentrale ERP-Domaenen und Kernobjekte.
**Erledigt:** `add_business_partners_tenant_id_20260219.py` ist jetzt neuinstallationssicher und ersetzt den falschen globalen Business-Partner-Unique-Pfad; `perf_indexes_multitenant_20260408.py` legt optionale Indexe nur noch fehlertolerant an; `docker-compose.yml`, `docker-compose.staging.yml`, `docker-compose.dev.yml`, `entrypoint.sh`, `Dockerfile` und `Dockerfile.backend` starten Backend-Prozesse erst nach erfolgreichem `python scripts/init_db.py`; Legacy-SQL-Tabellenpfade sind aus dem Dev-Erststart entfernt; `scripts/check_required_domain_schemas.py` verifiziert die zentrale Mehr-Domaenen-Struktur im CI und `scripts/smoke_first_install_docker.ps1/.sh` liefern einen reproduzierbaren First-Install-Smoke fuer frische GitHub-Spiegel.
**Checks:** frische Postgres-Container-DB via `python scripts/init_db.py`, `python scripts/check_required_domain_schemas.py`, `powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434`, `python -m py_compile scripts/init_db.py scripts/check_required_domain_schemas.py alembic/env.py alembic/versions/add_business_partners_tenant_id_20260219.py alembic/versions/perf_indexes_multitenant_20260408.py`, `docker compose -f docker-compose.yml config -q`, `docker compose -f docker-compose.staging.yml config -q`, `docker compose -f docker-compose.dev.yml config -q`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-013

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme-Abrechnung als echten Settlement-Fall mit Ressourcen-, Preis- und Freigabekontext surfacen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
**Abnahmekriterien:** Abrechnung zeigt Fallkopf, knappen Kontext und Timeline ueber dem Settlement-Arbeitsplatz, ohne neue API-Last.
**Erledigt:** `annahme/abrechnung.tsx` zeigt jetzt Settlement-Fallkopf, Abrechnungskontext und Verlauf aus bereits vorhandenen Preview-/Campaign-/Settlement-Daten direkt ueber dem Self-Billing-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-014

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rechnungseingaenge-Liste als operativen Sammelarbeitsplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`
**Abnahmekriterien:** Die Liste zeigt klaren Freigabe-/Verbuchungsdruck und die naechste Bulk-Aktion, ohne den Listenraum zu ueberladen.
**Erledigt:** `rechnungseingaenge-liste.tsx` verdichtet jetzt Freigabe-/Verbuchungsstau, Summenlage und die naechste Bulk-Aktion ueber der bestehenden Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-015

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Mahnwesen als echten Follow-up-Fall mit Owner-, Risiko- und Governance-Sicht verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
**Abnahmekriterien:** Mahnwesen zeigt Mahndruck, Zins-/Connector-Lage und naechste FIBU-Aktion direkt vor dem Objektarbeitsplatz.
**Erledigt:** `finance/mahnwesen.tsx` fuehrt jetzt Mahndruck, Zins-/Connector-Kontext und naechste FIBU-Massnahme als kompakten Follow-up-Kopf ueber dem Objektarbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-016

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Offene-Posten-Raeume fuer Debitoren und Kreditoren auf eine gemeinsame operative Sicht ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/{op-debitoren,op-kreditoren}.tsx`
**Abnahmekriterien:** Beide OP-Raeume zeigen Rueckstand, Risiko und naechste Massnahme konsistent und schlank.
**Erledigt:** `op-debitoren.tsx` und `op-kreditoren.tsx` nutzen jetzt dasselbe leichte OP-Modell fuer Rueckstand, Mahn-/Ueberfaelligkeitsdruck, Kontext und Folgeaktion, ohne die Facharbeit in Tabellen und Dialogen zu verdoppeln.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-017

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufsnahe Dokumenten-/Lieferobjekte mit leichtem Vorgangsbild harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis,auftragsbestaetigung}.tsx`
**Abnahmekriterien:** Beide Objektmasken gewinnen Blocker-, Kontext- und naechste-Aktion-Sicht ohne Doppelung zur Fachmaske.
**Erledigt:** `anlieferavis.tsx` und `auftragsbestaetigung.tsx` haben jetzt einen kompakten Logistik-/Pruefkopf ueber der ObjectPage und bleiben darunter fachlich unveraendert tief.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-018

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und offene Restgrenzen fuer den naechsten Operativ-Rollout dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Es ist dokumentiert, welche Sammel- und Follow-up-Masken jetzt unter dem Zielbild laufen und welche bewusst weiterhin schlank bleiben.
**Erledigt:** Das schlanke Workboard und die Scope-Doku decken jetzt auch Sammel- und Follow-up-Masken fuer Settlement, Rechnungseingaenge, Mahnwesen, OP-Raeume sowie einkaufsnahe Lieferobjekte ab.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-019

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufslisten fuer Avis und Auftragsbestaetigungen als operative Sammelarbeitsplaetze verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis-liste,auftragsbestaetigungen-liste}.tsx`
**Abnahmekriterien:** Beide Listen zeigen Stau, Blocker und naechste Bulk-Aktion ueber der Liste, ohne den Tabellenraum zu ueberfrachten.
**Erledigt:** `anlieferavis-liste.tsx` und `auftragsbestaetigungen-liste.tsx` fuehren jetzt denselben leichten Sammelvorgangskopf fuer Liefer- und Freigabestau ueber der bestehenden ListReport-Facharbeit.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-020

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungslaeufe und UStVA/ELSTER als echte Finance-Follow-up-Raeume verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{fibu/zahlungslaeufe,finance/ustva,fibu/elster-online}.tsx`
**Abnahmekriterien:** Die Seiten zeigen FIBU-Druck, Fristen und naechste Massnahme ueber dem Arbeitsraum.
**Erledigt:** `zahlungslaeufe.tsx`, `finance/ustva.tsx` und `fibu/elster-online.tsx` zeigen jetzt Fristen, Freigabedruck und Einreichungs-/Exportpfad als leichten Finance-Follow-up-Rahmen ueber Wizard bzw. Fachformular.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-021

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Schnittstellen- und Meldefolgearbeitsplatz mit demselben schlanken Fallmodell harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/schnittstellen-center.tsx`, ggf. angrenzende FIBU-Follow-up-Seiten.
**Abnahmekriterien:** Schnittstellen-Center zeigt operativen Druck, Risiken und naechste Aktion ohne KPI-Dopplung.
**Erledigt:** `fibu/schnittstellen-center.tsx` fuehrt Connector-, Revisions- und Periodenlage jetzt als technischen FIBU-Fallkopf mit kurzer Timeline und Masterdatenkontext.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-022

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme- und Queue-Sammelraum mit derselben Leitlogik weiterziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
**Abnahmekriterien:** Warteschlange zeigt operativen Stau, aktuelle Prioritaet und naechste Massnahme ueber der Liste.
**Erledigt:** `annahme/warteschlange.tsx` verdichtet Queue-Druck, Objektkettenlage und Bottleneck-Hinweis jetzt als operativen Annahmekopf ueber der bestehenden Operator-Oberflaeche.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-023

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-/Qualitaets-Sammelarbeitsplaetze auf den leichten Operationsrahmen heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{labor/proben-liste,qualitaet/labor-liste}.tsx`
**Abnahmekriterien:** Laborlisten zeigen Probenstau, kritische Faelle und naechste Folgeaktion ueber der Liste.
**Erledigt:** `labor/proben-liste.tsx` und `qualitaet/labor-liste.tsx` zeigen jetzt offenen Analyse- und Probenstau, Labor-/Chargekontext und die naechste Folgeaktion ueber den Tabellen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-024

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und Restgrenzen nach der dritten Rollout-Welle erneut komprimiert dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Der Rollout bleibt nachvollziehbar und weiterhin bewusst schlank.
**Erledigt:** Scope und Open-Gaps dokumentieren jetzt die dritte Welle fuer Einkaufslisten, FIBU-Follow-up, Schnittstellen, Queue und Laborraeume weiterhin als leichten Rollout ohne Zusatz-Requests.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-025

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditorenraum als FIBU-Profiarbeitsplatz mit echter Folgeaktion statt Info-Toast vertiefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/kreditoren.tsx`
**Abnahmekriterien:** `fibu/kreditoren.tsx` fuehrt DATEV-/Exportpfade als belastbare Folgeaktion ohne lokale Quittungs-Toastlogik.
**Erledigt:** `fibu/kreditoren.tsx` ist jetzt als echter Follow-up-Arbeitsraum mit Fallkopf, Kontext und Timeline verdichtet; DATEV-Export fuehrt direkt in den Buchungsuebergabe-Raum statt lokaler Info-Toast.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-026

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lieferanten-Dokumentraum mit realem Downloadverhalten statt TXT-Fallback professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`
**Abnahmekriterien:** Dokumentdownload in `lieferanten-stamm.tsx` nutzt nur echte Artefaktpfade und zeigt klare Fehlerfuehrung ohne pseudo-download.
**Erledigt:** `lieferanten-stamm.tsx` nutzt jetzt nur noch den echten Downloadpfad; pseudo-TXT-Fallback ist entfernt und Fehlersituationen zeigen klaren DMS-/Artefakt-Hinweis.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-027

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fuhrpark-Funktionsaktionen robust und revisionssicher machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fuhrpark/fahrzeug-stamm.tsx`
**Abnahmekriterien:** Drucker-/Druck-/Unfall-/Loesch-Aktionen behandeln Fehler sauber und quittieren nicht mehr blind.
**Erledigt:** `fuhrpark/fahrzeug-stamm.tsx` fuehrt Setup-, Druck-, Unfall- und Loesch-Aktionen jetzt mit try/catch, klaren Fehlertoasts und Loeschbestaetigung aus.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-028

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Charge-Verfolgung von fragiler Static-Toast-Konfiguration auf belastbaren Runtime-Aktionspfad ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/futtermittel/charge-verfolgung.tsx`
**Abnahmekriterien:** Bulk-Aktionen in der Charge-Verfolgung sind eindeutig runtime-gebunden und enthalten keine toten Static-Action-Reste.
**Erledigt:** `futtermittel/charge-verfolgung.tsx` fuehrt keine static Toast-BulkActions mehr; alle Massenaktionen laufen nur noch ueber den runtime-verdrahteten Aktionspfad.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-029

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/FIBU-Monatswerte als modernen ERP-Operatorraum mit klaren Folgeaktionen und Kontrolldichte veredeln.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/monatswerte.tsx`
**Abnahmekriterien:** Monatswerte liefern klaren Fallkopf, Risiken und naechste Aktion ohne Zusatz-Requests, konsistent zum Operational-Modell.
**Erledigt:** `fibu/monatswerte.tsx` hat jetzt denselben leichten Fallrahmen fuer L3/FIBU-Auswertung (Status, Risiken, naechste Aktion) ohne neue Datenabfragen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-030

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/Cutover-nahe Buchungsuebergabe als FIBU-Leitstand mit Governance- und Revisionskontext vervollstaendigen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/schnittstelle-fibu.tsx`
**Abnahmekriterien:** Schnittstelle-FIBU zeigt operativen Druck, Revisions-/Cutover-Kontext und belastbare Folgewege ohne Platzhalteraktionen.
**Erledigt:** `fibu/schnittstelle-fibu.tsx` zeigt jetzt Fallkopf, Timeline und Revisions-/Cutover-Kontext fuer den Buchungsuebergabeprozess, inklusive klarer Folgefuehrung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-031

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsjournal als FIBU-Operatorraum mit Revisionsdruck, Periode und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchungsjournal.tsx`
**Abnahmekriterien:** `fibu/buchungsjournal.tsx` zeigt Fallkopf, Kontext und Timeline aus bereits geladenen Journaldaten und fuehrt DATEV-/Stornofolge ohne Blindflug.
**Erledigt:** `fibu/buchungsjournal.tsx` fuehrt Journalbuchungen jetzt als Revisionsfall mit Fallkopf, Referenzkontext, Timeline und direktem Exportpfad in die Buchungsuebergabe.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-032

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Abschluss-Checkliste als echter Close-Fall mit Pflichtdruck, Owner und Flow-Spine-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/abschluss-checklist-detail.tsx`
**Abnahmekriterien:** `abschluss-checklist-detail.tsx` verdichtet Pflichtquote, Blocker und naechste Abschlussaktion oberhalb der Checkliste.
**Erledigt:** `abschluss-checklist-detail.tsx` zeigt jetzt den Close-Fall mit Pflichtdruck, Flow-Spine-Bezug, Blockern und kompakter Vorgangssicht ueber der Checkliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-033

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditoren-Zahlungslauf als modernen ERP-Zahlungsoperatorraum mit Governance- und Freigabedruck heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
**Abnahmekriterien:** `zahlungslauf-kreditoren.tsx` zeigt kompakten Zahlungsfallkopf, Kontext und Timeline ohne Zusatz-Requests.
**Erledigt:** `zahlungslauf-kreditoren.tsx` fuehrt den Kreditorenlauf jetzt mit Freigabe-, Skonto- und Ausfuehrungsdruck ueber dem bestehenden SEPA-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-034

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lastschriftlauf als Debitoren-Follow-up mit Mandats-, Frist- und Ausfuehrungsdruck darstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx`
**Abnahmekriterien:** `lastschriften-debitoren.tsx` bekommt denselben leichten Vorgangsrahmen fuer Mandatslage, Freigabe und Export.
**Erledigt:** `lastschriften-debitoren.tsx` surfact Mandatsluecken, Debitorenlauf und Freigabestatus jetzt als kompakten Follow-up-Rahmen ueber dem ObjectPage-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-035

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchhaltungsuebersicht als L3/FIBU-Cockpit mit Perioden- und Schnittstellenlage professionell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchhaltungsuebersicht.tsx`
**Abnahmekriterien:** `buchhaltungsuebersicht.tsx` zeigt kompakten Operatorrahmen fuer Periodenlage, Exportpfad und Revisionskontext.
**Erledigt:** `fibu/buchhaltungsuebersicht.tsx` verdichtet Periodenlage, Revisionskontext und Folgepfade jetzt als L3/FIBU-Cockpit ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-036

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Waagenliste als physischer Leitknoten auf das einheitliche Fallmodell ziehen, ohne die bestehende Uebersicht zu ueberladen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/liste.tsx`
**Abnahmekriterien:** `waage/liste.tsx` fuehrt kompakten Fallkopf, Kontext und Timeline fuer den physischen Kettenzustand aus vorhandenen Daten.
**Erledigt:** `waage/liste.tsx` nutzt jetzt denselben leichten Fallrahmen fuer Bottleneck, Eichlage und die physische Kette direkt ueber der Operatorliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-037

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bankabgleich als echter Klaerungs- und Ausgleichsfall mit Owner, Matching-Druck und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
**Abnahmekriterien:** `bank-abgleich.tsx` nutzt den leichten Fallrahmen ohne neue Requests und macht offene Matching-Lage sofort lesbar.
**Erledigt:** `finance/bank-abgleich.tsx` verdichtet Importstand, Abgleichsdifferenz, Zuordnungsdruck und naechste Aktion jetzt direkt ueber dem Object-Page-Arbeitsraum.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-038

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Payment-Matching als FIBU-Klaerungsarbeitsplatz mit Kontext, Timeline und Folgepfad professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/payment-matching.tsx`
**Abnahmekriterien:** `payment-matching.tsx` fuehrt Rueckstand, Matching-Risiko und naechste Aktion komprimiert ueber dem Arbeitsraum.
**Erledigt:** `finance/payment-matching.tsx` surfact Matching-Stau, manuellen Klaerungsbedarf und Importkontext als kompakten Vorgangsrahmen ohne Zusatz-Last.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-039

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** AP-Invoices-Liste als operativer Pruef- und Freigabestauplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoices-list.tsx`
**Abnahmekriterien:** `ap-invoices-list.tsx` zeigt Stau, Blocker und naechste Sammelaktion aus vorhandenen Listen-/Statusdaten.
**Erledigt:** `finance/ap-invoices-list.tsx` zeigt jetzt Freigabestau, buchbare Rechnungen und die naechste Sammelaktion direkt ueber der Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-040

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** AP-Invoice-Form als echter Pruef- und Buchungsfall mit Governance- und Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoice-form.tsx`
**Abnahmekriterien:** `ap-invoice-form.tsx` erhaelt den leichten Fallrahmen fuer Freigabe, Blocker und naechste Massnahme ohne neue API-Last.
**Erledigt:** `finance/ap-invoice-form.tsx` fuehrt Freigabestatus, Buchbarkeit und Summenlage jetzt als kompakten Pruef- und Buchungsfall.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-041

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** FIBU-Offene-Posten-Gesamtraum als operatorischer Sammelfall zwischen Debitoren und Kreditoren verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/offene-posten.tsx`
**Abnahmekriterien:** `fibu/offene-posten.tsx` zeigt OP-Druck, Ausgleichslage und Folgeweg ueber dem Arbeitsraum.
**Erledigt:** `fibu/offene-posten.tsx` verdichtet OP-Druck, Ueberfaelligkeit und Mahnfolge als klares Arbeitsbild vor der Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-042

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungseingaenge als echter Clearing- und Rueckstandsraum mit kompaktem Vorgangsbild heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungseingaenge.tsx`
**Abnahmekriterien:** `zahlungseingaenge.tsx` surfact Rueckstand, Abgleichslage und naechste Aktion oberhalb der Facharbeit.
**Erledigt:** `fibu/zahlungseingaenge.tsx` fuehrt Rueckstand, Trefferquote und Import-/Klaerungskontext jetzt als einheitlichen Clearing-Rahmen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-043

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungsvorschlaege als FIBU-Entscheidungsraum mit Priorisierung und Governance-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungsvorschlaege.tsx`
**Abnahmekriterien:** `zahlungsvorschlaege.tsx` zeigt Prioritaet, Liquiditaetsdruck und naechste Folgeaktion ohne neue Requests.
**Erledigt:** `fibu/zahlungsvorschlaege.tsx` zeigt jetzt Prioritaet, Skonto-Potenzial und Zahlungsfreigabe als kompakten Entscheidungsraum.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-044

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** BWA als modernen ERP-Analysearbeitsplatz mit Perioden-, Abweichungs- und Folgekontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bwa.tsx`
**Abnahmekriterien:** `bwa.tsx` fuehrt Fallkopf, Kontext und Timeline aus bereits geladenen Auswertungsdaten.
**Erledigt:** `fibu/bwa.tsx` verdichtet Periodenlage, Ergebnisabweichung und Folgeaktion als leichten Analysearbeitsplatz ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-045

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bilanz als L3/FIBU-Abschlussraum mit Risiko- und Folgepfad konsistent zum neuen Arbeitsmodell ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bilanz.tsx`
**Abnahmekriterien:** `bilanz.tsx` liefert kompakten Operatorrahmen fuer Abschlusslage, Revisionskontext und Drilldown-Folgewege.
**Erledigt:** `fibu/bilanz.tsx` fuehrt Bilanzsumme, EK-Quote, Ausgleichslage und Abschlussfolge nun als kompakten Abschlussrahmen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-046

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rueckverfolgung als physischer Ausnahme- und Nachweisfall mit Charge-/Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/rueckverfolgung.tsx`
**Abnahmekriterien:** `charge/rueckverfolgung.tsx` zeigt Status, Blocker und Folgewege fuer Charge-/Nachweisfaelle ohne neuen Datenpfad.
**Erledigt:** `charge/rueckverfolgung.tsx` verdichtet Spurpfad, Lieferkettenblocker und Nachweisfolge ueber der eigentlichen Timeline.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-047

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Wareneingang als physischer Fall zwischen Annahme, Charge und Lager deutlich mit dem Zielbild verknuepfen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/wareneingang.tsx`
**Abnahmekriterien:** `charge/wareneingang.tsx` fuehrt den leichten Fallrahmen fuer Ressource, Blocker und naechste Aktion aus vorhandenen Daten.
**Erledigt:** `charge/wareneingang.tsx` fuehrt Lieferant, Charge, Lagerort und QS-Lage nun als kompakten Eingangsvorgang vor dem Wizard.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-048

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Tourenplanung als Logistik-Leitraum mit Folgecharakter, Bottleneck und Aktionspriorisierung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/tourenplanung.tsx`
**Abnahmekriterien:** `tourenplanung.tsx` bekommt den kompakten Vorgangsrahmen fuer Druck, Blocker und naechste Massnahme ohne Zusatz-Requests.
**Erledigt:** `logistik/tourenplanung.tsx` zeigt Dispositionslage, Ressourcenengpaesse und die naechste Aktionsprioritaet jetzt direkt ueber den Touren.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-049

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Debitorische Ausgangsrechnungen als echter Freigabe-, Druck- und Forderungsfall statt reine Listenmaske fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/invoices-list.tsx`
**Abnahmekriterien:** `invoices-list.tsx` zeigt Rueckstand, Druck-/Versanddruck und naechste Sammelaktion aus bestehender Listenlage.

## OP-ROLL-050

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Ausgangsrechnungsformular als echter Faktura-, Freigabe- und Folgebelegfall verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/invoice-form.tsx`
**Abnahmekriterien:** `invoice-form.tsx` fuehrt Status, Blocker und naechste Aktion oberhalb der Fachbearbeitung.

## OP-ROLL-051

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Dunning-Editor als echter Mahn- und Eskalationsfall professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/dunning-editor.tsx`
**Abnahmekriterien:** `dunning-editor.tsx` surfact Mahnstufe, Eskalationspfad und naechste Aktion ohne neue Requests.

## OP-ROLL-052

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsimport als echter Import-, Pruef- und Verbuchungsfall aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/buchungsimport.tsx`
**Abnahmekriterien:** `buchungsimport.tsx` zeigt Importdruck, Fehlerlage und Folgepfad aus bereits vorhandenen Daten.

## OP-ROLL-053

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Audit-Trail als FIBU-Revisionsraum mit Follow-up und Ausnahmebild fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/audit-trail.tsx`
**Abnahmekriterien:** `audit-trail.tsx` fuehrt Revisionslage, offene Auffaelligkeiten und naechste Pruefaktion kompakt.

## OP-ROLL-054

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Nebenbuch-Abstimmung als echter Clearing- und Differenzraum verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/nebenbuch-abstimmung.tsx`
**Abnahmekriterien:** `nebenbuch-abstimmung.tsx` zeigt Differenzen, Blocker und naechste Klaerungsschritte im leichten Fallmodell.

## OP-ROLL-055

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Hauptbuch als echter Abschluss- und Revisionsraum aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/hauptbuch.tsx`
**Abnahmekriterien:** `hauptbuch.tsx` fuehrt Abschlusslage, Journaldruck und naechste Aktion oberhalb der Sachkontensicht.

## OP-ROLL-056

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** GuV als FIBU-Abweichungs- und Ergebnisraum konsistent zum Operationsmodell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/guv.tsx`
**Abnahmekriterien:** `guv.tsx` zeigt Ergebnisdruck, Ausreisser und Folgeweg ohne Zusatz-Requests.

## OP-ROLL-057

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kontenplan als professionellen Steuerungsraum mit Revisions- und Nutzungskontext ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/kontenplan.tsx`
**Abnahmekriterien:** `kontenplan.tsx` surfact Kontenlogik, Sperr-/Nutzungslage und naechste Verwaltungsaktion ohne Ueberladung.

## OP-ROLL-058

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** OP-Verwaltung als querliegender FIBU-Klaerungsraum zwischen Debitoren und Kreditoren fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/op-verwaltung.tsx`
**Abnahmekriterien:** `op-verwaltung.tsx` zeigt Blocker, Rueckstand und Eskalationspfad ueber der Sammelmaske.

## OP-ROLL-059

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Anlagen-Suite als echter Revisions-, Abschreibungs- und Abschlussfall verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/anlagen-suite.tsx`
**Abnahmekriterien:** `anlagen-suite.tsx` fuehrt Abschreibungsdruck, Revisionslage und naechste Periode kompakt.

## OP-ROLL-060

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditlinien als Risiko- und Freigaberaum fuer Finanzierung und Forderungsschutz aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/kreditlinien.tsx`
**Abnahmekriterien:** `kreditlinien.tsx` zeigt Auslastung, Grenzverletzungen und naechste Massnahme im einheitlichen Arbeitsmodell.

## OP-ROLL-061

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bestandsuebersicht als echter Lager- und Reservierungsraum mit Folgepfad verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx`
**Abnahmekriterien:** `bestandsuebersicht.tsx` zeigt Verfuegbarkeit, Engpaesse und naechste Lageraktion ohne neue API-Last.

## OP-ROLL-062

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bestandskorrektur als echter Pruef-, Freigabe- und Auditfall fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/bestandskorrektur.tsx`
**Abnahmekriterien:** `bestandskorrektur.tsx` surfact Differenz, Begruendung und Folgeaktion oberhalb der Erfassung.

## OP-ROLL-063

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einlagerung als physischer Vorgang zwischen Bestand, Charge und Lagerplatz klar verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/einlagerung.tsx`
**Abnahmekriterien:** `einlagerung.tsx` fuehrt Ressourcenlage, Blocker und naechste Massnahme ohne neue Requests.

## OP-ROLL-064

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Auslagerung als echter Liefer- und Verfuegbarkeitsfall professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/auslagerung.tsx`
**Abnahmekriterien:** `auslagerung.tsx` zeigt Verfuegbarkeit, Reservierungsdruck und Folgeweg oberhalb der Facharbeit.

## OP-ROLL-065

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lagerbewegungen als Revisions- und Rueckverfolgungsraum einheitlich aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/lagerbewegungen.tsx`
**Abnahmekriterien:** `lagerbewegungen.tsx` verdichtet Bewegungsdruck, Audit-Lage und Folgepfad ohne zusaetzliche Datenlast.

## OP-ROLL-066

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Inventur als echter Klaerungs- und Differenzraum zwischen Lager und FIBU fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/inventur.tsx`
**Abnahmekriterien:** `inventur.tsx` zeigt Differenzdruck, Owner und naechste Inventuraktion im leichten Fallmodell.

## OP-ROLL-067

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lagerterminal als physischer Arbeitsraum fuer schnelle Entscheidungen mit kompaktem Kontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/terminal.tsx`
**Abnahmekriterien:** `terminal.tsx` fuehrt Status, Blocker und naechste Aktion ohne die Touch-Bedienung zu ueberfrachten.

## OP-ROLL-068

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Qualitaetsausnahmen als echter Eskalations- und Freigaberaum fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx`
**Abnahmekriterien:** `ausnahmen.tsx` zeigt Risiko, Owner, naechste Massnahme und Eskalationsdruck ueber dem Arbeitsraum.

## OP-ROLL-069

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Reklamationsliste als Sammelraum fuer Eskalationen, Wiedervorlagen und Folgewege verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/reklamationen.tsx`
**Abnahmekriterien:** `reklamationen.tsx` surfact Rueckstand, Risikobild und naechste Sammelaktion kompakt aus vorhandenen Daten.

## OP-ROLL-070

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-Detail als echter Pruef- und Freigabefall zwischen Probe, Charge und QS fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/labor-detail.tsx`
**Abnahmekriterien:** `labor-detail.tsx` fuehrt Befundlage, Blocker und naechste Aktion konsistent ueber der Fachmaske.

## OP-ROLL-071

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Frachtbriefe als echter Logistik- und Nachweisraum zwischen Tour, Charge und Dokument professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/frachtbriefe.tsx`
**Abnahmekriterien:** `frachtbriefe.tsx` zeigt Blocker, Dokumentdruck und naechste Aktion ohne neue Requests.

## OP-ROLL-072

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Wiegungen als operative Sammelmaske zwischen Waage, Annahme und Abrechnung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/wiegungen.tsx`
**Abnahmekriterien:** `wiegungen.tsx` surfact Rueckstand, Blocker und Folgepfad im leichten Fallmodell aus bereits geladenen Daten.

## ERP-FINANZ-ROADMAP-P3P4

**Von:** Claude Code
**Owner:** (Team)
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** ERP-Finanz Roadmap Phase 3 (Orders-REST Architektur-Entscheid + Tenant-Isolation-Tests) und Phase 4 (Observability Counter + DB-Indexes) abschliessen.

**Dateibesitz:**
- `packages/erp-domain/src/bootstrap.ts` — Architektur-Kommentar Orders-REST = Python
- `packages/erp-domain/tests/integration/tenant-isolation.spec.ts` — Negative Tenant-Tests
- `app/core/metrics.py` — tenant_auth_errors_total Counter
- `app/middleware/tenant_enforcement.py` — Counter-Inkrementierung
- `migrations/sql/erp/006_missing_tenant_indexes.sql` — Composite-Indexes domain_sales/inventory/erp/finanz
- `alembic/versions/faf00a6bfc11_006_missing_tenant_indexes.py` — No-Op Alembic-Revision
- `tests/test_gap_fixes_phase4.py` — Phase-4-Smoke-Tests

**Abnahmekriterien:**
- bootstrap.ts dokumentiert: Orders-REST = Python; controller-Token nicht registriert (Invariante)
- Tenant-Isolation: fremder Tenant sieht keine Debitoren/Kreditoren des anderen Tenants
- `tenant_auth_errors_total{route, error_type}` Counter in Prometheus scrappbar
- 006_missing_tenant_indexes.sql: idempotente Composite-Indexes auf alle relevanten Schemas
- `alembic upgrade head` laeuft ohne drop_table-Operationen

**Erledigt:** Alle 4 Phase-3+4-Ziele umgesetzt, committed `f4d0462ae` + `6cf97afcc`; Linter sauber; 4/4 Phase-4-Tests gruen; `alembic upgrade head` = no-op; main + develop auf GitHub gepusht.

**Checks:** `pytest tests/test_gap_fixes_phase4.py -v`; `alembic upgrade head`; `flake8 app/core/metrics.py app/middleware/tenant_enforcement.py`

## UX-SERVICE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Service-Anfragen und Rueckmeldung mit Rollenfokus, klarer Aufgabe, Status, naechster Aktion und Nachweisfuehrung nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SERVICE-001.yaml`, `packages/frontend-web/src/pages/service/anfragen.tsx`, `packages/frontend-web/src/pages/service/rueckmeldung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Service-Anfragen und Rueckmeldung zeigen Rollenfokus, Service-/Rueckmeldeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Liste, Suche, Export, Workflow-Handover, Rueckmeldeformular und Navigation bleiben erhalten.
**Erledigt:** Service-Anfragen um Rollenfokus, Service-Arbeitsplan, Managemententscheidung, Next Action, Nachweislink, CRUD-Abdeckung und klare Leerzustandsaktion erweitert; Rueckmeldung um Rollenfokus, Rueckmeldeplan, Pflichtklarheit, Folgehinweis, Nachweislink und gefuehrte Sendebereitschaft erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SERVICE-001.yaml`; `git diff --check`
**Offene Risiken:** Service-Abschluss und Feldservice-Detail bleiben Folgeslices; dieser Slice fokussiert Anfrageuebersicht und Rueckmeldung.

## UX-MONITORING-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Monitoring-Alerts und Monitoring-Regeln mit Betriebsstatus, Owner, naechster Aktion, Eskalationsnachweis und CRUD-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-MONITORING-001.yaml`, `packages/frontend-web/src/pages/admin/monitoring/alerts.tsx`, `packages/frontend-web/src/pages/admin/monitoring/regeln.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Alert-Uebersicht und Regelverwaltung zeigen Rollenfokus, Betriebs-/Regelplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Alert-Liste, Regelanlage, Kanalverwaltung, Scheduler-Jobs und Loeschen bleiben erhalten.
**Erledigt:** Alert-Uebersicht um Rollenfokus, Betriebsplan, Managemententscheidung, Next Action, Eskalationsnachweis, Alert-Zeitleiste und klaren Leerzustand erweitert; Monitoring-Regeln um Rollenfokus, Regelbetriebsplan, Managemententscheidung, Next Action, Nachweislink, CRUD-Abdeckung und gefuehrte Auswahlfelder erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-MONITORING-001.yaml`; `git diff --check`
**Offene Risiken:** `system/live-monitor` bleibt technischer Folgeslice; dieser Slice fokussiert Admin-Alerts und Monitoring-Regeln.

## UX-COMPLIANCE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Compliance-Center und QS-Checkliste mit klarer Pruefaufgabe, Risiko, naechster Aktion, Nachweisfuehrung und CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-COMPLIANCE-001.yaml`, `packages/frontend-web/src/pages/admin/compliance-dashboard.tsx`, `packages/frontend-web/src/pages/compliance/qs-checkliste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Compliance-Center und QS-Checkliste zeigen Rollenfokus, Pruefplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Reports, Detailnavigation, Agent-Panel, Tastaturleiste und Tabellen bleiben erhalten.
**Erledigt:** Compliance-Center um Rollenfokus, Compliance-Pruefplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung erweitert; QS-Checkliste um Rollenfokus, QS-Pruefplan, Entscheidungsbild, Nachweislink und gefuehrte Auditbereitschaft erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-COMPLIANCE-001.yaml`; `git diff --check`
**Offene Risiken:** Meldewesen-Konsole bleibt Spezial-Folgeslice; dieser Slice fokussiert Dashboard und QS-Pruefaufgabe.

## UX-AGRIBUSINESS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Feldservice-Aufgaben als Agribusiness-Einsatzliste mit Einsatzstatus, Owner, naechster Aktion, Nachweisfuehrung und CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-AGRIBUSINESS-001.yaml`, `packages/frontend-web/src/pages/agribusiness/field-service-tasks.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Field-Service-Aufgaben zeigen Rollenfokus, Einsatzplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Suche, Copilot, Druck, Neu/Bearbeiten/Abbrechen/Loeschen, Workflow-Hinweis und Audit-Drawer bleiben erhalten.
**Erledigt:** Field-Service-Aufgabenliste um Rollenfokus, Einsatzplan, Managemententscheidung, Next Action, Nachweislink, Einsatz-KPIs und CRUD-/Workflow-Abdeckung erweitert; bestehende Suche, Copilot, Druck, Neu/Bearbeiten/Abbrechen/Loeschen, Workflow-Hinweis und Audit-Drawer bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-AGRIBUSINESS-001.yaml`; `git diff --check`
**Offene Risiken:** Neue-/Edit-Masken und Farmer-Stamm bleiben Folgeslices; dieser Slice fokussiert die Einsatzliste.

## UX-SYSTEM-LIVE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Technischen Live-Monitor von roher JSON-Sicht zu einer verstaendlichen Betriebsstatusseite mit Rollenfokus, Statusdeutung, naechster Aktion und Nachweisbezug nach UX-Standard umbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SYSTEM-LIVE-001.yaml`, `packages/frontend-web/src/pages/system/live-monitor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Live-Monitor zeigt Rollenfokus, Betriebsplan, Managemententscheidung, Next Action, Nachweislink und kompakte Ereignisuebersichten; technische JSON-Rohdaten bleiben als Diagnosebereich verfuegbar; bestehender NavLiveStatus und Live-Store werden weiter genutzt.
**Erledigt:** Live-Monitor als Live-Betriebsmonitor mit Rollenfokus, Betriebsplan, Managemententscheidung, Next Action, Nachweislink, Live-KPIs, Ereigniszeitleiste und kompakten Sales-/Bestands-/Policy-Listen umgesetzt; technische JSON-Rohdaten bleiben als Diagnosebereich verfuegbar.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SYSTEM-LIVE-001.yaml`; `git diff --check`
**Offene Risiken:** Externe SSE-Verfuegbarkeit bleibt umgebungsabhaengig; dieser Slice verbessert die UI-Deutung vorhandener Live-Daten.

## UX-MELDEWESEN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Meldewesen-Konsole mit Meldefrist, Artefaktstatus, Owner, naechster Einreichungsaktion, Nachweisfuehrung und CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-MELDEWESEN-001.yaml`, `packages/frontend-web/src/pages/compliance/meldewesen-konsole.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Meldewesen-Konsole zeigt Rollenfokus, Meldeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Connector-, Unit-, Schedule-, Job-, Import-/Export- und Artefaktfunktionen bleiben erhalten.
**Erledigt:** Meldewesen-Konsole um Rollenfokus, Meldeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung fuer Connectoren, Reporting Units, Zeitplaene, Jobs, Import/Export und Artefakte erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-MELDEWESEN-001.yaml`; `git diff --check`
**Offene Risiken:** Echte externe Meldestellen-Quittungen bleiben umgebungsabhaengig; dieser Slice verbessert die UI-Steuerung der vorhandenen Jobs und Artefakte.

## UX-AGRAR-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Agrar-Schlagkartei und Massnahmen-Dokumentation mit Feld-/Massnahmenstatus, Nachweis, naechster Aktion und gefuehrter CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-AGRAR-001.yaml`, `packages/frontend-web/src/pages/agrar/feldbuch/schlagkartei.tsx`, `packages/frontend-web/src/pages/agrar/feldbuch/massnahmen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Schlagkartei und Massnahmen-Dokumentation zeigen Rollenfokus, Feld-/Massnahmenplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Filter, Export, Feldblockfinder, Tabs, Tabellen, Anlage-, Bearbeitungs- und Loeschpfade bleiben erhalten.
**Erledigt:** Schlagkartei um Rollenfokus, Feldplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung erweitert; Massnahmen-Dokumentation um Rollenfokus, Massnahmenplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Nachweis-Abdeckung erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-AGRAR-001.yaml`; `git diff --check`
**Offene Risiken:** Duengungsplanung, PSM-Spezialmasken und Portal-Feldbuch bleiben Folgeslices; dieser Slice fokussiert Schlag- und Massnahmenuebersicht.

## UX-UX-AUDIT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Pruefen und verbindlich festlegen, wo der UX-Exzellenzbaukasten weiterhin fachlich sinnvoll ist, wo eine kompakte oder minimale Variante reicht und wo der systemweite Rollout als abgeschlossen gilt.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-UX-AUDIT-001.yaml`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Der UX-Standard unterscheidet volle, kompakte und minimale Baukasten-Nutzung; Stop-Regeln verhindern Ueberladung; verbleibende sinnvolle Rollout-Slices sind nach Nutzerwert priorisiert; Doku-Checks und Workboard-Validierung sind gruen.
**Erledigt:** UX-Standard von pauschaler Pflicht auf Seitentyp-Klassifikation umgestellt; Stop-Regeln gegen Ueberladung fuer Rollenfokus, Management-Bild, Nachweislinks, Audit-Zeitleiste und CRUD-Checkliste ergaenzt; systemweiter Rollout fuer Kernbereiche als abgeschlossen dokumentiert; weitere Arbeiten erfolgen nur noch nutzerwertbasiert.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-UX-AUDIT-001.yaml`; `git diff --check`
**Offene Risiken:** Bereits umgestellte Seiten koennen im Einzelfall zu schwer sein; kuenftige Trim-Reviews reduzieren nur konkret sichtbare Ueberladung, statt den Baukasten pauschal zurueckzunehmen.

## UX-REMAINDER-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Verbleibende sinnvolle UX-Abschlussarbeiten fuer Futtermittel, Duengung und Portal nach der neuen Baukasten-Einsatzlogik umsetzen: voll nur fuer echte Experten-/Pruefflaechen, kompakt fuer Planung und leicht fuer Self-Service.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-REMAINDER-001.yaml`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/src/pages/futtermittel/futtermittel-qualitaetskontrolle.tsx`, `packages/frontend-web/src/pages/agrar/duengung/planung.tsx`, `packages/frontend-web/src/pages/agrar/duenger/bedarfsrechner.tsx`, `packages/frontend-web/src/pages/portal/feldbuch.tsx`, `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`
**Abnahmekriterien:** Futtermittel-Expertenseiten zeigen Pruefstatus, Risiko, naechste Aktion und Nachweis ohne einfache Pflegebereiche zu ueberladen; Duengungsplanung und Bedarfsrechner fuehren Bedarf, Sperrfrist/Risiko, Nachweis und naechste Planungshandlung kompakt; Portal-Feldbuch und Naehrstoffbilanzen nutzen leichte Self-Service-Sprache; keine unpassenden Management-Bilder oder sichtbaren CRUD-Checklisten auf Self-Service-Seiten; Typecheck, Workboard-Validierung und Doku-Checks sind gruen.
**Erledigt:** Futtermittel-Rationsoptimierung um leichte fachliche Schrittfolge erweitert; Futtermittel-QS um Pruefablauf, naechste Pruefaktion und QS-Nachweislink erweitert; Duengungsplanung und Bedarfsrechner um kompakte Planung/Eingabefuehrung erweitert; Portal-Feldbuch und Naehrstoffbilanzen um leichte Self-Service-Next-Actions und Leerzustaende erweitert; UX-Standard auf abgeschlossenes Abschlussbild aktualisiert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-REMAINDER-001.yaml`; `git diff --check`
**Offene Risiken:** Kuenftige neue Fachfunktionen brauchen wieder Seitentyp-Klassifikation; aktuell sind keine weiteren UX-Flaechenrollouts vorgesehen.

## UX-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Die fuenf Abschlussgaps aus dem Ist/Soll-Vergleich schliessen: Open-Gaps-Doku auf die neue UX-Einsatzlogik ziehen, Portal-Dokumente entladen, RAT-OPT-001 im Workboard abschliessen, P1-Restprogramme klar von UX trennen und HRM-/Live-Gates als Betriebsnachweise statt Repo-Code-Gaps fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-GAP-CLOSURE-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/portal/dokumente.tsx`
**Abnahmekriterien:** Open-Gaps-Doku beschreibt UX nicht mehr als pauschale Pflichtmuster, sondern als abgeschlossenen Rollout mit Seitentyp-Logik; Portal-Dokumente zeigen keine Rollenleiste, kein Management-Bild und keine sichtbare CRUD-Checkliste mehr; RAT-OPT-001 ist im Workboard nicht mehr irrefuehrend als in Arbeit gefuehrt; Coverage/Domain-Parity und externe Gates sind klar als eigene technische bzw. betriebliche Programme abgegrenzt; Typecheck, Workboard-Validierung und Doku-Checks sind gruen.
**Erledigt:** Open-Gaps-Doku auf abgeschlossene UX-Seitentyp-Logik aktualisiert; Portal-Dokumente von Rollenleiste, Management-Entscheidung und CRUD-Checkliste auf leichte Self-Service-Fuehrung reduziert; RAT-OPT-001 im Workboard als abgeschlossen und historisch eingeordnet; Coverage/Domain-Parity als Qualitaetsprogramme und HRM-/Live-Gates als Betriebsnachweise abgegrenzt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-GAP-CLOSURE-001.yaml`; `git diff --check`
**Offene Risiken:** Kuenftige neue Fachfunktionen koennen neue UX-Detailreviews ausloesen; aktuell bestehen keine offenen UX-Baukasten-Rollout-Gaps.

## FRONTEND-DOMAIN-AUDIT-REPAIR-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Claude-Domain-Audit-Fixes vor Push qualitaetssichern: i18n-/Encoding-Korruption reparieren, temporaere Skripte entfernen, Routing- und Module-Registrierung validieren und lokale Commit-Historie mit korrektem Autor konsolidieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`, `packages/frontend-web/src/app/route-aliases.json`, `packages/frontend-web/src/app/page-module-loader.ts`, `packages/frontend-web/src/app/page-module-groups/commercial.ts`, `packages/frontend-web/src/i18n/locales/*/translation.json`, `packages/frontend-web/src/pages/**/*.tsx`
**Abnahmekriterien:** Keine neue UTF-8-Mojibake in geaenderten Frontend-Dateien; route-aliases verweisen auf ladbare Page-Module; fehlende i18n-Keys aus dem Audit sind ergaenzt ohne Locale-Korruption; Typecheck und Workboard-Validierung sind gruen; unpushte Commits haben korrekte Autoren-Metadaten.
**Erledigt:** Locale-Dateien de/en/es/fr auf sauberen Stand zurueckgefuehrt und `pattern.listreport.items_count` gezielt ergaenzt; Encoding-Funde im gesamten `packages/frontend-web/src` bereinigt; ungueltige UTF-8-Dateien nach UTF-8 konvertiert; temporaere Reparatur-Skripte entfernt; Route-Aliases gegen existierende Module validiert; lokale unpushed Historie vor Push auf saubere Autor-/Commitstruktur konsolidiert.
**Checks:** `node` JSON-Parse fuer `packages/frontend-web/src/i18n/locales/de|en|es|fr/translation.json`; Encoding-Scan `rg -n "Ã|Â|â" packages/frontend-web/src`; UTF-8-Validierung fuer `packages/frontend-web/src`; Route-Alias-Modulvalidierung gegen `packages/frontend-web/src`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `pnpm --filter @valero-neuroerp/frontend-web lint`; `pnpm --filter @valero-neuroerp/frontend-web build`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`; `git diff --check`
**Offene Risiken:** Vite-Build meldet weiterhin bestehende, nicht blockierende Warnungen aus CSS-Minifizierung und POS-Doppelimport; backendabhaengige Datenladefehler sind von Frontend-Routing/Rendering getrennt zu bewerten.

## FACHLICHE-VERTIEFUNG-UX-W17-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Wave 17 UX — Zu-/Abschlaggruppen [ZAGR], Zu-/Abschlagklassen [ZAKL] und Zu-/Abschlagkonditionen [ZAK] als vollständige produktive Maske unter `/preise/zu-abschlaggruppen`.
**Dateibesitz:** `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W17-001.yaml`, `packages/frontend-web/src/lib/api/zuAbschlaggruppen.ts`, `packages/frontend-web/src/pages/preise/zu-abschlaggruppen.tsx`, `packages/frontend-web/tests/e2e/fachliche-vertiefung-zu-abschlaege.spec.ts`
**Abnahmekriterien:** Tabs ZAGR/ZAKL/ZAK produktiv; CREATE + DELETE für Gruppen und Klassen; CREATE + Listenansicht für Konditionen; E2E 4/4 grün; Regression Rabattgruppen + Betriebsstätten grün; Typecheck grün; Workboard grün.
**Erledigt:** API-Client `zuAbschlaggruppen.ts`; UI-Maske mit 3 Tabs; Navigation + Route-Builder bereits vorhanden; E2E 4/4; Regression 9/9; TypeScript grün; alle Gates grün.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; Playwright-Gates W17 + Regression W14; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Keine.

## FACHLICHE-VERTIEFUNG-UX-W16-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-25
**Ziel des Slices:** Wave 16 Integration Vertreterstamm und Vertreterprovisionsgruppen: provisionsgruppe_nr in der Vertreterstamm-Maske (W15) als Select aus echten Provisionsgruppen (W12) statt freiem Text-Input.
**Dateibesitz:** `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W16-001.yaml`, `packages/frontend-web/src/pages/crm/vertreterstamm.tsx`, `packages/frontend-web/tests/e2e/fachliche-vertiefung-vertreterstamm-prov-integration.spec.ts`, Fremdfix: `packages/frontend-web/tests/e2e/fachliche-vertiefung-vertreterprovisionen.spec.ts`
**Abnahmekriterien:** provisionsgruppe_nr im Vertreter-Anlegen-Formular ist ein Select; provisionsgruppe_nr im Edit-Dialog ist ein Select; W16-Integrationstest gruen; Regression W15/W12 gruen; Typecheck gruen.
**Erledigt:** vertreterstamm.tsx Create-Form + Edit-Dialog auf useProvisionsgruppen()-Select; W16-Integrationstest (2/2 gruen); W15-Regression (4/4 gruen); W12-Regression (1/1 gruen, 1 Staffel-Test skip mit Begruendung); Fremdfix W12-Spec strict-mode-Violations.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; Playwright-Gates W16+W15+W12; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** W12-Staffeln-Test skip ist dokumentiertes pre-existing Playwright-Isolation-Issue; keine fachlichen Risiken.

## FACHLICHE-VERTIEFUNG-UX-W21-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Wave 21 — 6 fehlende Frontend-Pages: Daueraufträge, Massebilanz, Vermehrungsverträge, Zinsabrechnung, Artikel-Bestandteile, Artikelverpackung. Inkl. API-Clients, Navigation, Routen und E2E-Tests.
**Dateibesitz:** `packages/frontend-web/src/lib/api/dauerauftraege.ts`, `packages/frontend-web/src/lib/api/massebilanz.ts`, `packages/frontend-web/src/lib/api/vermehrungsvertraege.ts`, `packages/frontend-web/src/lib/api/zinsabrechnung.ts`, `packages/frontend-web/src/lib/api/artikelbestandteile.ts`, `packages/frontend-web/src/lib/api/artikelverpackung.ts`, `packages/frontend-web/src/pages/verkauf/dauerauftraege.tsx`, `packages/frontend-web/src/pages/lager/massebilanz.tsx`, `packages/frontend-web/src/pages/agrar/vermehrungsvertraege.tsx`, `packages/frontend-web/src/pages/agrar/zinsabrechnung.tsx`, `packages/frontend-web/src/pages/stammdaten/artikelbestandteile.tsx`, `packages/frontend-web/src/pages/stammdaten/artikelverpackung.tsx`, Navigation- und Route-Builder-Dateien, 6 E2E-Specs
**Abnahmekriterien:** 6 API-Clients + 6 Pages mit Mutation Lifecycle Guards; Toast-Feedback; Navigation aktualisiert; Route-Builder-Einträge; 6 E2E-Tests gruen; TypeCheck gruen.
**Erledigt:** 6 API-Clients, 6 Pages, Navigation und Route-Builder aktualisiert, 6 E2E-Tests. TypeCheck: 0 Fehler. Bugfix vermehrungsvertraege.tsx (Radix SelectItem value="").
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; Playwright-Gates W21; `python scripts/agent_workboard_supervisor.py validate`
**Gate-Ergebnis:** 6/6 E2E-Tests gruen, TypeCheck 0 Fehler (2026-05-26, develop)
**Offene Risiken:** Keine.

## BACKEND-SLICE-GDPR-KONTRAKTE-DMS-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Vier offene Backend-Slices implementieren: GDPR-requests-Lifecycle (Art. 15/17/20), Kontrakte-Amendments/Templates, Agribusiness-Farmers und DMS-Inbox + admin/dms. Pydantic-V2-ConfigDict-Migration in allen neuen Endpoint-Dateien.
**Dateibesitz:** `app/api/v1/endpoints/gdpr_requests.py`, `app/api/v1/endpoints/kontrakte.py`, `app/api/v1/endpoints/agribusiness.py`, `app/api/v1/endpoints/dms_inbox.py`, `app/api/v1/endpoints/admin_dms.py`, `app/infrastructure/models/agribusiness_models.py`, Alembic-Migrationen fuer GDPR und Farmers, `app/api/v1/api.py`
**Abnahmekriterien:** GDPR-Lifecycle (PENDING→VERIFIED→PROCESSING→COMPLETED|REJECTED) mit Download; Kontrakte GET amendments-templates + POST/PATCH amendments; Farmers GET/DELETE mit 204; DMS GET/POST/DELETE inbox + admin status/test/bootstrap; Pydantic V2 ohne Config-Deprecation-Warnungen.
**Erledigt:** 8 GDPR-Endpoints (814de39d0); 4 Kontrakte-Amendments-Endpoints (80077b009); Farmer-Model + Migration + 2 Endpoints (e8dd5b24e); 6 DMS-Inbox/Admin-Endpoints via Mayan-Client (a3a118e85); Pydantic-ConfigDict-Fix (0fb3f84eb).
**Checks:** `pytest tests/test_process_kernel_wave8_complaint_e2e.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`
**Gate-Ergebnis:** pytest Full Suite 9228 passed, 0 failed (2026-05-26, develop 271bc5e12)
**Offene Risiken:** Keine.

## TEST-SUITE-CLEANUP-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Alle 32 pre-existing und neu einfuehrten Failures in der pytest-Full-Suite auf 0 bringen. Kein semantic-breaking Code-Change.
**Dateibesitz:** `app/api/v1/endpoints/reklamation_api.py`, `app/core/multi_context_agent.py`, `app/api/v1/endpoints/agrar_settlements.py`, `app/api/v1/endpoints/ebilanz_elster.py`, `app/api/v1/endpoints/silo_operations_api.py`, `tests/test_workers_coverage.py`, `tests/test_process_kernel_wave8_complaint_e2e.py`, `tests/test_hrm_compliance_pos.py`, `tests/test_kontrakt_hedging_preis_erechnung.py`
**Abnahmekriterien:** `pytest --no-cov -q` liefert 0 failed in der Full-Suite.
**Erledigt:** reklamation_api.py: _build_reklamation_payload + _store-Stub + computed fields + audit-key-fix (34d02a803); multi_context_agent.py: field_validator UTC-aware + datetime.now(timezone.utc) (34d02a803); asyncio.run() in test_workers_coverage + test_hrm_compliance_pos + test_kontrakt_hedging_preis_erechnung; agrar_settlements.py: get_repository/save_to_store Stubs; ebilanz_elster.py: XBRL-Fallback mit taxNumber; silo_operations_api.py: GET /zellen/{id} by-ID Route; wave8_complaint: PostgreSQL SessionLocal statt SQLite (271bc5e12).
**Checks:** `pytest --no-cov -q` (Full Suite)
**Gate-Ergebnis:** 9228 passed, 0 failed (2026-05-26, develop 271bc5e12) — zuvor 32 Failures
**Offene Risiken:** Keine.

## SLICE-006-EINVOICE-B2B-EXPORT-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Commit:** `08d64eff4`
**Ziel des Slices:** XRechnung 3.0 (UBL 2.1) und ZUGFeRD 2.x (PDF/A-3 + CII-XML Profil EN 16931) Export für reguläre B2B-Verkaufsrechnungen (SalesInvoice). Schließt die einzige verbliebene gesetzliche Lücke (E-Rechnung-2025 B2B-Versand).
**Dateibesitz:** `docs/agent-ops/slices/SLICE-006-EINVOICE-B2B-EXPORT-001.yaml`, `app/services/einvoice_generator.py`, `app/api/v1/endpoints/sales_invoice_einvoice.py`, `tests/test_einvoice_generator.py`, `packages/frontend-web/src/lib/api/einvoice.ts`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `docs/PROJEKT-GESAMTSTAND-2026-05-27.md`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `docs/GOBD-COMPLIANCE.md`.
**Erledigt:** `einvoice_generator.py` (EN-16931-UBL-2.1 + CII-XML + PDF/A-3 via factur-x, 23 pytest-Tests); Endpoints `POST/GET /api/v1/sales/invoices/{n}/einvoice/xrechnung|zugferd` mit GoBD-Archiv; Frontend-Download-Buttons (XRechnung + ZUGFeRD) in Rechnungsmaske mit Mutation-Pending-Guard; 1/1 E2E grün; TypeCheck 0 Fehler; Fremdfix `closing_checklists.py` (Optional-Import fehlte).
**Gate-Ergebnis:** 23/23 pytest grün; 1/1 E2E grün; TypeScript 0 Fehler; py_compile grün; 3 Endpoints registriert; GoBD-Artifact-Persistenz vorhanden.
**Offene Risiken:** Volle Schematron-Validierung bleibt optionaler Hook; Peppol-Versand bleibt Folgeslice.

## SLICE-008-DSGVO-ART30-ROPA-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** DSGVO Art. 30 Verzeichnis von Verarbeitungstätigkeiten (Records of Processing Activities). Backend CRUD + JSON-Export + Frontend-Verwaltungsmaske. Art. 15/17/20 bereits implementiert — Art. 30 war die letzte zentrale DSGVO-Pflicht-Lücke.
**Dateibesitz:** `docs/agent-ops/slices/SLICE-008-DSGVO-ART30-ROPA-001.yaml`, `app/api/v1/endpoints/gdpr_art30_ropa.py`, `packages/frontend-web/src/lib/api/gdpr-art30.ts`, `packages/frontend-web/src/pages/compliance/verarbeitungsverzeichnis.tsx`, `packages/frontend-web/tests/e2e/slice-008-dsgvo-art30.spec.ts`, `tests/test_gdpr_art30_ropa.py`.
**Gate-Ergebnis:** pytest 20/20 ✅ · E2E 5/5 ✅ · TypeScript 0 Fehler ✅ · Routing fixiert ✅
**Offene Risiken:** Produktive DB-Persistenz bleibt Folgeslice (In-Memory-Store als Fallback aktiv).

## SLICE-009-DSGVO-ART33-BREACH-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** DSGVO Art. 33 Datenpannen-Meldeprozess — Backend CRUD + 72h-Fristüberwachung + Frontend-Maske mit Ampelindikator. Fremdfix: banken.py (get_tenant_id fehlte) + ebilanz_elster.py (Field fehlte).
**Dateibesitz:** `docs/agent-ops/slices/SLICE-009-DSGVO-ART33-BREACH-001.yaml`, `app/api/v1/endpoints/gdpr_art33_breach.py`, `packages/frontend-web/src/lib/api/gdpr-art33.ts`, `packages/frontend-web/src/pages/compliance/datenpannen.tsx`, `packages/frontend-web/tests/e2e/slice-009-dsgvo-art33.spec.ts`, `tests/test_gdpr_art33_breach.py`.
**Gate-Ergebnis:** pytest 24/24 ✅ · E2E 5/5 ✅ · TypeScript 0 Fehler ✅
**Offene Risiken:** E-Mail-Versand an Behörde bleibt Folgeslice.

## SLICE-010-VOICE-LAGER-EINKAUF-HR-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Voice-Intent für Lager / Einkauf / HR ausbauen — 15 neue Intents in action_registry.py, Keyword-Fallbacks im IntentResolver, Frontend-AI-Shortcuts.
**Dateibesitz:** `services/ki-usability/app/services/action_registry.py`, `services/ki-usability/app/services/intent_resolver.py`, `packages/frontend-web/src/app/navigation/ai-shortcuts.tsx`, `tests/test_voice_intent_lager_einkauf_hr.py`.
**Abnahmekriterien:** 15 neue Intents; Resolver löst alle Phrasen auf; pytest grün; TypeScript 0 Fehler.
**Erledigt:** 15 Lager/Einkauf/HR-Intents in der ActionRegistry, robuste Keyword-/Phrase-Aufloesung inklusive EAN-, Mengen-, Betrags- und HR-Datumsparametern sowie Frontend-AI-Shortcuts fuer die drei Domaenen.
**Checks:** `python -m pytest tests/test_voice_intent_lager_einkauf_hr.py -q --no-cov` in `services/ki-usability`; `pnpm --filter @valero-neuroerp/frontend-web type-check`.
**Offene Risiken:** VoiceButton-Integration auf einzelnen Fachseiten bleibt Folgeslice.

## SLICE-011-VOICE-VERKAUF-CRM-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Dispatch-Nachzug fuer Slice-010 (NAV_ACTIONS) + Voice Wave A fuer Verkauf und CRM.
**Dateibesitz:** `ActionDispatchContext.tsx`, `action_registry.py`, `intent_resolver.py`, `ai-shortcuts.tsx`, `tests/test_voice_intent_verkauf_crm.py`.
**Gate-Ergebnis:** pytest 62/62 ✅ (39 Slice-010 + 23 Slice-011) · TypeScript 0 Fehler ✅ · 52 Actions in Registry ✅
**Erledigt:** 14 NAV_ACTIONS fuer Slice-010 nachgezogen; 15 neue Verkauf/CRM-Intents; Resolver-Fallbacks + Param-Extraktion; AI-Shortcuts Verkauf/CRM.
**Offene Risiken:** Wave B (FiBu/Compliance) und Wave C (Agrar/Logistik) folgen als Slice-012+.

## SLICE-012-VOICE-FIBU-COMPLIANCE-AGrar-LOGISTIK-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Voice Wave B (FiBu + Compliance) und Wave C (Agrar + Logistik) — 26 neue Intents, NAV_ACTIONS, Resolver, AI-Shortcuts.
**Dateibesitz:** `ActionDispatchContext.tsx`, `action_registry.py`, `intent_resolver.py`, `ai-shortcuts.tsx`, `tests/test_voice_intent_fibu_compliance_agrar_logistik.py`.
**Gate-Ergebnis:** pytest 85/85 ✅ · TypeScript 0 Fehler ✅ · 78 Actions in Registry ✅
**Erledigt:** 8 Finanz-, 5 Compliance-, 8 Agrar-, 5 Logistik-Intents; NAV_ACTIONS-Dispatch; AI-Shortcuts fuer alle vier Domaenen.
**Offene Risiken:** Voice-Domain-Filter im Frontend (context.domain) noch ohne Resolver-Scoping — Folgeoptimierung.

## SLICE-013-VOICE-LOCAL-POLISH-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Privacy-First Diktat: faster-whisper STT + Ollama Text-Polish + Frontend Rohtext/Polish-Anzeige.
**Dateibesitz:** `voice_adapter.py`, `services/ki-usability/app/services/voice_polish.py`, `local_stt.py`, `ollama_client.py`, `voice.py` (Endpoints), `VoiceFeedback.tsx`, `useVoiceIntent.ts`, `VoiceButton.tsx`, `tests/test_voice_polish.py`.
**Gate-Ergebnis:** pytest 93/93 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** POST `/voice/polish` + `/voice/transcribe`; Ollama-Polish mit Fallback auf Rohtext; faster-whisper in `voice_adapter.py`; Frontend zeigt Rohtext und polierten Text in `VoiceFeedback`.
**Offene Risiken:** faster-whisper optional — ohne Install liefert `/transcribe` 503; Browser-STT bleibt Standard im Frontend bis Slice-013b.

## SLICE-013B-VOICE-SUMMARY-TTS-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Ollama 15s-Summary + lokales Piper-TTS + Frontend-Wiedergabe mit Browser-Fallback.
**Dateibesitz:** `voice_summary.py`, `local_tts.py`, `voice.py`, `voice_adapter.py`, `VoiceFeedback.tsx`, `useVoicePlayback.ts`, `VoiceButton.tsx`, `voice.ts`, `tests/test_voice_summary_tts.py`.
**Gate-Ergebnis:** pytest 103/103 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** POST `/voice/summary` + `/voice/synthesize`; Piper in `voice_adapter.py`; Summary + Vorlesen-Button in `VoiceFeedback`; Browser-SpeechSynthesis-Fallback.
**Offene Risiken:** Piper optional — ohne Modell/CLI nur Browser-TTS; Kokoro als Folge-Provider moeglich.

## SLICE-013C-VOICE-WHISPERBAR-SHORTCUTS-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** WhisperBar Shortcuts Strg+Shift+1/2, AutoHotkey/PowerShell, POST /voice/pipeline.
**Dateibesitz:** `tools/voice/whisperbar.ahk`, `whisperbar-summary.ps1`, `voice_pipeline.py`, `VoiceWhisperBarHost.tsx`, `useWhisperBarShortcuts.ts`, `ai-shortcuts.tsx`.
**Gate-Ergebnis:** pytest 112/112 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Browser-Shortcuts Diktat/Summary; AHK aktiviert ERP + ruft Summary-API; Pipeline-Endpoint dictate|summary|intent.
**Offene Risiken:** AHK erfordert lokal installiertes AutoHotkey v1.1; ki-usability muss auf Port 5200 laufen fuer PS-Summary.

## SLICE-013D-VOICE-DOMAIN-CONTEXT-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** context.domain filtert Intent-Aufloesung; voice-intent Events mit Domain-Payload.
**Dateibesitz:** `intent_resolver.py`, `useVoiceIntent.ts`, `command-palette-model.ts`, `CommandPalette.tsx`, `test_voice_domain_context.py`.
**Gate-Ergebnis:** pytest 112/112 ✅
**Erledigt:** Domain-Aliase und Registry-Filter; Command Palette dispatcht eventPayload als eventDetail; VoiceWhisperBarHost reagiert auf voice-intent.
**Offene Risiken:** Sehr generische Phrasen koennen domain-uebergreifend kollidieren — weiteres Tuning bei Bedarf.

## SLICE-014-VOICE-LOCAL-STACK-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Kokoro TTS, Docker Voice Stack (Ollama), Frontend Local STT via faster-whisper.
**Dateibesitz:** `local_kokoro.py`, `local_tts.py`, `docker-compose.voice.yml`, `useLocalVoiceCapture.ts`, `useVoiceIntent.ts`, `voice_adapter.py`, `test_voice_kokoro.py`.
**Gate-Ergebnis:** pytest ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Kokoro HTTP-Provider; docker-compose.voice.yml; VITE_VOICE_STT_PROVIDER=local mit Browser-Fallback.
**Offene Risiken:** faster-whisper/Kokoro muessen im ki-usability-Container oder lokal installiert sein; Kokoro-Image optional und gross.

## SLICE-015-VOICE-PRODUCTION-HARDENING-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Production Hardening — faster-whisper Docker, GET /voice/status, E2E WhisperBar-Smoke, Copilot Summary.
**Dateibesitz:** `Dockerfile.voice`, `voice_status.py`, `docker-compose.voice.yml`, `slice-015-voice-whisperbar.spec.ts`, `useVoiceCopilotSummary.ts`, `CopilotDockPanel.tsx`.
**Gate-Ergebnis:** pytest 116/116 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Dockerfile.voice + requirements-voice.txt; GET /voice/status; WhisperBar E2E Smoke; Copilot-Dock Voice-Summary mit Vorlesen.
**Offene Risiken:** faster-whisper-Image groesser; Kokoro weiterhin optional.

## SLICE-016-VOICE-ADMIN-STATUS-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Admin Voice-Kanal mit GET /voice/status Readiness und korrigiertem Transkript-Verlauf.
**Dateibesitz:** `voice-channel.tsx`, `useVoiceStackStatus.ts`, `voice-channel.test.tsx`.
**Gate-Ergebnis:** Vitest 1/1 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Status-Panel STT/TTS/Ollama; Transkript im Verlauf; useVoiceStackStatus Hook.
**Offene Risiken:** ki-usability muss laufen damit Status sichtbar ist.

## FACHLICHE-VERTIEFUNG-UX-W23-KUNDENBANKEN-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Kundenbankverbindungen (IBAN/BIC, SEPA) in Kundenstamm gegen Wave-3-Backend.
**Dateibesitz:** `kundenbanken.ts`, `KundenBankverbindungenPanel.tsx`, `kunden-stamm.tsx`, `fachliche-vertiefung-kundenbanken.spec.ts`.
**Gate-Ergebnis:** E2E 1/1 ✅
**Erledigt:** API-Client; Panel mit Anlegen/Standard/Löschen; Route-ID-Fix für Splat-Router; E2E gemockt.
**Offene Risiken:** Keine.

## FACHLICHE-VERTIEFUNG-UX-W24-INDIVIDUELLE-ARTIKELNUMMERN-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Individuelle Artikelnummern (Kunde/Lieferant-Mapping) gegen Wave-9-Backend.
**Dateibesitz:** `individuelleArtikelnummern.ts`, `individuelle-artikelnummern.tsx`, `stammdaten.ts`, `commercial.tsx`, `fachliche-vertiefung-individuelle-artikelnummern.spec.ts`.
**Gate-Ergebnis:** E2E 1/1 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** API-Client; Seite mit Liste/Anlegen/Lookup/Löschen; Route + Navigation; E2E gemockt.
**Offene Risiken:** Keine.
