from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.api.v1.schemas.base import BaseSchema

class WebhookOut(BaseSchema):
    id: str
    url: str
    event_area: str
    is_active: bool = True


class EventAreaOut(BaseModel):
    name: str
    description: str

