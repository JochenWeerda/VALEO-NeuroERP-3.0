"""Native list reads tenant-scoped service documents, not purchase requests."""
import asyncio

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.compat import list_service_entry_sheets
from app.api.v1.schemas.compat_schemas import ServiceEntrySheetListOut
from app.core.screen_definitions_domain_batch15 import build_einkauf_service_entry_sheets_screen_definition
from app.services import compat_helpers


class Repository:
    def __init__(self, documents):
        self.documents = documents
        self.calls = []

    def list_documents(self, doc_type, skip, limit, filters):
        self.calls.append((doc_type, skip, limit, filters))
        return [doc for doc in self.documents if all(doc.get(k) == v for k, v in filters.items())][skip:skip + limit]

    def count_documents(self, doc_type, filters):
        return sum(all(doc.get(k) == v for k, v in filters.items()) for doc in self.documents)


def test_native_list_reads_real_tenant_documents(monkeypatch):
    own = {"id": "own", "tenantId": "a", "number": "SES-1", "supplierId": "SUP-1",
           "purchaseOrderId": "PO-1", "serviceDate": "2026-11-23", "description": "Wartung",
           "quantity": 2, "unitPrice": 5, "amount": 10, "status": "ERFASST", "createdAt": "2026-11-23T07:00:00"}
    other = {**own, "id": "other", "tenantId": "b"}
    repo = Repository([own, other, {**own, "id": "approved", "status": "FREIGEGEBEN"}])
    monkeypatch.setattr(compat_helpers, "doc_repo", lambda db: repo)
    screen = build_einkauf_service_entry_sheets_screen_definition()
    assert screen["title"] == "Leistungsnachweise"
    assert screen["dataSources"][0]["endpoint"] == "/api/v1/einkauf/service-entry-sheets"
    assert screen["tables"][0]["rowActions"] == []
    assert [action["key"] for action in screen["actions"]] == ["export"]

    response = asyncio.run(list_service_entry_sheets(status="ERFASST", tenant_id="a", db=object()))
    serialized = ServiceEntrySheetListOut.model_validate(response).model_dump()
    assert serialized["items"] == [{k: v for k, v in own.items() if k != "tenantId"}]
    with pytest.raises(ValidationError):
        ServiceEntrySheetListOut.model_validate({"items": [{"id": "own"}], "total": 1})
    assert serialized["total"] == 1
    assert {column["key"] for column in screen["tables"][0]["columns"]} <= own.keys()
    assert repo.calls[-1] == ("service_entry_sheet", 0, 1000, {"tenantId": "a"})

    empty = asyncio.run(list_service_entry_sheets(status=None, tenant_id="c", db=object()))
    assert empty == {"items": [], "total": 0}
    assert repo.calls[-1][3] == {"tenantId": "c"}
