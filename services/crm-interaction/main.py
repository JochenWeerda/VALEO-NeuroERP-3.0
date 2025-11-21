from fastapi import FastAPI

app = FastAPI(title="CRM Interaction Service", version="0.1.0")


@app.get("/health")
async def health():
    return {"service": "crm-interaction", "status": "ok"}


@app.post("/api/v1/interactions")
async def ingest_interaction(event: dict):
    """Stub ingestion endpoint."""
    return {"status": "accepted", "event": event}
