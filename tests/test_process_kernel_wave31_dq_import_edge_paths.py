from __future__ import annotations

import asyncio
import importlib
from io import BytesIO

import pytest
from fastapi import HTTPException, UploadFile

from app.api.v1.endpoints.portal_feldbuch import portal_import
from app.api.v1.endpoints.quality_protocols import (
    QualityProtocolCreateIn,
    create_protocol,
    import_protocol_from_csv,
    import_protocol_from_json,
)
from app.api.v1.endpoints.self_billing import (
    CreditNoteCreateIn,
    PreviewIn,
    create_credit_note_endpoint,
    preview_self_billing,
)

quality_protocols_endpoint = importlib.import_module("app.api.v1.endpoints.quality_protocols")
self_billing_endpoint = importlib.import_module("app.api.v1.endpoints.self_billing")
portal_feldbuch_endpoint = importlib.import_module("app.api.v1.endpoints.portal_feldbuch")


class FailRepoDB:
    def query(self, *args, **kwargs):
        raise AssertionError("DB access should not happen before DQ validation")

    def commit(self):
        raise AssertionError("commit should not happen before DQ validation")


def _upload(name: str, content: str) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(content.encode("utf-8")))


def test_create_quality_protocol_rejects_missing_acceptance_before_repo_call(monkeypatch: pytest.MonkeyPatch):
    async def _fail(*args, **kwargs):
        raise AssertionError("service create should not happen before DQ validation")

    monkeypatch.setattr(quality_protocols_endpoint, "create_quality_protocol", _fail)
    payload = QualityProtocolCreateIn(source_type="manual", moisture_pct=15.5)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_protocol(payload, db=FailRepoDB(), tenant_id="tenant-1", request=None))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Qualitaetsprotokoll"


def test_import_quality_protocol_csv_rejects_invalid_moisture_before_repo_call():
    file = _upload("quality.csv", "moisture_pct,protein_pct,hl_weight_kg_per_hl\n120,12,72\n")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(import_protocol_from_csv(harvest_acceptance_id="HA-001", file=file, db=FailRepoDB(), tenant_id="tenant-1", request=None))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Qualitaetsprotokoll"


def test_import_quality_protocol_json_rejects_invalid_moisture_before_repo_call():
    file = _upload("quality.json", '{"moisture_pct": 120, "protein_pct": 12, "hl_weight_kg_per_hl": 72}')

    with pytest.raises(HTTPException) as exc:
        asyncio.run(import_protocol_from_json(harvest_acceptance_id="HA-001", file=file, db=FailRepoDB(), tenant_id="tenant-1", request=None))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "Qualitaetsprotokoll"


def test_self_billing_create_rejects_invalid_taxation_type_before_service_call(monkeypatch: pytest.MonkeyPatch):
    def _fail(*args, **kwargs):
        raise AssertionError("self-billing service should not happen before DQ validation")

    monkeypatch.setattr(self_billing_endpoint, "create_credit_note", _fail)
    payload = CreditNoteCreateIn(
        harvest_acceptance_id="HA-001",
        total_net_amount_eur=100,
        total_vat_amount_eur=0,
        total_gross_amount_eur=119,
        vat_rate_percent=19,
        taxation_type="invalid",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(create_credit_note_endpoint("HA-001", payload, db=FailRepoDB(), tenant_id="tenant-1", request=None))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "SelfBilling"


def test_self_billing_preview_rejects_invalid_taxation_type_before_processing():
    payload = PreviewIn(
        harvest_acceptance_id="HA-001",
        total_net_amount_eur=0,
        total_gross_amount_eur=100,
        vat_rate_percent=19,
        taxation_type="invalid",
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(preview_self_billing(payload, db=FailRepoDB(), tenant_id="tenant-1"))

    assert exc.value.status_code == 422
    assert exc.value.detail["entity_typ"] == "SelfBilling"


def test_portal_feldbuch_import_rejects_invalid_row_before_service_call(monkeypatch: pytest.MonkeyPatch):
    def _fail(*args, **kwargs):
        raise AssertionError("feldbuch import service should not happen before DQ validation")

    monkeypatch.setattr(portal_feldbuch_endpoint, "import_csv", _fail)
    file = _upload("feldbuch.csv", "Datum;Schlag;Typ;Flaeche\n;Nordfeld;duengung;12,5\n")

    with pytest.raises(HTTPException) as exc:
        asyncio.run(portal_import(file=file, db=FailRepoDB(), tenant_id="tenant-1", customer_id="cust-1"))

    assert exc.value.status_code == 422
