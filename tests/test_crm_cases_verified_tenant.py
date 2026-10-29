"""The compatibility query cannot replace the verified CRM tenant context."""
import asyncio
import pytest
from app.api.v1.endpoints import cases


@pytest.mark.parametrize('query_tenant',[None,'synthetic-foreign'])
def test_case_list_uses_verified_context_and_preserves_paging(monkeypatch, query_tenant):
    calls=[]
    async def backend(**kwargs):
        calls.append(kwargs)
        return [],0
    monkeypatch.setattr(cases,'crm_list_cases',backend)
    context=cases._MANDANT.set('synthetic-verified')
    try:
        result=asyncio.run(cases.list_cases(tenant_id=query_tenant,status='open',
            priority='high',assigned_to=None,customer_id=None,skip=25,limit=25))
    finally:
        cases._MANDANT.reset(context)
    assert calls==[{'tenant_id':'synthetic-verified','status':'open','priority':'high',
        'assigned_to':None,'customer_id':None,'skip':25,'limit':25}]
    assert result.items==[] and result.page==2 and result.size==25
