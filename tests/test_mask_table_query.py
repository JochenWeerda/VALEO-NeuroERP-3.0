"""Common table semantics and bounded collection, independent of adapter."""
import asyncio
import httpx
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.api.v1.schemas.mask_data_contracts import MaskDataReadIn
from app.services.mask_table_query import project_rows, TableCollector
from app.services import mask_data_read as service

TABLE = {"key":"list", "dataSourceKey":"rows", "columns":[{"key":"name"},{"key":"amount"},{"key":"secret","filterable":False,"sortable":False}]}
def query(**kw):
    return MaskDataReadIn(screen_id="test/list",source_key="rows",table_key="list",**kw)

@pytest.mark.parametrize("op,value,expected",[("eq",2,[2]),("neq",2,[1,3]),("contains","2",[2]),("lt",2,[1]),("lte",2,[1,2]),("gt",2,[3]),("gte",2,[2,3]),("in",[1,3],[1,3]),("between",[1,2],[1,2])])
def test_nine_operators(op,value,expected):
    result=project_rows([{"amount":n} for n in [1,2,3]],TABLE,query(filter_plan={"amount":{"op":op,"value":value,"label":"UI chip"}}))
    assert [r["amount"] for r in result["items"]]==expected

def test_search_sort_second_page_and_stable_order():
    rows=[{"name":v} for v in ["Müller 10","Muller 2","MÜLLER 1","Fremd"]]
    result=project_rows(rows,TABLE,query(q="muller",sort="name",page=2,limit=1))
    assert result["items"]==[{"name":"Muller 2"}] and result["total"]==3
    assert result["has_next"] and result["has_prev"]

@pytest.mark.parametrize("kw",[{"sort":"unknown"},{"sort":"secret"},{"filter_plan":{"secret":{"op":"eq","value":1}}}])
def test_fields_require_declaration(kw):
    with pytest.raises(HTTPException):project_rows([],TABLE,query(**kw))

@pytest.mark.parametrize("filter",[{"op":"eq","value":[]},{"op":"between","value":[1]},{"op":"in","value":1},{"op":"eq","value":float("nan")},{"op":"eq","value":"x"*201}])
def test_filter_shape_and_bounds(filter):
    with pytest.raises(ValidationError):query(filter_plan={"amount":filter})

def test_complete_collection_before_search():
    c=TableCollector(TABLE,query(q="target",limit=1),fetch_limit=2)
    assert c.receive({"items":[{"id":"a","name":"other"},{"id":"b","name":"other"}],"total":3},True) is None
    result=c.receive({"items":[{"id":"c","name":"target"}],"total":3},True)
    assert result["total"]==1 and result["items"][0]["id"]=="c"

@pytest.mark.parametrize("second",[{"items":[{"id":"a"}],"total":3},{"items":[{"id":"b"}],"total":4},{"items":[],"total":3}])
def test_repeated_changed_or_incomplete_pages_rejected(second):
    c=TableCollector(TABLE,query(),fetch_limit=1)
    c.receive({"items":[{"id":"a"}],"total":3},True)
    with pytest.raises(HTTPException):c.receive(second,True)

def test_unpageable_partial_source_rejected():
    with pytest.raises(HTTPException):TableCollector(TABLE,query()).receive({"items":[],"total":1},False)

@pytest.mark.parametrize("paging",["page","skip","offset"])
def test_sync_async_share_complete_paging_and_token(monkeypatch,paging):
    monkeypatch.setattr(service,"get_screen_definition",lambda *a,**k:{"tables":[TABLE],"dataSources":[{"key":"rows","endpoint":"/api/v1/test?state=open&state=review"}]})
    monkeypatch.setattr(service,"_query_parameters",lambda _:frozenset({paging,"limit"}))
    calls=[]
    def endpoint(request):
        assert request.headers["authorization"]=="Bearer caller"
        assert "x-tenant-id" not in request.headers
        assert request.url.params.get_list("state")==["open","review"]
        start=(int(request.url.params[paging])-1)*50 if paging=="page" else int(request.url.params[paging])
        calls.append(start)
        rows=[{"id":str(n),"name":f"Row {n}","amount":n} for n in range(start,min(start+50,61))]
        return httpx.Response(200,json={"items":rows,"total":61})
    q=query(sort="amount",sort_dir="desc",page=2,limit=2)
    transport=httpx.MockTransport(endpoint)
    sync=service.read_sync(q,"own","Bearer caller",transport=transport)
    async_result=asyncio.run(service.read_async(q,"own","Bearer caller",transport=transport))
    assert sync==async_result
    assert [r["amount"] for r in sync.data["items"]]==[58,57]
    assert sync.data["total"]==61 and calls==[0,50,0,50]

# Real signed HTTP adapters and SQL domain path; no role/tenant dependency override.
from test_mask_data_read import channels, case, subject_data, keys, probe, _headers

def test_signed_three_channel_table_projection_and_foreign_tenant(channels,monkeypatch):
    import json
    import uuid
    from app.infrastructure.models import Customer
    from app.api.v1.endpoints import finance_stammdaten
    from app.core.tenant_binding import install_tenant_bindings
    from main import BearerAuthMiddleware
    from valeo_cli import cli
    client,db,_,tenant,foreign,*_=channels
    client.app.include_router(finance_stammdaten.router,prefix="/api/v1")
    install_tenant_bindings(client.app,public_paths=BearerAuthMiddleware.PUBLIC_PATHS)
    marker="SYNTH-TABLE-"+uuid.uuid4().hex[:8]
    for owner,suffix in [(tenant,"1"),(tenant,"2"),(tenant,"10"),(foreign,"3")]:
        db.add(Customer(id=str(uuid.uuid4()),tenant_id=owner,customer_number=uuid.uuid4().hex[:16],company_name=marker+" "+suffix,is_active=True))
    db.flush()
    headers=_headers(channels)
    params={"table_key":"list","q":marker,"sort":"name","page":2,"limit":1,"filter_plan":json.dumps({"name":{"op":"contains","value":marker}})}
    rest=client.get("/api/v1/masks/finance/debitoren-liste/data/list",params=params,headers=headers)
    assert rest.status_code==200,rest.text
    result=rest.json()["data"]
    assert result["total"]==3 and result["items"][0]["name"]==marker+" 2"
    mcp=client.post("/api/v1/mcp/tools/call",headers=headers,json={"tool_name":"mask.data.read","mode":"dryRun","parameters":{**params,"filter_plan":json.loads(params["filter_plan"]),"screen_id":"finance/debitoren-liste","source_key":"list"}})
    assert mcp.status_code==200,mcp.text
    assert mcp.json()["data"]==result
    monkeypatch.setenv("VALEO_ACCESS_TOKEN",headers["Authorization"][7:])
    lines=[]
    assert cli.main(["daten","finance/debitoren-liste","list","--tabelle","list","--suche",marker,"--sortieren","name","--seite","2","--limit","1"],http=client,out=lines.append)==0
    assert json.loads(lines[0])["data"]==result
    for invalid in ['{"name":{"op":"eq","value":1,"value":2}}','{"name":{"op":"eq","value":NaN}}']:
        response=client.get("/api/v1/masks/finance/debitoren-liste/data/list",params={**params,"filter_plan":invalid},headers=headers)
        assert response.status_code==422 and marker not in response.text
    forged=client.get("/api/v1/masks/finance/debitoren-liste/data/list",params={**params,"tenant_id":foreign},headers=headers)
    assert forged.status_code==403
