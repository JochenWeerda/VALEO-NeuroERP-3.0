"""Self-billing uses explicit canonical taxes and does not commit halfway."""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
from app.services.harvest_acceptance_service import HarvestAcceptanceService
from app.core.exceptions import ValidationFailedError

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

def invoice():
    return SimpleNamespace(invoice_number="GS-test",vat_rate_percent=Decimal("7"),total_net_amount_eur=Decimal("100"),total_vat_amount_eur=Decimal("7"),total_gross_amount_eur=Decimal("107"))

def test_no_tax_assignment_blocks_without_commit():
    db=MagicMock();db.execute.return_value.scalar.return_value=None
    with pytest.raises(ValidationFailedError):
        HarvestAcceptanceService(db,"own")._book_self_billing_credit_note(invoice(),None)
    db.commit.assert_not_called()

def test_canonical_input_journal_has_correct_direction_and_no_commit(monkeypatch):
    from app.finance import steuerschluessel as taxes
    from app.services import finance_eingangsrechnung_buchung as accounting
    from app.services import finance_transaction_service as transactions
    db=MagicMock();db.execute.return_value.scalar.return_value="8"
    group=taxes.Vorsteuergruppe(tax_code="8",satz=7,netto=100,steuer=7,aufwandskonto="3300",vorsteuerkonto="1571")
    monkeypatch.setattr(taxes,"vorsteuergruppen",lambda *args:[group])
    monkeypatch.setattr(accounting,"kreditorenkonto",lambda *args:"1600")
    fin=MagicMock();fin.account_id_for_number.side_effect=lambda number:number
    factory=MagicMock(return_value=fin);monkeypatch.setattr(transactions,"FinanceTransactionService",factory)
    HarvestAcceptanceService(db,"own")._book_self_billing_credit_note(invoice(),None)
    factory.assert_called_once_with(db,"own",commit_on_success=False)
    lines=fin.create.call_args.kwargs["lines"]
    assert [(x["account_id"],x["debit_amount"],x["credit_amount"]) for x in lines]==[("3300",100,0),("1571",7,0),("1600",0,107)]
    db.commit.assert_not_called()

def test_invoice_repository_can_join_outer_transaction(monkeypatch):
    from modules.agrar.repositories.self_billing_repo import SelfBillingRepositoryImpl
    db=MagicMock();repo=SelfBillingRepositoryImpl(db,commit_on_success=False)
    data=invoice();model=MagicMock()
    monkeypatch.setattr(repo,"_from_service_invoice",lambda _:model)
    monkeypatch.setattr(repo,"_to_service_invoice",lambda _:data)
    assert repo.create_invoice(data) is data
    db.flush.assert_called_once();db.commit.assert_not_called()
