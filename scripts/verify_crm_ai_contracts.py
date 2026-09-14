"""Offline HTTP regression of the existing CRM-AI simulation API.

Run inside the built crm-ai image (working directory /app). No database is
replaced: creating an AsyncSession does not connect until a query is executed.
The existing simulated endpoints do not execute queries. No external traffic.
"""
import importlib
import os
from pathlib import Path
import sys
import unittest
from uuid import UUID

import httpx

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@127.0.0.1:1/test")
sys.path.insert(0, str(Path.cwd()))
app = importlib.import_module("main").app
ID = "550e8400-e29b-41d4-a716-446655440001"


class Contracts(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_health_and_openapi(self):
        response = await self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "crm-ai")
        schema = (await self.client.get("/openapi.json")).json()
        self.assertEqual(len(schema["paths"]), 11)
        for path, methods in schema["paths"].items():
            for operation in methods.values():
                self.assertFalse(any(p["name"] == "db" for p in operation.get("parameters", [])), path)

    async def test_prediction_response_contracts(self):
        cases = [
            ("lead-score", {"lead_id": ID, "features": {}}, "lead_id"),
            ("predict/churn", {"customer_id": ID, "features": {}}, "customer_id"),
            ("predict/clv", {"customer_id": ID, "features": {}}, "customer_id"),
            ("recommend/actions", {"customer_id": ID, "context": {}, "available_actions": []}, "entity_id"),
            ("analyze/email", {"email_id": ID, "content": "Please help with my invoice"}, "email_id"),
            ("classify/case", {"case_id": ID, "title": "Help", "description": "Unable to sign in"}, "case_id"),
        ]
        for path, payload, field in cases:
            with self.subTest(path=path):
                response = await self.client.post("/api/v1/ai/" + path, json=payload)
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()[field], ID)

    async def test_models_filter_pagination(self):
        response = await self.client.get("/api/v1/ai/models?model_type=lead_scoring&limit=1")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(len(response.json()["models"]), 1)
        self.assertEqual((await self.client.get("/api/v1/ai/models?limit=0")).status_code, 422)

    async def test_batch_response_contract(self):
        for kind in ("lead_scoring", "churn_prediction", "clv"):
            with self.subTest(kind=kind):
                response = await self.client.post("/api/v1/ai/batch/predict", json={
                    "entity_ids": [ID], "entity_type": "lead", "prediction_type": kind})
                self.assertEqual(response.status_code, 200, response.text)
                data = response.json()
                UUID(data["batch_id"])
                self.assertEqual(data["total_successful"], len(data["predictions"]))
                self.assertEqual(data["total_processed"], data["total_successful"] + data["total_failed"])

    async def test_training_response_contract(self):
        response = await self.client.post("/api/v1/ai/models/train", json={
            "model_type": "lead_scoring", "algorithm": "random_forest", "training_data_query": {}})
        self.assertEqual(response.status_code, 202, response.text)
        UUID(response.json()["model_id"])
        UUID(response.json()["training_job_id"])

    async def test_feedback_contract(self):
        response = await self.client.post("/api/v1/ai/feedback", json={
            "prediction_id": ID, "rating": 4, "feedback_type": "accuracy"})
        self.assertEqual(response.status_code, 201, response.text)

    async def test_invalid_requests(self):
        self.assertEqual((await self.client.post("/api/v1/ai/lead-score", json={"lead_id": "bad", "features": {}})).status_code, 422)
        self.assertEqual((await self.client.post("/api/v1/ai/recommend/actions", json={"context": {}, "available_actions": []})).status_code, 400)
        self.assertEqual((await self.client.post("/api/v1/ai/batch/predict", json={"entity_ids": [], "entity_type": "lead", "prediction_type": "lead_scoring"})).status_code, 422)
        self.assertEqual((await self.client.post("/api/v1/ai/batch/predict", json={"entity_ids": [ID], "entity_type": "lead", "prediction_type": "unknown"})).status_code, 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
