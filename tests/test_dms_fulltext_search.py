from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.api.v1.endpoints import dms_images

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_dms_search_is_tenant_scoped_and_returns_deep_links(monkeypatch) -> None:
    db = MagicMock()
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    rows_result = MagicMock()
    rows_result.mappings.return_value.all.return_value = [
        {
            "id": "link-1",
            "document_id": "42",
            "document_name": "Analyse",
            "document_type": "certificate",
            "document_category": "quality",
            "description": "Freigegeben",
            "dokument_nummer": "D-1",
            "valid_from": None,
            "valid_to": None,
            "created_at": None,
            "article_id": "A-1",
            "article_number": "1000",
            "article_name": "Artikel",
        }
    ]
    db.execute.side_effect = [count_result, rows_result]
    monkeypatch.setattr(dms_images, "is_configured", lambda: True)
    monkeypatch.setattr(
        dms_images, "get_document_url", lambda document_id: f"https://dms/{document_id}"
    )

    result = await dms_images.search_dms_documents(
        q="Analyse",
        document_type=None,
        document_category=None,
        article_id=None,
        page=1,
        page_size=50,
        tenant_id="tenant-1",
        db=db,
    )

    assert result.total == 1
    assert result.items[0].source_route == "/artikel/stamm/A-1"
    assert result.items[0].preview_url == "https://dms/42"
    assert all(call.args[1]["tid"] == "tenant-1" for call in db.execute.call_args_list)


def test_dms_and_audit_screens_use_native_runtime() -> None:
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import get_screen_definition

    for screen_id in ("auswertungen/dms-volltext", "auswertungen/aenderungshistorie"):
        definition = get_screen_definition(screen_id)
        assert definition["adapter"]["type"] == "native"
        assert _check_readiness(definition)["generatorReady"] is True
