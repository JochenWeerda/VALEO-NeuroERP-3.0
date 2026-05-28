"""Guardrails + PII — REST API (NC-C)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.guardrails import check_input, sanitize_output
from app.services.pii_detector import detect_pii, mask_irreversible, mask_reversible, scan_dict

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/neuro/guardrails", tags=["neuro-core", "guardrails", "pii"])


class TextRequest(BaseModel):
    text: str


class DictRequest(BaseModel):
    data: dict


@router.post("/check-input", summary="Check input do",
    response_model=CompatFlexOut
)
async def do_check_input(request: TextRequest):
    result = check_input(request.text)
    return result.to_dict()


@router.post("/sanitize-output", summary="Sanitize output do",
    response_model=CompatFlexOut
)
async def do_sanitize_output(request: TextRequest):
    result = sanitize_output(request.text)
    resp = result.to_dict()
    resp["sanitized_text"] = result.sanitized_text
    return resp


@router.post("/detect-pii", summary="Detect pii do",
    response_model=CompatFlexOut
)
async def do_detect_pii(request: TextRequest):
    matches = detect_pii(request.text)
    return {
        "count": len(matches),
        "matches": [{"type": m.type, "start": m.start, "end": m.end} for m in matches],
    }


@router.post("/mask", summary="Mask do",
    response_model=CompatFlexOut
)
async def do_mask(request: TextRequest):
    return {"masked": mask_irreversible(request.text)}


@router.post("/mask-reversible", summary="Mask reversible do",
    response_model=CompatFlexOut
)
async def do_mask_reversible(request: TextRequest):
    masked, token_map = mask_reversible(request.text)
    return {"masked": masked, "tokens": len(token_map)}


@router.post("/scan-dict", summary="Scan dict do",
    response_model=CompatFlexOut
)
async def do_scan_dict(request: DictRequest):
    matches = scan_dict(request.data)
    return {
        "count": len(matches),
        "matches": [{"type": m.type, "path": m.masked} for m in matches],
    }
