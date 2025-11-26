from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ORMModel(BaseModel):
    model_config = {"from_attributes": True}


class Timestamped(ORMModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None
