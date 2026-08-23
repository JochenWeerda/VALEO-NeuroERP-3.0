"""SPEC-P1-06 Welle 1: getypte response_model fuer procurement_match.

Zwei Absicherungen:
1. Die Endpunkte behalten ihr echtes Pydantic-Schema (kein Rueckfall auf dict).
2. Die Schemas verlieren kein Feld der Service-Rueckgaben — FastAPI filtert die
   Antwort gegen das response_model, ein fehlendes Feld waere ein stiller
   Datenverlust im Client.
"""

from decimal import Decimal

import pytest

from app.api.v1.endpoints import procurement_match as endpoint_module
from app.api.v1.schemas.procurement_match_schemas import (
    AutoMatchOut,
    ErsPreviewOut,
    MatchPositionOut,
    ThreeWayMatchOut,
    ThreeWayValueOut,
)
from app.services.procurement_match_service import (
    calculate_ers_credit,
    match_position,
    match_three_way_value,
)

pytestmark = pytest.mark.unit


TYPED_ROUTES = {
    ("/procurement/match/orders", "GET"): "OrderPickerListOut",
    ("/procurement/match", "GET"): "MatchOut",
    ("/procurement/match/three-way", "GET"): "ThreeWayMatchOut",
    ("/procurement/match/follow-up", "GET"): "FollowUpListOut",
    ("/procurement/match/follow-up", "POST"): "FollowUpOut",
    ("/procurement/match/ers/preview", "GET"): "ThreeWayMatchOut",
    ("/procurement/match/ers", "GET"): "ErsCreditListOut",
    ("/procurement/match/ers", "POST"): "ErsCreditOut",
    ("/procurement/match/auto", "POST"): "AutoMatchOut",
    ("/procurement/match/results", "GET"): "MatchResultListOut",
    ("/procurement/bestellungen/{bestellung_id}/wareneingang", "POST"): "WareneingangOut",
    ("/procurement/wareneingaenge/{we_id}/qs", "POST"): "WareneingangOut",
    ("/procurement/bestellungen/{bestellung_id}/rechnungspruefung", "POST"): "RechnungspruefungOut",
    ("/procurement/rechnungspruefungen/{pruefung_id}/freigabe", "POST"): "RechnungspruefungOut",
}


def _routes():
    out = {}
    for route in endpoint_module.router.routes:
        for method in route.methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                out[(route.path, method)] = route.response_model
    return out


@pytest.mark.parametrize(("key", "expected"), sorted(TYPED_ROUTES.items()))
def test_endpoint_hat_getyptes_response_model(key, expected):
    model = _routes()[key]
    assert getattr(model, "__name__", None) == expected


def test_nur_der_legacy_transition_endpunkt_bleibt_untypisiert():
    """Regressionsklammer: die Welle darf sich nicht rueckwaerts bewegen."""
    untyped = [
        path
        for (path, _method), model in _routes().items()
        if getattr(model, "__name__", None) in (None, "dict")
    ]
    assert untyped == ["/procurement/bestellungen/{bestellung_id}/transition"]


def _assert_kein_feldverlust(model, data):
    dumped = model.model_validate(data).model_dump()
    fehlend = [key for key in data if key not in dumped]
    assert not fehlend, f"{model.__name__} verliert Felder: {fehlend}"
    return dumped


@pytest.fixture
def position():
    return {
        **match_position(Decimal("100"), Decimal("120")),
        "pos_nr": 1,
        "artikel_nr": "A1",
        "bezeichnung": "Weizen",
        "einheit": "t",
        "einzelpreis": 210.0,
        "wert_offen": -4200.0,
    }


@pytest.fixture
def wertabgleich():
    return {
        **match_three_way_value(Decimal("1000"), Decimal("1200")),
        "bestellt_wert": 1000.0,
        "geliefert_wert": 1000.0,
        "fakturiert_netto": 1200.0,
        "drei_wege_abgeglichen": False,
    }


def test_positionsschema_behaelt_alle_match_felder(position):
    dumped = _assert_kein_feldverlust(MatchPositionOut, position)
    assert dumped["status"] == "ueberliefert"
    assert dumped["abweichung"] is True


def test_wertabgleich_behaelt_alle_felder(wertabgleich):
    dumped = _assert_kein_feldverlust(ThreeWayValueOut, wertabgleich)
    assert dumped["differenz"] == 200.0


def test_ers_vorschau_behaelt_alle_felder(position, wertabgleich):
    preview = calculate_ers_credit([position], wertabgleich)
    dumped = _assert_kein_feldverlust(ErsPreviewOut, preview)
    assert dumped["berechtigt"] is True
    typen = {zeile["typ"] for zeile in dumped["positionen"]}
    assert typen == {"ueberlieferung", "rechnungsueberzahlung"}


