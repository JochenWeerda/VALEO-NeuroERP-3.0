"""Executable Unit-Tests: Kontrakt-Mengenzeitraum Endpoints (Sonar New-Code-Coverage)."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import kontrakt_mengenzeitraum as mz


def _row(**fields):
    base = {
        "id": "mz-1",
        "kontrakt_nr": "K-1",
        "zeitraum_von": date(2026, 1, 1),
        "zeitraum_bis": date(2026, 1, 31),
        "menge_t": Decimal("10"),
        "menge_bereits_geliefert_t": Decimal("0"),
        "menge_restmenge_t": Decimal("10"),
        "variante": "monatl. lin. Abnahme",
        "status": "offen",
        "bemerkung": None,
        "created_at": datetime(2026, 1, 1, 12, 0, 0),
    }
    base.update(fields)
    return SimpleNamespace(_mapping=base, **base)


def test_list_mengenzeitraeume_maps_rows():
    db = MagicMock()
    db.execute.return_value.fetchall.return_value = [_row()]
    out = mz.list_mengenzeitraeume("K-1", db=db, tenant_id="t1")
    assert len(out) == 1
    assert out[0].kontrakt_nr == "K-1"
    assert out[0].menge_t == Decimal("10")


def test_create_mengenzeitraum_validates_dates_and_kontrakt_nr():
    db = MagicMock()
    payload = mz.MengenzeitraumCreate(
        kontrakt_nr="K-1",
        zeitraum_von=date(2026, 2, 1),
        zeitraum_bis=date(2026, 1, 1),
        menge_t=Decimal("5"),
    )
    with pytest.raises(HTTPException) as exc:
        mz.create_mengenzeitraum("K-1", payload, db=db, tenant_id="t1")
    assert exc.value.status_code == 422

    payload2 = mz.MengenzeitraumCreate(
        kontrakt_nr="OTHER",
        zeitraum_von=date(2026, 1, 1),
        zeitraum_bis=date(2026, 1, 31),
        menge_t=Decimal("5"),
    )
    with pytest.raises(HTTPException) as exc2:
        mz.create_mengenzeitraum("K-1", payload2, db=db, tenant_id="t1")
    assert exc2.value.status_code == 422


def test_create_mengenzeitraum_inserts_and_returns():
    db = MagicMock()
    created = _row(id="new-1")
    db.execute.return_value.fetchone.return_value = created
    with patch("app.api.v1.endpoints.kontrakt_mengenzeitraum.uuid7", return_value="new-1"):
        out = mz.create_mengenzeitraum(
            "K-1",
            mz.MengenzeitraumCreate(
                kontrakt_nr="K-1",
                zeitraum_von=date(2026, 1, 1),
                zeitraum_bis=date(2026, 1, 31),
                menge_t=Decimal("12.5"),
                variante="flexibel",
                bemerkung="ok",
            ),
            db=db,
            tenant_id="t1",
        )
    assert out.id == "new-1"
    db.commit.assert_called()


def test_update_mengenzeitraum_404_and_patch():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    with pytest.raises(HTTPException) as exc:
        mz.update_mengenzeitraum(
            "K-1",
            "mz-x",
            mz.MengenzeitraumUpdate(status="offen"),
            db=db,
            tenant_id="t1",
        )
    assert exc.value.status_code == 404

    existing = _row()
    updated = _row(status="teilgeliefert", menge_bereits_geliefert_t=Decimal("2"), menge_restmenge_t=Decimal("8"))
    db.execute.return_value.fetchone.side_effect = [existing, updated]
    out = mz.update_mengenzeitraum(
        "K-1",
        "mz-1",
        mz.MengenzeitraumUpdate(
            menge_t=Decimal("10"),
            menge_bereits_geliefert_t=Decimal("2"),
            status="teilgeliefert",
            bemerkung="teil",
        ),
        db=db,
        tenant_id="t1",
    )
    assert out.status == "teilgeliefert"
    db.commit.assert_called()


def test_delete_mengenzeitraum_guards():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    with pytest.raises(HTTPException) as exc:
        mz.delete_mengenzeitraum("K-1", "mz-x", db=db, tenant_id="t1")
    assert exc.value.status_code == 404

    db.execute.return_value.fetchone.return_value = SimpleNamespace(status="erfuellt")
    with pytest.raises(HTTPException) as exc2:
        mz.delete_mengenzeitraum("K-1", "mz-1", db=db, tenant_id="t1")
    assert exc2.value.status_code == 409

    db.execute.return_value.fetchone.return_value = SimpleNamespace(status="offen")
    resp = mz.delete_mengenzeitraum("K-1", "mz-1", db=db, tenant_id="t1")
    assert resp.status_code == 204
    db.commit.assert_called()


def test_generiere_mengenzeitraeume_body_and_query():
    db = MagicMock()
    with patch("app.api.v1.endpoints.kontrakt_mengenzeitraum.uuid7", side_effect=["a", "b", "c"]):
        out = mz.generiere_mengenzeitraeume(
            "K-1",
            body=mz.MengenzeitraeumeGenerierenIn(
                von_datum=date(2026, 1, 15),
                bis_datum=date(2026, 3, 10),
                gesamt_menge_t=Decimal("30"),
            ),
            db=db,
            tenant_id="t1",
        )
    assert out["anzahl_zeitraeume"] == 3
    assert out["kontrakt_nr"] == "K-1"
    db.commit.assert_called()

    with pytest.raises(HTTPException) as exc:
        mz.generiere_mengenzeitraeume("K-1", db=db, tenant_id="t1")
    assert exc.value.status_code == 422


def test_zuabschlag_gruppe_and_position_guards():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        mz.create_zuabschlagsgruppe(
            mz.ZuAbschlagsGruppeCreate(gruppe_nr="G1", bezeichnung="X", typ="invalid"),
            db=db,
            tenant_id="t1",
        )
    assert exc.value.status_code == 422

    db.execute.return_value.fetchone.return_value = None
    with pytest.raises(HTTPException) as exc2:
        mz.get_zuabschlagsgruppe("missing", db=db, tenant_id="t1")
    assert exc2.value.status_code == 404

    with pytest.raises(HTTPException) as exc3:
        mz.create_zuabschlag(
            "g1",
            mz.ZuAbschlagCreate(gruppe_id="other", bezeichnung="Z", betrag_eur=Decimal("1")),
            db=db,
            tenant_id="t1",
        )
    assert exc3.value.status_code == 422

    with pytest.raises(HTTPException) as exc4:
        mz.create_zuabschlag(
            "g1",
            mz.ZuAbschlagCreate(gruppe_id="g1", bezeichnung="Z"),
            db=db,
            tenant_id="t1",
        )
    assert exc4.value.status_code == 422

    db.execute.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc5:
        mz.create_zuabschlag(
            "g1",
            mz.ZuAbschlagCreate(gruppe_id="g1", bezeichnung="Z", betrag_eur=Decimal("1")),
            db=db,
            tenant_id="t1",
        )
    assert exc5.value.status_code == 404


def test_list_zuabschlagsgruppen_and_positionen():
    db = MagicMock()
    db.execute.return_value.fetchall.return_value = [
        SimpleNamespace(_mapping={
            "id": "g1",
            "gruppe_nr": "G1",
            "bezeichnung": "Quali",
            "typ": "zuschlag",
            "aktiv": True,
        })
    ]
    groups = mz.list_zuabschlagsgruppen(typ="zuschlag", db=db, tenant_id="t1")
    assert groups[0]["gruppe_nr"] == "G1"

    db.execute.return_value.fetchall.return_value = [
        SimpleNamespace(_mapping={
            "id": "z1",
            "gruppe_id": "g1",
            "kontrakt_nr": None,
            "bezeichnung": "Feuchte",
            "betrag_eur": Decimal("1.5"),
            "prozent": None,
            "einheit": "t",
            "gueltig_ab": None,
            "gueltig_bis": None,
            "aktiv": True,
            "created_at": datetime(2026, 1, 1),
        })
    ]
    pos = mz.list_zuabschlaege("g1", kontrakt_nr="K-1", stichtag=date(2026, 6, 1), db=db, tenant_id="t1")
    assert pos[0].bezeichnung == "Feuchte"


def test_create_zuabschlagsgruppe_and_zuabschlag_success():
    db = MagicMock()
    group_row = SimpleNamespace(_mapping={
        "id": "g-new",
        "gruppe_nr": "G9",
        "bezeichnung": "Zuschlag",
        "typ": "zuschlag",
        "aktiv": True,
    })
    db.execute.return_value.fetchone.return_value = group_row
    with patch("app.api.v1.endpoints.kontrakt_mengenzeitraum.uuid7", return_value="g-new"):
        created = mz.create_zuabschlagsgruppe(
            mz.ZuAbschlagsGruppeCreate(gruppe_nr="G9", bezeichnung="Zuschlag", typ="zuschlag"),
            db=db,
            tenant_id="t1",
        )
    assert created["id"] == "g-new"

    pos_row = SimpleNamespace(_mapping={
        "id": "z-new",
        "gruppe_id": "g-new",
        "kontrakt_nr": "K-1",
        "bezeichnung": "Feuchte",
        "betrag_eur": Decimal("2"),
        "prozent": None,
        "einheit": "t",
        "gueltig_ab": None,
        "gueltig_bis": None,
        "aktiv": True,
        "created_at": datetime(2026, 1, 2),
    })
    db.execute.return_value.first.return_value = 1
    db.execute.return_value.fetchone.return_value = pos_row
    with patch("app.api.v1.endpoints.kontrakt_mengenzeitraum.uuid7", return_value="z-new"):
        pos = mz.create_zuabschlag(
            "g-new",
            mz.ZuAbschlagCreate(
                gruppe_id="g-new",
                kontrakt_nr="K-1",
                bezeichnung="Feuchte",
                betrag_eur=Decimal("2"),
            ),
            db=db,
            tenant_id="t1",
        )
    assert pos.id == "z-new"
    assert pos.bezeichnung == "Feuchte"
