from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.domains.crm.activity_contracts import (
    ActivityCreateCommand, ActivityDeleteCommand, ActivityRead, ActivityUpdateCommand,
    normalize_legacy_activity_status, normalize_legacy_activity_type,
)


def create(**values):
    return ActivityCreateCommand(type="call", title=" Test ", idempotency_key=" key ", **values)


def test_create_defaults_and_strips():
    command = create(main_topics=[" topic "])
    assert (command.title, command.idempotency_key, command.main_topics, command.date) == ("Test", "key", ["topic"], None)


@pytest.mark.parametrize("field", ["tenant_id", "author", "created_by", "updated_by"])
def test_write_rejects_identity_fields(field):
    with pytest.raises(ValidationError):
        create(**{field: "forged"})


@pytest.mark.parametrize("field", ["type", "title", "customer", "contact_person", "status", "assigned_to", "main_topics", "orders_placed", "follow_up_actions"])
def test_update_rejects_explicit_null(field):
    with pytest.raises(ValidationError):
        ActivityUpdateCommand(expected_version=1, idempotency_key="key", **{field: None})


def test_update_distinguishes_null_from_absence():
    command = ActivityUpdateCommand(expected_version=1, idempotency_key="key", date=None, description=None, contact_id=None, customer_id=None, opportunity_id=None)
    assert command.model_dump(exclude_unset=True)["date"] is None
    assert "title" not in command.model_dump(exclude_unset=True)


@pytest.mark.parametrize("values", [
    {"title": " "}, {"title": "x" * 201}, {"idempotency_key": " "},
    {"type": "Anruf"}, {"status": "overdue"}, {"status": "unknown"},
    {"main_topics": ["x" * 201]}, {"orders_placed": ["x"] * 101},
    {"follow_up_actions": [{"text": "legacy"}]},
])
def test_create_rejects_invalid_values(values):
    data = {"type": "call", "title": "test", "idempotency_key": "key", **values}
    with pytest.raises(ValidationError):
        ActivityCreateCommand(**data)


def test_version_and_idempotency_required():
    for data in ({"expected_version": 0, "idempotency_key": "key"}, {"expected_version": True, "idempotency_key": "key"}, {"expected_version": 1}):
        with pytest.raises(ValidationError):
            ActivityDeleteCommand(**data)


def test_legacy_normalization_is_explicit_and_unknown_fails():
    assert normalize_legacy_activity_type(" E-Mail ") == "email"
    assert normalize_legacy_activity_type("Sonstiges") == "note"
    assert normalize_legacy_activity_status("overdue") == "planned"
    assert normalize_legacy_activity_status("Storniert") == "cancelled"
    with pytest.raises(ValueError):
        normalize_legacy_activity_status("mystery")
    with pytest.raises(ValueError):
        normalize_legacy_activity_type("mystery")


def test_read_uses_central_overdue_rule(monkeypatch):
    from app.services import list_presets
    monkeypatch.setattr(list_presets, "is_business_overdue", lambda date, status: date is not None and status == "planned")
    result = ActivityRead(type="call", title="test", id="a", version=1, date=datetime.now(timezone.utc))
    assert result.model_dump()["overdue"] is True


def test_read_recomputes_caller_supplied_overdue_and_cancelled_is_closed():
    row=ActivityRead(type="call",title="Synthetic",id="a",version=1,status="cancelled",date="2020-01-01T00:00:00Z",overdue=True)
    assert row.model_dump()["overdue"] is False


def test_equivalent_instants_have_the_same_canonical_command_value():
    a=ActivityCreateCommand(type="call",title="Synthetic",idempotency_key="one",date="2026-10-29T10:00:00+01:00")
    b=ActivityCreateCommand(type="call",title="Synthetic",idempotency_key="one",date="2026-10-29T09:00:00Z")
    assert a.model_dump(mode="json")==b.model_dump(mode="json")


@pytest.mark.parametrize("raw", ['["one", "two"]','[]','["", "third"]'])
def test_cli_string_lists_are_typed_without_losing_order(raw):
    import json
    from valeo_cli.support import coerce_fields
    action={"inputFields":[{"key":"topics","type":"stringList"}]}
    assert coerce_fields(action,{"topics":raw})["topics"]==json.loads(raw)


@pytest.mark.parametrize("raw", ['{"text":"wrong"}','[1]','not json'])
def test_cli_rejects_non_string_list_before_transport(raw):
    from valeo_cli.support import coerce_fields
    with pytest.raises(ValueError):coerce_fields({"inputFields":[{"key":"topics","type":"stringList"}]},{"topics":raw})


@pytest.mark.parametrize("action,contract", [("create", ActivityCreateCommand), ("update", ActivityUpdateCommand), ("delete", ActivityDeleteCommand)])
def test_mcp_catalog_is_an_exact_projection_of_versioned_domain_schema(action, contract):
    from pathlib import Path
    import yaml
    catalog = yaml.safe_load((Path(__file__).resolve().parents[1] / "config/mcp_erp_tools.yaml").read_text(encoding="utf-8"))
    tool = next(item for item in catalog["tools"] if item["tool_id"] == "crm.activity." + action)
    expected = contract.model_json_schema()
    expected.pop("title", None)
    expected["properties"].pop("idempotency_key")
    expected["required"].remove("idempotency_key")
    if action != "create":
        expected["properties"]["activity_id"] = {"type": "string", "minLength": 1, "maxLength": 64}
        expected["required"].append("activity_id")
    assert tool["input_schema"] == expected
    assert tool["output_schema"]["properties"]["activity"] == ActivityRead.model_json_schema(mode="serialization")
    assert tool["domain_command"] == "crm.activity." + action + ".v1"
    assert tool["command_version"] == 1
    assert tool["agent_write_enabled"] is False
