"""Guardrails + PII — REST API (NC-C)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

from app.services.guardrails import check_input, sanitize_output, check_and_sanitize
from app.services.pii_detector import detect_pii, mask_irreversible, mask_reversible, scan_dict

router = APIRouter(prefix="/neuro/guardrails", tags=["neuro-core", "guardrails", "pii"])


class TextRequest(BaseModel):
    text: str


class DictRequest(BaseModel):
    data: dict


@router.post("/check-input")
async def do_check_input(request: TextRequest):
    result = check_input(request.text)
    return result.to_dict()


@router.post("/sanitize-output")
async def do_sanitize_output(request: TextRequest):
    result = sanitize_output(request.text)
    resp = result.to_dict()
    resp["sanitized_text"] = result.sanitized_text
    return resp


@router.post("/detect-pii")
async def do_detect_pii(request: TextRequest):
    matches = detect_pii(request.text)
    return {
        "count": len(matches),
        "matches": [{"type": m.type, "start": m.start, "end": m.end} for m in matches],
    }


@router.post("/mask")
async def do_mask(request: TextRequest):
    return {"masked": mask_irreversible(request.text)}


@router.post("/mask-reversible")
async def do_mask_reversible(request: TextRequest):
    masked, token_map = mask_reversible(request.text)
    return {"masked": masked, "tokens": len(token_map)}


@router.post("/scan-dict")
async def do_scan_dict(request: DictRequest):
    matches = scan_dict(request.data)
    return {
        "count": len(matches),
        "matches": [{"type": m.type, "path": m.masked} for m in matches],
    }
