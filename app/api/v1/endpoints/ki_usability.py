"""
KI-Usability API.

Wave 25 hebt die bisher flache Action-Liste auf einen kontextsensitiven
Quick-Action-Contract mit Relevanzscore, Kontextscope und Surface-Hinweisen.
"""

from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ....core.ki_action_registry import (
    ActionContextScope,
    ActionSurface,
    get_action_definition,
    list_action_definitions,
    resolve_actions_for_context,
)


class ActionOut(BaseModel):
    id: str
    label: str
    label_en: str | None = None
    shortcut: str | None = None
    description: str | None = None
    category: str = "action"
    domain: str | None = None
    mask: str | None = None
    intent_phrases: list[str] = Field(default_factory=list)
    required_data: list[str] = Field(default_factory=list)
    surfaces: list[ActionSurface] = Field(default_factory=list)
    context_scope: ActionContextScope
    relevance_score: int
    priority: int
    default_params: dict[str, Any] = Field(default_factory=dict)


class ActionListResponse(BaseModel):
    actions: list[ActionOut]
    total: int


class VoiceResolveIn(BaseModel):
    text: str
    context: dict[str, Any] | None = None


class VoiceResolveOut(BaseModel):
    action_id: str
    params: dict[str, Any] = Field(default_factory=dict)
    confidence: float
    raw_text: str


def _norm(text: str) -> str:
    return " ".join((text or "").lower().strip().split())


def _match_phrases(text: str, phrases: list[str]) -> bool:
    normalized = _norm(text)
    for phrase in phrases:
        phrase_normalized = _norm(phrase)
        if phrase_normalized in normalized or normalized in phrase_normalized:
            return True
    return False


def _resolve_intent(text: str) -> VoiceResolveOut | None:
    if not (text and text.strip()):
        return None

    for action in list_action_definitions():
        if _match_phrases(text, action.intent_phrases):
            params: dict[str, Any] = dict(action.default_params)
            amount_match = re.search(r"betrag\s+([\d,.]+)\s*(?:eur|euro)?", text, re.I)
            if amount_match:
                params["amount"] = amount_match.group(1).replace(",", ".")
            return VoiceResolveOut(
                action_id=action.id,
                params=params,
                confidence=0.9,
                raw_text=text.strip(),
            )

    normalized_text = _norm(text)
    if any(word in normalized_text for word in ["speichern", "sichern"]):
        return VoiceResolveOut(action_id="save-document", params={}, confidence=0.85, raw_text=text.strip())
    if any(word in normalized_text for word in ["abbrechen", "zurueck", "schliessen"]):
        return VoiceResolveOut(action_id="cancel", params={}, confidence=0.8, raw_text=text.strip())
    return None


actions_router = APIRouter()
voice_router = APIRouter()


@actions_router.get("", response_model=ActionListResponse)
def list_actions(domain: str | None = None, mask: str | None = None) -> ActionListResponse:
    actions = [ActionOut(**action.model_dump()) for action in resolve_actions_for_context(domain=domain, mask=mask)]
    return ActionListResponse(actions=actions, total=len(actions))


@actions_router.get("/{action_id}", response_model=ActionOut)
def get_action(action_id: str, domain: str | None = None, mask: str | None = None) -> ActionOut:
    definition = get_action_definition(action_id)
    if definition is None:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")

    resolved = next(
        (action for action in resolve_actions_for_context(domain=domain, mask=mask) if action.id == action_id),
        None,
    )
    if resolved is not None:
        return ActionOut(**resolved.model_dump())

    return ActionOut(
        **definition.model_dump(),
        context_scope=ActionContextScope.GLOBAL,
        relevance_score=0,
    )


@voice_router.post("/resolve", response_model=VoiceResolveOut | None)
def resolve_voice(body: VoiceResolveIn) -> VoiceResolveOut | None:
    return _resolve_intent(body.text)


from app.api.v1.schemas.base import BaseSchema


router = APIRouter(tags=["ki-usability"])
router.include_router(actions_router, prefix="/actions")
router.include_router(voice_router, prefix="/voice")
