"""Wave 97 — Unit-Tests fuer workflow_guards, pii_detector, sales_credit_service,
contract_fixing_service, kaeufergruppe, case_management (pure domain functions)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# workflow_guards — guard_* functions  (pure payload checks)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_guard_has_approval_role_controller_passes() -> None:
    from app.services.workflow_guards import guard_has_approval_role
    ok, _ = guard_has_approval_role({"user_info": {"roles": ["controller"]}})
    assert ok is True


@pytest.mark.unit
def test_guard_has_approval_role_admin_passes() -> None:
    from app.services.workflow_guards import guard_has_approval_role
    ok, _ = guard_has_approval_role({"user_info": {"roles": ["admin"]}})
    assert ok is True


@pytest.mark.unit
def test_guard_has_approval_role_viewer_fails() -> None:
    from app.services.workflow_guards import guard_has_approval_role
    ok, reason = guard_has_approval_role({"user_info": {"roles": ["viewer"]}})
    assert ok is False
    assert len(reason) > 0


@pytest.mark.unit
def test_guard_total_positive_passes() -> None:
    from app.services.workflow_guards import guard_total_positive
    ok, _ = guard_total_positive({"total": 100})
    assert ok is True


@pytest.mark.unit
def test_guard_total_positive_zero_fails() -> None:
    from app.services.workflow_guards import guard_total_positive
    ok, _ = guard_total_positive({"total": 0})
    assert ok is False


@pytest.mark.unit
def test_guard_price_not_below_cost_ok() -> None:
    from app.services.workflow_guards import guard_price_not_below_cost
    ok, _ = guard_price_not_below_cost({"unit_price": 100, "cost_price": 80})
    assert ok is True


@pytest.mark.unit
def test_guard_psm_approval_valid_true() -> None:
    from app.services.workflow_guards import guard_psm_approval_valid
    ok, _ = guard_psm_approval_valid({"psm_approved": True})
    assert ok is True


@pytest.mark.unit
def test_guard_psm_expertise_required_passes() -> None:
    from app.services.workflow_guards import guard_psm_expertise_required
    ok, _ = guard_psm_expertise_required({"artikel_typ": "psm", "has_expertise": True})
    assert ok is True


# ---------------------------------------------------------------------------
# pii_detector — detect_pii, mask_reversible, mask_irreversible, unmask, scan_dict
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_detect_pii_email() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("max@example.com")
    assert len(matches) > 0
    assert any(m.type == "email" for m in matches)


@pytest.mark.unit
def test_detect_pii_iban() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("DE89 3704 0044 0532 0130 00")
    assert any(m.type == "iban" for m in matches)


@pytest.mark.unit
def test_detect_pii_clean_text_empty() -> None:
    from app.services.pii_detector import detect_pii
    matches = detect_pii("Der Mais hat heute 14 Prozent Feuchte.")
    assert matches == []


@pytest.mark.unit
def test_mask_reversible_replaces_pii() -> None:
    from app.services.pii_detector import mask_reversible
    masked, mapping = mask_reversible("Email: max@example.com")
    assert "max@example.com" not in masked
    assert len(mapping) > 0


@pytest.mark.unit
def test_unmask_restores_original() -> None:
    from app.services.pii_detector import mask_reversible, unmask
    original = "Email: max@example.com"
    masked, mapping = mask_reversible(original)
    restored = unmask(masked, mapping)
    assert restored == original


@pytest.mark.unit
def test_mask_irreversible_replaces_pii() -> None:
    from app.services.pii_detector import mask_irreversible
    result = mask_irreversible("Email: max@example.com")
    assert "max@example.com" not in result
    assert "[EMAIL]" in result


@pytest.mark.unit
def test_scan_dict_finds_email_in_nested() -> None:
    from app.services.pii_detector import scan_dict
    data = {"kontakt": {"email": "max@example.com"}, "ort": "Berlin"}
    matches = scan_dict(data)
    assert len(matches) > 0
    assert any(m.type == "email" for m in matches)


# ---------------------------------------------------------------------------
# sales_credit_service — credit_check  (pure limit check)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_credit_check_ok_returns_ampel_ok() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=10000.0, exposure=4000.0)
    assert result["ampel"] == "ok"
    assert result["verfuegbar"] == pytest.approx(6000.0)


@pytest.mark.unit
def test_credit_check_warn_threshold() -> None:
    from app.services.sales_credit_service import credit_check
    # 85% of limit triggers warn (default warn_pct=80)
    result = credit_check(limit=10000.0, exposure=8500.0)
    assert result["ampel"] in ("warn", "warnung", "blockiert")


@pytest.mark.unit
def test_credit_check_blocked_at_limit() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=10000.0, exposure=10000.0)
    assert result["ampel"] == "blockiert"
    assert result["verfuegbar"] == pytest.approx(0.0)


@pytest.mark.unit
def test_credit_check_has_required_keys() -> None:
    from app.services.sales_credit_service import credit_check
    result = credit_check(limit=5000.0, exposure=1000.0)
    for key in ("ampel", "limit", "exposure", "verfuegbar", "auslastung_pct"):
        assert key in result


# ---------------------------------------------------------------------------
# contract_fixing_service — effektiv_preis, marktwert_offen, restmenge
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_effektiv_preis_adds_premium() -> None:
    from app.services.contract_fixing_service import effektiv_preis
    result = effektiv_preis(200, 5)
    assert result == Decimal("205")


@pytest.mark.unit
def test_marktwert_offen_multiply() -> None:
    from app.services.contract_fixing_service import marktwert_offen
    result = marktwert_offen(Decimal("100"), Decimal("205"))
    assert result == Decimal("20500.00")


@pytest.mark.unit
def test_restmenge_subtract() -> None:
    from app.services.contract_fixing_service import restmenge
    result = restmenge(Decimal("1000"), Decimal("400"))
    assert result == Decimal("600")


# ---------------------------------------------------------------------------
# kaeufergruppe — klassifiziere, profil, bewerte_luecke, grenzaufwand_faktor, ziel_anteil
# ---------------------------------------------------------------------------

def _make_signale(**kwargs):
    from app.services.kaeufer_signal_service import Verhaltenssignale
    defaults = dict(kauffrequenz_12m=3, bedarf_gesamt_eur=30000.0, abschlussquote=0.5, deckung_gesamt_pct=0.5)
    defaults.update(kwargs)
    return Verhaltenssignale(**defaults)


@pytest.mark.unit
def test_kaeufergruppe_klassifiziere_returns_klassifikation() -> None:
    from app.services.kaeufergruppe import klassifiziere
    result = klassifiziere(_make_signale())
    assert result is not None
    assert hasattr(result, "gruppe")
    assert hasattr(result, "confidence")


@pytest.mark.unit
def test_kaeufergruppe_klassifiziere_confidence_in_range() -> None:
    from app.services.kaeufergruppe import klassifiziere
    result = klassifiziere(_make_signale())
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.unit
def test_kaeufergruppe_profil_returns_profil() -> None:
    from app.services.kaeufergruppe import profil, BuyingGroup
    p = profil(BuyingGroup.PREISABFRAGER)
    assert p is not None
    assert hasattr(p, "label")
    assert hasattr(p, "grenzaufwand")


@pytest.mark.unit
def test_kaeufergruppe_bewerte_luecke_positive_luecke() -> None:
    from app.services.kaeufergruppe import bewerte_luecke, BuyingGroup
    result = bewerte_luecke(100000, 40000, BuyingGroup.LEISTUNGSKAEUFER, "duenger")
    assert result is not None
    assert hasattr(result, "bedarf_eur")
    assert result.bedarf_eur == 100000


@pytest.mark.unit
def test_kaeufergruppe_grenzaufwand_faktor_positive() -> None:
    from app.services.kaeufergruppe import grenzaufwand_faktor, BuyingGroup
    result = grenzaufwand_faktor(BuyingGroup.PREISABFRAGER, 0.8)
    assert result > 0.0


@pytest.mark.unit
def test_kaeufergruppe_ziel_anteil_between_zero_and_one() -> None:
    from app.services.kaeufergruppe import ziel_anteil, BuyingGroup
    result = ziel_anteil(BuyingGroup.BEZIEHUNGSKAEUFER)
    assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# case_management — in-memory approval workflow
# ---------------------------------------------------------------------------

def _make_requirement():
    from app.core.human_approval_gate import ApprovalRisikostufe, HumanApprovalRequirement
    import inspect
    sig = inspect.signature(HumanApprovalRequirement.__init__)
    params = list(sig.parameters.keys())
    # Build with positional-compatible kwargs
    kwargs = {
        "aktions_typ": "freigabe",
        "risiko_stufe": ApprovalRisikostufe.HOCH,
        "requires_human_approval": True,
        "ausgeloeste_regel_id": "R-WAVE97",
        "begruendung": "Betrag ueberschreitet Schwelle",
        "freigabe_rolle": "controller",
    }
    # ausloser_typ may or may not be required
    if "ausloser_typ" in params:
        from app.core.human_approval_gate import ApprovalAusloserTyp
        vals = list(ApprovalAusloserTyp)
        kwargs["ausloser_typ"] = vals[0]
    return HumanApprovalRequirement(**kwargs)


@pytest.mark.unit
def test_case_management_create_case() -> None:
    from app.services.case_management import create_case
    req = _make_requirement()
    case = create_case(req, instanz_id="INV-WAVE97", agent_id="agent-97", context={"betrag": 15000})
    assert case is not None
    assert case.case_id is not None


@pytest.mark.unit
def test_case_management_get_case() -> None:
    from app.services.case_management import create_case, get_case
    req = _make_requirement()
    case = create_case(req, instanz_id="INV-W97-GET", agent_id="a97", context={})
    fetched = get_case(case.case_id)
    assert fetched is not None
    assert fetched.case_id == case.case_id


@pytest.mark.unit
def test_case_management_get_case_unknown_returns_none() -> None:
    from app.services.case_management import get_case
    result = get_case("nonexistent-case-wave97")
    assert result is None


@pytest.mark.unit
def test_case_management_assign_case() -> None:
    from app.services.case_management import create_case, assign_case
    req = _make_requirement()
    case = create_case(req, instanz_id="INV-W97-ASS", agent_id="a97", context={})
    updated = assign_case(case.case_id, "user-99")
    assert updated is not None
    assert updated.assigned_to == "user-99"


@pytest.mark.unit
def test_case_management_close_case() -> None:
    from app.services.case_management import create_case, close_case
    req = _make_requirement()
    case = create_case(req, instanz_id="INV-W97-CLOSE", agent_id="a97", context={})
    closed = close_case(case.case_id)
    assert closed is not None


@pytest.mark.unit
def test_case_management_dashboard_stats_returns_dict() -> None:
    from app.services.case_management import get_dashboard_stats
    stats = get_dashboard_stats()
    assert isinstance(stats, dict)
    assert len(stats) > 0
