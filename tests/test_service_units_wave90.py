"""Wave 90 — Unit-Tests fuer kunden_merge, kontrakte_service (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# kunden_merge — norm_id, bp_keys, crm_keys, reconcile_records
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_norm_id_lowercases_and_strips() -> None:
    from app.services.kunden_merge import norm_id
    result = norm_id("K-001")
    assert result == result.lower()
    assert result == "k001"


@pytest.mark.unit
def test_norm_id_none_returns_none() -> None:
    from app.services.kunden_merge import norm_id
    result = norm_id(None)
    assert result is None


@pytest.mark.unit
def test_norm_id_empty_string_returns_none() -> None:
    from app.services.kunden_merge import norm_id
    result = norm_id("")
    assert result is None


@pytest.mark.unit
def test_bp_keys_returns_dict() -> None:
    from app.services.kunden_merge import bp_keys
    bp = {"business_partner_id": "BP-001", "partner_number": "K001"}
    result = bp_keys(bp)
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.unit
def test_crm_keys_returns_dict() -> None:
    from app.services.kunden_merge import crm_keys
    rec = {"crm_id": "CRM-001", "kunden_nr": "K001"}
    result = crm_keys(rec)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_reconcile_records_empty_inputs() -> None:
    from app.services.kunden_merge import reconcile_records
    report = reconcile_records([], [])
    assert "summary" in report
    assert report["summary"]["total_kunden"] == 0


@pytest.mark.unit
def test_reconcile_records_single_match() -> None:
    from app.services.kunden_merge import reconcile_records
    kunden = [{"kunden_nr": "K001", "name": "Agrar GmbH", "plz": "12345", "ort": "Berlin"}]
    bps = [{"business_partner_id": "BP-001", "partner_number": "K001", "name": "Agrar GmbH", "plz": "12345", "ort": "Berlin"}]
    report = reconcile_records(kunden, bps)
    assert report["summary"]["total_kunden"] == 1
    assert report["summary"]["total_business_partners"] == 1


@pytest.mark.unit
def test_reconcile_records_has_candidates() -> None:
    from app.services.kunden_merge import reconcile_records
    kunden = [{"kunden_nr": "K001", "name": "Test GmbH", "plz": "12345"}]
    bps = [{"business_partner_id": "BP-001", "partner_number": "K001", "name": "Test GmbH", "plz": "12345"}]
    report = reconcile_records(kunden, bps)
    assert "candidates" in report
    assert isinstance(report["candidates"], list)


@pytest.mark.unit
def test_reconcile_records_summary_structure() -> None:
    from app.services.kunden_merge import reconcile_records
    report = reconcile_records([], [])
    summary = report["summary"]
    for key in ("total_kunden", "total_business_partners", "counts"):
        assert key in summary


# ---------------------------------------------------------------------------
# kontrakte_service — line_to_dict, build_contract_steering, contract_to_dict
# ---------------------------------------------------------------------------

def _make_kontrakt_line():
    from app.services.kontrakte_service import KonContractLine
    line = KonContractLine()
    line.line_id = "L-001"
    line.line_no = 1
    line.quantity = Decimal("100")
    line.unit = "t"
    line.price = Decimal("205.50")
    line.currency = "EUR"
    line.artikel_key = "WW"
    return line


def _make_kontrakt():
    from app.services.kontrakte_service import KonContract
    c = KonContract()
    c.contract_id = "CON-001"
    c.contract_no = "K-2024-001"
    c.party_id = "L-001"
    c.total_quantity = Decimal("100")
    c.unit = "t"
    c.status = "active"
    c.tenant_id = "T001"
    c.pricing_model = "fix"
    c.min_price = Decimal("200")
    return c


@pytest.mark.unit
def test_line_to_dict_returns_dict() -> None:
    from app.services.kontrakte_service import line_to_dict
    line = _make_kontrakt_line()
    result = line_to_dict(line, Decimal("50"))
    assert isinstance(result, dict)


@pytest.mark.unit
def test_line_to_dict_rest_stored() -> None:
    from app.services.kontrakte_service import line_to_dict
    line = _make_kontrakt_line()
    result = line_to_dict(line, Decimal("75"))
    assert result["qty_remaining"] == pytest.approx(75.0)


@pytest.mark.unit
def test_build_contract_steering_returns_dict() -> None:
    from app.services.kontrakte_service import build_contract_steering
    contract = _make_kontrakt()
    result = build_contract_steering(contract, Decimal("80"), first_line_price=205.50)
    assert isinstance(result, dict)


@pytest.mark.unit
def test_build_contract_steering_has_required_keys() -> None:
    from app.services.kontrakte_service import build_contract_steering
    contract = _make_kontrakt()
    result = build_contract_steering(contract, Decimal("80"))
    # Should contain status and progress info
    assert len(result) > 0


@pytest.mark.unit
def test_contract_to_dict_returns_dict() -> None:
    from app.services.kontrakte_service import contract_to_dict
    contract = _make_kontrakt()
    result = contract_to_dict(contract, [], Decimal("100"))
    assert isinstance(result, dict)


@pytest.mark.unit
def test_contract_to_dict_has_contract_no() -> None:
    from app.services.kontrakte_service import contract_to_dict
    contract = _make_kontrakt()
    result = contract_to_dict(contract, [], Decimal("100"))
    assert "contract_no" in result or "kontrakt_nr" in result or "id" in result
