from __future__ import annotations

from unittest.mock import MagicMock
import json

import pytest

from app.api.v1.endpoints import dms_images
from app.integrations import dms_client

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


@pytest.mark.asyncio
async def test_document_list_uses_canonical_columns_and_tenant_scope(monkeypatch) -> None:
    db = MagicMock()
    db.execute.return_value.mappings.return_value.all.return_value = [{
        "id": "link-1",
        "document_id": "42",
        "document_name": "Analyse.pdf",
        "document_type": "application/pdf",
    }]
    monkeypatch.setattr(dms_images, "is_configured", lambda: True)
    monkeypatch.setattr(dms_images, "get_document_url", lambda document_id: f"https://dms/{document_id}")

    result = await dms_images.list_dms_documents(
        entity_type="article", entity_id="A-1", tenant_id="tenant-1", db=db
    )

    assert result[0].filename == "Analyse.pdf"
    assert result[0].url == "https://dms/42"
    sql = str(db.execute.call_args.args[0])
    assert "document_name" in sql and "file_name" not in sql
    assert db.execute.call_args.args[1] == {"tid": "tenant-1", "eid": "A-1"}


@pytest.mark.asyncio
async def test_document_unlink_is_tenant_scoped() -> None:
    db = MagicMock()
    db.execute.return_value.rowcount = 1
    response = await dms_images.delete_dms_document("link-1", "tenant-1", db)
    assert response.status_code == 204
    assert "tenant_id=:tid" in str(db.execute.call_args.args[0])
    assert db.execute.call_args.args[1] == {"id": "link-1", "tid": "tenant-1"}


def test_article_upload_resolves_german_bootstrap_profile(monkeypatch, tmp_path) -> None:
    config = tmp_path / "dms.json"
    config.write_text(json.dumps({"document_types": {"Artikel": 7}}), encoding="utf-8")
    source = tmp_path / "analyse.pdf"
    source.write_bytes(b"pdf")
    posted: dict = {}

    class Response:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"id": 42}

    class Client:
        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def post(self, path, *, files=None, data=None, json=None):
            posted.update(path=path, files=files, data=data, json=json)
            return Response()

    monkeypatch.setattr(dms_client, "CONFIG_PATH", config)
    monkeypatch.setattr(dms_client, "get_client", lambda: Client())
    result = dms_client.upload_document("article", "Analyse", str(source))
    assert result["ok"] is True and result["document_id"] == 42
    assert posted["data"] == {"document_type_id": 7}
