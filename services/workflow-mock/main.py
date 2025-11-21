from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.post("/api/v1/workflows/definitions")
async def register_workflow(definition: dict) -> dict:
    return {"status": "registered", "name": definition.get("name")}