def _voller_match(position, wertabgleich):
    return {
        "found": True,
        "bestellnummer": "B-1",
        "status": "OFFEN",
        "lieferant_id": "L1",
        "netto_summe": 1000.0,
        "positionen": [position],
        "wareneingaenge": [
            {
                "id": "g1",
                "gr_number": "WE-1",
                "datum": "2026-08-23",
                "status": "OK",
                "lieferschein": "LS-1",
            }
        ],
        "luecken": [{"pos_nr": 1, "schwere": "warnung", "text": "teilgeliefert"}],
        "summary": {
            "positionen": 1,
            "wareneingaenge": 1,
            "vollstaendig_geliefert": True,
            "hat_abweichung": True,
            "offene_luecken": 1,
            "rechnungen": 1,
            "drei_wege_abgeglichen": False,
            "hat_ausnahme": True,
        },
        "rechnungen": [
            {
                "id": "r1",
                "rechnungsnummer": "R-1",
                "datum": "2026-08-01",
                "gesamt_netto": 1200.0,
                "gesamt_brutto": 1428.0,
                "zugeordneter_auftrag": "B-1",
                "zugeordneter_lieferschein": "LS-1",
                "status": "OFFEN",
            }
        ],
        "three_way": wertabgleich,
        "ausnahmen": [
            {"schwere": "blocker", "code": "rechnungswert_abweichung", "text": "Abweichung"}
        ],
        "follow_ups": [
            {
                "id": "f1",
                "action_type": "reklamation",
                "ausnahme_code": None,
                "grund": "Menge",
                "eskalationsstufe": 1,
                "created_at": "2026-08-23T00:00:00",
                "created_by": "u",
            }
        ],
        "ers_preview": calculate_ers_credit([position], wertabgleich),
        "ers_credits": [
            {
                "id": "e1",
                "gutschrift_nummer": "ERS-B-1-001",
                "betrag_netto": 200.0,
                "grund": "Abweichung",
                "ausnahme_code": "rechnungswert_abweichung",
                "status": "entwurf",
                "positionen": [],
                "created_at": "2026-08-23T00:00:00",
                "created_by": "u",
            }
        ],
    }


def test_three_way_match_behaelt_alle_felder(position, wertabgleich):
    dumped = _assert_kein_feldverlust(ThreeWayMatchOut, _voller_match(position, wertabgleich))
    # Verschachtelte Ebenen duerfen ebenfalls nichts verlieren.
    for feld in ("bestellt", "geliefert", "offen", "abweichung_pct", "wert_offen"):
        assert feld in dumped["positionen"][0]
    assert dumped["summary"]["hat_ausnahme"] is True
    assert dumped["follow_ups"][0]["eskalationsstufe"] == 1
    assert dumped["ers_credits"][0]["gutschrift_nummer"] == "ERS-B-1-001"


def test_three_way_match_traegt_den_nichttrefferfall():
    """`{"found": false, "detail": ...}` darf nicht wegtypisiert werden."""
    dumped = ThreeWayMatchOut.model_validate(
        {"found": False, "detail": "Bestellung nicht aufloesbar."}
    ).model_dump()
    assert dumped["found"] is False
    assert dumped["detail"] == "Bestellung nicht aufloesbar."
    assert dumped["positionen"] == []


def test_auto_match_behaelt_alle_felder(position, wertabgleich):
    daten = {
        "match_id": "m1",
        "match_status": "MISMATCH",
        "drei_wege_abgeglichen": False,
        "discrepancy_reason": "Mengenabweichung 20% > Toleranz 2%",
        "tolerance_check": {
            "qty_delta_pct": 20.0,
            "qty_tolerance_pct": 2.0,
            "qty_ok": False,
            "value_delta_pct": 20.0,
            "price_tolerance_pct": 1.0,
            "value_ok": False,
            "missing_context": ["Eingangsrechnung"],
        },
        "detail": _voller_match(position, wertabgleich),
    }
    dumped = _assert_kein_feldverlust(AutoMatchOut, daten)
    assert dumped["tolerance_check"]["missing_context"] == ["Eingangsrechnung"]
    assert dumped["detail"]["bestellnummer"] == "B-1"


def test_keine_response_model_korruption_in_summaries():
    """Ein frueherer Ersetzungslauf hatte `response_model=...` in eine
    OpenAPI-summary geschrieben; das darf nicht zurueckkommen."""
    for route in endpoint_module.router.routes:
        assert "response_model=" not in (getattr(route, "summary", "") or "")
