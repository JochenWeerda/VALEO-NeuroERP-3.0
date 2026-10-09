---
title: Fuhrpark Tenant CE 2026-10-09
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: abgeschlossen
last_reviewed: 2026-10-09
description: Additive tenant_id fuer Fuhrpark-Stammtabellen + CE/MCP Isolation.
---

# FUHRPARK-TENANT-CE-20261009

## Gewaehlt / geliefert

Additive `tenant_id` (Backfill `legacy-unassigned`) auf:

- `domain_ops.ops_fahrzeuge`
- `domain_ops.ops_fuhrpark_terminarten`
- `domain_ops.ops_fuhrpark_rechnungen`
- `domain_ops.ops_fuhrpark_ausgehende_dokumente`

Mandantenfilter auf allen Reads/Writes der Fuhrpark-Repos und REST-Routen.
Tenant-scoped Unique Keys: Kennzeichen, Terminart, Rechnungsnummer.

| Mask-Action | Klassifikation | CE / MCP |
|-------------|----------------|----------|
| `fuhrpark/fahrzeug-stamm:speichern` | mapped | CE `/api/v1/fuhrpark/fahrzeuge/actions/speichern` + `logistik.fahrzeug.speichern` |
| `fuhrpark/fahrzeug-stamm:loeschen` | mapped | CE `/api/v1/fuhrpark/fahrzeuge/{entity_id}/actions/loeschen` + `logistik.fahrzeug.loeschen` |
| `fuhrpark/terminarten:speichern` | mapped | CE + `logistik.terminart.speichern` |
| `fuhrpark/rechnungen:speichern` | mapped | CE + `logistik.rechnung.speichern` |
| `fuhrpark/ausgehende-dokumente:speichern` | mapped | CE + `logistik.ausgehendes_dokument.speichern` |

Isolation: Token-Mandant, Payload-`tenant_id` gestrippt, MCP Override 422,
Cross-Tenant Lookup → 404, dryRun ohne Schreibwirkung.

## Kennzahlen

| Metrik | Wert |
|--------|------|
| mapped | **41** (+5) |
| blocked_missing_tenant | **0** |
| blocked_no_endpoint | **0** |
| local_ui | **13** |
| open_high | **1** (Zahlauf) |
| Registry | **56** Tools (+5) |

## Migration / Probe

- Claim: `FUHRPARK-TENANT-CE-20261009`
- Revision: `fuhrpark_tenant_ce_20261009` (revises `postfach_microsoft_20261008`)
- Probe: `alembic upgrade fuhrpark_tenant_ce_20261009` auf `valeo_probe` —
  Status danach `fuhrpark_tenant_ce_20261009`
- Keine neue DB/Container. Fremde WIP-Head `versandwege_echt_20261008` unberuehrt
  (Dual-Head im Worktree; Upgrade gezielt auf Fuhrpark-Revision).

## Handshake

Codex `COMMAND-ENDPOINT-GODFILE-20261009` (Touren/Training/Bestellvorschlag)
nicht beruehrt.

## Nachweis

```bash
python scripts/pruefstand_db.py --status
python scripts/generate_screen_action_catalog.py --check
python scripts/generate_mcp_mask_action_map.py --check
python -m pytest tests/test_mcp_mask_ce_fuhrpark_tenant.py \
  tests/test_mcp_mask_ce_batch4_training.py \
  tests/test_mcp_mask_action_map.py tests/test_mcp_tool_registry.py \
  tests/test_mcp_local_action_classification.py \
  --noconftest -q --override-ini addopts=''
```

Kein Commit/Push.

## Unabhaengige Integrationsabnahme

Die nachfolgende Codex-Abnahme fand21 verbleibende Fehler im hier beschriebenen
Stand und schloss sie mit echten PG-Wirkungsvertraegen. Massgeblich ist jetzt
[Fuhrpark/MCP-Isolationsabnahme](fuhrpark-mcp-isolation-20261009.md).
