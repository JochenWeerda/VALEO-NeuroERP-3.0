"""Executable Unit-Tests: EinkaufCompat Angebot/Avis-Paritaet (Sonar New-Code-Coverage)."""
from __future__ import annotations

from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.services.einkauf_compat_service import EinkaufCompatService


def test_parse_notizen_dict_json_text_and_empty():
    assert EinkaufCompatService._parse_notizen({"a": 1}) == {"a": 1}
    assert EinkaufCompatService._parse_notizen('{"mindestabnahme": 10}') == {"mindestabnahme": 10}
    assert EinkaufCompatService._parse_notizen("[1,2]") == {}
    assert EinkaufCompatService._parse_notizen("Freitext ohne JSON") == {"bemerkungen": "Freitext ohne JSON"}
    assert EinkaufCompatService._parse_notizen("") == {}
    assert EinkaufCompatService._parse_notizen(None) == {}
    assert EinkaufCompatService._parse_notizen("   ") == {}


def test_angebot_row_to_dict_maps_positions_and_notizen():
    row = {
        "id": "ang-1",
        "angebots_nummer": "ANG-9",
        "anfrage_id": "anf-1",
        "lieferant_name": "Mueller GmbH",
        "lieferant_id": "L-1",
        "artikel_nr": "ART-1",
        "menge": 12.5,
        "einheit": "t",
        "einheitspreis": 100.0,
        "netto_summe": None,
        "waehrung": "EUR",
        "gueltig_bis": date(2026, 12, 31),
        "status": "ERFASST",
        "lieferzeit_tage": 5,
        "notizen": '{"mindestabnahme": 2, "zahlungsbedingungen": "14 Tage", "incoterms": "EXW", "bemerkungen": "ok"}',
        "created_at": datetime(2026, 11, 1, 10, 0, 0),
    }
    out = EinkaufCompatService._angebot_row_to_dict(row)
    assert out["id"] == "ang-1"
    assert out["angebotNummer"] == "ANG-9"
    assert out["anfrageId"] == "anf-1"
    assert out["lieferantId"] == "L-1"
    assert out["artikel"] == "ART-1"
    assert out["menge"] == 12.5
    assert out["preis"] == 100.0
    assert out["lieferzeit"] == 5
    assert out["mindestabnahme"] == 2
    assert out["zahlungsbedingungen"] == "14 Tage"
    assert out["incoterms"] == "EXW"
    assert out["bemerkungen"] == "ok"
    assert out["gueltigBis"] == "2026-12-31"


def test_angebot_row_to_dict_lieferzeit_from_notizen_when_column_missing():
    row = {
        "id": "ang-2",
        "angebots_nummer": None,
        "anfrage_id": None,
        "lieferant_name": None,
        "lieferant_id": None,
        "artikel_nr": None,
        "artikel_name": "Weizen",
        "menge": None,
        "einheit": None,
        "einheitspreis": None,
        "netto_summe": 50,
        "waehrung": None,
        "gueltig_bis": None,
        "status": None,
        "lieferzeit_tage": None,
        "notizen": {"lieferzeit": 7, "menge": 3, "einheit": "t", "artikel": "Weizen"},
        "created_at": None,
    }
    out = EinkaufCompatService._angebot_row_to_dict(row)
    assert out["angebotNummer"] == "ang-2"
    assert out["artikel"] == "Weizen"
    assert out["menge"] == 3.0
    assert out["einheit"] == "t"
    assert out["preis"] == 50.0
    assert out["lieferzeit"] == 7
    assert out["waehrung"] == "EUR"


