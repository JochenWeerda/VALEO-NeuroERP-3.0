"""P2.3 — KI-Datenklassen API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from app.services.ai_data_classification_service import DataClass, ai_data_classification_service

router = APIRouter(prefix="/ai-data-classes", tags=["ai-data-classification", "compliance"])


@router.get("/", summary="Alle KI-Datenkategorien auflisten", response_model=list[dict[str, Any]])
async def list_categories(data_class: str | None = None) -> list[dict[str, Any]]:
    parsed: DataClass | None = None
    if data_class:
        try:
            parsed = DataClass(data_class)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Unbekannte Klasse '{data_class}'. Gueltige Werte: {[c.value for c in DataClass]}")
    return ai_data_classification_service.list_categories(data_class=parsed)


@router.get("/summary", summary="Zusammenfassung der Datenklassen", response_model=dict[str, Any])
async def get_summary() -> dict[str, Any]:
    return ai_data_classification_service.summary()


@router.get("/{category_id}", summary="Einzelne Datenkategorie", response_model=dict[str, Any])
async def get_category(category_id: str) -> dict[str, Any]:
    try:
        return ai_data_classification_service.get_category(category_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class ModelCheckRequest(BaseModel):
    category_id: str
    model_pattern: str


@router.post("/check-model", summary="Pruefen ob KI-Modell fuer Kategorie erlaubt", response_model=dict[str, Any])
async def check_model(req: ModelCheckRequest) -> dict[str, Any]:
    try:
        return ai_data_classification_service.check_model_allowed(req.category_id, req.model_pattern)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
