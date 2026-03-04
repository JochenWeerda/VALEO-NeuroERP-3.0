"""
Action Registry schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ActionOut(BaseModel):
    """Single action (toolbar/shortcut/voice)."""

    id: str = Field(..., description="Action ID (e.g. save-document, nav-orders)")
    label: str = Field(..., description="Display label (DE)")
    label_en: Optional[str] = Field(None, description="Display label (EN)")
    shortcut: Optional[str] = Field(None, description="Keyboard shortcut (e.g. Strg+F4)")
    description: Optional[str] = Field(None, description="Short description")
    category: str = Field(default="action", description="Category: navigation, action, etc.")
    domain: Optional[str] = Field(None, description="Domain: finance, sales, ...")
    mask: Optional[str] = Field(None, description="Mask ID if scoped")
    intent_phrases: List[str] = Field(default_factory=list, description="Voice phrases (DE)")
    required_data: List[str] = Field(default_factory=list, description="Required data keys for execution")


class ActionListResponse(BaseModel):
    """List of actions (filtered by domain/mask)."""

    actions: List[ActionOut]
    total: int
