"""
POST /voice/resolve - Resolve transcribed text to action_id + params
"""

from fastapi import APIRouter

from app.schemas.voice import VoiceResolveIn, VoiceResolveOut
from app.services.intent_resolver import intent_resolver

router = APIRouter()


@router.post("/resolve", response_model=VoiceResolveOut | None)
def resolve_voice(body: VoiceResolveIn) -> VoiceResolveOut | None:
    """
    Resolve voice text to an action.
    Returns action_id, params, confidence. None if no intent matched (client gets 200 + null).
    """
    context = body.context or {}
    return intent_resolver.resolve(body.text, context=context)
