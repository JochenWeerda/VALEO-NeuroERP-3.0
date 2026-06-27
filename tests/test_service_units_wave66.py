"""Wave 66 — Unit-Tests fuer pii_detector und workflow_guards (pure logic)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# pii_detector  (pure regex-based PII detection — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_detect_pii_iban() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("IBAN DE89370400440532013000 bitte überweisen")
    types = [m.type for m in matches]
    assert "iban" in types


@pytest.mark.unit
def test_detect_pii_email() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("Schreib an max.muster@example.de für Rückfragen")
    types = [m.type for m in matches]
    assert "email" in types


@pytest.mark.unit
def test_detect_pii_phone() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("Ruf mich an unter 0179-1234567 an")
    assert any(m.type in ("phone", "telefon", "mobile", "phone_de") for m in matches)


@pytest.mark.unit
def test_detect_pii_clean_text() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("Weizen kostet 200 EUR je Tonne in Hamburch")
    assert len(matches) == 0


@pytest.mark.unit
def test_mask_irreversible_replaces_pii() -> None:
    from app.services.pii_detector import mask_irreversible
    original = "IBAN DE89370400440532013000"
    masked = mask_irreversible(original)
    assert "DE89370400440532013000" not in masked
    assert "[IBAN]" in masked or "***" in masked or "IBAN" in masked


@pytest.mark.unit
def test_mask_reversible_and_unmask() -> None:
    from app.services.pii_detector import mask_reversible, unmask
    original = "IBAN DE89370400440532013000"
    masked_text, token_map = mask_reversible(original)
    assert "DE89370400440532013000" not in masked_text
    assert len(token_map) > 0
    restored = unmask(masked_text, token_map)
    assert "DE89370400440532013000" in restored


@pytest.mark.unit
def test_mask_reversible_no_pii_unchanged() -> None:
    from app.services.pii_detector import mask_reversible
    text = "Weizen kostet 200 EUR"
    masked, tok = mask_reversible(text)
    assert tok == {} or len(tok) == 0
    assert masked == text


@pytest.mark.unit
def test_scan_dict_finds_email() -> None:
    from app.services.pii_detector import scan_dict
    data = {"name": "Max Muster", "contact": "max@example.com", "amount": 100}
    matches = scan_dict(data)
    assert any(m.type == "email" for m in matches)


@pytest.mark.unit
def test_scan_dict_nested() -> None:
    from app.services.pii_detector import scan_dict
    data = {"customer": {"email": "a@b.de", "iban": "DE89370400440532013000"}}
    matches = scan_dict(data)
    assert len(matches) >= 1


@pytest.mark.unit
def test_scan_dict_no_pii() -> None:
    from app.services.pii_detector import scan_dict
    data = {"article": "Weizen", "price": 200, "unit": "EUR/t"}
    matches = scan_dict(data)
    assert len(matches) == 0


# ---------------------------------------------------------------------------
# workflow_guards  (pure predicate functions — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_guard_total_positive_ok() -> None:
    from app.services.workflow_guards import guard_total_positive
    ok, msg = guard_total_positive({"total": 150.0})
    assert ok is True


@pytest.mark.unit
def test_guard_total_positive_zero_fails() -> None:
    from app.services.workflow_guards import guard_total_positive
    ok, msg = guard_total_positive({"total": 0.0})
    assert ok is False
    assert len(msg) > 0


@pytest.mark.unit
def test_guard_total_positive_negative_fails() -> None:
    from app.services.workflow_guards import guard_total_positive
    ok, _ = guard_total_positive({"total": -50.0})
    assert ok is False


@pytest.mark.unit
def test_guard_has_approval_role_with_controller_role() -> None:
    from app.services.workflow_guards import guard_has_approval_role
    ok, msg = guard_has_approval_role({"user_info": {"roles": ["controller"]}})
    assert ok is True


@pytest.mark.unit
def test_guard_has_approval_role_admin() -> None:
    from app.services.workflow_guards import guard_has_approval_role
    ok, _ = guard_has_approval_role({"user_info": {"roles": ["admin"]}})
    assert ok is True


@pytest.mark.unit
def test_guard_has_approval_role_wrong_role() -> None:
    from app.services.workflow_guards import guard_has_approval_role
    ok, msg = guard_has_approval_role({"user_info": {"roles": ["viewer"]}})
    assert ok is False
    assert len(msg) > 0


@pytest.mark.unit
def test_guard_has_submit_role_with_sales() -> None:
    from app.services.workflow_guards import guard_has_submit_role
    ok, _ = guard_has_submit_role({"user_info": {"roles": ["sales"]}})
    assert ok is True


@pytest.mark.unit
def test_guard_price_not_below_cost_ok() -> None:
    from app.services.workflow_guards import guard_price_not_below_cost
    ok, _ = guard_price_not_below_cost({"lines": [{"price": 200.0, "cost": 150.0, "article": "ART-1"}]})
    assert ok is True


@pytest.mark.unit
def test_guard_price_not_below_cost_fail() -> None:
    from app.services.workflow_guards import guard_price_not_below_cost
    ok, msg = guard_price_not_below_cost({"lines": [{"price": 100.0, "cost": 150.0, "article": "ART-1"}]})
    assert ok is False
    assert len(msg) > 0


@pytest.mark.unit
def test_guard_price_not_below_cost_no_lines() -> None:
    from app.services.workflow_guards import guard_price_not_below_cost
    ok, _ = guard_price_not_below_cost({})
    assert ok is True


@pytest.mark.unit
def test_guard_psm_expertise_required_with_cert() -> None:
    from app.services.workflow_guards import guard_psm_expertise_required
    ok, _ = guard_psm_expertise_required({"psm_expertise_cert": "valid-cert-id"})
    assert ok is True
