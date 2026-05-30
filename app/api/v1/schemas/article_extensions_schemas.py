"""Pydantic schemas for the article extensions domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class BatchOut(BaseSchema):
    id: str
    article_id: str
    batch_number: str
    warehouse_id: str
    quantity: float = 0
    expiry_date: Optional[str] = None


class SelectionOut(BaseSchema):
    id: str
    article_id: str
    selection_code: str
    label: Optional[str] = None


class SelectionCreate(BaseModel):
    article_id: str
    selection_code: str
    label: Optional[str] = None


class FileUploadResponse(BaseModel):
    filename: str
    size: int
    message: str


class RecipeImportRequest(BaseModel):
    article_id: str
    components: list[dict]

