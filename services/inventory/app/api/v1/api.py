"""API Router v1."""

from fastapi import APIRouter

from .endpoints import epcis, inventory, locations, reports, stock, warehouses

api_router = APIRouter()
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(locations.router, prefix="/warehouses", tags=["locations"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(stock.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(reports.router, prefix="/inventory", tags=["reports"])
api_router.include_router(epcis.router, prefix="/inventory", tags=["epcis"])
