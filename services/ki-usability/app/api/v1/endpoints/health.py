"""Health check."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
def health() -> dict:
    return {"status": "healthy", "service": "ki-usability-api", "version": "1.0.0"}
