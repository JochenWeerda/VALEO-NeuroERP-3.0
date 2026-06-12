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
| Waage / Wiegeschein | Agrar-/Supply-Endpunkte (z. B. Waage, Annahme) | Verknüpfung zu `delivery_note_ref` in `tour_stops` möglich, **kein durchgängiger Read-Spine dokumentiert** |
| Settlement / Abrechnung | Process-Kernel, Agrar-Settlement | Ziel-Ende der Kette |

## 2. Bruchstellen (fachlich / technisch)

1. **Runtime-Schema (`CREATE TABLE IF NOT EXISTS`)** in Logistik-Routern — **geschlossen**
   am 2026-06-12 durch **LOG-PROD-001** (Alembic `log_logistics_core_20260612`, Router ohne
   Lazy-DDL). Gleiches Muster wie RFQ (PROC-RFQ-001).
2. **Kein gemeinsamer Lifecycle-Test** (Spine → Mutation → Storno → UAT) für Tour/Fracht ↔ Lieferschein ↔ Settlement.
3. **Playwright @smoke** war lokal gegen Dev unzuverlässig — **behoben** durch Dev-Token-Session (`docs/quality-assurance/playwright-smoke-auth.md`).
4. **`delivery_note_ref`** in `tour_stops` ist Feld ohne erzwungene FK/Validierung — operative Durchgängigkeit:
   Read-Auflösung über **LOG-SPINE-RAND-001** (`/logistik/sales-delivery-note-by-ref`, optional Tour-Hints); volle UI-/Picker-/Seed-Spine bleibt **LOG-SPINE-001**.

## 3. Empfohlene Slice-Reihenfolge (nach Audit)

1. **LOG-PROD-001 (erledigt):** Alembic `log_logistics_core_20260612`, `_ensure_*` entfernt,
   `tests/test_logistics_integration.py`.
2. **LOG-SPINE-RAND-001 (2026-06-12):** Read-only API
   ``GET /api/v1/logistik/sales-delivery-note-by-ref`` und optional
   ``GET /api/v1/logistik/tours/{id}?include_delivery_hints=true`` — Auflösung
   ``delivery_note_ref`` → ``domain_sales.delivery_notes`` (UUID oder Nummer), tenant-pflichtig.
3. **LOG-SPINE-001:** Read-Spine „Lieferschein → Tour-Stop / Frachtposition“ (Picker + API), Seed-DEMO.
4. **LOG-LIFE-001:** Mutationen (Stop bestätigen, POD) + **Storno/Fail-closed** + UAT-Skript (analog `proc_match_lifecycle_uat.py`).
5. **UI:** ein Arbeitsraum „Tour / Frachtbrief“ mit OperationalCaseHeader (DOM-SUPPLY-004-Stil).

## 4. Bewusst nicht in dieser Welle

HRM, POS, Webshop, Agent-Ops, Compliance/Meldewesen (extern / P3 laut Depth-Plan).

## Verweise

- Depth-Plan: `docs/project-context/domain-depth-plan-2026-05-17.md`
- Playwright Auth: `docs/quality-assurance/playwright-smoke-auth.md`
- Process-Kernel: `docs/architecture/process-kernel/STATUS.md`
