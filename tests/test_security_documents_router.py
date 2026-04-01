from __future__ import annotations

import importlib

import pytest
from fastapi import HTTPException

from app.documents.models import SalesOrder

documents_router = importlib.import_module("app.documents.router")


@pytest.mark.asyncio
async def test_sales_order_masks_internal_error_details(monkeypatch):
    def _raise(*args, **kwargs):
        raise RuntimeError("psycopg2 password=secret host=db-internal")

    monkeypatch.setattr(documents_router, "save_to_store", _raise)

    with pytest.raises(HTTPException) as exc:
        await documents_router.upsert_sales_order(
            SalesOrder(number="SO-1", date="2026-04-01", customerId="C-1"),
            db=None,
        )

    assert exc.value.status_code == 500
    assert exc.value.detail == "Interner Fehler bei Dokumentverarbeitung"
