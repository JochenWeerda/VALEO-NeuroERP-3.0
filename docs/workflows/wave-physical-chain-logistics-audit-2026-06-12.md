# Welle „Physische Landhandels-Kette“ — Tiefen-Audit Logistik (Task 0)

**Stand:** 2026-06-12
**Ziel:** Medienbruch-Reduktion entlang **Waage → Annahme → Lager → Lieferschein → Fracht/Tour → Abrechnung**
**Scope:** In-Repo; keine parallelen DOM-*-005-Inseln; erst Audit, dann gezielte Lifecycle-Slices.

## 1. Ist-Inventar (API, aus Router / Code)

| Bereich | Prefix / Modul | Bemerkung |
|---------|----------------|-----------|
| Touren / Stopps / ePOD | `GET/POST …` unter `app/api/v1/endpoints/logistics_tours.py` → `/logistik/...` | `domain_logistics.tour_stops`, `tour_events`; **`_ensure_schema` Runtime-DDL** |
| Frachtkosten / Tarife | `logistics_freight.py` → `/logistik/...` | `freight_tariffs`; **`_ensure_freight_table` Runtime-DDL** |
| Verkauf Lieferschein | `sales-shipping`, Match O2C | SUPPLY-/SALES-004 Anknüpfungspunkt |
| Waage / Wiegeschein | Agrar-/Supply-Endpunkte (z. B. Waage, Annahme) | Verknüpfung zu `delivery_note_ref` in `tour_stops` möglich, **kein durchgängiger Read-Spine dokumentiert** |
| Settlement / Abrechnung | Process-Kernel, Agrar-Settlement | Ziel-Ende der Kette |

## 2. Bruchstellen (fachlich / technisch)

1. **Runtime-Schema (`CREATE TABLE IF NOT EXISTS`)** in Logistik-Routern — nicht production-gleich mit Alembic-only-Politik; gleiches Muster wie früher RFQ (bereinigt in PROC-RFQ-001).
2. **Kein gemeinsamer Lifecycle-Test** (Spine → Mutation → Storno → UAT) für Tour/Fracht ↔ Lieferschein ↔ Settlement.
3. **Playwright @smoke** war lokal gegen Dev unzuverlässig — **behoben** durch Dev-Token-Session (`docs/quality-assurance/playwright-smoke-auth.md`).
4. **`delivery_note_ref`** in `tour_stops` ist Feld ohne erzwungene FK/Validierung — operative Durchgängigkeit offen.

## 3. Empfohlene Slice-Reihenfolge (nach Audit)

1. **LOG-PROD-001:** Alembic für `domain_logistics` (Touren + Fracht), `_ensure_*` entfernen, Integrationstests minimal.
2. **LOG-SPINE-001:** Read-Spine „Lieferschein → Tour-Stop / Frachtposition“ (Picker + API), Seed-DEMO.
3. **LOG-LIFE-001:** Mutationen (Stop bestätigen, POD) + **Storno/Fail-closed** + UAT-Skript (analog `proc_match_lifecycle_uat.py`).
4. **UI:** ein Arbeitsraum „Tour / Frachtbrief“ mit OperationalCaseHeader (DOM-SUPPLY-004-Stil).

## 4. Bewusst nicht in dieser Welle

HRM, POS, Webshop, Agent-Ops, Compliance/Meldewesen (extern / P3 laut Depth-Plan).

## Verweise

- Depth-Plan: `docs/project-context/domain-depth-plan-2026-05-17.md`
- Playwright Auth: `docs/quality-assurance/playwright-smoke-auth.md`
- Process-Kernel: `docs/architecture/process-kernel/STATUS.md`
