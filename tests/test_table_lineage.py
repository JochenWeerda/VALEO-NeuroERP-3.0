"""Tests fuer scripts/table_lineage.py (P3, ohne DB)."""

from __future__ import annotations

from pathlib import Path

from scripts.table_lineage import (
    attach_lineage,
    attach_screens,
    endpoint_needle,
    harvest_python_text,
    screen_entity_failures,
    split_qualified,
)


ROUTER_SNIPPET = '''
async def create_consent(db):
    await db.execute(text("""
            INSERT INTO domain_crm.crm_consents
            (id, tenant_id, partner_id, purpose, granted)
            VALUES (:id, :tid, :pid, :purpose, :granted)
    """))
    rows = await db.execute(text("SELECT * FROM domain_crm.crm_consents WHERE id = :id"))
    return rows
'''

ENDPOINT_SNIPPET = '''
"""Persistenz: ``domain_crm.crm_contact_consents`` — neben der Partner-Tabelle
``domain_crm.crm_consents`` (Art. 6/7, partner_id/purpose/granted).
"""

class CrmConsent:
    __tablename__ = "crm_contact_consents"
    __table_args__ = (
        {"schema": "domain_crm"},
    )
'''


def test_insert_ist_write_select_ist_read() -> None:
    found = harvest_python_text("app/crm/router.py", ROUTER_SNIPPET)
    key = ("domain_crm", "crm_consents")
    assert "app/crm/router.py" in found[key]["written_by"]
    assert "app/crm/router.py" in found[key]["read_by"]


def test_orm_und_docstring_lesen_contact_consents() -> None:
    found = harvest_python_text("app/api/v1/endpoints/crm_consents.py", ENDPOINT_SNIPPET)
    contact = found[("domain_crm", "crm_contact_consents")]
    assert "app/api/v1/endpoints/crm_consents.py" in contact["read_by"]
    partner = found[("domain_crm", "crm_consents")]
    assert "app/api/v1/endpoints/crm_consents.py" in partner["read_by"]
    assert partner["written_by"] == set()


def test_echte_consent_dateien() -> None:
    repo = Path(__file__).resolve().parents[1]
    router = (repo / "app/crm/router.py").read_text(encoding="utf-8")
    endpoint = (repo / "app/api/v1/endpoints/crm_consents.py").read_text(encoding="utf-8")
    from_router = harvest_python_text("app/crm/router.py", router)
    from_endpoint = harvest_python_text("app/api/v1/endpoints/crm_consents.py", endpoint)
    assert "app/crm/router.py" in from_router[("domain_crm", "crm_consents")]["written_by"]
    assert (
        "app/api/v1/endpoints/crm_consents.py"
        in from_endpoint[("domain_crm", "crm_contact_consents")]["read_by"]
    )


def test_entity_table_ohne_katalog_faellt() -> None:
    screens = [
        {
            "id": "crm/consent",
            "adapter": {"type": "native", "temporary": False},
            "dataSources": [
                {
                    "key": "entity",
                    "endpoint": "/api/v1/crm/consents/{entity_id}",
                    "table": "domain_crm.gibt_es_nicht",
                }
            ],
        }
    ]
    failures = screen_entity_failures(
        screens,
        {("domain_crm", "crm_consents")},
        {},
        {},
    )
    assert failures
    assert "gibt_es_nicht" in failures[0]


def test_entity_table_im_katalog_ist_ok() -> None:
    screens = [
        {
            "id": "crm/consent",
            "adapter": {"type": "native"},
            "dataSources": [
                {
                    "key": "entity",
                    "endpoint": "/api/v1/x/{entity_id}",
                    "table": "domain_crm.crm_consents",
                }
            ],
        }
    ]
    failures = screen_entity_failures(
        screens,
        {("domain_crm", "crm_consents")},
        {},
        {},
    )
    assert failures == []


def test_router_prefix_bindet_screen() -> None:
    rel = "app/api/v1/endpoints/crm_consents.py"
    text = (
        'router = APIRouter(prefix="/crm/consents", tags=["crm"])\n'
        'rows = db.execute(text("SELECT * FROM domain_crm.crm_contact_consents"))\n'
    )
    lineage = harvest_python_text(rel, text)
    screens = [
        {
            "id": "crm/consent",
            "adapter": {"type": "native"},
            "dataSources": [
                {"key": "entity", "endpoint": "/api/v1/crm/consents/{entity_id}"},
            ],
        }
    ]
    attach_screens(lineage, screens, {rel: text})
    assert "crm/consent" in lineage[("domain_crm", "crm_contact_consents")]["screens"]
    assert endpoint_needle("/api/v1/crm/consents/{entity_id}") == "/crm/consents"
    assert split_qualified("domain_crm.crm_consents") == ("domain_crm", "crm_consents")


def test_attach_lineage_schreibt_nur_bekannte_tabellen() -> None:
    payload = {
        "schemas": {
            "domain_crm": {
                "tables": {
                    "crm_consents": {"columns": []},
                }
            }
        }
    }
    attach_lineage(
        payload,
        {
            ("domain_crm", "crm_consents"): {
                "read_by": ["app/crm/router.py"],
                "written_by": ["app/crm/router.py"],
                "screens": ["crm/consent"],
            },
            ("domain_crm", "ghost"): {
                "read_by": ["app/ghost.py"],
                "written_by": [],
                "screens": [],
            },
        },
    )
    body = payload["schemas"]["domain_crm"]["tables"]["crm_consents"]
    assert body["written_by"] == ["app/crm/router.py"]
    assert body["screens"] == ["crm/consent"]
    assert "ghost" not in payload["schemas"]["domain_crm"]["tables"]
