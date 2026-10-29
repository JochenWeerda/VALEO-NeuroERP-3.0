"""All existing Biostimulanz adapters use the verified tenant, shared PG rollback only."""
import os
from uuid import uuid4
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.auth.deps import get_current_user
from app.core.database import engine, get_db
from app.core.tenant import get_tenant_id
from app.domains.agrar.api import biostimulanzien as routes
from app.infrastructure.models import Biostimulanz, Tenant


@pytest.mark.integration
@pytest.mark.parametrize("operation", ["list", "search", "detail", "create", "patch"])
def test_all_adapters_ignore_caller_selected_tenant(operation):
    assert engine.url.get_backend_name() == "postgresql"
    assert engine.url.database == "valeo_probe" or os.getenv("CI") == "true"
    marker = uuid4().hex
    a, b = str(uuid4()), str(uuid4())
    own, foreign = str(uuid4()), str(uuid4())
    with engine.connect() as conn:
        outer = conn.begin()
        try:
            with Session(bind=conn, join_transaction_mode="create_savepoint") as db:
                for tenant in (a, b):
                    db.add(Tenant(id=tenant, name="Synthetischer Pruefmandant", domain=f"{tenant}.invalid"))
                db.flush()
                for item, tenant in ((own, a), (foreign, b)):
                    db.add(Biostimulanz(id=item, tenant_id=tenant, artikelnummer=item, name=f"SYNTH-{marker}", typ="Biostimulanz", zusammensetzung={}, anwendungsbereich=[]))
                db.flush()
                app = FastAPI()
                app.include_router(routes.router, prefix="/bio")
                app.dependency_overrides[get_db] = lambda: db
                client = TestClient(app)
                assert client.get(f"/bio/{own}").status_code == 401
                app.dependency_overrides[get_tenant_id] = lambda: a
                app.dependency_overrides[get_current_user] = lambda: {"sub": "synthetic-actor", "roles": ["AGRAR_BEARBEITEN"]}
                if operation == "list":
                    response = client.get("/bio", params={"tenant_id": b, "search": marker})
                    assert response.status_code == 200, response.text
                    assert [row["id"] for row in response.json()["items"]] == [own]
                elif operation == "search":
                    response = client.get("/bio/search", params={"tenant_id": b, "q": marker})
                    assert response.status_code == 200, response.text
                    assert [row["id"] for row in response.json()] == [own]
                elif operation == "detail":
                    assert client.get(f"/bio/{own}", params={"tenant_id": b}).status_code == 200
                    assert client.get(f"/bio/{foreign}", params={"tenant_id": b}).status_code == 404
                elif operation == "patch":
                    assert client.patch(f"/bio/{foreign}", params={"tenant_id": b}, json={"name": "FOREIGN"}).status_code == 404
                    response = client.patch(f"/bio/{own}", params={"tenant_id": b}, json={"name": "SYNTH-CHANGED"})
                    assert response.status_code == 200, response.text
                    assert response.json()["tenant_id"] == a
                    assert db.get(Biostimulanz, foreign).name == f"SYNTH-{marker}"
                else:
                    body = {"artikelnummer": str(uuid4()), "name": "SYNTH-NEW", "typ": "Biostimulanz", "tenant_id": b}
                    response = client.post("/bio", params={"tenant_id": b}, json=body)
                    assert response.status_code == 201, response.text
                    assert response.json()["tenant_id"] == a
                app.dependency_overrides[get_current_user] = lambda: {"sub": "synthetic-reader", "roles": ["AGRAR_LESEN"]}
                assert client.patch(f"/bio/{own}", json={"name": "FORBIDDEN"}).status_code == 403
        finally:
            outer.rollback()
