"""
Sales shipping extension endpoints (l3c-verkaufslieferschein extras)
File upload for delivery notes.
"""

from fastapi import APIRouter, Query, UploadFile, File
from pydantic import BaseModel

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut


router = APIRouter()


class FileUploadResponse(BaseModel):
    filename: str
    size: int
    message: str


@router.post("/file-upload", response_model=FileUploadResponse, summary="Delivery note file hochladen")
async def upload_delivery_note_file(
    delivery_note_id: str = Query(..., description="ID of the sales delivery note"),
    file: UploadFile = File(...),
):
    """POST Verkaufslieferschein: Datei hochladen"""
    content = await file.read()
    return FileUploadResponse(
        filename=file.filename or "unknown",
        size=len(content),
        message=f"File uploaded for delivery note {delivery_note_id}",
    )
