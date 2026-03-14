"""
Wave-18 Follow-up Contract Tests: Settlement Contract Propagation

Konsolidiert Altpfade ausserhalb des direkten Process-Kernel-Kerns auf den
expliziten Settlement-Kompatibilitaetsvertrag.
"""

from __future__ import annotations

from app.core.exception_rules import DEFAULT_SETTLEMENT_EXCEPTION_CATALOG
from app.core.process_commands import get_process_command_catalog
from app.core.process_config import DEFAULT_PROCESS_VARIANTS
from app.core.settlement_commands import (
    SettlementCommandPayload,
    build_command_dispatch_log,
    build_settlement_dispatch_result,
)


def test_settlement_process_commands_expose_canonical_metadata():
    settlement_commands = [
        cmd for cmd in get_process_command_catalog() if cmd.aggregate == "settlement"
    ]
    assert settlement_commands
    for cmd in settlement_commands:
        assert cmd.canonical_aggregate == "agrar_settlement"
        assert cmd.canonical_process_definition_key == "quality_to_settlement"


def test_settlement_exception_catalog_exposes_canonical_metadata():
    assert DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.process_key == "settlement"
    assert DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.canonical_aggregate_type == "agrar_settlement"
    assert (
        DEFAULT_SETTLEMENT_EXCEPTION_CATALOG.canonical_process_definition_key
        == "quality_to_settlement"
    )


def test_settlement_process_variant_exposes_canonical_metadata():
    settlement_cfg = DEFAULT_PROCESS_VARIANTS["settlement"]
    assert settlement_cfg["canonical_aggregate_type"] == "agrar_settlement"
    assert settlement_cfg["canonical_process_definition_key"] == "quality_to_settlement"


def test_settlement_command_payload_defaults_to_canonical_metadata():
    payload = SettlementCommandPayload(
        command_id="settlement.create",
        tenant_id="t1",
        actor="user-1",
    )
    assert payload.canonical_aggregate_type == "agrar_settlement"
    assert payload.canonical_process_definition_key == "quality_to_settlement"


def test_settlement_dispatch_log_carries_canonical_metadata():
    payload = SettlementCommandPayload(
        command_id="settlement.post",
        tenant_id="t1",
        actor="user-1",
    )
    result = build_settlement_dispatch_result(payload, dispatch_id="disp-1")
    log = build_command_dispatch_log(result, actor="user-1")
    assert log.canonical_aggregate_type == "agrar_settlement"
    assert log.canonical_process_definition_key == "quality_to_settlement"
