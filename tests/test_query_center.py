from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.query_center_service import QueryCenterError, QueryCenterService

pytestmark = pytest.mark.unit

VALID = {
    "name": "Offene Rechnungen",
    "data_product_id": "finance-ap-invoice-cockpit",
    "selected_fields": ["invoice_number", "status", "gross_amount"],
    "filter_spec": {"status": "open"},
    "aggregations": [],
}


def test_rejects_unknown_data_product() -> None:
    with pytest.raises(QueryCenterError, match="nicht.*freigegeben"):
        QueryCenterService(MagicMock(), "tenant-1").validate(
            {**VALID, "data_product_id": "raw-sql"}
        )


def test_rejects_unknown_field_and_aggregation() -> None:
    service = QueryCenterService(MagicMock(), "tenant-1")
    with pytest.raises(QueryCenterError, match="Feldliste"):
        service.validate({**VALID, "selected_fields": ["password"]})
    with pytest.raises(QueryCenterError, match="Aggregation"):
        service.validate({**VALID, "aggregations": ["sum:password"]})


def test_signed_export_and_import_revalidates() -> None:
    db = MagicMock()
    loaded = MagicMock()
    loaded.mappings.return_value.first.return_value = {
        "id": "q1",
        **VALID,
        "is_favorite": True,
    }
    db.execute.side_effect = [loaded, MagicMock()]
    service = QueryCenterService(db, "tenant-1", signing_key="test-signing-key")
    bundle = service.export_signed("q1", actor="user-1", reason="Weitergabe intern")
    assert bundle["algorithm"] == "HMAC-SHA256"
    assert len(bundle["signature"]) == 64


def test_tampered_import_is_rejected() -> None:
    service = QueryCenterService(
        MagicMock(), "tenant-1", signing_key="test-signing-key"
    )
    with pytest.raises(QueryCenterError, match="Signatur"):
        service.import_signed(
            {"schema_version": 1, "definition": VALID, "signature": "0" * 64},
            actor="user",
            reason="Import pruefen",
        )


def test_list_is_tenant_and_owner_scoped() -> None:
    db = MagicMock()
    count = MagicMock()
    count.scalar_one.return_value = 1
    rows = MagicMock()
    rows.mappings.return_value.all.return_value = [{"id": "q1"}]
    db.execute.side_effect = [count, rows]
    result = QueryCenterService(db, "tenant-1").list_page(owner_id="user-1")
    assert result["total"] == 1
    for call in db.execute.call_args_list:
        assert call.args[1]["tid"] == "tenant-1" and call.args[1]["owner"] == "user-1"


def test_screen_is_native_and_generator_ready() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    definition = get_screen_definition("auswertungen/abfrage-center")
    assert definition and definition["adapter"]["type"] == "native"
    assert _check_readiness(definition)["generatorReady"] is True
