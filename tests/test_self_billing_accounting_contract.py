"""Self-billing uses multi-param taxes, posted AP path, and does not commit halfway."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

from app.core.exceptions import ValidationFailedError
from app.services.harvest_acceptance_service import HarvestAcceptanceService
from modules.agrar.services.tax_profile_service import (
    TRANSACTION_TYPE_SELF_BILLING,
    get_taxation_type_for_supplier,
    require_self_billing_agreement,
    resolve_self_billing_tax_code,
)


@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield


def invoice(**kwargs):
    base = dict(
        id="sb_1",
        invoice_number="GS-test",
        vat_rate_percent=Decimal("7"),
        total_net_amount_eur=Decimal("100"),
        total_vat_amount_eur=Decimal("7"),
        total_gross_amount_eur=Decimal("107"),
        harvest_acceptance_id="ha-1",
        journal_entry_id=None,
        docflow_header_id=None,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_require_profile_hard_422_without_fallback():
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    with pytest.raises(ValidationFailedError, match="Steuerprofil"):
        get_taxation_type_for_supplier(db, "sup-1", "own", date(2026, 3, 1), require_profile=True)


def test_draft_allows_missing_profile_fallback_regular():
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    assert get_taxation_type_for_supplier(db, "sup-1", "own", date(2026, 3, 1), require_profile=False) == "regular"


def test_agreement_required():
    db = MagicMock()
    db.execute.return_value.first.return_value = (False,)
    with pytest.raises(ValidationFailedError, match="Selbstfakturierungsvereinbarung"):
        require_self_billing_agreement(db, "own", "sup-1")


def test_resolve_regular_ignores_zero_rate_keys():
    """Regular darf den Nullsatz-Schlüssel nicht greifen (sonst vat_rate_percent=0)."""
    db = MagicMock()
    db.execute.side_effect = [
        MagicMock(fetchall=MagicMock(return_value=[])),
        MagicMock(
            mappings=MagicMock(
                return_value=MagicMock(
                    all=MagicMock(
                        return_value=[
                            {
                                "code": "0",
                                "steuersatz": Decimal("0"),
                                "debit_account": None,
                                "expense_account": "3300",
                                "par_24_ustg": False,
                                "reverse_charge": False,
                            },
                            {
                                "code": "8",
                                "steuersatz": Decimal("7"),
                                "debit_account": "1571",
                                "expense_account": "3300",
                                "par_24_ustg": False,
                                "reverse_charge": False,
                            },
                        ]
                    )
                )
            )
        ),
    ]
    resolved = resolve_self_billing_tax_code(
        db,
        tenant_id="own",
        supplier_id="sup",
        taxation_type="regular",
        article_tax_class=None,
        transaction_type=TRANSACTION_TYPE_SELF_BILLING,
        delivery_date=date(2026, 6, 1),
    )
    assert resolved["tax_code"] == "8"
    assert resolved["rate"] == Decimal("7")


def test_resolve_ustg24_only_p24_keys():
    db = MagicMock()
    db.execute.side_effect = [
        MagicMock(fetchall=MagicMock(return_value=[])),  # properties
        MagicMock(
            mappings=MagicMock(
                return_value=MagicMock(
                    all=MagicMock(
                        return_value=[
                            {
                                "code": "8",
                                "steuersatz": Decimal("7"),
                                "debit_account": "1571",
                                "expense_account": "3300",
                                "par_24_ustg": False,
                                "reverse_charge": False,
                            },
                            {
                                "code": "24",
                                "steuersatz": Decimal("10.7"),
                                "debit_account": "1571",
                                "expense_account": "3300",
                                "par_24_ustg": True,
                                "reverse_charge": False,
                            },
                        ]
                    )
                )
            )
        ),
    ]
    resolved = resolve_self_billing_tax_code(
        db,
        tenant_id="own",
        supplier_id="sup",
        taxation_type="ustg24_flat_rate",
        article_tax_class=None,
        transaction_type=TRANSACTION_TYPE_SELF_BILLING,
        delivery_date=date(2026, 6, 1),
    )
    assert resolved["tax_code"] == "24"
    assert resolved["par_24_ustg"] is True


def test_no_tax_assignment_blocks_without_commit(monkeypatch):
    db = MagicMock()
    svc = HarvestAcceptanceService(db, "own")

    def boom(*a, **k):
        raise ValidationFailedError("Lieferanten-Steuerprofil fehlt")

    monkeypatch.setattr(
        "modules.agrar.services.tax_profile_service.get_taxation_type_for_supplier", boom
    )
    with pytest.raises(ValidationFailedError):
        svc._book_self_billing_credit_note(invoice(), date(2026, 3, 1), supplier_id="sup")
    db.commit.assert_not_called()


def test_canonical_booking_uses_buche_eingangsrechnung(monkeypatch):
    from app.finance import steuerschluessel as taxes
    from app.services import self_billing_buchung as core

    db = MagicMock()
    db.execute.return_value.scalar.return_value = None
    resolved = {
        "tax_code": "8",
        "rate": Decimal("7"),
        "expense_account": "3300",
        "vorsteuerkonto": "1571",
        "par_24_ustg": False,
        "taxation_type": "regular",
        "supplier_id": "sup",
        "article_tax_class": None,
        "delivery_date": "2026-03-01",
    }
    monkeypatch.setattr(
        "modules.agrar.services.tax_profile_service.get_taxation_type_for_supplier",
        lambda *a, **k: "regular",
    )
    monkeypatch.setattr(
        "modules.agrar.services.tax_profile_service.resolve_self_billing_tax_code",
        lambda *a, **k: resolved,
    )
    monkeypatch.setattr(
        "app.services.self_billing_docflow.lege_self_billing_beleg_an",
        lambda *a, **k: "doc-1",
    )
    monkeypatch.setattr(
        "app.services.self_billing_docflow.verknuepfe_erweiterung",
        lambda *a, **k: None,
    )
    group = taxes.Vorsteuergruppe(
        tax_code="8",
        satz=Decimal("7"),
        netto=Decimal("100"),
        steuer=Decimal("7"),
        aufwandskonto="3300",
        vorsteuerkonto="1571",
    )
    booked = MagicMock(return_value=("j-1", [group]))
    monkeypatch.setattr(core, "buche_self_billing", booked)

    HarvestAcceptanceService(db, "own")._book_self_billing_credit_note(
        invoice(), date(2026, 3, 1), supplier_id="sup", posted_by="u1"
    )
    booked.assert_called_once()
    assert booked.call_args.kwargs["supplier_id"] == "sup"
    assert booked.call_args.kwargs["gruppen"][0].tax_code == "8"
    db.commit.assert_not_called()


def test_invoice_repository_can_join_outer_transaction(monkeypatch):
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl

    db = MagicMock()
    repo = SelfBillingRepositoryImpl(db, commit_on_success=False)
    data = invoice()
    model = MagicMock()
    monkeypatch.setattr(repo, "_from_service_invoice", lambda _: model)
    monkeypatch.setattr(repo, "_to_service_invoice", lambda _: data)
    assert repo.create_invoice(data) is data
    db.flush.assert_called_once()
    db.commit.assert_not_called()


def test_buche_self_billing_rejects_amount_mismatch(monkeypatch):
    from app.finance.steuerschluessel import Vorsteuergruppe
    from app.services.self_billing_buchung import buche_self_billing

    db = MagicMock()
    db.execute.return_value.scalar.return_value = None
    groups = [
        Vorsteuergruppe(
            tax_code="8",
            satz=Decimal("7"),
            netto=Decimal("100"),
            steuer=Decimal("7"),
            aufwandskonto="3300",
            vorsteuerkonto="1571",
        )
    ]
    bad = invoice(total_vat_amount_eur=Decimal("8"), total_gross_amount_eur=Decimal("108"))
    with pytest.raises(ValidationFailedError, match="widersprechen"):
        buche_self_billing(
            db,
            "own",
            invoice=bad,
            supplier_id="sup",
            delivery_date=date(2026, 3, 1),
            tax_context={"taxation_type": "regular"},
            gruppen=groups,
            posted_by="u",
            harvest_acceptance_id="ha-1",
        )


def test_buche_self_billing_idempotent_conflict(monkeypatch):
    from app.core.exceptions import ConflictError
    from app.finance.steuerschluessel import Vorsteuergruppe
    from app.services.self_billing_buchung import buche_self_billing

    db = MagicMock()
    inv = invoice(journal_entry_id="j-existing")
    groups = [
        Vorsteuergruppe(
            tax_code="8",
            satz=Decimal("7"),
            netto=Decimal("100"),
            steuer=Decimal("7"),
            aufwandskonto="3300",
            vorsteuerkonto="1571",
        )
    ]
    with pytest.raises(ConflictError):
        buche_self_billing(
            db,
            "own",
            invoice=inv,
            supplier_id="sup",
            delivery_date=date(2026, 3, 1),
            tax_context={"taxation_type": "regular"},
            gruppen=groups,
            posted_by="u",
        )


def test_vorsteuergruppe_uses_half_up_like_harvest_calculator():
    """5417.50 × 7 % → 379.23 (HALF_UP), nicht 379.22 (Banker's)."""
    from app.services.self_billing_buchung import build_vorsteuergruppen_from_resolved

    groups = build_vorsteuergruppen_from_resolved(
        {
            "rate": Decimal("7"),
            "tax_code": "8",
            "expense_account": "3300",
            "vorsteuerkonto": "1571",
        },
        netto=Decimal("5417.50"),
    )
    assert groups[0].steuer == Decimal("379.23")
    assert groups[0].netto == Decimal("5417.50")
