import json
from types import SimpleNamespace

import pytest

from app.api.v1.endpoints import crm_campaigns as api
from app.core.screen_definitions_stamm import build_crm_campaign_template_stamm


def run_endpoint(coroutine):
    # These endpoints execute synchronously against the injected session.
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("Endpoint unexpectedly suspended")


class FakeDB:
    def __init__(self, row):
        self.row = row
        self.calls = []

    def execute(self, statement, params):
        self.calls.append((str(statement), dict(params)))
        return self

    def fetchone(self):
        return self.row

    def commit(self):
        pass


def template_row():
    return SimpleNamespace(id="template-1", tenant_id="tenant-a", name="Vorlage",
        description="Beschreibung", campaign_type="email", subject_line="Betreff",
        message_body="Text", is_active=True, created_by=None,
        meta={"nested": {"enabled": True}}, created_at=None, updated_at=None)


def test_definition_uses_real_contract_and_human_only_writes():
    definition = build_crm_campaign_template_stamm()
    fields = definition["creation"]["fields"]
    assert {field["key"] for field in fields} == {
        "name", "description", "campaign_type", "subject_line", "message_body", "is_active"
    }
    edit, duplicate, back = definition["actions"]
    assert edit["method"] == "PUT" and edit["inputFields"] == fields
    assert edit["inputPrefill"] == "entity"
    assert edit["forbiddenForAgents"] and duplicate["forbiddenForAgents"]
    assert duplicate["commandEndpoint"].endswith("/{entity_id}/duplicate")
    assert duplicate["resultNavigationRoute"] == "/crm/campaign-template/{result_id}"
    assert back["navigationRoute"] == "/crm/campaign-templates"


def test_create_and_duplicate_serialize_json_and_scope_readback(monkeypatch):
    monkeypatch.setattr(api, "uuid7", lambda: "new-id")
    for operation in ("create", "duplicate"):
        db = FakeDB(template_row())
        if operation == "create":
            run_endpoint(api.create_template(api.TemplateCreate(name="A", meta={"enabled": True}), "tenant-a", db))
        else:
            run_endpoint(api.duplicate_template("template-1", "tenant-a", db))
        sql, params = next(call for call in db.calls if "INSERT INTO" in call[0])
        assert json.loads(params["meta"])["enabled" if operation == "create" else "nested"]
        assert "tenant_id = :tid" in db.calls[-1][0]
        assert db.calls[-1][1]["tid"] == "tenant-a"


def test_update_preserves_missing_meta_and_writes_valid_json():
    db = FakeDB(template_row())
    run_endpoint(api.update_template("template-1", api.TemplateUpdate(description=None, meta={"ok": True}), "tenant-a", db))
    sql, params = next(call for call in db.calls if "UPDATE " in call[0])
    assert "meta = CAST(:meta AS jsonb)" in sql
    assert json.loads(params["meta"]) == {"ok": True}
    assert params["description"] is None
    assert "tenant_id = :tid" in db.calls[-1][0]
    db = FakeDB(template_row())
    run_endpoint(api.update_template("template-1", api.TemplateUpdate(name="Neu"), "tenant-a", db))
    assert "meta" not in next(params for sql, params in db.calls if "UPDATE " in sql)


def test_update_and_duplicate_reject_missing_tenant_record():
    for operation in ("update", "duplicate"):
        db = FakeDB(None)
        with pytest.raises(api.HTTPException) as error:
            if operation == "update":
                run_endpoint(api.update_template("other", api.TemplateUpdate(name="X"), "tenant-a", db))
            else:
                run_endpoint(api.duplicate_template("other", "tenant-a", db))
        assert error.value.status_code == 404
        assert len(db.calls) == 1 and db.calls[0][1]["tid"] == "tenant-a"


@pytest.mark.parametrize("payload", [{"name":None}, {"campaign_type":None}, {"is_active":None}, {"campaign_type":"invalid"}, {"subject_line":"x"*501}])
def test_invalid_template_update_rejected_before_sql(payload):
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        api.TemplateUpdate(**payload)
