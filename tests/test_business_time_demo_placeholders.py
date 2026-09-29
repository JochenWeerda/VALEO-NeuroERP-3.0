from __future__ import annotations

from datetime import date, datetime

from app.einkauf import ocr_invoice
from app.security import compliance_monitor
from app.services import atlas_customs_service


class _FrozenUtcDatetime(datetime):
    @classmethod
    def utcnow(cls):
        return cls(2029, 12, 31, 23, 30, 0)


def test_ocr_fallback_uses_business_day_and_keeps_processing_timestamp_utc(
    monkeypatch,
) -> None:
    monkeypatch.setattr(ocr_invoice, "business_today", lambda: date(2030, 1, 1))
    monkeypatch.setattr(ocr_invoice, "datetime", _FrozenUtcDatetime)

    result = ocr_invoice.extract_invoice_pdf(
        file_id="invoice-without-pdf",
        engine="stub",
        pdf_bytes=None,
    )

    assert result["extracted_data"]["rechnungs_datum"] == "2030-01-01"
    assert result["processed_at"] == "2029-12-31T23:30:00"


def test_atlas_mrn_year_uses_business_day(monkeypatch) -> None:
    monkeypatch.setattr(
        atlas_customs_service,
        "business_today",
        lambda: date(2030, 1, 1),
    )

    mrn = atlas_customs_service.generate_mrn("DE")

    assert mrn[:4] == "DE30"
    assert len(mrn) == 19


def test_atlas_exit_date_uses_business_day_and_keeps_event_timestamp_utc(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        atlas_customs_service,
        "business_today",
        lambda: date(2030, 1, 1),
    )
    monkeypatch.setattr(atlas_customs_service, "datetime", _FrozenUtcDatetime)
    service = atlas_customs_service.ATLASCustomsService()
    monkeypatch.setattr(
        service,
        "_load_by_mrn",
        lambda _mrn, _db: {"status": "BEWILLIGT"},
    )

    result = service.get_ausfuhrnachricht("DE30ABCDEFGHIJKLM")

    assert result["ausgang_am"] == "2030-01-01"
    assert result["erledigt_am"] == "2029-12-31T23:30:00Z"


def test_compliance_demo_trend_ends_on_business_day(monkeypatch) -> None:
    monkeypatch.setattr(
        compliance_monitor,
        "business_today",
        lambda: date(2030, 1, 1),
    )
    monitor = compliance_monitor.ISO27001ComplianceMonitor(db_session=None)

    trend = monitor._get_compliance_trend("tenant-1")

    assert [point["date"] for point in trend] == [
        date(2029, 12, 26),
        date(2029, 12, 27),
        date(2029, 12, 28),
        date(2029, 12, 29),
        date(2029, 12, 30),
        date(2029, 12, 31),
        date(2030, 1, 1),
    ]
