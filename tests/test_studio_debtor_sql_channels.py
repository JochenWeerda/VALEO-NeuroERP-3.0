"""Signed debtor reads on the shared probe; all own data rolls back with the fixture."""
import json
from datetime import date, timedelta
from uuid import uuid4
from sqlalchemy import text
from test_mask_data_read import channels, case, subject_data, keys, probe, _headers  # noqa: F401


def test_debtor_source_summary_and_three_channel_money(channels,monkeypatch):
    from app.api.v1.endpoints import open_items,mask_rollout_summaries
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    from valeo_cli import cli
    client,db,_,tenant,foreign,*_=channels
    client.app.include_router(open_items.router,prefix="/api/v1/finance")
    client.app.include_router(mask_rollout_summaries.router,prefix="/api/v1")
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    marker="SYNTH-OP-"+uuid4().hex[:10]
    writer=_headers(channels,role="FINANCE_BEARBEITEN")
    ids=[]
    for index,(kind,status,amount,stage) in enumerate([("debitoren","offen","0.10",0),("debitoren","teilweise","0.20",1),("kreditoren","offen","999.00",0),("debitoren","geschlossen","0.00",0)]):
        response=client.post("/api/v1/finance/open-items",headers=writer,json={"konto_typ":kind,"op_status":status,"rechnungsnr":marker+str(index),"rechnungsdatum":date.today().isoformat(),"faelligkeit":(date.today()-timedelta(days=1)).isoformat(),"op_betrag":"10.00","offen":amount,"kunde_name":marker,"konto_nr":"SYNTH-D-1","mahn_stufe":stage,"waehrung":"EUR"})
        assert response.status_code==201,response.text
        ids.append(response.json()["id"])
    reader=_headers(channels,role="FINANCE_LESEN")
    direct=client.get("/api/v1/finance/open-items",headers=reader,params={"konto_typ":"debitoren","only_open":True,"search":marker,"limit":1,"offset":1})
    assert direct.status_code==200,direct.text
    assert direct.json()["total"]==2 and direct.json()["items"][0]["id"]==ids[1]
    assert direct.json()["items"][0]["ueberfaellig"] is True
    route="/api/v1/masks/fibu/debitoren-liste/data/list"
    params={"table_key":"list","q":marker}
    response=client.get(route,headers=reader,params=params)
    assert response.status_code==200,response.text
    result=response.json()["data"]
    assert result["total"]==2 and result["aggregates"]=={"all":2,"open_amount":0.3,"overdue":2,"dunning":1}
    assert result["aggregate_currencies"]=={"open_amount":"EUR"}
    mcp=client.post("/api/v1/mcp/tools/call",headers=reader,json={"tool_name":"mask.data.read","mode":"dryRun","parameters":{**params,"screen_id":"fibu/debitoren-liste","source_key":"list"}})
    assert mcp.status_code==200,mcp.text
    assert mcp.json()["data"]==result
    monkeypatch.setenv("VALEO_ACCESS_TOKEN",reader["Authorization"][7:]);lines=[]
    assert cli.main(["daten","fibu/debitoren-liste","list","--tabelle","list","--suche",marker],http=client,out=lines.append)==0
    assert json.loads(lines[0])["data"]==result
    summary=client.get(f"/api/v1/mask-rollouts/finance/ar-open-item/{ids[0]}/screen-summary",headers=reader)
    assert summary.status_code==200,summary.text
    assert marker in summary.text
    # Two settlement journals have indistinguishable descriptions: only the structured audit link counts.
    from datetime import datetime, timezone
    from app.infrastructure.models.journal import JournalEntry
    from app.infrastructure.models import AuditLog
    actor=db.execute(text("SELECT id FROM domain_shared.users WHERE tenant_id=:tenant ORDER BY id LIMIT 1"),{"tenant":tenant}).scalar_one()
    now=datetime.now(timezone.utc); journal_ids=[str(uuid4()),str(uuid4())]
    for index,journal_id in enumerate(journal_ids):
        db.add(JournalEntry(id=journal_id,tenant_id=tenant,entry_number="SP-"+uuid4().hex[:12],entry_date=now,posting_date=now,description="Synthetic payment without an OP identifier",source="op_settlement",currency="USD",total_debit="0.10",total_credit="0.10",status="draft"))
        db.add(AuditLog(id=str(uuid4()),timestamp=now,tenant_id=tenant,user_id=actor,user_email="synthetic@example.invalid",action="create",entity_type="journal_entry",entity_id=journal_id,changes={"source":"op_settlement","op_id":ids[index]},ip_address="127.0.0.1",user_agent="Synthetic"))
    db.flush()
    payments=client.get(f"/api/v1/finance/open-items/{ids[0]}/settlements",headers=reader)
    assert payments.status_code==200,payments.text
    assert [item["id"] for item in payments.json()]==[journal_ids[0]]
    assert payments.json()[0]["waehrung"]=="USD"
    tab=client.get(f"/api/v1/mask-rollouts/finance/ar-open-item/{ids[0]}/tabs/ausgleich",headers=reader)
    assert tab.status_code==200,tab.text
    assert journal_ids[0] in tab.text and journal_ids[1] not in tab.text
    other_reader=_headers(channels,role="FINANCE_LESEN",tenant=foreign)
    assert client.get(f"/api/v1/finance/open-items/{ids[0]}",headers=other_reader).status_code==404
    assert client.get(f"/api/v1/finance/open-items/{ids[0]}/settlements",headers=other_reader).status_code==404
    assert client.get(route,headers=_headers(channels,role=None),params=params).status_code==403
