"""Fast Track — REST API (NC-E)."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.fast_track import classify_request, is_fast_track, FAST_TRACK_WHITELIST

router = APIRouter(prefix="/neuro/fast-track", tags=["neuro-core", "fast-track"])


class ClassifyRequest(BaseModel):
    method: str = Field(..., description="HTTP-Methode (GET/POST/PUT/...)")
    path: str = Field(..., description="Request-Pfad")
    has_ai_context: bool = Field(False)


@router.post("/classify", summary="Classify")
async def classify(request: ClassifyRequest):
    return classify_request(request.method, request.path, request.has_ai_context)


@router.get("/whitelist", summary="Whitelist abrufen")
async def get_whitelist():
    return {"paths": sorted(FAST_TRACK_WHITELIST), "count": len(FAST_TRACK_WHITELIST)}


@router.get("/check", summary="Prüfen")
async def check(method: str = "GET", path: str = "/api/v1/articles"):
    return {"is_fast_track": is_fast_track(method, path), "method": method, "path": path}
