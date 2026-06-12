# Welle „Physische Landhandels-Kette“ — Tiefen-Audit Logistik (Task 0)

**Stand:** 2026-06-12
**Ziel:** Medienbruch-Reduktion entlang **Waage → Annahme → Lager → Lieferschein → Fracht/Tour → Abrechnung**
**Scope:** In-Repo; keine parallelen DOM-*-005-Inseln; erst Audit, dann gezielte Lifecycle-Slices.

## 1. Ist-Inventar (API, aus Router / Code)

| Bereich | Prefix / Modul | Bemerkung |
|---------|----------------|-----------|
| Touren / Stopps / ePOD | `GET/POST …` unter `app/api/v1/endpoints/logistics_tours.py` → `/logistik/...` | `domain_logistics.tours`, `tour_stops`, `tour_events`; Schema per Alembic `log_logistics_core_20260612` |
| Frachtkosten / Tarife | `logistics_freight.py` → `/logistik/...` | `freight_tariffs`; gleiche Alembic-Revision |
| Verkauf Lieferschein | `sales-shipping`, Match O2C | SUPPLY-/SALES-004 Anknüpfungspunkt |
| Waage / Wiegeschein | Agrar-/Supply-Endpunkte (z. B. Waage, Annahme) | Verknüpfung zu `delivery_note_ref` in `tour_stops`; Read-Spine zu Verkaufs-LS siehe **LOG-SPINE-001** |
| Settlement / Abrechnung | Process-Kernel, Agrar-Settlement | Ziel-Ende der Kette |

## 2. Bruchstellen (fachlich / technisch)

1. **Runtime-Schema (`CREATE TABLE IF NOT EXISTS`)** in Logistik-Routern — **geschlossen**
   am 2026-06-12 durch **LOG-PROD-001** (Alembic `log_logistics_core_20260612`, Router ohne
   Lazy-DDL). Gleiches Muster wie RFQ (PROC-RFQ-001).
2. **Kein gemeinsamer Lifecycle-Test** (Spine → Mutation → Storno → UAT) für Tour/Fracht ↔ Lieferschein ↔ Settlement — **geschlossen** am 2026-06-12 durch **LOG-CHAIN-001**: Integrationstest
   ``test_chain_lifecycle_ls_tour_hints_freight_supply_read`` in ``tests/test_logistics_integration.py``
   (Voraussetzung ``DEMO-LS-001`` aus ``seed_demo_sales.py``; sonst Skip), UAT
   ``scripts/uat/logistics_chain_lifecycle_uat.py`` (Read-Spine inkl.
   ``GET /api/v1/supply-chain/traceability/tickets``; volle Mutation nur mit LS-Seed).
   Settlement-Ende der Kette bleibt bewusst **read-only** (Traceability-Übersicht), keine Abrechnungs-Mutation in diesem Slice.
3. **Playwright @smoke** war lokal gegen Dev unzuverlässig — **behoben** durch Dev-Token-Session (`docs/quality-assurance/playwright-smoke-auth.md`).
4. **`delivery_note_ref`** — Read-Auflösung und UI: **LOG-SPINE-RAND-001** (API) +
   **LOG-SPINE-001** (Tourenplanung, `seed_demo_logistics_spine.py`). Keine DB-FK-Pflicht.

## 3. Empfohlene Slice-Reihenfolge (nach Audit)

1. **LOG-PROD-001 (erledigt):** Alembic `log_logistics_core_20260612`, `_ensure_*` entfernt,
   `tests/test_logistics_integration.py`.
2. **LOG-SPINE-RAND-001 (2026-06-12):** Read-only API
   ``GET /api/v1/logistik/sales-delivery-note-by-ref`` und optional
   ``GET /api/v1/logistik/tours/{id}?include_delivery_hints=true`` — Auflösung
   ``delivery_note_ref`` → ``domain_sales.delivery_notes`` (UUID oder Nummer), tenant-pflichtig.
3. **LOG-SPINE-001 (erledigt 2026-06-12):** Frontend Tourenplanung (Resolve + Tour-Hints),
   `GET /logistik/tours` mit `stop_count`, PATCH `delivery_note_ref`, Seed `seed_demo_logistics_spine.py`
   (nach `seed_demo_sales.py`).
4. **LOG-CHAIN-001 (erledigt 2026-06-12):** Ketten-Lifecycle-Test + UAT (Audit Bruchstelle 2) —
   LS-Ref → Tour-Hints → Fracht simulate → Traceability-Tickets (Read) → Tour-Storno;
   Artefakte siehe Punkt 2 oben.
5. **LOG-LIFE-001 (erledigt 2026-06-12):** Storno-Endpunkte fail-closed
   (`POST …/tours/{id}/cancel`, `POST …/tours/{id}/stops/{sid}/cancel`), Frontend
   Status ``STORNIERT`` (KPI + Badges), Integrationstest + UAT-Skript
   ``scripts/uat/logistics_tour_lifecycle_uat.py`` (analog Match-UAT).
6. **UI:** ein Arbeitsraum „Tour / Frachtbrief“ mit OperationalCaseHeader (DOM-SUPPLY-004-Stil).
   **Stand 2026-06-12:** Route ``/logistik/tour-fracht-arbeitsraum`` („Tour & Fracht (Dispo)“) mit
   gemeinsamer Lage, Tasks, Entscheidungspanel und Sprung zu Tourenplanung/Frachtbriefen;
   Logistik-Domain-Landing zeigt diese Seite zuerst.

## 4. Bewusst nicht in dieser Welle

HRM, POS, Webshop, Agent-Ops, Compliance/Meldewesen (extern / P3 laut Depth-Plan).

## Verweise

- Depth-Plan: `docs/project-context/domain-depth-plan-2026-05-17.md`
- Playwright Auth: `docs/quality-assurance/playwright-smoke-auth.md`
- Process-Kernel: `docs/architecture/process-kernel/STATUS.md`
