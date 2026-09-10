"""Exercise real escalation service results through FastAPI response validation."""
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.api.v1.endpoints.finance_actions import router
from app.core.database import get_db


@pytest.mark.parametrize("current,next_stage", [(None, "1"), ("1", "2"), ("2", "3"), ("3", "INKASSO")])
def test_escalation_serializes_service_and_audit_stages(current, next_stage):
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = (
        {"stufe": current} if current is not None else None
    )
    app = FastAPI()
    app.include_router(router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        response = client.post("/finance/mahnstufe/RE-CONTRACT/eskalieren",
                               headers={"X-Tenant-ID": "contract-test"},
                               json={"operator": "contract-test"})
    assert response.status_code == 201, response.text
    assert response.json()["stufe"] == next_stage
    assert response.json()["vorherige_stufe"] == current
    db.commit.assert_called_once()


def test_maximum_stage_remains_rejected_without_another_write():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {"stufe": "INKASSO"}
    app = FastAPI()
    app.include_router(router, prefix="/finance")
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        response = client.post("/finance/mahnstufe/RE-CONTRACT/eskalieren", json={"operator": "test"})
    assert response.status_code == 422
    db.commit.assert_not_called()
    assert db.execute.call_count == 1
