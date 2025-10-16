"""Agrar API routers."""

from fastapi import APIRouter
from .saatgut import router as saatgut_router
from .duenger import router as duenger_router
from .psm import router as psm_router

router = APIRouter()
router.include_router(saatgut_router, prefix="/saatgut", tags=["saatgut"])
router.include_router(duenger_router, prefix="/duenger", tags=["duenger"])
router.include_router(psm_router, prefix="/psm", tags=["psm"])

__all__ = ['router']