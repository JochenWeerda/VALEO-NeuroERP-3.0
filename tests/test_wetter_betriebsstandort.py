"""Wetterwege ohne Koordinate: Betriebsstandort des Mandanten (09.11.2026).

Die Studio-Maske ``agrar/wetter`` rief ``/wetter/boden`` ohne lat/lon und bekam 422; die alte Warnungsseite setzte
fest Emden fuer jeden Mandanten. Jetzt gilt ``tenants.settings.standort``; fehlt er, sagt die Antwort, was fehlt.
"""
from __future__ import annotations

import json
import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)


@pytest.fixture(scope="module")
def mandanten():
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    mit, ohne = f"wt-{uuid.uuid4().hex[:8]}", f"wt-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name, settings) VALUES (:id, :id, CAST(:s AS jsonb))"),
                  {"id": mit, "s": json.dumps({"standort": {"lat": 52.5, "lon": 8.1}})})
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :id)"), {"id": ohne})
    yield {"mit": mit, "ohne": ohne}
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id IN (:a, :b)"), {"a": mit, "b": ohne})


def test_standort_aus_den_mandanten_einstellungen(mandanten, monkeypatch):
    from fastapi.testclient import TestClient

    from app.api.v1.endpoints import agrar_wetter
    from app.main import app

    gefragt: list[dict] = []

    async def abruf(url, params, cache_ttl=0):
        gefragt.append(params)
        return {"alerts": []}

    monkeypatch.setattr(agrar_wetter, "_cached_get", abruf)
    client = TestClient(app, raise_server_exceptions=False)
    kopf = {"Authorization": "Bearer dev-token"}
    ohne = client.get("/api/v1/agrar/wetter/warnungen", headers={**kopf, "X-Tenant-Id": mandanten["ohne"]})
    assert ohne.status_code == 422 and "Betriebsstandort" in ohne.text
    mit = client.get("/api/v1/agrar/wetter/warnungen", headers={**kopf, "X-Tenant-Id": mandanten["mit"]})
    assert mit.status_code == 200, mit.text
    assert (gefragt[-1]["lat"], gefragt[-1]["lon"]) == (52.5, 8.1)
    eigene = client.get("/api/v1/agrar/wetter/warnungen?lat=53.0&lon=7.0",
                        headers={**kopf, "X-Tenant-Id": mandanten["ohne"]})
    assert eigene.status_code == 200 and (gefragt[-1]["lat"], gefragt[-1]["lon"]) == (53.0, 7.0)
