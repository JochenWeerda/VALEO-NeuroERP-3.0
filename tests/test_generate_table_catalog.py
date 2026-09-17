"""Tests fuer scripts/generate_table_catalog.py."""

from __future__ import annotations

import json

import pytest

from scripts.generate_table_catalog import (
    KNOWN_SIBLING_MODELS,
    assemble_catalog,
    catalog_for_check,
    normalize_markdown,
    render_json,
    render_markdown,
)


def _sample_catalog() -> dict:
    tables = [
        ("domain_crm", "crm_consents"),
        ("domain_crm", "crm_contact_consents"),
        ("domain_erp", "journal_entries"),
        ("domain_finance", "journal_entries"),
    ]
    columns = [
        ("domain_crm", "crm_consents", "id", "character varying", "NO", 1),
        ("domain_crm", "crm_consents", "partner_id", "character varying", "NO", 2),
        ("domain_crm", "crm_consents", "purpose", "character varying", "YES", 3),
        ("domain_crm", "crm_contact_consents", "id", "character varying", "NO", 1),
        ("domain_crm", "crm_contact_consents", "contact_id", "character varying", "NO", 2),
        ("domain_crm", "crm_contact_consents", "consent_type", "character varying", "NO", 3),
        ("domain_erp", "journal_entries", "id", "character varying", "NO", 1),
        ("domain_finance", "journal_entries", "id", "character varying", "NO", 1),
    ]
    pks = [
        ("domain_crm", "crm_consents", "id", 1),
        ("domain_crm", "crm_contact_consents", "id", 1),
    ]
    return assemble_catalog(tables, columns, pks, [])


def test_geschwister_stehen_getrennt() -> None:
    payload = _sample_catalog()
    crm = payload["schemas"]["domain_crm"]["tables"]
    assert "partner_id" in [c["name"] for c in crm["crm_consents"]["columns"]]
    assert "contact_id" in [c["name"] for c in crm["crm_contact_consents"]["columns"]]
    assert "contact_id" not in [c["name"] for c in crm["crm_consents"]["columns"]]
    siblings = {(item["left"], item["right"]) for item in payload["sibling_models"]}
    left = f"{KNOWN_SIBLING_MODELS[0][0]}.{KNOWN_SIBLING_MODELS[0][1]}"
    right = f"{KNOWN_SIBLING_MODELS[0][2]}.{KNOWN_SIBLING_MODELS[0][3]}"
    assert (left, right) in siblings


def test_gleicher_name_in_zwei_schemas() -> None:
    payload = _sample_catalog()
    cross = {item["table"]: item["schemas"] for item in payload["same_name_across_schemas"]}
    assert cross["journal_entries"] == ["domain_erp", "domain_finance"]


def test_markdown_nennt_beide_consent_tabellen() -> None:
    md = render_markdown(_sample_catalog(), today="2026-09-17")
    assert "`crm_consents`" in md
    assert "`crm_contact_consents`" in md
    assert "Nicht manuell bearbeiten" in md
    assert "partner_id" in md
    assert "contact_id" in md
    assert "| Domain |" in md
    assert "`crm`" in md


def test_json_ist_stabil_sortiert() -> None:
    first = render_json(_sample_catalog())
    second = render_json(_sample_catalog())
    assert first == second
    body = json.loads(first)
    assert "generated_at" not in body
    assert list(body["schemas"]) == sorted(body["schemas"])


def test_normalize_markdown_ignoriert_review_datum() -> None:
    a = render_markdown(_sample_catalog(), today="2026-01-01")
    b = render_markdown(_sample_catalog(), today="2026-09-17")
    assert normalize_markdown(a) == normalize_markdown(b)


def test_catalog_for_check_laesst_schemas() -> None:
    payload = _sample_catalog()
    checked = catalog_for_check(payload)
    assert "crm_consents" in checked["schemas"]["domain_crm"]["tables"]


def test_markdown_nennt_verbraucher() -> None:
    from scripts.table_lineage import attach_lineage

    payload = _sample_catalog()
    attach_lineage(
        payload,
        {
            ("domain_crm", "crm_consents"): {
                "read_by": ["app/crm/router.py"],
                "written_by": ["app/crm/router.py"],
                "screens": ["crm/consent"],
            }
        },
    )
    md = render_markdown(payload, today="2026-09-17")
    assert "## Verbraucher" in md
    assert "`app/crm/router.py`" in md
    assert "`crm/consent`" in md


@pytest.mark.integration
def test_ernte_enthaelt_beide_consent_tabellen(require_db) -> None:
    from scripts.generate_table_catalog import harvest

    payload = harvest()
    crm = payload["schemas"]["domain_crm"]["tables"]
    assert "crm_consents" in crm
    assert "crm_contact_consents" in crm
    partner_cols = {c["name"] for c in crm["crm_consents"]["columns"]}
    contact_cols = {c["name"] for c in crm["crm_contact_consents"]["columns"]}
    assert "partner_id" in partner_cols
    assert "contact_id" in contact_cols
    assert "contact_id" not in partner_cols
    assert "app/crm/router.py" in crm["crm_consents"].get("written_by", [])
    assert "app/api/v1/endpoints/crm_consents.py" in crm["crm_contact_consents"].get(
        "read_by", []
    )
