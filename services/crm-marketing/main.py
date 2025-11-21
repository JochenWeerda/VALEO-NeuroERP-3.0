from fastapi import FastAPI

app = FastAPI(title="CRM Marketing Service", version="0.1.0")


@app.get("/health")
async def health():
    return {"service": "crm-marketing", "status": "ok"}


@app.get("/api/v1/campaigns")
async def list_campaigns():
    return {"items": [], "total": 0}
