"""No guessed free allowance and no loss of explicitly measured zero values."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import ValidationFailedError
from app.infrastructure.models import AgrarContract, Article, HarvestAcceptancePosition, WeighingTicket
from app.services.harvest_acceptance_service import HarvestAcceptanceService
from modules.agrar.services import harvest_calculator as calculator
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionRuleV1


def rule(**changes):
    return HarvestDeductionRuleV1(**dict({
        "rule_id": "synthetic", "rule_version": 1, "tenant_id": "own", "contract_id": None,
        "customer_id": "customer", "article_id": "article",
        "valid_from": date(2026, 1, 1), "valid_until": date(2026, 12, 31),
        "source_reference": "synthetic test terms", "measurement_method": "synthetic-lab",
        "measurement_method_version": "1", "impurities_free_pct": Decimal("0"),
    }, **changes))


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """These isolated domain/service tests do not initialize compatibility auth."""
    yield


@pytest.mark.parametrize("impurities", [None, Decimal("0"), Decimal("1.5")])
def test_missing_allowance_never_becomes_a_two_percent_default(impurities):
    inp = calculator.HarvestCalculationInput(
        delivered_quantity_kg=Decimal("25000"), impurities_pct=impurities,
    )
    with pytest.raises(calculator.MissingHarvestContractRuleError, match="Abrechnungsgrundlage fehlt"):
        calculator.calculate_harvest_settlement(inp, vat_rate_percent=Decimal("0"))


@pytest.mark.parametrize("allowance,net", [("0", "24625"), ("2", "25000"), ("3", "25000")])
def test_explicit_allowance_and_informative_wind_preserve_the_domain_formula(allowance, net):
    result = calculator.calculate_harvest_settlement(calculator.HarvestCalculationInput(
        delivered_quantity_kg=Decimal("25000"), impurities_pct=Decimal("1.5"),
        windage_pct=Decimal("0.8"), impurities_free_pct=Decimal(allowance),
        unit_price_eur_per_ton=Decimal("220"),
    ), vat_rate_percent=Decimal("0"))
    positions = {p.position_number: p for p in result.positions}
    assert positions[65].quantity_kg == Decimal(net)
    assert positions[15].quantity_kg == Decimal("200")
    assert positions[20].description == f"Besatz {allowance}% frei"


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "-0.01", "100.01"])
def test_invalid_allowance_is_rejected_before_calculation(value):
    with pytest.raises(ValueError, match="Besatzfreigrenze"):
        calculator.calculate_harvest_settlement(calculator.HarvestCalculationInput(
            delivered_quantity_kg=Decimal("25000"), impurities_free_pct=Decimal(value),
        ))


@pytest.mark.parametrize("contract_price", [None, Decimal("0")])
@pytest.mark.parametrize("resolved", [False, True])
def test_operational_calculation_does_not_persist_guessed_terms_and_preserves_zero(monkeypatch, contract_price, resolved):
    db = MagicMock()
    service = HarvestAcceptanceService(db, "own")
    obj = SimpleNamespace(
        id="acceptance", release_status="draft", invoice_id=None, tenant_id="own",
        customer_id="customer", article_id="article", warehouse_id=None,
        weighing_ticket_id="ticket", contract_id="contract" if contract_price is not None else None,
        delivery_date=date(2026, 10, 15),
        total_net_amount_eur=Decimal("123"), total_gross_amount_eur=Decimal("123"),
    )
    service._get_or_raise = lambda _, **kwargs: obj
    service._validate_references = lambda _: None
    ticket = SimpleNamespace(net_weight=Decimal("25000"), moisture_pct=Decimal("14"),
                             impurities_pct=Decimal("3"), hl_weight=Decimal("76"))
    article = SimpleNamespace(warengruppe=None, sales_price=Decimal("220"), mehrwertsteuer_prozent=0)
    positions = [SimpleNamespace(position_number=number, lab_value_pct=Decimal("0"),
                                 quantity_kg=Decimal("0"), amount_eur=Decimal("0"))
                 for number in [15, 20, 40, 60, 63, 75, 78, 80]]
    queries = {model: MagicMock() for model in [WeighingTicket, Article, HarvestAcceptancePosition, AgrarContract]}
    for query in queries.values():
        query.filter.return_value = query
    queries[WeighingTicket].first.return_value = ticket
    queries[Article].first.return_value = article
    queries[HarvestAcceptancePosition].all.return_value = positions
    queries[AgrarContract].first.return_value = SimpleNamespace(pricing_model="fixed", fixed_price=contract_price)
    db.query.side_effect = lambda model: queries[model]
    if resolved:
        service._rule_resolver = lambda **kwargs: rule(contract_id=obj.contract_id)
    actual = calculator.calculate_harvest_settlement
    captured = []

    def observe(inp, **kwargs):
        captured.append(inp)
        return actual(inp, **kwargs)

    monkeypatch.setattr(calculator, "calculate_harvest_settlement", observe)
    if resolved:
        result = service.calculate_settlement("acceptance")
        assert result["total_net_amount_eur"] == (0 if contract_price is not None else 5500)
        impurity = next(p for p in result["positions"] if p["position_number"] == 20)
        assert impurity["quantity_kg"] == impurity["quantity_pct"] == 0
        assert impurity["description"] == "Besatz 0% frei"
        assert rule(contract_id=obj.contract_id).content_hash in impurity["calculation_formula"]
        assert positions[1].description == "Besatz 0% frei"
        db.commit.assert_called_once()
    else:
        with pytest.raises(ValidationFailedError, match="Abrechnungsgrundlage fehlt"):
            service.calculate_settlement("acceptance")
        assert not captured
        assert obj.total_net_amount_eur == Decimal("123")
        db.query.assert_not_called()
        db.add.assert_not_called()
        db.flush.assert_not_called()
        db.commit.assert_not_called()
        return
    inp, = captured
    assert inp.impurities_free_pct == (Decimal("0") if resolved else None)
    assert inp.unit_price_eur_per_ton == (Decimal("220") if contract_price is None else Decimal("0"))
    for field in ["impurities_pct", "moisture_pct", "windage_pct", "hl_weight_kg_per_hl",
                  "storage_shrinkage_pct", "storage_fee_per_month", "freight_costs", "weighing_fees"]:
        assert getattr(inp, field) == Decimal("0"), field
    if not resolved:
        assert obj.total_net_amount_eur == Decimal("123")
        db.add.assert_not_called()
        db.flush.assert_not_called()
        db.commit.assert_not_called()


@pytest.mark.parametrize("change", [
    {"tenant_id": "foreign"}, {"contract_id": "other"}, {"customer_id": "other"},
    {"article_id": "other"}, {"valid_from": date(2026, 10, 16)},
    {"valid_until": date(2026, 10, 14)},
])
def test_rule_scope_mismatch_is_rejected_before_any_calculation_or_mutation(change):
    db = MagicMock()
    service = HarvestAcceptanceService(db, "own", rule_resolver=lambda **kwargs: rule(**change))
    service._get_or_raise = lambda _, **kwargs: SimpleNamespace(
        release_status="draft", invoice_id=None, customer_id="customer", article_id="article",
        warehouse_id=None, weighing_ticket_id=None, contract_id=None, delivery_date=date(2026, 10, 15),
    )
    service._validate_references = lambda _: None
    with pytest.raises(ValidationFailedError, match="Vertragsregel"):
        service.calculate_settlement("acceptance")
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_rule_is_immutable_and_hash_binds_the_actual_terms():
    original = rule()
    assert original.content_hash == rule().content_hash
    assert original.content_hash != rule(impurities_free_pct=Decimal("2")).content_hash
    assert original.content_hash != rule(measurement_method_version="2").content_hash
    assert original.content_hash == rule(impurities_free_pct=Decimal("-0.000")).content_hash
    assert rule(impurities_free_pct=Decimal("2")).content_hash == rule(impurities_free_pct=Decimal("2.00")).content_hash
    precise = Decimal("1.123456789012345678901234567890123456789")
    assert rule(impurities_free_pct=precise).impurities_free_pct == precise
    with pytest.raises(ValueError):
        original.impurities_free_pct = Decimal("2")


@pytest.mark.parametrize("change", [{"rule_version": True}, {"windage_mode": "extra_deduction"},
    {"valid_until": date(2025, 1, 1)}, {"impurities_free_pct": Decimal("NaN")},
    {"quality_limit_pct": Decimal("Infinity")}, {"sql": "arbitrary"}])
def test_unsupported_or_malformed_rule_cannot_enter_the_domain(change):
    with pytest.raises(ValueError):
        rule(**change)


@pytest.mark.parametrize("bad", [
    {"impurities_free_pct": 0},
    rule().model_copy(update={"impurities_free_pct": Decimal("NaN")}),
])
def test_resolver_cannot_bypass_typed_validation_with_unvalidated_data(bad):
    db = MagicMock()
    service = HarvestAcceptanceService(db, "own", rule_resolver=lambda **kwargs: bad)
    service._get_or_raise = lambda _, **kwargs: SimpleNamespace(
        release_status="draft", invoice_id=None, customer_id="customer", article_id="article",
        warehouse_id=None, weighing_ticket_id=None, contract_id=None, delivery_date=date(2026, 10, 15),
    )
    service._validate_references = lambda _: None
    with pytest.raises(ValidationFailedError, match="Vertragsregel"):
        service.calculate_settlement("acceptance")
    db.query.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("resolver", [None, lambda **kwargs: rule(tenant_id="foreign")])
def test_old_totals_cannot_bypass_the_rule_gate_through_financial_release(resolver):
    db = MagicMock()
    service = HarvestAcceptanceService(db, "own", rule_resolver=resolver)
    obj = SimpleNamespace(
        release_status="draft", invoice_id=None, customer_id="customer", article_id="article",
        warehouse_id="warehouse", weighing_ticket_id="ticket", contract_id=None,
        delivery_date=date(2026, 10, 15), total_net_amount_eur=Decimal("123"),
    )
    service._get_or_raise = lambda _, **kwargs: obj
    service._validate_references = lambda _: None
    with pytest.raises(ValidationFailedError):
        service.release_acceptance("acceptance", "final", True, True, "verified-actor")
    assert obj.release_status == "draft" and obj.total_net_amount_eur == Decimal("123")
    db.query.assert_not_called()
    db.add.assert_not_called()
    db.flush.assert_not_called()
    db.commit.assert_not_called()


def test_nonfinancial_receipt_does_not_depend_on_a_monetary_rule():
    db = MagicMock()
    service = HarvestAcceptanceService(db, "own")
    obj = SimpleNamespace(
        release_status="draft", invoice_id=None, customer_id="customer", article_id="article",
        warehouse_id="warehouse", weighing_ticket_id="ticket", contract_id=None,
        delivery_date=date(2026, 10, 15), total_net_amount_eur=Decimal("123"),
        stock_movement_id=None,
    )
    service._get_or_raise = lambda _, **kwargs: obj
    service._validate_references = lambda _: None
    db.query.return_value.filter.return_value.first.return_value = SimpleNamespace(net_weight=Decimal("25000"))
    # Observe the actual service's transition; presentation is outside this test.
    import app.services.harvest_acceptance_service as module
    from unittest.mock import patch
    with patch.object(module, "_to_dict_with_positions", return_value={"release_status": "final"}):
        result = service.release_acceptance("acceptance", "final", False, False, "verified-actor")
    assert result["release_status"] == "final" and obj.release_status == "final"
    assert obj.invoice_id is None
    db.commit.assert_called_once()
