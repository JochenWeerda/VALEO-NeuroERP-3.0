# Handshake: Cursor Agent → Claude Code (SPEC-P1-04/08, Prompt A8)

Stand: 2026-07-06
Von: Cursor Agent
An: Claude Code
Slice: `SPEC-P1-04-08-A8`
Branch: `fix/pii-remediation`

## Kontext in einem Satz

Production-Readiness Prompt A8 ist umgesetzt: keine gestubten `commandEndpoint`s mehr auf nativen ScreenDefinitions, gemeinsame Mask-ActionRuntime mit Audit/Outbox, Chargen-FEFO über MHD.

## Geliefert

| Bereich | Inhalt |
|---|---|
| **SPEC-P1-04** | `MaskActionRuntime` (`validate`/`dryRun`/`propose`/`execute`); Endpoints in `mask_actions.py` + AP/Mahnung/Bestellung auf Runtime; Inventur `scripts/check_mask_command_endpoint_inventory.py` |
| **SPEC-P1-08** | Lot-Attribute (`herkunft`, `sperrgrund`, `qs_status`, `received_at`); FEFO `ORDER BY mhd ASC NULLS LAST, created_at ASC`; Migration `inv_lot_depth_spec_p1_08` |
| **Tests** | `test_spec_p1_04_mask_commands.py`, `test_spec_p1_08_lot_fefo_pick.py`, `test_uix050_053_advanced_actions.py` angepasst |
| **Doku** | Workboard, Open-Gaps, Production-Readiness-Audit A8-Stand, `universal-mask-runtime-status.md` |

## Wichtige Dateien

- `app/services/mask_action_runtime_service.py` — zentrale Runtime
- `app/api/v1/endpoints/mask_actions.py` — Mask-CommandEndpoints
- `app/core/screen_definitions.py` — `commandEndpoint` ohne `stubReason` (native SDs)
- `app/services/inventory_lot_trace_service.py` — FEFO-Pick
- `alembic/versions/inv_lot_depth_spec_p1_08.py`
- `scripts/check_mask_command_endpoint_inventory.py`

## Verifikation (lokal 2026-07-06)

```bash
python scripts/check_mask_command_endpoint_inventory.py
# → Exit 0 (26 native SDs, 0 stubReason)

pytest tests/test_spec_p1_04_mask_commands.py tests/test_spec_p1_08_lot_fefo_pick.py tests/test_uix050_053_advanced_actions.py -q --no-cov
# → 26 passed
```

Vor Deploy: `alembic upgrade head` (Migration `inv_lot_depth_spec_p1_08`).

## Bekannte Grenzen / Follow-up

1. **Execute-Pfad** simuliert Status-Mutation + Outbox/Audit — keine vollständige Domain-Persistenz (PDF-Druck, Lagerbuchungen, Zahlungslauf-Freigabe in FIBU).
2. **`pick_lots_fefo`** committet pro Lot via `consume_lot` — bei Bedarf in eine Transaktion ziehen.
3. **Rollout-Pilot-SDs** (`temporary=True`) behalten ggf. `stubReason` auf `edit` — Inventur schließt diese aus.
4. **CI-Inventur** optional in `universal-mask-ci.yml` oder `quality-gate.yml` einhängen.

## Claude: Bitte beachten

- Vor weiteren Mask-Action-Änderungen Slice claimen (`chore(workboard): claim …`).
- Neue Actions über `run_mask_action()` — nicht ad-hoc Stub-Responses.
- `require_audit_reason=True` für critical Actions (`payment-run/freigeben`, `stornieren`).
- FEFO-Tests bei Lot-Logik-Änderungen mitführen.

## Nächster sinnvoller Schritt

Optional pro Action echte Domain-Services anbinden (Druck-PDF, Lager-Storno, Zahlungslauf-Freigabe). Oder Prompt A9 (Archiv-Konsolidierung) — siehe separaten Commit auf dem Branch falls bereits staged.
