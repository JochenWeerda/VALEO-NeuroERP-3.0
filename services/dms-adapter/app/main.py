"""
DMS-Adapter Service

FastAPI-Anwendung für Dokumentenverwaltung.
Verbindet NeuroERP mit Paperless-ngx als DMS-Backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.api.routes import router

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

# FastAPI App erstellen
app = FastAPI(
    title="DMS-Adapter",
    description="""
    ## DMS-Adapter für NeuroERP
    
    Dieser Service verbindet NeuroERP mit Paperless-ngx als Document Management System (DMS).
    
    ### Hauptfunktionen
    
    - **Upload**: Dokumente hochladen und mit Geschäftsobjekten verknüpfen
    - **Liste**: Dokumente nach Geschäftsobjekt filtern
    - **Download**: Dokumente herunterladen
    - **Inbox**: Unzugeordnete Dokumente verwalten
    - **Suche**: Volltextsuche in allen Dokumenten
    
    ### Authentifizierung
    
    Alle Requests müssen den Header `X-Tenant-ID` enthalten für Mandantentrennung.
    
    ### Tag-Konvention in Paperless-ngx
    
    - `TENANT:{tenant_id}` - Mandantenzuordnung
    - `OBJ:{type}` - Geschäftsobjekt-Typ (INVOICE, ORDER, etc.)
    - `OBJID:{id}` - Geschäftsobjekt-ID
    - `DOCTYPE:{type}` - Dokumenttyp
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router einbinden
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Startup-Event"""
    logger.info(f"Starting {settings.SERVICE_NAME}...")
    logger.info(f"Paperless URL: {settings.PAPERLESS_URL}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown-Event"""
    logger.info(f"Shutting down {settings.SERVICE_NAME}...")


@app.get("/")
async def root():
    """Root-Endpoint"""
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/dms/health",
    }

