from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.numbering_service import get_numbering

router = APIRouter()


class NumberingRequest(BaseModel):
    domain: str
    tenant_id: str | None = None


class NumberingResponse(BaseModel):
    ok: bool
    number: str


@router.post("/next", response_model=NumberingResponse)
def next_number(payload: NumberingRequest) -> NumberingResponse:
    number = get_numbering().next_number(payload.domain)
    return NumberingResponse(ok=True, number=number)
