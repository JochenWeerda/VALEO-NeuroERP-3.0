"""Real service decisions share the configured business day across month boundaries."""
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core import business_time
from app.services import bewerbung_einwilligung_service as consent
from app.services import bewerbung_loeschlauf_service as retention
from app.services import schaden_service as damage
from app.services import wareneingang_avis_service as receipt


@pytest.fixture(params=[("Europe/Berlin", date(2026, 4, 1)), ("Pacific/Honolulu", date(2026, 3, 31))])
def day(request, monkeypatch):
    zone, expected = request.param
    monkeypatch.setenv("BUSINESS_TIMEZONE", zone)
    instant = datetime(2026, 3, 31, 22, 30, tzinfo=timezone.utc)
    monkeypatch.setattr(business_time, "business_now", lambda: instant.astimezone(business_time.business_timezone()))
    return expected


def test_retention_cutoff_respects_business_zone_and_explicit_day(day):
    assert retention.stichtag(180) == day - timedelta(days=180)
    assert retention.stichtag(30, date(2025, 1, 1)) == date(2024, 12, 2)


def test_retention_cutoff_consent_and_hold_compare_the_same_day(day):
    db = MagicMock()
    db.execute.return_value.mappings.return_value.fetchmany.return_value = []
    assert retention.faellige(db, "tenant-a", 180) == []
    statement, params = db.execute.call_args.args
    assert params["heute"] == day
    assert params["stichtag"] == day - timedelta(days=180)
    assert params["tid"] == "tenant-a"
    assert str(statement).count("CAST(:heute AS date)") == 2
    assert "CURRENT_DATE" not in str(statement)
    db.commit.assert_not_called()


def test_consent_status_binds_business_day(day, monkeypatch):
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "gueltig_bis": day, "erteilt_am": None, "laeuft": True,
    }
    monkeypatch.setattr(consent, "verzeichnis", lambda *args: [])
    result = consent.stand(db, "tenant-a", "application")
    statement, params = db.execute.call_args.args
    assert params == {"id": "application", "tid": "tenant-a", "heute": day}
    assert "CAST(:heute AS date)" in str(statement)
    assert result["gueltig_bis"] == day.isoformat() and result["laeuft"] is True


def test_retention_audit_and_candidates_share_day_across_midnight(day, monkeypatch):
    clock = MagicMock(side_effect=[day, day + timedelta(days=1)])
    monkeypatch.setattr(retention, "business_today", clock)
    db = MagicMock()
    db.execute.return_value.mappings.return_value.fetchmany.return_value = []
    db.execute.return_value.mappings.return_value.first.return_value = {"stichtag": day - timedelta(days=180)}
    result = retention.lauf_ausfuehren(db, "tenant-a", "run", {
        "aufbewahrung_tage": 180, "gesetzliche_grundlage": "approved rule",
    }, "actor")
    candidates, audit = [c.args[1] for c in db.execute.call_args_list]
    assert candidates["heute"] == day
    assert candidates["stichtag"] == audit["stichtag"] == day - timedelta(days=180)
    assert result["stichtag"] == audit["stichtag"].isoformat()
    clock.assert_called_once()
    db.commit.assert_not_called()


@pytest.mark.parametrize("offset,allowed", [(0, False), (1, True), (1095, True), (1096, False)])
def test_consent_validity_uses_business_day_and_preserves_limits(day, offset, allowed, monkeypatch):
    monkeypatch.setattr(consent, "bewerbung_sperren", lambda *args: {})
    monkeypatch.setattr(consent, "_erklaerung_holen", lambda *args: {"id": "text"})
    write = MagicMock(return_value={"id": "event"})
    monkeypatch.setattr(consent, "_vorgang_schreiben", write)
    db = MagicMock()
    payload = SimpleNamespace(
        fassung=1,
        gueltig_bis=day + timedelta(days=offset),
        kanal="PAPIER",
        erfasst_durch="actor",
    )
    if allowed:
        assert consent.erteilen(db, "tenant-a", "application", "event", payload) == {"id": "event"}
        assert write.call_args.args[5] == payload.gueltig_bis
    else:
        with pytest.raises(HTTPException) as error:
            consent.erteilen(db, "tenant-a", "application", "event", payload)
        assert error.value.status_code == 422
        write.assert_not_called()
        db.execute.assert_not_called()
    db.commit.assert_not_called()


@pytest.mark.parametrize("offset,expired", [(-1, True), (0, False), (1, False)])
def test_damage_deadline_is_inclusive_on_business_day(day, offset, expired):
    result = damage.anreichern({"status": "ENTWURF", "schadendatum": day + timedelta(days=offset-3)}, 3)
    assert result["frist_ueberschritten"] is expired


def test_all_receipt_positions_and_order_share_one_day_even_across_midnight(day, monkeypatch):
    clock = MagicMock(side_effect=[day, day + timedelta(days=1)])
    monkeypatch.setattr(receipt, "business_today", clock)
    monkeypatch.setattr(receipt, "_avis_und_bestellung", lambda *args: ({"avis_nummer": "AV-1"}, {"id": "order", "bestellnummer": "EK-1"}))
    monkeypatch.setattr(receipt, "pruefe_wareneingang", lambda *args: [
        {"id": f"position-{i}", "pos_nr": i, "article_id": f"article-{i}", "menge_offen": 2, "einheit": "t"}
        for i in (1, 2)
    ])
    monkeypatch.setattr(receipt, "current_stock", lambda *args, **kwargs: 10)
    db = MagicMock()
    result = receipt.buche_wareneingang_aus_avis(db, "avis", "tenant-a", "warehouse", " LS-1 ", "actor")
    movements = [c.args[1] for c in db.execute.call_args_list if "INSERT INTO domain_inventory.inventory_stock_movements" in str(c.args[0])]
    order = next(c.args[1] for c in db.execute.call_args_list if "lieferdatum_ist" in str(c.args[0]))
    assert len(movements) == 2
    assert all(p["datum"] == day and p["tid"] == "tenant-a" for p in movements)
    assert order["heute"] == day and order["tid"] == "tenant-a"
    clock.assert_called_once()
    db.commit.assert_called_once()
    assert result["positionen"] == 2
