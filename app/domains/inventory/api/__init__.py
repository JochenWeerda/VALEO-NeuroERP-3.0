"""Inventory API routers."""

from fastapi import APIRouter
from ....api.v1.endpoints.articles import router as articles_router
from .warehouses import router as warehouses_router

router = APIRouter()
router.include_router(articles_router, prefix="/articles", tags=["articles"])
router.include_router(warehouses_router, prefix="/warehouses", tags=["warehouses"])

__all__ = ['router']

