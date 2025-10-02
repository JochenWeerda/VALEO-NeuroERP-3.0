#!/usr/bin/env python
"""
Einfacher API-Server für das ERP-System.

Dieser Server dient als Fallback, falls der modulare Server nicht funktioniert.
"""

import logging
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_server")

# FastAPI-App erstellen
app = FastAPI(
    title="Simple ERP API",
    description="Eine einfache API für das ERP-System (Fallback)",
    version="0.1.0",
)

# CORS-Middleware hinzufügen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Profiling-Middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Middleware zur Messung der Antwortzeit"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Root-Endpunkt
@app.get("/")
async def root():
    """Root-Endpunkt mit Grundinformationen zur API"""
    return {
        "message": "Willkommen bei der Simple ERP API (Fallback)",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_url": "/api/v1"
    }

# Health-Check-Endpunkt
@app.get("/health")
async def health_check():
    """Einfacher Health-Check-Endpunkt"""
    return {"status": "healthy", "timestamp": time.time()}

# Einfacher Status-Endpunkt
@app.get("/api/v1/status")
async def status():
    """Grundlegender Statusendpunkt für Health-Checks"""
    return {"status": "online", "message": "Einfacher Server läuft (Fallback)"}

# Einfacher Batch-Endpunkt
@app.get("/api/v1/batch/test")
async def batch_test():
    """Test-Endpunkt für Batch-API"""
    return {"status": "success", "message": "Batch-API funktioniert"}

# Einfacher Performance-Endpunkt
@app.get("/api/v1/performance/test")
async def performance_test():
    """Test-Endpunkt für Performance-API"""
    return {"status": "success", "message": "Performance-API funktioniert"}

# Hauptfunktion
if __name__ == "__main__":
    logger.info("Starte einfachen API-Server auf Port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 