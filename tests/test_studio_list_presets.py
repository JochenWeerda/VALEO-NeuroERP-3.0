"""Server-owned selectors: no caller identity, executable expressions or hidden partial pages."""
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.services import list_presets as presets
from app.services.mask_table_query import project_rows
from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn
from app.services.studio_list_contracts import ListPreset


def group(kind="choice", key="state", field="status", values=("all", "planned", "completed"), **extra):
    return dict(key=key, label=key, field=field, kind=kind,
                options=[dict(value=value, label=value) for value in values], **extra)


def experience():
    return {"presets": [group(), group("actor", "owner", "assigned_to", ("all", "mine")),
        group("date", "when", "date", ("all", "today", "week", "overdue"), completionField="status")]}


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    monkeypatch.setenv("BUSINESS_TIMEZONE", "Europe/Berlin")
    monkeypatch.setattr(presets, "business_now", lambda: datetime(2026, 10, 29, 12, tzinfo=presets.business_timezone()))


@pytest.mark.parametrize("value", [None, "", "broken", "2026-13-42"])
def test_undated_and_invalid_dates_are_never_invented(value):
    assert presets.business_instant(value) is None
    assert not presets.is_business_overdue(value, "planned")


def test_naive_utc_matches_shared_business_clock_at_midnight():
    assert presets.business_instant("2026-10-28T23:30:00").date().isoformat() == "2026-10-29"
    assert not presets.is_business_overdue("2026-10-28T23:30:00", "planned")
    assert presets.is_business_overdue("2026-10-28T10:00:00Z", "planned")
    assert not presets.is_business_overdue("2026-10-28T10:00:00Z", "completed")


@pytest.mark.parametrize("selection,expected", [("today", [2]), ("week", [1, 2, 3]), ("overdue", [1])])
def test_calendar_ranges_are_business_days_monday_based_and_exclude_undated(selection, expected):
    rows = [dict(id=1, date="2026-10-26T00:00:00+01:00", status="planned"),
            dict(id=2, date="2026-10-28T23:30:00Z", status="planned"),
            dict(id=3, date="2026-11-01T23:59:00+01:00", status="planned"),
            dict(id=4, date="2026-11-02T00:00:00+01:00", status="planned"),
            dict(id=5, date=None, status="planned"),
            dict(id=6, date="2026-10-25T12:00:00Z", status="completed")]
    assert [row["id"] for row in presets.apply_list_presets(rows, experience(), {"when": selection})] == expected


def test_combined_registered_filters_and_verified_actor(monkeypatch):
    monkeypatch.setattr(presets, "current_identity", lambda: SimpleNamespace(subject="actor-1", claims={"email":"owner@example.invalid", "name":"Owner"}))
    rows = [dict(id=1, status="planned", assigned_to="actor-1"),
            dict(id=2, status="completed", assigned_to="actor-1"),
            dict(id=3, status="planned", assigned_to="other"),
            dict(id=4, status="planned", assigned_to="OWNER@example.invalid")]
    assert [row["id"] for row in presets.apply_list_presets(rows, experience(), {"owner":"mine", "state":"planned"})] == [1,4]


def test_mine_requires_verified_identity_even_when_no_rows_exist(monkeypatch):
    def unauthenticated():
        raise HTTPException(401, "Verified execution identity required")
    monkeypatch.setattr(presets, "current_identity", unauthenticated)
    with pytest.raises(HTTPException) as error:
        presets.apply_list_presets([], experience(), {"owner":"mine"})
    assert error.value.status_code == 401


@pytest.mark.parametrize("selection", [{"tenant_id":"foreign"}, {"owner":"other-user"}, {"when":"tomorrow"}, {"state":"__proto__"}])
def test_arbitrary_fields_values_and_actor_injection_rejected(selection):
    with pytest.raises(HTTPException) as error:
        presets.apply_list_presets([], experience(), selection)
    assert error.value.status_code == 422


@pytest.mark.parametrize("change", [dict(options=[dict(value="mine",label="Mine")]*2),
    dict(kind="actor"), dict(kind="date"), dict(completionField="status"), dict(key="__proto__"), dict(command="delete")])
def test_presets_are_strict_bounded_declarations(change):
    with pytest.raises(ValidationError):
        ListPreset.model_validate({**group(), **change})


def test_complete_projection_filters_before_count_and_does_not_truncate_to_ui_page():
    table = {"columns":[{"key":"status"},{"key":"id"}], "listExperience":{"presets":[group()],"aggregates":[]}}
    query = MaskDataReadIn(screen_id="test/list", source_key="rows", table_key="list", complete=True,
                           limit=2, preset_filters={"state":"planned"})
    rows = [dict(id=n,status="planned" if n%2 == 0 else "completed") for n in range(130)]
    result = project_rows(rows,table,query)
    assert result["total"] == 65
    assert len(result["items"]) == 65
    assert result["pages"] == 1 and not result["has_next"]