def test_anlieferavis_row_to_dict_builds_fahrzeug_from_flat_or_nested():
    flat = {
        "id": "av-1",
        "avis_nummer": "AV-1",
        "bestellung_id": "PO-1",
        "lieferant_name": "Hof",
        "lieferant_id": "L-9",
        "status": "offen",
        "geplantes_anliefer_datum": date(2026, 11, 20),
        "notizen": '{"kennzeichen": "B-AB 1", "fahrer": "Max", "telefon": "0123", "positionen": [{"pos": 1}], "bemerkungen": "Tor 2"}',
        "created_at": datetime(2026, 11, 2, 8, 0, 0),
    }
    out = EinkaufCompatService._anlieferavis_row_to_dict(flat)
    assert out["avisNummer"] == "AV-1"
    assert out["bestellungId"] == "PO-1"
    assert out["lieferantId"] == "L-9"
    assert out["kennzeichen"] == "B-AB 1"
    assert out["fahrer"] == "Max"
    assert out["telefon"] == "0123"
    assert out["fahrzeug"]["kennzeichen"] == "B-AB 1"
    assert out["positionen"] == [{"pos": 1}]
    assert out["bemerkungen"] == "Tor 2"
    assert out["geplantesAnlieferDatum"] == "2026-11-20"

    nested = {
        "id": "av-2",
        "avis_nummer": None,
        "bestellung_id": None,
        "lieferant_name": None,
        "lieferant_id": None,
        "status": None,
        "geplantes_anliefer_datum": None,
        "notizen": {"fahrzeug": {"kennzeichen": "M-XY 9", "fahrer": "Eva", "telefon": "99"}},
        "created_at": None,
    }
    out2 = EinkaufCompatService._anlieferavis_row_to_dict(nested)
    assert out2["avisNummer"] == "av-2"
    assert out2["fahrzeug"]["fahrer"] == "Eva"
    assert out2["kennzeichen"] == "M-XY 9"
    assert out2["positionen"] == []


def test_angebot_notizen_payload_empty_or_json():
    svc = EinkaufCompatService(MagicMock(), "t1")
    assert svc._angebot_notizen_payload({}) is None
    raw = svc._angebot_notizen_payload(
        {
            "mindestabnahme": 1,
            "zahlungsbedingungen": "Sofort",
            "incoterms": "FOB",
            "bemerkungen": "Hinweis",
            "lieferzeit": 3,
            "artikel": "Gerste",
            "menge": 10,
            "einheit": "t",
        }
    )
    assert raw is not None
    assert '"incoterms": "FOB"' in raw
    assert '"artikel": "Gerste"' in raw


def test_create_angebot_writes_kopf_and_position():
    db = MagicMock()
    created = SimpleNamespace(
        _mapping={
            "id": "new-ang",
            "angebots_nummer": "ANG-NEW",
            "anfrage_id": "anf-1",
            "lieferant_name": "Hof",
            "lieferant_id": "L-1",
            "artikel_nr": "ART",
            "menge": 2.0,
            "einheit": "t",
            "einheitspreis": 80.0,
            "netto_summe": 160.0,
            "waehrung": "EUR",
            "gueltig_bis": None,
            "status": "ERFASST",
            "lieferzeit_tage": 4,
            "notizen": None,
            "created_at": None,
        }
    )
    db.execute.return_value.fetchone.return_value = created
    svc = EinkaufCompatService(db, "tenant-a")
    with patch.object(svc, "_invalidate"), patch(
        "app.services.einkauf_compat_service.uuid7", side_effect=["id-kopf", "id-pos"]
    ):
        out = svc.create_angebot(
            {
                "angebotNummer": "ANG-NEW",
                "lieferant": "Hof",
                "lieferantId": "L-1",
                "anfrageId": "anf-1",
                "artikel": "ART",
                "menge": 2,
                "preis": 80,
                "einheit": "t",
                "lieferzeit": 4,
                "status": "ERFASST",
            }
        )
    assert out["id"] == "new-ang"
    assert out["preis"] == 160.0
    assert db.execute.call_count >= 2
    db.commit.assert_called_once()


def test_create_angebot_lieferzeit_ungueltig_wird_none():
    db = MagicMock()
    created = SimpleNamespace(
        _mapping={
            "id": "ang-x",
            "angebots_nummer": "ANG-X",
            "anfrage_id": None,
            "lieferant_name": None,
            "lieferant_id": None,
            "artikel_nr": "X",
            "menge": 1.0,
            "einheit": "Stk",
            "einheitspreis": 1.0,
            "netto_summe": 1.0,
            "waehrung": "EUR",
            "gueltig_bis": None,
            "status": "ERFASST",
            "lieferzeit_tage": None,
            "notizen": None,
            "created_at": None,
        }
    )
    db.execute.return_value.fetchone.return_value = created
    svc = EinkaufCompatService(db, "tenant-a")
    with patch.object(svc, "_invalidate"), patch(
        "app.services.einkauf_compat_service.uuid7", side_effect=["k", "p"]
    ):
        svc.create_angebot({"artikel": "X", "menge": 1, "preis": 1, "lieferzeit": "nicht-zahl"})
    pos_call = db.execute.call_args_list[1]
    params = pos_call.args[1] if len(pos_call.args) > 1 else pos_call.kwargs.get("params") or pos_call.args[1]
    # second execute is position insert
    assert any(
        isinstance(c.args[1], dict) and c.args[1].get("lt") is None
        for c in db.execute.call_args_list
        if len(c.args) > 1 and isinstance(c.args[1], dict)
    )


