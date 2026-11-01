"""Shared tenant-checked opportunity reference resolution for every activity adapter."""
import asyncio
import httpx
from fastapi import HTTPException
from sqlalchemy import text
from app.integrations.crm_core_client import get_opportunity


async def require_opportunity(opportunity_id,tenant,local_lookup):
    try:
        record=await get_opportunity(opportunity_id)
    except httpx.HTTPStatusError as error:
        if error.response.status_code!=404:
            raise HTTPException(503,"Opportunity source unavailable") from error
        record=local_lookup()
    except (httpx.RequestError,RuntimeError):
        record=local_lookup()
    if not record or str(record.get("tenant_id") or "")!=tenant:
        raise HTTPException(404,"Opportunity not found")
    return record


def require_opportunity_sync(db,opportunity_id,tenant):
    # Blocking command services are invoked in FastAPI's threadpool, not its event loop.
    def local():
        row=db.execute(text("SELECT id,tenant_id FROM domain_crm.opportunity WHERE id=:id AND tenant_id=:tenant FOR SHARE"),
                       {"id":opportunity_id,"tenant":tenant}).mappings().first()
        return dict(row) if row else None
    return asyncio.run(require_opportunity(opportunity_id,tenant,local))
