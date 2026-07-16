"""FEED-CONS-032 red contract for reproducible consulting report drafts."""

from datetime import date, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.v1.endpoints import feeding_consulting
from app.auth.deps import get_current_user
from app.core.tenant import get_tenant_id
from app.main import app
from test_feeding_actual_api import BASE, HEADERS
from test_feeding_measure_lifecycle_api import _measure


client = TestClient(app, raise_server_exceptions=False)


def test_case_measure_link_and_reproducible_versioned_report_draft() -> None:
    case = client.post(
        f"{BASE}/feeding/consulting-cases",
        headers=HEADERS,
        json={
            "title": f"Berichtsentwurf {uuid4().hex[:8]}",
            "case_type": "visit",
            "initial_situation": "Mischabweichung soll strukturiert nachverfolgt werden",
        },
    )
    assert case.status_code == 201, case.text
    case_id = case.json()["id"]
    observation = client.post(
        f"{BASE}/feeding/consulting-cases/{case_id}/observations",
        headers=HEADERS,
        json={
            "category": "fuetterung",
            "text": "Waagenkontrolle und Dosierreihenfolge wurden vor Ort geprueft",
            "client_ref": f"report-observation-{uuid4()}",
        },
    )
    assert observation.status_code == 201, observation.text
    measure = _measure(due_date=date.today() + timedelta(days=3))
    linked = client.post(
        f"{BASE}/feeding/consulting-cases/{case_id}/measures",
        headers=HEADERS,
        json={"measure_id": measure["id"]},
    )
    assert linked.status_code == 201, linked.text

    first = client.post(
        f"{BASE}/feeding/consulting-cases/{case_id}/report-drafts",
        headers=HEADERS,
        json={"reason": "Beratungsstand fuer die gemeinsame Durchsicht festhalten"},
    )
    assert first.status_code == 201, first.text
    draft = first.json()
    assert draft["version"] == 1
    assert draft["content"]["case"]["id"] == case_id
    assert len(draft["content"]["observations"]) == 1
    assert draft["content"]["measures"][0]["measure_id"] == measure["id"]
    assert "document_id" not in draft, "PDF/DMS ist ein spaeterer Berichts-Slice"

    repeated = client.post(
        f"{BASE}/feeding/consulting-cases/{case_id}/report-drafts",
        headers=HEADERS,
        json={"reason": "Identischen Datenstand reproduzierbar erneut anfordern"},
    )
    assert repeated.status_code == 201
    assert repeated.json()["id"] == draft["id"]
    assert repeated.json()["content_hash"] == draft["content_hash"]

    client.post(
        f"{BASE}/feeding/consulting-cases/{case_id}/observations",
        headers=HEADERS,
        json={
            "category": "fuetterung",
            "text": "Folgekontrolle dokumentiert einen neuen fachlichen Datenstand",
            "client_ref": f"report-observation-{uuid4()}",
        },
    )
    second = client.post(
        f"{BASE}/feeding/consulting-cases/{case_id}/report-drafts",
        headers=HEADERS,
        json={"reason": "Folgekontrolle als neue Berichtsversion festhalten"},
    )
    assert second.status_code == 201, second.text
    assert second.json()["version"] == 2
    assert len(second.json()["content"]["observations"]) == 2

    history = client.get(
        f"{BASE}/feeding/consulting-cases/{case_id}/report-drafts", headers=HEADERS
    )
    assert [item["version"] for item in history.json()] == [2, 1]

    outsider_app = FastAPI()
    outsider_app.include_router(feeding_consulting.router)
    outsider_app.dependency_overrides[get_current_user] = lambda: {
        "sub": f"outsider-{uuid4()}",
        "roles": ["FUTTERMITTEL_LESEN"],
    }
    outsider_app.dependency_overrides[get_tenant_id] = lambda: HEADERS["X-Tenant-Id"]
    with TestClient(outsider_app, raise_server_exceptions=False) as outsider:
        assert (
            outsider.get(
                f"/feeding/consulting-cases/{case_id}/report-drafts"
            ).status_code
            == 404
        )
        assert (
            outsider.get(f"/feeding/consulting-cases/{case_id}/measures").status_code
            == 404
        )


def test_unscoped_own_case_cannot_link_measure_from_ungranted_business() -> None:
    measure = _measure(due_date=date.today() + timedelta(days=3))
    writer_subject = f"external-writer-{uuid4()}"
    writer_app = FastAPI()
    writer_app.include_router(feeding_consulting.router)
    writer_app.dependency_overrides[get_current_user] = lambda: {
        "sub": writer_subject,
        "roles": ["FUTTERMITTEL_BEARBEITEN"],
    }
    writer_app.dependency_overrides[get_tenant_id] = lambda: HEADERS["X-Tenant-Id"]
    with TestClient(writer_app, raise_server_exceptions=False) as writer:
        case = writer.post(
            "/feeding/consulting-cases",
            json={
                "title": "Eigener Fall ohne fremden Betriebsscope",
                "case_type": "remote",
                "initial_situation": "Noch keinem Betrieb zugeordnet",
            },
        )
        assert case.status_code == 201, case.text
        denied = writer.post(
            f"/feeding/consulting-cases/{case.json()['id']}/measures",
            json={"measure_id": measure["id"]},
        )
        assert denied.status_code == 404
