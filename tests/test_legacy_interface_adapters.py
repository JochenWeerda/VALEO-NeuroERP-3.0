from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.services.legacy_interface_adapter_service import (
    LegacyAdapterError,
    LegacyInterfaceAdapterService,
)

pytestmark = pytest.mark.unit


def result(*, first=None, one=None, all_rows=None, scalar=None):  # noqa: ANN001, ANN201
    value = MagicMock()
    value.mappings.return_value.first.return_value = first
    value.mappings.return_value.one.return_value = one
    value.mappings.return_value.all.return_value = all_rows or []
    value.scalar_one.return_value = scalar
    return value


def test_catalog_exposes_only_fixed_inactive_profiles() -> None:
    catalog = LegacyInterfaceAdapterService(MagicMock(), "tenant-1").catalog()
    assert {item["profile_key"] for item in catalog} == {"l3_standard", "unimet"}
    assert all(
        item["status"] == "inactive" and item["execution_enabled"] is False
        for item in catalog
    )


def test_configuration_requires_real_format_contract_and_blocks_pilot() -> None:
    service = LegacyInterfaceAdapterService(MagicMock(), "tenant-1")
    with pytest.raises(LegacyAdapterError, match="unvollstaendig"):
        service.configure(
            "unimet",
            {"format_contract": {}, "field_mapping": {"x": "source_ref"}},
            actor="u",
            reason="test format",
        )
    contract = {
        "encoding": "utf-8",
        "decimal_separator": ",",
        "date_format": "DD.MM.YYYY",
        "record_types": ["invoice"],
        "sample_hash": "sha256:x",
    }
    with pytest.raises(LegacyAdapterError, match="Kundenfreigabe"):
        service.configure(
            "unimet",
            {
                "format_contract": contract,
                "field_mapping": {"x": "source_ref"},
                "status": "pilot",
            },
            actor="u",
            reason="test pilot",
        )


def test_intake_detects_payload_conflict_for_same_external_id() -> None:
    db = MagicMock()
    db.execute.return_value = result(
        first={"id": "b1", "payload_hash": "other", "status": "received"}
    )
    with pytest.raises(LegacyAdapterError, match="abweichendem Payload"):
        LegacyInterfaceAdapterService(db, "tenant-1").intake(
            "l3_standard", "ext-1", {"records": []}, actor="u"
        )


def test_unconfigured_intake_is_quarantined_and_never_executed() -> None:
    db = MagicMock()
    db.execute.side_effect = [
        result(first=None),
        result(first=None),
        MagicMock(),
        MagicMock(),
    ]
    created = LegacyInterfaceAdapterService(db, "tenant-1").intake(
        "unimet", "ext-1", {"records": [{"x": 1}]}, actor="u"
    )
    assert created["status"] == "quarantine" and created["duplicate"] is False
    insert_params = db.execute.call_args_list[2].args[1]
    assert insert_params["error_code"] == "PROFILE_NOT_READY"


def test_stage_uses_declarative_mapping_and_keeps_execution_disabled() -> None:
    db = MagicMock()
    batch = {
        "profile_key": "l3_standard",
        "status": "received",
        "profile_status": "ready",
        "field_mapping": {"typ": "record_type", "ref": "source_ref", "summe": "amount"},
        "raw_payload": {"records": [{"typ": "invoice", "ref": "R-1", "summe": 10}]},
    }
    db.execute.side_effect = [
        result(first=batch),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    ]
    staged = LegacyInterfaceAdapterService(db, "tenant-1").stage(
        "b1", actor="u", reason="mapping test"
    )
    assert staged == {
        "id": "b1",
        "status": "staged",
        "staged_count": 1,
        "mismatch_count": 0,
        "execution_enabled": False,
    }
    staging_params = db.execute.call_args_list[2].args[1]
    assert '"record_type": "invoice"' in staging_params["payload"]


def test_reconciliation_and_approval_are_gates_not_booking() -> None:
    db = MagicMock()
    batch = {"profile_key": "unimet", "status": "staged", "record_count": 2}
    counts = {"total": 2, "valid": 2}
    db.execute.side_effect = [
        result(first=batch),
        result(one=counts),
        MagicMock(),
        MagicMock(),
    ]
    reconciled = LegacyInterfaceAdapterService(db, "tenant-1").reconcile(
        "b1", actor="u", reason="counts match"
    )
    assert (
        reconciled["status"] == "reconciled"
        and reconciled["execution_enabled"] is False
    )

    db2 = MagicMock()
    db2.execute.side_effect = [result(first={"profile_key": "unimet"}), MagicMock()]
    approved = LegacyInterfaceAdapterService(db2, "tenant-1").approve(
        "b1", actor="u", reason="pilot only"
    )
    assert approved["status"] == "approved" and approved["execution_enabled"] is False
    assert approved["next_gate"] == "customer_format_and_target_adapter_activation"


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("schnittstelle/legacy-adapter-monitor")
    assert definition and definition["tables"][0]["serverPagination"] is True
    assert _check_readiness(definition)["generatorReady"] is True
