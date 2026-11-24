"""M4-LO-P0: Mandantenleck ops_fahrer / transporte.py.

Gegen den gemeinsamen Pruefstand (TEST_DATABASE_URL / valeo_probe). Eigene Testdaten
werden angelegt und am Ende geloescht — kein Probe-Reset.
"""

from __future__ import annotations

import os
import uuid

import pytest
from fastapi import Request
from sqlalchemy import create_engine, text

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")
os.environ.setdefault("PGAPPNAME", "agent:cursor-m4-lo-p0")

HAUS_A = f"m4lo-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"m4lo-b-{uuid.uuid4().hex[:6]}"


def _kopf(mandant: str) -> dict[str, str]:
    return {
        "Authorization": "Bearer dev-token",
        "X-Tenant-ID": mandant,
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="module")
def engine():
    try:
        eng = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        with eng.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_ops.ops_fahrer LIMIT 0"))
            hat = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_schema='domain_ops' AND table_name='ops_fahrer' "
                    "AND column_name='tenant_id'"
                )
            ).scalar()
            if not hat:
                pytest.skip(
                    "ops_fahrer.tenant_id fehlt — Migration ops_fahrer_tenant_20261124 anwenden"
                )
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Pruefstand nicht erreichbar: {fehler}")
    return eng


@pytest.fixture()
def client(engine):
    from fastapi.testclient import TestClient

    from app.auth import deps, deps_oidc
    from app.core.security import require_bearer_token
    from app.main import app

    def user(request: Request):
        tenant = (request.headers.get("X-Tenant-ID") or "").strip()
        return {
            "sub": "m4lo-fahrer-test",
            "roles": ["admin"],
            "raw": {"tenant_id": tenant, "sub": "m4lo-fahrer-test"},
        }

    def bearer(request: Request):
        declared = user(request)
        tenant = declared["raw"]["tenant_id"]
        request.state.tenant_verified = bool(tenant)
        request.state.tenant_id = tenant
        request.state.token_claims = {"sub": declared["sub"], **declared["raw"]}
        return "explicit-synthetic-test-token"

    app.dependency_overrides[require_bearer_token] = bearer
    app.dependency_overrides[deps.get_current_user] = user
    app.dependency_overrides[deps_oidc.get_current_user] = user

    with TestClient(app, raise_server_exceptions=False) as tc:
        yield tc

    app.dependency_overrides.pop(require_bearer_token, None)
    app.dependency_overrides.pop(deps.get_current_user, None)
    app.dependency_overrides.pop(deps_oidc.get_current_user, None)


@pytest.fixture()
def zwei_fahrer(engine):
    """Je Mandant ein Fahrer direkt in der Tabelle."""
    id_a = f"DR-A{uuid.uuid4().hex[:6].upper()}"
    id_b = f"DR-B{uuid.uuid4().hex[:6].upper()}"
    pn_a = f"PA-{uuid.uuid4().hex[:5].upper()}"
    pn_b = f"PB-{uuid.uuid4().hex[:5].upper()}"

    with engine.begin() as v:
        for haus, name in ((HAUS_A, "Haus A"), (HAUS_B, "Haus B")):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "n": name},
            )
        for fahrer_id, haus, pn, name in (
            (id_a, HAUS_A, pn_a, "Mueller"),
            (id_b, HAUS_B, pn_b, "Schmidt"),
        ):
            v.execute(
                text(
                    "INSERT INTO domain_ops.ops_fahrer "
                    "(id, tenant_id, personalnummer, name, fuehrerschein, status) "
                    "VALUES (:id, :tid, :pn, :name, 'CE', 'verfuegbar')"
                ),
                {"id": fahrer_id, "tid": haus, "pn": pn, "name": name},
            )

    yield {"id_a": id_a, "id_b": id_b, "pn_a": pn_a, "pn_b": pn_b}

    with engine.begin() as v:
        v.execute(
            text("DELETE FROM domain_ops.ops_fahrer WHERE id = ANY(:ids)"),
            {"ids": [id_a, id_b]},
        )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )


def test_liste_zeigt_nur_eigenen_mandanten(client, zwei_fahrer):
    eigen = client.get("/api/v1/transporte/fahrer", headers=_kopf(HAUS_A))
    assert eigen.status_code == 200, eigen.text
    ids = {row.get("id") for row in eigen.json()}
    assert zwei_fahrer["id_a"] in ids
    assert zwei_fahrer["id_b"] not in ids


def test_get_fremder_fahrer_404(client, zwei_fahrer):
    fremd = client.get(
        f"/api/v1/transporte/fahrer/{zwei_fahrer['id_b']}", headers=_kopf(HAUS_A)
    )
    assert fremd.status_code == 404, fremd.text


def test_patch_fremder_fahrer_404(client, zwei_fahrer):
    patch = client.patch(
        f"/api/v1/transporte/fahrer/{zwei_fahrer['id_b']}",
        headers=_kopf(HAUS_A),
        json={"telefon": "040-LECK"},
    )
    assert patch.status_code == 404, patch.text


def test_delete_fremder_fahrer_404(client, zwei_fahrer, engine):
    delete = client.delete(
        f"/api/v1/transporte/fahrer/{zwei_fahrer['id_b']}",
        headers=_kopf(HAUS_A),
    )
    assert delete.status_code == 404, delete.text
    with engine.connect() as c:
        noch_da = c.execute(
            text("SELECT 1 FROM domain_ops.ops_fahrer WHERE id = :id"),
            {"id": zwei_fahrer["id_b"]},
        ).scalar()
    assert noch_da == 1


def test_create_setzt_mandant_und_fremd_unsichtbar(client, engine):
    with engine.begin() as v:
        for haus, name in ((HAUS_A, "Haus A"), (HAUS_B, "Haus B")):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :n) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "n": name},
            )

    pn = f"PC-{uuid.uuid4().hex[:5].upper()}"
    anlegen = client.post(
        "/api/v1/transporte/fahrer",
        headers=_kopf(HAUS_A),
        json={
            "personalnummer": pn,
            "name": "Neu",
            "vorname": "Test",
            "fuehrerschein": "C",
        },
    )
    assert anlegen.status_code == 201, anlegen.text
    body = anlegen.json()
    fahrer_id = body["id"]
    assert body.get("tenant_id") == HAUS_A

    fremd_liste = client.get("/api/v1/transporte/fahrer", headers=_kopf(HAUS_B))
    assert fremd_liste.status_code == 200, fremd_liste.text
    assert fahrer_id not in {row.get("id") for row in fremd_liste.json()}

    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_ops.ops_fahrer WHERE id = :id"), {"id": fahrer_id})
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"),
            {"h": [HAUS_A, HAUS_B]},
        )
