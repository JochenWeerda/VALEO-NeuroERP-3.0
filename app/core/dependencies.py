"""Reusable FastAPI dependency factories for pagination and tenant validation."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db


class PaginationParams(BaseModel):
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=500)

    @property
    def page(self) -> int:
        return (self.skip // self.limit) + 1 if self.limit else 1

    @property
    def pages(self, total: int = 0) -> int:
        return max(1, -(-total // self.limit)) if self.limit else 1


def get_pagination(
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(50, ge=1, le=500, description="Max items to return"),
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)


def get_tenant_id(x_tenant_id: str = Header(..., alias="X-Tenant-ID")) -> str:
    """Extract and validate the tenant ID from the request header."""
    if not x_tenant_id or not x_tenant_id.strip():
        raise HTTPException(status_code=400, detail="X-Tenant-ID header is required")
    return x_tenant_id.strip()


def require_tenant_record(model):
    """
    Returns a dependency that fetches `model` by id + tenant_id, raising 404 if absent.

    Usage:
        get_account = require_tenant_record(Account)

        @router.get("/{id}")
        def detail(record=Depends(get_account), ...):
            ...
    """
    def _dep(
        id: str,
        db: Session = Depends(get_db),
        tenant_id: str = Depends(get_tenant_id),
    ):
        obj = (
            db.query(model)
            .filter(model.id == id, model.tenant_id == tenant_id)
            .first()
        )
        if obj is None:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        return obj
    return _dep