@pytest.mark.parametrize("changes", [dict(complete=True, page=2), dict(complete=True,table_key=None),
    dict(preset_filters={"x":"all"},table_key=None), dict(preset_filters={"":"all"}),
    dict(preset_filters={"x":""}), dict(preset_filters={str(n):"all" for n in range(9)})])
def test_read_request_shape_is_bounded(changes):
    with pytest.raises(ValidationError):
        MaskDataReadIn.model_validate({"screen_id":"test/list", "source_key":"rows", "table_key":"list", **changes})


def test_source_complete_read_collects_once_and_presets_before_paging(monkeypatch):
    import httpx
    from app.services import mask_data_read as source
    table = {"key":"list", "dataSourceKey":"rows", "columns":[{"key":"id"},{"key":"status"}]}
    declaration = {"tables":[table], "listExperience":{"searchFields":["id"],"aggregates":[],"presets":[group()]},
        "dataSources":[{"key":"rows","endpoint":"/api/v1/test"}]}
    monkeypatch.setattr(source,"get_screen_definition",lambda *a,**k:declaration)
    monkeypatch.setattr(source,"_query_parameters",lambda _:frozenset({"skip","limit"}))
    calls=[]
    def endpoint(request):
        assert request.headers["authorization"] == "Bearer verified-caller"
        assert "x-tenant-id" not in request.headers
        start = int(request.url.params["skip"])
        calls.append(start)
        return httpx.Response(200,json={"items":[dict(id=str(n),status="planned" if n%2==0 else "completed")
            for n in range(start,min(start+50,130))],"total":130})
    q=MaskDataReadIn(screen_id="test/list",source_key="rows",table_key="list",complete=True,
        preset_filters={"state":"planned"},limit=2)
    result=source.read_sync(q,"own","Bearer verified-caller",transport=httpx.MockTransport(endpoint))
    assert calls == [0,50,100]
    assert result.data["total"] == 65 and len(result.data["items"]) == 65
    assert not result.data["has_next"]


@pytest.mark.parametrize("selections", [{"unregistered":"all"},{"owner":"other"}])
def test_invalid_preset_rejected_before_any_source_request(monkeypatch,selections):
    import httpx
    from app.services import mask_data_read as source
    declaration={"tables":[{"key":"list","dataSourceKey":"rows","columns":[{"key":"id"},{"key":"assigned_to"}]}],
        "listExperience":{"searchFields":["id"],"aggregates":[],"presets":[group("actor","owner","assigned_to",("all","mine"))]},
        "dataSources":[{"key":"rows","endpoint":"/api/v1/test"}]}
    monkeypatch.setattr(source,"get_screen_definition",lambda *a,**k:declaration)
    def forbidden(request):
        pytest.fail("Invalid selector reached a source")
    query=MaskDataReadIn(screen_id="test/list",source_key="rows",table_key="list",preset_filters=selections)
    with pytest.raises(HTTPException) as error:
        source.read_sync(query,"own","Bearer verified-caller",transport=httpx.MockTransport(forbidden))
    assert error.value.status_code == 422


def test_unscheduled_activity_is_readable_but_read_identity_is_not_a_create_command():
    from app.api.v1.schemas.crm import Activity, ActivityCreate
    payload=dict(id="aaaaaaaa-0000-4000-8000-00000000000a",version=1,type="call",title="Synthetic callback",
                 customer="Synthetic customer", contact_person="-", status="planned", assigned_to="")
    assert Activity.model_validate(payload).model_dump()["overdue"] is False
    assert Activity.model_validate(payload).date is None
    with pytest.raises(ValidationError):
        ActivityCreate.model_validate(payload)


def test_cli_complete_and_registered_presets_use_same_read_contract(monkeypatch):
    import base64
    import json
    import httpx
    from valeo_cli import cli
    encode=lambda value:base64.urlsafe_b64encode(json.dumps(value).encode()).decode().rstrip("=")
    token=".".join([encode({"alg":"none"}),encode({"sub":"fixture","tenant_id":"own","identity_type":"human","exp":4000000000}),"sig"])
    monkeypatch.setenv("VALEO_ACCESS_TOKEN",token)
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(200,json={"data":{"items":[],"total":0}})
    lines=[]
    with httpx.Client(base_url="https://api.invalid",transport=httpx.MockTransport(handler)) as client:
        result=cli.main(["daten","test/list","rows","--tabelle","list","--vollstaendig","--preset","owner=mine","--preset","when=today"],http=client,out=lines.append)
    assert result == 0 and len(calls) == 1
    params=calls[0].url.params
    assert params["complete"] == "true"
    assert json.loads(params["preset_filters"]) == {"owner":"mine","when":"today"}
    assert "tenant_id" not in params


def test_complete_projection_never_silently_truncates_an_oversized_source():
    query=MaskDataReadIn(screen_id="test/list",source_key="rows",table_key="list",complete=True)
    with pytest.raises(HTTPException) as error:
        project_rows([{"id":n} for n in range(5001)],{"columns":[{"key":"id"}]},query)
    assert error.value.status_code == 409
