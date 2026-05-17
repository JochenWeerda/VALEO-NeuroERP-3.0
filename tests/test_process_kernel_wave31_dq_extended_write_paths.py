from __future__ import annotations

import asyncio
import importlib
from datetime import date
from io import BytesIO
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import HTTPException, UploadFile

from app.api.v1.endpoints.compat import (
    import_debitoren_csv,
    import_einzelfuttermittel_csv,
    import_kunden_csv,
)
from app.api.v1.endpoints.customers import CustomerCreate, CustomerUpdate, create_customer, update_customer
from app.api.v1.endpoints.harvest_acceptance import (
    HarvestAcceptanceCreate,
    HarvestAcceptanceUpdate,
    create_harvest_acceptance,
    update_harvest_acceptance,
)

customers_endpoint = importlib.import_module("app.api.v1.endpoints.customers")
customer_service_module = importlib.import_module("app.services.customer_service")


class FailQueryDB:
    def query(self, *args, **kwargs):
        raise AssertionError("DB query should not happen before DQ validation")

    def execute(self, *args, **kwargs):
        raise AssertionError("DB execute should not happen before DQ validation")

    def commit(self):
        raise AssertionError("commit should not happen before DQ validation")

    def refresh(self, *args, **kwargs):
        raise AssertionError("refresh should not happen before DQ validation")


class ImportGuardDB:
    def execute(self, *args, **kwargs):
        raise AssertionError("invalid CSV row should not be persisted")

    def commit(self):
        return None

    def rollback(self):
        raise AssertionError("rollback should not happen for skipped invalid rows")


class _QueryStub:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class HarvestAcceptanceUpdateDB:
    def __init__(self):
        self.acceptance = type(
            "AcceptanceStub",
            (),
            {
                "id": "ha-1",
                "tenant_id": "tenant-1",
                "acceptance_number": "HA-001",
                "customer_id": "C-001",
                "delivery_date": date(2026, 3, 15),
                "pricing_mode": "spot_daily",
                "acceptance_mode": "PURCHASE_AT_DELIVERY_PTBF",
                "origin_country_code": "DE",
                "release_status": "draft",
            },
        )()

    def query(self, *args, **kwargs):
        return _QueryStub(self.acceptance)

    def commit(self):
        raise AssertionError("commit should not happen after DQ rejection")

    def refresh(self, *args, **kwargs):
        raise AssertionError("refresh should not happen after DQ rejection")


def _upload(name: str, content: str) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(content.encode("utf-8")))


def test_create_customer_rejects_invalid_country_before_crm_call(monkeypatch: pytest.MonkeyPatch):
    async def _fail(*args, **kwargs):
        raise AssertionError("crm create should not happen before DQ validation")

    monkeypatch.setattr(customer_service_module, "_crm_create", _fail)

    payload = CustomerCreate(
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        customer_number="C-001",
        company_name="Kunde AG",
        country="XX",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_customer(payload, db=MagicMock()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Debitor"


def test_update_customer_rejects_invalid_country_before_crm_call(monkeypatch: pytest.MonkeyPatch):
    async def _fail(*args, **kwargs):
        raise AssertionError("crm update should not happen before DQ validation")

    monkeypatch.setattr(customer_service_module, "_crm_update", _fail)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(update_customer("cust-1", CustomerUpdate(country="XX")))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Debitor"


def test_import_kunden_csv_skips_invalid_country_without_db_write():
    file = _upload("kunden.csv", "Firma;Land\nKunde AG;XX\n")

    result = asyncio.run(
        import_kunden_csv(
            file=file,
            db=ImportGuardDB(),
            tenant_id="00000000-0000-0000-0000-000000000001",
        )
    )

    assert result["created"] == 0
    assert result["updated"] == 0
    assert len(result["errors"]) == 1


def test_import_einzelfuttermittel_csv_skips_invalid_vat_without_db_write():
    file = _upload("artikel.csv", "Bezeichnung;Artikelnummer;MwSt\nWeizen;ART-1;25\n")

    result = asyncio.run(import_einzelfuttermittel_csv(file=file, db=ImportGuardDB()))

    assert result["created"] == 0
    assert result["updated"] == 0
    assert len(result["errors"]) == 1


def test_import_debitoren_csv_skips_invalid_country_without_db_write():
    file = _upload("debitoren.csv", "Kunde;Land\nKunde AG;XX\n")

    result = asyncio.run(
        import_debitoren_csv(
            file=file,
            db=ImportGuardDB(),
            tenant_id="00000000-0000-0000-0000-000000000001",
        )
    )

    assert result["created"] == 0
    assert result["updated"] == 0
    assert len(result["errors"]) == 1


def test_create_harvest_acceptance_rejects_invalid_country_before_db_query():
    payload = HarvestAcceptanceCreate(
        customer_id="C-001",
        delivery_date=date(2026, 3, 15),
        origin_country_code="XX",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_harvest_acceptance(payload, request=None, tenant_id="tenant-1", db=FailQueryDB()))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "ErnteAnnahme"


def test_update_harvest_acceptance_rejects_invalid_country_before_commit():
    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            update_harvest_acceptance(
                "ha-1",
                HarvestAcceptanceUpdate(origin_country_code="XX"),
                request=None,
                tenant_id="tenant-1",
                db=HarvestAcceptanceUpdateDB(),
            )
        )

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "ErnteAnnahme"
