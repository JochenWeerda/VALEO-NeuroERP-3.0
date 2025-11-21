from fastapi import FastAPI

app = FastAPI(title="CRM Sync Service", version="0.1.0")


@app.get("/health")
async def health():
    return {"service": "crm-sync", "status": "ok"}


@app.post("/api/v1/legacy/customers/{legacy_id}/ingest")
async def ingest_legacy_customer(legacy_id: str):
    """Placeholder endpoint representing adapter ingestion."""
    return {"legacy_id": legacy_id, "status": "queued"}
