"""Pydantic schemas for Knowledge Base."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgeArticleBase(BaseModel):
    """Base knowledge article schema."""
    title: str = Field(..., max_length=255)
    content: str = Field(...)  # Rich text content
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None
    tags: Optional[str] = Field(None, max_length=500)  # Comma-separated
    is_published: bool = False
    is_featured: bool = False


class KnowledgeArticleCreate(KnowledgeArticleBase):
    """Schema for creating knowledge articles."""
    tenant_id: str = Field(..., max_length=64)
    created_by: Optional[str] = Field(None, max_length=64)


class KnowledgeArticleUpdate(BaseModel):
    """Schema for updating knowledge articles."""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None
    tags: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    updated_by: Optional[str] = Field(None, max_length=64)


class KnowledgeArticle(KnowledgeArticleBase):
    """Full knowledge article schema."""
    id: UUID
    tenant_id: str
    view_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    """Schema for creating categories."""
    tenant_id: str = Field(..., max_length=64)


class CategoryUpdate(BaseModel):
    """Schema for updating categories."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class Category(CategoryBase):
    """Full category schema."""
    id: UUID
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleFeedback(BaseModel):
    """Schema for article feedback."""
    article_id: UUID
    is_helpful: bool
    user_id: Optional[str] = None
    comments: Optional[str] = None