from __future__ import annotations

import asyncio
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.api.v1.endpoints.daily_prices import (
    DailyPriceBulkCreateIn,
    DailyPriceCreateIn,
    bulk_import_prices_endpoint,
    import_prices_file,
)


class FailDailyPriceDB:
    def add(self, *args, **kwargs):
        raise AssertionError("DB write should not happen before DQ validation")

    def add_all(self, *args, **kwargs):
        raise AssertionError("DB write should not happen before DQ validation")

    def commit(self):
        raise AssertionError("commit should not happen before DQ validation")

    def refresh(self, *args, **kwargs):
        raise AssertionError("refresh should not happen before DQ validation")


def _upload(name: str, content: str) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(content.encode("utf-8")))


def test_daily_price_bulk_import_rejects_missing_scope_before_db_access():
    payload = DailyPriceBulkCreateIn(
        prices=[
            DailyPriceCreateIn(
                price_eur_per_ton=250.0,
                currency="EUR",
                price_date="2026-03-15",
                source_type="manual",
            )
        ]
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            bulk_import_prices_endpoint(
                payload=payload,
                db=FailDailyPriceDB(),
                tenant_id="tenant-1",
                request=None,
                _="admin",
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "DailyPriceImport"


def test_daily_price_csv_import_rejects_invalid_price_before_db_access():
    file = _upload("prices.csv", "article_id,price_eur_per_ton,currency,price_date,source_type\nART-1,0,EUR,2026-03-15,manual\n")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            import_prices_file(
                file=file,
                db=FailDailyPriceDB(),
                tenant_id="tenant-1",
                request=None,
                _="admin",
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "DailyPriceImport"


def test_daily_price_json_import_rejects_invalid_source_type_before_db_access():
    file = _upload(
        "prices.json",
        '[{"article_id":"ART-1","price_eur_per_ton":250,"currency":"EUR","price_date":"2026-03-15","source_type":"broken"}]',
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            import_prices_file(
                file=file,
                db=FailDailyPriceDB(),
                tenant_id="tenant-1",
                request=None,
                _="admin",
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "DailyPriceImport"
