"""Real signed HTTP/SQL contracts on the shared probe; outer fixture rollback."""
import json
from uuid import uuid4
from test_mask_data_read import channels, case, subject_data, keys, probe, _headers  # noqa: F401


def install(channels, router):
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    channels[0].app.include_router(router, prefix="/api/v1")
    install_tenant_bindings(channels[0].app, public_paths=BearerAuthMiddleware.PUBLIC_PATHS)


def test_contract_audit_real_three_channel_context_and_tenant(channels, monkeypatch):
    from app.api.v1.endpoints.kontrakte import router
    from app.domains.operations.models import KonContract, KonAuditLog
    from valeo_cli import cli
    client, db, _, tenant, foreign, *_ = channels
    install(channels, router)
    own, other = str(uuid4()), str(uuid4())
    for cid, tid in [(own, tenant), (other, foreign)]:
        db.add(KonContract(contract_id=cid, contract_no="SYNTH-"+cid, contract_type="VERKAUF", party_id="synthetic-party", tenant_id=tid))
        db.add(KonAuditLog(audit_id=str(uuid4()), entity_type="contract", entity_id=cid, field_name="Preis", old_value=None, new_value="12", action="UPDATE", changed_by="synthetic-reviewer", tenant_id=tid))
    db.flush()
    headers = _headers(channels, role="KONTRAKT_LESEN")
    params = {"entity_id": own, "table_key": "list"}
    route = "/api/v1/masks/kontrakte/FrmKontraktProtokoll/data/list"
    rest = client.get(route, headers=headers, params=params)
    assert rest.status_code == 200, rest.text
    result = rest.json()["data"]
    assert result["total"] == 1 and result["items"][0]["old_value"] is None
    assert result["items"][0]["entity_id"] == own
    mcp = client.post("/api/v1/mcp/tools/call", headers=headers, json={"tool_name":"mask.data.read", "mode":"dryRun", "parameters":{**params,"screen_id":"kontrakte/FrmKontraktProtokoll","source_key":"list"}})
    assert mcp.status_code == 200, mcp.text
    assert mcp.json()["data"] == result
    monkeypatch.setenv("VALEO_ACCESS_TOKEN", headers["Authorization"][7:])
    lines=[]
    assert cli.main(["daten","kontrakte/FrmKontraktProtokoll","list","--id",own,"--tabelle","list"],http=client,out=lines.append)==0
    assert json.loads(lines[0])["data"] == result
    assert client.get(route, headers=headers, params={**params,"entity_id":other}).status_code == 404
    assert client.get(route, headers=_headers(channels, role=None), params=params).status_code == 403


def test_template_real_create_update_duplicate_and_isolation(channels):
    from app.api.v1.endpoints.crm_campaigns import router
    client, db, _, tenant, foreign, *_ = channels
    install(channels, router)
    base = "/api/v1/crm/campaigns/templates"
    headers = _headers(channels, role="CRM_BEARBEITEN")
    created = client.post(base, headers=headers, json={"name":"SYNTH-template-"+uuid4().hex,"campaign_type":"sms","meta":{"nested":{"enabled":True}}})
    assert created.status_code == 201, created.text
    cid=created.json()["id"]
    updated = client.put(base+"/"+cid, headers=headers, json={"description":None,"subject_line":"Neuer Betreff"})
    assert updated.status_code == 200, updated.text
    assert updated.json()["subject_line"] == "Neuer Betreff" and updated.json()["meta"] == {"nested":{"enabled":True}}
    duplicate = client.post(base+"/"+cid+"/duplicate", headers=headers)
    assert duplicate.status_code == 201, duplicate.text
    assert duplicate.json()["id"] != cid and duplicate.json()["is_active"] is False
    assert duplicate.json()["meta"] == created.json()["meta"]
    foreign_headers = _headers(channels, role="CRM_BEARBEITEN", tenant=foreign)
    for suffix, method in [("", "get"), ("", "put"), ("/duplicate", "post")]:
        kwargs={"json":{"name":"forbidden"}} if method=="put" else {}
        assert getattr(client,method)(base+"/"+cid+suffix,headers=foreign_headers,**kwargs).status_code == 404
    assert client.put(base+"/"+cid, headers=_headers(channels,role=None), json={"name":"forbidden"}).status_code == 403
