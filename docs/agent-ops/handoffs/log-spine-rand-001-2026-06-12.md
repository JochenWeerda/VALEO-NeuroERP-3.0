# Handoff: Logistik Read-Spine + LOG-PROD Abschluss (2026-06-12)

## Umgesetzte Slice-IDs

- **LOG-SPINE-001** (abgeschlossen): Tourenplanung UI, `stop_count` auf Tour-Liste, PATCH `delivery_note_ref`, Seed `seed_demo_logistics_spine.py`.
- **LOG-SPINE-RAND-001** (abgeschlossen): Read-only Auflösung `delivery_note_ref` → `domain_sales.delivery_notes`.
- **LOG-PROD-001** (nachgezogen committet): Alembic `log_logistics_core_20260612`, `logistics_freight` ohne Runtime-DDL, Integrationstests.

## Fachlicher Nutzen

- Dispatcher/Touren-UI kann Lieferschein-Metadaten zu einem Stopp-Referenzfeld nachladen, ohne FK-Migration.
- Tenant-Zwang auf Resolve-Endpunkt; gleiche Referenzlogik wie Verkaufs-Storno (UUID oder `delivery_note_number`).

## Geänderte / neue Dateien (Kern)

- `app/api/v1/endpoints/logistics_tours.py` — `_lookup_sales_delivery_note`, `GET .../sales-delivery-note-by-ref`, `get_tour(..., include_delivery_hints=...)`
- `packages/frontend-web/src/lib/api/logistics-tours.ts`, `misc-modules.ts`, `tourenplanung.tsx`, `scripts/seed_demo_logistics_spine.py`
- `docs/workflows/wave-physical-chain-logistics-audit-2026-06-12.md`
- `docs/agent-ops/slices/LOG-SPINE-RAND-001.yaml`, `active-workboard.md`
- (LOG-PROD) `alembic/versions/log_logistics_core_20260612.py`, `logistics_freight.py`, `tests/test_logistics_integration.py`, `tests/test_logistics_tour_freight.py`, `LOG-PROD-001.yaml`, `domain-depth-plan`

## Tests

- `pytest tests/test_logistics_delivery_hint.py tests/test_logistics_tour_freight.py -o addopts="--tb=short -q" -q` → **14 passed** (ohne repo-weites `--cov`, sonst Ratchet bei Einzeldatei).
- `pnpm --filter @valero-neuroerp/frontend-web type-check` → **0 Fehler** (nach Fix `DeliveryNoteHint`).

## Restrisiken

- `sales_order_id` im SELECT setzt voraus, dass Migration `sales_o2c_link_20260610` auf der DB gelaufen ist (Standard bei `upgrade head`).
- `include_delivery_hints` pro distinct `delivery_note_ref` ein DB-Roundtrip — bei sehr großen Touren ggf. später batchen (Folge-Optimierung).

## Folgeauftrag (nächster 3h-Block)

1. **LOG-SPINE-001:** UI-Picker + Seed-DEMO + ein Batch-Read falls nötig.
2. Frontend: `packages/frontend-web` API-Helfer + Tour-Maske optional `include_delivery_hints=true`.
3. `pytest tests/test_logistics_integration.py -m integration` gegen Postgres mit migrierter DB.

## Commits (Branch)

- `chore(workboard): claim LOG-SPINE-RAND-001`
- `feat(logistics): LOG-SPINE-RAND-001 Lieferschein-Ref Read-Spine`
- `feat(logistics): LOG-PROD-001 Alembic domain_logistics`
