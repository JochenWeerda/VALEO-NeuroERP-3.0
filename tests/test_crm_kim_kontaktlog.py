"""KIM-L3-BACKEND-001 — Kontaktlog-Mapping + TAPI-Normalisierung (reine Funktionen)."""

from __future__ import annotations

import pytest


def test_log_from_row_maps_art_betreff_kommentar_cc() -> None:
    from app.api.v1.endpoints.crm_kim import _log_from_row

    row = {
        "id": "11111111-1111-1111-1111-111111111111",
        "richtung": "ein",
        "art": "email",
        "kurzinfo": "Angebot 40t Weizen",
        "notiz": "Kunde wünscht Lieferung Montag, Preis bestätigt.",
        "wiedervorlage": "2026-06-15",
        "weiterleitung_an": "AO",
        "bediener": "JW",
        "verweis": "AN-2026-1",
        "erledigt": False,
        "created_at": "2026-06-09",
    }
    log = _log_from_row(row, "1280227")
    assert log.art == "email"
    assert log.betreff == "Angebot 40t Weizen"
    assert log.kommentar == "Kunde wünscht Lieferung Montag, Preis bestätigt."
    assert log.ccIntern == "AO"
    assert log.artKurzinfo == "Angebot 40t Weizen"
    assert log.direction == "INCOMING"
    assert log.reSubmissionDate == "2026-06-15"
    assert log.referenceNo == "AN-2026-1"


def test_log_from_row_tolerates_empty_optional_fields() -> None:
    from app.api.v1.endpoints.crm_kim import _log_from_row

    log = _log_from_row({"id": "x", "richtung": "aus"}, "1")
    assert log.direction == "OUTGOING"
    assert log.art is None
    assert log.betreff is None
    assert log.kommentar is None
    assert log.artKurzinfo == ""


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("0049 4941 71729", "494171729"),
        ("+49 (4941) 71729", "494171729"),
        ("04941/71729", "494171729"),
        ("4941 71729", "494171729"),
    ],
)
def test_tapi_norm_phone(raw: str, expected: str) -> None:
    from app.api.v1.endpoints.tapi import _norm_phone

    assert _norm_phone(raw) == expected
