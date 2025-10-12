"""Finance API routers."""

from fastapi import APIRouter

***REMOVED*** Import from existing fibu_router for now, will migrate later
from ....routers.fibu_router import router as fibu_router

router = APIRouter()
***REMOVED*** Include existing fibu endpoints under finance
router.include_router(fibu_router, tags=["finance"])

__all__ = ['router']

