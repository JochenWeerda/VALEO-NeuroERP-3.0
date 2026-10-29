"""GoBD-Belegnachweise liegen in der Datenbank, nicht im Arbeitsspeicher (20.10.2026).

Vorher legte keine Migration ``domain_shared.audit_evidence`` an; jede Installation schrieb Nachweise in einen
Speicher-Ersatz, ``gobd-check`` meldete "konform" daraus, und ein Neustart loeschte sie. Der Pruefer kam aus dem
Body. Geprueft gegen eine frische Pruefstand-Datenbank.
"""
from __future__ import annotations

import os
import uuid

import pytest
from fastapi import Request  # Modulebene: FastAPI loest die Annotation hier auf

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)

HAUS = f"gobd-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_shared.audit_evidence LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar oder nicht migriert: {fehler}")
    yield motor
    with motor.begin() as v:
        v.execute(text("DELETE FROM domain_shared.audit_evidence WHERE tenant_id = :h"), {"h": HAUS})


@pytest.fixture(autouse=True)
def gepruefte_person():
    from app.auth.deps import get_current_user
    from app.core.security import require_bearer_token
    from app.main import app
    from testgrenze import ALLE_FACHROLLEN, mandant_aus_kopf

    def geprueft(request: Request) -> str:
        tenant = mandant_aus_kopf(request)
        request.state.tenant_id = tenant
        request.state.tenant_verified = True
        request.state.token_claims = {"sub": "pruefer-token", "tenant_id": tenant, "roles": list(ALLE_FACHROLLEN)}
        return "pruefstand"

    app.dependency_overrides[require_bearer_token] = geprueft
    app.dependency_overrides[get_current_user] = lambda: {"sub": "pruefer-token", "roles": list(ALLE_FACHROLLEN)}
    yield
    app.dependency_overrides.pop(require_bearer_token, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def test_nachweis_wird_gespeichert_und_gobd_check_liest_die_tabelle(engine, client):
    from sqlalchemy import text

    kopf = {"X-Tenant-ID": HAUS}
    eintrag = client.post("/api/v1/audit-evidence", headers=kopf,
                          json={"aggregate_type": "rechnung", "aggregate_id": "RE-1", "action": "verbucht"})
    assert eintrag.status_code == 201, eintrag.text
    kennung = eintrag.json()["audit_entry_id"]
    vorher = client.get("/api/v1/audit-evidence/policy/gobd-check/rechnung/RE-1", headers=kopf).json()
    assert vorher["gobd_compliant"] is False and vorher["audit_entries_count"] == 1

    beleg = client.post(f"/api/v1/audit-evidence/{kennung}/evidence-refs", headers=kopf,
                        json={"external_id": "DMS-77", "verified": True, "verified_by": "im-body-behauptet"})
    assert beleg.status_code == 201, beleg.text
    assert beleg.json()["evidence_refs"][0]["verified_by"] == "pruefer-token"

    nachher = client.get("/api/v1/audit-evidence/policy/gobd-check/rechnung/RE-1", headers=kopf).json()
    assert nachher["gobd_compliant"] is True and nachher["evidence_count"] == 1
    with engine.connect() as v:
        assert v.execute(text("SELECT count(*) FROM domain_shared.audit_evidence WHERE tenant_id = :h"),
                         {"h": HAUS}).scalar() == 1


def test_fremder_mandant_sieht_den_nachweis_nicht(client):
    kopf = {"X-Tenant-ID": HAUS}
    kennung = client.post("/api/v1/audit-evidence", headers=kopf,
                          json={"aggregate_type": "rechnung", "aggregate_id": "RE-2"}).json()["audit_entry_id"]
    assert client.get(f"/api/v1/audit-evidence/{kennung}", headers={"X-Tenant-ID": "fremd-x"}).status_code == 404
