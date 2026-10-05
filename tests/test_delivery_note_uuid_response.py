"""Regression for real PostgreSQL UUID order links in delivery-note responses."""
from datetime import date, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.sales_delivery_notes import DeliveryNote


def note(order_id):
    return DeliveryNote(id="delivery-1", tenant_id="tenant-1",
                        delivery_note_number="LS-1", delivery_date=date.today(),
                        created_at=datetime.now(), updated_at=datetime.now(),
                        sales_order_id=order_id)


@pytest.mark.parametrize("value", [None, "legacy-order", UUID(int=1)])
def test_order_reference_retains_string_api_contract(value):
    result = note(value)
    assert result.model_dump(mode="json")["sales_order_id"] == (str(value) if value is not None else None)


def test_invalid_reference_type_is_not_silently_stringified():
    with pytest.raises(ValidationError):
        note({"id": "not-a-scalar"})
