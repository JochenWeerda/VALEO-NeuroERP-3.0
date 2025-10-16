"""Inventory API routers."""

from fastapi import APIRouter
from ....api.v1.endpoints.articles import router as articles_router
from .warehouses import router as warehouses_router
from .stock_movements import router as stock_movements_router
from .inventory_reports import router as inventory_reports_router

router = APIRouter()
router.include_router(articles_router, prefix="/articles", tags=["articles"])
router.include_router(warehouses_router, prefix="/warehouses", tags=["warehouses"])
router.include_router(stock_movements_router, prefix="/stock-movements", tags=["stock-movements"])
router.include_router(inventory_reports_router, prefix="/reports", tags=["inventory-reports"])

__all__ = ['router']

