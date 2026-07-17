"""Bidirektionaler Kundenrezeptur-Kreislauf (FEED-RECIPE-052).

Hinweg (Bestellrezeptur), Bestellung (fixiert die freigegebene Optimal-Version)
und Rueckweg (Ist-Mischung mit Nachkalkulation). Drift-Schutz strukturell: eine
Bestellung nutzt immer die freigegebene Version, nie das gelieferte Ist.
"""
from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, WRITE_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_recipe_service import (
    FeedingRecipeService,
    RecipeConflict,
    RecipeNotFound,
    RecipeValidationError,
)

router = APIRouter(prefix="/feeding", tags=["feeding-recipes"])


class RecipeComponentIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    kg_per_t: float = Field(gt=0)
    feed_id: str | None = Field(default=None, max_length=80)


class RecipeCreateIn(BaseModel):
    customer_ref: str = Field(min_length=1, max_length=160)
    artikel_nr: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=200)
    source_ration_ref: str | None = Field(default=None, max_length=120)
    components: list[RecipeComponentIn] = Field(min_length=1)


class RecipeVersionIn(BaseModel):
    expected_latest_version_no: int = Field(ge=1)
    components: list[RecipeComponentIn] = Field(min_length=1)


class RecipeApproveIn(BaseModel):
    version_no: int = Field(ge=1)


class RecipeOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    customer_ref: str
    artikel_nr: str
    name: str
    source_ration_ref: str | None = None
    latest_version_no: int
    approved_version_no: int | None = None
    latest_components: list[dict[str, Any]]


class OrderCreateIn(BaseModel):
    menge_t: float = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=160)


class DeliveryComponentIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    ist_kg: float = Field(ge=0)


class DeliveryIn(BaseModel):
    source: Literal["mixer", "manual", "import"]
    idempotency_key: str = Field(min_length=1, max_length=160)
    components: list[DeliveryComponentIn] = Field(min_length=1)


class OrderOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    recipe_id: str
    recipe_version_id: str
    recipe_version_no: int
    menge_t: float
    soll_components: list[dict[str, Any]]
    delivery: dict[str, Any] | None = None
    nachkalkulation: list[dict[str, Any]] | None = None


def _service(db: Session, tenant_id: str, user: User) -> FeedingRecipeService:
    return FeedingRecipeService(db, tenant_id, str(user.get("sub") or "unknown"))


def _handle(exc: Exception) -> HTTPException:
    if isinstance(exc, RecipeNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, RecipeConflict):
        return HTTPException(status_code=409, detail=str(exc))
    return HTTPException(status_code=422, detail=str(exc))


@router.post("/recipes", response_model=RecipeOut, status_code=201,
             summary="Bestellrezeptur aus verknuepften Zeilen anlegen (Kunden-Artikelnr.)")
async def create_recipe(body: RecipeCreateIn, db: Session = Depends(get_db),
                        tenant_id: str = Depends(get_tenant_id),
                        user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Rezepturen.")
    try:
        return _service(db, tenant_id, user).create_recipe(
            body.model_dump() | {"components": [c.model_dump() for c in body.components]})
    except (RecipeConflict, RecipeValidationError, RecipeNotFound) as exc:
        raise _handle(exc) from exc


@router.get("/recipes", response_model=list[RecipeOut],
            summary="Bestellrezepturen (optional je Kunde)")
async def list_recipes(customer_ref: str | None = None, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Rezepturen.")
    return _service(db, tenant_id, user).list_recipes(customer_ref=customer_ref)


@router.post("/recipes/{recipe_id}/versions", response_model=RecipeOut, status_code=201,
             summary="Neue Rezepturversion (append-only, optimistische Revision)")
async def add_version(recipe_id: str, body: RecipeVersionIn, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id),
                      user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Rezepturen.")
    try:
        return _service(db, tenant_id, user).add_version(
            recipe_id, expected_latest_version_no=body.expected_latest_version_no,
            components=[c.model_dump() for c in body.components])
    except (RecipeConflict, RecipeValidationError, RecipeNotFound) as exc:
        raise _handle(exc) from exc


@router.post("/recipes/{recipe_id}/approve", response_model=RecipeOut,
             summary="Optimal-Rezeptur freigeben (Voraussetzung fuer Bestellung)")
async def approve_recipe(recipe_id: str, body: RecipeApproveIn, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Rezepturen.")
    try:
        return _service(db, tenant_id, user).approve(recipe_id, body.version_no)
    except (RecipeConflict, RecipeValidationError, RecipeNotFound) as exc:
        raise _handle(exc) from exc


@router.post("/recipes/{recipe_id}/orders", response_model=OrderOut, status_code=201,
             summary="Futterbestellung — fixiert immer die freigegebene Optimal-Version")
async def create_order(recipe_id: str, body: OrderCreateIn, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id),
                       user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Rezepturbestellungen.")
    try:
        return _service(db, tenant_id, user).create_order(
            recipe_id, menge_t=body.menge_t, idempotency_key=body.idempotency_key)
    except (RecipeConflict, RecipeValidationError, RecipeNotFound) as exc:
        raise _handle(exc) from exc


@router.post("/recipe-orders/{order_id}/delivery", response_model=OrderOut, status_code=201,
             summary="Ist-Mischung (Mahl-/Mischwagen) mit Nachkalkulation gegen die fixierte Version")
async def record_delivery(order_id: str, body: DeliveryIn, db: Session = Depends(get_db),
                          tenant_id: str = Depends(get_tenant_id),
                          user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, WRITE_ROLES, detail="Keine Berechtigung fuer Lieferrueckmeldungen.")
    try:
        return _service(db, tenant_id, user).record_delivery(
            order_id, source=body.source, idempotency_key=body.idempotency_key,
            components=[c.model_dump() for c in body.components])
    except (RecipeConflict, RecipeValidationError, RecipeNotFound) as exc:
        raise _handle(exc) from exc


@router.get("/recipe-orders/{order_id}", response_model=OrderOut,
            summary="Bestellung mit fixierter Version und Nachkalkulation")
async def get_order(order_id: str, db: Session = Depends(get_db),
                    tenant_id: str = Depends(get_tenant_id),
                    user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer Rezepturbestellungen.")
    try:
        return _service(db, tenant_id, user).get_order(order_id)
    except RecipeNotFound as exc:
        raise _handle(exc) from exc
