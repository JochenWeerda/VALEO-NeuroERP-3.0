"""
Wave-13 Contract Tests:
- AP1: DeductionInput validation contracts
- AP2: compute_contract_status all state transitions
- AP3: TaxKeyCreate validators
- AP4: compliance_exports (hazard rows + nutrient stream)
- AP5: DunningRun execution model
- AP6: DunningRun escalation and fee tracking
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.core.agrar_settlement_models import DeductionInput
from app.core.agrar_contract_status import compute_contract_status
from app.core.tax_key_models import TaxKeyCreate
from app.core.compliance_exports import extract_hazard_export_rows, compute_nutrient_stream
from app.core.dunning_model import MahnwesenItem
from app.core.dunning_run import DunningRunResult, execute_dunning_run


# ---------------------------------------------------------------------------
# AP1: DeductionInput Validation
# ---------------------------------------------------------------------------

def test_deduction_input_per_ton_requires_rate():
    with pytest.raises(Exception):
        DeductionInput(deduction_type="drying", mode="per_ton")  # missing rate


def test_deduction_input_fixed_requires_fixed_amount():
    with pytest.raises(Exception):
        DeductionInput(deduction_type="cleaning", mode="fixed")  # missing fixed_amount


def test_deduction_input_per_ton_valid():
    d = DeductionInput(deduction_type="drying", mode="per_ton", rate_per_ton_eur=3.5)
    assert d.rate_per_ton_eur == 3.5
    assert d.fixed_amount_eur is None


def test_deduction_input_fixed_valid():
    d = DeductionInput(deduction_type="freight", mode="fixed", fixed_amount_eur=50.0)
    assert d.fixed_amount_eur == 50.0
    assert d.rate_per_ton_eur is None


def test_deduction_input_all_types_accepted():
    for dtype in ("drying", "cleaning", "freight", "other"):
        d = DeductionInput(deduction_type=dtype, mode="fixed", fixed_amount_eur=10.0)
        assert d.deduction_type == dtype


# ---------------------------------------------------------------------------
# AP2: compute_contract_status transitions
# ---------------------------------------------------------------------------

def test_contract_status_fulfilled_when_remaining_zero():
    status = compute_contract_status(Decimal("100"), Decimal("0"), "open")
    assert status == "fulfilled"


def test_contract_status_partially_allocated():
    status = compute_contract_status(Decimal("100"), Decimal("40"), "open")
    assert status == "partially_allocated"


def test_contract_status_open_when_nothing_allocated():
    status = compute_contract_status(Decimal("100"), Decimal("100"), "open")
    assert status == "open"


def test_contract_status_cancelled_overrides_all():
    status = compute_contract_status(Decimal("100"), Decimal("0"), "cancelled")
    assert status == "cancelled"


def test_contract_status_partially_allocated_overrides_near_zero():
    status = compute_contract_status(Decimal("100"), Decimal("0.01"), "open")
    assert status == "partially_allocated"


# ---------------------------------------------------------------------------
# AP3: TaxKeyCreate validators
# ---------------------------------------------------------------------------

def test_tax_key_create_valid_minimal():
    tk = TaxKeyCreate(
        code="19",
        bezeichnung="Regelsteuersatz",
        steuersatz=Decimal("19"),
        ustva_position="9b",
        ustva_bezeichnung="Steuerpflichtige Umsätze 19%",
        gueltig_von=date(2007, 1, 1),
    )
    assert tk.code == "19"
    assert tk.country == "DE"


def test_tax_key_create_rejects_non_digit_code():
    with pytest.raises(Exception):
        TaxKeyCreate(
            code="AB",
            bezeichnung="Fehler",
            steuersatz=Decimal("7"),
            ustva_position="9a",
            ustva_bezeichnung="Test",
            gueltig_von=date(2007, 1, 1),
        )


def test_tax_key_create_reverse_charge_requires_zero_rate():
    with pytest.raises(Exception):
        TaxKeyCreate(
            code="0",
            bezeichnung="Reverse Charge",
            steuersatz=Decimal("19"),
            ustva_position="9b",
            ustva_bezeichnung="Reverse",
            gueltig_von=date(2007, 1, 1),
            reverse_charge=True,
        )


def test_tax_key_create_valid_reverse_charge_with_zero_rate():
    tk = TaxKeyCreate(
        code="0",
        bezeichnung="Reverse Charge",
        steuersatz=Decimal("0"),
        ustva_position="9b",
        ustva_bezeichnung="Reverse",
        gueltig_von=date(2007, 1, 1),
        reverse_charge=True,
    )
    assert tk.reverse_charge is True


def test_tax_key_create_rejects_invalid_date_range():
    with pytest.raises(Exception):
        TaxKeyCreate(
            code="7",
            bezeichnung="Ermäßigt",
            steuersatz=Decimal("7"),
            ustva_position="9a",
            ustva_bezeichnung="Test",
            gueltig_von=date(2026, 1, 1),
            gueltig_bis=date(2025, 12, 31),
        )


# ---------------------------------------------------------------------------
# AP4: compliance_exports contracts
# ---------------------------------------------------------------------------

def _make_delivery(number: str, date_str: str, n_kg: float = 0.0, p2o5_kg: float = 0.0,
                   has_psm: bool = False) -> dict:
    line = {"article": "PSM-A"}
    if has_psm:
        line["bvlZulassungsnummer"] = "B-12345"
        line["hazardHinweise"] = "H301"
    return {
        "number": number,
        "date": date_str,
        "supplierName": "Lieferant GmbH",
        "customerId": "CUST-1",
        "psmCompliance": {"sachkundeStatus": "ok", "compliant": True},
        "adrPunkte": 200,
        "lines": [line],
        "totalNutrientNKg": n_kg,
        "totalNutrientP2o5Kg": p2o5_kg,
    }


def test_extract_hazard_export_rows_filters_non_psm_lines():
    deliveries = [_make_delivery("D1", "2026-01-10", has_psm=False)]
    rows = extract_hazard_export_rows(deliveries)
    assert rows == []


def test_extract_hazard_export_rows_includes_psm_lines():
    deliveries = [_make_delivery("D2", "2026-02-05", has_psm=True)]
    rows = extract_hazard_export_rows(deliveries)
    assert len(rows) == 1
    assert rows[0]["deliveryNumber"] == "D2"
    assert rows[0]["bvlZulassungsnummer"] == "B-12345"


def test_extract_hazard_export_rows_filters_by_year():
    deliveries = [
        _make_delivery("D3", "2025-06-01", has_psm=True),
        _make_delivery("D4", "2026-03-01", has_psm=True),
    ]
    rows = extract_hazard_export_rows(deliveries, year=2026)
    assert len(rows) == 1
    assert rows[0]["deliveryNumber"] == "D4"


def test_compute_nutrient_stream_aggregates_by_month():
    deliveries = [
        _make_delivery("D5", "2026-01-10", n_kg=100.0, p2o5_kg=40.0),
        _make_delivery("D6", "2026-01-20", n_kg=50.0, p2o5_kg=20.0),
        _make_delivery("D7", "2026-02-05", n_kg=80.0, p2o5_kg=30.0),
    ]
    result = compute_nutrient_stream(deliveries, year=2026)
    assert result["deliveryCount"] == 3
    assert result["totalNutrientNKg"] == pytest.approx(230.0)
    assert "2026-01" in result["byMonth"]
    assert result["byMonth"]["2026-01"]["deliveries"] == 2


def test_compute_nutrient_stream_ignores_other_years():
    deliveries = [
        _make_delivery("D8", "2025-12-31", n_kg=500.0),
        _make_delivery("D9", "2026-01-01", n_kg=100.0),
    ]
    result = compute_nutrient_stream(deliveries, year=2026)
    assert result["deliveryCount"] == 1
    assert result["totalNutrientNKg"] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# AP5: DunningRun execution model
# ---------------------------------------------------------------------------

def _make_item(item_id: str, due_date: date, open_amount: float = 200.0,
               current_level: int = 0, blocked: bool = False) -> MahnwesenItem:
    return MahnwesenItem(
        item_id=item_id,
        tenant_id="t1",
        debtor_id=f"deb-{item_id}",
        invoice_id=f"INV-{item_id}",
        invoice_date=date(2026, 1, 1),
        due_date=due_date,
        open_amount=open_amount,
        current_dunning_level=current_level,
        blocked=blocked,
        block_reason="Dispute" if blocked else None,
    )


def test_execute_dunning_run_produces_completed_result():
    items = [_make_item("i1", date(2026, 1, 10))]
    result = execute_dunning_run("t1", items, reference_date=date(2026, 3, 13))
    assert result.status == "completed"
    assert result.schema_version == 1
    assert result.tenant_id == "t1"
    assert result.processed_count == 1


def test_execute_dunning_run_counts_blocked_items():
    items = [
        _make_item("i2", date(2026, 1, 5), blocked=True),
        _make_item("i3", date(2026, 1, 10)),
    ]
    result = execute_dunning_run("t1", items, reference_date=date(2026, 3, 13))
    assert result.blocked_count == 1


def test_execute_dunning_run_does_not_escalate_level2():
    items = [_make_item("i4", date(2026, 2, 20))]  # 21 days overdue → level 2
    result = execute_dunning_run("t1", items, reference_date=date(2026, 3, 13))
    assert result.escalated_count == 0


# ---------------------------------------------------------------------------
# AP6: DunningRun fees and level escalation
# ---------------------------------------------------------------------------

def test_execute_dunning_run_escalates_legal_items():
    items = [_make_item("i5", date(2026, 1, 10))]  # 62 days overdue → level 4 (legal)
    result = execute_dunning_run("t1", items, reference_date=date(2026, 3, 13))
    assert result.escalated_count == 1
    legal_item = next(i for i in result.items if i.item_id == "i5")
    assert legal_item.new_dunning_level == 4
    assert legal_item.action_required == "legal"


def test_execute_dunning_run_accumulates_fees():
    items = [
        _make_item("i6", date(2026, 1, 10)),   # 62 days → level 4, fee=50
        _make_item("i7", date(2026, 2, 20)),   # 21 days → level 2, fee=5
    ]
    result = execute_dunning_run("t1", items, reference_date=date(2026, 3, 13))
    assert result.total_fees > 0


def test_execute_dunning_run_blocked_items_unchanged():
    item = _make_item("i8", date(2026, 1, 1), current_level=2, blocked=True)
    result = execute_dunning_run("t1", [item], reference_date=date(2026, 3, 13))
    run_item = result.items[0]
    assert run_item.level_changed is False
    assert run_item.new_dunning_level == 2


def test_dunning_run_result_schema_version():
    result = execute_dunning_run("t1", [], reference_date=date(2026, 3, 13))
    assert result.schema_version == 1
    assert result.processed_count == 0
    assert result.status == "completed"
