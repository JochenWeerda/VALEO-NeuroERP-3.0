from unittest.mock import MagicMock

import pytest

from app.services.docflow_return_service import (
    DocflowReturnService,
    DocumentReturnError,
    valid_return_transition,
)

pytestmark = pytest.mark.unit


def test_shipping_and_return_transition_contracts() -> None:
    assert valid_return_transition("shipping", "not_sent", "sent")
    assert not valid_return_transition("shipping", "delivered", "sent")
    assert valid_return_transition("return", "expected", "received")
    assert valid_return_transition("return", "verified", "closed")
    assert not valid_return_transition("return", "expected", "closed")


def test_list_page_is_tenant_scoped_and_server_paginated() -> None:
    db = MagicMock()
    total_result = MagicMock()
    total_result.scalar_one.return_value = 1
    rows_result = MagicMock()
    rows_result.mappings.return_value.all.return_value = [{"id": "case-1"}]
    db.execute.side_effect = [total_result, rows_result]
    result = DocflowReturnService(db, "tenant-1").list_page(page=2, page_size=25, assigned_user="jochen")
    assert result["total"] == 1
    assert result["page"] == 2
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1"


def test_create_rejects_artifact_from_another_document_or_tenant() -> None:
    db = MagicMock()
    header_result = MagicMock()
    header_result.mappings.return_value.first.return_value = {"id": "doc-1", "doc_number": "RE-1"}
    artifact_result = MagicMock()
    artifact_result.scalar_one_or_none.return_value = None
    db.execute.side_effect = [header_result, artifact_result]

    with pytest.raises(DocumentReturnError, match="Artefakt gehoert nicht"):
        DocflowReturnService(db, "tenant-1").create_case(
            {"document_ref": "RE-1", "artifact_id": "foreign-artifact", "reason": "Ruecklauf erwartet"},
            actor="tester",
        )
    db.commit.assert_not_called()


def test_document_return_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("docflow/dokumenten-ruecklauf")
    assert definition is not None
    assert definition["adapter"]["temporary"] is False
    assert definition["tables"][0]["serverPagination"] is True
    assert definition["tables"][0]["dataSourceKey"] == "returns"
    assert _check_readiness(definition)["generatorReady"] is True


def test_document_return_routes_are_registered() -> None:
    from main import app

    paths = {route.path for route in app.routes}
    assert "/api/v1/docflow/returns" in paths
    assert "/api/v1/docflow/returns/{case_id}/evidence" in paths
    assert "/api/v1/docflow/returns/{case_id}/transition" in paths
