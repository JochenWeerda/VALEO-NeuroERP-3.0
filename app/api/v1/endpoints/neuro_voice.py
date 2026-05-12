"""Voice Adapter Layer — REST API (NC-003)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.voice_adapter import create_session, end_session, transcribe, synthesize

router = APIRouter(prefix="/neuro/voice", tags=["neuro-core", "voice"])


class SessionRequest(BaseModel):
    language: str = Field("de-DE")
    channel: str = Field("phone")


class TranscribeRequest(BaseModel):
    session_id: str
    audio_format: str = Field("wav")


class SynthesizeRequest(BaseModel):
    session_id: str
    text: str


@router.post("/session")
async def start_session(request: SessionRequest):
    return create_session(request.language, request.channel)


@router.delete("/session/{session_id}")
async def close_session(session_id: str):
    result = end_session(session_id)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/transcribe")
async def do_transcribe(request: TranscribeRequest):
    result = await transcribe(request.session_id, request.audio_format)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


@router.post("/synthesize")
async def do_synthesize(request: SynthesizeRequest):
    result = await synthesize(request.session_id, request.text)
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result
