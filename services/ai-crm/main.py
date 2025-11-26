from fastapi import FastAPI

app = FastAPI(title="AI CRM Service", version="0.1.0")


@app.get("/health")
async def health():
    return {"service": "ai-crm", "status": "ok"}


@app.post("/ai/crm/compose-email")
async def compose_email(payload: dict):
    return {"subject": "[draft]", "body": "Placeholder response", "payload": payload}
