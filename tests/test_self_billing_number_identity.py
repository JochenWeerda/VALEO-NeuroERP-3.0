"""Time-neighboring self-billing drafts must keep the UUID entropy."""
from types import SimpleNamespace
from unittest.mock import MagicMock
from decimal import Decimal
import pytest
from modules.agrar.services import self_billing_service as service

@pytest.fixture(autouse=True)
def _enable_dev_token():
    yield

UUID_A="019a0100-0000-7000-8000-000000000001"
UUID_B="019a0100-0000-7000-8000-000000000002"

def test_standalone_references_do_not_collapse_to_uuid_timestamp(monkeypatch):
    values=iter((UUID_A,UUID_B));monkeypatch.setattr(service,"uuid7",lambda:next(values))
    first=service._generate_invoice_number("own","019a0100-0000-7000-8000-000000000099")
    second=service._generate_invoice_number("own","019a0100-0000-7000-8000-000000000099")
    assert first!=second and len(first)<=50 and len(second)<=50

def test_invoice_identity_keeps_full_uuid_for_same_timestamp(monkeypatch):
    values=iter((UUID_A,UUID_B));monkeypatch.setattr(service,"uuid7",lambda:next(values))
    repo=MagicMock();repo.create_invoice.side_effect=lambda invoice:invoice
    payload=service.CreditNoteCreate("own","acceptance",Decimal("100"),Decimal("7"),Decimal("107"),Decimal("7"),invoice_number="GS000001")
    first=service.create_credit_note(repo,payload);second=service.create_credit_note(repo,payload)
    assert first.id!=second.id
    assert first.id=="sb_"+UUID_A.replace("-","")
    assert second.id=="sb_"+UUID_B.replace("-","")