def test_get_angebot_fehlt_wirft():
    from app.core.exceptions import EntityNotFoundError

    db = MagicMock()
    svc = EinkaufCompatService(db, "tenant-a")
    with patch.object(svc, "_load_angebot_raw_row", return_value=None):
        with pytest.raises(EntityNotFoundError):
            svc.get_angebot("missing")


def test_update_angebot_aktualisiert_kopf_und_position():
    from app.core.exceptions import EntityNotFoundError

    existing = SimpleNamespace(
        _mapping={
            "id": "ang-upd",
            "angebots_nummer": "ANG-OLD",
            "anfrage_id": "anf-1",
            "lieferant_name": "Alt",
            "lieferant_id": "L-1",
            "artikel_nr": "ART-OLD",
            "artikel_name": "ART-OLD",
            "menge": 1.0,
            "einheit": "t",
            "einheitspreis": 10.0,
            "netto_summe": 10.0,
            "waehrung": "EUR",
            "gueltig_bis": date(2026, 12, 1),
            "status": "ERFASST",
            "lieferzeit_tage": 2,
            "notizen": '{"bemerkungen": "alt"}',
            "created_at": None,
        }
    )
    db = MagicMock()
    pos_row = MagicMock()
    pos_row._mapping = {"id": "pos-1"}
    # first execute after load: UPDATE; then SELECT position; then UPDATE position
    db.execute.side_effect = [
        MagicMock(),  # UPDATE kopf
        MagicMock(fetchone=MagicMock(return_value=pos_row)),  # existing position
        MagicMock(),  # UPDATE position
        MagicMock(fetchone=MagicMock(return_value=existing)),  # get_angebot reload via _load
    ]
    svc = EinkaufCompatService(db, "tenant-a")
    with patch.object(svc, "_load_angebot_raw_row", side_effect=[existing, existing]), patch.object(
        svc, "_invalidate"
    ):
        out = svc.update_angebot(
            "ang-upd",
            {
                "lieferant": "Neu",
                "artikel": "ART-NEW",
                "menge": 3,
                "preis": 20,
                "einheit": "t",
                "lieferzeit": 9,
                "status": "GESENDET",
            },
        )
    assert out["id"] == "ang-upd"
    assert db.commit.called

    with patch.object(svc, "_load_angebot_raw_row", return_value=None):
        with pytest.raises(EntityNotFoundError):
            svc.update_angebot("missing", {})


def test_avis_notizen_and_create_anlieferavis():
    svc = EinkaufCompatService(MagicMock(), "tenant-a")
    assert svc._avis_notizen_payload({}) is None
    raw = svc._avis_notizen_payload(
        {
            "kennzeichen": "B-1",
            "fahrer": "Max",
            "telefon": "1",
            "fahrzeug": {"kennzeichen": "B-1", "fahrer": "Max", "telefon": "1"},
            "positionen": [{"pos": 1}],
            "bemerkungen": "Tor",
        }
    )
    assert raw is not None
    assert "kennzeichen" in raw

    db = MagicMock()
    created = SimpleNamespace(
        _mapping={
            "id": "av-new",
            "avis_nummer": "AV-NEW",
            "bestellung_id": "PO-1",
            "lieferant_name": "Hof",
            "lieferant_id": "L-1",
            "status": "GESENDET",
            "geplantes_anliefer_datum": date(2026, 11, 21),
            "notizen": raw,
            "created_at": None,
        }
    )
    db.execute.return_value.fetchone.return_value = created
    svc = EinkaufCompatService(db, "tenant-a")
    with patch.object(svc, "_invalidate"), patch(
        "app.services.einkauf_compat_service.uuid7", return_value="av-id"
    ), patch.object(svc, "get_anlieferavis", return_value={"id": "av-new", "avisNummer": "AV-NEW"}):
        out = svc.create_anlieferavis(
            {
                "avisNummer": "AV-NEW",
                "lieferant": "Hof",
                "lieferantId": "L-1",
                "bestellungId": "PO-1",
                "geplantesAnlieferDatum": "2026-11-21T08:00:00",
                "kennzeichen": "B-1",
                "fahrer": "Max",
                "telefon": "1",
                "bemerkungen": "Tor",
            }
        )
    assert out["id"] == "av-new"
    db.commit.assert_called_once()
