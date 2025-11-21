"""
CRM Analytics Service
FastAPI application for advanced analytics, reporting, and business intelligence.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app.api.v1.api import api_router
from .app.config.settings import settings

app = FastAPI(
    title="CRM Analytics Service",
    description="Advanced analytics, reporting, and business intelligence for CRM",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "crm-analytics"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=6000,
        reload=True,
    )
