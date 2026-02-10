"""
DMS image endpoints (l3c-dms extension)
GET for document images and thumbnails.
"""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class DMSDocumentOut(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    url: str


class DMSImageOut(BaseModel):
    id: str
    document_id: str
    thumbnail_url: str
    full_url: str


@router.get("/documents", response_model=list[DMSDocumentOut])
async def list_dms_documents(
    entity_type: Optional[str] = Query(None, description="e.g. 'article', 'customer'"),
    entity_id: Optional[str] = Query(None),
):
    """GET DMS Daten ermitteln"""
    # Stub – real implementation reads from file storage / S3
    return []


@router.get("/images", response_model=list[DMSImageOut])
async def list_dms_images(
    document_id: Optional[str] = Query(None),
):
    """GET Bilder ermitteln"""
    # Stub – real implementation reads from image storage
    return []
