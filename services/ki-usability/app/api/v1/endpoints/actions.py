"""
GET /actions - List actions (optional filter by domain, mask)
GET /actions/{action_id} - Single action
"""

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.schemas.actions import ActionOut, ActionListResponse
from app.services.action_registry import action_registry

router = APIRouter()


@router.get("", response_model=ActionListResponse)
def list_actions(
    domain: Optional[str] = None,
    mask: Optional[str] = None,
) -> ActionListResponse:
    """List all actions, optionally filtered by domain or mask."""
    actions = action_registry.list_actions(domain=domain, mask=mask)
    return ActionListResponse(actions=actions, total=len(actions))


@router.get("/{action_id}", response_model=ActionOut)
def get_action(action_id: str) -> ActionOut:
    """Get one action by ID."""
    action = action_registry.get(action_id)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    return action
